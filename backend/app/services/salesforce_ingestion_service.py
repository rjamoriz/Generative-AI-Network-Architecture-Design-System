"""
Salesforce Ingestion Service
Fetches technical validation data, normalizes it, stores in Postgres and vector DB
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import logging

from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import get_database_manager
from app.integrations.salesforce_client import SalesforceClient
from app.models.network_design import DesignEmbedding
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SalesforceIngestionService:
    """Ingestion service for Salesforce technical validation data"""

    def __init__(
        self,
        salesforce_client: SalesforceClient,
        embedding_service: EmbeddingService,
        db_manager=None
    ):
        self.settings = get_settings()
        self.salesforce_client = salesforce_client
        self.embedding_service = embedding_service
        self.db_manager = db_manager or get_database_manager()

    async def ingest_validations(
        self,
        soql: Optional[str] = None,
        limit: Optional[int] = None,
        store_in_vector_db: bool = True,
        store_in_postgres: bool = True,
        embed: bool = True,
    ) -> Dict[str, Any]:
        soql_query = soql or self.settings.salesforce_validation_soql
        records = await self.salesforce_client.query(soql_query)

        if limit:
            records = records[:limit]

        stats = {
            "total_records": len(records),
            "stored_postgres": 0,
            "embedded": 0,
            "stored_vector": 0,
            "failed": 0,
            "errors": [],
            "soql_used": soql_query,
        }

        for record in records:
            try:
                normalized = self._normalize_record(record)

                if store_in_postgres:
                    stored = await self._store_in_postgres(normalized)
                    if stored:
                        stats["stored_postgres"] += 1

                if embed:
                    design_summary = self._build_summary(normalized, record)
                    embedding = await self.embedding_service.generate_embedding(design_summary)
                    stats["embedded"] += 1

                    if store_in_vector_db:
                        design_embedding = DesignEmbedding(
                            design_id=normalized["source_id"],
                            design_summary=design_summary,
                            embedding=embedding,
                            metadata={
                                "source": "salesforce",
                                "status": normalized.get("status"),
                                "validation_score": normalized.get("validation_score"),
                                "network_type": normalized.get("network_type"),
                                "topology_type": normalized.get("topology_type"),
                                "payload": normalized.get("payload"),
                            },
                        )
                        await self.embedding_service.store_embedding_in_vector_db(design_embedding)
                        stats["stored_vector"] += 1

            except Exception as exc:
                stats["failed"] += 1
                error_message = f"Failed to ingest record: {exc}"
                logger.error(error_message)
                stats["errors"].append(error_message)

        return stats

    def _normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        payload = {k: v for k, v in record.items() if k != "attributes"}
        source_id = self._first_value(payload, [
            "Design_Id__c",
            "DesignId",
            "design_id",
            "Id",
            "id",
        ])

        if not source_id:
            source_id = f"sf_{hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]}"

        name = self._first_value(payload, ["Name", "name", "Design_Name__c"], source_id)
        status = self._first_value(payload, ["Status__c", "status", "Validation_Status__c"], "validated")
        validation_score = self._first_value(payload, ["Validation_Score__c", "Score__c", "validation_score"])
        network_type = self._first_value(payload, ["Network_Type__c", "network_type"])
        topology_type = self._first_value(payload, ["Topology_Type__c", "topology_type"])
        created_at = self._first_value(payload, ["CreatedDate", "created_at"])
        validated_at = self._first_value(payload, ["ValidatedDate__c", "validated_at"])

        return {
            "source": "salesforce",
            "source_id": str(source_id),
            "name": str(name) if name is not None else str(source_id),
            "status": status,
            "validation_score": validation_score,
            "network_type": network_type,
            "topology_type": topology_type,
            "created_at": created_at,
            "validated_at": validated_at,
            "payload": payload,
        }

    def _build_summary(self, normalized: Dict[str, Any], record: Dict[str, Any]) -> str:
        pieces = [
            f"Name: {normalized.get('name')}",
            f"Status: {normalized.get('status')}",
        ]

        if normalized.get("validation_score") is not None:
            pieces.append(f"Score: {normalized.get('validation_score')}")
        if normalized.get("network_type"):
            pieces.append(f"Network Type: {normalized.get('network_type')}")
        if normalized.get("topology_type"):
            pieces.append(f"Topology: {normalized.get('topology_type')}")

        detail_items = []
        for key, value in record.items():
            if key == "attributes" or value is None:
                continue
            detail_items.append(f"{key}={value}")
            if len(detail_items) >= 20:
                break

        details = "; ".join(detail_items)
        return f"Salesforce Technical Validation | {', '.join(pieces)} | {details}"

    async def _store_in_postgres(self, normalized: Dict[str, Any]) -> bool:
        try:
            async with self.db_manager.get_postgres_session() as session:
                query = text(
                    """
                    INSERT INTO technical_validations (
                        source,
                        source_id,
                        name,
                        status,
                        validation_score,
                        network_type,
                        topology_type,
                        created_at,
                        validated_at,
                        payload,
                        ingested_at
                    ) VALUES (
                        :source,
                        :source_id,
                        :name,
                        :status,
                        :validation_score,
                        :network_type,
                        :topology_type,
                        :created_at,
                        :validated_at,
                        :payload,
                        :ingested_at
                    )
                    ON CONFLICT (source, source_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        status = EXCLUDED.status,
                        validation_score = EXCLUDED.validation_score,
                        network_type = EXCLUDED.network_type,
                        topology_type = EXCLUDED.topology_type,
                        created_at = EXCLUDED.created_at,
                        validated_at = EXCLUDED.validated_at,
                        payload = EXCLUDED.payload,
                        ingested_at = EXCLUDED.ingested_at
                    """
                )

                await session.execute(
                    query,
                    {
                        "source": normalized["source"],
                        "source_id": normalized["source_id"],
                        "name": normalized["name"],
                        "status": normalized["status"],
                        "validation_score": normalized.get("validation_score"),
                        "network_type": normalized.get("network_type"),
                        "topology_type": normalized.get("topology_type"),
                        "created_at": normalized.get("created_at"),
                        "validated_at": normalized.get("validated_at"),
                        "payload": json.dumps(normalized.get("payload", {})),
                        "ingested_at": datetime.utcnow(),
                    },
                )

            return True

        except Exception as exc:
            logger.warning(f"Failed to store Salesforce record in Postgres: {exc}")
            return False

    @staticmethod
    def _first_value(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
        for key in keys:
            value = data.get(key)
            if value is not None:
                return value
        return default
