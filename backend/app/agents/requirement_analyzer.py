"""
Requirement Analysis Agent
Analyzes and structures network requirements using LLM
"""
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

from app.services.llm_service import LLMService, LLMProvider
from app.models.requirements import NetworkRequirements, RequirementAnalysisResult
from app.models.network_design import NetworkType, TopologyType

logger = logging.getLogger(__name__)


class RequirementAnalyzerAgent:
    """
    Agent for analyzing network requirements
    Extracts key information, identifies constraints, and assesses feasibility
    """
    
    def __init__(self):
        """Initialize requirement analyzer agent"""
        self.llm_service = LLMService()
        self.agent_name = "requirement_analysis_agent"
        
        logger.info("Requirement Analyzer Agent initialized")
    
    def _build_analysis_prompt(self, requirements: NetworkRequirements) -> str:
        """
        Build prompt for requirement analysis
        
        Args:
            requirements: Network requirements to analyze
        
        Returns:
            Analysis prompt
        """
        prompt = f"""You are an expert network architect analyzing requirements for a network design project.

Project: {requirements.project_name}
Description: {requirements.description}

Requirements:
- Network Type: {requirements.network_type.value}
- Scale: {requirements.scale.devices} devices, {requirements.scale.users} users, {requirements.scale.sites} sites
- Bandwidth: {requirements.bandwidth.min} to {requirements.bandwidth.max}
- Redundancy: {requirements.redundancy.value}
- Security Level: {requirements.security_level.value}
- Compliance: {', '.join(requirements.compliance) if requirements.compliance else 'None specified'}
- Topology Preference: {requirements.topology_preference.value if requirements.topology_preference else 'Not specified'}
- Budget: ${requirements.budget:,.2f} if requirements.budget else 'Not specified'
- Timeline: {requirements.deployment_timeline or 'Not specified'}

Additional Requirements:
- SDN Required: {requirements.sdn_required}
- Cloud Integration: {requirements.cloud_integration}
- Wireless: {requirements.requires_wireless}
- VoIP: {requirements.requires_voip}
- Video Conferencing: {requirements.requires_video_conferencing}

Analyze these requirements and provide:

1. **Key Requirements** (3-5 most critical requirements)
2. **Technical Constraints** (technical limitations or requirements)
3. **Business Constraints** (budget, timeline, vendor preferences)
4. **Completeness Score** (0.0-1.0, how complete are the requirements)
5. **Missing Information** (what critical information is missing)
6. **Ambiguous Requirements** (what needs clarification)
7. **Feasibility Assessment** (is this technically feasible? any concerns?)
8. **Recommended Topology** (best topology for these requirements)
9. **Recommended Network Type** (confirm or suggest alternative network type)
10. **Design Approach** (high-level approach to meet requirements)
11. **Search Criteria** (what to look for in similar designs)

Provide your analysis in a structured, professional manner."""

        return prompt
    
    def _build_structured_output_schema(self) -> Dict[str, Any]:
        """
        Build JSON schema for structured output
        
        Returns:
            JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "key_requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-5 most critical requirements"
                },
                "technical_constraints": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "business_constraints": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "completeness_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "missing_information": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "ambiguous_requirements": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "is_feasible": {
                    "type": "boolean"
                },
                "feasibility_concerns": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "recommended_topology": {
                    "type": "string",
                    "enum": ["spine_leaf", "three_tier", "collapsed_core", "mesh", "star", "ring", "hybrid_topology"]
                },
                "recommended_network_type": {
                    "type": "string",
                    "enum": ["enterprise_datacenter", "sdn_campus", "legacy_campus", "hybrid", "cloud_native", "wan", "data_center_interconnect"]
                },
                "design_approach": {
                    "type": "string"
                },
                "confidence_score": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": [
                "key_requirements",
                "completeness_score",
                "is_feasible",
                "recommended_topology",
                "recommended_network_type",
                "design_approach",
                "confidence_score"
            ]
        }
    
    async def analyze_requirements(self, requirements: NetworkRequirements) -> RequirementAnalysisResult:
        """
        Analyze network requirements using LLM
        
        Args:
            requirements: Network requirements to analyze
        
        Returns:
            Structured analysis result
        """
        try:
            logger.info(f"Analyzing requirements for project: {requirements.project_name}")
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(requirements)
            
            # Get structured output from LLM (prefer Claude for analysis)
            schema = self._build_structured_output_schema()
            analysis_data = await self.llm_service.generate_structured(
                prompt=prompt,
                schema=schema,
                provider=LLMProvider.ANTHROPIC,
                use_fallback=True
            )
            
            # Build search criteria for RAG
            search_criteria = {
                "network_type": analysis_data.get("recommended_network_type"),
                "topology": analysis_data.get("recommended_topology"),
                "min_scale_devices": requirements.scale.devices,
                "min_scale_users": requirements.scale.users,
                "security_level": requirements.security_level.value,
                "compliance": requirements.compliance
            }
            
            # Create analysis result
            result = RequirementAnalysisResult(
                requirements_id=requirements.requirements_id or f"req_{datetime.utcnow().timestamp()}",
                original_requirements=requirements,
                key_requirements=analysis_data.get("key_requirements", []),
                technical_constraints=analysis_data.get("technical_constraints", []),
                business_constraints=analysis_data.get("business_constraints", []),
                completeness_score=analysis_data.get("completeness_score", 0.0),
                missing_information=analysis_data.get("missing_information", []),
                ambiguous_requirements=analysis_data.get("ambiguous_requirements", []),
                is_feasible=analysis_data.get("is_feasible", True),
                feasibility_concerns=analysis_data.get("feasibility_concerns", []),
                recommended_topology=TopologyType(analysis_data.get("recommended_topology")),
                recommended_network_type=NetworkType(analysis_data.get("recommended_network_type")),
                design_approach=analysis_data.get("design_approach", ""),
                search_criteria=search_criteria,
                analyzed_by=self.agent_name,
                analyzed_at=datetime.utcnow(),
                confidence_score=analysis_data.get("confidence_score", 0.0)
            )
            
            logger.info(f"Requirements analysis complete (confidence: {result.confidence_score:.2f}, feasible: {result.is_feasible})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze requirements: {e}")
            raise
    
    async def validate_requirements(self, requirements: NetworkRequirements) -> Dict[str, Any]:
        """
        Validate requirements for completeness and consistency
        
        Args:
            requirements: Network requirements
        
        Returns:
            Validation result
        """
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check for missing critical information
        if not requirements.scale.devices or requirements.scale.devices < 1:
            validation["errors"].append("Number of devices must be specified and > 0")
            validation["is_valid"] = False
        
        if not requirements.scale.users or requirements.scale.users < 1:
            validation["errors"].append("Number of users must be specified and > 0")
            validation["is_valid"] = False
        
        # Check bandwidth requirements
        if not requirements.bandwidth.min or not requirements.bandwidth.max:
            validation["warnings"].append("Bandwidth requirements not fully specified")
        
        # Check budget vs scale
        if requirements.budget:
            estimated_cost_per_user = requirements.budget / requirements.scale.users
            if estimated_cost_per_user < 100:
                validation["warnings"].append(f"Budget may be insufficient (${estimated_cost_per_user:.2f} per user)")
        
        # Check compliance requirements
        if requirements.security_level.value in ["enterprise", "government", "critical_infrastructure"]:
            if not requirements.compliance:
                validation["suggestions"].append("Consider specifying compliance requirements for high security level")
        
        # Check redundancy vs availability
        if requirements.availability_requirement and requirements.availability_requirement > 0.999:
            if requirements.redundancy.value in ["none", "low"]:
                validation["warnings"].append("High availability requirement needs higher redundancy level")
        
        logger.info(f"Requirements validation: {validation['is_valid']} ({len(validation['errors'])} errors, {len(validation['warnings'])} warnings)")
        return validation
    
    async def extract_use_cases(self, requirements: NetworkRequirements) -> List[str]:
        """
        Extract and identify use cases from requirements
        
        Args:
            requirements: Network requirements
        
        Returns:
            List of identified use cases
        """
        use_cases = []
        
        # Explicit use cases
        if requirements.use_cases:
            use_cases.extend(requirements.use_cases)
        
        # Inferred use cases
        if requirements.requires_voip:
            use_cases.append("Voice over IP (VoIP) communications")
        
        if requirements.requires_video_conferencing:
            use_cases.append("Video conferencing and collaboration")
        
        if requirements.requires_wireless:
            use_cases.append("Wireless connectivity for mobile devices")
        
        if requirements.cloud_integration:
            use_cases.append("Cloud service integration and hybrid connectivity")
        
        if requirements.sdn_required:
            use_cases.append("Software-defined networking for programmability")
        
        # Infer from network type
        if requirements.network_type == NetworkType.ENTERPRISE_DATACENTER:
            use_cases.append("Enterprise data center operations")
        elif requirements.network_type == NetworkType.SDN_CAMPUS:
            use_cases.append("Campus network with SDN capabilities")
        
        logger.info(f"Identified {len(use_cases)} use cases")
        return list(set(use_cases))  # Remove duplicates


# Dependency injection for FastAPI
def get_requirement_analyzer() -> RequirementAnalyzerAgent:
    """Get requirement analyzer agent for dependency injection"""
    return RequirementAnalyzerAgent()
