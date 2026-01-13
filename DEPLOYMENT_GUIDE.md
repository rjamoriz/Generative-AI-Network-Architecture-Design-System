# Deployment Guide
## Network Architecture Design System

**Last Updated**: January 13, 2026  
**Version**: 1.0.0

---

## 📋 Overview

This guide covers deployment options for the Network Architecture Design System, from local development to production Kubernetes clusters.

---

## 🚀 Quick Start with Docker

### **Prerequisites**
- Docker 24.0+
- Docker Compose 2.20+
- 4GB RAM minimum
- 10GB disk space

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd Generative-AI-Network-Architecture-Design-System
```

### **Step 2: Configure Environment**
```bash
# Copy environment template
cp .env.docker .env

# Edit .env and add your API keys
nano .env
```

Required variables:
```bash
POSTGRES_PASSWORD=your_secure_password
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### **Step 3: Start Services**
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### **Step 4: Verify Deployment**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## 🏗️ Architecture

### **Docker Compose Stack**
```
┌─────────────────────────────────────────┐
│           Load Balancer (Nginx)         │
│              Port 80/443                │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐   ┌───▼────┐   ┌───▼────┐
│Backend │   │Backend │   │Backend │
│  API   │   │  API   │   │  API   │
│ :8000  │   │ :8001  │   │ :8002  │
└───┬────┘   └───┬────┘   └───┬────┘
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│Postgres│  │MongoDB │  │ Redis  │
│ :5432  │  │ :27017 │  │ :6379  │
└────────┘  └────────┘  └────────┘
```

### **Services**
- **Backend API**: FastAPI application (4 workers)
- **PostgreSQL**: Relational data storage
- **MongoDB**: Design documents and vector search
- **Redis**: Caching and session storage

---

## 🔧 Configuration

### **Environment Variables**

#### Application Settings
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

#### Database Connections
```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=network_designs
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password

# MongoDB
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=network_designs

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

#### LLM Providers
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai
```

#### External Databases (Optional)
```bash
HISTORICAL_DATA_ENABLED=true
EXTERNAL_POSTGRES_HOST=external-db.example.com
EXTERNAL_POSTGRES_PASSWORD=...
```

---

## 🐳 Docker Commands

### **Basic Operations**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
```

### **Database Operations**
```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d network_designs

# MongoDB shell
docker-compose exec mongodb mongosh network_designs

# Redis CLI
docker-compose exec redis redis-cli
```

### **Maintenance**
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# View resource usage
docker stats
```

---

## ☸️ Kubernetes Deployment

### **Prerequisites**
- Kubernetes 1.28+
- kubectl configured
- Helm 3.0+

### **Step 1: Create Namespace**
```bash
kubectl create namespace network-design
```

### **Step 2: Create Secrets**
```bash
# Create secret for API keys
kubectl create secret generic api-keys \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=anthropic-api-key='sk-ant-...' \
  -n network-design

# Create secret for database passwords
kubectl create secret generic db-passwords \
  --from-literal=postgres-password='secure_password' \
  -n network-design
```

### **Step 3: Deploy with Helm**
```bash
# Add Helm repository (if using Helm charts)
helm repo add network-design ./helm

# Install
helm install network-design ./helm/network-design \
  --namespace network-design \
  --values values.production.yaml
```

### **Step 4: Verify Deployment**
```bash
# Check pods
kubectl get pods -n network-design

# Check services
kubectl get svc -n network-design

# View logs
kubectl logs -f deployment/backend -n network-design
```

---

## 🔐 Security

### **SSL/TLS Configuration**
```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# Production: Use Let's Encrypt
certbot certonly --standalone -d api.yourdomain.com
```

### **Secrets Management**

#### HashiCorp Vault
```bash
# Store secrets in Vault
vault kv put secret/network-design \
  openai_api_key='sk-...' \
  anthropic_api_key='sk-ant-...'

# Configure backend to use Vault
SECRETS_PROVIDER=vault
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=your_token
```

#### AWS Secrets Manager
```bash
# Store secrets
aws secretsmanager create-secret \
  --name network-design/api-keys \
  --secret-string '{"openai":"sk-...","anthropic":"sk-ant-..."}'

# Configure backend
SECRETS_PROVIDER=aws
AWS_REGION=us-east-1
```

### **Network Security**
```yaml
# Network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
```

---

## 📊 Monitoring

### **Health Checks**
```bash
# Application health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/api/v1/admin/health/detailed
```

### **Metrics (Prometheus)**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'network-design-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### **Logging (ELK Stack)**
```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
      - logs_path:
          logs_path: "/var/log/containers/"
```

---

## 🔄 CI/CD Pipeline

### **GitHub Actions Example**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t network-design:${{ github.sha }} ./backend
      
      - name: Push to registry
        run: |
          docker push network-design:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend \
            backend=network-design:${{ github.sha }} \
            -n network-design
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Missing API keys
# 2. Database connection failed
# 3. Port already in use

# Solutions:
docker-compose down
docker-compose up -d postgres mongodb redis
# Wait 10 seconds
docker-compose up -d backend
```

#### Database connection errors
```bash
# Check database status
docker-compose ps postgres mongodb

# Restart databases
docker-compose restart postgres mongodb

# Check network
docker network inspect network-design-net
```

#### High memory usage
```bash
# Check resource usage
docker stats

# Reduce workers
# In docker-compose.yml:
command: ["uvicorn", "app.main:app", "--workers", "2"]
```

---

## 📈 Scaling

### **Horizontal Scaling**
```bash
# Scale backend replicas
docker-compose up -d --scale backend=3

# Kubernetes
kubectl scale deployment backend --replicas=5 -n network-design
```

### **Vertical Scaling**
```yaml
# docker-compose.yml
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

---

## 🔄 Backup & Recovery

### **Database Backups**
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U postgres network_designs > backup.sql

# MongoDB backup
docker-compose exec mongodb mongodump --db network_designs --out /backup

# Restore PostgreSQL
docker-compose exec -T postgres psql -U postgres network_designs < backup.sql

# Restore MongoDB
docker-compose exec mongodb mongorestore --db network_designs /backup/network_designs
```

### **Automated Backups**
```bash
# Cron job for daily backups
0 2 * * * /path/to/backup-script.sh
```

---

## 🌐 Production Checklist

- [ ] SSL/TLS certificates configured
- [ ] Secrets stored in secrets manager
- [ ] Database backups automated
- [ ] Monitoring and alerting set up
- [ ] Rate limiting configured
- [ ] CORS origins restricted
- [ ] Firewall rules configured
- [ ] Resource limits set
- [ ] Health checks enabled
- [ ] Logging centralized
- [ ] CI/CD pipeline tested
- [ ] Disaster recovery plan documented

---

## 📞 Support

### **Logs Location**
- Application: `/app/logs/`
- Docker: `docker-compose logs`
- Kubernetes: `kubectl logs`

### **Debug Mode**
```bash
# Enable debug logging
LOG_LEVEL=DEBUG docker-compose up backend
```

---

**Deployment Status**: ✅ **Production Ready**  
**Supported Platforms**: Docker, Kubernetes, AWS ECS, Azure Container Instances  
**Minimum Requirements**: 4GB RAM, 2 CPU cores, 10GB storage

---

*For additional support, consult the main README.md and API documentation at `/docs`*
