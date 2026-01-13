"""
Capacity Validation Rules
Rules for validating network capacity and scalability
"""
from typing import Dict, Any
import re

from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.models.network_design import NetworkDesign


class MinimumComponentsRule(ValidationRule):
    """Validate minimum number of components"""
    
    def __init__(self, min_components: int = 5):
        self.min_components = min_components
        super().__init__()
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        component_count = len(design.components)
        passed = component_count >= self.min_components
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR,
            passed=passed,
            score=1.0 if passed else 0.0,
            message=f"Design has {component_count} components (minimum: {self.min_components})",
            recommendation=None if passed else f"Add {self.min_components - component_count} more components",
            affected_components=[] if passed else ["design"]
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Minimum Components",
            "description": f"Design must have at least {self.min_components} components",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.ERROR,
            "tags": ["capacity", "components", "basic"]
        }


class MinimumConnectionsRule(ValidationRule):
    """Validate minimum number of connections"""
    
    def __init__(self, min_connections: int = 3):
        self.min_connections = min_connections
        super().__init__()
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        connection_count = len(design.connections)
        passed = connection_count >= self.min_connections
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR,
            passed=passed,
            score=1.0 if passed else 0.0,
            message=f"Design has {connection_count} connections (minimum: {self.min_connections})",
            recommendation=None if passed else f"Add {self.min_connections - connection_count} more connections",
            affected_components=[] if passed else ["design"]
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Minimum Connections",
            "description": f"Design must have at least {self.min_connections} connections",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.ERROR,
            "tags": ["capacity", "connections", "basic"]
        }


class BandwidthCapacityRule(ValidationRule):
    """Validate bandwidth capacity meets requirements"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        has_bandwidth = design.bandwidth_requirement and design.bandwidth_requirement.min
        
        if not has_bandwidth:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message="Bandwidth requirements not specified",
                recommendation="Specify minimum and maximum bandwidth requirements"
            )
        
        # Parse bandwidth values
        min_bw = self._parse_bandwidth(design.bandwidth_requirement.min)
        max_bw = self._parse_bandwidth(design.bandwidth_requirement.max) if design.bandwidth_requirement.max else min_bw
        
        # Check if bandwidth is reasonable
        if min_bw <= 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="Invalid minimum bandwidth specified",
                recommendation="Specify valid bandwidth value (e.g., 1Gbps, 10Gbps)"
            )
        
        if max_bw < min_bw:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="Maximum bandwidth less than minimum bandwidth",
                recommendation="Ensure max bandwidth >= min bandwidth"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Bandwidth capacity: {design.bandwidth_requirement.min} to {design.bandwidth_requirement.max}"
        )
    
    def _parse_bandwidth(self, bw_str: str) -> float:
        """Parse bandwidth string to Mbps"""
        if not bw_str:
            return 0.0
        
        bw_str = bw_str.upper().strip()
        
        # Extract number and unit
        match = re.match(r'([\d.]+)\s*([KMGT]?BPS?)', bw_str)
        if not match:
            return 0.0
        
        value = float(match.group(1))
        unit = match.group(2)
        
        # Convert to Mbps
        multipliers = {
            'BPS': 0.000001,
            'KBPS': 0.001,
            'MBPS': 1,
            'GBPS': 1000,
            'TBPS': 1000000
        }
        
        return value * multipliers.get(unit, 1)
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Bandwidth Capacity",
            "description": "Validate bandwidth requirements are specified and valid",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "bandwidth", "performance"]
        }


class ScaleRequirementsRule(ValidationRule):
    """Validate scale requirements are reasonable"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if not design.scale:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message="Scale requirements not specified",
                recommendation="Specify number of devices, users, and sites"
            )
        
        issues = []
        
        if design.scale.devices <= 0:
            issues.append("Invalid device count")
        
        if design.scale.users < 0:
            issues.append("Invalid user count")
        
        if design.scale.sites <= 0:
            issues.append("Invalid site count")
        
        # Check if scale is reasonable
        if design.scale.devices > 100000:
            issues.append("Very large device count (>100k) - verify requirements")
        
        if design.scale.users > design.scale.devices * 10:
            issues.append("User count significantly exceeds device count")
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if issues else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.5,
            message=f"Scale: {design.scale.devices} devices, {design.scale.users} users, {design.scale.sites} sites",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues} if issues else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Scale Requirements",
            "description": "Validate scale requirements are specified and reasonable",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "scale", "sizing"]
        }


class ComponentQuantityRule(ValidationRule):
    """Validate component quantities are reasonable"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        affected = []
        
        for component in design.components:
            if component.quantity <= 0:
                issues.append(f"{component.name}: Invalid quantity ({component.quantity})")
                affected.append(component.component_id)
            elif component.quantity > 100:
                issues.append(f"{component.name}: Very high quantity ({component.quantity})")
                affected.append(component.component_id)
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING,
            passed=passed,
            score=1.0 if passed else 0.7,
            message=f"Validated {len(design.components)} component quantities",
            recommendation="; ".join(issues[:3]) if issues else None,
            affected_components=affected,
            details={"issues": issues} if issues else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Component Quantity",
            "description": "Validate component quantities are reasonable",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "components", "quantity"]
        }


class DeviceToComponentRatioRule(ValidationRule):
    """Validate device to component ratio is reasonable"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if not design.scale or design.scale.devices <= 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Scale not specified, skipping ratio check"
            )
        
        total_components = sum(c.quantity for c in design.components)
        
        if total_components == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No components in design",
                recommendation="Add network components"
            )
        
        ratio = design.scale.devices / total_components
        
        # Typical ratio: 10-100 devices per infrastructure component
        if ratio < 1:
            severity = RuleSeverity.WARNING
            message = f"Very low device/component ratio ({ratio:.1f}:1) - may be over-provisioned"
            passed = True
            score = 0.8
        elif ratio > 500:
            severity = RuleSeverity.WARNING
            message = f"Very high device/component ratio ({ratio:.1f}:1) - may be under-provisioned"
            passed = False
            score = 0.6
        else:
            severity = RuleSeverity.INFO
            message = f"Device/component ratio: {ratio:.1f}:1 (reasonable)"
            passed = True
            score = 1.0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=severity,
            passed=passed,
            score=score,
            message=message,
            details={"ratio": ratio, "devices": design.scale.devices, "components": total_components}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Device to Component Ratio",
            "description": "Validate device to infrastructure component ratio is reasonable",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "sizing", "ratio"]
        }


