# CLAUDE.md - AI Context for Generative AI Network Architecture Design System

## Project Overview

You are working on a **critical enterprise Generative AI system** designed to design and validate both legacy and SDN (Software-Defined Networking) network architectures. This system integrates with enterprise web applications and databases containing historically validated network designs, using advanced LLM reasoning, RAG (Retrieval-Augmented Generation), and strict validation workflows.

## Core Problem

Organizations accumulate vast volumes of network architecture knowledge across legacy and SDN environments. This knowledge is fragmented across web applications and databases, difficult to reuse consistently. The goal is to build a Generative AI system capable of consuming this historical knowledge and extrapolating technically valid designs for new network requirements, maintaining technical rigor and explainability.

## System Architecture - 5 Layers

### 1. Presentation Layer (React.js)
- Enterprise-grade user interface
- Interactive network design visualization
- Requirements and parameters management

### 2. API & Orchestration Layer (FastAPI)
- AI workflow orchestration
- Authentication and authorization management
- MCP server interface
- Validation pipeline control
- Auditability and logging

### 3. AI Reasoning Layer (LLMs + Agent Framework)
- **Requirement Analysis Agent**: Extracts and structures network requirements
- **Retrieval Agent (RAG)**: Semantic search of validated designs
- **Design Synthesis Agent**: Generates network architectures
- **Validation & Compliance Agent**: Validates against rules and best practices

### 4. Knowledge & Retrieval Layer (Vector + Relational DBs)
- Semantic search of validated designs
- Storage of historical architectures
- Management of constraints and rules

### 5. Integration Layer (MCP Servers / Connectors)
- Integration with enterprise web applications
- Legacy database connectors
- Historical data bridges

## Technical Stack Summary

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Async Runtime**: Uvicorn
- **Validation**: Pydantic v2
- **Task Queue**: Celery + Redis
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

### Frontend
- **Framework**: React.js with Next.js
- **UI Components**: Material UI / Ant Design
- **State Management**: React Query / TanStack Query
- **Visualization**: D3.js / Cytoscape.js
- **Forms**: React Hook Form

### AI/ML Layer
- **LLM Providers**: OpenAI (GPT-4) / Anthropic (Claude)
- **Agent Framework**: LangChain / LlamaIndex
- **Embeddings**: OpenAI Embeddings / sentence-transformers
- **Monitoring**: LangSmith / Weights & Biases

### Databases
- **Relational**: PostgreSQL / Oracle (authoritative validated designs)
- **Vector DB**: MongoDB Atlas Vector Search OR DataStax Astra DB
- **Cache**: Redis

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions / GitLab CI
- **IaC**: Terraform / Pulumi
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack / Loki
- **Tracing**: Jaeger / OpenTelemetry

## Key AI Workflow (RAG + Validation)

1. **User** submits network requirements via React UI
2. **Requirement Agent** analyzes and structures requirements using LLM
3. **RAG Agent** performs semantic search in vector database for similar validated designs
4. **Design Synthesis Agent** generates candidate design using RAG context
5. **Validation Agent** validates design through:
   - **Deterministic validation**: Capacity, protocol, compliance, topology rules
   - **Probabilistic validation**: LLM reasoning for edge cases
6. **Scoring & Explanation**: Combines validation results with detailed explanations
7. **Iterative Refinement**: If validation fails, regenerate with constraints
8. **User Approval**: Human-in-the-loop approval required
9. **Audit Logging**: All operations logged immutably

## Critical Design Principles

### Security & Governance
- **NO AUTONOMOUS DEPLOYMENT**: System NEVER deploys configurations automatically - always requires human approval
- **Complete Auditability**: Immutable logs of all requests, prompts, responses, and approvals
- **RBAC**: Role-based access control (admin, network_architect, reviewer, viewer)
- **Zero Trust Architecture**: Authentication on all endpoints, TLS 1.3, encryption at rest
- **Explainability**: Every design includes step-by-step reasoning, confidence scores, sources consulted

### Validation Requirements
- **Dual Validation Framework**:
  1. **Deterministic**: Rules engine for capacity, protocols, compliance
  2. **Probabilistic**: LLM validators for contextual reasoning and edge cases
- **Validation Threshold**: Minimum 85% score required for approval
- **Structured Outputs**: All LLM outputs validated through Pydantic models

### RAG Strategy
- **Validated Sources Only**: RAG only retrieves from historically validated designs
- **Relevance Filtering**: Top-K similar designs with relevance threshold
- **Token Budget Management**: Optimize context window usage
- **Constraint Matching**: Filter by network type, scale, topology

## Project Structure

