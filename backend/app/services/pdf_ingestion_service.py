"""
PDF Ingestion Service
Extracts text from PDFs, chunks content, generates embeddings, stores in vector DB
"""
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime
import io
import logging
import uuid

from pypdf import PdfReader

from app.models.network_design import DesignEmbedding
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class PdfIngestionService:
    """Service to ingest PDF documents into vector DB"""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def ingest_pdf(
        self,
        file_name: str,
        content: bytes,
        generate_embeddings: bool = True,
        store_in_vector_db: bool = True,
    ) -> Dict[str, Any]:
        reader = PdfReader(io.BytesIO(content))
        page_texts = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n".join(page_texts).strip()

        if not full_text:
            raise ValueError("No extractable text found in PDF")

        document_id = f"pdf_{uuid.uuid4().hex[:12]}"
        chunks = self._chunk_text(full_text)

        embedded_chunks = 0
        stored_vector = 0

        if generate_embeddings and chunks:
            vector_store = get_vector_store()
            await vector_store.ensure_ready()

            for index, chunk in enumerate(chunks):
                embedding = await self.embedding_service.generate_embedding(chunk)
                embedded_chunks += 1

                if store_in_vector_db:
                    design_embedding = DesignEmbedding(
                        design_id=f"{document_id}_chunk_{index}",
                        design_summary=chunk,
                        embedding=embedding,
                        metadata={
                            "source": "pdf_upload",
                            "document_id": document_id,
                            "file_name": file_name,
                            "chunk_index": index,
                            "chunk_count": len(chunks),
                            "page_count": len(reader.pages),
                            "ingested_at": datetime.utcnow().isoformat(),
                        },
                    )
                    await self.embedding_service.store_embedding_in_vector_db(design_embedding)
                    stored_vector += 1

        return {
            "document_id": document_id,
            "file_name": file_name,
            "page_count": len(reader.pages),
            "chunk_count": len(chunks),
            "embedded_chunks": embedded_chunks,
            "stored_vector": stored_vector,
            "status": "completed",
        }

    def _chunk_text(self, text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
        chunks: List[str] = []
        start = 0
        length = len(text)

        while start < length:
            end = min(start + chunk_size, length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == length:
                break
            start = max(end - overlap, 0)

        return chunks


async def get_pdf_ingestion_service(
    embedding_service: EmbeddingService,
) -> PdfIngestionService:
    return PdfIngestionService(embedding_service)
