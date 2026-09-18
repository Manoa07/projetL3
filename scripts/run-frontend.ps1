$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$env:API_BASE_URL = "http://127.0.0.1:8000"
$env:CAMERA_SOURCES = "1,0"

Push-Location (Join-Path $projectRoot "frontend")
try {
    & $python main.py
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}