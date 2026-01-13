"""
Compliance Validation Rules
Rules for validating regulatory and standards compliance
"""
from typing import Dict, Any, List

from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.models.network_design import NetworkDesign


class ComplianceRequirementsRule(ValidationRule):
    """Validate compliance requirements are specified"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.security_level.value in ["government", "critical_infrastructure", "enterprise"]:
            if not design.compliance_requirements:
                return RuleResult(
                    rule_id=self.get_rule_id(),
                    rule_name=self.get_name(),
                    category=self.get_category(),
                    severity=RuleSeverity.WARNING,
                    passed=False,
                    score=0.6,
                    message="No compliance requirements specified for high security design",
                    recommendation="Specify applicable compliance standards (PCI-DSS, HIPAA, SOC2, etc.)"
                )
        
        if design.compliance_requirements:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"Compliance requirements: {', '.join(design.compliance_requirements)}"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Compliance requirements check passed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Compliance Requirements",
            "description": "Validate compliance requirements are specified",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "requirements"]
        }


class PCIDSSComplianceRule(ValidationRule):
    """Validate PCI-DSS compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and "PCI-DSS" in design.compliance_requirements
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # PCI-DSS requires network segmentation
        vlans = set(c.vlan for c in design.connections if c.vlan)
        if len(vlans) < 2:
            issues.append("Network segmentation required (separate cardholder data environment)")
            score -= 0.3
        
        # PCI-DSS requires firewalls
        firewalls = [c for c in design.components if 'firewall' in c.component_type.lower()]
        if not firewalls:
            issues.append("Firewall required between trusted and untrusted networks")
            score -= 0.3
        
        # PCI-DSS requires encryption
        has_encryption = any('ipsec' in (c.protocol or '').lower() or 'tls' in (c.protocol or '').lower() for c in design.connections)
        if not has_encryption:
            issues.append("Encryption required for cardholder data transmission")
            score -= 0.2
        
        # PCI-DSS requires logging
        logging = [c for c in design.components if any(l in c.component_type.lower() for l in ['log', 'siem', 'syslog'])]
        if not logging:
            issues.append("Logging and monitoring required for audit trails")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"PCI-DSS compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "PCI-DSS Compliance",
            "description": "Validate PCI-DSS compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.ERROR,
            "tags": ["compliance", "pci-dss", "payment"]
        }


class HIPAAComplianceRule(ValidationRule):
    """Validate HIPAA compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and "HIPAA" in design.compliance_requirements
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # HIPAA requires encryption
        has_encryption = any('ipsec' in (c.protocol or '').lower() or 'tls' in (c.protocol or '').lower() or 'vpn' in (c.protocol or '').lower() for c in design.connections)
        if not has_encryption:
            issues.append("Encryption required for PHI (Protected Health Information)")
            score -= 0.3
        
        # HIPAA requires access controls
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'radius', 'tacacs', 'ldap'])]
        if not auth:
            issues.append("Access control mechanisms required (AAA/RADIUS)")
            score -= 0.3
        
        # HIPAA requires audit logging
        logging = [c for c in design.components if any(l in c.component_type.lower() for l in ['log', 'siem', 'audit'])]
        if not logging:
            issues.append("Audit logging required for access to PHI")
            score -= 0.2
        
        # HIPAA requires network segmentation
        vlans = set(c.vlan for c in design.connections if c.vlan)
        if len(vlans) < 2:
            issues.append("Network segmentation recommended for PHI isolation")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"HIPAA compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "HIPAA Compliance",
            "description": "Validate HIPAA compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.ERROR,
            "tags": ["compliance", "hipaa", "healthcare"]
        }


class SOC2ComplianceRule(ValidationRule):
    """Validate SOC 2 compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and any(s in design.compliance_requirements for s in ["SOC2", "SOC 2"])
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # SOC 2 requires monitoring
        monitoring = [c for c in design.components if any(m in c.component_type.lower() for m in ['monitor', 'siem', 'log'])]
        if not monitoring:
            issues.append("Monitoring and logging required for security controls")
            score -= 0.25
        
        # SOC 2 requires redundancy (availability)
        if design.topology.redundancy_level.value in ["none", "low"]:
            issues.append("Higher redundancy recommended for availability requirements")
            score -= 0.25
        
        # SOC 2 requires access controls
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'radius', 'auth'])]
        if not auth:
            issues.append("Access control mechanisms required")
            score -= 0.25
        
        # SOC 2 requires encryption
        has_encryption = any('tls' in (c.protocol or '').lower() or 'ipsec' in (c.protocol or '').lower() for c in design.connections)
        if not has_encryption:
            issues.append("Encryption recommended for data in transit")
            score -= 0.25
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"SOC 2 compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "SOC 2 Compliance",
            "description": "Validate SOC 2 compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "soc2", "audit"]
        }


