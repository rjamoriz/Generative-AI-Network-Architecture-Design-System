"""
Example Workflow Script
Demonstrates common usage patterns for the Network Design System
"""
import asyncio
import httpx
from typing import Dict, Any


# API Base URL
BASE_URL = "http://localhost:8000/api/v1"


async def example_workflow():
    """
    Complete workflow example: Requirements -> Design -> Validation
    """
    print("=" * 80)
    print("Network Architecture Design System - Example Workflow")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Step 1: Analyze Requirements
        print("\n[Step 1] Analyzing Requirements...")
        requirements = {
            "project_name": "Enterprise Datacenter Network",
            "description": "High-availability datacenter for 500 devices",
            "network_type": "enterprise_datacenter",
            "scale": {
                "devices": 500,
                "users": 2000,
                "sites": 2
            },
            "bandwidth": {
                "min": "10Gbps",
                "max": "100Gbps"
            },
            "redundancy": "high",
            "security_level": "enterprise",
            "compliance": ["PCI-DSS", "SOC2"],
            "topology_preference": "spine_leaf",
            "budget": 500000.0,
            "deployment_timeline": "6 months"
        }
        
        response = await client.post(
            f"{BASE_URL}/design/analyze",
            json=requirements
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"✓ Requirements analyzed")
            print(f"  - Feasible: {analysis['is_feasible']}")
            print(f"  - Confidence: {analysis['confidence_score']:.2f}")
            print(f"  - Key Requirements: {len(analysis['key_requirements'])}")
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            return
        
        # Step 2: Generate Design
        print("\n[Step 2] Generating Network Design...")
        response = await client.post(
            f"{BASE_URL}/design/generate",
            json=requirements,
            params={"use_rag": True, "use_historical": False}
        )
        
        if response.status_code == 200:
            design = response.json()
            print(f"✓ Design generated")
            print(f"  - Design ID: {design['design_id']}")
            print(f"  - Components: {len(design['components'])}")
            print(f"  - Connections: {len(design['connections'])}")
            print(f"  - Topology: {design['topology']['topology_type']}")
        else:
            print(f"✗ Design generation failed: {response.status_code}")
            return
        
        design_id = design['design_id']
        
        # Step 3: Validate Design
        print("\n[Step 3] Validating Design...")
        response = await client.post(
            f"{BASE_URL}/validation/validate",
            json=design,
            params={"mode": "standard"}
        )
        
        if response.status_code == 200:
            validation = response.json()
            print(f"✓ Validation complete")
            print(f"  - Overall Score: {validation['overall_score']:.2f}")
            print(f"  - Passed: {validation['passed']}")
            print(f"  - Critical Issues: {validation['critical_count']}")
            print(f"  - Errors: {validation['error_count']}")
            print(f"  - Warnings: {validation['warning_count']}")
            
            if validation['issues']:
                print(f"\n  Top Issues:")
                for issue in validation['issues'][:3]:
                    print(f"    - [{issue['severity']}] {issue['message']}")
        else:
            print(f"✗ Validation failed: {response.status_code}")
            return
        
        # Step 4: Get System Metrics
        print("\n[Step 4] Checking System Status...")
        response = await client.get(f"{BASE_URL}/admin/health/detailed")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✓ System Status: {health['status']}")
            print(f"  - Validation Rules: {health['components']['validation_engine']['total_rules']}")
            print(f"  - Uptime: {health['uptime_seconds']}s")
        
        print("\n" + "=" * 80)
        print("Workflow Complete!")
        print("=" * 80)


async def example_historical_workflow():
    """
    Workflow using historical data
    """
    print("\n" + "=" * 80)
    print("Historical Data Workflow Example")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Step 1: Connect to Historical Database
        print("\n[Step 1] Connecting to Historical Database...")
        # Note: This requires actual database credentials
        print("  (Skipped - requires database configuration)")
        
        # Step 2: Query Similar Designs
        print("\n[Step 2] Querying Similar Historical Designs...")
        print("  (Skipped - requires database connection)")
        
        # Step 3: Analyze Patterns
        print("\n[Step 3] Analyzing Design Patterns...")
        print("  (Skipped - requires database connection)")
        
        # Step 4: Generate with Historical Context
        print("\n[Step 4] Generating Design with Historical Context...")
        print("  (Skipped - requires database connection)")
        
        print("\n" + "=" * 80)
        print("Historical workflow requires database configuration")
        print("See HISTORICAL_DATA_INTEGRATION.md for setup instructions")
        print("=" * 80)


async def example_admin_workflow():
    """
    Administrative operations workflow
    """
    print("\n" + "=" * 80)
    print("Admin Operations Workflow Example")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Get rule statistics
        print("\n[Step 1] Getting Rule Statistics...")
        response = await client.get(f"{BASE_URL}/admin/rules/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Rule Statistics:")
            print(f"  - Total Rules: {stats['total_rules']}")
            print(f"  - Enabled: {stats['enabled_rules']}")
            print(f"  - Categories: {len(stats['categories'])}")
        
        # List rules by category
        print("\n[Step 2] Listing Security Rules...")
        response = await client.get(
            f"{BASE_URL}/admin/rules",
            params={"category": "security"}
        )
        
        if response.status_code == 200:
            rules = response.json()
            print(f"✓ Found {len(rules)} security rules")
            for rule in rules[:3]:
                print(f"  - {rule['name']} ({rule['severity']})")
        
        # Get system metrics
        print("\n[Step 3] Getting System Metrics...")
        response = await client.get(f"{BASE_URL}/metrics/application")
        
        if response.status_code == 200:
            metrics = response.json()
            print(f"✓ Application Metrics:")
            print(f"  - Uptime: {metrics['uptime']['hours']}h {metrics['uptime']['minutes'] % 60}m")
            print(f"  - Total Requests: {metrics['api']['total_requests']}")
            print(f"  - Success Rate: {metrics['api']['success_rate']:.2%}")
        
        print("\n" + "=" * 80)
        print("Admin Workflow Complete!")
        print("=" * 80)


def main():
    """Run example workflows"""
    print("\nNetwork Architecture Design System - Example Workflows\n")
    print("Available workflows:")
    print("1. Complete Design Workflow (Requirements -> Design -> Validation)")
    print("2. Historical Data Workflow (requires database setup)")
    print("3. Admin Operations Workflow")
    print("\nNote: Ensure the API server is running at http://localhost:8000")
    print("\nRunning Complete Design Workflow...\n")
    
    # Run the main workflow
    asyncio.run(example_workflow())
    
    # Optionally run admin workflow
    print("\n\nRunning Admin Workflow...\n")
    asyncio.run(example_admin_workflow())


if __name__ == "__main__":
    main()
