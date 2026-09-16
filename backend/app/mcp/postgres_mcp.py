from app.mcp.base_mcp import BaseMCP
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from sqlalchemy import text
import json


class PostgreSQLMCP(BaseMCP):
    """PostgreSQL database operations via MCP"""
    
    def __init__(self):
        super().__init__("postgres")

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call PostgreSQL tools"""
        try:
            if tool_name == "execute_query":
                return await self._execute_query(parameters["query"], parameters.get("params"))
            elif tool_name == "get_table_info":
                return await self._get_table_info(parameters["table_name"])
            elif tool_name == "list_tables":
                return await self._list_tables()
            elif tool_name == "get_schema":
                return await self._get_schema()
            elif tool_name == "insert_record":
                return await self._insert_record(parameters["table"], parameters["data"])
            elif tool_name == "update_record":
                return await self._update_record(
                    parameters["table"],
                    parameters["record_id"],
                    parameters["data"]
                )
            elif tool_name == "delete_record":
                return await self._delete_record(parameters["table"], parameters["record_id"])
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available PostgreSQL tools"""
        return [
            {
                "name": "execute_query",
                "description": "Execute a SQL query",
                "parameters": {
                    "query": {"type": "string", "description": "SQL query"},
                    "params": {"type": "object", "description": "Query parameters (optional)"}
                }
            },
            {
                "name": "get_table_info",
                "description": "Get information about a table",
                "parameters": {
                    "table_name": {"type": "string", "description": "Table name"}
                }
            },
            {
                "name": "list_tables",
                "description": "List all tables in the database",
                "parameters": {}
            },
            {
                "name": "get_schema",
                "description": "Get database schema information",
                "parameters": {}
            },
            {
                "name": "insert_record",
                "description": "Insert a record into a table",
                "parameters": {
                    "table": {"type": "string", "description": "Table name"},
                    "data": {"type": "object", "description": "Record data"}
                }
            },
            {
                "name": "update_record",
                "description": "Update a record in a table",
                "parameters": {
                    "table": {"type": "string", "description": "Table name"},
                    "record_id": {"type": "integer", "description": "Record ID"},
                    "data": {"type": "object", "description": "Updated data"}
                }
            },
            {
                "name": "delete_record",
                "description": "Delete a record from a table",
                "parameters": {
                    "table": {"type": "string", "description": "Table name"},
                    "record_id": {"type": "integer", "description": "Record ID"}
                }
            }
        ]

    async def _execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a SQL query"""
        async for db in get_async_db():
            try:
                # Security check - prevent dangerous operations
                if not self._is_query_safe(query):
                    return {"error": "Query not allowed for security reasons"}
                
                result = await db.execute(text(query), params or {})
                await db.commit()
                
                # Try to fetch results if it's a SELECT query
                if query.strip().upper().startswith("SELECT"):
                    rows = result.fetchall()
                    columns = result.keys()
                    return {
                        "rows": [dict(zip(columns, row)) for row in rows],
                        "row_count": len(rows)
                    }
                else:
                    return {
                        "success": True,
                        "row_count": result.rowcount
                    }
            except Exception as e:
                await db.rollback()
                return {"error": str(e)}

    async def _get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table"""
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """
        return await self._execute_query(query, {"table_name": table_name})

    async def _list_tables(self) -> Dict[str, Any]:
        """List all tables in the database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        return await self._execute_query(query)

    async def _get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """
        return await self._execute_query(query)

    async def _insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into a table"""
        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f":{col}" for col in columns]
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        params = {col: val for col, val in zip(columns, values)}
        return await self._execute_query(query, params)

    async def _update_record(self, table: str, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in a table"""
        set_clause = ", ".join([f"{col} = :{col}" for col in data.keys()])
        query = f"""
            UPDATE {table}
            SET {set_clause}
            WHERE id = :id
        """
        
        params = {**data, "id": record_id}
        return await self._execute_query(query, params)

    async def _delete_record(self, table: str, record_id: int) -> Dict[str, Any]:
        """Delete a record from a table"""
        query = f"DELETE FROM {table} WHERE id = :id"
        return await self._execute_query(query, {"id": record_id})

    def _is_query_safe(self, query: str) -> bool:
        """Basic security check for SQL queries"""
        dangerous_patterns = [
            "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                return False
        
        return True
