"""
Design Synthesis Agent
Generates network architecture designs using LLM with RAG context
"""
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
import uuid

from app.services.llm_service import LLMService, LLMProvider
from app.services.rag_service import RAGService
from app.models.requirements import NetworkRequirements, RequirementAnalysisResult
from app.models.network_design import (
    NetworkDesign, NetworkType, TopologyType, DesignStatus,
    ComponentSpecification, Connection, TopologyDetails,
    BandwidthRequirement, ScaleRequirement, RedundancyLevel, SecurityLevel
)

logger = logging.getLogger(__name__)


class DesignSynthesizerAgent:
    """
    Agent for synthesizing network designs
    Uses LLM with RAG context to generate technically valid designs
    """
    
    def __init__(self):
        """Initialize design synthesizer agent"""
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.agent_name = "design_synthesis_agent"
        
        logger.info("Design Synthesizer Agent initialized")
    
    def _build_synthesis_prompt(self,
                                requirements: NetworkRequirements,
                                analysis: RequirementAnalysisResult,
                                rag_context: Dict[str, Any]) -> str:
        """
        Build prompt for design synthesis with RAG context
        
        Args:
            requirements: Original requirements
            analysis: Analyzed requirements
            rag_context: RAG context with similar designs
        
        Returns:
            Synthesis prompt
        """
        # Build similar designs context
        similar_designs_text = ""
        if rag_context.get("similar_designs"):
            similar_designs_text = "\n\nSimilar Validated Designs (for reference):\n"
            for i, design in enumerate(rag_context["similar_designs"][:3], 1):
                similar_designs_text += f"\n{i}. Design ID: {design['design_id']}\n"
                similar_designs_text += f"   Similarity: {design['similarity_score']:.2f}\n"
                similar_designs_text += f"   Metadata: {json.dumps(design['metadata'], indent=2)}\n"
        
        # Add historical context if available
        historical_text = ""
        if rag_context.get("historical_context"):
            historical_text = f"\n\n{rag_context['historical_context']}\n"
        
        prompt = f"""You are an expert network architect tasked with designing a network architecture.

PROJECT REQUIREMENTS:
Project: {requirements.project_name}
Description: {requirements.description}

TECHNICAL SPECIFICATIONS:
- Network Type: {requirements.network_type.value}
- Recommended Topology: {analysis.recommended_topology.value}
- Scale: {requirements.scale.devices} devices, {requirements.scale.users} users, {requirements.scale.sites} sites
- Bandwidth: {requirements.bandwidth.min} to {requirements.bandwidth.max}
- Redundancy Level: {requirements.redundancy.value}
- Security Level: {requirements.security_level.value}
- Compliance: {', '.join(requirements.compliance) if requirements.compliance else 'None'}

KEY REQUIREMENTS (from analysis):
{chr(10).join(f'- {req}' for req in analysis.key_requirements)}

CONSTRAINTS:
Technical: {', '.join(analysis.technical_constraints) if analysis.technical_constraints else 'None'}
Business: {', '.join(analysis.business_constraints) if analysis.business_constraints else 'None'}

DESIGN APPROACH (recommended):
{analysis.design_approach}
{similar_designs_text}
{historical_text}

TASK:
Design a complete network architecture that meets all requirements. Your design must include:

1. **Network Topology Details**:
   - Topology type and structure
   - Number of layers
   - Redundancy configuration
   - Identify any single points of failure

2. **Network Components** (minimum 5 components):
   For each component specify:
   - Component type (switch, router, firewall, load_balancer, etc.)
   - Name and quantity
   - Model/specifications
   - Location/layer
   - Redundancy group (if applicable)

3. **Network Connections** (minimum 3 connections):
   For each connection specify:
   - Source and target components
   - Interfaces used
   - Connection type (ethernet, fiber, etc.)
   - Bandwidth
   - VLAN (if applicable)

4. **Design Rationale**:
   - Why this design meets the requirements
   - Key features and benefits
   - Trade-offs made

Provide a comprehensive, technically sound design that can be validated and implemented."""

        return prompt
    
    def _build_structured_output_schema(self) -> Dict[str, Any]:
        """
        Build JSON schema for structured design output
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "design_name": {"type": "string"},
                "design_description": {"type": "string"},
                "topology": {
                    "type": "object",
                    "properties": {
                        "topology_type": {
                            "type": "string",
                            "enum": ["spine_leaf", "three_tier", "collapsed_core", "mesh", "star", "ring", "hybrid_topology"]
                        },
                        "layers": {"type": "integer", "minimum": 1, "maximum": 7},
                        "redundancy_level": {
                            "type": "string",
                            "enum": ["none", "low", "medium", "high", "critical"]
                        },
                        "has_single_point_of_failure": {"type": "boolean"},
                        "redundant_paths": {"type": "integer", "minimum": 0},
                        "description": {"type": "string"}
                    },
                    "required": ["topology_type", "layers", "redundancy_level", "has_single_point_of_failure"]
                },
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component_type": {"type": "string"},
                            "name": {"type": "string"},
                            "model": {"type": "string"},
                            "vendor": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1},
                            "specifications": {"type": "object"},
                            "location": {"type": "string"},
                            "redundancy_group": {"type": "string"}
                        },
                        "required": ["component_type", "name", "quantity"]
                    },
                    "minItems": 5
                },
                "connections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_component": {"type": "string"},
                            "source_interface": {"type": "string"},
                            "target_component": {"type": "string"},
                            "target_interface": {"type": "string"},
                            "connection_type": {"type": "string"},
                            "bandwidth": {"type": "string"},
                            "protocol": {"type": "string"},
                            "vlan": {"type": "integer"}
                        },
                        "required": ["source_component", "target_component", "connection_type", "bandwidth"]
                    },
                    "minItems": 3
                },
                "design_rationale": {"type": "string"},
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "trade_offs": {"type": "string"}
            },
            "required": ["design_name", "topology", "components", "connections", "design_rationale"]
        }
    
    async def synthesize_design(self,
                               requirements: NetworkRequirements,
                               analysis: RequirementAnalysisResult,
                               use_rag: bool = True,
                               use_historical: bool = True,
                               historical_context: str = None) -> NetworkDesign:
        """
        Synthesize network design using LLM, RAG, and historical data
        
        Args:
            requirements: Network requirements
            analysis: Requirement analysis result
            use_rag: Whether to use RAG context
            use_historical: Whether to use historical design data
            historical_context: Pre-built historical context string
        
        Returns:
            Generated network design
        """
        try:
            logger.info(f"Synthesizing design for: {requirements.project_name}")
            
            # Build RAG context if enabled
            rag_context = {}
            if use_rag:
                rag_context = await self.rag_service.build_rag_context(requirements)
                logger.info(f"RAG context built with {rag_context['design_count']} similar designs")
            
            # Add historical context if provided
            if use_historical and historical_context:
                rag_context['historical_context'] = historical_context
                logger.info("Historical design context added to synthesis")
            
            # Build synthesis prompt
            prompt = self._build_synthesis_prompt(requirements, analysis, rag_context)
            
            # Generate design using LLM (prefer GPT-4 for synthesis)
            schema = self._build_structured_output_schema()
            design_data = await self.llm_service.generate_structured(
                prompt=prompt,
                schema=schema,
                provider=LLMProvider.OPENAI,
                use_fallback=True
            )
            
            # Convert to NetworkDesign model
            design = self._convert_to_network_design(
                design_data,
                requirements,
                analysis,
                rag_context
            )
            
            logger.info(f"Design synthesized: {design.name} ({len(design.components)} components, {len(design.connections)} connections)")
            return design
            
        except Exception as e:
            logger.error(f"Failed to synthesize design: {e}")
            raise
    
    def _convert_to_network_design(self,
                                   design_data: Dict[str, Any],
                                   requirements: NetworkRequirements,
                                   analysis: RequirementAnalysisResult,
                                   rag_context: Dict[str, Any]) -> NetworkDesign:
        """
        Convert LLM output to NetworkDesign model
        
        Args:
            design_data: Raw design data from LLM
            requirements: Original requirements
            analysis: Requirement analysis
            rag_context: RAG context used
        
        Returns:
            NetworkDesign instance
        """
        # Generate unique design ID
        design_id = f"design_{uuid.uuid4().hex[:12]}"
        
        # Parse topology
        topology_data = design_data.get("topology", {})
        topology = TopologyDetails(
            topology_type=TopologyType(topology_data.get("topology_type")),
            layers=topology_data.get("layers", 3),
            redundancy_level=RedundancyLevel(topology_data.get("redundancy_level", "medium")),
            has_single_point_of_failure=topology_data.get("has_single_point_of_failure", False),
            redundant_paths=topology_data.get("redundant_paths", 0),
            description=topology_data.get("description")
        )
        
        # Parse components
        components = []
        for i, comp_data in enumerate(design_data.get("components", [])):
            component = ComponentSpecification(
                component_id=f"comp_{i+1:03d}",
                component_type=comp_data.get("component_type", "unknown"),
                name=comp_data.get("name", f"Component {i+1}"),
                model=comp_data.get("model"),
                vendor=comp_data.get("vendor"),
                quantity=comp_data.get("quantity", 1),
                specifications=comp_data.get("specifications", {}),
                location=comp_data.get("location"),
                redundancy_group=comp_data.get("redundancy_group")
            )
            components.append(component)
        
        # Parse connections
        connections = []
        for i, conn_data in enumerate(design_data.get("connections", [])):
            connection = Connection(
                connection_id=f"conn_{i+1:03d}",
                source_component=conn_data.get("source_component", ""),
                source_interface=conn_data.get("source_interface", "eth0"),
                target_component=conn_data.get("target_component", ""),
                target_interface=conn_data.get("target_interface", "eth0"),
                connection_type=conn_data.get("connection_type", "ethernet"),
                bandwidth=conn_data.get("bandwidth", "1Gbps"),
                protocol=conn_data.get("protocol"),
                vlan=conn_data.get("vlan")
            )
            connections.append(connection)
        
        # Extract similar design IDs from RAG context
        similar_design_ids = [
            d["design_id"] for d in rag_context.get("similar_designs", [])
        ]
        
        # Create NetworkDesign
        design = NetworkDesign(
            design_id=design_id,
            name=design_data.get("design_name", requirements.project_name),
            description=design_data.get("design_description", requirements.description),
            network_type=requirements.network_type,
            status=DesignStatus.GENERATED,
            topology=topology,
            components=components,
            connections=connections,
            bandwidth_requirement=requirements.bandwidth,
            scale=requirements.scale,
            security_level=requirements.security_level,
            compliance_requirements=requirements.compliance,
            design_rationale=design_data.get("design_rationale", ""),
            key_features=design_data.get("key_features", []),
            trade_offs=design_data.get("trade_offs"),
            requirements_id=requirements.requirements_id,
            similar_designs=similar_design_ids,
            rag_sources=[f"rag_context_{len(similar_design_ids)}_designs"],
            created_at=datetime.utcnow()
        )
        
        return design
    
    async def refine_design(self,
                          design: NetworkDesign,
                          feedback: str,
                          requirements: NetworkRequirements) -> NetworkDesign:
        """
        Refine existing design based on feedback
        
        Args:
            design: Current design
            feedback: Feedback for refinement
            requirements: Original requirements
        
        Returns:
            Refined network design
        """
        try:
            logger.info(f"Refining design: {design.name}")
            
            prompt = f"""You are refining a network architecture design based on feedback.

