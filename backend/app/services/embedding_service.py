"""
Embedding Service
Generates and caches embeddings for network designs
"""
from typing import List, Optional, Dict, Any
import logging
import hashlib
import json

from app.core.config import get_settings
from app.core.database import get_database_manager
from app.services.llm_service import LLMService
from app.models.network_design import NetworkDesign, DesignEmbedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing embeddings
    Supports caching in Redis for performance
    """
    
    def __init__(self):
        """Initialize embedding service"""
        self.settings = get_settings()
        self.llm_service = LLMService()
        self.db_manager = get_database_manager()
        
        # Embedding configuration
        self.embedding_model = self.settings.embedding_model
        self.embedding_dimensions = self.settings.embedding_dimensions
        self.batch_size = self.settings.embedding_batch_size
        
        logger.info(f"Embedding service initialized (model: {self.embedding_model}, dim: {self.embedding_dimensions})")
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate cache key for embedding
        
        Args:
            text: Text to generate key for
        
        Returns:
            Cache key (hash of text)
        """
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"embedding:{self.embedding_model}:{text_hash}"
    
    async def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """
        Retrieve embedding from cache
        
        Args:
            text: Text to retrieve embedding for
        
        Returns:
            Cached embedding or None
        """
        try:
            redis = await self.db_manager.get_redis_client()
            cache_key = self._generate_cache_key(text)
            
            cached = await redis.get(cache_key)
            if cached:
                embedding = json.loads(cached)
                logger.debug(f"Cache hit for embedding (key: {cache_key[:16]}...)")
                return embedding
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to retrieve cached embedding: {e}")
            return None
    
    async def _cache_embedding(self, text: str, embedding: List[float], ttl: int = 86400):
        """
        Cache embedding in Redis
        
        Args:
            text: Text that was embedded
            embedding: Embedding vector
            ttl: Time to live in seconds (default 24 hours)
        """
        try:
            redis = await self.db_manager.get_redis_client()
            cache_key = self._generate_cache_key(text)
            
            await redis.setex(
                cache_key,
                ttl,
                json.dumps(embedding)
            )
            
            logger.debug(f"Cached embedding (key: {cache_key[:16]}...)")
            
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            use_cache: Whether to use cache
        
        Returns:
            Embedding vector
        """
        # Check cache first
        if use_cache:
            cached = await self._get_cached_embedding(text)
            if cached:
                return cached
        
        # Generate new embedding
        try:
            embedding = await self.llm_service.embed(text)
            
            # Cache for future use
            if use_cache:
                await self._cache_embedding(text, embedding)
            
            logger.info(f"Generated embedding for text ({len(text)} chars, {len(embedding)} dimensions)")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, 
                                       texts: List[str], 
                                       use_cache: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            batch_embeddings = []
            for text in batch:
                embedding = await self.generate_embedding(text, use_cache)
                batch_embeddings.append(embedding)
            
            embeddings.extend(batch_embeddings)
            logger.info(f"Processed batch {i // self.batch_size + 1} ({len(batch)} texts)")
        
        return embeddings
    
    def _design_to_text(self, design: NetworkDesign) -> str:
        """
        Convert network design to text representation for embedding
        
        Args:
            design: Network design
        
        Returns:
            Text representation
        """
        parts = [
            f"Network Design: {design.name}",
            f"Type: {design.network_type.value}",
            f"Topology: {design.topology.topology_type.value}",
            f"Scale: {design.scale.devices} devices, {design.scale.users} users",
            f"Bandwidth: {design.bandwidth_requirement.min} to {design.bandwidth_requirement.max}",
            f"Security Level: {design.security_level.value}",
            f"Redundancy: {design.topology.redundancy_level.value}",
        ]
        
        if design.description:
            parts.append(f"Description: {design.description}")
        
        if design.compliance_requirements:
            parts.append(f"Compliance: {', '.join(design.compliance_requirements)}")
        
        if design.design_rationale:
            parts.append(f"Rationale: {design.design_rationale}")
        
        if design.key_features:
            parts.append(f"Features: {', '.join(design.key_features)}")
        
        # Include component summary
        if design.components:
            component_types = {}
            for comp in design.components:
                component_types[comp.component_type] = component_types.get(comp.component_type, 0) + 1
            
            comp_summary = ", ".join([f"{count} {ctype}" for ctype, count in component_types.items()])
            parts.append(f"Components: {comp_summary}")
        
        return " | ".join(parts)
    
    async def embed_design(self, design: NetworkDesign, use_cache: bool = True) -> DesignEmbedding:
        """
        Generate embedding for network design
        
        Args:
            design: Network design to embed
            use_cache: Whether to use cache
        
        Returns:
            Design embedding
        """
        # Convert design to text
        text = self._design_to_text(design)
        
        # Generate embedding
        embedding = await self.generate_embedding(text, use_cache)
        
        # Create design embedding object
        design_embedding = DesignEmbedding(
            design_id=design.design_id or "unknown",
            design_summary=text,
            embedding=embedding,
            metadata={
                "network_type": design.network_type.value,
                "topology_type": design.topology.topology_type.value,
                "security_level": design.security_level.value,
                "component_count": len(design.components),
                "validation_score": design.validation_score
            }
        )
        
        logger.info(f"Generated embedding for design: {design.name}")
        return design_embedding
    
    async def embed_designs_batch(self, 
                                  designs: List[NetworkDesign],
                                  use_cache: bool = True) -> List[DesignEmbedding]:
        """
        Generate embeddings for multiple designs
        
        Args:
            designs: List of network designs
            use_cache: Whether to use cache
        
        Returns:
            List of design embeddings
        """
        design_embeddings = []
        
        for design in designs:
            try:
                embedding = await self.embed_design(design, use_cache)
                design_embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed design {design.design_id}: {e}")
                # Continue with other designs
        
        logger.info(f"Generated embeddings for {len(design_embeddings)}/{len(designs)} designs")
        return design_embeddings
    
    async def store_embedding_in_vector_db(self, design_embedding: DesignEmbedding):
        """
        Store design embedding in vector database (MongoDB)
        
        Args:
            design_embedding: Design embedding to store
        """
        try:
            collection = self.db_manager.get_mongodb_collection()
            
            document = {
                "design_id": design_embedding.design_id,
                "design_summary": design_embedding.design_summary,
                "embedding": design_embedding.embedding,
                "metadata": design_embedding.metadata,
                "created_at": datetime.utcnow()
            }
            
            # Upsert (update if exists, insert if not)
            await collection.update_one(
                {"design_id": design_embedding.design_id},
                {"$set": document},
                upsert=True
            )
            
            logger.info(f"Stored embedding in vector DB: {design_embedding.design_id}")
            
        except Exception as e:
            logger.error(f"Failed to store embedding in vector DB: {e}")
            raise
    
    async def store_embeddings_batch(self, design_embeddings: List[DesignEmbedding]):
        """
        Store multiple design embeddings in vector database
        
        Args:
            design_embeddings: List of design embeddings
        """
        for embedding in design_embeddings:
            try:
                await self.store_embedding_in_vector_db(embedding)
            except Exception as e:
                logger.error(f"Failed to store embedding {embedding.design_id}: {e}")
        
        logger.info(f"Stored {len(design_embeddings)} embeddings in vector DB")
    
    async def clear_cache(self, pattern: str = "embedding:*"):
        """
        Clear embedding cache
        
        Args:
            pattern: Redis key pattern to clear
        """
        try:
            redis = await self.db_manager.get_redis_client()
            
            # Get all keys matching pattern
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached embeddings")
            else:
                logger.info("No cached embeddings to clear")
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


# Import datetime for store methods
from datetime import datetime


# Dependency injection for FastAPI
def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance for dependency injection"""
    return EmbeddingService()
