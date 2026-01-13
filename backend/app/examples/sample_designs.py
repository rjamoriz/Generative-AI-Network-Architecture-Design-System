"""
Sample Network Designs
Example designs for testing and demonstration
"""
from datetime import datetime
from app.models.network_design import (
    NetworkDesign, NetworkType, TopologyType, DesignStatus,
    ComponentSpecification, Connection, TopologyDetails,
    BandwidthRequirement, ScaleRequirement, RedundancyLevel, SecurityLevel
)


def create_sample_enterprise_datacenter() -> NetworkDesign:
    """Create sample enterprise datacenter design"""
    
    # Topology
    topology = TopologyDetails(
        topology_type=TopologyType.SPINE_LEAF,
        layers=2,
        redundancy_level=RedundancyLevel.HIGH,
        has_single_point_of_failure=False,
        redundant_paths=2,
        description="Spine-leaf architecture with dual spine switches for high availability"
    )
    
    # Components
    components = [
        ComponentSpecification(
            component_id="spine_001",
            component_type="switch",
            name="Spine Switch 1",
            model="Cisco Nexus 9300",
            vendor="Cisco",
            quantity=1,
            specifications={
                "ports": 48,
                "port_speed": "100Gbps",
                "switching_capacity": "4.8Tbps"
            },
            location="Core",
            redundancy_group="spine"
        ),
        ComponentSpecification(
            component_id="spine_002",
            component_type="switch",
            name="Spine Switch 2",
            model="Cisco Nexus 9300",
            vendor="Cisco",
            quantity=1,
            specifications={
                "ports": 48,
                "port_speed": "100Gbps",
                "switching_capacity": "4.8Tbps"
            },
            location="Core",
            redundancy_group="spine"
        ),
        ComponentSpecification(
            component_id="leaf_001",
            component_type="switch",
            name="Leaf Switch 1",
            model="Cisco Nexus 9200",
            vendor="Cisco",
            quantity=1,
            specifications={
                "ports": 32,
                "port_speed": "25Gbps",
                "uplink_speed": "100Gbps"
            },
            location="Access",
            redundancy_group="leaf_rack1"
        ),
        ComponentSpecification(
            component_id="leaf_002",
            component_type="switch",
            name="Leaf Switch 2",
            model="Cisco Nexus 9200",
            vendor="Cisco",
            quantity=1,
            specifications={
                "ports": 32,
                "port_speed": "25Gbps",
                "uplink_speed": "100Gbps"
            },
            location="Access",
            redundancy_group="leaf_rack1"
        ),
        ComponentSpecification(
            component_id="fw_001",
            component_type="firewall",
            name="Firewall Cluster",
            model="Palo Alto PA-5220",
            vendor="Palo Alto Networks",
            quantity=2,
            specifications={
                "throughput": "63Gbps",
                "connections_per_second": "1.2M",
                "ha_mode": "active-active"
            },
            location="DMZ",
            redundancy_group="firewall"
        ),
        ComponentSpecification(
            component_id="lb_001",
            component_type="load_balancer",
            name="Load Balancer",
            model="F5 BIG-IP 4200v",
            vendor="F5 Networks",
            quantity=2,
            specifications={
                "throughput": "40Gbps",
                "ssl_tps": "50000",
                "ha_mode": "active-standby"
            },
            location="DMZ",
            redundancy_group="load_balancer"
        )
    ]
    
    # Connections
    connections = [
        Connection(
            connection_id="conn_001",
            source_component="Leaf Switch 1",
            source_interface="eth1/49",
            target_component="Spine Switch 1",
            target_interface="eth1/1",
            connection_type="fiber",
            bandwidth="100Gbps",
            protocol="LACP"
        ),
        Connection(
            connection_id="conn_002",
            source_component="Leaf Switch 1",
            source_interface="eth1/50",
            target_component="Spine Switch 2",
            target_interface="eth1/1",
            connection_type="fiber",
            bandwidth="100Gbps",
            protocol="LACP"
        ),
        Connection(
            connection_id="conn_003",
            source_component="Leaf Switch 2",
            source_interface="eth1/49",
            target_component="Spine Switch 1",
            target_interface="eth1/2",
            connection_type="fiber",
            bandwidth="100Gbps",
            protocol="LACP"
        ),
        Connection(
            connection_id="conn_004",
            source_component="Leaf Switch 2",
            source_interface="eth1/50",
            target_component="Spine Switch 2",
            target_interface="eth1/2",
            connection_type="fiber",
            bandwidth="100Gbps",
            protocol="LACP"
        ),
        Connection(
            connection_id="conn_005",
            source_component="Spine Switch 1",
            source_interface="eth1/47",
            target_component="Firewall Cluster",
            target_interface="eth1/1",
            connection_type="fiber",
            bandwidth="40Gbps",
            protocol="BGP",
            vlan=100
        )
    ]
    
    # Create design
    design = NetworkDesign(
        design_id="sample_enterprise_dc_001",
        name="Enterprise Datacenter - Spine-Leaf",
        description="High-availability enterprise datacenter with spine-leaf topology supporting 500 devices and 2000 users",
        network_type=NetworkType.ENTERPRISE_DATACENTER,
        status=DesignStatus.VALIDATED,
        topology=topology,
        components=components,
        connections=connections,
        bandwidth_requirement=BandwidthRequirement(min="10Gbps", max="100Gbps"),
        scale=ScaleRequirement(devices=500, users=2000, sites=2),
        security_level=SecurityLevel.ENTERPRISE,
        compliance_requirements=["PCI-DSS", "SOC2"],
        design_rationale="Spine-leaf architecture provides high bandwidth, low latency, and excellent scalability. Dual spine switches eliminate single points of failure. All critical components are redundant.",
        key_features=[
            "Dual spine switches for redundancy",
            "100Gbps uplinks between spine and leaf",
            "Active-active firewall cluster",
            "Load balancer with SSL offload",
            "LACP for link aggregation",
            "BGP routing for scalability"
        ],
        trade_offs="Higher initial cost for redundant components, but provides excellent reliability and performance",
        version="1.0",
        created_at=datetime.utcnow()
    )
    
    return design


