"""
Vector Store Abstraction
Supports MongoDB Atlas Vector Search and DataStax Astra DB
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import httpx
import numpy as np

from app.core.config import get_settings
from app.core.database import get_database_manager
from app.models.network_design import DesignEmbedding

logger = logging.getLogger(__name__)


class BaseVectorStore(ABC):
    """Abstract vector store interface"""

    async def ensure_ready(self) -> None:
        """Best-effort initialization for vector store"""
        return None

    @abstractmethod
    async def store_embedding(self, design_embedding: DesignEmbedding) -> None:
        """Store a single embedding"""
        raise NotImplementedError

    async def store_embeddings(self, embeddings: List[DesignEmbedding]) -> None:
        """Store multiple embeddings"""
        for embedding in embeddings:
            await self.store_embedding(embedding)

    @abstractmethod
    async def search(self,
                     query_embedding: List[float],
                     top_k: int,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        raise NotImplementedError


class MongoVectorStore(BaseVectorStore):
    """MongoDB Atlas vector store implementation"""

    def __init__(self):
        self.settings = get_settings()
        self.db_manager = get_database_manager()
        self._index_checked = False

    async def ensure_ready(self) -> None:
        if self._index_checked:
            return

        collection = self.db_manager.get_mongodb_collection()

        try:
            existing = await collection.list_search_indexes().to_list(length=100)
            if any(index.get("name") == "vector_index" for index in existing):
                self._index_checked = True
                return

            await collection.create_search_index(
                {
                    "name": "vector_index",
                    "definition": {
                        "fields": [
                            {
                                "type": "vector",
                                "path": "embedding",
                                "numDimensions": self.settings.embedding_dimensions,
                                "similarity": "cosine",
                            },
                            {"type": "filter", "path": "metadata.network_type"},
                            {"type": "filter", "path": "metadata.topology_type"},
                            {"type": "filter", "path": "metadata.status"},
                        ]
                    },
                }
            )
            logger.info("MongoDB vector search index provisioned")
        except Exception as exc:
            logger.warning(f"Vector index provisioning skipped: {exc}")
        finally:
            self._index_checked = True

    async def store_embedding(self, design_embedding: DesignEmbedding) -> None:
        collection = self.db_manager.get_mongodb_collection()
        document = {
            "design_id": design_embedding.design_id,
            "design_summary": design_embedding.design_summary,
            "embedding": design_embedding.embedding,
            "metadata": design_embedding.metadata,
            "created_at": datetime.utcnow()
        }

        await collection.update_one(
            {"design_id": design_embedding.design_id},
            {"$set": document},
            upsert=True
        )
        logger.info(f"Stored embedding in MongoDB: {design_embedding.design_id}")

    async def search(self,
                     query_embedding: List[float],
                     top_k: int,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        collection = self.db_manager.get_mongodb_collection()

        pipeline: List[Dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": top_k * 10,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "design_id": 1,
                    "design_summary": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        if filters:
            match_stage = {"$match": {}}
            for key, value in filters.items():
                match_stage["$match"][f"metadata.{key}"] = value
            pipeline.insert(1, match_stage)

        try:
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=top_k)
            logger.info(f"MongoDB vector search returned {len(results)} results")
            return results
        except Exception as exc:
            logger.error(f"MongoDB vector search failed: {exc}")
            return await self._brute_force_search(collection, query_embedding, top_k, filters)

    async def _brute_force_search(self,
                                  collection,
                                  query_embedding: List[float],
                                  top_k: int,
                                  filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if filters:
            for key, value in filters.items():
                query[f"metadata.{key}"] = value

        cursor = collection.find(query)
        documents = await cursor.to_list(length=1000)

        results: List[Dict[str, Any]] = []
        query_vec = np.array(query_embedding)

        for doc in documents:
            embedding = doc.get("embedding")
            if not embedding:
                continue
            score = self._cosine_similarity(query_vec, np.array(embedding))
            results.append({
                "design_id": doc.get("design_id"),
                "design_summary": doc.get("design_summary"),
                "metadata": doc.get("metadata", {}),
                "score": score
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        denom = (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        if denom == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / denom)


class AstraVectorStore(BaseVectorStore):
    """DataStax Astra DB vector store implementation using REST Data API"""

    def __init__(self):
        self.settings = get_settings()

        if not self.settings.astra_db_id or not self.settings.astra_db_region:
            raise ValueError("Astra DB ID and region are required for Astra vector store")

        self.base_url = (
            f"https://{self.settings.astra_db_id}-{self.settings.astra_db_region}"
            f".apps.astra.datastax.com/api/rest/v2/namespaces/{self.settings.astra_db_keyspace}"
            f"/collections/{self.settings.astra_db_collection}"
        )
        self.headers = {
            "X-Cassandra-Token": self.settings.astra_db_token or "",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30)

    async def ensure_ready(self) -> None:
        if not self.settings.astra_db_token:
            raise ValueError("ASTRA_DB_TOKEN must be set for Astra vector store")
        # Astra collections are created via UI/API. Keep as a no-op.
        return None

    async def store_embedding(self, design_embedding: DesignEmbedding) -> None:
        if not self.settings.astra_db_token:
            raise ValueError("ASTRA_DB_TOKEN must be set for Astra vector store")

        payload = {
            "design_id": design_embedding.design_id,
            "design_summary": design_embedding.design_summary,
            "embedding": design_embedding.embedding,
            "metadata": design_embedding.metadata,
            "created_at": datetime.utcnow().isoformat()
        }

        response = await self.client.put(
            f"{self.base_url}/{design_embedding.design_id}",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        logger.info(f"Stored embedding in Astra DB: {design_embedding.design_id}")

    async def search(self,
                     query_embedding: List[float],
                     top_k: int,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.settings.astra_db_token:
            raise ValueError("ASTRA_DB_TOKEN must be set for Astra vector store")

        payload = {
            "vector": query_embedding,
            "limit": top_k,
            "filter": filters or {}
        }

        response = await self.client.post(
            f"{self.base_url}/vector/search",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()

        documents = data.get("data") or data.get("documents") or []
        results: List[Dict[str, Any]] = []

        for doc in documents:
            results.append({
                "design_id": doc.get("design_id") or doc.get("documentId"),
                "design_summary": doc.get("design_summary") or doc.get("document", {}).get("design_summary"),
                "metadata": doc.get("metadata") or doc.get("document", {}).get("metadata", {}),
                "score": doc.get("score", 0.0)
            })

        return results


_vector_store: Optional[BaseVectorStore] = None


def get_vector_store() -> BaseVectorStore:
    """Get configured vector store implementation"""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        provider = settings.vector_store_provider.lower()
        if provider == "astra":
            _vector_store = AstraVectorStore()
        else:
            _vector_store = MongoVectorStore()

        logger.info(f"Vector store initialized: {provider}")

    return _vector_store
