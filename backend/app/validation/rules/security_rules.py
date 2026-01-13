"""
Security Validation Rules
Rules for validating network security configurations
"""
from typing import Dict, Any, List

from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.models.network_design import NetworkDesign, SecurityLevel


class FirewallPresenceRule(ValidationRule):
    """Validate firewall presence for secure networks"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if firewalls are required
        requires_firewall = design.security_level.value in ["enterprise", "government", "critical_infrastructure"]
        
        # Find firewall components
        firewalls = [c for c in design.components if 'firewall' in c.component_type.lower() or 'firewall' in c.name.lower()]
        
        if requires_firewall and not firewalls:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.CRITICAL,
                passed=False,
                score=0.0,
                message=f"No firewall for {design.security_level.value} security level",
                recommendation="Add firewall components for network security"
            )
        
        if firewalls:
            total_firewalls = sum(c.quantity for c in firewalls)
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"{total_firewalls} firewall(s) configured"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Firewall not required for this security level"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Firewall Presence",
            "description": "Validate firewall presence for secure networks",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.CRITICAL,
            "tags": ["security", "firewall", "critical"]
        }


class RedundantFirewallsRule(ValidationRule):
    """Validate firewall redundancy for high security"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.security_level.value not in ["government", "critical_infrastructure"]:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Firewall redundancy not required for this security level"
            )
        
        firewalls = [c for c in design.components if 'firewall' in c.component_type.lower()]
        total_firewalls = sum(c.quantity for c in firewalls)
        
        if total_firewalls < 2:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.5,
                message=f"Only {total_firewalls} firewall(s) for {design.security_level.value} security",
                recommendation="Add redundant firewalls for high availability"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"{total_firewalls} redundant firewalls configured"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Redundant Firewalls",
            "description": "Validate firewall redundancy for high security levels",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.ERROR,
            "tags": ["security", "firewall", "redundancy"]
        }


class IDSIPSPresenceRule(ValidationRule):
    """Validate IDS/IPS presence for threat detection"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        requires_ids = design.security_level.value in ["enterprise", "government", "critical_infrastructure"]
        
        # Find IDS/IPS components
        ids_components = [c for c in design.components if any(x in c.component_type.lower() for x in ['ids', 'ips', 'intrusion'])]
        
        if requires_ids and not ids_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message="No IDS/IPS for threat detection",
                recommendation="Add IDS/IPS for intrusion detection and prevention"
            )
        
        if ids_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"IDS/IPS configured ({len(ids_components)} component(s))"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="IDS/IPS not required for this security level"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "IDS/IPS Presence",
            "description": "Validate IDS/IPS presence for threat detection",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "ids", "ips", "threat-detection"]
        }


class NetworkSegmentationRule(ValidationRule):
    """Validate network segmentation for security"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.security_level.value == "basic":
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Segmentation not required for basic security"
            )
        
        # Check for VLANs (basic segmentation)
        vlans_used = set()
        for conn in design.connections:
            if conn.vlan:
                vlans_used.add(conn.vlan)
        
        # Check for security zones in component locations
        zones = set()
        for component in design.components:
            if component.location:
                loc = component.location.lower()
                if any(z in loc for z in ['dmz', 'internal', 'external', 'zone', 'segment']):
                    zones.add(component.location)
        
        has_segmentation = len(vlans_used) > 1 or len(zones) > 1
        
        if not has_segmentation:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message="No network segmentation detected",
                recommendation="Implement network segmentation using VLANs or security zones"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Network segmentation: {len(vlans_used)} VLANs, {len(zones)} zones"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Network Segmentation",
            "description": "Validate network segmentation for security isolation",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "segmentation", "isolation"]
        }


class EncryptionRule(ValidationRule):
    """Validate encryption for sensitive data"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        requires_encryption = design.security_level.value in ["government", "critical_infrastructure"]
        
        # Check for encryption mentions
        has_encryption = False
        
        for conn in design.connections:
            if conn.protocol:
                protocol = conn.protocol.lower()
                if any(e in protocol for e in ['ipsec', 'vpn', 'tls', 'ssl', 'macsec', 'encryption']):
                    has_encryption = True
                    break
        
        if not has_encryption:
            for component in design.components:
                if component.specifications:
                    specs_str = str(component.specifications).lower()
                    if any(e in specs_str for e in ['encryption', 'ipsec', 'vpn', 'tls']):
                        has_encryption = True
                        break
        
        if requires_encryption and not has_encryption:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.5,
                message="No encryption configured for high security level",
                recommendation="Implement encryption (IPsec, MACsec, TLS) for data protection"
            )
        
        if has_encryption:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Encryption configured"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=0.9,
            message="Consider encryption for enhanced security"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Encryption",
            "description": "Validate encryption for sensitive data protection",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.ERROR,
            "tags": ["security", "encryption", "data-protection"]
        }


class AuthenticationRule(ValidationRule):
    """Validate authentication mechanisms"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        requires_auth = design.security_level.value in ["enterprise", "government", "critical_infrastructure"]
        
        # Check for authentication components
        auth_components = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'radius', 'tacacs', 'ldap', 'authentication'])]
        
        if requires_auth and not auth_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.7,
                message="No authentication server configured",
                recommendation="Add AAA/RADIUS/TACACS+ for centralized authentication"
            )
        
        if auth_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"Authentication configured ({len(auth_components)} component(s))"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Authentication check passed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Authentication",
            "description": "Validate authentication mechanisms are configured",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "authentication", "aaa"]
        }


