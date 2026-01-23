# Quick Start Script - Run Locally
# Network Architecture Design System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Network Architecture Design System" -ForegroundColor Cyan
Write-Host "Local Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Navigate to backend
Write-Host "Step 1: Navigating to backend directory..." -ForegroundColor Yellow
Set-Location backend

# Step 2: Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Step 2: Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "Step 2: Virtual environment already exists" -ForegroundColor Green
}

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Step 4: Install dependencies
Write-Host "Step 4: Installing core dependencies..." -ForegroundColor Yellow
pip install --quiet fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv sqlalchemy asyncpg httpx aiohttp openai anthropic numpy python-jose motor pymongo redis structlog

# Step 5: Set environment variables
Write-Host "Step 5: Setting environment variables..." -ForegroundColor Yellow
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
$env:ENVIRONMENT="development"
$env:LOG_LEVEL="INFO"
$env:JWT_SECRET_KEY="dev-secret-key-for-local-testing-only"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "API will be available at:" -ForegroundColor Cyan
Write-Host "  - Health:  http://localhost:8000/health" -ForegroundColor White
Write-Host "  - Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - ReDoc:   http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Step 6: Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
