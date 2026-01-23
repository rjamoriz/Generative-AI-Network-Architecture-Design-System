# 🐳 Docker Containerization Guide
## Network Architecture Design System

Complete guide for running the system with Docker.

---

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)
- **4GB+ RAM** available for containers
- **10GB+ disk space**

---

## 🚀 Quick Start

### **Windows (PowerShell)**

```powershell
# 1. Configure environment
Copy-Item .env.docker .env.docker.local
# Edit .env.docker.local with your API keys

# 2. Start all services
.\docker-start.ps1

# 3. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **Linux/Mac (Bash)**

```bash
# 1. Configure environment
cp .env.docker .env.docker.local
# Edit .env.docker.local with your API keys

# 2. Start all services
chmod +x docker-start.sh
./docker-start.sh

# 3. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 🏗️ Architecture

### **Services**

The Docker setup includes 4 services:

1. **Backend API** (Port 8000)
   - FastAPI application
   - 4 Uvicorn workers
   - Health checks enabled

2. **PostgreSQL** (Port 5432)
   - Relational database
   - Persistent volume
   - Auto-initialization

3. **MongoDB** (Port 27017)
   - Document database
   - Vector embeddings storage
   - Persistent volume

4. **Redis** (Port 6379)
   - Cache layer
   - Session storage
   - Persistent volume

### **Network**

All services communicate on a private bridge network: `network-design-net`

### **Volumes**

Persistent data storage:
- `postgres-data` - PostgreSQL database files
- `mongodb-data` - MongoDB database files
- `mongodb-config` - MongoDB configuration
- `redis-data` - Redis persistence
- `backend-logs` - Application logs

---

## ⚙️ Configuration

### **Environment Variables**

Edit `.env.docker` or create `.env.docker.local`:

```bash
# Required
POSTGRES_PASSWORD=your-secure-password
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

# Optional
MONGODB_USERNAME=admin
MONGODB_PASSWORD=secure-password
REDIS_PASSWORD=redis-password
```

### **Resource Limits**

Default resource allocation:
- Backend: 2GB RAM, 2 CPU cores
- PostgreSQL: 1GB RAM, 1 CPU core
- MongoDB: 2GB RAM, 1 CPU core
- Redis: 512MB RAM, 0.5 CPU cores

To modify, edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🎯 Usage

### **Start Services**

```powershell
# Windows
.\docker-start.ps1

# Linux/Mac
./docker-start.sh
```

This will:
1. Stop any existing containers
2. Build Docker images
3. Start all services
4. Wait for health checks
5. Display service URLs

### **Stop Services**

```powershell
# Windows
.\docker-stop.ps1

# Linux/Mac
./docker-stop.sh
```

### **View Logs**

```powershell
# All services
.\docker-logs.ps1

# Specific service
.\docker-logs.ps1 backend
.\docker-logs.ps1 postgres
.\docker-logs.ps1 mongodb
.\docker-logs.ps1 redis
```

### **Restart Services**

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

---

## 🔍 Verification

### **Health Checks**

```bash
# Backend API
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/api/v1/metrics/health/detailed

# PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Redis
docker-compose exec redis redis-cli ping
```

### **Service Status**

```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# View networks
docker network ls

# View volumes
docker volume ls
```

---

## 🛠️ Development Mode

### **Live Code Reload**

The backend service mounts your local code:

```yaml
volumes:
  - ./backend/app:/app/app  # Live reload
```

Changes to Python files will automatically reload the server.

### **Access Container Shell**

```bash
# Backend
docker-compose exec backend bash

# PostgreSQL
docker-compose exec postgres psql -U postgres -d network_designs

# MongoDB
docker-compose exec mongodb mongosh

# Redis
docker-compose exec redis redis-cli
```

### **Run Tests**

```bash
# Inside backend container
docker-compose exec backend pytest tests/ -v

# Or from host
docker-compose exec backend python -m pytest tests/ -v --cov=app
```

---

## 📊 Database Management

### **PostgreSQL**

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d network_designs

# Backup database
docker-compose exec postgres pg_dump -U postgres network_designs > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d network_designs