def create_sample_campus_network() -> NetworkDesign:
    """Create sample campus network design"""
    
    topology = TopologyDetails(
        topology_type=TopologyType.THREE_TIER,
        layers=3,
        redundancy_level=RedundancyLevel.MEDIUM,
        has_single_point_of_failure=False,
        redundant_paths=1,
        description="Traditional three-tier campus network with core, distribution, and access layers"
    )
    
    components = [
        ComponentSpecification(
            component_id="core_001",
            component_type="router",
            name="Core Router 1",
            model="Cisco Catalyst 9600",
            vendor="Cisco",
            quantity=1,
            specifications={"ports": 24, "routing_capacity": "2Tbps"},
            location="Core",
            redundancy_group="core"
        ),
        ComponentSpecification(
            component_id="core_002",
            component_type="router",
            name="Core Router 2",
            model="Cisco Catalyst 9600",
            vendor="Cisco",
            quantity=1,
            specifications={"ports": 24, "routing_capacity": "2Tbps"},
            location="Core",
            redundancy_group="core"
        ),
        ComponentSpecification(
            component_id="dist_001",
            component_type="switch",
            name="Distribution Switch 1",
            model="Cisco Catalyst 9400",
            vendor="Cisco",
            quantity=2,
            specifications={"ports": 48, "port_speed": "10Gbps"},
            location="Distribution",
            redundancy_group="distribution"
        ),
        ComponentSpecification(
            component_id="access_001",
            component_type="switch",
            name="Access Switch",
            model="Cisco Catalyst 9300",
            vendor="Cisco",
            quantity=10,
            specifications={"ports": 48, "port_speed": "1Gbps", "poe": "PoE+"},
            location="Access"
        ),
        ComponentSpecification(
            component_id="fw_001",
            component_type="firewall",
            name="Edge Firewall",
            model="Fortinet FortiGate 600E",
            vendor="Fortinet",
            quantity=1,
            specifications={"throughput": "10Gbps"},
            location="Edge"
        )
    ]
    
    connections = [
        Connection(
            connection_id="conn_001",
            source_component="Core Router 1",
            source_interface="gi0/1",
            target_component="Core Router 2",
            target_interface="gi0/1",
            connection_type="fiber",
            bandwidth="10Gbps",
            protocol="OSPF"
        ),
        Connection(
            connection_id="conn_002",
            source_component="Core Router 1",
            source_interface="gi0/2",
            target_component="Distribution Switch 1",
            target_interface="te1/1",
            connection_type="fiber",
            bandwidth="10Gbps",
            protocol="OSPF",
            vlan=10
        ),
        Connection(
            connection_id="conn_003",
            source_component="Distribution Switch 1",
            source_interface="gi1/1",
            target_component="Access Switch",
            target_interface="gi0/48",
            connection_type="copper",
            bandwidth="1Gbps",
            vlan=100
        )
    ]
    
    design = NetworkDesign(
        design_id="sample_campus_001",
        name="Campus Network - Three-Tier",
        description="Traditional campus network supporting 1000 users across multiple buildings",
        network_type=NetworkType.CAMPUS,
        status=DesignStatus.VALIDATED,
        topology=topology,
        components=components,
        connections=connections,
        bandwidth_requirement=BandwidthRequirement(min="1Gbps", max="10Gbps"),
        scale=ScaleRequirement(devices=200, users=1000, sites=1),
        security_level=SecurityLevel.STANDARD,
        compliance_requirements=[],
        design_rationale="Three-tier design provides clear separation of concerns and scalability for campus environment",
        key_features=[
            "Redundant core routers",
            "Hierarchical design for scalability",
            "PoE+ for wireless access points",
            "OSPF for dynamic routing"
        ],
        version="1.0",
        created_at=datetime.utcnow()
    )
    
    return design


# Export sample designs
SAMPLE_DESIGNS = {
    "enterprise_datacenter": create_sample_enterprise_datacenter,
    "campus_network": create_sample_campus_network
}


def get_sample_design(design_type: str) -> NetworkDesign:
    """
    Get a sample design by type
    
    Args:
        design_type: Type of design (enterprise_datacenter, campus_network)
    
    Returns:
        Sample network design
    """
    if design_type not in SAMPLE_DESIGNS:
        raise ValueError(f"Unknown design type: {design_type}. Available: {list(SAMPLE_DESIGNS.keys())}")
    
    return SAMPLE_DESIGNS[design_type]()
