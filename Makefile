# Makefile for Network Architecture Design System
# Provides convenient commands for Docker operations

.PHONY: help build up down restart logs clean test health

# Default target
help:
	@echo "Network Architecture Design System - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs (all services)"
	@echo "  make logs-backend - View backend logs"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make test      - Run tests in backend container"
	@echo "  make health    - Check service health"
	@echo "  make shell     - Access backend shell"
	@echo "  make db        - Access PostgreSQL shell"
	@echo "  make mongo     - Access MongoDB shell"
	@echo "  make redis     - Access Redis CLI"
	@echo ""

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@make health

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Restart all services
restart:
	@echo "Restarting all services..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-postgres:
	docker-compose logs -f postgres

logs-mongodb:
	docker-compose logs -f mongodb

logs-redis:
	docker-compose logs -f redis

# Clean up
clean:
	@echo "Removing containers and volumes..."
	docker-compose down -v
	@echo "Pruning unused Docker resources..."
	docker system prune -f

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec backend pytest tests/ -v --cov=app

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend not ready"
	@docker-compose exec postgres pg_isready -U postgres || echo "PostgreSQL not ready"
	@docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" || echo "MongoDB not ready"
	@docker-compose exec redis redis-cli ping || echo "Redis not ready"

# Shell access
shell:
	docker-compose exec backend bash

db:
	docker-compose exec postgres psql -U postgres -d network_designs

mongo:
	docker-compose exec mongodb mongosh

redis:
	docker-compose exec redis redis-cli

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@cp .env.docker .env.docker.local
	@echo "Please edit .env.docker.local with your configuration"

# Backup database
backup:
	@echo "Backing up PostgreSQL..."
	docker-compose exec postgres pg_dump -U postgres network_designs > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup complete"

# Status
status:
	@echo "Container status:"
	docker-compose ps
	@echo ""
	@echo "Resource usage:"
	docker stats --no-stream