# View tables
docker-compose exec postgres psql -U postgres -d network_designs -c "\dt"
```

### **MongoDB**

```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh

# List databases
docker-compose exec mongodb mongosh --eval "show dbs"

# Backup database
docker-compose exec mongodb mongodump --out=/data/backup

# Restore database
docker-compose exec mongodb mongorestore /data/backup
```

### **Redis**

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View all keys
docker-compose exec redis redis-cli KEYS '*'

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## 🔧 Troubleshooting

### **Port Already in Use**

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### **Container Won't Start**

```bash
# View logs
docker-compose logs backend

# Check container status
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache backend
docker-compose up -d
```

### **Database Connection Failed**

```bash
# Check if database is ready
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### **Out of Memory**

```bash
# Check resource usage
docker stats

# Increase Docker Desktop memory
# Settings → Resources → Memory → Increase to 8GB

# Reduce worker count in Dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### **Slow Performance**

```bash
# Check resource allocation
docker stats

# Optimize volumes (Windows)
# Use WSL2 backend in Docker Desktop settings

# Prune unused resources
docker system prune -a
docker volume prune
```

---

## 🧹 Cleanup

### **Stop and Remove Containers**

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove everything
docker-compose down -v --rmi all
```

### **Remove Unused Resources**

```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 📦 Building for Production

### **Build Optimized Images**

```bash
# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Tag for registry
docker tag network-design-backend:latest your-registry/network-design-backend:v1.0.0

# Push to registry
docker push your-registry/network-design-backend:v1.0.0
```

### **Production Environment**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
      - WORKERS=8
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔐 Security Best Practices

### **1. Use Secrets**

```bash
# Create secrets file
echo "my-secret-password" | docker secret create postgres_password -

# Use in docker-compose.yml
secrets:
  postgres_password:
    external: true
```

### **2. Non-Root User**

Already configured in Dockerfile:

```dockerfile
USER appuser
```

### **3. Network Isolation**

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

### **4. Read-Only Filesystem**

```yaml
services:
  backend:
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
```

---

## 📈 Monitoring

### **Container Metrics**

```bash
# Real-time stats
docker stats

# Export metrics
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### **Application Metrics**

```bash
# Prometheus metrics
curl http://localhost:8000/api/v1/metrics/prometheus

# System metrics
curl http://localhost:8000/api/v1/metrics/system

# Application metrics
curl http://localhost:8000/api/v1/metrics/application
```

### **Log Aggregation**

```bash
# Follow all logs
docker-compose logs -f

# Export logs
docker-compose logs > application.log

# Filter logs
docker-compose logs backend | grep ERROR
```

---

## 🚀 Deployment Options

### **1. Docker Compose (Development)**

```bash
docker-compose up -d
```

**Pros**: Simple, fast setup  
**Cons**: Single host, limited scaling

### **2. Docker Swarm (Production)**

```bash
docker swarm init
docker stack deploy -c docker-compose.yml network-design
```

**Pros**: Multi-host, built-in orchestration  
**Cons**: Less features than Kubernetes

### **3. Kubernetes (Enterprise)**

```bash
kubectl apply -f k8s/
```

**Pros**: Full orchestration, auto-scaling  
**Cons**: Complex setup

---

## 📞 Quick Reference

### **Essential Commands**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache

# Status
docker-compose ps

# Shell access
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Health check
curl http://localhost:8000/health
```

### **Service URLs**

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json
- **Health**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/api/v1/metrics/prometheus

---

## ✅ Checklist

Before deploying:

- [ ] Configure `.env.docker` with actual values
- [ ] Set strong passwords for databases
- [ ] Configure LLM API keys
- [ ] Test health checks
- [ ] Verify database connections
- [ ] Check resource limits
- [ ] Review security settings
- [ ] Test backup/restore procedures
- [ ] Configure monitoring
- [ ] Document custom configurations

---

**Ready to containerize!** 🐳

For issues or questions, refer to:
- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Documentation](https://docs.docker.com/compose)
- Project `README.md`