```
Generative-AI-Network-Architecture-Design-System/
├── frontend/                    # React.js + Next.js application
│   ├── src/
│   │   ├── components/         # NetworkVisualizer, RequirementForm, ValidationDashboard
│   │   ├── pages/              # Next.js pages
│   │   ├── hooks/              # React Query hooks
│   │   └── services/           # API services
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/routes/         # API endpoints (design, validation, retrieval)
│   │   ├── agents/             # AI Agents (requirement_analyzer, retrieval_agent, design_synthesizer, validation_agent)
│   │   ├── services/           # Business services (llm_service, rag_service, validation_service)
│   │   ├── models/             # Pydantic models
│   │   ├── core/               # Configuration, security, logging
│   │   └── integrations/       # MCP servers and connectors
│
├── ai_models/                   # AI/ML components
│   ├── embeddings/             # Embedding models
│   ├── prompts/                # Prompt templates
│   └── chains/                 # LangChain chains
│
├── database/                    # Database schemas and migrations
│   ├── migrations/             # Alembic migrations
│   ├── schemas/                # PostgreSQL and vector DB schemas
│   └── seeds/                  # Seed data
│
├── validation/                  # Validation framework
│   ├── rules/                  # Deterministic rules (capacity, protocol, compliance)
│   ├── llm_validators/         # LLM-based validators
│   └── scoring/                # Scoring system
│
├── mcp_servers/                 # MCP server implementations
│   ├── legacy_app_server/
│   └── sdn_data_server/
│
├── infrastructure/              # Kubernetes & DevOps
│   ├── k8s/                    # Kubernetes manifests
│   ├── docker/                 # Dockerfiles
│   └── terraform/              # Infrastructure as Code
│
├── tests/                       # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── data/                        # Historical data
    ├── validated_designs/
    └── training_examples/
```

## Critical Constraints & Requirements

### Must Have
1. All designs MUST pass dual validation (deterministic + probabilistic)
2. All operations MUST be logged for audit trail
3. Human approval REQUIRED before any deployment
4. RAG MUST only use validated historical designs
5. All LLM outputs MUST be structured (Pydantic models)
6. Minimum 85% validation score for approval
7. Complete explainability for all generated designs

### Must NOT
1. NEVER deploy configurations autonomously
2. NEVER use unvalidated designs for RAG context
3. NEVER skip validation steps
4. NEVER expose sensitive data in logs (PII masking required)
5. NEVER compromise security for performance

## Environment Variables

```env
# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=network_design_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Vector Database (choose one)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=network_vectors
# OR
ASTRA_DB_ID=your-astra-db-id
ASTRA_DB_TOKEN=your-token

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
JWT_SECRET_KEY=your-super-secret-key
API_KEY_SALT=random-salt-value

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Success Metrics (KPIs)

| Metric | Target |
|--------|--------|
| Design Generation Time | < 30 seconds |
| Validation Accuracy | > 95% |
| RAG Retrieval Precision | > 85% |
| User Approval Rate | > 80% |
| System Uptime | 99.5% |
| API Response Time (p95) | < 2 seconds |
| LLM Call Success Rate | > 98% |

## Development Priorities

### Phase 1: Data Modeling & MCP Integration (Current)
- Database schema design
- MCP server implementation
- Historical data ingestion pipeline

### Phase 2: RAG & LLM Prototyping
- Embedding and vectorization
- Semantic search implementation
- Agent framework with LangChain
- Prompt engineering for each agent

### Phase 3: Validation Engine
- Deterministic rules engine
- LLM validators for edge cases
- Scoring and explanation system

### Phase 4: Frontend & UX
- React/Next.js UI development
- Network topology visualization
- Validation dashboard

### Phase 5: Security & Production
- OAuth2/RBAC implementation
- Security testing
- Kubernetes deployment
- CI/CD pipelines

## Commands & Quick Reference

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
pytest tests/unit/ -v --cov=app
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Current Status

- [x] Project initialization
- [x] Architecture documentation
- [x] Technical specifications
- [ ] Phase 1: Data Modeling & MCP Integration (IN PROGRESS)
- [ ] Phase 2: RAG & LLM Prototyping
- [ ] Phase 3: Validation Engine
- [ ] Phase 4: Frontend & UX
- [ ] Phase 5: Security & Production

## Context for AI Assistant

When working on this project:
1. Always prioritize security and validation rigor
2. Follow the 5-layer architecture strictly
3. Ensure all LLM outputs are structured with Pydantic
4. Implement comprehensive error handling
5. Add detailed logging for auditability
6. Write tests for all critical functionality
7. Document all API endpoints with OpenAPI
8. Consider scalability and performance from the start
9. Never compromise on explainability
10. Always maintain human-in-the-loop control

This is an enterprise-critical system handling network infrastructure designs - accuracy and security are paramount.
