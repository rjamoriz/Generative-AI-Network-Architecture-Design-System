"""
SQLAlchemy ORM models for Postgres authoritative storage
"""
from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class RequirementsRecord(Base):
    __tablename__ = "requirements"

    requirements_id = Column(String(100), primary_key=True, default=lambda: f"req_{uuid.uuid4().hex[:12]}")
    project_name = Column(String(200), nullable=True)
    network_type = Column(String(50), nullable=True)
    security_level = Column(String(50), nullable=True)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class NetworkDesignRecord(Base):
    __tablename__ = "network_designs"

    design_id = Column(String(100), primary_key=True, default=lambda: f"design_{uuid.uuid4().hex[:12]}")
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    network_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)
    version = Column(String(20), nullable=True)
    requirements_id = Column(String(100), ForeignKey("requirements.requirements_id"), nullable=True)
    topology_type = Column(String(50), nullable=True)
    design_data = Column(JSONB, nullable=True)
    validation_score = Column(Float, nullable=True)
    validation_id = Column(String(100), ForeignKey("validation_results.validation_id"), nullable=True)
    created_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_network_designs_network_type", "network_type"),
        Index("ix_network_designs_status", "status"),
    )


class ValidationResultRecord(Base):
    __tablename__ = "validation_results"

    validation_id = Column(String(100), primary_key=True, default=lambda: f"val_{uuid.uuid4().hex[:12]}")
    design_id = Column(String(100), ForeignKey("network_designs.design_id"), nullable=False)
    mode = Column(String(20), nullable=True)
    overall_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    deterministic_result = Column(JSONB, nullable=True)
    llm_result = Column(JSONB, nullable=True)
    issues = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_validation_results_design_id", "design_id"),
    )


class TechnicalValidationRecord(Base):
    __tablename__ = "technical_validations"

    source = Column(String(50), primary_key=True)
    source_id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=True)
    status = Column(String(50), nullable=True)
    validation_score = Column(Float, nullable=True)
    network_type = Column(String(50), nullable=True)
    topology_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    payload = Column(JSONB, nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_technical_validations_status", "status"),
        Index("ix_technical_validations_network_type", "network_type"),
    )


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id = Column(String(100), primary_key=True, default=lambda: f"log_{uuid.uuid4().hex[:12]}")
    actor = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    trace_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
    )