class ISO27001ComplianceRule(ValidationRule):
    """Validate ISO 27001 compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and any(i in design.compliance_requirements for i in ["ISO27001", "ISO 27001"])
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # ISO 27001 requires risk-based security controls
        if design.security_level.value == "basic":
            issues.append("Higher security level recommended for ISO 27001")
            score -= 0.2
        
        # ISO 27001 requires access control
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'radius', 'auth'])]
        if not auth:
            issues.append("Access control policy implementation required")
            score -= 0.2
        
        # ISO 27001 requires network security
        firewalls = [c for c in design.components if 'firewall' in c.component_type.lower()]
        if not firewalls:
            issues.append("Network security controls (firewalls) required")
            score -= 0.2
        
        # ISO 27001 requires monitoring
        monitoring = [c for c in design.components if any(m in c.component_type.lower() for m in ['monitor', 'siem', 'log'])]
        if not monitoring:
            issues.append("Security monitoring and logging required")
            score -= 0.2
        
        # ISO 27001 requires encryption
        has_encryption = any('encryption' in str(c.specifications).lower() if c.specifications else False for c in design.components)
        if not has_encryption:
            issues.append("Cryptographic controls recommended")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"ISO 27001 compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "ISO 27001 Compliance",
            "description": "Validate ISO 27001 compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "iso27001", "isms"]
        }


class GDPRComplianceRule(ValidationRule):
    """Validate GDPR compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and "GDPR" in design.compliance_requirements
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # GDPR requires encryption
        has_encryption = any('encryption' in (c.protocol or '').lower() or 'tls' in (c.protocol or '').lower() for c in design.connections)
        if not has_encryption:
            issues.append("Encryption required for personal data protection")
            score -= 0.3
        
        # GDPR requires access controls
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'auth', 'access'])]
        if not auth:
            issues.append("Access control mechanisms required for data protection")
            score -= 0.3
        
        # GDPR requires audit logging
        logging = [c for c in design.components if any(l in c.component_type.lower() for l in ['log', 'audit', 'siem'])]
        if not logging:
            issues.append("Audit logging required for data processing activities")
            score -= 0.2
        
        # GDPR requires data segmentation
        vlans = set(c.vlan for c in design.connections if c.vlan)
        if len(vlans) < 2:
            issues.append("Data segmentation recommended for personal data isolation")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"GDPR compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "GDPR Compliance",
            "description": "Validate GDPR compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "gdpr", "privacy"]
        }


