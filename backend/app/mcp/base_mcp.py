from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import asyncio
from app.core.config import settings


class BaseMCP(ABC):
    """Base class for all MCP integrations"""
    
    def __init__(self, name: str, endpoint: Optional[str] = None):
        self.name = name
        self.endpoint = endpoint
        self.timeout = settings.mcp_server_timeout
        self.max_retries = settings.mcp_max_retries

    @abstractmethod
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        pass

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server"""
        pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to MCP server"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    if method == "GET":
                        response = await client.get(endpoint, params=data)
                    elif method == "POST":
                        response = await client.post(endpoint, json=data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    response.raise_for_status()
                    return response.json()
                    
                except httpx.HTTPError as e:
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            if self.endpoint:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{self.endpoint}/health")
                    return response.status_code == 200
            return True  # For local MCP implementations
        except Exception:
            return False
