"""
MCP (Model Context Protocol) Client
Generic client for connecting to external APIs and databases via MCP servers
Handles authentication and credential injection without hardcoding
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging
import httpx
from enum import Enum

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MCPServerType(str, Enum):
    """Types of MCP servers"""
    LEGACY_DATABASE = "legacy_database"
    WEB_APPLICATION = "web_application"
    DATA_BRIDGE = "data_bridge"


class BaseMCPClient(ABC):
    """
    Abstract base class for MCP clients
    All MCP clients should inherit from this and implement the abstract methods
    """
    
    def __init__(self, 
                 base_url: str,
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Initialize MCP client
        
        Args:
            base_url: Base URL of the MCP server
            api_key: API key for authentication (injected at runtime)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        if not base_url:
            raise ValueError("base_url is required")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_headers()
        )
        
        logger.info(f"Initialized {self.__class__.__name__} for {base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers including authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Network-Design-AI/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _request(self, 
                      method: str,
                      endpoint: str,
                      **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
        
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        pass
    
    @abstractmethod
    async def fetch_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch data from MCP server"""
        pass
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        logger.info(f"{self.__class__.__name__} client closed")


class LegacyDatabaseMCPClient(BaseMCPClient):
    """
    MCP client for legacy database connections
    Connects to Oracle/PostgreSQL databases containing historical network designs
    """
    
    async def health_check(self) -> bool:
        """Check if legacy database MCP server is healthy"""
        try:
            response = await self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Legacy DB health check failed: {e}")
            return False
    
    async def fetch_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch network designs from legacy database
        
        Args:
            query: Query parameters (e.g., filters, pagination)
        
        Returns:
            List of network design records
        """
        try:
            response = await self._request("POST", "/query", json=query)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch data from legacy DB: {e}")
            raise
    
    async def get_design_by_id(self, design_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific network design by ID
        
        Args:
            design_id: Design identifier
        
        Returns:
            Design data or None if not found
        """
        try:
            response = await self._request("GET", f"/designs/{design_id}")
            return response.get("design")
        except Exception as e:
            logger.error(f"Failed to get design {design_id}: {e}")
            return None
    
    async def search_designs(self, 
                           network_type: Optional[str] = None,
                           topology: Optional[str] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for network designs with filters
        
        Args:
            network_type: Filter by network type
            topology: Filter by topology type
            limit: Maximum number of results
        
        Returns:
            List of matching designs
        """
        query = {
            "filters": {},
            "limit": limit
        }
        
        if network_type:
            query["filters"]["network_type"] = network_type
        if topology:
            query["filters"]["topology"] = topology
        
        return await self.fetch_data(query)


class WebApplicationMCPClient(BaseMCPClient):
    """
    MCP client for web application integrations
    Connects to enterprise web applications via REST APIs
    """
    
    async def health_check(self) -> bool:
        """Check if web application MCP server is healthy"""
        try:
            response = await self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Web app health check failed: {e}")
            return False
    
    async def fetch_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data from web application
        
        Args:
            query: Query parameters
        
        Returns:
            List of records
        """
        try:
            response = await self._request("POST", "/api/data", json=query)
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Failed to fetch data from web app: {e}")
            raise
    
    async def get_validated_designs(self, 
                                   status: str = "approved",
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get validated network designs from web application
        
        Args:
            status: Design status filter
            limit: Maximum number of results
        
        Returns:
            List of validated designs
        """
        query = {
            "endpoint": "designs",
            "filters": {"status": status},
            "limit": limit
        }
        
        return await self.fetch_data(query)
    
    async def submit_design_for_review(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a design for review in the web application
        
        Args:
            design: Design data to submit
        
        Returns:
            Submission response
        """
        try:
            response = await self._request("POST", "/api/designs/submit", json=design)
            return response
        except Exception as e:
            logger.error(f"Failed to submit design: {e}")
            raise


class DataBridgeMCPClient(BaseMCPClient):
    """
    MCP client for data bridge
    Aggregates and normalizes data from multiple sources
    """
    
    async def health_check(self) -> bool:
        """Check if data bridge MCP server is healthy"""
        try:
            response = await self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Data bridge health check failed: {e}")
            return False
    
    async def fetch_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch aggregated data from multiple sources
        
        Args:
            query: Query parameters
        
        Returns:
            List of aggregated records
        """
        try:
            response = await self._request("POST", "/aggregate", json=query)
            return response.get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch aggregated data: {e}")
            raise
    
    async def aggregate_designs(self, 
                               sources: List[str],
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Aggregate designs from multiple sources
        
        Args:
            sources: List of data sources to query
            filters: Optional filters to apply
        
        Returns:
            List of aggregated and normalized designs
        """
        query = {
            "sources": sources,
            "filters": filters or {},
            "normalize": True,
            "deduplicate": True
        }
        
        return await self.fetch_data(query)


class MCPClientManager:
    """
    Manages multiple MCP clients with credential injection
    Provides unified interface for all external data sources
    """
    
    def __init__(self):
        """Initialize MCP client manager"""
        self.settings = get_settings()
        self.clients: Dict[MCPServerType, BaseMCPClient] = {}
        
        self._initialize_clients()
        
        logger.info("MCP Client Manager initialized")
    
    def _initialize_clients(self):
        """Initialize MCP clients with credentials from config"""
        
        # Legacy Database MCP Client
        if self.settings.mcp_legacy_db_url:
            try:
                self.clients[MCPServerType.LEGACY_DATABASE] = LegacyDatabaseMCPClient(
                    base_url=self.settings.mcp_legacy_db_url,
                    api_key=self.settings.mcp_legacy_db_api_key,
                    timeout=self.settings.mcp_timeout,
                    max_retries=self.settings.mcp_max_retries
                )
                logger.info("Legacy Database MCP client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Legacy DB MCP client: {e}")
        
        # Web Application MCP Client
        if self.settings.mcp_web_app_url:
            try:
                self.clients[MCPServerType.WEB_APPLICATION] = WebApplicationMCPClient(
                    base_url=self.settings.mcp_web_app_url,
                    api_key=self.settings.mcp_web_app_api_key,
                    timeout=self.settings.mcp_timeout,
                    max_retries=self.settings.mcp_max_retries
                )
                logger.info("Web Application MCP client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Web App MCP client: {e}")
    
    def get_client(self, server_type: MCPServerType) -> BaseMCPClient:
        """
        Get MCP client for specified server type
        
        Args:
            server_type: Type of MCP server
        
        Returns:
            MCP client instance
        """
        if server_type not in self.clients:
            raise ValueError(f"MCP client for {server_type} not configured")
        
        return self.clients[server_type]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all configured MCP servers
        
        Returns:
            Dictionary mapping server types to health status
        """
        results = {}
        
        for server_type, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                results[server_type] = is_healthy
                logger.info(f"{server_type}: {'✓ healthy' if is_healthy else '✗ unhealthy'}")
            except Exception as e:
                logger.error(f"{server_type} health check error: {e}")
                results[server_type] = False
        
        return results
    
    async def close_all(self):
        """Close all MCP clients"""
        for server_type, client in self.clients.items():
            try:
                await client.close()
                logger.info(f"Closed {server_type} client")
            except Exception as e:
                logger.error(f"Error closing {server_type} client: {e}")


# Global MCP client manager instance
_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """Get global MCP client manager instance"""
    global _mcp_manager
    
    if _mcp_manager is None:
        _mcp_manager = MCPClientManager()
    
    return _mcp_manager


# Dependency injection for FastAPI
def get_legacy_db_client() -> LegacyDatabaseMCPClient:
    """Get legacy database MCP client for dependency injection"""
    manager = get_mcp_manager()
    return manager.get_client(MCPServerType.LEGACY_DATABASE)


def get_web_app_client() -> WebApplicationMCPClient:
    """Get web application MCP client for dependency injection"""
    manager = get_mcp_manager()
    return manager.get_client(MCPServerType.WEB_APPLICATION)
