$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-Not (Test-Path ".venv")) {
  python -m venv .venv
}
. ./.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --disable-pip-version-check
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
