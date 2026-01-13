"""
Validation Rule Registry
Manages all validation rules and provides rule discovery
"""
from typing import Dict, List, Optional, Set
import logging
from datetime import datetime

from app.validation.rule_base import ValidationRule, RuleCategory, RuleSeverity, RuleResult
from app.models.network_design import NetworkDesign

logger = logging.getLogger(__name__)


class RuleRegistry:
    """
    Central registry for all validation rules
    Provides rule management, filtering, and execution
    """
    
    def __init__(self):
        """Initialize rule registry"""
        self._rules: Dict[str, ValidationRule] = {}
        self._categories: Dict[RuleCategory, List[str]] = {}
        self._tags: Dict[str, List[str]] = {}
        
        logger.info("Rule registry initialized")
    
    def register(self, rule: ValidationRule) -> None:
        """
        Register a validation rule
        
        Args:
            rule: Validation rule to register
        """
        rule_id = rule.get_rule_id()
        
        if rule_id in self._rules:
            logger.warning(f"Rule {rule_id} already registered, overwriting")
        
        self._rules[rule_id] = rule
        
        # Index by category
        category = rule.get_category()
        if category not in self._categories:
            self._categories[category] = []
        if rule_id not in self._categories[category]:
            self._categories[category].append(rule_id)
        
        # Index by tags
        for tag in rule.get_tags():
            if tag not in self._tags:
                self._tags[tag] = []
            if rule_id not in self._tags[tag]:
                self._tags[tag].append(rule_id)
        
        logger.info(f"Registered rule: {rule_id} ({rule.get_name()})")
    
    def unregister(self, rule_id: str) -> bool:
        """
        Unregister a validation rule
        
        Args:
            rule_id: Rule ID to unregister
        
        Returns:
            True if rule was unregistered
        """
        if rule_id not in self._rules:
            return False
        
        rule = self._rules[rule_id]
        
        # Remove from category index
        category = rule.get_category()
        if category in self._categories and rule_id in self._categories[category]:
            self._categories[category].remove(rule_id)
        
        # Remove from tag index
        for tag in rule.get_tags():
            if tag in self._tags and rule_id in self._tags[tag]:
                self._tags[tag].remove(rule_id)
        
        # Remove rule
        del self._rules[rule_id]
        
        logger.info(f"Unregistered rule: {rule_id}")
        return True
    
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """
        Get rule by ID
        
        Args:
            rule_id: Rule identifier
        
        Returns:
            ValidationRule or None
        """
        return self._rules.get(rule_id)
    
    def get_all_rules(self) -> List[ValidationRule]:
        """Get all registered rules"""
        return list(self._rules.values())
    
    def get_rules_by_category(self, category: RuleCategory) -> List[ValidationRule]:
        """
        Get all rules in a category
        
        Args:
            category: Rule category
        
        Returns:
            List of rules
        """
        rule_ids = self._categories.get(category, [])
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]
    
    def get_rules_by_tag(self, tag: str) -> List[ValidationRule]:
        """
        Get all rules with a specific tag
        
        Args:
            tag: Tag to filter by
        
        Returns:
            List of rules
        """
        rule_ids = self._tags.get(tag, [])
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]
    
    def get_rules_by_severity(self, severity: RuleSeverity) -> List[ValidationRule]:
        """
        Get all rules with a specific severity
        
        Args:
            severity: Severity level
        
        Returns:
            List of rules
        """
        return [rule for rule in self._rules.values() if rule.get_severity() == severity]
    
    def get_enabled_rules(self) -> List[ValidationRule]:
        """Get all enabled rules"""
        return [rule for rule in self._rules.values() if rule.is_enabled()]
    
    def get_applicable_rules(self, design: NetworkDesign) -> List[ValidationRule]:
        """
        Get all rules applicable to a design
        
        Args:
            design: Network design
        
        Returns:
            List of applicable rules
        """
        return [
            rule for rule in self.get_enabled_rules()
            if rule.is_applicable(design)
        ]
    
    async def execute_rules(self,
                          design: NetworkDesign,
                          categories: Optional[List[RuleCategory]] = None,
                          tags: Optional[List[str]] = None,
                          rule_ids: Optional[List[str]] = None) -> List[RuleResult]:
        """
        Execute validation rules
        
        Args:
            design: Network design to validate
            categories: Filter by categories (None = all)
            tags: Filter by tags (None = all)
            rule_ids: Specific rule IDs to execute (None = all)
        
        Returns:
            List of rule results
        """
        # Determine which rules to execute
        if rule_ids:
            rules = [self._rules[rid] for rid in rule_ids if rid in self._rules]
        else:
            rules = self.get_enabled_rules()
        
        # Filter by category
        if categories:
            rules = [r for r in rules if r.get_category() in categories]
        
        # Filter by tags
        if tags:
            rules = [r for r in rules if any(tag in r.get_tags() for tag in tags)]
        
        # Filter by applicability
        rules = [r for r in rules if r.is_applicable(design)]
        
        logger.info(f"Executing {len(rules)} validation rules")
        
        # Execute rules
        results = []
        for rule in rules:
            try:
                start_time = datetime.utcnow()
                result = await rule.validate(design)
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                result.execution_time_ms = execution_time
                results.append(result)
            except Exception as e:
                logger.error(f"Rule {rule.get_rule_id()} failed: {e}")
                # Create error result
                results.append(RuleResult(
                    rule_id=rule.get_rule_id(),
                    rule_name=rule.get_name(),
                    category=rule.get_category(),
                    severity=RuleSeverity.ERROR,
                    passed=False,
                    score=0.0,
                    message=f"Rule execution failed: {str(e)}",
                    execution_time_ms=0.0
                ))
        
        logger.info(f"Executed {len(results)} rules, {len([r for r in results if r.passed])} passed")
        return results
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics
        
        Returns:
            Statistics dictionary
        """
        enabled_count = len(self.get_enabled_rules())
        
        return {
            "total_rules": len(self._rules),
            "enabled_rules": enabled_count,
            "disabled_rules": len(self._rules) - enabled_count,
            "categories": {
                cat.value: len(rules)
                for cat, rules in self._categories.items()
            },
            "tags": {
                tag: len(rules)
                for tag, rules in self._tags.items()
            },
            "severity_distribution": {
                sev.value: len(self.get_rules_by_severity(sev))
                for sev in RuleSeverity
            }
        }
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enable()
            logger.info(f"Enabled rule: {rule_id}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.disable()
            logger.info(f"Disabled rule: {rule_id}")
            return True
        return False
    
    def enable_category(self, category: RuleCategory) -> int:
        """Enable all rules in a category"""
        rules = self.get_rules_by_category(category)
        for rule in rules:
            rule.enable()
        logger.info(f"Enabled {len(rules)} rules in category {category.value}")
        return len(rules)
    
    def disable_category(self, category: RuleCategory) -> int:
        """Disable all rules in a category"""
        rules = self.get_rules_by_category(category)
        for rule in rules:
            rule.disable()
        logger.info(f"Disabled {len(rules)} rules in category {category.value}")
        return len(rules)
    
    def clear(self) -> None:
        """Clear all registered rules"""
        self._rules.clear()
        self._categories.clear()
        self._tags.clear()
        logger.info("Rule registry cleared")


# Global registry instance
_global_registry: Optional[RuleRegistry] = None


def get_rule_registry() -> RuleRegistry:
    """Get global rule registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = RuleRegistry()
    return _global_registry


def reset_rule_registry() -> None:
    """Reset global rule registry (for testing)"""
    global _global_registry
    _global_registry = None