CURRENT DESIGN:
Name: {design.name}
Topology: {design.topology.topology_type.value}
Components: {len(design.components)}
Connections: {len(design.connections)}

FEEDBACK FOR IMPROVEMENT:
{feedback}

REQUIREMENTS:
- Network Type: {requirements.network_type.value}
- Scale: {requirements.scale.devices} devices, {requirements.scale.users} users
- Security Level: {requirements.security_level.value}

TASK:
Refine the design to address the feedback while maintaining all requirements.
Provide the complete refined design with the same structure as before."""

            # Generate refined design
            schema = self._build_structured_output_schema()
            refined_data = await self.llm_service.generate_structured(
                prompt=prompt,
                schema=schema,
                provider=LLMProvider.OPENAI,
                use_fallback=True
            )
            
            # Create refined design (reuse conversion logic)
            refined_design = self._convert_to_network_design(
                refined_data,
                requirements,
                RequirementAnalysisResult(
                    requirements_id=requirements.requirements_id or "unknown",
                    original_requirements=requirements,
                    key_requirements=[],
                    completeness_score=1.0,
                    is_feasible=True,
                    recommended_topology=design.topology.topology_type,
                    recommended_network_type=design.network_type,
                    design_approach="Refinement based on feedback",
                    confidence_score=0.9
                ),
                {}
            )
            
            # Update metadata
            refined_design.design_id = design.design_id  # Keep same ID
            refined_design.version = f"{float(design.version) + 0.1:.1f}"
            refined_design.status = DesignStatus.GENERATED
            
            logger.info(f"Design refined: {refined_design.name} (v{refined_design.version})")
            return refined_design
            
        except Exception as e:
            logger.error(f"Failed to refine design: {e}")
            raise


# Dependency injection for FastAPI
def get_design_synthesizer() -> DesignSynthesizerAgent:
    """Get design synthesizer agent for dependency injection"""
    return DesignSynthesizerAgent()
