"""
Nango API service for authentication and proxy requests
"""
import httpx
from typing import Any, Dict, Optional
from config import get_settings

settings = get_settings()


class NangoService:
    """Service for interacting with Nango API"""
    
    def __init__(self):
        self.base_url = settings.nango_host.rstrip("/")
        self.secret_key = settings.nango_secret_key
        self.provider_key = settings.nango_jira_provider_key
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Nango API requests"""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
    
    async def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get connection details from Nango

        Args:
            connection_id: The connection identifier

        Returns:
            Connection details including credentials and config
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/connection/{connection_id}",
                    headers=self._get_headers(),
                    params={"provider_config_key": self.provider_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise
            except Exception:
                return None
    
    async def proxy_get(
        self, 
        connection_id: str, 
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request through Nango proxy
        
        Args:
            connection_id: The connection identifier
            endpoint: The API endpoint (e.g., /ex/jira/{cloudId}/rest/api/3/search)
            params: Query parameters
            
        Returns:
            API response data
        """
        headers = self._get_headers()
        headers["Connection-Id"] = connection_id
        headers["Provider-Config-Key"] = self.provider_key
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/proxy{endpoint}",
                headers=headers,
                params=params or {},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def proxy_post(
        self,
        connection_id: str,
        endpoint: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request through Nango proxy
        
        Args:
            connection_id: The connection identifier
            endpoint: The API endpoint
            data: Request body
            params: Query parameters
            
        Returns:
            API response data
        """
        headers = self._get_headers()
        headers["Connection-Id"] = connection_id
        headers["Provider-Config-Key"] = self.provider_key
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/proxy{endpoint}",
                headers=headers,
                json=data,
                params=params or {},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_cloud_id(self, connection_id: str) -> Optional[str]:
        """
        Get the Jira Cloud ID from connection configuration
        
        Args:
            connection_id: The connection identifier
            
        Returns:
            The Jira Cloud ID or None
        """
        connection = await self.get_connection(connection_id)
        if connection and "connection_config" in connection:
            return connection["connection_config"].get("cloudId")
        return None
    
    async def get_account_id(self, connection_id: str) -> Optional[str]:
        """
        Get the Jira Account ID from connection configuration
        
        Args:
            connection_id: The connection identifier
            
        Returns:
            The Jira Account ID or None
        """
        connection = await self.get_connection(connection_id)
        if connection and "connection_config" in connection:
            return connection["connection_config"].get("accountId")
        return None


# Singleton instance
nango_service = NangoService()
