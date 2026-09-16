from app.mcp.base_mcp import BaseMCP
from typing import Dict, Any, List
import os
import aiofiles
from pathlib import Path


class FilesystemMCP(BaseMCP):
    """Local filesystem operations via MCP"""
    
    def __init__(self):
        super().__init__("filesystem")
        self.allowed_paths = set()  # Configure allowed paths for security

    def add_allowed_path(self, path: str):
        """Add a path to the allowed list"""
        self.allowed_paths.add(os.path.abspath(path))

    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        abs_path = os.path.abspath(path)
        for allowed in self.allowed_paths:
            if abs_path.startswith(allowed):
                return True
        return False

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call filesystem tools"""
        try:
            if tool_name == "read_file":
                return await self._read_file(parameters["path"])
            elif tool_name == "write_file":
                return await self._write_file(parameters["path"], parameters["content"])
            elif tool_name == "list_directory":
                return await self._list_directory(parameters["path"])
            elif tool_name == "search_files":
                return await self._search_files(parameters["path"], parameters["pattern"])
            elif tool_name == "get_file_info":
                return await self._get_file_info(parameters["path"])
            elif tool_name == "create_directory":
                return await self._create_directory(parameters["path"])
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available filesystem tools"""
        return [
            {
                "name": "read_file",
                "description": "Read contents of a file",
                "parameters": {
                    "path": {"type": "string", "description": "File path"}
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                }
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory",
                "parameters": {
                    "path": {"type": "string", "description": "Directory path"}
                }
            },
            {
                "name": "search_files",
                "description": "Search for files matching a pattern",
                "parameters": {
                    "path": {"type": "string", "description": "Directory to search"},
                    "pattern": {"type": "string", "description": "File pattern (e.g., *.py)"}
                }
            },
            {
                "name": "get_file_info",
                "description": "Get file metadata",
                "parameters": {
                    "path": {"type": "string", "description": "File path"}
                }
            },
            {
                "name": "create_directory",
                "description": "Create a directory",
                "parameters": {
                    "path": {"type": "string", "description": "Directory path"}
                }
            }
        ]

    async def _read_file(self, path: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        async with aiofiles.open(path, 'r') as f:
            content = await f.read()
        
        return {"content": content, "path": path}

    async def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        async with aiofiles.open(path, 'w') as f:
            await f.write(content)
        
        return {"success": True, "path": path}

    async def _list_directory(self, path: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        try:
            entries = []
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                stat = os.stat(full_path)
                entries.append({
                    "name": entry,
                    "is_file": os.path.isfile(full_path),
                    "is_directory": os.path.isdir(full_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            return {"entries": entries, "path": path}
        except Exception as e:
            return {"error": str(e)}

    async def _search_files(self, path: str, pattern: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        matches = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if Path(file).match(pattern):
                    matches.append(os.path.join(root, file))
        
        return {"matches": matches, "pattern": pattern, "path": path}

    async def _get_file_info(self, path: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        stat = os.stat(path)
        return {
            "path": path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "is_file": os.path.isfile(path),
            "is_directory": os.path.isdir(path)
        }

    async def _create_directory(self, path: str) -> Dict[str, Any]:
        if not self._is_path_allowed(path):
            return {"error": "Path not allowed"}
        
        os.makedirs(path, exist_ok=True)
        return {"success": True, "path": path}
