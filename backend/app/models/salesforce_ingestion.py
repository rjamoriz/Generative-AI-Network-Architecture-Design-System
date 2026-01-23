"""
Pydantic models for Salesforce ingestion requests/responses
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class SalesforceIngestionRequest(BaseModel):
    """Request payload for ingesting Salesforce technical validations"""
    soql: Optional[str] = Field(default=None, description="SOQL query override")
    limit: Optional[int] = Field(default=None, ge=1, description="Optional record limit")
    store_in_vector_db: bool = Field(default=True, description="Store embeddings in vector DB")
    store_in_postgres: bool = Field(default=True, description="Store normalized records in Postgres")
    embed: bool = Field(default=True, description="Generate embeddings")


class SalesforceIngestionResult(BaseModel):
    """Summary of Salesforce ingestion results"""
    total_records: int
    stored_postgres: int
    embedded: int
    stored_vector: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    soql_used: str