class NISTComplianceRule(ValidationRule):
    """Validate NIST Cybersecurity Framework compliance"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and any(n in design.compliance_requirements for n in ["NIST", "NIST-CSF"])
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # NIST requires identification (asset management)
        # Assume components represent identified assets
        
        # NIST requires protection
        firewalls = [c for c in design.components if 'firewall' in c.component_type.lower()]
        if not firewalls:
            issues.append("Protective controls (firewalls) required")
            score -= 0.2
        
        # NIST requires detection
        ids = [c for c in design.components if any(i in c.component_type.lower() for i in ['ids', 'ips', 'intrusion'])]
        if not ids:
            issues.append("Detection capabilities (IDS/IPS) recommended")
            score -= 0.2
        
        # NIST requires response (monitoring)
        monitoring = [c for c in design.components if any(m in c.component_type.lower() for m in ['siem', 'monitor', 'log'])]
        if not monitoring:
            issues.append("Response capabilities (monitoring/SIEM) required")
            score -= 0.2
        
        # NIST requires recovery (redundancy)
        if design.topology.redundancy_level.value in ["none", "low"]:
            issues.append("Recovery capabilities (redundancy) recommended")
            score -= 0.2
        
        # NIST requires access control
        auth = [c for c in design.components if any(a in c.component_type.lower() for a in ['aaa', 'auth'])]
        if not auth:
            issues.append("Access control mechanisms recommended")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"NIST CSF compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "NIST Compliance",
            "description": "Validate NIST Cybersecurity Framework compliance",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "nist", "cybersecurity"]
        }


class FedRAMPComplianceRule(ValidationRule):
    """Validate FedRAMP compliance requirements"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.compliance_requirements and "FedRAMP" in design.compliance_requirements
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        issues = []
        score = 1.0
        
        # FedRAMP requires high security
        if design.security_level.value not in ["government", "critical_infrastructure"]:
            issues.append("Government or critical infrastructure security level required")
            score -= 0.3
        
        # FedRAMP requires encryption
        has_encryption = any('fips' in str(c.specifications).lower() if c.specifications else False for c in design.components)
        if not has_encryption:
            issues.append("FIPS 140-2 validated encryption required")
            score -= 0.3
        
        # FedRAMP requires continuous monitoring
        monitoring = [c for c in design.components if any(m in c.component_type.lower() for m in ['siem', 'monitor'])]
        if not monitoring:
            issues.append("Continuous monitoring (SIEM) required")
            score -= 0.2
        
        # FedRAMP requires redundancy
        if design.topology.redundancy_level.value not in ["high", "critical"]:
            issues.append("High redundancy required for availability")
            score -= 0.2
        
        passed = len(issues) == 0
        score = max(0.0, score)
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR if not passed else RuleSeverity.INFO,
            passed=passed,
            score=score,
            message=f"FedRAMP compliance check: {len(issues)} issues found",
            recommendation="; ".join(issues) if issues else None,
            details={"issues": issues}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "FedRAMP Compliance",
            "description": "Validate FedRAMP compliance requirements",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.ERROR,
            "tags": ["compliance", "fedramp", "government"]
        }


class DataResidencyRule(ValidationRule):
    """Validate data residency requirements"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if multi-site design
        if not design.scale or design.scale.sites <= 1:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Single site design, data residency not applicable"
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
                score=0.6,
                message="Multi-site design but no component locations specified",
                recommendation="Specify component locations for data residency compliance"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Component locations specified for {len(components_with_location)} components"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Data Residency",
            "description": "Validate data residency requirements for multi-site designs",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "data-residency", "multi-site"]
        }


class AuditTrailRule(ValidationRule):
    """Validate audit trail capabilities"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if compliance requires audit trails
        requires_audit = bool(design.compliance_requirements)
        
        if not requires_audit:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Audit trails not required (no compliance requirements)"
            )
        
        # Check for logging/audit components
        audit_components = [c for c in design.components if any(a in c.component_type.lower() for a in ['log', 'siem', 'audit', 'syslog'])]
        
        if not audit_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message="No audit trail components configured",
                recommendation="Add logging/SIEM for compliance audit trails"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message=f"Audit trail configured ({len(audit_components)} component(s))"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Audit Trail",
            "description": "Validate audit trail capabilities for compliance",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.WARNING,
            "tags": ["compliance", "audit", "logging"]
        }


class ChangeManagementRule(ValidationRule):
    """Validate change management considerations"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # This is more of a process rule, but we can check for version control indicators
        
        if design.version and design.version != "1.0":
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"Design version {design.version} - change management in place"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Ensure change management processes are followed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Change Management",
            "description": "Validate change management considerations",
            "category": RuleCategory.COMPLIANCE,
            "severity": RuleSeverity.INFO,
            "tags": ["compliance", "change-management", "process"]
        }