class DMZConfigurationRule(ValidationRule):
    """Validate DMZ configuration for internet-facing services"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if design needs DMZ
        needs_dmz = design.network_type.value in ["enterprise_datacenter", "service_provider"]
        
        if not needs_dmz:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="DMZ not required for this network type"
            )
        
        # Check for DMZ components or zones
        has_dmz = False
        
        for component in design.components:
            if component.location and 'dmz' in component.location.lower():
                has_dmz = True
                break
            if 'dmz' in component.name.lower():
                has_dmz = True
                break
        
        if not has_dmz:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.7,
                message="No DMZ configured for internet-facing services",
                recommendation="Configure DMZ for public-facing servers"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="DMZ configured"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "DMZ Configuration",
            "description": "Validate DMZ configuration for internet-facing services",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "dmz", "perimeter"]
        }


class AccessControlListsRule(ValidationRule):
    """Validate access control lists are considered"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.security_level.value == "basic":
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="ACLs not required for basic security"
            )
        
        # Check for ACL mentions
        has_acl = False
        
        for conn in design.connections:
            if conn.protocol and 'acl' in conn.protocol.lower():
                has_acl = True
                break
        
        for component in design.components:
            if component.specifications:
                specs_str = str(component.specifications).lower()
                if 'acl' in specs_str or 'access-list' in specs_str:
                    has_acl = True
                    break
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0 if has_acl else 0.9,
            message="ACLs configured" if has_acl else "Consider implementing ACLs for access control"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Access Control Lists",
            "description": "Validate access control lists are considered",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.INFO,
            "tags": ["security", "acl", "access-control"]
        }


class AntiDDoSRule(ValidationRule):
    """Validate DDoS protection for internet-facing networks"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        needs_ddos = design.network_type.value in ["service_provider", "cloud_provider"]
        
        if not needs_ddos:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="DDoS protection not required for this network type"
            )
        
        # Check for DDoS protection
        has_ddos = False
        
        for component in design.components:
            comp_str = f"{component.component_type} {component.name}".lower()
            if any(d in comp_str for d in ['ddos', 'anti-ddos', 'mitigation']):
                has_ddos = True
                break
        
        if not has_ddos:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message="No DDoS protection configured",
                recommendation="Add DDoS mitigation for internet-facing services"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="DDoS protection configured"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Anti-DDoS Protection",
            "description": "Validate DDoS protection for internet-facing networks",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "ddos", "protection"]
        }


class SecurityMonitoringRule(ValidationRule):
    """Validate security monitoring and logging"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        requires_monitoring = design.security_level.value in ["enterprise", "government", "critical_infrastructure"]
        
        # Check for monitoring/logging components
        monitoring = [c for c in design.components if any(m in c.component_type.lower() for m in ['siem', 'log', 'monitor', 'syslog', 'netflow'])]
        
        if requires_monitoring and not monitoring:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message="No security monitoring configured",
                recommendation="Add SIEM/logging for security monitoring"
            )
        
        if monitoring:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"Security monitoring configured ({len(monitoring)} component(s))"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Security monitoring check passed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Security Monitoring",
            "description": "Validate security monitoring and logging capabilities",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "monitoring", "siem", "logging"]
        }


class ZeroTrustPrinciplesRule(ValidationRule):
    """Validate zero trust security principles"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.security_level.value not in ["government", "critical_infrastructure"]:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Zero trust not required for this security level"
            )
        
        # Check for zero trust components
        zero_trust_score = 0
        max_score = 4
        
        # 1. Micro-segmentation (VLANs)
        vlans = set(c.vlan for c in design.connections if c.vlan)
        if len(vlans) > 2:
            zero_trust_score += 1
        
        # 2. Authentication
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'radius', 'tacacs'])]
        if auth:
            zero_trust_score += 1
        
        # 3. Encryption
        encryption = any('ipsec' in (c.protocol or '').lower() or 'vpn' in (c.protocol or '').lower() for c in design.connections)
        if encryption:
            zero_trust_score += 1
        
        # 4. Monitoring
        monitoring = [c for c in design.components if 'siem' in c.component_type.lower() or 'log' in c.component_type.lower()]
        if monitoring:
            zero_trust_score += 1
        
        score = zero_trust_score / max_score
        passed = score >= 0.75
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"Zero trust principles: {zero_trust_score}/{max_score} implemented",
            recommendation="Implement micro-segmentation, authentication, encryption, and monitoring" if not passed else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Zero Trust Principles",
            "description": "Validate zero trust security principles for high security",
            "category": RuleCategory.SECURITY,
            "severity": RuleSeverity.WARNING,
            "tags": ["security", "zero-trust", "modern"]
        }
