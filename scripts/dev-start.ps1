param(
    [switch]$Frontend
)

$repoRoot = Split-Path $PSScriptRoot -Parent
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"

Write-Host "Starting FastAPI backend with uvicorn..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location `"$backendDir`"; uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "Starting Celery worker..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location `"$backendDir`"; celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info"

if ($Frontend) {
    Write-Host "Starting Vite dev server..."
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location `"$frontendDir`"; npm run dev"
}
