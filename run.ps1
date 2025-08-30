$ErrorActionPreference = "Stop"

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Create venv if missing
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating venv..."
    python -m venv .venv
}

# Activate venv
$activate = Join-Path (Get-Location) ".venv/Scripts/Activate.ps1"
. $activate

# Upgrade pip and install deps
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --disable-pip-version-check

# Run mode selection
Write-Host "Select mode: 1) Web UI  2) Console runner"
$mode = Read-Host "Enter 1 or 2"
if ($mode -eq "2") {
  Write-Host "Starting console runner"
  python -m src.console_runner
} else {
  Write-Host "Starting server on 0.0.0.0:8000"
  python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
}
