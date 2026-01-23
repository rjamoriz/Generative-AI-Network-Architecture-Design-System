# Docker Deployment Guide

## Overview

This guide covers deploying the Network Architecture Design System using Docker and Docker Compose with full Postgres integration, vector storage, and audit logging.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM available
- 20GB free disk space

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

**Required environment variables:**

```bash
# LLM Provider (at least one required)
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

# Database
POSTGRES_PASSWORD=your-secure-password

# Security
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
API_KEY_SALT=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Vector Store (choose one)
VECTOR_STORE_PROVIDER=mongodb  # or datastax
# If using DataStax:
DATASTAX_TOKEN=your-token
DATASTAX_ENDPOINT=https://your-endpoint.apps.astra.datastax.com

# Salesforce (optional)
SALESFORCE_ENABLED=false
```

### 2. Build and Start Services

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Verify Deployment

```bash
# Check service health
docker-compose ps

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

## Architecture

### Services

1. **Backend (FastAPI)** - Port 8000
   - Python 3.11
   - Async SQLAlchemy + Alembic migrations
   - Multi-agent AI system
   - Automatic database migration on startup

2. **Frontend (Next.js)** - Port 3000
   - React 18
   - TailwindCSS
   - Server-side rendering

3. **PostgreSQL** - Port 5432
   - Authoritative storage for:
     - Network designs
     - Requirements
     - Validation results
     - Audit logs

4. **MongoDB** - Port 27017
   - Vector embeddings storage
   - Historical design documents

5. **Redis** - Port 6379
   - Caching layer
   - Session storage

## Database Migrations

Migrations run automatically on backend startup via the entrypoint script.

### Manual Migration Commands

```bash
# Run migrations manually
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Data Persistence

All data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep network-design

# Backup Postgres data
docker-compose exec postgres pg_dump -U postgres network_designs > backup.sql

# Restore Postgres data
docker-compose exec -T postgres psql -U postgres network_designs < backup.sql

# Backup MongoDB data
docker-compose exec mongodb mongodump --out=/data/backup

# View volume details
docker volume inspect network-design-system_postgres-data
```

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Access Containers

```bash
# Backend shell
docker-compose exec backend bash

# Postgres shell
docker-compose exec postgres psql -U postgres -d network_designs

# MongoDB shell
docker-compose exec mongodb mongosh

# Redis CLI
docker-compose exec redis redis-cli
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Use Nginx load balancer (uncomment in docker-compose.yml)
```

### Resource Limits

Edit `docker-compose.yml` to add resource constraints:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secret keys
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up secrets management (Vault, AWS Secrets Manager)
- [ ] Enable audit logging
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Enable health checks
- [ ] Configure monitoring (Prometheus, Grafana)

### Environment-Specific Configs

```bash
# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait for postgres healthcheck
# 2. Missing environment variables - check .env file
# 3. Migration errors - check alembic logs
```

### Database connection errors

```bash
# Verify Postgres is running
docker-compose exec postgres pg_isready -U postgres

# Check connection from backend
docker-compose exec backend python -c "from app.core.database import test_connection; test_connection()"

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

### Frontend can't reach backend

```bash
# Check backend health
curl http://localhost:8000/health

# Verify network
docker network inspect network-design-system_network-design-net

# Check CORS settings in .env
CORS_ORIGINS=["http://localhost:3000"]
```

### Out of disk space

```bash
# Clean up unused images
docker system prune -a

# Remove old volumes (WARNING: destroys data)
docker volume prune

# Check disk usage
docker system df
```

## API Endpoints

### Backend (http://localhost:8000)

- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- `POST /api/v1/design/generate` - Generate network design
- `POST /api/v1/validation/validate` - Validate design
- `POST /api/v1/historical/upload` - Upload PDF documents
- `GET /api/v1/audit/logs` - View audit logs
- `GET /api/v1/design/list` - List designs

### Frontend (http://localhost:3000)

- `/` - Home page
- `/upload` - Upload documents
- `/validate` - Validate designs
- `/design/new` - Generate new design
- `/audit` - View audit logs

## Updates & Maintenance

### Update Images

```bash
# Pull latest images
docker-compose pull

# Rebuild with latest code
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Run daily via cron

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup Postgres
docker-compose exec -T postgres pg_dump -U postgres network_designs > $BACKUP_DIR/postgres.sql

# Backup MongoDB
docker-compose exec mongodb mongodump --out=/data/backup
docker cp network-design-mongodb:/data/backup $BACKUP_DIR/mongodb

# Backup volumes
docker run --rm -v network-design-system_postgres-data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres-data.tar.gz /data

echo "Backup completed: $BACKUP_DIR"
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review health: `docker-compose ps`
- Inspect services: `docker-compose exec <service> bash`
