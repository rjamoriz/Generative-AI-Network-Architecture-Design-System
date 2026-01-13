"""
Pydantic models for network designs
Structured data models for network architecture designs
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class NetworkType(str, Enum):
    """Types of network architectures"""
    ENTERPRISE_DATACENTER = "enterprise_datacenter"
    SDN_CAMPUS = "sdn_campus"
    LEGACY_CAMPUS = "legacy_campus"
    HYBRID = "hybrid"
    CLOUD_NATIVE = "cloud_native"
    WAN = "wan"
    DATA_CENTER_INTERCONNECT = "data_center_interconnect"


class TopologyType(str, Enum):
    """Network topology types"""
    SPINE_LEAF = "spine_leaf"
    THREE_TIER = "three_tier"
    COLLAPSED_CORE = "collapsed_core"
    MESH = "mesh"
    STAR = "star"
    RING = "ring"
    HYBRID_TOPOLOGY = "hybrid_topology"


class RedundancyLevel(str, Enum):
    """Redundancy levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLevel(str, Enum):
    """Security levels"""
    BASIC = "basic"
    CORPORATE = "corporate"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"


class DesignStatus(str, Enum):
    """Design lifecycle status"""
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATING = "validating"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class BandwidthRequirement(BaseModel):
    """Bandwidth requirements"""
    min: str = Field(..., description="Minimum bandwidth (e.g., '1Gbps', '10Gbps')")
    max: str = Field(..., description="Maximum bandwidth")
    average: Optional[str] = Field(None, description="Average expected bandwidth")
    
    @validator('min', 'max', 'average')
    def validate_bandwidth_format(cls, v):
        """Validate bandwidth format"""
        if v is None:
            return v
        valid_units = ['Mbps', 'Gbps', 'Tbps']
        if not any(v.endswith(unit) for unit in valid_units):
            raise ValueError(f"Bandwidth must end with one of {valid_units}")
        return v


class ScaleRequirement(BaseModel):
    """Scale requirements"""
    devices: int = Field(..., ge=1, description="Number of network devices")
    users: int = Field(..., ge=1, description="Number of users")
    sites: int = Field(default=1, ge=1, description="Number of sites/locations")
    vlans: Optional[int] = Field(None, ge=1, le=4094, description="Number of VLANs")
    subnets: Optional[int] = Field(None, ge=1, description="Number of subnets")


class ComponentSpecification(BaseModel):
    """Network component specification"""
    component_id: str = Field(..., description="Unique component identifier")
    component_type: str = Field(..., description="Type: switch, router, firewall, etc.")
    name: str = Field(..., description="Component name")
    model: Optional[str] = Field(None, description="Hardware model")
    vendor: Optional[str] = Field(None, description="Vendor name")
    quantity: int = Field(default=1, ge=1, description="Number of units")
    specifications: Dict[str, Any] = Field(default_factory=dict, description="Technical specs")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuration details")
    location: Optional[str] = Field(None, description="Physical location")
    redundancy_group: Optional[str] = Field(None, description="Redundancy group ID")


class Connection(BaseModel):
    """Network connection between components"""
    connection_id: str = Field(..., description="Unique connection identifier")
    source_component: str = Field(..., description="Source component ID")
    source_interface: str = Field(..., description="Source interface")
    target_component: str = Field(..., description="Target component ID")
    target_interface: str = Field(..., description="Target interface")
    connection_type: str = Field(..., description="Type: ethernet, fiber, wireless, etc.")
    bandwidth: str = Field(..., description="Connection bandwidth")
    protocol: Optional[str] = Field(None, description="Protocol used")
    vlan: Optional[int] = Field(None, description="VLAN ID if applicable")


class TopologyDetails(BaseModel):
    """Detailed topology information"""
    topology_type: TopologyType
    layers: int = Field(..., ge=1, le=7, description="Number of network layers")
    redundancy_level: RedundancyLevel
    has_single_point_of_failure: bool = Field(..., description="SPOF detected")
    redundant_paths: int = Field(default=0, ge=0, description="Number of redundant paths")
    description: Optional[str] = Field(None, description="Topology description")


class NetworkDesign(BaseModel):
    """Complete network design model"""
    design_id: Optional[str] = Field(None, description="Unique design identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Design name")
    description: Optional[str] = Field(None, description="Design description")
    
    # Design metadata
    network_type: NetworkType
    status: DesignStatus = Field(default=DesignStatus.DRAFT)
    version: str = Field(default="1.0", description="Design version")
    
    # Requirements reference
    requirements_id: Optional[str] = Field(None, description="Associated requirements ID")
    
    # Topology
    topology: TopologyDetails
    
    # Components and connections
    components: List[ComponentSpecification] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)
    
    # Technical details
    bandwidth_requirement: BandwidthRequirement
    scale: ScaleRequirement
    security_level: SecurityLevel
    compliance_requirements: List[str] = Field(default_factory=list)
    
    # Design rationale and explanation
    design_rationale: Optional[str] = Field(None, description="Why this design was chosen")
    key_features: List[str] = Field(default_factory=list)
    trade_offs: Optional[str] = Field(None, description="Design trade-offs")
    
    # Validation
    validation_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_id: Optional[str] = Field(None, description="Associated validation ID")
    
    # RAG context
    similar_designs: List[str] = Field(default_factory=list, description="IDs of similar designs used")
    rag_sources: List[str] = Field(default_factory=list, description="RAG sources consulted")
    
    # Metadata
    created_by: Optional[str] = Field(None, description="User who created the design")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    approved_by: Optional[str] = Field(None, description="User who approved")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    
    # Cost estimation
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost in USD")
    deployment_timeline: Optional[str] = Field(None, description="Estimated deployment time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Enterprise Data Center Network",
                "network_type": "enterprise_datacenter",
                "topology": {
                    "topology_type": "spine_leaf",
                    "layers": 3,
                    "redundancy_level": "high",
                    "has_single_point_of_failure": False,
                    "redundant_paths": 4
                },
                "bandwidth_requirement": {
                    "min": "10Gbps",
                    "max": "100Gbps"
                },
                "scale": {
                    "devices": 500,
                    "users": 2000,
                    "sites": 3
                },
                "security_level": "enterprise",
                "compliance_requirements": ["PCI-DSS", "HIPAA"]
            }
        }


class DesignSummary(BaseModel):
    """Lightweight design summary for listings"""
    design_id: str
    name: str
    network_type: NetworkType
    topology_type: TopologyType
    status: DesignStatus
    validation_score: Optional[float]
    created_at: Optional[datetime]
    component_count: int = Field(default=0, description="Number of components")
    
    class Config:
        json_schema_extra = {
            "example": {
                "design_id": "design_123",
                "name": "Enterprise Data Center",
                "network_type": "enterprise_datacenter",
                "topology_type": "spine_leaf",
                "status": "validated",
                "validation_score": 0.92,
                "component_count": 45
            }
        }


class DesignEmbedding(BaseModel):
    """Design with embedding for vector search"""
    design_id: str
    design_summary: str = Field(..., description="Text summary for embedding")
    embedding: List[float] = Field(..., description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('embedding')
    def validate_embedding_dimension(cls, v):
        """Validate embedding dimension (1536 for OpenAI)"""
        if len(v) not in [1536, 768, 384]:  # Common embedding dimensions
            raise ValueError(f"Embedding dimension {len(v)} not supported")
        return v
