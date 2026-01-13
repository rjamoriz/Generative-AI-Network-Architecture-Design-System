"""
Comprehensive Health Check Script
Run before and after deployment to verify system health
"""
import asyncio
import sys
import httpx
from typing import Dict, List, Tuple
from datetime import datetime


class HealthChecker:
    """Comprehensive health check for the application"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
        self.passed = 0
        self.failed = 0
    
    async def check_endpoint(self, method: str, path: str, expected_status: int = 200, 
                           payload: Dict = None, timeout: int = 30) -> Tuple[bool, str]:
        """Check a single endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json=payload)
                else:
                    return False, f"Unsupported method: {method}"
                
                if response.status_code == expected_status:
                    return True, f"✓ {method} {path} -> {response.status_code}"
                else:
                    return False, f"✗ {method} {path} -> {response.status_code} (expected {expected_status})"
        
        except httpx.ConnectError:
            return False, f"✗ {method} {path} -> Connection refused (is server running?)"
        except httpx.TimeoutException:
            return False, f"✗ {method} {path} -> Timeout after {timeout}s"
        except Exception as e:
            return False, f"✗ {method} {path} -> Error: {str(e)}"
    
    async def check_basic_health(self) -> bool:
        """Check basic health endpoint"""
        print("\n=== Basic Health Check ===")
        success, message = await self.check_endpoint("GET", "/health")
        print(message)
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        return success
    
    async def check_detailed_health(self) -> bool:
        """Check detailed health endpoint"""
        print("\n=== Detailed Health Check ===")
        success, message = await self.check_endpoint("GET", "/api/v1/metrics/health/detailed")
        print(message)
        
        if success:
            self.passed += 1
            
            # Get details
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.base_url}/api/v1/metrics/health/detailed")
                    data = response.json()
                    
                    print(f"  Status: {data.get('status')}")
                    print(f"  Services:")
                    for service, status in data.get('services', {}).items():
                        print(f"    - {service}: {status}")
            except:
                pass
        else:
            self.failed += 1
        
        return success
    
    async def check_api_documentation(self) -> bool:
        """Check API documentation endpoints"""
        print("\n=== API Documentation ===")
        
        endpoints = [
            ("GET", "/docs", 200),
            ("GET", "/redoc", 200),
            ("GET", "/openapi.json", 200),
        ]
        
        all_passed = True
        for method, path, expected in endpoints:
            success, message = await self.check_endpoint(method, path, expected)
            print(message)
            
            if success:
                self.passed += 1
            else:
                self.failed += 1
                all_passed = False
        
        return all_passed
    
    async def check_admin_endpoints(self) -> bool:
        """Check admin endpoints"""
        print("\n=== Admin Endpoints ===")
        
        endpoints = [
            ("GET", "/api/v1/admin/rules", 200),
            ("GET", "/api/v1/admin/statistics", 200),
        ]
        
        all_passed = True
        for method, path, expected in endpoints:
            success, message = await self.check_endpoint(method, path, expected)
            print(message)
            
            if success:
                self.passed += 1
            else:
                self.failed += 1
                all_passed = False
        
        return all_passed
    
    async def check_metrics_endpoints(self) -> bool:
        """Check metrics endpoints"""
        print("\n=== Metrics Endpoints ===")
        
        endpoints = [
            ("GET", "/api/v1/metrics/system", 200),
            ("GET", "/api/v1/metrics/application", 200),
            ("GET", "/api/v1/metrics/prometheus", 200),
        ]
        
        all_passed = True
        for method, path, expected in endpoints:
            success, message = await self.check_endpoint(method, path, expected)
            print(message)
            
            if success:
                self.passed += 1
            else:
                self.failed += 1
                all_passed = False
        
        return all_passed
    
    async def check_design_endpoints(self) -> bool:
        """Check design endpoints (basic connectivity)"""
        print("\n=== Design Endpoints (Connectivity) ===")
        
        # Just check if endpoints are reachable (may return 422 for invalid payload)
        endpoints = [
            ("POST", "/api/v1/design/analyze", 422),  # Will fail validation but endpoint exists
            ("POST", "/api/v1/design/generate", 422),
        ]
        
        all_passed = True
        for method, path, expected in endpoints:
            success, message = await self.check_endpoint(method, path, expected, payload={})
            print(message)
            
            if success:
                self.passed += 1
            else:
                self.failed += 1
                all_passed = False
        
        return all_passed
    
    async def check_validation_endpoints(self) -> bool:
        """Check validation endpoints"""
        print("\n=== Validation Endpoints (Connectivity) ===")
        
        success, message = await self.check_endpoint("POST", "/api/v1/validation/validate", 422, payload={})
        print(message)
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
        
        return success
    
    async def run_all_checks(self) -> bool:
        """Run all health checks"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE HEALTH CHECK")
        print(f"Target: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run checks
        checks = [
            ("Basic Health", self.check_basic_health),
            ("Detailed Health", self.check_detailed_health),
            ("API Documentation", self.check_api_documentation),
            ("Admin Endpoints", self.check_admin_endpoints),
            ("Metrics Endpoints", self.check_metrics_endpoints),
            ("Design Endpoints", self.check_design_endpoints),
            ("Validation Endpoints", self.check_validation_endpoints),
        ]
        
        for check_name, check_func in checks:
            try:
                await check_func()
            except Exception as e:
                print(f"\n✗ {check_name} failed with exception: {e}")
                self.failed += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n✓ ALL CHECKS PASSED - System is healthy!")
            print("=" * 80 + "\n")
            return True
        else:
            print(f"\n✗ {self.failed} CHECKS FAILED - System needs attention!")
            print("=" * 80 + "\n")
            return False


async def main():
    """Main health check function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Health check for Network Design System")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    args = parser.parse_args()
    
    checker = HealthChecker(base_url=args.url)
    success = await checker.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
