"""
Pydantic models for PDF ingestion
"""
from pydantic import BaseModel, Field


class PdfIngestionResult(BaseModel):
    """Result summary for PDF ingestion"""
    document_id: str
    file_name: str
    page_count: int
    chunk_count: int
    embedded_chunks: int
    stored_vector: int
    status: str = Field(default="completed")
