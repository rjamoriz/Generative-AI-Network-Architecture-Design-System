"""
Rule Loader
Loads and initializes all validation rules into the registry
"""
import logging
from typing import List

from app.validation.rule_registry import RuleRegistry, get_rule_registry
from app.validation.rules import ALL_RULES
from app.validation.rule_base import ValidationRule

logger = logging.getLogger(__name__)


def load_all_rules(registry: RuleRegistry = None) -> int:
    """
    Load all validation rules into the registry
    
    Args:
        registry: Rule registry to load into (uses global if None)
    
    Returns:
        Number of rules loaded
    """
    if registry is None:
        registry = get_rule_registry()
    
    loaded_count = 0
    
    for rule_class in ALL_RULES:
        try:
            # Instantiate rule
            rule = rule_class()
            
            # Register rule
            registry.register(rule)
            loaded_count += 1
            
        except Exception as e:
            logger.error(f"Failed to load rule {rule_class.__name__}: {e}")
    
    logger.info(f"Loaded {loaded_count} validation rules")
    return loaded_count


def load_rules_by_category(category: str, registry: RuleRegistry = None) -> int:
    """
    Load rules for a specific category
    
    Args:
        category: Category to load (capacity, topology, protocol, security, compliance)
        registry: Rule registry to load into
    
    Returns:
        Number of rules loaded
    """
    if registry is None:
        registry = get_rule_registry()
    
    category_map = {
        'capacity': [
            'MinimumComponentsRule', 'MinimumConnectionsRule', 'BandwidthCapacityRule',
            'ScaleRequirementsRule', 'ComponentQuantityRule', 'DeviceToComponentRatioRule',
            'ConnectionDensityRule', 'RedundantComponentsRule', 'SiteDistributionRule',
            'OversubscriptionRule'
        ],
        'topology': [
            'NoSinglePointOfFailureRule', 'RedundantPathsRule', 'TopologyLayersRule',
            'ConnectedComponentsRule', 'LoopPreventionRule', 'CoreRedundancyRule',
            'SpineLeafRatioRule', 'MeshFullConnectivityRule', 'HierarchicalStructureRule',
            'SymmetricDesignRule', 'EastWestTrafficRule'
        ],
        'protocol': [
            'ValidConnectionTypesRule', 'BandwidthConsistencyRule', 'VLANConfigurationRule',
            'RoutingProtocolRule', 'InterfaceNamingRule', 'QoSConfigurationRule',
            'MulticastSupportRule', 'IPv6SupportRule', 'LinkAggregationRule',
            'JumboFramesRule'
        ],
        'security': [
            'FirewallPresenceRule', 'RedundantFirewallsRule', 'IDSIPSPresenceRule',
            'NetworkSegmentationRule', 'EncryptionRule', 'AuthenticationRule',
            'DMZConfigurationRule', 'AccessControlListsRule', 'AntiDDoSRule',
            'SecurityMonitoringRule', 'ZeroTrustPrinciplesRule'
        ],
        'compliance': [
            'ComplianceRequirementsRule', 'PCIDSSComplianceRule', 'HIPAAComplianceRule',
            'SOC2ComplianceRule', 'ISO27001ComplianceRule', 'GDPRComplianceRule',
            'NISTComplianceRule', 'FedRAMPComplianceRule', 'DataResidencyRule',
            'AuditTrailRule', 'ChangeManagementRule'
        ]
    }
    
    rule_names = category_map.get(category.lower(), [])
    loaded_count = 0
    
    for rule_class in ALL_RULES:
        if rule_class.__name__ in rule_names:
            try:
                rule = rule_class()
                registry.register(rule)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load rule {rule_class.__name__}: {e}")
    
    logger.info(f"Loaded {loaded_count} {category} rules")
    return loaded_count


def get_rule_summary() -> dict:
    """
    Get summary of all available rules
    
    Returns:
        Dictionary with rule counts by category
    """
    summary = {
        'total_rules': len(ALL_RULES),
        'by_category': {
            'capacity': 10,
            'topology': 11,
            'protocol': 10,
            'security': 11,
            'compliance': 11
        },
        'rule_list': [rule.__name__ for rule in ALL_RULES]
    }
    
    return summary


# Auto-load rules on module import
_auto_loaded = False

def ensure_rules_loaded():
    """Ensure rules are loaded into global registry"""
    global _auto_loaded
    if not _auto_loaded:
        load_all_rules()
        _auto_loaded = True
