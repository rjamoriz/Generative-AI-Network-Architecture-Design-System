# Docker Logs Script for Network Architecture Design System (PowerShell)

param(
    [string]$Service = "all"
)

if ($Service -eq "all") {
    Write-Host "Showing logs for all services (Ctrl+C to exit)..." -ForegroundColor Cyan
    docker-compose logs -f
} else {
    Write-Host "Showing logs for $Service (Ctrl+C to exit)..." -ForegroundColor Cyan
    docker-compose logs -f $Service
}
