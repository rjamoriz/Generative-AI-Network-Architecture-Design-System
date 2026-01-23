"""
Validation API Routes
Endpoints for network design validation
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.models.network_design import NetworkDesign, DesignStatus
from app.models.validation_result import ValidationResult, ValidationRequest
from app.agents.validation_agent import ValidationAgent, get_validation_agent
from app.core.database import get_postgres_session
from app.db.postgres_repository import DesignRepository, ValidationRepository, AuditLogRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/validate", response_model=ValidationResult)
async def validate_design(
    design: NetworkDesign,
    validation_mode: str = "strict",
    validator: ValidationAgent = Depends(get_validation_agent),
    session: AsyncSession = Depends(get_postgres_session),
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

        # Persist validation if design is known
        if design.design_id:
            design_repo = DesignRepository()
            validation_repo = ValidationRepository()
            validation_id = await validation_repo.create(session, result, validation_mode)
            status_value = DesignStatus.VALIDATED.value if result.passed else DesignStatus.REJECTED.value
            await design_repo.update_validation(
                session,
                design.design_id,
                validation_id,
                result.overall_score,
                status=status_value,
            )
            result.validation_id = validation_id
        
        audit_repo = AuditLogRepository()
        await audit_repo.log(
            session,
            action="design_validate",
            status="success",
            resource_type="network_design",
            resource_id=design.design_id,
            message="Design validation completed",
            metadata={
                "validation_id": result.validation_id,
                "score": result.overall_score,
                "passed": result.passed,
                "mode": validation_mode,
            },
        )
        logger.info(f"Validation complete: score={result.overall_score:.2f}, passed={result.passed}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        try:
            audit_repo = AuditLogRepository()
            await audit_repo.log(
                session,
                action="design_validate",
                status="failed",
                resource_type="network_design",
                resource_id=design.design_id,
                message=str(e),
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validate-by-id/{design_id}", response_model=ValidationResult)
async def validate_design_by_id(
    design_id: str,
    request: ValidationRequest,
    validator: ValidationAgent = Depends(get_validation_agent),
    session: AsyncSession = Depends(get_postgres_session),
) -> ValidationResult:
    """
    Validate design by ID
    
    Retrieves design from database and validates it
    """
    try:
        design_repo = DesignRepository()
        validation_repo = ValidationRepository()
        record = await design_repo.get(session, design_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )

        design = design_repo.to_model(record)
        result = await validator.validate_design(design, request.validation_mode)

        validation_id = await validation_repo.create(session, result, request.validation_mode)
        status_value = DesignStatus.VALIDATED.value if result.passed else DesignStatus.REJECTED.value
        await design_repo.update_validation(
            session,
            design_id,
            validation_id,
            result.overall_score,
            status=status_value,
        )
        result.validation_id = validation_id
        audit_repo = AuditLogRepository()
        await audit_repo.log(
            session,
            action="design_validate",
            status="success",
            resource_type="network_design",
            resource_id=design_id,
            message="Design validation completed",
            metadata={
                "validation_id": result.validation_id,
                "score": result.overall_score,
                "passed": result.passed,
                "mode": request.validation_mode,
            },
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        try:
            audit_repo = AuditLogRepository()
            await audit_repo.log(
                session,
                action="design_validate",
                status="failed",
                resource_type="network_design",
                resource_id=design_id,
                message=str(e),
            )
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
