"""
Main FastAPI Application
Network Architecture Design System with RAG
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings, validate_configuration
from app.core.database import get_database_manager
from app.integrations.mcp_client import get_mcp_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("=" * 80)
    logger.info("Starting Network Architecture Design System")
    logger.info("=" * 80)
    
    try:
        # Validate configuration
        settings = validate_configuration()
        logger.info(f"✓ Configuration validated (Environment: {settings.environment})")
        
        # Connect to databases
        db_manager = get_database_manager()
        await db_manager.connect_all()
        logger.info("✓ Database connections established")
        
        # Initialize MCP clients
        mcp_manager = get_mcp_manager()
        health_status = await mcp_manager.health_check_all()
        logger.info(f"✓ MCP clients initialized: {health_status}")
        
        logger.info("=" * 80)
        logger.info("Application startup complete")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("Shutting down application")
    logger.info("=" * 80)
    
    try:
        # Close database connections
        db_manager = get_database_manager()
        await db_manager.close_all()
        logger.info("✓ Database connections closed")
        
        # Close MCP clients
        mcp_manager = get_mcp_manager()
        await mcp_manager.close_all()
        logger.info("✓ MCP clients closed")
        
        logger.info("=" * 80)
        logger.info("Application shutdown complete")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="Network Architecture Design System",
    description="AI-powered network architecture design and validation system with RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Network Architecture Design System API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.environment
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns system health status
    """
    try:
        # Check database connections
        db_manager = get_database_manager()
        
        # Check PostgreSQL
        postgres_healthy = False
        try:
            async with db_manager.get_postgres_session() as session:
                await session.execute("SELECT 1")
                postgres_healthy = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
        
        # Check Redis
        redis_healthy = False
        try:
            redis = await db_manager.get_redis_client()
            await redis.ping()
            redis_healthy = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
        
        # Check MCP servers
        mcp_manager = get_mcp_manager()
        mcp_health = await mcp_manager.health_check_all()
        
        # Overall health status
        all_healthy = postgres_healthy and redis_healthy
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": {
                "postgres": "healthy" if postgres_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy",
                "mcp_servers": mcp_health
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/config/status", tags=["Configuration"])
async def config_status():
    """
    Configuration status endpoint
    Shows which services are configured (without exposing credentials)
    """
    return {
        "llm_providers": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key)
        },
        "databases": {
            "postgres": bool(settings.postgres_url),
            "mongodb": bool(settings.mongodb_uri),
            "astra": bool(settings.astra_db_token),
            "redis": True
        },
        "mcp_servers": {
            "legacy_database": bool(settings.mcp_legacy_db_url),
            "web_application": bool(settings.mcp_web_app_url)
        },
        "monitoring": {
            "langsmith": bool(settings.langsmith_api_key),
            "tracing_enabled": settings.enable_tracing
        },
        "environment": settings.environment
    }


# ============================================================================
# API Routes
# ============================================================================

from app.api.routes import design, validation, retrieval, admin, historical, migration, metrics

app.include_router(design.router, prefix="/api/v1/design", tags=["Design"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(retrieval.router, prefix="/api/v1/retrieval", tags=["Retrieval"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(historical.router, prefix="/api/v1/historical", tags=["Historical Data"])
app.include_router(migration.router, prefix="/api/v1/migration", tags=["Data Migration"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics & Monitoring"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower()
    )
