"""
Pydantic models package
"""
from app.models.network_design import (
    NetworkDesign,
    DesignSummary,
    DesignEmbedding,
    NetworkType,
    TopologyType,
    RedundancyLevel,
    SecurityLevel,
    DesignStatus,
    ComponentSpecification,
    Connection,
    TopologyDetails,
    BandwidthRequirement,
    ScaleRequirement
)

from app.models.requirements import (
    NetworkRequirements,
    RequirementAnalysisResult,
    RequirementValidation,
    Constraint
)

from app.models.validation_result import (
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ValidationCategory,
    DeterministicValidationResult,
    LLMValidationResult,
    ValidationRequest,
    ValidationHistory
)

__all__ = [
    # Network Design
    "NetworkDesign",
    "DesignSummary",
    "DesignEmbedding",
    "NetworkType",
    "TopologyType",
    "RedundancyLevel",
    "SecurityLevel",
    "DesignStatus",
    "ComponentSpecification",
    "Connection",
    "TopologyDetails",
    "BandwidthRequirement",
    "ScaleRequirement",
    
    # Requirements
    "NetworkRequirements",
    "RequirementAnalysisResult",
    "RequirementValidation",
    "Constraint",
    
    # Validation
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationCategory",
    "DeterministicValidationResult",
    "LLMValidationResult",
    "ValidationRequest",
    "ValidationHistory",
]
