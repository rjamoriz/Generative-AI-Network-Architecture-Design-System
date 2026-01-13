"""
API Endpoint Integration Tests
Tests all major API endpoints for deployment readiness
"""
import pytest
import asyncio
from httpx import AsyncClient
from typing import Dict, Any


class TestDesignEndpoints:
    """Test design-related endpoints"""
    
    @pytest.mark.asyncio
    async def test_analyze_requirements(self, client: AsyncClient):
        """Test requirements analysis endpoint"""
        payload = {
            "project_name": "Test Network",
            "description": "Test network for integration testing",
            "network_type": "enterprise",
            "expected_users": 500,
            "bandwidth_requirements": "1Gbps",
            "security_requirements": ["firewall", "encryption"],
            "compliance_frameworks": ["PCI-DSS"]
        }
        
        response = await client.post("/api/v1/design/analyze", json=payload)
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "analysis" in data
            assert "recommendations" in data
    
    @pytest.mark.asyncio
    async def test_generate_design(self, client: AsyncClient):
        """Test design generation endpoint"""
        payload = {
            "requirements": {
                "project_name": "Test Network",
                "description": "Test network",
                "network_type": "enterprise",
                "expected_users": 500,
                "bandwidth_requirements": "1Gbps"
            },
            "use_historical_context": False
        }
        
        response = await client.post("/api/v1/design/generate", json=payload)
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "design" in data
            assert "design_id" in data["design"]


class TestValidationEndpoints:
    """Test validation endpoints"""
    
    @pytest.mark.asyncio
    async def test_validate_design(self, client: AsyncClient):
        """Test design validation endpoint"""
        payload = {
            "design": {
                "design_id": "test-123",
                "name": "Test Design",
                "description": "Test",
                "network_type": "enterprise",
                "topology": {
                    "topology_type": "hierarchical",
                    "layers": []
                },
                "components": [],
                "connections": []
            },
            "mode": "deterministic",
            "categories": ["capacity", "security"]
        }
        
        response = await client.post("/api/v1/validation/validate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "validation_id" in data
        assert "issues" in data
        assert "summary" in data


class TestAdminEndpoints:
    """Test admin endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_rules(self, client: AsyncClient):
        """Test get validation rules endpoint"""
        response = await client.get("/api/v1/admin/rules")
        assert response.status_code == 200
        
        data = response.json()
        assert "rules" in data
        assert "total_count" in data
        assert data["total_count"] > 0
    
    @pytest.mark.asyncio
    async def test_get_rule_by_id(self, client: AsyncClient):
        """Test get specific rule endpoint"""
        # First get all rules
        response = await client.get("/api/v1/admin/rules")
        rules = response.json()["rules"]
        
        if rules:
            rule_id = rules[0]["rule_id"]
            response = await client.get(f"/api/v1/admin/rules/{rule_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["rule_id"] == rule_id


class TestMetricsEndpoints:
    """Test metrics and monitoring endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test detailed health check"""
        response = await client.get("/api/v1/metrics/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
    
    @pytest.mark.asyncio
    async def test_system_metrics(self, client: AsyncClient):
        """Test system metrics endpoint"""
        response = await client.get("/api/v1/metrics/system")
        assert response.status_code == 200
        
        data = response.json()
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
    
    @pytest.mark.asyncio
    async def test_prometheus_metrics(self, client: AsyncClient):
        """Test Prometheus metrics endpoint"""
        response = await client.get("/api/v1/metrics/prometheus")
        assert response.status_code == 200
        
        # Prometheus format is plain text
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        text = response.text
        assert "http_requests_total" in text


class TestHistoricalEndpoints:
    """Test historical data endpoints"""
    
    @pytest.mark.asyncio
    async def test_query_similar_designs(self, client: AsyncClient):
        """Test similar designs query"""
        payload = {
            "requirements": {
                "network_type": "enterprise",
                "expected_users": 500
            },
            "limit": 5
        }
        
        response = await client.post("/api/v1/historical/query/similar-designs", json=payload)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "designs" in data
            assert isinstance(data["designs"], list)


class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, client: AsyncClient):
        """Test 404 for invalid endpoint"""
        response = await client.get("/api/v1/invalid/endpoint")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_payload(self, client: AsyncClient):
        """Test 422 for invalid payload"""
        response = await client.post("/api/v1/design/analyze", json={"invalid": "data"})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient):
        """Test validation of required fields"""
        response = await client.post("/api/v1/design/analyze", json={})
        assert response.status_code == 422


@pytest.fixture
async def client():
    """Create test client"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
