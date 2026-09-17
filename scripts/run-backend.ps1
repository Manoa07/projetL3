$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$env:PYTHONPATH = Join-Path $projectRoot "Backend\app"
$env:API_BASE_URL = "http://127.0.0.1:8000"

Push-Location (Join-Path $projectRoot "Backend\app")
try {
    & $python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}