from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class MCPIntegration(Base):
    """Model for MCP (Model Context Protocol) integrations"""
    __tablename__ = "mcp_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)  # e.g., "filesystem", "github", "git", "postgres"
    config = Column(JSON, nullable=True)  # Configuration for the MCP server
    enabled = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default="disconnected", nullable=False)  # connected, disconnected, error
    last_connected = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MCPIntegration(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"