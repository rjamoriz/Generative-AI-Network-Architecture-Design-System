"""
Validation Rules Package
All validation rules organized by category
"""
from app.validation.rules.capacity_rules import (
    MinimumComponentsRule,
    MinimumConnectionsRule,
    BandwidthCapacityRule,
    ScaleRequirementsRule,
    ComponentQuantityRule,
    DeviceToComponentRatioRule,
    ConnectionDensityRule,
    RedundantComponentsRule,
    SiteDistributionRule,
    OversubscriptionRule,
)

from app.validation.rules.topology_rules import (
    NoSinglePointOfFailureRule,
    RedundantPathsRule,
    TopologyLayersRule,
    ConnectedComponentsRule,
    LoopPreventionRule,
    CoreRedundancyRule,
    SpineLeafRatioRule,
    MeshFullConnectivityRule,
    HierarchicalStructureRule,
    SymmetricDesignRule,
    EastWestTrafficRule,
)

from app.validation.rules.protocol_rules import (
    ValidConnectionTypesRule,
    BandwidthConsistencyRule,
    VLANConfigurationRule,
    RoutingProtocolRule,
    InterfaceNamingRule,
    QoSConfigurationRule,
    MulticastSupportRule,
    IPv6SupportRule,
    LinkAggregationRule,
    JumboFramesRule,
)

from app.validation.rules.security_rules import (
    FirewallPresenceRule,
    RedundantFirewallsRule,
    IDSIPSPresenceRule,
    NetworkSegmentationRule,
    EncryptionRule,
    AuthenticationRule,
    DMZConfigurationRule,
    AccessControlListsRule,
    AntiDDoSRule,
    SecurityMonitoringRule,
    ZeroTrustPrinciplesRule,
)

from app.validation.rules.compliance_rules import (
    ComplianceRequirementsRule,
    PCIDSSComplianceRule,
    HIPAAComplianceRule,
    SOC2ComplianceRule,
    ISO27001ComplianceRule,
    GDPRComplianceRule,
    NISTComplianceRule,
    FedRAMPComplianceRule,
    DataResidencyRule,
    AuditTrailRule,
    ChangeManagementRule,
)

# All rule classes
ALL_RULES = [
    # Capacity Rules (10)
    MinimumComponentsRule,
    MinimumConnectionsRule,
    BandwidthCapacityRule,
    ScaleRequirementsRule,
    ComponentQuantityRule,
    DeviceToComponentRatioRule,
    ConnectionDensityRule,
    RedundantComponentsRule,
    SiteDistributionRule,
    OversubscriptionRule,
    
    # Topology Rules (11)
    NoSinglePointOfFailureRule,
    RedundantPathsRule,
    TopologyLayersRule,
    ConnectedComponentsRule,
    LoopPreventionRule,
    CoreRedundancyRule,
    SpineLeafRatioRule,
    MeshFullConnectivityRule,
    HierarchicalStructureRule,
    SymmetricDesignRule,
    EastWestTrafficRule,
    
    # Protocol Rules (10)
    ValidConnectionTypesRule,
    BandwidthConsistencyRule,
    VLANConfigurationRule,
    RoutingProtocolRule,
    InterfaceNamingRule,
    QoSConfigurationRule,
    MulticastSupportRule,
    IPv6SupportRule,
    LinkAggregationRule,
    JumboFramesRule,
    
    # Security Rules (11)
    FirewallPresenceRule,
    RedundantFirewallsRule,
    IDSIPSPresenceRule,
    NetworkSegmentationRule,
    EncryptionRule,
    AuthenticationRule,
    DMZConfigurationRule,
    AccessControlListsRule,
    AntiDDoSRule,
    SecurityMonitoringRule,
    ZeroTrustPrinciplesRule,
    
    # Compliance Rules (11)
    ComplianceRequirementsRule,
    PCIDSSComplianceRule,
    HIPAAComplianceRule,
    SOC2ComplianceRule,
    ISO27001ComplianceRule,
    GDPRComplianceRule,
    NISTComplianceRule,
    FedRAMPComplianceRule,
    DataResidencyRule,
    AuditTrailRule,
    ChangeManagementRule,
]

__all__ = [
    "ALL_RULES",
    # Capacity
    "MinimumComponentsRule",
    "MinimumConnectionsRule",
    "BandwidthCapacityRule",
    "ScaleRequirementsRule",
    "ComponentQuantityRule",
    "DeviceToComponentRatioRule",
    "ConnectionDensityRule",
    "RedundantComponentsRule",
    "SiteDistributionRule",
    "OversubscriptionRule",
    # Topology
    "NoSinglePointOfFailureRule",
    "RedundantPathsRule",
    "TopologyLayersRule",
    "ConnectedComponentsRule",
    "LoopPreventionRule",
    "CoreRedundancyRule",
    "SpineLeafRatioRule",
    "MeshFullConnectivityRule",
    "HierarchicalStructureRule",
    "SymmetricDesignRule",
    "EastWestTrafficRule",
    # Protocol
    "ValidConnectionTypesRule",
    "BandwidthConsistencyRule",
    "VLANConfigurationRule",
    "RoutingProtocolRule",
    "InterfaceNamingRule",
    "QoSConfigurationRule",
    "MulticastSupportRule",
    "IPv6SupportRule",
    "LinkAggregationRule",
    "JumboFramesRule",
    # Security
    "FirewallPresenceRule",
    "RedundantFirewallsRule",
    "IDSIPSPresenceRule",
    "NetworkSegmentationRule",
    "EncryptionRule",
    "AuthenticationRule",
    "DMZConfigurationRule",
    "AccessControlListsRule",
    "AntiDDoSRule",
    "SecurityMonitoringRule",
    "ZeroTrustPrinciplesRule",
    # Compliance
    "ComplianceRequirementsRule",
    "PCIDSSComplianceRule",
    "HIPAAComplianceRule",
    "SOC2ComplianceRule",
    "ISO27001ComplianceRule",
    "GDPRComplianceRule",
    "NISTComplianceRule",
    "FedRAMPComplianceRule",
    "DataResidencyRule",
    "AuditTrailRule",
    "ChangeManagementRule",
]
