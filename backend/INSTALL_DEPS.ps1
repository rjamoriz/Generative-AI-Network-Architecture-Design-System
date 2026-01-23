# Install dependencies one by one to avoid path length issues
# Run this from the backend directory with venv activated

Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host ""

# Core FastAPI
pip install fastapi==0.109.0
pip install "uvicorn[standard]==0.27.0"
pip install pydantic==2.5.3
pip install pydantic-settings==2.1.0

# Utilities
pip install python-dotenv==1.0.0
pip install python-dateutil==2.8.2

# Database
pip install sqlalchemy==2.0.25
pip install asyncpg==0.29.0
pip install motor==3.3.2
pip install pymongo==4.6.1
pip install redis==5.0.1

# HTTP
pip install httpx==0.26.0
pip install aiohttp==3.9.1

# LLM APIs
pip install openai==1.10.0
pip install anthropic==0.8.1

# Security
pip install "python-jose[cryptography]==3.3.0"

# Logging
pip install structlog==24.1.0

# Numpy (lightweight version)
pip install numpy==1.26.3

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
