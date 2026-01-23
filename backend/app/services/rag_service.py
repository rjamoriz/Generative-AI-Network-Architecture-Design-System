"""
RAG (Retrieval-Augmented Generation) Service
Semantic search and context retrieval for network designs
"""
from typing import List, Optional, Dict, Any, Tuple
import logging
import numpy as np

from app.core.config import get_settings
from app.core.database import get_database_manager
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import get_vector_store
from app.models.network_design import NetworkDesign, DesignEmbedding, NetworkType, TopologyType
from app.models.requirements import NetworkRequirements

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG service for retrieving similar network designs
    Implements semantic search with filtering and ranking
    """
    
    def __init__(self):
        """Initialize RAG service"""
        self.settings = get_settings()
        self.db_manager = get_database_manager()
        self.embedding_service = EmbeddingService()
        
        # RAG configuration
        self.top_k = self.settings.rag_top_k
        self.similarity_threshold = self.settings.rag_similarity_threshold
        self.max_context_tokens = self.settings.rag_max_context_tokens
        
        logger.info(f"RAG service initialized (top_k: {self.top_k}, threshold: {self.similarity_threshold})")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0-1)
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    async def _vector_search(self,
                             query_embedding: List[float],
                             top_k: int,
                             filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform vector search using configured vector store (MongoDB or Astra)
        """
        try:
            vector_store = get_vector_store()
            results = await vector_store.search(query_embedding, top_k, filters)
            logger.info(f"Vector search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            # Fallback to brute force search (MongoDB only)
            return await self._brute_force_search(query_embedding, top_k, filters)
    
    async def _brute_force_search(self,
                                  query_embedding: List[float],
                                  top_k: int,
                                  filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Fallback brute force similarity search
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            filters: Optional filters
        
        Returns:
            List of matching documents with scores
        """
        try:
            collection = self.db_manager.get_mongodb_collection()
            
            # Build query with filters
            query = {}
            if filters:
                for key, value in filters.items():
                    query[f"metadata.{key}"] = value
            
            # Retrieve all matching documents
            cursor = collection.find(query)
            documents = await cursor.to_list(length=1000)  # Limit to 1000 for performance
            
            # Calculate similarities
            results = []
            for doc in documents:
                if "embedding" in doc:
                    similarity = self._cosine_similarity(query_embedding, doc["embedding"])
                    results.append({
                        "design_id": doc.get("design_id"),
                        "design_summary": doc.get("design_summary"),
                        "metadata": doc.get("metadata", {}),
                        "score": similarity
                    })
            
            # Sort by similarity and take top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:top_k]
            
            logger.info(f"Brute force search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Brute force search failed: {e}")
            return []
    
    async def search_similar_designs(self,
                                    query_text: str,
                                    top_k: Optional[int] = None,
                                    filters: Optional[Dict[str, Any]] = None,
                                    min_similarity: Optional[float] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar network designs using text query
        
        Args:
            query_text: Text description to search for
            top_k: Number of results (defaults to config)
            filters: Optional metadata filters
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of (design_id, similarity_score, metadata) tuples
        """
        top_k = top_k or self.top_k
        min_similarity = min_similarity or self.similarity_threshold
        
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        
        # Perform vector search
        results = await self._vector_search(query_embedding, top_k, filters)
        
        # Filter by similarity threshold
        filtered_results = [
            (r["design_id"], r["score"], r["metadata"])
            for r in results
            if r["score"] >= min_similarity
        ]
        
        logger.info(f"Found {len(filtered_results)} designs above threshold {min_similarity}")
        return filtered_results
    
    async def search_by_requirements(self,
                                    requirements: NetworkRequirements,
                                    top_k: Optional[int] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for designs matching requirements
        
        Args:
            requirements: Network requirements
            top_k: Number of results
        
        Returns:
            List of (design_id, similarity_score, metadata) tuples
        """
        # Convert requirements to search text
        search_text = f"""
        Network Type: {requirements.network_type.value}
        Scale: {requirements.scale.devices} devices, {requirements.scale.users} users
        Bandwidth: {requirements.bandwidth.min} to {requirements.bandwidth.max}
        Security Level: {requirements.security_level.value}
        Redundancy: {requirements.redundancy.value}
        """
        
        if requirements.topology_preference:
            search_text += f"\nTopology: {requirements.topology_preference.value}"
        
        if requirements.compliance:
            search_text += f"\nCompliance: {', '.join(requirements.compliance)}"
        
        # Build metadata filters
        filters = {
            "network_type": requirements.network_type.value,
            "security_level": requirements.security_level.value
        }
        
        # Search with filters
        return await self.search_similar_designs(search_text, top_k, filters)
    
    async def get_design_by_id(self, design_id: str) -> Optional[NetworkDesign]:
        """
        Retrieve full design by ID from PostgreSQL
        
        Args:
            design_id: Design identifier
        
        Returns:
            Network design or None
        """
        try:
            async with self.db_manager.get_postgres_session() as session:
                # TODO: Implement actual database query
                # For now, return None as placeholder
                logger.warning(f"get_design_by_id not fully implemented for {design_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve design {design_id}: {e}")
            return None
    
    async def build_rag_context(self,
                               requirements: NetworkRequirements,
                               max_designs: Optional[int] = None) -> Dict[str, Any]:
        """
        Build RAG context for design generation
        
        Args:
            requirements: Network requirements
            max_designs: Maximum number of designs to include
        
        Returns:
            RAG context dictionary
        """
        max_designs = max_designs or self.top_k
        
        # Search for similar designs
        similar_designs = await self.search_by_requirements(requirements, max_designs)
        
        # Build context
        context = {
            "requirements_summary": {
                "network_type": requirements.network_type.value,
                "scale": {
                    "devices": requirements.scale.devices,
                    "users": requirements.scale.users
                },
                "security_level": requirements.security_level.value,
                "redundancy": requirements.redundancy.value
            },
            "similar_designs": [],
            "design_count": len(similar_designs),
            "average_similarity": 0.0
        }
        
        # Add similar designs to context
        total_similarity = 0.0
        for design_id, similarity, metadata in similar_designs:
            context["similar_designs"].append({
                "design_id": design_id,
                "similarity_score": similarity,
                "metadata": metadata
            })
            total_similarity += similarity
        
        if similar_designs:
            context["average_similarity"] = total_similarity / len(similar_designs)
        
        logger.info(f"Built RAG context with {len(similar_designs)} designs (avg similarity: {context['average_similarity']:.3f})")
        return context
    
    async def rank_designs_by_relevance(self,
                                       design_ids: List[str],
                                       requirements: NetworkRequirements) -> List[Tuple[str, float]]:
        """
        Rank designs by relevance to requirements
        
        Args:
            design_ids: List of design IDs to rank
            requirements: Network requirements
        
        Returns:
            List of (design_id, relevance_score) tuples, sorted by relevance
        """
        # Generate requirements embedding
        req_text = f"{requirements.network_type.value} {requirements.scale.devices} devices"
        req_embedding = await self.embedding_service.generate_embedding(req_text)
        
        # Get embeddings for designs and calculate similarities
        ranked = []
        collection = self.db_manager.get_mongodb_collection()
        
        for design_id in design_ids:
            try:
                doc = await collection.find_one({"design_id": design_id})
                if doc and "embedding" in doc:
                    similarity = self._cosine_similarity(req_embedding, doc["embedding"])
                    ranked.append((design_id, similarity))
            except Exception as e:
                logger.error(f"Failed to rank design {design_id}: {e}")
        
        # Sort by relevance
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Ranked {len(ranked)} designs by relevance")
        return ranked
    
    async def get_design_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about designs in vector database
        
        Returns:
            Statistics dictionary
        """
        try:
            collection = self.db_manager.get_mongodb_collection()
            
            total_count = await collection.count_documents({})
            
            # Count by network type
            pipeline = [
                {"$group": {
                    "_id": "$metadata.network_type",
                    "count": {"$sum": 1}
                }}
            ]
            type_counts = await collection.aggregate(pipeline).to_list(length=100)
            
            stats = {
                "total_designs": total_count,
                "by_network_type": {item["_id"]: item["count"] for item in type_counts if item["_id"]},
                "vector_dimensions": self.settings.embedding_dimensions
            }
            
            logger.info(f"Design statistics: {total_count} total designs")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get design statistics: {e}")
            return {"total_designs": 0, "by_network_type": {}}


# Dependency injection for FastAPI
def get_rag_service() -> RAGService:
    """Get RAG service instance for dependency injection"""
    return RAGService()
