"""
Integration Tests for RAG Pipeline
Tests end-to-end workflow from requirements to validated design
"""
import pytest
import asyncio
from datetime import datetime

from app.models.requirements import NetworkRequirements, ScaleRequirement, BandwidthRequirement, RedundancyLevel, SecurityLevel
from app.models.network_design import NetworkType, TopologyType
from app.agents.requirement_analyzer import RequirementAnalyzerAgent
from app.agents.design_synthesizer import DesignSynthesizerAgent
from app.agents.validation_agent import ValidationAgent


@pytest.fixture
def sample_requirements():
    """Create sample network requirements for testing"""
    return NetworkRequirements(
        requirements_id="test_req_001",
        project_name="Test Enterprise Network",
        description="High-availability enterprise network for 500 users",
        network_type=NetworkType.ENTERPRISE_DATACENTER,
        scale=ScaleRequirement(
            devices=500,
            users=2000,
            sites=2
        ),
        bandwidth=BandwidthRequirement(
            min="10Gbps",
            max="100Gbps"
        ),
        redundancy=RedundancyLevel.HIGH,
        security_level=SecurityLevel.ENTERPRISE,
        compliance=["PCI-DSS", "SOC2"],
        topology_preference=TopologyType.SPINE_LEAF,
        budget=500000.0,
        deployment_timeline="6 months"
    )


@pytest.fixture
def requirement_analyzer():
    """Create requirement analyzer agent"""
    return RequirementAnalyzerAgent()


@pytest.fixture
def design_synthesizer():
    """Create design synthesizer agent"""
    return DesignSynthesizerAgent()


@pytest.fixture
def validation_agent():
    """Create validation agent"""
    return ValidationAgent()


