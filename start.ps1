$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Venv = Join-Path $Root ".venv_local"
$Python = Join-Path $Venv "Scripts\python.exe"
$Npm = "npm"
$FrontendPort = 3000

Write-Host "Starting PFA - Gestion des Achats" -ForegroundColor Cyan
$env:PYTHONUTF8 = "1"

if (-not (Test-Path $Python)) {
    Write-Host "Creating Python virtual environment in .venv_local..."
    py -m venv $Venv
}

Write-Host "Installing backend dependencies..."
& $Python -m pip install -r (Join-Path $Backend "requirements.txt")

Write-Host "Running Django migrations..."
Push-Location $Backend
& $Python manage.py migrate
Write-Host "Seeding demo data..."
& $Python seed_data.py
Pop-Location

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $Frontend
    & $Npm install
    Pop-Location
}

$TmpDir = Join-Path $Root ".tmp"
$backendLog = Join-Path $TmpDir "backend.log"
$backendErrorLog = Join-Path $TmpDir "backend.err.log"
$frontendLog = Join-Path $TmpDir "frontend.log"
$frontendErrorLog = Join-Path $TmpDir "frontend.err.log"
New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

while (Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue) {
    $FrontendPort += 1
}

Write-Host "Launching backend on http://localhost:8000 ..."
$BackendProcess = Start-Process -FilePath $Python `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" `
    -WorkingDirectory $Backend `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErrorLog `
    -PassThru `
    -WindowStyle Hidden

Write-Host "Launching frontend on http://localhost:$FrontendPort ..."
$FrontendProcess = Start-Process -FilePath $Npm `
    -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "$FrontendPort" `
    -WorkingDirectory $Frontend `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErrorLog `
    -PassThru `
    -WindowStyle Hidden

Write-Host ""
Write-Host "Application started." -ForegroundColor Green
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Backend : http://localhost:8000"
Write-Host "Admin   : http://localhost:8000/admin"
Write-Host ""
Write-Host "Backend PID : $($BackendProcess.Id)"
Write-Host "Frontend PID: $($FrontendProcess.Id)"
Write-Host "Logs:"
Write-Host "  $backendLog"
Write-Host "  $backendErrorLog"
Write-Host "  $frontendLog"
Write-Host "  $frontendErrorLog"
