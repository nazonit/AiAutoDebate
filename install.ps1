$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "Creating venv..."
python -m venv .venv
. ./.venv/Scripts/Activate.ps1
Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --disable-pip-version-check
Write-Host "Creating storage and logs directories..."
New-Item -ItemType Directory -Force -Path ./logs | Out-Null
New-Item -ItemType Directory -Force -Path ./storage | Out-Null
New-Item -ItemType Directory -Force -Path ./storage/prompts | Out-Null
Write-Host "Done. Use start_web.ps1 or run.ps1 to start the app."
