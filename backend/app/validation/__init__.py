"""
Validation Engine Package
Comprehensive rule-based validation system for network designs
"""
from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.validation.rule_registry import RuleRegistry, get_rule_registry

__all__ = [
    "ValidationRule",
    "RuleResult",
    "RuleSeverity",
    "RuleCategory",
    "RuleRegistry",
    "get_rule_registry",
]
