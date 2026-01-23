# Docker Startup Analysis & Solutions

## 🔍 Current Situation

**Status**: App failing to start in Docker  
**Root Cause**: Missing dependencies in minimal requirements  
**Error**: `ModuleNotFoundError: No module named 'oracledb'`

---

## 📊 Issues Identified

### **1. Dependency Chain Problems**

The app has a complex dependency chain:
```
main.py 
  → routes (design, validation, historical, etc.)
    → agents (requirement_analyzer, design_synthesizer, validation_agent)
      → services (rag_service, llm_service, embedding_service)
        → integrations (external_db_connector, mcp_client)
          → REQUIRES: oracledb, langchain, sentence-transformers, torch, etc.
```

### **2. Missing Dependencies in Minimal Build**

**Currently Missing**:
- `oracledb` - Oracle database connector
- `langchain` + related packages - LLM framework
- `sentence-transformers` - Embeddings
- `torch` - ML framework (HUGE - 2GB+)
- `psutil` - System metrics
- `hvac` - Vault integration
- Many others...

### **3. Build Time Issues**

**Full requirements.txt** includes:
- 145 packages
- PyTorch (2GB+)
- CUDA libraries (1GB+)
- Total build time: 10-15 minutes
- Total image size: 8-10GB

---

## 💡 Solution Options

### **Option 1: Use Full Requirements (Slow but Complete)** ⏱️

**Time**: 15-20 minutes  
**Size**: 8-10GB  
**Status**: Ready to use

```powershell
# Use the full docker-compose.yml with all dependencies
docker-compose up -d --build
```

**Pros**:
- Everything works
- All features available
- Production-ready

**Cons**:
- Very slow first build
- Large image size
- Requires good internet connection

---

### **Option 2: Make Code Optional-Dependency Friendly** 🔧

**Time**: 30 minutes  
**Effort**: Code modifications needed

Modify the code to make heavy dependencies optional:

```python
# Example: Make oracledb optional
try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    oracledb = None
```

**Pros**:
- Fast startup for testing
- Smaller image
- Graceful degradation

**Cons**:
- Requires code changes
- Some features won't work
- Need to test all import paths

---

### **Option 3: Run Without Docker (Fastest)** ⚡

**Time**: 2-3 minutes  
**Complexity**: Low

```powershell
# 1. Create virtual environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install minimal dependencies
pip install fastapi uvicorn pydantic sqlalchemy

# 3. Run directly
uvicorn app.main:app --reload
```

**Pros**:
- Fastest to get running
- Easy to debug
- No Docker overhead

**Cons**:
- No database services
- Missing many dependencies
- Not production-like

---

### **Option 4: Stub Out Heavy Dependencies** 🎭

**Time**: 15 minutes  
**Effort**: Create mock modules

Create stub files for missing modules:

```python
# backend/app/stubs/oracledb.py
class Connection:
    pass

def connect(*args, **kwargs):
    raise NotImplementedError("Oracle not available in minimal mode")
```

**Pros**:
- App starts quickly
- Can test basic functionality
- Small image size

**Cons**:
- Features using stubs won't work
- Requires maintenance
- Not suitable for real testing

---

## 🎯 Recommended Approach

### **For Quick Demo/Testing**: Option 3 (Run Without Docker)

```powershell
# Quick start (5 minutes)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] pydantic python-dotenv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **For Full System**: Option 1 (Full Docker Build)

```powershell
# Complete system (20 minutes)
docker-compose --env-file .env.docker up -d --build
```

---

## 📝 Current Docker Files Available

1. **`docker-compose.yml`** - Full stack (backend + postgres + mongodb + redis)
2. **`docker-compose.simple.yml`** - Backend only (still needs full deps)
3. **`docker-compose.minimal.yml`** - Attempted minimal (failing)

---

## 🚀 Quick Fix Commands

### **Stop Current Failing Container**
```powershell
docker-compose -f docker-compose.minimal.yml down
```

### **Start Full System**
```powershell
# This will take 15-20 minutes on first build
docker-compose --env-file .env.docker up -d --build
```

### **Or Run Locally (Fastest)**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt  # Or minimal subset
$env:OPENAI_API_KEY="sk-test"
$env:ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY_HERE"
uvicorn app.main:app --reload
```

---

## 📊 Dependency Analysis

### **Core (Required)**
- fastapi, uvicorn, pydantic ✅
- sqlalchemy, asyncpg ✅
- redis, motor, pymongo ✅

### **LLM (Heavy)**
- openai, anthropic ⚠️
- langchain + extensions ⚠️
- sentence-transformers ❌ (requires torch)

### **ML/Vector (Very Heavy)**
- torch, transformers ❌ (2GB+)
- numpy ✅
- sentence-transformers ❌

### **Database Connectors**
- psycopg2-binary ✅
- asyncpg ✅
- motor ✅
- oracledb ❌ (missing)

### **Integrations**
- hvac (Vault) ❌
- boto3 (AWS) ❌
- psutil (metrics) ❌

---

## 🎬 Next Steps

**Choose your path**:

1. **Want it working NOW** → Run locally without Docker
2. **Want full system** → Use full docker-compose.yml (wait 20 min)
3. **Want to fix minimal** → Modify code to make deps optional

**My Recommendation**: Start with local run to see the app working, then do full Docker build in background.

---

## 📞 Commands Summary

```powershell
# OPTION A: Local (2 minutes)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] pydantic
uvicorn app.main:app --reload

# OPTION B: Full Docker (20 minutes)
docker-compose down
docker-compose --env-file .env.docker up -d --build

# OPTION C: Check what's running
docker ps
docker logs network-design-backend-minimal
```

---

**Current Status**: Minimal Docker build failing due to missing `oracledb` and other heavy dependencies.

**Best Next Action**: Choose Option A (local) or Option B (full Docker) above.
