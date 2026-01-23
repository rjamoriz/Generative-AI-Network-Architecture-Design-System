"""
Audit Log API Routes
Endpoints for viewing audit logs
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_postgres_session
from app.db.postgres_repository import AuditLogRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/logs")
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_postgres_session),
) -> List[Dict[str, Any]]:
    """
    List audit logs with optional filters
    
    Args:
        limit: Maximum number of logs to return (1-100)
        offset: Number of logs to skip
        status: Filter by status (success, failed)
        action: Filter by action type
    
    Returns:
        List of audit log entries
    """
    repo = AuditLogRepository()
    records = await repo.list(session, limit=limit, offset=offset, status=status, action=action)
    
    return [
        {
            "id": record.id,
            "actor": record.actor,
            "action": record.action,
            "status": record.status,
            "resource_type": record.resource_type,
            "resource_id": record.resource_id,
            "message": record.message,
            "metadata": record.metadata,
            "trace_id": record.trace_id,
            "request_id": record.request_id,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]
