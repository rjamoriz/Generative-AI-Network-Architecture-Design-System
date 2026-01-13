"""
Retrieval API Routes
Endpoints for RAG and similar design search
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import logging

from app.models.requirements import NetworkRequirements
from app.services.rag_service import RAGService, get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_similar_designs(
    query_text: str,
    top_k: int = Query(default=5, ge=1, le=20),
    min_similarity: float = Query(default=0.75, ge=0.0, le=1.0),
    rag_service: RAGService = Depends(get_rag_service)
) -> List[Dict[str, Any]]:
    """
    Search for similar network designs using text query
    
    Returns list of similar designs with similarity scores
    """
    try:
        logger.info(f"Searching for similar designs: '{query_text[:50]}...' (top_k={top_k})")
        
        # Search for similar designs
        results = await rag_service.search_similar_designs(
            query_text=query_text,
            top_k=top_k,
            min_similarity=min_similarity
        )
        
        # Format results
        formatted_results = [
            {
                "design_id": design_id,
                "similarity_score": score,
                "metadata": metadata
            }
            for design_id, score, metadata in results
        ]
        
        logger.info(f"Found {len(formatted_results)} similar designs")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/search-by-requirements", response_model=List[Dict[str, Any]])
async def search_by_requirements(
    requirements: NetworkRequirements,
    top_k: int = Query(default=5, ge=1, le=20),
    rag_service: RAGService = Depends(get_rag_service)
) -> List[Dict[str, Any]]:
    """
    Search for designs matching requirements
    
    Uses requirements to find similar validated designs
    """
    try:
        logger.info(f"Searching by requirements: {requirements.project_name}")
        
        # Search by requirements
        results = await rag_service.search_by_requirements(requirements, top_k)
        
        # Format results
        formatted_results = [
            {
                "design_id": design_id,
                "similarity_score": score,
                "metadata": metadata
            }
            for design_id, score, metadata in results
        ]
        
        logger.info(f"Found {len(formatted_results)} matching designs")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    Get statistics about designs in vector database
    
    Returns counts by network type and other metrics
    """
    try:
        logger.info("Retrieving design statistics")
        
        stats = await rag_service.get_design_statistics()
        
        logger.info(f"Statistics retrieved: {stats.get('total_designs', 0)} total designs")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
