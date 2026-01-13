"""
Topology Validation Rules
Rules for validating network topology and structure
"""
from typing import Dict, Any, Set, List
from collections import defaultdict

from app.validation.rule_base import ValidationRule, RuleResult, RuleSeverity, RuleCategory
from app.models.network_design import NetworkDesign, TopologyType


class NoSinglePointOfFailureRule(ValidationRule):
    """Validate no single point of failure for high redundancy"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if design.topology.redundancy_level.value not in ["high", "critical"]:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="SPOF check not required for this redundancy level"
            )
        
        has_spof = design.topology.has_single_point_of_failure
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.CRITICAL if has_spof else RuleSeverity.INFO,
            passed=not has_spof,
            score=0.0 if has_spof else 1.0,
            message="Single point of failure detected" if has_spof else "No single point of failure",
            recommendation="Add redundant components and paths to eliminate SPOF" if has_spof else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "No Single Point of Failure",
            "description": "Validate no SPOF exists for high redundancy designs",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.CRITICAL,
            "tags": ["topology", "redundancy", "spof", "critical"]
        }


class RedundantPathsRule(ValidationRule):
    """Validate sufficient redundant paths exist"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        redundancy_level = design.topology.redundancy_level.value
        redundant_paths = design.topology.redundant_paths
        
        # Define minimum paths based on redundancy level
        min_paths = {
            "none": 0,
            "low": 1,
            "medium": 2,
            "high": 2,
            "critical": 3
        }
        
        required = min_paths.get(redundancy_level, 2)
        passed = redundant_paths >= required
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.ERROR if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else (redundant_paths / required if required > 0 else 0.0),
            message=f"{redundant_paths} redundant paths (required: {required} for {redundancy_level} redundancy)",
            recommendation=f"Add {required - redundant_paths} more redundant paths" if not passed else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Redundant Paths",
            "description": "Validate sufficient redundant paths for redundancy level",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.ERROR,
            "tags": ["topology", "redundancy", "paths"]
        }


class TopologyLayersRule(ValidationRule):
    """Validate topology layer count is appropriate"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        layers = design.topology.layers
        topology_type = design.topology.topology_type
        
        # Expected layers by topology type
        expected_layers = {
            TopologyType.THREE_TIER: 3,
            TopologyType.COLLAPSED_CORE: 2,
            TopologyType.SPINE_LEAF: 2,
            TopologyType.MESH: 1,
            TopologyType.STAR: 2,
            TopologyType.RING: 1,
            TopologyType.HYBRID_TOPOLOGY: (2, 4)  # Range
        }
        
        expected = expected_layers.get(topology_type)
        
        if expected is None:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"Topology has {layers} layers"
            )
        
        # Check if layers match expected
        if isinstance(expected, tuple):
            passed = expected[0] <= layers <= expected[1]
            message = f"{layers} layers (expected: {expected[0]}-{expected[1]} for {topology_type.value})"
        else:
            passed = layers == expected
            message = f"{layers} layers (expected: {expected} for {topology_type.value})"
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.7,
            message=message,
            recommendation=f"Consider {expected} layers for {topology_type.value} topology" if not passed else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Topology Layers",
            "description": "Validate layer count matches topology type",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "layers", "structure"]
        }


class ConnectedComponentsRule(ValidationRule):
    """Validate all components are connected (no isolated components)"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        if not design.components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No components in design"
            )
        
        # Build adjacency list
        component_names = {c.name for c in design.components}
        connected = set()
        
        for conn in design.connections:
            if conn.source_component in component_names:
                connected.add(conn.source_component)
            if conn.target_component in component_names:
                connected.add(conn.target_component)
        
        isolated = component_names - connected
        
        passed = len(isolated) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else (len(connected) / len(component_names)),
            message=f"{len(connected)}/{len(component_names)} components connected",
            recommendation=f"Connect isolated components: {', '.join(list(isolated)[:3])}" if isolated else None,
            affected_components=list(isolated)
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Connected Components",
            "description": "Validate all components are connected (no isolated components)",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "connectivity", "isolation"]
        }


