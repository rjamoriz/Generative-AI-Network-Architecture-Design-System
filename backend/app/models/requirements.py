"""
Pydantic models for network requirements
Structured input models for network design requirements
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.network_design import (
    NetworkType, TopologyType, RedundancyLevel, 
    SecurityLevel, BandwidthRequirement, ScaleRequirement
)


class ConstraintType(str):
    """Types of constraints"""
    BUDGET = "budget"
    TIMELINE = "timeline"
    VENDOR = "vendor"
    TECHNOLOGY = "technology"
    REGULATORY = "regulatory"
    PHYSICAL = "physical"


class Constraint(BaseModel):
    """Design constraint"""
    constraint_type: str = Field(..., description="Type of constraint")
    description: str = Field(..., description="Constraint description")
    value: Optional[Any] = Field(None, description="Constraint value")
    priority: str = Field(default="medium", description="Priority: low, medium, high, critical")
    is_hard_constraint: bool = Field(default=True, description="Must be satisfied vs. nice-to-have")


class NetworkRequirements(BaseModel):
    """
    Complete network requirements specification
    Input for the design generation process
    """
    requirements_id: Optional[str] = Field(None, description="Unique requirements identifier")
    
    # Basic information
    project_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, description="Detailed requirements description")
    
    # Network characteristics
    network_type: NetworkType
    topology_preference: Optional[TopologyType] = Field(None, description="Preferred topology")
    
    # Scale requirements
    scale: ScaleRequirement
    
    # Bandwidth requirements
    bandwidth: BandwidthRequirement
    
    # Redundancy and availability
    redundancy: RedundancyLevel
    availability_requirement: Optional[float] = Field(
        None, ge=0.0, le=1.0, 
        description="Required availability (e.g., 0.9999 for 99.99%)"
    )
    max_downtime_minutes_per_year: Optional[int] = Field(None, ge=0)
    
    # Security requirements
    security_level: SecurityLevel
    compliance: List[str] = Field(
        default_factory=list,
        description="Compliance requirements: PCI-DSS, HIPAA, ISO27001, SOC2, etc."
    )
    requires_segmentation: bool = Field(default=False, description="Network segmentation required")
    requires_encryption: bool = Field(default=False, description="Encryption required")
    
    # Technology preferences
    preferred_vendors: List[str] = Field(default_factory=list)
    excluded_vendors: List[str] = Field(default_factory=list)
    technology_stack: Optional[str] = Field(None, description="Preferred technology stack")
    sdn_required: bool = Field(default=False, description="SDN required")
    cloud_integration: bool = Field(default=False, description="Cloud integration needed")
    
    # Performance requirements
    max_latency_ms: Optional[int] = Field(None, ge=0, description="Maximum acceptable latency")
    min_throughput_gbps: Optional[float] = Field(None, ge=0, description="Minimum throughput")
    packet_loss_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Physical requirements
    number_of_sites: int = Field(default=1, ge=1)
    site_locations: List[str] = Field(default_factory=list)
    requires_wireless: bool = Field(default=False)
    requires_voip: bool = Field(default=False)
    requires_video_conferencing: bool = Field(default=False)
    
    # Constraints
    constraints: List[Constraint] = Field(default_factory=list)
    budget: Optional[float] = Field(None, ge=0, description="Budget in USD")
    deployment_timeline: Optional[str] = Field(None, description="Deployment timeline")
    
    # Growth and scalability
    expected_growth_rate: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Expected annual growth rate (e.g., 0.2 for 20%)"
    )
    scalability_horizon_years: Optional[int] = Field(None, ge=1, le=10)
    
    # Additional requirements
    special_requirements: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    critical_applications: List[str] = Field(default_factory=list)
    
    # Metadata
    submitted_by: Optional[str] = Field(None, description="User who submitted requirements")
    submitted_at: Optional[datetime] = Field(None)
    priority: str = Field(default="medium", description="Project priority")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "Corporate HQ Network Upgrade",
                "description": "Upgrade existing network to support 2000 users with high availability",
                "network_type": "enterprise_datacenter",
                "topology_preference": "spine_leaf",
                "scale": {
                    "devices": 500,
                    "users": 2000,
                    "sites": 3
                },
                "bandwidth": {
                    "min": "10Gbps",
                    "max": "100Gbps"
                },
                "redundancy": "high",
                "security_level": "enterprise",
                "compliance": ["PCI-DSS", "HIPAA"],
                "budget": 500000,
                "deployment_timeline": "6 months"
            }
        }


class RequirementAnalysisResult(BaseModel):
    """
    Result of requirement analysis by the Requirement Analysis Agent
    Structured and validated requirements ready for design generation
    """
    requirements_id: str
    original_requirements: NetworkRequirements
    
    # Extracted and structured information
    key_requirements: List[str] = Field(..., description="Key requirements identified")
    technical_constraints: List[str] = Field(default_factory=list)
    business_constraints: List[str] = Field(default_factory=list)
    
    # Completeness analysis
    completeness_score: float = Field(..., ge=0.0, le=1.0)
    missing_information: List[str] = Field(default_factory=list)
    ambiguous_requirements: List[str] = Field(default_factory=list)
    
    # Feasibility analysis
    is_feasible: bool = Field(..., description="Requirements are technically feasible")
    feasibility_concerns: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommended_topology: TopologyType
    recommended_network_type: NetworkType
    design_approach: str = Field(..., description="Recommended design approach")
    
    # RAG search parameters
    search_criteria: Dict[str, Any] = Field(
        default_factory=dict,
        description="Criteria for searching similar designs"
    )
    
    # Analysis metadata
    analyzed_by: str = Field(default="requirement_analysis_agent")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirements_id": "req_123",
                "key_requirements": [
                    "High availability (99.99%)",
                    "Support 2000 concurrent users",
                    "PCI-DSS compliance required"
                ],
                "completeness_score": 0.85,
                "is_feasible": True,
                "recommended_topology": "spine_leaf",
                "recommended_network_type": "enterprise_datacenter",
                "confidence_score": 0.92
            }
        }


class RequirementValidation(BaseModel):
    """Validation result for requirements"""
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
