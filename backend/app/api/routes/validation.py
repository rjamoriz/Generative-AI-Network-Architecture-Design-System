"""
Validation API Routes
Endpoints for network design validation
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.models.network_design import NetworkDesign
from app.models.validation_result import ValidationResult, ValidationRequest
from app.agents.validation_agent import ValidationAgent, get_validation_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/validate", response_model=ValidationResult)
async def validate_design(
    design: NetworkDesign,
    validation_mode: str = "strict",
    validator: ValidationAgent = Depends(get_validation_agent)
) -> ValidationResult:
    """
    Validate network design
    
    Performs both deterministic rule-based and LLM-based validation
    
    Validation modes:
    - strict: 90% threshold, all critical rules must pass
    - standard: 85% threshold (default)
    - lenient: 75% threshold
    """
    try:
        if validation_mode not in ["strict", "standard", "lenient"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid validation mode: {validation_mode}. Must be strict, standard, or lenient"
            )
        
        logger.info(f"Validating design: {design.name} (mode: {validation_mode})")
        
        # Validate design
        result = await validator.validate_design(design, validation_mode)
        
        logger.info(f"Validation complete: score={result.overall_score:.2f}, passed={result.passed}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validate-by-id/{design_id}", response_model=ValidationResult)
async def validate_design_by_id(
    design_id: str,
    request: ValidationRequest,
    validator: ValidationAgent = Depends(get_validation_agent)
) -> ValidationResult:
    """
    Validate design by ID
    
    Retrieves design from database and validates it
    """
    try:
        # TODO: Implement actual database retrieval
        logger.warning(f"validate_design_by_id not fully implemented for {design_id}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Design retrieval from database not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
