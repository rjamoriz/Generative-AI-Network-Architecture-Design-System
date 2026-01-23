"""
Salesforce Client
Fetches technical validation data from Salesforce
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging
import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SalesforceClient:
    """Minimal Salesforce REST API client"""

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=30)
        self._access_token: Optional[str] = self.settings.salesforce_access_token
        self._instance_url: Optional[str] = self.settings.salesforce_instance_url

        if not self.settings.salesforce_enabled:
            raise ValueError("Salesforce integration is disabled")

    async def authenticate(self) -> None:
        """Authenticate via OAuth password flow if token not provided"""
        if self._access_token and self._instance_url:
            return

        required = [
            self.settings.salesforce_client_id,
            self.settings.salesforce_client_secret,
            self.settings.salesforce_username,
            self.settings.salesforce_password,
        ]
        if not all(required):
            raise ValueError("Missing Salesforce OAuth credentials")

        password = self.settings.salesforce_password
        if self.settings.salesforce_security_token:
            password = f"{password}{self.settings.salesforce_security_token}"

        token_url = f"{self.settings.salesforce_login_url}/services/oauth2/token"
        payload = {
            "grant_type": "password",
            "client_id": self.settings.salesforce_client_id,
            "client_secret": self.settings.salesforce_client_secret,
            "username": self.settings.salesforce_username,
            "password": password,
        }

        response = await self.client.post(token_url, data=payload)
        response.raise_for_status()
        data = response.json()

        self._access_token = data.get("access_token")
        self._instance_url = data.get("instance_url")

        if not self._access_token or not self._instance_url:
            raise ValueError("Failed to acquire Salesforce access token")

        logger.info("Salesforce authentication successful")

    async def _headers(self) -> Dict[str, str]:
        await self.authenticate()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    async def query(self, soql: str) -> List[Dict[str, Any]]:
        """Run a SOQL query and return records"""
        headers = await self._headers()
        url = f"{self._instance_url}/services/data/{self.settings.salesforce_api_version}/query"
        response = await self.client.get(url, headers=headers, params={"q": soql})
        response.raise_for_status()
        data = response.json()
        return data.get("records", [])

    async def health_check(self) -> bool:
        """Check Salesforce connectivity"""
        try:
            await self.query("SELECT Id FROM User LIMIT 1")
            return True
        except Exception as exc:
            logger.error(f"Salesforce health check failed: {exc}")
            return False

    async def close(self) -> None:
        await self.client.aclose()


_salesforce_client: Optional[SalesforceClient] = None


def get_salesforce_client() -> SalesforceClient:
    global _salesforce_client
    if _salesforce_client is None:
        _salesforce_client = SalesforceClient()
    return _salesforce_client
