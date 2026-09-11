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
  setup             prima configurazione del PC: chiave SSH, alias e chiave host del server.
                    Da eseguire una sola volta da chi entra nel team.
  authorize-key     autorizza sul server la chiave pubblica di un collega (-KeyFile <file.pub>).
                    La esegue chi ha gia' accesso.
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
  publish-domain    pubblica il collaudo sul dominio servito dal reverse proxy della LAN
  unpublish-domain  toglie la pubblicazione e torna al solo tunnel SSH
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
    [ValidateSet('setup', 'authorize-key', 'preflight', 'install', 'deploy', 'build', 'refresh-clone',
        'configure-source', 'rollback', 'backup-db', 'restore-db', 'status', 'logs', 'verify',
        'stop', 'start', 'tunnel', 'publish-domain', 'unpublish-domain')]
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
    [string] $SourceDb = 'admin_entedb',
    # Pubblicazione sul dominio: il reverse proxy della LAN raggiunge la porta web del server.
    [string] $Domain = 'unistaging.ersaf.it',
    [string] $ProxyIp = '192.168.40.10',
    # File .pub del collega da autorizzare sul server (azione authorize-key).
    [string] $KeyFile = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)

$RemoteBase = '/srv/ersaf-universita'
$NomeChiave = 'id_ed25519_ersaf_12'
# Chiave pubblica host del server, presa da una postazione gia' autorizzata. Serve a scrivere
# known_hosts in anticipo: il primo collegamento non chiede nulla e non si accetta alla cieca
# un'identita' mai vista. Se il server venisse reinstallato, questa riga va aggiornata.
$ChiaveHostServer = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFjwh8bLL2j9/5T9ok8NzI0OpsQmgerNO0sNfpPuacdQ'
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
        Stop-WithError "connessione SSH a '$SshHost' non riuscita. Se e' la prima volta su questo PC, eseguire: scripts\deploy.ps1 -Action setup, poi far autorizzare la chiave mostrata."
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
    # Pubblicare un ramo diverso da main e' legittimo, serve a provare il proprio lavoro
    # prima della revisione, ma deve restare evidente: l'ambiente e' uno solo e condiviso.
    if ($Ref -and $Ref -ne 'origin/main') {
        Write-Host "    ATTENZIONE: stai pubblicando $Ref, non main. Il collaudo restera' su questo" -ForegroundColor Yellow
        Write-Host '    codice finche'' qualcuno non ripubblica. Avvisa in chat.' -ForegroundColor Yellow
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

# ---------------------------------------------------------------- prima configurazione

function Get-CartellaSsh {
    $cartella = Join-Path $env:USERPROFILE '.ssh'
    if (-not (Test-Path -LiteralPath $cartella)) {
        New-Item -ItemType Directory -Path $cartella | Out-Null
    }
    return $cartella
}

function New-IdentitaSsh([string] $Percorso) {
    if (Test-Path -LiteralPath $Percorso) {
        Write-Note 'chiave SSH gia'' presente, la conservo'
        return
    }
    Write-Note 'genero una chiave SSH dedicata a questo progetto'
    # Senza passphrase: lo script si collega da solo e una richiesta interattiva lo bloccherebbe.
    # La chiave vale solo per questo server e resta sul PC.
    & ssh-keygen -t ed25519 -f $Percorso -N '""' -C "$env:USERNAME@ersaf-universita" | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'generazione della chiave SSH non riuscita' }
}

function Add-ChiaveHostConosciuta([string] $Cartella) {
    $percorso = Join-Path $Cartella 'known_hosts'
    if (-not (Test-Path -LiteralPath $percorso)) { New-Item -ItemType File -Path $percorso | Out-Null }
    $righe = @(Get-Content -LiteralPath $percorso -ErrorAction SilentlyContinue)
    if ($righe | Where-Object { $_ -like "$ServerIp *" }) {
        Write-Note 'chiave host del server gia'' registrata'
        return
    }
    Add-Content -LiteralPath $percorso -Value "$ServerIp $ChiaveHostServer"
    Write-Note 'registrata la chiave host del server: il primo collegamento non chiedera'' conferme'
}

function Add-AliasSsh([string] $Cartella, [string] $Chiave) {
    $percorso = Join-Path $Cartella 'config'
    if (-not (Test-Path -LiteralPath $percorso)) { New-Item -ItemType File -Path $percorso | Out-Null }
    $contenuto = Get-Content -LiteralPath $percorso -Raw -ErrorAction SilentlyContinue
    if ($contenuto -and $contenuto -match "(?m)^Host\s+.*\b$([regex]::Escape($SshHost))\b") {
        Write-Note "alias '$SshHost' gia' presente in ~/.ssh/config"
        return
    }
    $blocco = @"

Host $SshHost $ServerIp
  HostName $ServerIp
  User root
  Port $SshPort
  IdentityFile $($Chiave -replace '\\', '/')
  IdentitiesOnly yes
  StrictHostKeyChecking yes
"@
    Add-Content -LiteralPath $percorso -Value $blocco
    Write-Note "aggiunto l'alias '$SshHost' a ~/.ssh/config"
}

