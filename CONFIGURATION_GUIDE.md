# Configuration Guide
## Network Architecture Design System - RAG Application

This guide explains how to configure the application to connect to all required services **without hardcoding any credentials**.

---

## 🔐 Security Principles

**CRITICAL**: This application follows security best practices:

1. ✅ **NO hardcoded credentials** - All credentials injected via environment variables
2. ✅ **NO credentials in code** - Configuration loaded from `.env` or secrets manager
3. ✅ **NO credentials in version control** - `.env` file is gitignored
4. ✅ **Supports secrets management** - HashiCorp Vault, AWS Secrets Manager
5. ✅ **Credential rotation ready** - Change credentials without code changes

---

## 📋 Quick Start

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Required Credentials

Edit `.env` and set these **minimum required** values:

```env
# At least ONE LLM provider
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=network_design_db

# At least ONE vector database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
# OR
ASTRA_DB_TOKEN=your-astra-token

# Security (production)
JWT_SECRET_KEY=generate-random-key-here
API_KEY_SALT=generate-random-salt-here
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Application

```bash
python -m app.main
```

The application will validate all credentials on startup and report any missing configurations.

---

## 🔧 Configuration Architecture

### Configuration Layers

```
┌─────────────────────────────────────────┐
│   1. Environment Variables (.env)       │  ← Default
├─────────────────────────────────────────┤
│   2. HashiCorp Vault (optional)         │  ← Production
├─────────────────────────────────────────┤
│   3. AWS Secrets Manager (optional)     │  ← Cloud
└─────────────────────────────────────────┘
```

### How It Works

1. **Configuration Loading** (`app/core/config.py`)
   - Loads settings from environment variables
   - Validates required credentials
   - Provides typed configuration objects

2. **Secrets Management** (`app/core/secrets.py`)
   - Abstracts credential retrieval
   - Supports multiple backends (env, Vault, AWS)
   - Injects credentials at runtime

3. **Service Initialization**
   - Services receive credentials via dependency injection
   - No hardcoded values in service code
   - Credentials never logged or exposed

---

## 🔌 Service Configuration

### LLM Providers

#### OpenAI

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4096
```

**Get API Key**: https://platform.openai.com/api-keys

#### Anthropic Claude

```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=4096
```

**Get API Key**: https://console.anthropic.com/

---

### Databases

#### PostgreSQL

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=network_design_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_POOL_SIZE=10
```

**Setup**:
```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=your-password \
  -e POSTGRES_DB=network_design_db \
  -p 5432:5432 \
  postgres:15
```

#### MongoDB Atlas Vector Search

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=network_vectors
MONGODB_COLLECTION=design_embeddings
```

**Setup**:
1. Create account at https://cloud.mongodb.com/
2. Create M10+ cluster (required for vector search)
3. Get connection string from "Connect" → "Connect your application"
4. Create vector search index on `embedding` field (1536 dimensions)

#### DataStax Astra DB (Alternative)

```env
ASTRA_DB_ID=your-database-id
ASTRA_DB_REGION=us-east-1
ASTRA_DB_TOKEN=AstraCS:...
ASTRA_DB_KEYSPACE=network_designs
```

**Setup**:
1. Create account at https://astra.datastax.com/
2. Create vector database
3. Generate application token
4. Copy credentials

#### Redis

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional-password
REDIS_DB=0
```

**Setup**:
```bash
# Using Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

---

### MCP Servers (External APIs)

#### Legacy Database Connector

```env
MCP_LEGACY_DB_URL=http://legacy-api.example.com
MCP_LEGACY_DB_API_KEY=your-api-key-here
```

**Purpose**: Connect to legacy Oracle/PostgreSQL databases with historical network designs

#### Web Application Connector

```env
MCP_WEB_APP_URL=http://web-app.example.com/api
MCP_WEB_APP_API_KEY=your-api-key-here
```

**Purpose**: Connect to enterprise web applications via REST APIs

---

## 🔐 Production Secrets Management

### Option 1: HashiCorp Vault

```env
USE_VAULT=true
VAULT_URL=https://vault.example.com:8200
VAULT_TOKEN=hvs.your-vault-token
VAULT_MOUNT_POINT=secret
```

