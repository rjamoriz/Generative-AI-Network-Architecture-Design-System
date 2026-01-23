# Docker Start Script for Network Architecture Design System (PowerShell)
# This script builds and starts all Docker containers

$ErrorActionPreference = "Stop"

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Network Architecture Design System - Docker Startup" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env.docker")) {
    Write-Host "⚠ .env.docker not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env.docker.local"
    Write-Host "⚠ Please edit .env.docker.local with your actual values" -ForegroundColor Yellow
    Write-Host ""
}

# Check for required environment variables
if (Test-Path ".env.docker") {
    $envContent = Get-Content ".env.docker"
    
    $hasOpenAI = $envContent | Select-String "OPENAI_API_KEY=(?!your-openai-api-key-here)"
    $hasPostgres = $envContent | Select-String "POSTGRES_PASSWORD=(?!your-secure-password-here)"
    
    if (-not $hasOpenAI) {
        Write-Host "⚠ WARNING: OPENAI_API_KEY not set or using placeholder" -ForegroundColor Yellow
    }
    
    if (-not $hasPostgres) {
        Write-Host "⚠ WARNING: POSTGRES_PASSWORD not set or using placeholder" -ForegroundColor Yellow
    }
}

Write-Host "=== Step 1: Stopping existing containers ===" -ForegroundColor Cyan
docker-compose down
Write-Host "✓ Containers stopped" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 2: Building Docker images ===" -ForegroundColor Cyan
docker-compose build --no-cache
Write-Host "✓ Images built" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 3: Starting services ===" -ForegroundColor Cyan
docker-compose up -d
Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 4: Waiting for services to be ready ===" -ForegroundColor Cyan

Write-Host "Waiting for PostgreSQL..." -NoNewline
do {
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
    $pgReady = docker-compose exec -T postgres pg_isready -U postgres 2>&1
} while ($LASTEXITCODE -ne 0)
Write-Host ""
Write-Host "✓ PostgreSQL ready" -ForegroundColor Green

Write-Host "Waiting for MongoDB..." -NoNewline
do {
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
    $mongoReady = docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" 2>&1
} while ($LASTEXITCODE -ne 0)
Write-Host ""
Write-Host "✓ MongoDB ready" -ForegroundColor Green

Write-Host "Waiting for Redis..." -NoNewline
do {
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
    $redisReady = docker-compose exec -T redis redis-cli ping 2>&1
} while ($LASTEXITCODE -ne 0)
Write-Host ""
Write-Host "✓ Redis ready" -ForegroundColor Green

Write-Host "Waiting for Backend API..." -NoNewline
Start-Sleep -Seconds 10
do {
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 3
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        $apiReady = $true
    } catch {
        $apiReady = $false
    }
} while (-not $apiReady)
Write-Host ""
Write-Host "✓ Backend API ready" -ForegroundColor Green
Write-Host ""

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "✓ All services are running!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:"
Write-Host "  - Backend API:    http://localhost:8000"
Write-Host "  - API Docs:       http://localhost:8000/docs"
Write-Host "  - PostgreSQL:     localhost:5432"
Write-Host "  - MongoDB:        localhost:27017"
Write-Host "  - Redis:          localhost:6379"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  - View logs:      docker-compose logs -f"
Write-Host "  - Stop services:  docker-compose down"
Write-Host "  - Restart:        docker-compose restart"
Write-Host ""
Write-Host "Health check:"
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
$health | ConvertTo-Json
Write-Host ""
