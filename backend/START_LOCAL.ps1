# Quick Start - Run from backend directory
# Activate virtual environment, set keys, and start server

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Setting environment variables..." -ForegroundColor Yellow
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
$env:ENVIRONMENT="development"
$env:JWT_SECRET_KEY="dev-secret-key-for-local-testing"

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --quiet fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv sqlalchemy asyncpg httpx aiohttp openai anthropic numpy python-jose motor pymongo redis structlog

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "API will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/health" -ForegroundColor White
Write-Host "  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
