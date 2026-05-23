$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Venv = Join-Path $Root ".venv_local"
$Python = Join-Path $Venv "Scripts\python.exe"
$TmpDir = Join-Path $Root ".tmp"
$BackendLog = Join-Path $TmpDir "backend.log"
$BackendErrorLog = Join-Path $TmpDir "backend.err.log"

Write-Host "Starting GestAchats - Django API + static HTML/CSS frontend" -ForegroundColor Cyan
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

New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

Write-Host "Launching backend on http://localhost:8000 ..."
$BackendProcess = Start-Process -FilePath $Python `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" `
    -WorkingDirectory $Backend `
    -RedirectStandardOutput $BackendLog `
    -RedirectStandardError $BackendErrorLog `
    -PassThru `
    -WindowStyle Hidden

Write-Host ""
Write-Host "Application started." -ForegroundColor Green
Write-Host "Frontend: http://localhost:8000/"
Write-Host "Static file: $(Join-Path $Root "frontend\index.html")"
Write-Host "Backend : http://localhost:8000"
Write-Host "Admin   : http://localhost:8000/admin"
Write-Host ""
Write-Host "Backend PID: $($BackendProcess.Id)"
Write-Host "Logs:"
Write-Host "  $BackendLog"
Write-Host "  $BackendErrorLog"
