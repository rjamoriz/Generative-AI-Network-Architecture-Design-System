"""
Protocol Validation Rules
Rules for validating network protocols and configurations
"""
from typing import Dict, Any, Set
import re

from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.models.network_design import NetworkDesign


class ValidConnectionTypesRule(ValidationRule):
    """Validate connection types are valid"""
    
    def __init__(self):
        self.valid_types = {
            'ethernet', 'fiber', 'copper', 'wireless', 'optical',
            'cat5', 'cat5e', 'cat6', 'cat6a', 'cat7',
            'sfp', 'sfp+', 'qsfp', 'qsfp+', 'qsfp28',
            'single-mode', 'multi-mode', 'coax'
        }
        super().__init__()
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        invalid_connections = []
        
        for conn in design.connections:
            conn_type = conn.connection_type.lower().strip()
            if conn_type not in self.valid_types:
                invalid_connections.append(f"{conn.connection_id}: {conn.connection_type}")
        
        passed = len(invalid_connections) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.7,
            message=f"Validated {len(design.connections)} connection types",
            recommendation=f"Review connection types: {', '.join(invalid_connections[:3])}" if invalid_connections else None,
            details={"invalid_connections": invalid_connections} if invalid_connections else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Valid Connection Types",
            "description": "Validate connection types are recognized",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "connections", "types"]
        }


class BandwidthConsistencyRule(ValidationRule):
    """Validate bandwidth specifications are consistent"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        
        for conn in design.connections:
            if not conn.bandwidth:
                issues.append(f"{conn.connection_id}: No bandwidth specified")
                continue
            
            # Parse bandwidth
            bw = conn.bandwidth.upper().strip()
            if not re.match(r'^\d+(\.\d+)?\s*[KMGT]?BPS?$', bw):
                issues.append(f"{conn.connection_id}: Invalid bandwidth format '{conn.bandwidth}'")
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.8,
            message=f"Validated bandwidth for {len(design.connections)} connections",
            recommendation="; ".join(issues[:3]) if issues else None,
            details={"issues": issues} if issues else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Bandwidth Consistency",
            "description": "Validate bandwidth specifications are consistent and valid",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "bandwidth", "consistency"]
        }


class VLANConfigurationRule(ValidationRule):
    """Validate VLAN configuration"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        vlans_used = set()
        issues = []
        
        for conn in design.connections:
            if conn.vlan is not None:
                # VLAN range: 1-4094 (0 and 4095 reserved)
                if conn.vlan < 1 or conn.vlan > 4094:
                    issues.append(f"{conn.connection_id}: Invalid VLAN {conn.vlan} (valid: 1-4094)")
                else:
                    vlans_used.add(conn.vlan)
        
        # Check for VLAN 1 usage (default, should be avoided)
        if 1 in vlans_used:
            issues.append("VLAN 1 in use (default VLAN, consider using different VLANs)")
        
        passed = len([i for i in issues if 'Invalid' in i]) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.7,
            message=f"Using {len(vlans_used)} VLANs across {len(design.connections)} connections",
            recommendation="; ".join(issues[:3]) if issues else None,
            details={"vlans_used": sorted(list(vlans_used)), "issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "VLAN Configuration",
            "description": "Validate VLAN configuration is correct",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "vlan", "layer2"]
        }


class RoutingProtocolRule(ValidationRule):
    """Validate routing protocol configuration"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        routing_protocols = set()
        
        for conn in design.connections:
            if conn.protocol:
                protocol = conn.protocol.lower()
                if any(p in protocol for p in ['ospf', 'bgp', 'eigrp', 'rip', 'isis']):
                    routing_protocols.add(conn.protocol)
        
        # Check for routers
        routers = [c for c in design.components if 'router' in c.component_type.lower()]
        
        if routers and not routing_protocols:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message="Routers present but no routing protocol specified",
                recommendation="Specify routing protocol (OSPF, BGP, EIGRP, etc.)"
            )
        
        # Check for multiple routing protocols (can be valid but should be intentional)
        if len(routing_protocols) > 2:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=True,
                score=0.8,
                message=f"Multiple routing protocols in use: {', '.join(routing_protocols)}",
                recommendation="Verify multiple routing protocols are intentional"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Routing protocols: {', '.join(routing_protocols) if routing_protocols else 'None specified'}"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Routing Protocol",
            "description": "Validate routing protocol configuration",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "routing", "layer3"]
        }


class InterfaceNamingRule(ValidationRule):
    """Validate interface naming conventions"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        
        for conn in design.connections:
            # Check source interface
            if not conn.source_interface or conn.source_interface.strip() == "":
                issues.append(f"{conn.connection_id}: Missing source interface")
            
            # Check target interface
            if not conn.target_interface or conn.target_interface.strip() == "":
                issues.append(f"{conn.connection_id}: Missing target interface")
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.7,
            message=f"Validated interfaces for {len(design.connections)} connections",
            recommendation="; ".join(issues[:5]) if issues else None,
            details={"issues": issues} if issues else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Interface Naming",
            "description": "Validate interface naming is specified",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "interfaces", "naming"]
        }