class ConnectionDensityRule(ValidationRule):
    """Validate connection density is appropriate"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        component_count = len(design.components)
        connection_count = len(design.connections)
        
        if component_count == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No components to connect"
            )
        
        if connection_count == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No connections defined",
                recommendation="Add connections between components"
            )
        
        # Calculate average connections per component
        avg_connections = connection_count / component_count
        
        # Typical: 2-10 connections per component
        if avg_connections < 1:
            severity = RuleSeverity.WARNING
            message = f"Low connection density ({avg_connections:.1f} per component)"
            passed = False
            score = 0.6
        elif avg_connections > 20:
            severity = RuleSeverity.WARNING
            message = f"Very high connection density ({avg_connections:.1f} per component)"
            passed = True
            score = 0.8
        else:
            severity = RuleSeverity.INFO
            message = f"Connection density: {avg_connections:.1f} per component (good)"
            passed = True
            score = 1.0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=severity,
            passed=passed,
            score=score,
            message=message,
            details={"avg_connections": avg_connections, "total_connections": connection_count}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Connection Density",
            "description": "Validate connection density is appropriate for design",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "connections", "density"]
        }


class RedundantComponentsRule(ValidationRule):
    """Validate redundant components for high availability"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.topology.redundancy_level.value not in ["high", "critical"]:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Redundancy not required for this design"
            )
        
        # Check for redundancy groups
        redundancy_groups = {}
        for component in design.components:
            if component.redundancy_group:
                if component.redundancy_group not in redundancy_groups:
                    redundancy_groups[component.redundancy_group] = []
                redundancy_groups[component.redundancy_group].append(component)
        
        issues = []
        
        # Each redundancy group should have at least 2 components
        for group, components in redundancy_groups.items():
            if len(components) < 2:
                issues.append(f"Redundancy group '{group}' has only {len(components)} component(s)")
        
        # Critical components should be in redundancy groups
        critical_types = ["router", "switch", "firewall", "load_balancer"]
        for component in design.components:
            if component.component_type.lower() in critical_types and not component.redundancy_group:
                issues.append(f"Critical component '{component.name}' not in redundancy group")
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING,
            passed=passed,
            score=1.0 if passed else 0.6,
            message=f"Found {len(redundancy_groups)} redundancy groups",
            recommendation="; ".join(issues[:3]) if issues else None,
            details={"redundancy_groups": len(redundancy_groups), "issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Redundant Components",
            "description": "Validate redundant components for high availability designs",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "redundancy", "high-availability"]
        }


class SiteDistributionRule(ValidationRule):
    """Validate component distribution across sites"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if not design.scale or design.scale.sites <= 1:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Single site design, distribution check not applicable"
            )
        
        # Check if components specify locations
        components_with_location = [c for c in design.components if c.location]
        
        if len(components_with_location) == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message=f"Multi-site design ({design.scale.sites} sites) but no component locations specified",
                recommendation="Specify location for each component"
            )
        
        # Count unique locations
        locations = set(c.location for c in components_with_location if c.location)
        
        if len(locations) < design.scale.sites:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.7,
                message=f"Only {len(locations)} locations specified for {design.scale.sites} sites",
                recommendation="Ensure components are distributed across all sites"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Components distributed across {len(locations)} locations"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Site Distribution",
            "description": "Validate component distribution across multiple sites",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "multi-site", "distribution"]
        }


class OversubscriptionRule(ValidationRule):
    """Validate network oversubscription ratios"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # This is a simplified check - in production, would analyze actual topology
        
        # Count access vs core components
        access_components = [c for c in design.components if 'access' in c.name.lower() or 'edge' in c.name.lower()]
        core_components = [c for c in design.components if 'core' in c.name.lower() or 'spine' in c.name.lower()]
        
        if not access_components or not core_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Cannot determine oversubscription (access/core components not clearly identified)"
            )
        
        access_count = sum(c.quantity for c in access_components)
        core_count = sum(c.quantity for c in core_components)
        
        ratio = access_count / core_count if core_count > 0 else 0
        
        # Typical oversubscription: 2:1 to 4:1 for access to core
        if ratio < 1:
            severity = RuleSeverity.WARNING
            message = f"Low oversubscription ratio ({ratio:.1f}:1) - may be over-provisioned"
            passed = True
            score = 0.8
        elif ratio > 10:
            severity = RuleSeverity.WARNING
            message = f"High oversubscription ratio ({ratio:.1f}:1) - may cause congestion"
            passed = False
            score = 0.6
        else:
            severity = RuleSeverity.INFO
            message = f"Oversubscription ratio: {ratio:.1f}:1 (acceptable)"
            passed = True
            score = 1.0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=severity,
            passed=passed,
            score=score,
            message=message,
            details={"ratio": ratio, "access_components": access_count, "core_components": core_count}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Oversubscription Ratio",
            "description": "Validate network oversubscription ratios are reasonable",
            "category": RuleCategory.CAPACITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["capacity", "oversubscription", "performance"]
        }
