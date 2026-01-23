# 🚀 Run Locally - Quick Start Guide

## Option 2: Local Development Setup (2-3 minutes)

This guide will get your app running locally without Docker for quick testing.

---

## Step 1: Navigate to Backend Directory

```powershell
cd backend
```

---

## Step 2: Create Virtual Environment

```powershell
python -m venv venv
```

---

## Step 3: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 4: Install Core Dependencies

```powershell
# Install minimal dependencies for quick start
pip install fastapi uvicorn[standard] pydantic pydantic-settings python-dotenv sqlalchemy asyncpg httpx aiohttp openai anthropic numpy
```

---

## Step 5: Set Environment Variables

```powershell
# Set your API keys
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"

# Set environment
$env:ENVIRONMENT="development"
$env:LOG_LEVEL="INFO"
```

---

## Step 6: Start the Application

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verify It's Running

Open your browser and visit:

- **API Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Test the API

### Using PowerShell:

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Test admin statistics
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/statistics"
```

### Using curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test admin statistics
curl http://localhost:8000/api/v1/admin/statistics
```

---

## 📝 Notes

### What Works:
- ✅ FastAPI server
- ✅ API endpoints
- ✅ OpenAI integration
- ✅ Anthropic integration
- ✅ Basic validation

### What Won't Work (without databases):
- ❌ Database operations (PostgreSQL, MongoDB)
- ❌ Caching (Redis)
- ❌ Historical data queries
- ❌ Data persistence

---

## 🛑 Stop the Application

Press `Ctrl+C` in the terminal where uvicorn is running.

---

## 🔄 Restart

If you close the terminal, you'll need to:

1. Reactivate the virtual environment:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   ```

2. Set environment variables again:
   ```powershell
   $env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
   $env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
   ```

3. Start the server:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 🐳 Alternative: Use Docker (Full System)

If you want the complete system with databases, use Docker instead:

```powershell
# From project root
docker-compose --env-file .env.docker up -d
```

This will start:
- Backend API (port 8000)
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Redis (port 6379)

---

## 📊 Quick Command Reference

```powershell
# Activate environment
cd backend
.\venv\Scripts\Activate.ps1

# Set keys
$env:OPENAI_API_KEY="your-key"
$env:ANTHROPIC_API_KEY="your-key"

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

---

**Ready to go!** 🎉

Your app should now be running at http://localhost:8000
