# Docker Stop Script for Network Architecture Design System (PowerShell)

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Stopping Network Architecture Design System" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Stop all containers
Write-Host "Stopping containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✓ All containers stopped" -ForegroundColor Green
Write-Host ""
Write-Host "To remove volumes as well, run:"
Write-Host "  docker-compose down -v"
Write-Host ""
