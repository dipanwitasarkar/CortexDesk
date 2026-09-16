from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.database import get_async_db
from app.services.mcp_service import mcp_service
from app.models.mcp import MCPIntegration

router = APIRouter()


# Pydantic models for API
class MCPIntegrationCreate(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    description: Optional[str] = None


class MCPIntegrationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class MCPIntegrationResponse(BaseModel):
    id: int
    name: str
    type: str
    config: Dict[str, Any]
    enabled: bool
    status: str
    last_connected: Optional[str] = None
    last_error: Optional[str] = None
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/mcp/integrations", response_model=List[MCPIntegrationResponse])
async def list_integrations(
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """List all MCP integrations"""
    integrations = await mcp_service.list_integrations(db, enabled_only=enabled_only)
    return integrations


@router.get("/mcp/integrations/{integration_id}", response_model=MCPIntegrationResponse)
async def get_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific MCP integration"""
    integration = await mcp_service.get_integration(db, integration_id)
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP integration not found"
        )
    return integration


@router.post("/mcp/integrations", response_model=MCPIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration: MCPIntegrationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new MCP integration"""
    try:
        new_integration = await mcp_service.create_integration(
            db=db,
            name=integration.name,
            type=integration.type,
            config=integration.config,
            description=integration.description
        )
        return new_integration
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/mcp/integrations/{integration_id}", response_model=MCPIntegrationResponse)
async def update_integration(
    integration_id: int,
    integration: MCPIntegrationUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing MCP integration"""
    try:
        updated_integration = await mcp_service.update_integration(
            db=db,
            integration_id=integration_id,
            name=integration.name,
            type=integration.type,
            config=integration.config,
            enabled=integration.enabled,
            description=integration.description
        )
        if not updated_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCP integration not found"
            )
        return updated_integration
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/mcp/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete an MCP integration"""
    success = await mcp_service.delete_integration(db, integration_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP integration not found"
        )
    return {"message": "MCP integration deleted successfully"}


@router.post("/mcp/integrations/{integration_id}/test")
async def test_connection(
    integration_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Test connection to an MCP integration"""
    result = await mcp_service.test_connection(db, integration_id)
    if not result["success"] and "Integration not found" in result.get("error", ""):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP integration not found"
        )
    return result


@router.get("/mcp/types")
async def get_available_types():
    """Get available MCP integration types"""
    return await mcp_service.get_available_types()