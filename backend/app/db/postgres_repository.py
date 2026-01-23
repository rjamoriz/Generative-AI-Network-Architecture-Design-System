"""
Postgres repositories for authoritative storage
"""
from __future__ import annotations

from typing import Optional, Any, Dict, List
from datetime import datetime
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    RequirementsRecord,
    NetworkDesignRecord,
    ValidationResultRecord,
    AuditLogRecord,
)
from app.models.requirements import NetworkRequirements
from app.models.network_design import NetworkDesign
from app.models.validation_result import ValidationResult


class RequirementsRepository:
    """Repository for requirements records"""

    async def create(self, session: AsyncSession, requirements: NetworkRequirements) -> str:
        requirements_id = requirements.requirements_id or f"req_{uuid.uuid4().hex[:12]}"

        record = RequirementsRecord(
            requirements_id=requirements_id,
            project_name=requirements.project_name,
            network_type=requirements.network_type.value,
            security_level=requirements.security_level.value,
            payload=requirements.model_dump(mode="json"),
            created_at=requirements.submitted_at or datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(record)
        await session.flush()
        return requirements_id

    async def upsert(self, session: AsyncSession, requirements: NetworkRequirements) -> str:
        requirements_id = requirements.requirements_id or f"req_{uuid.uuid4().hex[:12]}"
        existing = await self.get(session, requirements_id)

        if existing:
            await session.execute(
                update(RequirementsRecord)
                .where(RequirementsRecord.requirements_id == requirements_id)
                .values(
                    project_name=requirements.project_name,
                    network_type=requirements.network_type.value,
                    security_level=requirements.security_level.value,
                    payload=requirements.model_dump(mode="json"),
                    updated_at=datetime.utcnow(),
                )
            )
            return requirements_id

        requirements.requirements_id = requirements_id
        await self.create(session, requirements)
        return requirements_id

    async def get(self, session: AsyncSession, requirements_id: str) -> Optional[RequirementsRecord]:
        result = await session.execute(
            select(RequirementsRecord).where(RequirementsRecord.requirements_id == requirements_id)
        )
        return result.scalars().first()


class DesignRepository:
    """Repository for network designs"""

    async def create(self, session: AsyncSession, design: NetworkDesign) -> str:
        design_id = design.design_id or f"design_{uuid.uuid4().hex[:12]}"
        topology_type = design.topology.topology_type.value if design.topology else None

        record = NetworkDesignRecord(
            design_id=design_id,
            name=design.name,
            description=design.description,
            network_type=design.network_type.value,
            status=design.status.value,
            version=design.version,
            requirements_id=design.requirements_id,
            topology_type=topology_type,
            design_data=design.model_dump(mode="json"),
            validation_score=design.validation_score,
            validation_id=design.validation_id,
            created_by=design.created_by,
            approved_by=design.approved_by,
            created_at=design.created_at or datetime.utcnow(),
            updated_at=design.updated_at or datetime.utcnow(),
            approved_at=design.approved_at,
        )
        session.add(record)
        await session.flush()
        return design_id

    async def get(self, session: AsyncSession, design_id: str) -> Optional[NetworkDesignRecord]:
        result = await session.execute(
            select(NetworkDesignRecord).where(NetworkDesignRecord.design_id == design_id)
        )
        return result.scalars().first()

    async def upsert(self, session: AsyncSession, design: NetworkDesign) -> str:
        design_id = design.design_id or f"design_{uuid.uuid4().hex[:12]}"
        existing = await self.get(session, design_id)

        if existing:
            await session.execute(
                update(NetworkDesignRecord)
                .where(NetworkDesignRecord.design_id == design_id)
                .values(
                    name=design.name,
                    description=design.description,
                    network_type=design.network_type.value,
                    status=design.status.value,
                    version=design.version,
                    requirements_id=design.requirements_id,
                    topology_type=design.topology.topology_type.value if design.topology else None,
                    design_data=design.model_dump(mode="json"),
                    validation_score=design.validation_score,
                    validation_id=design.validation_id,
                    created_by=design.created_by,
                    approved_by=design.approved_by,
                    approved_at=design.approved_at,
                    updated_at=design.updated_at or datetime.utcnow(),
                )
            )
            return design_id

        design.design_id = design_id
        await self.create(session, design)
        return design_id

    async def list(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[NetworkDesignRecord]:
        query = select(NetworkDesignRecord)
        if status:
            query = query.where(NetworkDesignRecord.status == status)

        result = await session.execute(
            query.order_by(NetworkDesignRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_validation(
        self,
        session: AsyncSession,
        design_id: str,
        validation_id: Optional[str],
        validation_score: Optional[float],
        status: Optional[str] = None,
    ) -> None:
        values: Dict[str, Any] = {
            "validation_id": validation_id,
            "validation_score": validation_score,
            "updated_at": datetime.utcnow(),
        }
        if status is not None:
            values["status"] = status

        await session.execute(
            update(NetworkDesignRecord)
            .where(NetworkDesignRecord.design_id == design_id)
            .values(**values)
        )

    @staticmethod
    def to_model(record: NetworkDesignRecord) -> NetworkDesign:
        payload = record.design_data or {}
        payload.setdefault("design_id", record.design_id)
        return NetworkDesign(**payload)


class ValidationRepository:
    """Repository for validation results"""

    async def create(
        self,
        session: AsyncSession,
        result: ValidationResult,
        mode: Optional[str] = None,
    ) -> str:
        validation_id = result.validation_id or f"val_{uuid.uuid4().hex[:12]}"

        record = ValidationResultRecord(
            validation_id=validation_id,
            design_id=result.design_id,
            mode=mode,
            overall_score=result.overall_score,
            passed=result.passed,
            deterministic_result=result.deterministic_validation.model_dump(mode="json"),
            llm_result=result.llm_validation.model_dump(mode="json"),
            issues=[issue.model_dump(mode="json") for issue in result.all_issues],
            created_at=result.validated_at,
        )
        session.add(record)
        await session.flush()
        return validation_id


class AuditLogRepository:
    """Repository for audit logs"""

    async def log(
        self,
        session: AsyncSession,
        action: str,
        status: str,
        actor: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        record = AuditLogRecord(
            actor=actor,
            action=action,
            status=status,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message,
            metadata=metadata,
            trace_id=trace_id,
            request_id=request_id,
            created_at=datetime.utcnow(),
        )
        session.add(record)
        await session.flush()

    async def list(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[AuditLogRecord]:
        query = select(AuditLogRecord)
        if status:
            query = query.where(AuditLogRecord.status == status)
        if action:
            query = query.where(AuditLogRecord.action == action)

        result = await session.execute(
            query.order_by(AuditLogRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
