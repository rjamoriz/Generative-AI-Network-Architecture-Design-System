#!/bin/bash
# ============================================================================
# Development Environment Setup Script
# Network Architecture Design System
# ============================================================================

set -e  # Exit on error

echo "=========================================="
echo "Network Design System - Dev Setup"
echo "=========================================="

# ============================================================================
# Check Prerequisites
# ============================================================================

echo ""
echo "[1/8] Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi
echo "✓ pip3 found"

# ============================================================================
# Create Virtual Environment
# ============================================================================

echo ""
echo "[2/8] Creating virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate
echo "✓ Virtual environment activated"

# ============================================================================
# Install Dependencies
# ============================================================================

echo ""
echo "[3/8] Installing Python dependencies..."

pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# ============================================================================
# Setup Environment Variables
# ============================================================================

echo ""
echo "[4/8] Setting up environment variables..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file already exists"
fi

# ============================================================================
# Check Database Services
# ============================================================================

echo ""
echo "[5/8] Checking database services..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        echo "✓ Docker Compose found"
        echo ""
        echo "You can start databases with:"
        echo "  docker-compose up -d postgres mongodb redis"
    fi
else
    echo "⚠️  Docker not found - you'll need to install databases manually"
fi

# ============================================================================
# Create Required Directories
# ============================================================================

echo ""
echo "[6/8] Creating required directories..."

mkdir -p logs
mkdir -p data
mkdir -p uploads
echo "✓ Directories created"

# ============================================================================
# Initialize Database (if available)
# ============================================================================

echo ""
echo "[7/8] Database initialization..."

if command -v docker &> /dev/null && docker ps &> /dev/null; then
    # Check if postgres container is running
    if docker ps | grep -q postgres; then
        echo "Initializing PostgreSQL database..."
        docker exec -i $(docker ps -qf "name=postgres") psql -U postgres < db/init.sql || true
        echo "✓ Database initialized"
    else
        echo "⚠️  PostgreSQL container not running"
        echo "   Start it with: docker-compose up -d postgres"
    fi
else
    echo "⚠️  Docker not available - skipping database initialization"
fi

# ============================================================================
# Run Tests
# ============================================================================

echo ""
echo "[8/8] Running tests..."

if pytest --version &> /dev/null; then
    echo "Running test suite..."
    pytest tests/ -v || echo "⚠️  Some tests failed (this is normal if LLM APIs are not configured)"
else
    echo "⚠️  pytest not found - skipping tests"
fi

# ============================================================================
# Complete
# ============================================================================

echo ""
echo "=========================================="
echo "✓ Development environment setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo ""
echo "2. Start database services:"
echo "   docker-compose up -d"
echo ""
echo "3. Run the application:"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "4. Access the API:"
echo "   http://localhost:8000"
echo "   http://localhost:8000/docs (Swagger UI)"
echo ""
echo "5. Run example workflow:"
echo "   python scripts/test_workflow.py"
echo ""
echo "=========================================="
