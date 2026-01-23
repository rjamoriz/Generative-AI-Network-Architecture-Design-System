"""Initial Postgres schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-01-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "requirements",
        sa.Column("requirements_id", sa.String(length=100), primary_key=True),
        sa.Column("project_name", sa.String(length=200), nullable=True),
        sa.Column("network_type", sa.String(length=50), nullable=True),
        sa.Column("security_level", sa.String(length=50), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "network_designs",
        sa.Column("design_id", sa.String(length=100), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("network_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column("requirements_id", sa.String(length=100), sa.ForeignKey("requirements.requirements_id"), nullable=True),
        sa.Column("topology_type", sa.String(length=50), nullable=True),
        sa.Column("design_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("validation_score", sa.Float(), nullable=True),
        sa.Column("validation_id", sa.String(length=100), sa.ForeignKey("validation_results.validation_id"), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_network_designs_network_type", "network_designs", ["network_type"])
    op.create_index("ix_network_designs_status", "network_designs", ["status"])

    op.create_table(
        "validation_results",
        sa.Column("validation_id", sa.String(length=100), primary_key=True),
        sa.Column("design_id", sa.String(length=100), sa.ForeignKey("network_designs.design_id"), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("deterministic_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("llm_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("issues", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_validation_results_design_id", "validation_results", ["design_id"])

    op.create_table(
        "technical_validations",
        sa.Column("source", sa.String(length=50), primary_key=True),
        sa.Column("source_id", sa.String(length=100), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("validation_score", sa.Float(), nullable=True),
        sa.Column("network_type", sa.String(length=50), nullable=True),
        sa.Column("topology_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_technical_validations_status", "technical_validations", ["status"])
    op.create_index("ix_technical_validations_network_type", "technical_validations", ["network_type"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=100), primary_key=True),
        sa.Column("actor", sa.String(length=100), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("trace_id", sa.String(length=100), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_technical_validations_network_type", table_name="technical_validations")
    op.drop_index("ix_technical_validations_status", table_name="technical_validations")
    op.drop_table("technical_validations")

    op.drop_index("ix_validation_results_design_id", table_name="validation_results")
    op.drop_table("validation_results")

    op.drop_index("ix_network_designs_status", table_name="network_designs")
    op.drop_index("ix_network_designs_network_type", table_name="network_designs")
    op.drop_table("network_designs")

    op.drop_table("requirements")
