param(
    [ValidateSet('Unit', 'Backend', 'Frontend', 'All')]
    [string] $Gate = 'Unit'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot 'backend\.venv\Scripts\python.exe'
$LogDirectory = Join-Path $ProjectRoot 'logs\verification'
$Results = [System.Collections.Generic.List[object]]::new()
New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null

function Invoke-ProjectGate($Name, $Directory, $Action) {
    $LogPath = Join-Path $LogDirectory ($Name + '.log')
    Push-Location $Directory
    try {
        & $Action *> $LogPath
        $Code = $LASTEXITCODE
        $Results.Add([pscustomobject]@{ Gate = $Name; ExitCode = $Code; Log = $LogPath })
        Get-Content -LiteralPath $LogPath -Tail 12
    }
    finally { Pop-Location }
}

# I test ricostruiscono tabelle e fanno TRUNCATE. La destinazione è fissa e
# usa-e-getta; non ereditare TEST_DATABASE_URL o il backend email della shell.
$SavedEnvironment = @{}
foreach ($Name in @('TEST_DATABASE_URL', 'EMAIL_BACKEND', 'ERSAF_ENV')) {
    $SavedEnvironment[$Name] = [Environment]::GetEnvironmentVariable($Name, 'Process')
}

try {
    $env:TEST_DATABASE_URL = 'mysql+pymysql://ersaf:ersaf@127.0.0.1:3307/ersaf_test'
    $env:EMAIL_BACKEND = 'memoria'
    $env:ERSAF_ENV = 'test'
    if ($Gate -in @('Unit', 'Backend', 'All')) {
        if (-not (Test-Path -LiteralPath $Python)) { throw 'Creare prima backend/.venv: docs/development.md' }
        $Backend = Join-Path $ProjectRoot 'backend'
        if ($Gate -eq 'Unit') {
            Invoke-ProjectGate 'backend-unit' $Backend { & $Python -m pytest tests/unit }
        }
        else {
            Invoke-ProjectGate 'backend-full' $Backend { & $Python -m pytest --require-mariadb }
        }
    }
    if ($Gate -in @('Frontend', 'All')) {
        $Frontend = Join-Path $ProjectRoot 'frontend'
        Invoke-ProjectGate 'frontend-build' $Frontend { npm.cmd run build }
        Invoke-ProjectGate 'frontend-lint' $Frontend { npm.cmd run lint }
    }
}
finally {
    foreach ($Name in $SavedEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($Name, $SavedEnvironment[$Name], 'Process')
    }
}

$Results | Format-Table -AutoSize
if (@($Results | Where-Object ExitCode -ne 0).Count -gt 0) { exit 1 }
exit 0
