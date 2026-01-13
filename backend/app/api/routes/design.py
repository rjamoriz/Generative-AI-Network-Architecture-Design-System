"""
Design API Routes
Endpoints for network design generation and management
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
import logging

from app.models.requirements import NetworkRequirements, RequirementAnalysisResult
from app.models.network_design import NetworkDesign, DesignSummary
from app.agents.requirement_analyzer import RequirementAnalyzerAgent, get_requirement_analyzer
from app.agents.design_synthesizer import DesignSynthesizerAgent, get_design_synthesizer
from app.services.embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-requirements", response_model=RequirementAnalysisResult)
async def analyze_requirements(
    requirements: NetworkRequirements,
    analyzer: RequirementAnalyzerAgent = Depends(get_requirement_analyzer)
) -> RequirementAnalysisResult:
    """
    Analyze network requirements
    
    Extracts key requirements, assesses feasibility, and recommends topology
    """
    try:
        logger.info(f"Analyzing requirements for: {requirements.project_name}")
        
        # Validate requirements first
        validation = await analyzer.validate_requirements(requirements)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Requirements validation failed",
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                }
            )
        
        # Analyze requirements
        analysis = await analyzer.analyze_requirements(requirements)
        
        logger.info(f"Requirements analyzed: confidence={analysis.confidence_score:.2f}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze requirements: {str(e)}"
        )


@router.post("/generate", response_model=NetworkDesign)
async def generate_design(
    requirements: NetworkRequirements,
    use_rag: bool = True,
    use_historical: bool = False,
    historical_context: Optional[str] = None,
    analyzer: RequirementAnalyzerAgent = Depends(get_requirement_analyzer),
    synthesizer: DesignSynthesizerAgent = Depends(get_design_synthesizer),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> NetworkDesign:
    """
    Generate network design from requirements
    
    Uses RAG to retrieve similar designs, historical data for insights, and LLM to synthesize new design
    
    Args:
        requirements: Network requirements
        use_rag: Enable RAG for similar design retrieval
        use_historical: Enable historical design data analysis
        historical_context: Pre-built historical context (from /api/v1/historical/context/build)
    """
    try:
        logger.info(f"Generating design for: {requirements.project_name} (RAG: {use_rag}, Historical: {use_historical})")
        
        # Step 1: Analyze requirements
        analysis = await analyzer.analyze_requirements(requirements)
        
        if not analysis.is_feasible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Requirements are not feasible",
                    "concerns": analysis.feasibility_concerns
                }
            )
        
        # Step 2: Synthesize design with historical context
        design = await synthesizer.synthesize_design(
            requirements, 
            analysis, 
            use_rag,
            use_historical,
            historical_context
        )
        
        # Step 3: Generate and store embedding (async, don't wait)
        try:
            design_embedding = await embedding_service.embed_design(design)
            await embedding_service.store_embedding_in_vector_db(design_embedding)
            logger.info(f"Design embedding stored: {design.design_id}")
        except Exception as e:
            logger.warning(f"Failed to store embedding: {e}")
            # Don't fail the request if embedding storage fails
        
        logger.info(f"Design generated: {design.name} ({design.design_id})")
        return design
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate design: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate design: {str(e)}"
        )


@router.post("/{design_id}/refine", response_model=NetworkDesign)
async def refine_design(
    design_id: str,
    design: NetworkDesign,
    feedback: str,
    requirements: NetworkRequirements,
    synthesizer: DesignSynthesizerAgent = Depends(get_design_synthesizer)
) -> NetworkDesign:
    """
    Refine existing design based on feedback
    
    Uses feedback to improve the design while maintaining requirements
    """
    try:
        logger.info(f"Refining design: {design_id}")
        
        if design.design_id != design_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Design ID mismatch"
            )
        
        refined_design = await synthesizer.refine_design(design, feedback, requirements)
        
        logger.info(f"Design refined: {refined_design.name} (v{refined_design.version})")
        return refined_design
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refine design: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refine design: {str(e)}"
        )


@router.get("/{design_id}", response_model=NetworkDesign)
async def get_design(design_id: str) -> NetworkDesign:
    """
    Retrieve design by ID
    
    Returns complete design information
    """
    try:
        # TODO: Implement actual database retrieval
        logger.warning(f"get_design not fully implemented for {design_id}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Design retrieval from database not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve design: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve design: {str(e)}"
        )