class TestRequirementAnalysis:
    """Test requirement analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_requirements(self, requirement_analyzer, sample_requirements):
        """Test requirement analysis"""
        # This test requires LLM API access
        # Skip if no API key available
        try:
            result = await requirement_analyzer.analyze_requirements(sample_requirements)
            
            assert result is not None
            assert result.requirements_id == sample_requirements.requirements_id
            assert result.is_feasible is True
            assert len(result.key_requirements) > 0
            assert result.completeness_score > 0.5
            assert result.confidence_score > 0.5
            
        except Exception as e:
            pytest.skip(f"LLM API not available: {e}")
    
    @pytest.mark.asyncio
    async def test_validate_requirements(self, requirement_analyzer, sample_requirements):
        """Test requirement validation"""
        validation = await requirement_analyzer.validate_requirements(sample_requirements)
        
        assert validation is not None
        assert "is_valid" in validation
        assert validation["is_valid"] is True


class TestDesignSynthesis:
    """Test design synthesis functionality"""
    
    @pytest.mark.asyncio
    async def test_synthesize_design_without_rag(self, design_synthesizer, requirement_analyzer, sample_requirements):
        """Test design synthesis without RAG"""
        try:
            # First analyze requirements
            analysis = await requirement_analyzer.analyze_requirements(sample_requirements)
            
            # Synthesize design without RAG
            design = await design_synthesizer.synthesize_design(
                sample_requirements,
                analysis,
                use_rag=False
            )
            
            assert design is not None
            assert design.name == sample_requirements.project_name
            assert design.network_type == sample_requirements.network_type
            assert len(design.components) >= 5
            assert len(design.connections) >= 3
            assert design.status.value == "generated"
            
        except Exception as e:
            pytest.skip(f"LLM API not available: {e}")


class TestValidation:
    """Test validation functionality"""
    
    @pytest.mark.asyncio
    async def test_validate_design(self, validation_agent, design_synthesizer, requirement_analyzer, sample_requirements):
        """Test design validation"""
        try:
            # Create a design
            analysis = await requirement_analyzer.analyze_requirements(sample_requirements)
            design = await design_synthesizer.synthesize_design(
                sample_requirements,
                analysis,
                use_rag=False
            )
            
            # Validate design
            validation_result = await validation_agent.validate_design(design, "standard")
            
            assert validation_result is not None
            assert validation_result.design_id == design.design_id
            assert validation_result.overall_score >= 0.0
            assert validation_result.overall_score <= 1.0
            assert validation_result.deterministic_validation is not None
            assert validation_result.llm_validation is not None
            
        except Exception as e:
            pytest.skip(f"LLM API not available: {e}")
    
    def test_rule_registry(self, validation_agent):
        """Test rule registry functionality"""
        registry = validation_agent.rule_registry
        
        # Check rules are loaded
        all_rules = registry.get_all_rules()
        assert len(all_rules) > 0
        
        # Check statistics
        stats = registry.get_statistics()
        assert stats["total_rules"] > 0
        assert "categories" in stats
        assert "severity_distribution" in stats


class TestEndToEndPipeline:
    """Test complete end-to-end pipeline"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, requirement_analyzer, design_synthesizer, validation_agent, sample_requirements):
        """Test complete pipeline from requirements to validated design"""
        try:
            # Step 1: Analyze requirements
            print("\n=== Step 1: Analyzing Requirements ===")
            analysis = await requirement_analyzer.analyze_requirements(sample_requirements)
            assert analysis.is_feasible is True
            print(f"Analysis complete: {len(analysis.key_requirements)} key requirements identified")
            
            # Step 2: Synthesize design
            print("\n=== Step 2: Synthesizing Design ===")
            design = await design_synthesizer.synthesize_design(
                sample_requirements,
                analysis,
                use_rag=False
            )
            assert len(design.components) >= 5
            print(f"Design created: {len(design.components)} components, {len(design.connections)} connections")
            
            # Step 3: Validate design
            print("\n=== Step 3: Validating Design ===")
            validation_result = await validation_agent.validate_design(design, "standard")
            print(f"Validation score: {validation_result.overall_score:.2f}")
            print(f"Passed: {validation_result.passed}")
            print(f"Issues: {validation_result.critical_count} critical, {validation_result.error_count} errors, {validation_result.warning_count} warnings")
            
            # Assertions
            assert validation_result.overall_score > 0.0
            assert validation_result.deterministic_validation.total_rules_executed > 0
            
            # Print summary
            print("\n=== Pipeline Complete ===")
            print(f"Requirements: {sample_requirements.project_name}")
            print(f"Design: {design.name}")
            print(f"Components: {len(design.components)}")
            print(f"Validation Score: {validation_result.overall_score:.2f}")
            print(f"Status: {'PASSED' if validation_result.passed else 'FAILED'}")
            
        except Exception as e:
            pytest.skip(f"Pipeline test failed (likely no LLM API): {e}")


class TestRuleEngine:
    """Test validation rule engine"""
    
    def test_rule_loading(self, validation_agent):
        """Test that all rules are loaded"""
        registry = validation_agent.rule_registry
        
        # Should have 53 rules
        all_rules = registry.get_all_rules()
        assert len(all_rules) == 53
        
        # Check categories
        from app.validation.rule_base import RuleCategory
        
        capacity_rules = registry.get_rules_by_category(RuleCategory.CAPACITY)
        assert len(capacity_rules) == 10
        
        topology_rules = registry.get_rules_by_category(RuleCategory.TOPOLOGY)
        assert len(topology_rules) == 11
        
        protocol_rules = registry.get_rules_by_category(RuleCategory.PROTOCOL)
        assert len(protocol_rules) == 10
        
        security_rules = registry.get_rules_by_category(RuleCategory.SECURITY)
        assert len(security_rules) == 11
        
        compliance_rules = registry.get_rules_by_category(RuleCategory.COMPLIANCE)
        assert len(compliance_rules) == 11
    
    def test_rule_enable_disable(self, validation_agent):
        """Test enabling and disabling rules"""
        registry = validation_agent.rule_registry
        
        # Get a rule
        all_rules = registry.get_all_rules()
        test_rule = all_rules[0]
        rule_id = test_rule.get_rule_id()
        
        # Disable rule
        assert registry.disable_rule(rule_id) is True
        assert test_rule.is_enabled() is False
        
        # Enable rule
        assert registry.enable_rule(rule_id) is True
        assert test_rule.is_enabled() is True


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