class QoSConfigurationRule(ValidationRule):
    """Validate QoS configuration for critical traffic"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if design requires QoS
        requires_qos = False
        
        if design.scale and design.scale.users > 1000:
            requires_qos = True
        
        if design.network_type.value in ["enterprise_datacenter", "service_provider"]:
            requires_qos = True
        
        if not requires_qos:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="QoS not required for this design"
            )
        
        # Check for QoS in protocols
        has_qos = False
        for conn in design.connections:
            if conn.protocol:
                protocol = conn.protocol.lower()
                if any(q in protocol for q in ['qos', 'cos', 'dscp', 'priority']):
                    has_qos = True
                    break
        
        if not has_qos:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.7,
                message="QoS recommended but not configured",
                recommendation="Configure QoS for traffic prioritization"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="QoS configuration detected"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "QoS Configuration",
            "description": "Validate QoS configuration for critical traffic",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.WARNING,
            "tags": ["protocol", "qos", "performance"]
        }


class MulticastSupportRule(ValidationRule):
    """Validate multicast support if needed"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if multicast is needed
        needs_multicast = False
        
        if design.network_type.value in ["enterprise_datacenter", "campus"]:
            needs_multicast = True
        
        if not needs_multicast:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Multicast not required for this network type"
            )
        
        # Check for multicast protocols
        has_multicast = False
        for conn in design.connections:
            if conn.protocol:
                protocol = conn.protocol.lower()
                if any(m in protocol for m in ['igmp', 'pim', 'multicast']):
                    has_multicast = True
                    break
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0 if has_multicast else 0.9,
            message="Multicast support configured" if has_multicast else "Consider multicast support (IGMP, PIM)"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Multicast Support",
            "description": "Validate multicast support if needed",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.INFO,
            "tags": ["protocol", "multicast", "igmp"]
        }


class IPv6SupportRule(ValidationRule):
    """Validate IPv6 support for modern networks"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check for IPv6 mentions in protocols or specifications
        has_ipv6 = False
        
        for conn in design.connections:
            if conn.protocol and 'ipv6' in conn.protocol.lower():
                has_ipv6 = True
                break
        
        for component in design.components:
            if component.specifications:
                specs_str = str(component.specifications).lower()
                if 'ipv6' in specs_str:
                    has_ipv6 = True
                    break
        
        # IPv6 is recommended for new designs
        if not has_ipv6:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=0.8,
                message="IPv6 not explicitly configured",
                recommendation="Consider IPv6 support for future-proofing"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="IPv6 support configured"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "IPv6 Support",
            "description": "Validate IPv6 support for modern networks",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.INFO,
            "tags": ["protocol", "ipv6", "modern"]
        }


class LinkAggregationRule(ValidationRule):
    """Validate link aggregation for high bandwidth"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check for link aggregation protocols
        has_lag = False
        lag_connections = []
        
        for conn in design.connections:
            if conn.protocol:
                protocol = conn.protocol.lower()
                if any(l in protocol for l in ['lacp', 'lag', 'etherchannel', 'port-channel']):
                    has_lag = True
                    lag_connections.append(conn.connection_id)
        
        # Check if high bandwidth requires LAG
        if design.bandwidth_requirement and design.bandwidth_requirement.min:
            min_bw = design.bandwidth_requirement.min.upper()
            if any(x in min_bw for x in ['10G', '25G', '40G', '100G']):
                if not has_lag:
                    return RuleResult(
                        rule_id=self.get_rule_id(),
                        rule_name=self.get_name(),
                        category=self.get_category(),
                        severity=RuleSeverity.INFO,
                        passed=True,
                        score=0.9,
                        message="High bandwidth design - consider link aggregation (LACP)",
                        recommendation="Use LACP for increased bandwidth and redundancy"
                    )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Link aggregation configured on {len(lag_connections)} connections" if has_lag else "Link aggregation check passed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Link Aggregation",
            "description": "Validate link aggregation for high bandwidth and redundancy",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.INFO,
            "tags": ["protocol", "lacp", "aggregation", "bandwidth"]
        }


class JumboFramesRule(ValidationRule):
    """Validate jumbo frames for high-performance networks"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if jumbo frames are needed
        needs_jumbo = False
        
        if design.network_type.value in ["enterprise_datacenter", "storage_network"]:
            needs_jumbo = True
        
        if design.bandwidth_requirement and design.bandwidth_requirement.min:
            min_bw = design.bandwidth_requirement.min.upper()
            if any(x in min_bw for x in ['10G', '25G', '40G', '100G']):
                needs_jumbo = True
        
        if not needs_jumbo:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Jumbo frames not required for this design"
            )
        
        # Check for MTU specifications
        has_jumbo = False
        for component in design.components:
            if component.specifications:
                specs_str = str(component.specifications).lower()
                if 'mtu' in specs_str or 'jumbo' in specs_str or '9000' in specs_str:
                    has_jumbo = True
                    break
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0 if has_jumbo else 0.9,
            message="Jumbo frames configured" if has_jumbo else "Consider jumbo frames (MTU 9000) for performance"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Jumbo Frames",
            "description": "Validate jumbo frames for high-performance networks",
            "category": RuleCategory.PROTOCOL,
            "severity": RuleSeverity.INFO,
            "tags": ["protocol", "mtu", "performance"]
        }
