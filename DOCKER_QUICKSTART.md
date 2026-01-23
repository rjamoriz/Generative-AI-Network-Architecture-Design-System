# 🚀 Docker Quick Start
## Get Running in 5 Minutes

---

## Step 1: Prerequisites ✅

Make sure you have:
- ✅ Docker Desktop installed and running
- ✅ 4GB+ RAM available
- ✅ 10GB+ disk space

**Check Docker:**
```powershell
docker --version
docker-compose --version
```

---

## Step 2: Configure Environment ⚙️

### **Windows**

```powershell
# Copy environment template
Copy-Item .env.docker .env.docker.local

# Edit with your API keys
notepad .env.docker.local
```

### **Linux/Mac**

```bash
# Copy environment template
cp .env.docker .env.docker.local

# Edit with your API keys
nano .env.docker.local
```

### **Required Configuration**

Edit these values in `.env.docker.local`:

```bash
# Set a strong password
POSTGRES_PASSWORD=your-secure-password-here

# Add your LLM API keys
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
```

---

## Step 3: Start Services 🚀

### **Option A: Using Scripts (Recommended)**

**Windows:**
```powershell
.\docker-start.ps1
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### **Option B: Using Docker Compose**

```bash
docker-compose up -d
```

### **Option C: Using Makefile**

```bash
make up
```

---

## Step 4: Verify Everything Works ✅

### **Check Health**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-13T12:00:00Z"
}
```

### **Access API Documentation**

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Check All Services**

```bash
docker-compose ps
```

All services should show "Up" status:
```
NAME                        STATUS
network-design-backend      Up (healthy)
network-design-postgres     Up (healthy)
network-design-mongodb      Up (healthy)
network-design-redis        Up (healthy)
```

---

## Step 5: Test the API 🧪

### **Simple Test**

```bash
# Get admin statistics
curl http://localhost:8000/api/v1/admin/statistics

# List validation rules
curl http://localhost:8000/api/v1/admin/rules
```

### **Full Workflow Test**

```bash
# Run the test workflow script
docker-compose exec backend python scripts/test_workflow.py
```

---

## 🎉 You're Running!

Your services are now available at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:8000 | Main API |
| **API Docs** | http://localhost:8000/docs | Interactive documentation |
| **PostgreSQL** | localhost:5432 | Relational database |
| **MongoDB** | localhost:27017 | Document database |
| **Redis** | localhost:6379 | Cache layer |

---

## 📊 Common Commands

### **View Logs**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### **Stop Services**

```bash
# Using script
.\docker-stop.ps1  # Windows
./docker-stop.sh   # Linux/Mac

# Using Docker Compose
docker-compose down
```

### **Restart Services**

```bash
docker-compose restart
```

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

---

## 🔧 Troubleshooting

### **Port Already in Use**

```bash
# Windows - Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F

# Or change port in docker-compose.yml
```

### **Container Won't Start**

```bash
# View logs
docker-compose logs backend

# Rebuild
docker-compose build --no-cache backend
docker-compose up -d
```

### **Database Connection Failed**

```bash
# Check database is ready
docker-compose exec postgres pg_isready

# Restart database
docker-compose restart postgres
```

### **Out of Memory**

```bash
# Check usage
docker stats

# Increase Docker Desktop memory
# Settings → Resources → Memory → 8GB
```

---

## 🧹 Clean Up

### **Stop Everything**

```bash
docker-compose down
```

### **Remove Volumes Too**

```bash
docker-compose down -v
```

### **Complete Cleanup**

```bash
docker-compose down -v --rmi all
docker system prune -a --volumes
```

---

## 📚 Next Steps

1. **Read Full Guide**: See `DOCKER_GUIDE.md` for detailed documentation
2. **Configure Production**: Check `docker-compose.prod.yml` for production settings
3. **Set Up Monitoring**: Configure Prometheus and Grafana
4. **Deploy to Cloud**: Follow `DEPLOYMENT_GUIDE.md`

---

## 🆘 Need Help?

- **Docker Issues**: Check `DOCKER_GUIDE.md` troubleshooting section
- **API Issues**: View logs with `docker-compose logs -f backend`
- **Database Issues**: Check database logs and health checks
- **General Help**: See main `README.md`

---

**That's it!** You're now running the complete Network Architecture Design System in Docker. 🎉
