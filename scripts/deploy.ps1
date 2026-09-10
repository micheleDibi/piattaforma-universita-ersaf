<#
.SYNOPSIS
Deploy della piattaforma Universita ERSAF sul server di collaudo 192.168.40.12 (VPN + SSH + Docker).

.DESCRIPTION
Un solo comando per l'intero ciclo: controlli locali (strumenti, VPN, SSH), preflight remoto in
sola lettura, pacchetto del codice, deploy con verifica finale e rollback automatico.
Tutto cio' che tocca il server e' in deploy/remote/*.sh, inviato via SSH a ogni esecuzione:
sul server restano soltanto le release. I segreti vengono generati o richiesti una volta e
restano sul server (shared/, solo root): questo script non li stampa e non li salva sul PC.

Azioni (-Action):
  preflight         controlli in sola lettura, locali e remoti
  install           prima installazione: directory, segreti, build, clone del database (dump in
                    sola lettura dalla sorgente), migrazioni sul clone, avvio e verifica
  deploy            aggiornamento dell'applicazione da origin/main; i dati del clone restano intatti (default)
  build             costruisce le immagini sul server senza toccare i container in esercizio
  refresh-clone     ricrea il clone dalla sorgente: operazione esplicita, chiede conferma
  configure-source  registra sul server le credenziali di lettura del database originale
  rollback          torna alla release precedente
  backup-db         snapshot del clone in snapshots/
  restore-db        ripristina il clone da uno snapshot (-Snapshot nome), chiede conferma
  status, logs, verify, stop, start
  tunnel            apre il tunnel SSH verso il collaudo: http://localhost:18082

.EXAMPLE
powershell -NoProfile -File scripts\deploy.ps1 -Action preflight
.EXAMPLE
powershell -NoProfile -File scripts\deploy.ps1 -Action install
.EXAMPLE
powershell -NoProfile -File scripts\deploy.ps1
.EXAMPLE
powershell -NoProfile -File scripts\deploy.ps1 -Action deploy -Ref ''   # albero di lavoro, solo prove
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('preflight', 'install', 'deploy', 'build', 'refresh-clone', 'configure-source', 'rollback',
        'backup-db', 'restore-db', 'status', 'logs', 'verify', 'stop', 'start', 'tunnel')]
    [string] $Action = 'deploy',
    [string] $SshHost = 'ersaf-12',
    [string] $ServerIp = '192.168.40.12',
    [int] $SshPort = 22,
    # Cosa pubblicare. Predefinito origin/main, aggiornato con fetch: si pubblica sempre cio' che
    # e' su GitHub. Stringa vuota: l'albero di lavoro corrente, solo per prove (file ignorati esclusi).
    [string] $Ref = 'origin/main',
    [string] $Service = 'api',
    [int] $Tail = 200,
    [string] $Snapshot = '',
    [int] $LocalPort = 18082,
    [int] $WebPort = 18082,
    [string] $SourceHost = '192.168.40.11',
    [int] $SourcePort = 3306,
    [string] $SourceDb = 'admin_entedb'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)

$RemoteBase = '/srv/ersaf-universita'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RemoteScripts = Join-Path $ProjectRoot 'deploy\remote'
$SshOptions = @('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
    '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=6')
# Toglie il BOM UTF-8 iniziale e i CR che Windows PowerShell 5.1 aggiunge allo stdin dei comandi nativi.
$RemoteSanitizer = "sed -e '1s/^\xEF\xBB\xBF//' -e 's/\r$//'"

function Write-Step([string] $Text) { Write-Host "`n==> $Text" -ForegroundColor Cyan }
function Write-Note([string] $Text) { Write-Host "    $Text" -ForegroundColor DarkGray }
function Stop-WithError([string] $Text) {
    Write-Host "`nERRORE: $Text" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------- prerequisiti

function Test-LocalTools {
    Write-Step 'Strumenti locali'
    foreach ($tool in 'ssh', 'scp', 'git', 'tar') {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            Stop-WithError "'$tool' non trovato nel PATH. Servono OpenSSH per Windows, Git e tar (inclusi in Windows 10/11)."
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $RemoteScripts '90-main.sh'))) {
        Stop-WithError 'cartella deploy\remote incompleta: eseguire lo script dal repository.'
    }
    Write-Note 'ssh, scp, git e tar disponibili'
}

function Test-Vpn {
    Write-Step "Raggiungibilita' del server $ServerIp (VPN aziendale)"
    # Ping e non una connessione TCP alla porta 22: un handshake aperto e chiuso a meta' viene letto
    # dai sistemi di sicurezza del server come una scansione e puo' far bloccare l'accesso.
    $ping = New-Object System.Net.NetworkInformation.Ping
    $risponde = $false
    foreach ($tentativo in 1..3) {
        try { if ($ping.Send($ServerIp, 2500).Status -eq 'Success') { $risponde = $true; break } } catch { }
    }
    if (-not $risponde) {
        Stop-WithError "il server $ServerIp non risponde al ping. La VPN aziendale non e' connessa oppure il server non e' raggiungibile: collegare la VPN e riprovare."
    }
    Write-Note 'il server risponde al ping'
}

function Test-ConnessioneCompleta {
    Test-LocalTools
    Test-Vpn
}

# ---------------------------------------------------------------- esecuzione remota

function Get-RemoteBundle {
    $parti = Get-ChildItem -Path $RemoteScripts -Filter '*.sh' | Sort-Object Name | ForEach-Object {
        (Get-Content -LiteralPath $_.FullName -Raw) -replace "`r`n", "`n"
    }
    # Chiude senza a capo: il trasporto aggiunge CRLF e completa una riga di commento.
    return (($parti -join "`n") + "`n# fine bundle")
}

function Invoke-Remote {
    param([Parameter(Mandatory)] [string[]] $Arguments, [switch] $AllowFailure)
    $bundle = Get-RemoteBundle
    # Windows PowerShell 5.1 antepone un BOM UTF-8 e chiude con CRLF: sed li toglie prima di bash.
    $comando = "$RemoteSanitizer | bash -s -- " + ($Arguments -join ' ')
    $bundle | & ssh @SshOptions $SshHost $comando | Out-Host
    $codice = $LASTEXITCODE
    if ($codice -eq 255) {
        Stop-WithError "connessione SSH a '$SshHost' non riuscita. Verificare l'alias in ~/.ssh/config e che la chiave pubblica sia autorizzata su root@$ServerIp (docs/deploy.md, sezione Accesso)."
    }
    if ($codice -ne 0 -and -not $AllowFailure) {
        Stop-WithError "comando remoto '$($Arguments[0])' terminato con codice $codice."
    }
    return $codice
}

function Invoke-Preflight([string] $Modo) {
    Write-Step 'Preflight remoto (sola lettura)'
    Invoke-Remote @('preflight', $Modo) | Out-Null
}

function Confirm-Typed([string] $Parola, [string] $Messaggio) {
    Write-Host "`n$Messaggio" -ForegroundColor Yellow
    $risposta = Read-Host "Digitare $Parola per confermare, qualunque altra cosa per annullare"
    if ($risposta -ne $Parola) { Stop-WithError "operazione annullata dall'operatore." }
}

# ---------------------------------------------------------------- pacchetto e deploy

function Update-RemoteRef {
    if ($Ref -notlike 'origin/*') { return }
    Write-Note "aggiorno $Ref da GitHub"
    & git -C $ProjectRoot fetch --quiet origin ($Ref -replace '^origin/', '')
    if ($LASTEXITCODE -ne 0) { Stop-WithError "fetch di $Ref fallito: verificare l'accesso a GitHub" }
}

function Get-GitSha {
    Update-RemoteRef
    if ($Ref) { $sha = & git -C $ProjectRoot rev-parse --verify "$Ref^{commit}" 2>$null }
    else { $sha = & git -C $ProjectRoot rev-parse HEAD }
    if ($LASTEXITCODE -ne 0 -or -not $sha) { Stop-WithError "riferimento git non valido: '$Ref'" }
    return "$sha".Trim()
}

function Test-DirtyTree {
    $stato = & git -C $ProjectRoot status --porcelain -- backend frontend db deploy
    return [bool] $stato
}

function New-ReleaseArchive([string] $Id) {
    $percorso = Join-Path $env:TEMP "ersaf-universita-$Id.tar.gz"
    if ($Ref) {
        & git -C $ProjectRoot archive --format=tar.gz -o $percorso $Ref backend frontend db deploy
        if ($LASTEXITCODE -ne 0) { Stop-WithError "git archive fallito per '$Ref'" }
        return $percorso
    }
    # Albero di lavoro: file tracciati e non tracciati, esclusi quelli ignorati (.env, dist, venv).
    $elenco = @(& git -C $ProjectRoot ls-files -co --exclude-standard -- backend frontend db deploy |
        Where-Object { Test-Path -LiteralPath (Join-Path $ProjectRoot $_) })
    if ($LASTEXITCODE -ne 0 -or $elenco.Count -eq 0) { Stop-WithError 'nessun file da pubblicare' }
    $listaFile = Join-Path $env:TEMP "ersaf-universita-$Id.lst"
    [IO.File]::WriteAllText($listaFile, (($elenco -join "`n") + "`n"))
    & tar -czf $percorso -C $ProjectRoot -T $listaFile
    $codice = $LASTEXITCODE
    Remove-Item -LiteralPath $listaFile -Force -ErrorAction SilentlyContinue
    if ($codice -ne 0) { Stop-WithError "creazione dell'archivio fallita (tar)" }
    return $percorso
}

function Send-Archive([string] $Percorso, [string] $Id) {
    $destinazione = "$RemoteBase/incoming/$Id.tar.gz"
    & scp -q @SshOptions -P $SshPort $Percorso "${SshHost}:$destinazione"
    if ($LASTEXITCODE -ne 0) { Stop-WithError "trasferimento dell'archivio fallito (scp)" }
    Remove-Item -LiteralPath $Percorso -Force -ErrorAction SilentlyContinue
    return $destinazione
}

function Publish-Release([string] $Comando, [string[]] $Opzioni) {
    Write-Step "Pacchetto del codice ($(if ($Ref) { $Ref } else { 'albero di lavoro' }))"
    $sha = Get-GitSha
    $sporco = 'false'
    if (-not $Ref -and (Test-DirtyTree)) {
        $sporco = 'true'
        Write-Note "ATTENZIONE: si pubblica l'albero di lavoro con modifiche non committate."
    }
    $id = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + $sha.Substring(0, 7)
    $archivio = New-ReleaseArchive $id
    $dimensione = [math]::Round((Get-Item -LiteralPath $archivio).Length / 1KB)
    Write-Note "release $id (git $($sha.Substring(0, 7)), $dimensione KB)"
    Write-Step 'Trasferimento sul server'
    $remoto = Send-Archive $archivio $id
    if ($Comando -eq 'build') { Write-Step 'Build remota delle immagini, nessun container toccato' }
    else { Write-Step 'Deploy remoto: build, migrazioni sul clone, avvio, verifica' }
    Invoke-Remote (@($Comando, $remoto, $id, $sha, $sporco) + $Opzioni) | Out-Null
    return $id
}

function Show-Access {
    Write-Host "`nAccesso al collaudo, solo tramite tunnel SSH:" -ForegroundColor Green
    Write-Host '  powershell -NoProfile -File scripts\deploy.ps1 -Action tunnel'
    Write-Host "  poi aprire http://localhost:$LocalPort nel browser."
}

# ---------------------------------------------------------------- sorgente (credenziali)

function Format-CnfValue([string] $Valore) {
    return '"' + $Valore.Replace('\', '\\').Replace('"', '\"') + '"'
}

function Set-SourceCredentials {
    Write-Step "Credenziali di lettura del database originale ${SourceHost}:$SourcePort/$SourceDb"
    Write-Note 'Vengono inviate via SSH e salvate solo sul server (shared/source-db.cnf, permessi 600).'
    Write-Note 'Servono soltanto a mariadb-dump in sola lettura: se disponibile usare un utente senza privilegi di scrittura.'
    $utente = Read-Host 'Utente del database originale'
    if (-not $utente) { Stop-WithError 'utente mancante' }
    $sicura = Read-Host 'Password (non viene mostrata)' -AsSecureString
    $password = (New-Object System.Management.Automation.PSCredential('x', $sicura)).GetNetworkCredential().Password
    if (-not $password) { Stop-WithError 'password mancante' }
    $cnf = "[client]`nhost=$SourceHost`nport=$SourcePort`nuser=$(Format-CnfValue $utente)`npassword=$(Format-CnfValue $password)`n"
    $meta = "SOURCE_DB_HOST=$SourceHost`nSOURCE_DB_PORT=$SourcePort`nSOURCE_DB_NAME=$SourceDb`n"
    $cnfRemoto = "$RemoteBase/shared/source-db.cnf"
    $metaRemoto = "$RemoteBase/shared/source-db.env"
    # Un solo collegamento: il flusso porta entrambi i file, separati da una riga marcatore.
    $remoto = "umask 077; $RemoteSanitizer | awk -v c='$cnfRemoto' -v e='$metaRemoto' 'BEGIN{f=c} /^#---ERSAF-SPLIT---$/{f=e; next} {print > f}' && test -s '$cnfRemoto' && test -s '$metaRemoto'"
    ($cnf + "#---ERSAF-SPLIT---`n" + $meta) | & ssh @SshOptions $SshHost $remoto | Out-Host
    $codice = $LASTEXITCODE
    $password = $null
    $cnf = $null
    if ($codice -ne 0) { Stop-WithError "registrazione delle credenziali fallita (codice $codice)" }
    Write-Note "sorgente registrata sul server: ${SourceHost}:$SourcePort schema $SourceDb"
}

# ---------------------------------------------------------------- azioni

switch ($Action) {
    'preflight' {
        Test-ConnessioneCompleta
        Invoke-Preflight '--auto'
    }
    'install' {
        Test-ConnessioneCompleta
        Write-Step 'Preflight, directory e segreti sul server'
        $esito = Invoke-Remote @('install', $WebPort) -AllowFailure
        if ($esito -eq 10) { Set-SourceCredentials }
        elseif ($esito -ne 0) { Stop-WithError "installazione remota terminata con codice $esito." }
        Confirm-Typed 'CLONA' ("L'installazione legge il database originale ${SourceHost}/$SourceDb con mariadb-dump in sola " +
            "lettura (snapshot consistente, nessun lock e nessuna scrittura) e lo importa nel clone sul server. " +
            "Se il clone esiste gia' non viene toccato. Durata indicativa: 10-30 minuti.")
        Publish-Release 'deploy' @('--primo-clone') | Out-Null
        Show-Access
    }
    'deploy' {
        Test-ConnessioneCompleta
        Publish-Release 'deploy' @() | Out-Null
        Show-Access
    }
    'build' {
        Test-ConnessioneCompleta
        Publish-Release 'build' @() | Out-Null
    }
    'refresh-clone' {
        Test-ConnessioneCompleta
        Confirm-Typed 'RICREA' ("Il clone verra' ricreato dal database originale (lettura con mariadb-dump). I dati di collaudo " +
            "attuali vengono prima salvati in snapshots/ e poi sostituiti; l'applicazione resta ferma durante l'operazione.")
        Invoke-Remote @('clone', '--confermato', '--refresh') | Out-Null
    }
    'configure-source' {
        Test-ConnessioneCompleta
        Set-SourceCredentials
    }
    'rollback' {
        Test-ConnessioneCompleta
        Invoke-Remote @('rollback') | Out-Null
    }
    'backup-db' {
        Test-ConnessioneCompleta
        Invoke-Remote @('backup') | Out-Null
    }
    'restore-db' {
        if (-not $Snapshot) { Stop-WithError 'indicare -Snapshot <nome file in snapshots/> (vedi -Action status)' }
        Test-ConnessioneCompleta
        Confirm-Typed 'RIPRISTINA' "Il clone verra' sostituito con lo snapshot $Snapshot; l'applicazione resta ferma durante l'operazione."
        Invoke-Remote @('restore', $Snapshot, '--confermato') | Out-Null
    }
    'status' { Test-Vpn; Invoke-Remote @('status') | Out-Null }
    'logs'   { Test-Vpn; Invoke-Remote @('logs', $Service, $Tail) | Out-Null }
    'verify' { Test-Vpn; Invoke-Remote @('verify') | Out-Null }
    'stop'   { Test-Vpn; Invoke-Remote @('stop') | Out-Null }
    'start'  { Test-Vpn; Invoke-Remote @('start') | Out-Null }
    'tunnel' {
        Test-Vpn
        Write-Host "`nTunnel attivo: aprire http://localhost:$LocalPort (Ctrl+C per chiudere)" -ForegroundColor Green
        & ssh @SshOptions -N -L "${LocalPort}:127.0.0.1:$WebPort" $SshHost
    }
}
exit 0