class LoopPreventionRule(ValidationRule):
    """Validate loop prevention mechanisms"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if design has redundant paths (which could create loops)
        if design.topology.redundant_paths == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="No redundant paths, loop prevention not critical"
            )
        
        # Check for spanning tree protocol or similar in connections
        has_loop_prevention = False
        for conn in design.connections:
            protocol = (conn.protocol or "").lower()
            if any(p in protocol for p in ["stp", "rstp", "mstp", "spanning"]):
                has_loop_prevention = True
                break
        
        # For mesh or ring topologies, loop prevention is critical
        critical_topologies = [TopologyType.MESH, TopologyType.RING]
        is_critical = design.topology.topology_type in critical_topologies
        
        if not has_loop_prevention and is_critical:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.6,
                message=f"Loop prevention not specified for {design.topology.topology_type.value} topology",
                recommendation="Specify loop prevention protocol (STP, RSTP, MSTP)"
            )
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=1.0,
            message="Loop prevention configured" if has_loop_prevention else "Loop prevention check passed"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Loop Prevention",
            "description": "Validate loop prevention mechanisms for redundant topologies",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "loops", "stp", "protocol"]
        }


class CoreRedundancyRule(ValidationRule):
    """Validate core layer has redundancy"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Only applicable for multi-tier topologies
        if design.topology.topology_type not in [TopologyType.THREE_TIER, TopologyType.COLLAPSED_CORE]:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="Core redundancy check not applicable for this topology"
            )
        
        # Find core components
        core_components = [c for c in design.components if 'core' in c.name.lower()]
        
        if not core_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message="No core components identified",
                recommendation="Add core layer components"
            )
        
        total_core = sum(c.quantity for c in core_components)
        
        # Core should have at least 2 devices for redundancy
        passed = total_core >= 2
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.5,
            message=f"Core layer has {total_core} component(s)",
            recommendation="Add redundant core components (minimum 2)" if not passed else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Core Redundancy",
            "description": "Validate core layer has redundancy for multi-tier topologies",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "core", "redundancy"]
        }


class SpineLeafRatioRule(ValidationRule):
    """Validate spine-leaf ratio for spine-leaf topology"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.topology.topology_type == TopologyType.SPINE_LEAF
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        spine_components = [c for c in design.components if 'spine' in c.name.lower()]
        leaf_components = [c for c in design.components if 'leaf' in c.name.lower()]
        
        if not spine_components or not leaf_components:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.WARNING,
                passed=False,
                score=0.5,
                message="Spine-leaf topology but spine/leaf components not clearly identified",
                recommendation="Ensure components are named with 'spine' and 'leaf' identifiers"
            )
        
        spine_count = sum(c.quantity for c in spine_components)
        leaf_count = sum(c.quantity for c in leaf_components)
        
        # Typical ratio: 1 spine per 2-4 leaf switches
        ratio = leaf_count / spine_count if spine_count > 0 else 0
        
        if ratio < 1:
            severity = RuleSeverity.WARNING
            message = f"Low leaf/spine ratio ({ratio:.1f}:1)"
            passed = False
            score = 0.6
        elif ratio > 8:
            severity = RuleSeverity.WARNING
            message = f"High leaf/spine ratio ({ratio:.1f}:1) - may need more spine switches"
            passed = False
            score = 0.7
        else:
            severity = RuleSeverity.INFO
            message = f"Leaf/spine ratio: {ratio:.1f}:1 (good)"
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
            details={"ratio": ratio, "spine_count": spine_count, "leaf_count": leaf_count}
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Spine-Leaf Ratio",
            "description": "Validate spine to leaf ratio for spine-leaf topology",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "spine-leaf", "ratio"]
        }


class MeshFullConnectivityRule(ValidationRule):
    """Validate full connectivity for mesh topology"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.topology.topology_type == TopologyType.MESH
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        n = len(design.components)
        
        if n == 0:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No components in mesh topology"
            )
        
        # Full mesh requires n*(n-1)/2 connections
        expected_connections = n * (n - 1) // 2
        actual_connections = len(design.connections)
        
        # Allow some tolerance (80% of full mesh)
        min_connections = int(expected_connections * 0.8)
        
        passed = actual_connections >= min_connections
        coverage = actual_connections / expected_connections if expected_connections > 0 else 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=coverage,
            message=f"Mesh connectivity: {actual_connections}/{expected_connections} connections ({coverage*100:.0f}%)",
            recommendation=f"Add {min_connections - actual_connections} more connections for proper mesh" if not passed else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Mesh Full Connectivity",
            "description": "Validate full or near-full connectivity for mesh topology",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "mesh", "connectivity"]
        }


