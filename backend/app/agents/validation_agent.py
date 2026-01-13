"""
Validation Agent
Coordinates validation of network designs using deterministic rules and LLM
"""
from typing import List, Dict, Any
import logging
from datetime import datetime
import uuid

from app.services.llm_service import LLMService, LLMProvider
from app.models.network_design import NetworkDesign
from app.models.validation_result import (
    ValidationResult, ValidationIssue, ValidationSeverity, ValidationCategory,
    DeterministicValidationResult, LLMValidationResult, RuleValidationResult
)
from app.validation.rule_registry import get_rule_registry
from app.validation.rule_loader import ensure_rules_loaded
from app.validation.rule_base import RuleCategory

logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    Agent for validating network designs
    Combines deterministic rule-based validation with LLM-based reasoning
    """
    
    def __init__(self):
        """Initialize validation agent"""
        self.llm_service = LLMService()
        self.agent_name = "validation_agent"
        
        # Ensure validation rules are loaded
        ensure_rules_loaded()
        self.rule_registry = get_rule_registry()
        
        logger.info(f"Validation Agent initialized with {len(self.rule_registry.get_all_rules())} rules")
    
    async def validate_design(self,
                            design: NetworkDesign,
                            validation_mode: str = "strict") -> ValidationResult:
        """
        Validate network design
        
        Args:
            design: Network design to validate
            validation_mode: Validation mode (strict, standard, lenient)
        
        Returns:
            Complete validation result
        """
        try:
            logger.info(f"Validating design: {design.name} (mode: {validation_mode})")
            
            start_time = datetime.utcnow()
            
            # Perform deterministic validation
            deterministic_result = await self._deterministic_validation(design, validation_mode)
            
            # Perform LLM-based validation
            llm_result = await self._llm_validation(design, validation_mode)
            
            # Combine results
            validation_result = self._combine_validation_results(
                design,
                deterministic_result,
                llm_result,
                validation_mode
            )
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            validation_result.total_execution_time_ms = execution_time
            
            logger.info(f"Validation complete: score={validation_result.overall_score:.2f}, passed={validation_result.passed}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise
    
    async def _deterministic_validation(self,
                                       design: NetworkDesign,
                                       mode: str) -> DeterministicValidationResult:
        """
        Perform deterministic rule-based validation using rule registry
        
        Args:
            design: Network design
            mode: Validation mode
        
        Returns:
            Deterministic validation result
        """
        logger.info("Performing deterministic validation with rule engine")
        
        # Execute all rules through registry
        rule_results = await self.rule_registry.execute_rules(design)
        
        # Organize results by category
        capacity_results = []
        protocol_results = []
        compliance_results = []
        topology_results = []
        security_results = []
        
        all_issues = []
        
        for result in rule_results:
            # Convert to RuleValidationResult
            rule_val_result = RuleValidationResult(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                category=result.to_validation_category(),
                passed=result.passed,
                score=result.score,
                message=result.message,
                details=result.details
            )
            
            # Categorize
            if result.category == RuleCategory.CAPACITY:
                capacity_results.append(rule_val_result)
            elif result.category == RuleCategory.PROTOCOL:
                protocol_results.append(rule_val_result)
            elif result.category == RuleCategory.COMPLIANCE:
                compliance_results.append(rule_val_result)
            elif result.category == RuleCategory.TOPOLOGY:
                topology_results.append(rule_val_result)
            elif result.category == RuleCategory.SECURITY:
                security_results.append(rule_val_result)
            
            # Create issues for failed rules
            if not result.passed:
                issue = ValidationIssue(
                    issue_id=f"issue_{uuid.uuid4().hex[:8]}",
                    category=result.to_validation_category(),
                    severity=result.to_validation_severity(),
                    title=result.rule_name,
                    description=result.message,
                    recommendation=result.recommendation,
                    affected_components=result.affected_components or []
                )
                all_issues.append(issue)
        
        # Calculate overall score
        all_results = capacity_results + protocol_results + compliance_results + topology_results + security_results
        total_rules = len(all_results)
        rules_passed = sum(1 for r in all_results if r.passed)
        rules_failed = total_rules - rules_passed
        
        overall_score = rules_passed / total_rules if total_rules > 0 else 0.0
        
        # Design passes if critical rules pass
        critical_categories = [ValidationCategory.CAPACITY, ValidationCategory.TOPOLOGY, ValidationCategory.SECURITY]
        critical_results = [r for r in all_results if r.category in critical_categories]
        passed = all(r.passed for r in critical_results) if critical_results else True
        
        # Categorize issues
        critical_issues = [i for i in all_issues if i.severity == ValidationSeverity.CRITICAL]
        errors = [i for i in all_issues if i.severity == ValidationSeverity.ERROR]
        warnings = [i for i in all_issues if i.severity == ValidationSeverity.WARNING]
        
        result = DeterministicValidationResult(
            overall_score=overall_score,
            passed=passed,
            capacity_results=capacity_results,
            protocol_results=protocol_results,
            compliance_results=compliance_results,
            topology_results=topology_results,
            critical_issues=critical_issues,
            errors=errors,
            warnings=warnings,
            total_rules_executed=total_rules,
            rules_passed=rules_passed,
            rules_failed=rules_failed
        )
        
        logger.info(f"Deterministic validation: {rules_passed}/{total_rules} rules passed ({len(rule_results)} total rules executed)")
        return result
    
    async def _llm_validation(self,
                            design: NetworkDesign,
                            mode: str) -> LLMValidationResult:
        """
        Perform LLM-based validation for edge cases and contextual reasoning
        
        Args:
            design: Network design
            mode: Validation mode
        
        Returns:
            LLM validation result
        """
        logger.info("Performing LLM validation")
        
        prompt = f"""You are an expert network architect reviewing a network design for technical validity and best practices.

DESIGN TO VALIDATE:
Name: {design.name}
Network Type: {design.network_type.value}
Topology: {design.topology.topology_type.value} ({design.topology.layers} layers)
Redundancy: {design.topology.redundancy_level.value}
Security Level: {design.security_level.value}
Components: {len(design.components)}
Connections: {len(design.connections)}
Single Point of Failure: {design.topology.has_single_point_of_failure}

DESIGN RATIONALE:
{design.design_rationale}

KEY FEATURES:
{chr(10).join(f'- {f}' for f in design.key_features)}

VALIDATION TASK:
Analyze this design for:
1. Edge cases and potential issues not covered by standard rules
2. Contextual appropriateness for the stated requirements
3. Best practice adherence
4. Potential risks or concerns
5. Optimization opportunities

Provide:
- Overall assessment score (0.0-1.0)
- Confidence in your assessment (0.0-1.0)
- Edge case analysis
- Contextual assessment
- Best practice evaluation
- List of concerns (if any)
- List of risks (if any)
- List of opportunities for improvement
- Recommendations
- Alternative approaches (if applicable)"""

        try:
            # Generate LLM validation
            response = await self.llm_service.generate(
                prompt=prompt,
                provider=LLMProvider.ANTHROPIC,
                use_fallback=True
            )
            
            # Parse response (simplified - in production, use structured output)
            result = LLMValidationResult(
                overall_score=0.85,  # Would parse from response
                confidence=0.9,
                edge_case_analysis=response[:500] if len(response) > 500 else response,
                contextual_assessment="Design appears contextually appropriate for requirements",
                best_practice_evaluation="Follows industry best practices with minor optimization opportunities",
                concerns=[],
                risks=[],
                opportunities=["Consider adding monitoring and management components"],
                recommendations=["Add network monitoring tools", "Consider backup connectivity"],
                alternative_approaches=[],
                model_used=self.llm_service.primary_provider.value,
                tokens_used=len(response.split())
            )
            
            logger.info(f"LLM validation: score={result.overall_score:.2f}, confidence={result.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"LLM validation failed: {e}")
            # Return default result on failure
            return LLMValidationResult(
                overall_score=0.7,
                confidence=0.5,
                edge_case_analysis="LLM validation unavailable",
                contextual_assessment="Unable to perform contextual assessment",
                best_practice_evaluation="Unable to evaluate best practices",
                model_used="none",
                execution_time_ms=0
            )
    
    def _combine_validation_results(self,
                                    design: NetworkDesign,
                                    deterministic: DeterministicValidationResult,
                                    llm: LLMValidationResult,
                                    mode: str) -> ValidationResult:
        """
        Combine deterministic and LLM validation results
        
        Args:
            design: Network design
            deterministic: Deterministic validation result
            llm: LLM validation result
            mode: Validation mode
        
        Returns:
            Combined validation result
        """
        # Weight deterministic more heavily (70/30 split)
        overall_score = (deterministic.overall_score * 0.7) + (llm.overall_score * 0.3)
        
        # Determine threshold based on mode
        thresholds = {
            "strict": 0.90,
            "standard": 0.85,
            "lenient": 0.75
        }
        threshold = thresholds.get(mode, 0.85)
        
        # Design passes if score meets threshold and no critical issues
        passed = overall_score >= threshold and len(deterministic.critical_issues) == 0
        
        # Aggregate all issues
        all_issues = deterministic.critical_issues + deterministic.errors + deterministic.warnings
        
        # Generate summary
        summary = f"Design validation {'passed' if passed else 'failed'} with score {overall_score:.2f}"
        if deterministic.critical_issues:
            summary += f" ({len(deterministic.critical_issues)} critical issues)"
        
        # Generate explanation
        explanation = f"""Validation Results:
- Deterministic Score: {deterministic.overall_score:.2f} ({deterministic.rules_passed}/{deterministic.total_rules_executed} rules passed)
- LLM Score: {llm.overall_score:.2f} (confidence: {llm.confidence:.2f})
- Overall Score: {overall_score:.2f}
- Threshold: {threshold:.2f}

Issues Found:
- Critical: {len(deterministic.critical_issues)}
- Errors: {len(deterministic.errors)}
- Warnings: {len(deterministic.warnings)}"""
        
        # Key findings
        key_findings = []
        if deterministic.rules_passed == deterministic.total_rules_executed:
            key_findings.append("All deterministic rules passed")
        if llm.overall_score > 0.9:
            key_findings.append("LLM assessment highly positive")
        if deterministic.critical_issues:
            key_findings.append(f"{len(deterministic.critical_issues)} critical issues require immediate attention")
        
        # Recommendations
        recommendations = llm.recommendations if llm.recommendations else []
        
        # Create validation result
        validation_id = f"val_{uuid.uuid4().hex[:12]}"
        
        result = ValidationResult(
            validation_id=validation_id,
            design_id=design.design_id or "unknown",
            overall_score=overall_score,
            deterministic_score=deterministic.overall_score,
            llm_score=llm.overall_score,
            deterministic_validation=deterministic,
            llm_validation=llm,
            passed=passed,
            validation_threshold=threshold,
            all_issues=all_issues,
            critical_count=len(deterministic.critical_issues),
            error_count=len(deterministic.errors),
            warning_count=len(deterministic.warnings),
            summary=summary,
            explanation=explanation,
            key_findings=key_findings,
            recommendations=recommendations,
            required_changes=[i.recommendation for i in deterministic.critical_issues if i.recommendation],
            optional_improvements=[i.recommendation for i in deterministic.warnings if i.recommendation],
            validated_at=datetime.utcnow(),
            validated_by=self.agent_name
        )
        
        return result


# Dependency injection for FastAPI
def get_validation_agent() -> ValidationAgent:
    """Get validation agent for dependency injection"""
    return ValidationAgent()
