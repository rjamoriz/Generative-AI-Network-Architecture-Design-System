"""
Salesforce API Routes
Endpoints for ingesting technical validation data from Salesforce
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.core.config import get_settings
from app.integrations.salesforce_client import SalesforceClient, get_salesforce_client
from app.models.salesforce_ingestion import SalesforceIngestionRequest, SalesforceIngestionResult
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.salesforce_ingestion_service import SalesforceIngestionService
from app.core.database import get_postgres_session
from app.db.postgres_repository import AuditLogRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest/technical-validations", response_model=SalesforceIngestionResult)
async def ingest_technical_validations(
    request: SalesforceIngestionRequest,
    salesforce_client: SalesforceClient = Depends(get_salesforce_client),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    session: AsyncSession = Depends(get_postgres_session),
) -> SalesforceIngestionResult:
    """
    Ingest technical validation records from Salesforce
    """
    settings = get_settings()
    if not settings.salesforce_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Salesforce integration is disabled"
        )

    try:
        service = SalesforceIngestionService(salesforce_client, embedding_service)
        result = await service.ingest_validations(
            soql=request.soql,
            limit=request.limit,
            store_in_vector_db=request.store_in_vector_db,
            store_in_postgres=request.store_in_postgres,
            embed=request.embed,
        )
        audit_repo = AuditLogRepository()
        await audit_repo.log(
            session,
            action="salesforce_ingest",
            status="success",
            resource_type="technical_validations",
            message="Salesforce ingestion completed",
            metadata=result,
        )
        return SalesforceIngestionResult(**result)

    except Exception as exc:
        logger.error(f"Salesforce ingestion failed: {exc}")
        try:
            audit_repo = AuditLogRepository()
            await audit_repo.log(
                session,
                action="salesforce_ingest",
                status="failed",
                resource_type="technical_validations",
                message=str(exc),
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Salesforce ingestion failed: {exc}")
