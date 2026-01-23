"""
Historical Design API Routes
Endpoints for querying and analyzing historical network design data
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
import logging

from app.models.requirements import NetworkRequirements
from app.models.network_design import NetworkType, SecurityLevel
from app.models.pdf_ingestion import PdfIngestionResult
from app.integrations.external_db_connector import ExternalDatabaseConnector, get_external_db_connector
from app.services.historical_analysis_service import HistoricalAnalysisService, get_historical_analysis_service
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.pdf_ingestion_service import PdfIngestionService
from app.core.database import get_postgres_session
from app.db.postgres_repository import AuditLogRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/connect/postgresql")
async def connect_postgresql(
    connection_string: str,
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Connect to external PostgreSQL database
    
    Args:
        connection_string: PostgreSQL connection string
    
    Returns:
        Connection status
    """
    try:
        success = await db_connector.connect_postgresql(connection_string)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to PostgreSQL database"
            )
        
        return {
            "status": "connected",
            "database_type": "postgresql",
            "message": "Successfully connected to external PostgreSQL database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection failed: {str(e)}"
        )


@router.post("/connect/mongodb")
async def connect_mongodb(
    connection_string: str,
    database: str,
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Connect to external MongoDB database
    
    Args:
        connection_string: MongoDB connection string
        database: Database name
    
    Returns:
        Connection status
    """
    try:
        success = await db_connector.connect_mongodb(connection_string, database)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to MongoDB database"
            )
        
        return {
            "status": "connected",
            "database_type": "mongodb",
            "database": database,
            "message": "Successfully connected to external MongoDB database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection failed: {str(e)}"
        )


@router.post("/upload", response_model=PdfIngestionResult)
async def upload_historical_pdf(
    file: UploadFile = File(...),
    generate_embeddings: bool = Form(True),
    store_in_vector_db: bool = Form(True),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    session: AsyncSession = Depends(get_postgres_session),
) -> PdfIngestionResult:
    """
    Upload a historical design PDF and store embeddings in vector DB
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    try:
        content = await file.read()
        ingestion_service = PdfIngestionService(embedding_service)
        result = await ingestion_service.ingest_pdf(
            file_name=file.filename,
            content=content,
            generate_embeddings=generate_embeddings,
            store_in_vector_db=store_in_vector_db,
        )
        audit_repo = AuditLogRepository()
        await audit_repo.log(
            session,
            action="pdf_ingest",
            status="success",
            resource_type="historical_pdf",
            resource_id=result.get("document_id"),
            message="PDF ingestion completed",
            metadata=result,
        )
        return PdfIngestionResult(**result)
    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")
        try:
            audit_repo = AuditLogRepository()
            await audit_repo.log(
                session,
                action="pdf_ingest",
                status="failed",
                resource_type="historical_pdf",
                message=str(e),
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF ingestion failed: {str(e)}",
        )


@router.post("/query/similar-designs")
async def query_similar_designs(
    requirements: NetworkRequirements,
    min_validation_score: float = Query(default=0.85, ge=0.0, le=1.0),
    limit: int = Query(default=10, ge=1, le=50),
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> List[Dict[str, Any]]:
    """
    Query similar validated designs from historical data
    
    Args:
        requirements: Network requirements to match
        min_validation_score: Minimum validation score filter
        limit: Maximum number of results
    
    Returns:
        List of similar designs
    """
    try:
        analysis_service = get_historical_analysis_service(db_connector)
        
        similar_designs = await analysis_service.find_similar_validated_designs(
            requirements,
            min_validation_score,
            limit
        )
        
        return similar_designs
        
    except Exception as e:
        logger.error(f"Failed to query similar designs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.get("/patterns/{network_type}")
async def analyze_design_patterns(
    network_type: NetworkType,
    days_back: int = Query(default=365, ge=1, le=3650),
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Analyze design patterns from historical data
    
    Args:
        network_type: Network type to analyze
        days_back: Number of days to look back
    
    Returns:
        Pattern analysis results
    """
    try:
        analysis_service = get_historical_analysis_service(db_connector)
        
        patterns = await analysis_service.analyze_design_patterns(
            network_type,
            days_back
        )
        
        return patterns
        
    except Exception as e:
        logger.error(f"Failed to analyze patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/best-practices/{network_type}/{security_level}")
async def get_best_practices(
    network_type: NetworkType,
    security_level: SecurityLevel,
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Get best practices from highly validated designs
    
    Args:
        network_type: Network type
        security_level: Security level
    
    Returns:
        Best practices and recommendations
    """
    try:
        analysis_service = get_historical_analysis_service(db_connector)
        
        best_practices = await analysis_service.get_best_practices(
            network_type,
            security_level
        )
        
        return best_practices
        
    except Exception as e:
        logger.error(f"Failed to get best practices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve best practices: {str(e)}"
        )


@router.get("/insights/{network_type}")
async def get_validation_insights(
    network_type: NetworkType,
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Get validation insights for a network type
    
    Args:
        network_type: Network type
    
    Returns:
        Validation insights
    """
    try:
        analysis_service = get_historical_analysis_service(db_connector)
        
        insights = await analysis_service.get_validation_insights(network_type)
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve insights: {str(e)}"
        )


@router.post("/context/build")
async def build_historical_context(
    requirements: NetworkRequirements,
    max_designs: int = Query(default=5, ge=1, le=10),
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Build historical context for LLM-based design generation
    
    Args:
        requirements: Network requirements
        max_designs: Maximum designs to include in context
    
    Returns:
        Historical context string and metadata
    """
    try:
        analysis_service = get_historical_analysis_service(db_connector)
        
        context = await analysis_service.build_historical_context(
            requirements,
            max_designs
        )
        
        return {
            "context": context,
            "max_designs": max_designs,
            "network_type": requirements.network_type.value,
            "message": "Historical context built successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to build context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build context: {str(e)}"
        )


@router.get("/statistics")
async def get_historical_statistics(
    source: str = Query(default="postgresql", regex="^(postgresql|mongodb|oracle)$"),
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Get statistics about historical design data
    
    Args:
        source: Database source (postgresql, mongodb, oracle)
    
    Returns:
        Statistics dictionary
    """
    try:
        stats = await db_connector.get_design_statistics(source)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No statistics available for source: {source}"
            )
        
        return {
            "source": source,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.post("/generate-with-history")
async def generate_design_with_historical_data(
    requirements: NetworkRequirements,
    use_historical: bool = True,
    max_historical_designs: int = Query(default=5, ge=1, le=10),
    db_connector: ExternalDatabaseConnector = Depends(get_external_db_connector)
) -> Dict[str, Any]:
    """
    Generate design using historical data insights
    
    This endpoint builds historical context and returns it for use in design generation.
    The actual design generation should be done via the /api/v1/design/generate endpoint
    with the historical context.
    
    Args:
        requirements: Network requirements
        use_historical: Whether to use historical data
        max_historical_designs: Maximum historical designs to analyze
    
    Returns:
        Historical insights and context for design generation
    """
    try:
        if not use_historical:
            return {
                "message": "Historical data not requested",
                "use_historical": False
            }
        
        analysis_service = get_historical_analysis_service(db_connector)
        
        # Build historical context
        context = await analysis_service.build_historical_context(
            requirements,
            max_historical_designs
        )
        
        # Get patterns
        patterns = await analysis_service.analyze_design_patterns(
            requirements.network_type,
            days_back=180
        )
        
        # Get best practices
        best_practices = await analysis_service.get_best_practices(
            requirements.network_type,
            requirements.security_level
        )
        
        return {
            "historical_context": context,
            "patterns": patterns,
            "best_practices": best_practices,
            "use_historical": True,
            "message": "Historical insights generated successfully. Use this data with /api/v1/design/generate endpoint."
        }
        
    except Exception as e:
        logger.error(f"Failed to generate with historical data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )
