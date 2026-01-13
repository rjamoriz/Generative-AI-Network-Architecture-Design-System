"""
Validation Rule Base Classes
Foundation for all validation rules
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from app.models.network_design import NetworkDesign
from app.models.validation_result import ValidationSeverity, ValidationCategory


class RuleSeverity(str, Enum):
    """Severity levels for validation rules"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class RuleCategory(str, Enum):
    """Categories for validation rules"""
    CAPACITY = "capacity"
    PROTOCOL = "protocol"
    TOPOLOGY = "topology"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    COST = "cost"
    BEST_PRACTICE = "best_practice"


@dataclass
class RuleResult:
    """Result of a validation rule execution"""
    rule_id: str
    rule_name: str
    category: RuleCategory
    severity: RuleSeverity
    passed: bool
    score: float
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    affected_components: Optional[List[str]] = None
    execution_time_ms: float = 0.0
    
    def to_validation_severity(self) -> ValidationSeverity:
        """Convert rule severity to validation severity"""
        mapping = {
            RuleSeverity.CRITICAL: ValidationSeverity.CRITICAL,
            RuleSeverity.ERROR: ValidationSeverity.ERROR,
            RuleSeverity.WARNING: ValidationSeverity.WARNING,
            RuleSeverity.INFO: ValidationSeverity.INFO,
        }
        return mapping.get(self.severity, ValidationSeverity.WARNING)
    
    def to_validation_category(self) -> ValidationCategory:
        """Convert rule category to validation category"""
        mapping = {
            RuleCategory.CAPACITY: ValidationCategory.CAPACITY,
            RuleCategory.PROTOCOL: ValidationCategory.PROTOCOL,
            RuleCategory.TOPOLOGY: ValidationCategory.TOPOLOGY,
            RuleCategory.SECURITY: ValidationCategory.SECURITY,
            RuleCategory.COMPLIANCE: ValidationCategory.COMPLIANCE,
            RuleCategory.PERFORMANCE: ValidationCategory.PERFORMANCE,
            RuleCategory.COST: ValidationCategory.COST,
            RuleCategory.BEST_PRACTICE: ValidationCategory.BEST_PRACTICE,
        }
        return mapping.get(self.category, ValidationCategory.TOPOLOGY)


class ValidationRule(ABC):
    """
    Abstract base class for all validation rules
    
    Each rule must implement:
    - validate(): Execute the validation logic
    - get_metadata(): Return rule metadata
    """
    
    def __init__(self):
        """Initialize validation rule"""
        self.rule_id = self.__class__.__name__
        self.enabled = True
        self.metadata = self.get_metadata()
    
    @abstractmethod
    async def validate(self, design: NetworkDesign) -> RuleResult:
        """
        Execute validation rule
        
        Args:
            design: Network design to validate
        
        Returns:
            RuleResult with validation outcome
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get rule metadata
        
        Returns:
            Dictionary with rule information:
            - name: Human-readable rule name
            - description: Rule description
            - category: Rule category
            - severity: Default severity level
            - tags: List of tags for filtering
        """
        pass
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        """
        Check if rule is applicable to the design
        
        Args:
            design: Network design
        
        Returns:
            True if rule should be executed
        """
        return True
    
    def get_rule_id(self) -> str:
        """Get unique rule identifier"""
        return self.rule_id
    
    def get_name(self) -> str:
        """Get rule name"""
        return self.metadata.get("name", self.rule_id)
    
    def get_category(self) -> RuleCategory:
        """Get rule category"""
        return self.metadata.get("category", RuleCategory.TOPOLOGY)
    
    def get_severity(self) -> RuleSeverity:
        """Get default severity"""
        return self.metadata.get("severity", RuleSeverity.WARNING)
    
    def get_tags(self) -> List[str]:
        """Get rule tags"""
        return self.metadata.get("tags", [])
    
    def enable(self):
        """Enable this rule"""
        self.enabled = True
    
    def disable(self):
        """Disable this rule"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if rule is enabled"""
        return self.enabled


class CompositeRule(ValidationRule):
    """
    Composite rule that combines multiple rules
    Useful for creating rule groups
    """
    
    def __init__(self, rules: List[ValidationRule], require_all: bool = True):
        """
        Initialize composite rule
        
        Args:
            rules: List of rules to combine
            require_all: If True, all rules must pass. If False, any rule passing is sufficient
        """
        self.rules = rules
        self.require_all = require_all
        super().__init__()
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        """Execute all child rules"""
        results = []
        total_time = 0.0
        
        for rule in self.rules:
            if rule.is_enabled() and rule.is_applicable(design):
                result = await rule.validate(design)
                results.append(result)
                total_time += result.execution_time_ms
        
        if not results:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=self.get_severity(),
                passed=True,
                score=1.0,
                message="No applicable rules in composite",
                execution_time_ms=total_time
            )
        
        # Aggregate results
        if self.require_all:
            passed = all(r.passed for r in results)
            score = sum(r.score for r in results) / len(results)
        else:
            passed = any(r.passed for r in results)
            score = max(r.score for r in results)
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=self.get_severity(),
            passed=passed,
            score=score,
            message=f"Composite rule: {len([r for r in results if r.passed])}/{len(results)} passed",
            details={"child_results": [r.__dict__ for r in results]},
            execution_time_ms=total_time
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get composite rule metadata"""
        return {
            "name": f"Composite Rule ({len(self.rules)} rules)",
            "description": "Combines multiple validation rules",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["composite"]
        }


class ConditionalRule(ValidationRule):
    """
    Rule that only executes if a condition is met
    """
    
    def __init__(self, rule: ValidationRule, condition_fn):
        """
        Initialize conditional rule
        
        Args:
            rule: Rule to execute conditionally
            condition_fn: Function that takes NetworkDesign and returns bool
        """
        self.rule = rule
        self.condition_fn = condition_fn
        super().__init__()
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        """Check if condition is met"""
        try:
            return self.condition_fn(design)
        except Exception:
            return False
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        """Execute rule if condition is met"""
        if not self.is_applicable(design):
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.get_name(),
                category=self.rule.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Rule not applicable (condition not met)",
                execution_time_ms=0.0
            )
        
        return await self.rule.validate(design)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get conditional rule metadata"""
        base_metadata = self.rule.get_metadata()
        base_metadata["name"] = f"Conditional: {base_metadata['name']}"
        return base_metadata