class HierarchicalStructureRule(ValidationRule):
    """Validate hierarchical structure for tiered topologies"""
    
    def is_applicable(self, design: NetworkDesign) -> bool:
        return design.topology.topology_type in [TopologyType.THREE_TIER, TopologyType.COLLAPSED_CORE]
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Identify layers
        core = [c for c in design.components if 'core' in c.name.lower()]
        distribution = [c for c in design.components if any(x in c.name.lower() for x in ['distribution', 'aggregation', 'dist'])]
        access = [c for c in design.components if 'access' in c.name.lower() or 'edge' in c.name.lower()]
        
        issues = []
        
        if design.topology.topology_type == TopologyType.THREE_TIER:
            if not core:
                issues.append("Missing core layer")
            if not distribution:
                issues.append("Missing distribution layer")
            if not access:
                issues.append("Missing access layer")
        elif design.topology.topology_type == TopologyType.COLLAPSED_CORE:
            if not core and not distribution:
                issues.append("Missing core/distribution layer")
            if not access:
                issues.append("Missing access layer")
        
        passed = len(issues) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.6,
            message=f"Hierarchical structure: Core={len(core)}, Dist={len(distribution)}, Access={len(access)}",
            recommendation="; ".join(issues) if issues else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Hierarchical Structure",
            "description": "Validate proper hierarchical structure for tiered topologies",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "hierarchy", "layers"]
        }


class SymmetricDesignRule(ValidationRule):
    """Validate design symmetry for balanced performance"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if redundancy groups have symmetric component counts
        redundancy_groups = defaultdict(list)
        
        for component in design.components:
            if component.redundancy_group:
                redundancy_groups[component.redundancy_group].append(component)
        
        if not redundancy_groups:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message="No redundancy groups to check for symmetry"
            )
        
        asymmetric_groups = []
        
        for group, components in redundancy_groups.items():
            quantities = [c.quantity for c in components]
            if len(set(quantities)) > 1:
                asymmetric_groups.append(f"{group} ({quantities})")
        
        passed = len(asymmetric_groups) == 0
        
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.WARNING if not passed else RuleSeverity.INFO,
            passed=passed,
            score=1.0 if passed else 0.8,
            message=f"Checked {len(redundancy_groups)} redundancy groups for symmetry",
            recommendation=f"Asymmetric groups: {', '.join(asymmetric_groups)}" if asymmetric_groups else None
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Symmetric Design",
            "description": "Validate design symmetry for balanced performance",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.WARNING,
            "tags": ["topology", "symmetry", "balance"]
        }


class EastWestTrafficRule(ValidationRule):
    """Validate east-west traffic paths for modern architectures"""
    
    async def validate(self, design: NetworkDesign) -> RuleResult:
        # Check if topology supports efficient east-west traffic
        efficient_topologies = [TopologyType.SPINE_LEAF, TopologyType.MESH]
        
        if design.topology.topology_type in efficient_topologies:
            return RuleResult(
                rule_id=self.get_rule_id(),
                rule_name=self.get_name(),
                category=self.get_category(),
                severity=RuleSeverity.INFO,
                passed=True,
                score=1.0,
                message=f"{design.topology.topology_type.value} topology supports efficient east-west traffic"
            )
        
        # For other topologies, check if there are direct peer connections
        # This is a simplified check
        return RuleResult(
            rule_id=self.get_rule_id(),
            rule_name=self.get_name(),
            category=self.get_category(),
            severity=RuleSeverity.INFO,
            passed=True,
            score=0.8,
            message=f"{design.topology.topology_type.value} topology - verify east-west traffic efficiency",
            recommendation="Consider spine-leaf or mesh for high east-west traffic"
        )
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "East-West Traffic",
            "description": "Validate topology supports efficient east-west traffic",
            "category": RuleCategory.TOPOLOGY,
            "severity": RuleSeverity.INFO,
            "tags": ["topology", "traffic", "modern"]
        }
