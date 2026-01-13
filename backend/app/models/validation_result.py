"""
Pydantic models for validation results
Structured validation output models
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(str, Enum):
    """Categories of validation"""
    CAPACITY = "capacity"
    PROTOCOL = "protocol"
    COMPLIANCE = "compliance"
    TOPOLOGY = "topology"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REDUNDANCY = "redundancy"
    SCALABILITY = "scalability"


class ValidationIssue(BaseModel):
    """Individual validation issue"""
    issue_id: str = Field(..., description="Unique issue identifier")
    category: ValidationCategory
    severity: ValidationSeverity
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Detailed description")
    affected_components: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = Field(None, description="How to fix")
    rule_id: Optional[str] = Field(None, description="Rule that triggered this issue")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_id": "issue_001",
                "category": "capacity",
                "severity": "error",
                "title": "Insufficient bandwidth",
                "description": "Core switch bandwidth insufficient for expected traffic",
                "affected_components": ["core_switch_01"],
                "recommendation": "Upgrade to 100Gbps interfaces"
            }
        }


class RuleValidationResult(BaseModel):
    """Result from a single validation rule"""
    rule_id: str
    rule_name: str
    category: ValidationCategory
    passed: bool
    score: float = Field(..., ge=0.0, le=1.0, description="Rule score")
    message: str
    details: Optional[Dict[str, Any]] = Field(None)
    issues: List[ValidationIssue] = Field(default_factory=list)


class DeterministicValidationResult(BaseModel):
    """
    Results from deterministic rule-based validation
    Capacity, protocol, compliance, topology rules
    """
    overall_score: float = Field(..., ge=0.0, le=1.0)
    passed: bool = Field(..., description="All critical rules passed")
    
    # Rule results by category
    capacity_results: List[RuleValidationResult] = Field(default_factory=list)
    protocol_results: List[RuleValidationResult] = Field(default_factory=list)
    compliance_results: List[RuleValidationResult] = Field(default_factory=list)
    topology_results: List[RuleValidationResult] = Field(default_factory=list)
    
    # Aggregated issues
    critical_issues: List[ValidationIssue] = Field(default_factory=list)
    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    
    # Summary
    total_rules_executed: int = Field(..., ge=0)
    rules_passed: int = Field(..., ge=0)
    rules_failed: int = Field(..., ge=0)
    
    execution_time_ms: Optional[float] = Field(None, description="Validation execution time")


class LLMValidationResult(BaseModel):
    """
    Results from LLM-based probabilistic validation
    Edge case analysis, contextual reasoning
    """
    overall_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM confidence in assessment")
    
    # Analysis results
    edge_case_analysis: str = Field(..., description="Analysis of edge cases")
    contextual_assessment: str = Field(..., description="Contextual reasoning")
    best_practice_evaluation: str = Field(..., description="Best practices assessment")
    
    # Identified concerns
    concerns: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    
    # LLM metadata
    model_used: str = Field(..., description="LLM model used for validation")
    tokens_used: Optional[int] = Field(None)
    execution_time_ms: Optional[float] = Field(None)


class ValidationResult(BaseModel):
    """
    Complete validation result combining deterministic and LLM validation
    """
    validation_id: str = Field(..., description="Unique validation identifier")
    design_id: str = Field(..., description="Associated design ID")
    
    # Validation scores
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Combined validation score")
    deterministic_score: float = Field(..., ge=0.0, le=1.0)
    llm_score: float = Field(..., ge=0.0, le=1.0)
    
    # Validation results
    deterministic_validation: DeterministicValidationResult
    llm_validation: LLMValidationResult
    
    # Overall assessment
    passed: bool = Field(..., description="Design passed validation threshold")
    validation_threshold: float = Field(default=0.85, description="Threshold used")
    
    # All issues aggregated
    all_issues: List[ValidationIssue] = Field(default_factory=list)
    critical_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    warning_count: int = Field(default=0, ge=0)
    
    # Explanation and reasoning
    summary: str = Field(..., description="Validation summary")
    explanation: str = Field(..., description="Detailed explanation of results")
    key_findings: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    required_changes: List[str] = Field(default_factory=list)
    optional_improvements: List[str] = Field(default_factory=list)
    
    # Metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: str = Field(default="validation_agent")
    validation_version: str = Field(default="1.0")
    total_execution_time_ms: Optional[float] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "validation_id": "val_123",
                "design_id": "design_456",
                "overall_score": 0.92,
                "deterministic_score": 0.95,
                "llm_score": 0.89,
                "passed": True,
                "critical_count": 0,
                "error_count": 0,
                "warning_count": 3,
                "summary": "Design passed validation with minor warnings",
                "key_findings": [
                    "All capacity requirements met",
                    "Redundancy properly configured",
                    "Minor optimization opportunities identified"
                ]
            }
        }


class ValidationHistory(BaseModel):
    """History of validation attempts for a design"""
    design_id: str
    validations: List[ValidationResult] = Field(default_factory=list)
    iteration_count: int = Field(default=0, ge=0)
    score_progression: List[float] = Field(default_factory=list)
    latest_validation: Optional[ValidationResult] = None


class ValidationRequest(BaseModel):
    """Request to validate a design"""
    design_id: str
    validation_mode: str = Field(default="strict", description="strict, standard, or lenient")
    include_llm_validation: bool = Field(default=True)
    custom_rules: List[str] = Field(default_factory=list, description="Additional rule IDs to apply")
    skip_rules: List[str] = Field(default_factory=list, description="Rule IDs to skip")
