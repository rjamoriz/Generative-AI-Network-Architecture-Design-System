#!/bin/bash

# Docker Start Script for Network Architecture Design System
# This script builds and starts all Docker containers

set -e  # Exit on error

echo "=============================================================================="
echo "Network Architecture Design System - Docker Startup"
echo "=============================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check for .env file
if [ ! -f ".env.docker" ]; then
    echo -e "${YELLOW}⚠ .env.docker not found. Creating from template...${NC}"
    cp .env.docker .env.docker.local
    echo -e "${YELLOW}⚠ Please edit .env.docker.local with your actual values${NC}"
    echo ""
fi

# Check for required environment variables
if [ -f ".env.docker" ]; then
    source .env.docker
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
        echo -e "${YELLOW}⚠ WARNING: OPENAI_API_KEY not set or using placeholder${NC}"
    fi
    
    if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your-secure-password-here" ]; then
        echo -e "${YELLOW}⚠ WARNING: POSTGRES_PASSWORD not set or using placeholder${NC}"
    fi
fi

echo "=== Step 1: Stopping existing containers ==="
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

echo "=== Step 2: Building Docker images ==="
docker-compose build --no-cache
echo -e "${GREEN}✓ Images built${NC}"
echo ""

echo "=== Step 3: Starting services ==="
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

echo "=== Step 4: Waiting for services to be ready ==="
echo "Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL ready${NC}"

echo "Waiting for MongoDB..."
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✓ MongoDB ready${NC}"

echo "Waiting for Redis..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✓ Redis ready${NC}"

echo "Waiting for Backend API..."
sleep 10  # Give backend time to start
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo -n "."
    sleep 3
done
echo -e "${GREEN}✓ Backend API ready${NC}"
echo ""

echo "=============================================================================="
echo -e "${GREEN}✓ All services are running!${NC}"
echo "=============================================================================="
echo ""
echo "Service URLs:"
echo "  - Backend API:    http://localhost:8000"
echo "  - API Docs:       http://localhost:8000/docs"
echo "  - PostgreSQL:     localhost:5432"
echo "  - MongoDB:        localhost:27017"
echo "  - Redis:          localhost:6379"
echo ""
echo "Useful commands:"
echo "  - View logs:      docker-compose logs -f"
echo "  - Stop services:  docker-compose down"
echo "  - Restart:        docker-compose restart"
echo ""
echo "Health check:"
curl -s http://localhost:8000/health | python -m json.tool
echo ""
