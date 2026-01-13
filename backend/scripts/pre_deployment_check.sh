#!/bin/bash

# Pre-Deployment Check Script
# Runs all verification steps before deployment

set -e  # Exit on error

echo "=============================================================================="
echo "PRE-DEPLOYMENT VERIFICATION"
echo "=============================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        FAILURES=$((FAILURES + 1))
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Change to backend directory
cd "$(dirname "$0")/.."

echo "=== Step 1: Python Version Check ==="
python --version
if [ $? -eq 0 ]; then
    print_status 0 "Python is installed"
else
    print_status 1 "Python is not installed"
fi
echo ""

echo "=== Step 2: Dependencies Check ==="
if [ -f "requirements.txt" ]; then
    print_status 0 "requirements.txt found"
    
    # Check if virtual environment exists
    if [ -d "venv" ] || [ -d ".venv" ]; then
        print_status 0 "Virtual environment found"
    else
        print_warning "No virtual environment found"
    fi
else
    print_status 1 "requirements.txt not found"
fi
echo ""

echo "=== Step 3: Environment Configuration ==="
if [ -f ".env" ]; then
    print_status 0 ".env file exists"
    
    # Check for required variables
    required_vars=("DATABASE_URL" "MONGODB_URL" "REDIS_URL" "OPENAI_API_KEY" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            print_status 0 "$var is set"
        else
            print_status 1 "$var is missing"
        fi
    done
else
    print_status 1 ".env file not found"
    print_warning "Copy .env.example to .env and configure"
fi
echo ""

echo "=== Step 4: File Structure Check ==="
required_dirs=("app/api" "app/core" "app/models" "app/agents" "app/services" "app/validation")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_status 0 "Directory exists: $dir"
    else
        print_status 1 "Directory missing: $dir"
    fi
done
echo ""

echo "=== Step 5: Docker Check ==="
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed"
    docker --version
    
    if command -v docker-compose &> /dev/null; then
        print_status 0 "Docker Compose is installed"
        docker-compose --version
    else
        print_warning "Docker Compose not found"
    fi
else
    print_warning "Docker not installed (optional for local dev)"
fi
echo ""

echo "=== Step 6: Code Verification ==="
if [ -f "scripts/verify_deployment.py" ]; then
    print_status 0 "Deployment verification script found"
    echo "Running verification script..."
    python scripts/verify_deployment.py
    if [ $? -eq 0 ]; then
        print_status 0 "Deployment verification passed"
    else
        print_status 1 "Deployment verification failed"
    fi
else
    print_warning "Deployment verification script not found"
fi
echo ""

echo "=== Step 7: Database Scripts ==="
if [ -f "db/init.sql" ]; then
    print_status 0 "Database initialization script found"
else
    print_status 1 "Database initialization script missing"
fi
echo ""

echo "=== Step 8: Documentation Check ==="
docs=("../README.md" "../DEPLOYMENT_GUIDE.md" "../DEPLOYMENT_CHECKLIST.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        print_status 0 "Found: $(basename $doc)"
    else
        print_warning "Missing: $(basename $doc)"
    fi
done
echo ""

echo "=============================================================================="
echo "VERIFICATION SUMMARY"
echo "=============================================================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo "System is ready for deployment!"
    exit 0
else
    echo -e "${RED}✗ $FAILURES CHECK(S) FAILED${NC}"
    echo "Please fix the issues before deploying"
    exit 1
fi
