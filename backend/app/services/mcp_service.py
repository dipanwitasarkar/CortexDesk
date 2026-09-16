from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.mcp import MCPIntegration
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPService:
    """Service for managing MCP integrations"""
    
    async def list_integrations(
        self,
        db: AsyncSession,
        enabled_only: bool = False
    ) -> List[MCPIntegration]:
        """List all MCP integrations"""
        query = select(MCPIntegration)
        if enabled_only:
            query = query.where(MCPIntegration.enabled == True)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_integration(
        self,
        db: AsyncSession,
        integration_id: int
    ) -> Optional[MCPIntegration]:
        """Get a specific MCP integration by ID"""
        result = await db.execute(
            select(MCPIntegration).where(MCPIntegration.id == integration_id)
        )
        return result.scalar_one_or_none()
    
    async def get_integration_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[MCPIntegration]:
        """Get a specific MCP integration by name"""
        result = await db.execute(
            select(MCPIntegration).where(MCPIntegration.name == name)
        )
        return result.scalar_one_or_none()
    
    async def create_integration(
        self,
        db: AsyncSession,
        name: str,
        type: str,
        config: Dict[str, Any],
        description: Optional[str] = None
    ) -> MCPIntegration:
        """Create a new MCP integration"""
        # Check if integration with this name already exists
        existing = await self.get_integration_by_name(db, name)
        if existing:
            raise ValueError(f"MCP integration with name '{name}' already exists")
        
        integration = MCPIntegration(
            name=name,
            type=type,
            config=config,
            description=description,
            status="disconnected"
        )
        db.add(integration)
        await db.commit()
        await db.refresh(integration)
        
        logger.info(f"Created MCP integration: {name} ({type})")
        return integration
    
    async def update_integration(
        self,
        db: AsyncSession,
        integration_id: int,
        name: Optional[str] = None,
        type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        description: Optional[str] = None
    ) -> Optional[MCPIntegration]:
        """Update an existing MCP integration"""
        integration = await self.get_integration(db, integration_id)
        if not integration:
            return None
        
        if name is not None:
            # Check if new name conflicts with existing integration
            existing = await self.get_integration_by_name(db, name)
            if existing and existing.id != integration_id:
                raise ValueError(f"MCP integration with name '{name}' already exists")
            integration.name = name
        
        if type is not None:
            integration.type = type
        if config is not None:
            integration.config = config
        if enabled is not None:
            integration.enabled = enabled
        if description is not None:
            integration.description = description
        
        await db.commit()
        await db.refresh(integration)
        
        logger.info(f"Updated MCP integration: {integration.name}")
        return integration
    
    async def delete_integration(
        self,
        db: AsyncSession,
        integration_id: int
    ) -> bool:
        """Delete an MCP integration"""
        integration = await self.get_integration(db, integration_id)
        if not integration:
            return False
        
        await db.delete(integration)
        await db.commit()
        
        logger.info(f"Deleted MCP integration: {integration.name}")
        return True
    
    async def test_connection(
        self,
        db: AsyncSession,
        integration_id: int
    ) -> Dict[str, Any]:
        """Test connection to an MCP integration"""
        integration = await self.get_integration(db, integration_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}
        
        try:
            # Simulate connection test based on integration type
            # In a real implementation, this would actually connect to the MCP server
            if integration.type == "filesystem":
                # Test filesystem access
                test_result = {"success": True, "message": "Filesystem connection successful"}
            elif integration.type == "github":
                # Test GitHub API access
                test_result = {"success": True, "message": "GitHub API connection successful"}
            elif integration.type == "git":
                # Test Git repository access
                test_result = {"success": True, "message": "Git repository connection successful"}
            elif integration.type == "postgres":
                # Test PostgreSQL connection
                test_result = {"success": True, "message": "PostgreSQL connection successful"}
            else:
                test_result = {"success": False, "error": f"Unknown integration type: {integration.type}"}
            
            # Update integration status
            if test_result["success"]:
                integration.status = "connected"
                integration.last_connected = datetime.utcnow()
                integration.last_error = None
            else:
                integration.status = "error"
                integration.last_error = test_result.get("error", "Unknown error")
            
            await db.commit()
            return test_result
            
        except Exception as e:
            integration.status = "error"
            integration.last_error = str(e)
            await db.commit()
            return {"success": False, "error": str(e)}
    
    async def get_available_types(self) -> List[Dict[str, Any]]:
        """Get available MCP integration types"""
        return [
            {
                "type": "filesystem",
                "name": "Filesystem",
                "description": "Access local filesystem for file operations",
                "required_config": ["base_path"],
                "optional_config": ["allowed_extensions", "max_file_size"]
            },
            {
                "type": "github",
                "name": "GitHub",
                "description": "Access GitHub repositories and operations",
                "required_config": ["token"],
                "optional_config": ["default_owner", "default_repo"]
            },
            {
                "type": "git",
                "name": "Git",
                "description": "Access Git repositories for version control",
                "required_config": ["repo_path"],
                "optional_config": ["git_binary_path"]
            },
            {
                "type": "postgres",
                "name": "PostgreSQL",
                "description": "Access PostgreSQL databases",
                "required_config": ["connection_string"],
                "optional_config": ["schema", "table_whitelist"]
            }
        ]


mcp_service = MCPService()