function Test-AccessoRemoto {
    $precedente = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $esito = @(& ssh @SshOptions $SshHost 'echo ERSAF_OK' 2>&1 | ForEach-Object { "$_" })
    $codice = $LASTEXITCODE
    $ErrorActionPreference = $precedente
    return ($codice -eq 0 -and ($esito -contains 'ERSAF_OK'))
}

function Invoke-Setup {
    Test-LocalTools
    $cartella = Get-CartellaSsh
    $chiave = Join-Path $cartella $NomeChiave
    Write-Step 'Configurazione dell''accesso al server'
    New-IdentitaSsh $chiave
    Add-ChiaveHostConosciuta $cartella
    Add-AliasSsh $cartella $chiave
    Test-Vpn
    if (Test-AccessoRemoto) {
        Write-Host "`nTutto pronto: l'accesso al server funziona." -ForegroundColor Green
        Write-Host 'Da ora il deploy e'' un solo comando:'
        Write-Host '  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\deploy.ps1'
        return
    }
    Write-Host "`nManca solo un passo: la tua chiave deve essere autorizzata sul server." -ForegroundColor Yellow
    Write-Host 'Invia a chi gestisce il server il contenuto di questo file (e'' una chiave pubblica,'
    Write-Host 'si puo'' mandare tranquillamente in chat):'
    Write-Host "  $chiave.pub" -ForegroundColor Cyan
    Write-Host ''
    Write-Host (Get-Content -LiteralPath "$chiave.pub" -Raw).Trim()
    Write-Host ''
    Write-Host 'Quando ti dicono che e'' fatto, ricontrolla con:'
    Write-Host '  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\deploy.ps1 -Action preflight'
}

function Invoke-AuthorizeKey {
    if (-not $KeyFile) { Stop-WithError 'indicare -KeyFile <percorso del file .pub del collega>' }
    if (-not (Test-Path -LiteralPath $KeyFile)) { Stop-WithError "file non trovato: $KeyFile" }
    $chiave = (Get-Content -LiteralPath $KeyFile -Raw).Trim()
    if ($chiave -match 'PRIVATE KEY') { Stop-WithError 'questa e'' una chiave PRIVATA: va usata solo quella .pub' }
    if ($chiave -notmatch '^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp[0-9]+) [A-Za-z0-9+/=]+') {
        Stop-WithError 'il file non contiene una chiave pubblica SSH valida'
    }
    if ($chiave -match "['`"``$\\]" -or $chiave -match "[`r`n]") {
        Stop-WithError 'la chiave contiene caratteri non ammessi nel commento: correggerlo e riprovare'
    }
    Write-Step 'Autorizzazione di una chiave sul server'
    & ssh-keygen -l -f $KeyFile | Out-Host
    Confirm-Typed 'AUTORIZZA' ("La chiave qui sopra potra' accedere come root a $ServerIp. " +
        'Le chiavi gia'' presenti restano invariate.')

    # Lo script remoto viaggia in base64: e'' l''unico modo per attraversare PowerShell, ssh e la
    # shell remota senza che virgolette e fine riga vengano reinterpretati lungo il percorso.
    $righe = @(
        'set -e',
        'umask 077',
        'mkdir -p /root/.ssh',
        'chmod 700 /root/.ssh',
        'touch /root/.ssh/authorized_keys',
        'chmod 600 /root/.ssh/authorized_keys',
        "chiave='$chiave'",
        'if grep -qxF "$chiave" /root/.ssh/authorized_keys; then',
        '  echo "chiave gia presente, nulla da modificare"',
        'else',
        '  printf "%s\n" "$chiave" >> /root/.ssh/authorized_keys',
        '  echo "chiave aggiunta"',
        'fi',
        'echo "chiavi autorizzate ora: $(grep -c . /root/.ssh/authorized_keys)"'
    )
    $codificato = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($righe -join "`n") + "`n"))
    & ssh @SshOptions $SshHost "echo $codificato | base64 -d | bash" | Out-Host
    if ($LASTEXITCODE -ne 0) { Stop-WithError "autorizzazione non riuscita (codice $LASTEXITCODE)" }
}

# ---------------------------------------------------------------- azioni

switch ($Action) {
    'setup' { Invoke-Setup }
    'authorize-key' { Test-LocalTools; Test-Vpn; Invoke-AuthorizeKey }
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
    'publish-domain' {
        Test-ConnessioneCompleta
        Write-Step "Pubblicazione su https://$Domain tramite il reverse proxy $ProxyIp"
        Write-Note 'La porta del web viene aperta sulla LAN al solo host del proxy, con regole firewall dedicate.'
        Invoke-Remote @('expose', $Domain, $ProxyIp) | Out-Null
        Write-Host "`nSul reverse proxy creare il proxy host per $Domain verso l'indirizzo indicato sopra." -ForegroundColor Green
    }
    'unpublish-domain' {
        Test-ConnessioneCompleta
        Invoke-Remote @('unexpose') | Out-Null
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
