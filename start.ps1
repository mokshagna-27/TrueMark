# One-command local start (Windows PowerShell): backend on :8000, frontend on :5173
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv)) { py -m venv .venv }
. .\.venv\Scripts\Activate.ps1
pip install -q -r backend/requirements.txt
if (-not (Test-Path frontend\.env.local)) { Copy-Item frontend\.env.example frontend\.env.local }
Push-Location frontend; npm ci; Pop-Location
$backend = Start-Process -PassThru -NoNewWindow python -ArgumentList "-m","uvicorn","main:app","--reload","--host","127.0.0.1","--port","8000" -WorkingDirectory backend
try { Push-Location frontend; npm run dev } finally { Pop-Location; Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue }
