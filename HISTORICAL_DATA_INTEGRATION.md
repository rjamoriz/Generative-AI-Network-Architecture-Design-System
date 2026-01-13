# Historical Data Integration Guide
## Connecting to External Databases for Network Design History

**Last Updated**: January 13, 2026  
**Feature**: Historical Design Data Integration

---

## 📋 Overview

The system now supports connecting to external databases containing historical network design and validation data. This enables the LLM to generate designs based on proven, validated patterns from your organization's design history.

### **Supported Databases**
- ✅ **PostgreSQL** - Primary recommended source
- ✅ **MongoDB** - Document-based design storage
- ✅ **Oracle** - Enterprise design repositories

---

## 🎯 Key Features

### **1. Historical Design Retrieval**
- Query validated designs from external databases
- Filter by network type, validation score, date range
- Rank by similarity to current requirements

### **2. Pattern Analysis**
- Analyze design patterns across time periods
- Identify most successful topologies
- Calculate average validation scores
- Topology distribution analysis

### **3. Best Practices Extraction**
- Extract insights from top-performing designs (>95% validation score)
- Identify common components and configurations
- Generate recommendations based on historical success

### **4. LLM-Enhanced Design Generation**
- Provide historical context to LLM prompts
- Generate designs based on proven patterns
- Leverage organizational knowledge

---

## 🔧 Setup Instructions

### **Step 1: Configure Environment Variables**

Add to your `.env` file:

```bash
# External PostgreSQL
EXTERNAL_POSTGRES_HOST=your-db-host.com
EXTERNAL_POSTGRES_PORT=5432
EXTERNAL_POSTGRES_DB=network_designs_history
EXTERNAL_POSTGRES_USER=readonly_user
EXTERNAL_POSTGRES_PASSWORD=your_secure_password

# Enable historical data
HISTORICAL_DATA_ENABLED=true
HISTORICAL_DATA_SOURCE=postgresql
HISTORICAL_DATA_CACHE_TTL=3600
```

### **Step 2: Database Schema Requirements**

Your external database should have a table with this structure:

#### PostgreSQL Schema
```sql
CREATE TABLE network_designs (
    design_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    network_type VARCHAR(100),
    topology_type VARCHAR(100),
    status VARCHAR(50),
    validation_score DECIMAL(3,2),
    component_count INTEGER,
    security_level VARCHAR(50),
    created_at TIMESTAMP,
    validated_at TIMESTAMP,
    design_data JSONB  -- Full design JSON
);

-- Indexes for performance
CREATE INDEX idx_network_type ON network_designs(network_type);
CREATE INDEX idx_status ON network_designs(status);
CREATE INDEX idx_validation_score ON network_designs(validation_score);
CREATE INDEX idx_created_at ON network_designs(created_at);
```

#### MongoDB Collection Structure
```json
{
  "design_id": "design_001",
  "name": "Enterprise Datacenter",
  "description": "High-availability design",
  "network_type": "enterprise_datacenter",
  "topology_type": "spine_leaf",
  "status": "validated",
  "validation_score": 0.95,
  "component_count": 12,
  "security_level": "enterprise",
  "created_at": "2025-01-01T00:00:00Z",
  "validated_at": "2025-01-02T00:00:00Z",
  "design_data": { /* full design object */ }
}
```

---

## 🌐 API Endpoints

### **1. Connect to External Database**

#### PostgreSQL
```bash
POST /api/v1/historical/connect/postgresql
Content-Type: application/json

{
  "connection_string": "postgresql://user:pass@host:5432/dbname"
}
```

#### MongoDB
```bash
POST /api/v1/historical/connect/mongodb
Content-Type: application/json

{
  "connection_string": "mongodb://user:pass@host:27017",
  "database": "historical_designs"
}
```

### **2. Query Similar Designs**

```bash
POST /api/v1/historical/query/similar-designs
Content-Type: application/json

{
  "requirements": {
    "project_name": "New Datacenter",
    "network_type": "enterprise_datacenter",
    "scale": {
      "devices": 500,
      "users": 2000,
      "sites": 2
    },
    "security_level": "enterprise"
  },
  "min_validation_score": 0.85,
  "limit": 10
}
```

**Response:**
```json
[
  {
    "design_id": "design_001",
    "name": "Enterprise DC - Spine-Leaf",
    "network_type": "enterprise_datacenter",
    "topology_type": "spine_leaf",
    "validation_score": 0.95,
    "similarity_score": 0.87,
    "component_count": 12
  }
]
```

### **3. Analyze Design Patterns**

```bash
GET /api/v1/historical/patterns/enterprise_datacenter?days_back=365
```

**Response:**
```json
{
  "total_designs": 150,
  "network_type": "enterprise_datacenter",
  "topology_distribution": {
    "spine_leaf": 85,
    "three_tier": 45,
    "collapsed_core": 20
  },
  "avg_validation_score": 0.88,
  "avg_component_count": 10.5,
  "recommended_topology": "spine_leaf"
}
```

### **4. Get Best Practices**

```bash
GET /api/v1/historical/best-practices/enterprise_datacenter/enterprise
```

**Response:**
```json
{
  "network_type": "enterprise_datacenter",
  "security_level": "enterprise",
  "sample_size": 45,
  "typical_topology": "spine_leaf",
  "avg_validation_score": 0.96,
  "recommendations": [
    "Use spine_leaf topology for optimal results",
    "Target validation score: 0.96",
    "Based on 45 highly validated designs"
  ]
}
```

### **5. Build Historical Context for LLM**

```bash
POST /api/v1/historical/context/build
Content-Type: application/json

{
  "requirements": { /* network requirements */ },
  "max_designs": 5
}
```

**Response:**
```json
{
  "context": "Historical Validated Designs (5 examples):\n\n1. Enterprise DC...",
  "max_designs": 5,
  "network_type": "enterprise_datacenter",
  "message": "Historical context built successfully"
}
```

### **6. Generate Design with Historical Data**

```bash
POST /api/v1/historical/generate-with-history
Content-Type: application/json

{
  "requirements": { /* network requirements */ },
  "use_historical": true,
  "max_historical_designs": 5
}
```

**Response:**
```json
{
  "historical_context": "Historical Validated Designs...",
  "patterns": { /* pattern analysis */ },
  "best_practices": { /* best practices */ },
  "use_historical": true,
  "message": "Historical insights generated successfully"
}
```

---

## 🔄 Complete Workflow

### **End-to-End Design Generation with Historical Data**

```bash
# Step 1: Connect to historical database
POST /api/v1/historical/connect/postgresql
{
  "connection_string": "postgresql://..."
}

# Step 2: Get historical insights
POST /api/v1/historical/generate-with-history
{
  "requirements": {
    "project_name": "New Enterprise Network",
    "network_type": "enterprise_datacenter",
    "scale": {"devices": 500, "users": 2000, "sites": 2},
    "security_level": "enterprise"
  },
  "use_historical": true,
  "max_historical_designs": 5
}

# Step 3: Generate design with historical context
POST /api/v1/design/generate
{
  "requirements": { /* same requirements */ },
  "use_rag": true,
  "use_historical": true,
  "historical_context": "/* context from step 2 */"
}
```

---

## 📊 Data Flow

```
External Database (PostgreSQL/MongoDB/Oracle)
         ↓
External DB Connector
         ↓
Historical Analysis Service
         ↓
    [Pattern Analysis]
    [Similarity Ranking]
    [Best Practices Extraction]
         ↓
Historical Context Builder
         ↓
Design Synthesizer Agent (with LLM)
         ↓
Generated Design (based on historical patterns)
```

---

## 🔐 Security Considerations

### **Read-Only Access**
- Use dedicated read-only database users
- Never grant write permissions to external databases
- Implement connection pooling with limits

### **Credential Management**
```bash
# Use secrets manager for production
EXTERNAL_POSTGRES_PASSWORD=$(vault kv get -field=password secret/external-db)

# Or AWS Secrets Manager
EXTERNAL_POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id external-db-password \
  --query SecretString \
  --output text)
```

### **Network Security**
- Use SSL/TLS for database connections
- Whitelist application IP addresses
- Use VPN or private network connections
- Implement connection timeouts

---

## 📈 Performance Optimization

### **Caching**
```python
# Historical queries are cached for 1 hour by default
HISTORICAL_DATA_CACHE_TTL=3600

# Adjust based on your needs:
# - High traffic: 7200 (2 hours)
# - Frequently updated data: 1800 (30 minutes)
```

### **Connection Pooling**
```python
# PostgreSQL pool settings
min_size=2    # Minimum connections
max_size=10   # Maximum connections
command_timeout=60  # Query timeout in seconds
```

### **Query Optimization**
- Ensure proper indexes on external database
- Limit result sets (default: 100 max)
- Use date range filters to reduce data volume

---

## 🎯 Use Cases

### **1. Enterprise Design Repository**
Connect to your organization's validated design database to leverage proven patterns.

### **2. Compliance-Driven Design**
Query historical designs that passed specific compliance validations (PCI-DSS, HIPAA, etc.).

### **3. Performance Benchmarking**
Analyze validation scores across different topologies to identify best performers.

### **4. Design Evolution Tracking**
Track how design patterns have evolved over time in your organization.

### **5. Knowledge Transfer**
Capture and reuse institutional knowledge from experienced network architects.

---

## 🐛 Troubleshooting

### **Connection Issues**

```bash
# Test PostgreSQL connection
psql -h external-db.example.com -U readonly_user -d network_designs_history

# Test MongoDB connection
mongosh "mongodb://external-mongo.example.com:27017" \
  --username readonly_user \
  --authenticationDatabase admin
```

### **No Results Returned**

Check filters:
- Ensure `network_type` matches database values
- Lower `min_validation_score` threshold
- Increase `days_back` parameter
- Verify data exists in external database

### **Slow Queries**

- Add database indexes (see schema section)
- Reduce `limit` parameter
- Enable query caching
- Use connection pooling

---

## 📚 Examples

### **Example 1: Query Top Designs**

```python
# Get top 10 validated spine-leaf designs
filters = {
    'network_type': 'enterprise_datacenter',
    'topology_type': 'spine_leaf',
    'status': 'validated',
    'min_validation_score': 0.90
}

designs = await db_connector.query_historical_designs_pg(filters, limit=10)
```

### **Example 2: Pattern Analysis**

```python
# Analyze last year's enterprise datacenter designs
patterns = await analysis_service.analyze_design_patterns(
    NetworkType.ENTERPRISE_DATACENTER,
    days_back=365
)

print(f"Most successful topology: {patterns['recommended_topology']}")
print(f"Average score: {patterns['avg_validation_score']}")
```

### **Example 3: Generate with History**

```python
# Build historical context
context = await analysis_service.build_historical_context(
    requirements,
    max_designs=5
)

# Use in design generation
design = await synthesizer.synthesize_design(
    requirements,
    analysis,
    use_rag=True,
    use_historical=True,
    historical_context=context
)
```

---

## 🔄 Data Migration

### **Importing Existing Designs**

If you need to populate the historical database:

```sql
-- Example: Import from CSV
COPY network_designs(
    design_id, name, description, network_type, 
    topology_type, status, validation_score, 
    component_count, created_at
)
FROM '/path/to/designs.csv'
DELIMITER ','
CSV HEADER;
```

### **Syncing from Internal Database**

```python
# Export validated designs to external database
async def sync_to_historical_db():
    # Get validated designs from internal DB
    designs = await design_repo.list_designs(
        status=DesignStatus.VALIDATED,
        limit=1000
    )
    
    # Insert into external DB
    for design in designs:
        await external_db.insert_design(design)
```

---

## 📞 Support

### **Configuration Issues**
- Check `.env` file for correct credentials
- Verify network connectivity to external database
- Review application logs for connection errors

### **Query Performance**
- Monitor query execution times
- Optimize database indexes
- Adjust cache TTL settings

### **Data Quality**
- Ensure validation scores are accurate
- Verify design metadata is complete
- Check for duplicate entries

---

**Feature Status**: ✅ **Production Ready**  
**API Endpoints**: 8 new endpoints  
**Supported Databases**: PostgreSQL, MongoDB, Oracle  
**Performance**: Cached queries, connection pooling  

---

*This feature enables your AI system to learn from your organization's design history and generate better, proven network architectures.*