**Usage**:
```python
from app.core.secrets import initialize_secrets_manager

# Initialize on startup
initialize_secrets_manager(
    use_vault=True,
    vault_config={
        'url': 'https://vault.example.com:8200',
        'token': 'hvs.token',
        'mount_point': 'secret'
    }
)
```

**Store secrets in Vault**:
```bash
vault kv put secret/network-design/openai api_key="sk-..."
vault kv put secret/network-design/postgres password="..."
```

### Option 2: AWS Secrets Manager

```python
from app.core.secrets import initialize_secrets_manager

# Initialize on startup
initialize_secrets_manager(
    use_aws=True,
    aws_region='us-east-1'
)
```

**Store secrets in AWS**:
```bash
aws secretsmanager create-secret \
  --name network-design/openai-key \
  --secret-string "sk-..."
```

---

## ✅ Configuration Validation

### Startup Validation

The application validates configuration on startup:

```python
from app.core.config import validate_configuration

# This runs automatically on startup
settings = validate_configuration()
```

**Validation checks**:
- ✓ At least one LLM provider configured
- ✓ PostgreSQL credentials present
- ✓ At least one vector database configured
- ✓ Security keys set in production
- ✓ All required environment variables present

### Check Configuration Status

```bash
curl http://localhost:8000/config/status
```

**Response**:
```json
{
  "llm_providers": {
    "openai": true,
    "anthropic": false
  },
  "databases": {
    "postgres": true,
    "mongodb": true,
    "astra": false,
    "redis": true
  },
  "mcp_servers": {
    "legacy_database": false,
    "web_application": false
  },
  "environment": "development"
}
```

---

## 🧪 Testing Configuration

### Test Database Connections

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "postgres": "healthy",
    "redis": "healthy",
    "mcp_servers": {
      "legacy_database": true,
      "web_application": false
    }
  }
}
```

### Test LLM Providers

```python
from app.services.llm_service import LLMService

service = LLMService()

# Test OpenAI
response = await service.generate("Hello", provider="openai")

# Test Claude with fallback
response = await service.generate("Hello", use_fallback=True)
```

---

## 🔄 Credential Rotation

### Rotating Credentials

1. **Update environment variable**:
   ```bash
   # Edit .env
   OPENAI_API_KEY=sk-new-key-here
   ```

2. **Restart application**:
   ```bash
   # Application will load new credentials
   python -m app.main
   ```

3. **No code changes required** ✅

### Rotating Vault Secrets

```bash
# Update secret in Vault
vault kv put secret/network-design/openai api_key="sk-new-key"

# Restart application (or implement hot-reload)
```

---

## 📊 Environment-Specific Configuration

### Development

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
JWT_SECRET_KEY=staging-secret-key
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
USE_VAULT=true
JWT_SECRET_KEY=production-secret-key-from-vault
```

---

## 🚨 Troubleshooting

### Missing Credentials Error

```
ValueError: Missing required configuration:
  - At least one LLM provider API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)
```

**Solution**: Set at least one LLM provider API key in `.env`

### Database Connection Failed

```
Failed to connect to PostgreSQL: could not connect to server
```

**Solution**: 
1. Check PostgreSQL is running
2. Verify credentials in `.env`
3. Check network connectivity

### MCP Server Unhealthy

```
MCP client for legacy_database not configured
```

**Solution**: MCP servers are optional. Set `MCP_LEGACY_DB_URL` if needed.

---

## 📚 Additional Resources

- **Configuration Reference**: `app/core/config.py`
- **Secrets Management**: `app/core/secrets.py`
- **Database Setup**: `app/core/database.py`
- **LLM Service**: `app/services/llm_service.py`
- **MCP Clients**: `app/integrations/mcp_client.py`

---

## 🔒 Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] Strong random keys generated for production
- [ ] Credentials rotated regularly
- [ ] Secrets manager configured for production
- [ ] No credentials in logs
- [ ] No credentials in error messages
- [ ] TLS enabled for all connections
- [ ] Least privilege access for database users

---

**Last Updated**: January 13, 2026
**Version**: 1.0.0
