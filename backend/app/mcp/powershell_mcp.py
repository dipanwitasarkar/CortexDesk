from app.mcp.base_mcp import BaseMCP
from typing import Dict, Any, List
import subprocess
import asyncio
import json


class PowerShellMCP(BaseMCP):
    """PowerShell operations via MCP for Windows automation"""
    
    def __init__(self):
        super().__init__("powershell")
        self.allowed_commands = {
            "Get-Process", "Get-Service", "Get-ChildItem", "Get-Content",
            "Set-Content", "New-Item", "Remove-Item", "Test-Path",
            "Get-Location", "Set-Location", "Get-Command", "Get-Help"
        }

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call PowerShell tools"""
        try:
            if tool_name == "execute_command":
                return await self._execute_command(parameters["command"])
            elif tool_name == "get_process":
                return await self._get_process(parameters.get("name"))
            elif tool_name == "get_service":
                return await self._get_service(parameters.get("name"))
            elif tool_name == "open_application":
                return await self._open_application(parameters["app_path"])
            elif tool_name == "get_clipboard":
                return await self._get_clipboard()
            elif tool_name == "set_clipboard":
                return await self._set_clipboard(parameters["content"])
            elif tool_name == "take_screenshot":
                return await self._take_screenshot()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available PowerShell tools"""
        return [
            {
                "name": "execute_command",
                "description": "Execute a PowerShell command",
                "parameters": {
                    "command": {"type": "string", "description": "PowerShell command to execute"}
                }
            },
            {
                "name": "get_process",
                "description": "Get information about running processes",
                "parameters": {
                    "name": {"type": "string", "description": "Process name (optional)"}
                }
            },
            {
                "name": "get_service",
                "description": "Get information about Windows services",
                "parameters": {
                    "name": {"type": "string", "description": "Service name (optional)"}
                }
            },
            {
                "name": "open_application",
                "description": "Open an application",
                "parameters": {
                    "app_path": {"type": "string", "description": "Path to application executable"}
                }
            },
            {
                "name": "get_clipboard",
                "description": "Get clipboard content",
                "parameters": {}
            },
            {
                "name": "set_clipboard",
                "description": "Set clipboard content",
                "parameters": {
                    "content": {"type": "string", "description": "Content to set"}
                }
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot",
                "parameters": {}
            }
        ]

    async def _execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a PowerShell command"""
        try:
            # Security check - validate command
            if not self._is_command_safe(command):
                return {"error": "Command not allowed for security reasons"}
            
            process = await asyncio.create_subprocess_exec(
                "powershell.exe",
                "-Command",
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "error": stderr.decode(),
                    "exit_code": process.returncode
                }
            
            return {
                "output": stdout.decode(),
                "exit_code": process.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_process(self, name: str = None) -> Dict[str, Any]:
        """Get process information"""
        command = "Get-Process | Select-Object Name, Id, CPU, WorkingSet | ConvertTo-Json"
        if name:
            command = f"Get-Process -Name '{name}' | Select-Object Name, Id, CPU, WorkingSet | ConvertTo-Json"
        
        return await self._execute_command(command)

    async def _get_service(self, name: str = None) -> Dict[str, Any]:
        """Get service information"""
        command = "Get-Service | Select-Object Name, Status, StartType | ConvertTo-Json"
        if name:
            command = f"Get-Service -Name '{name}' | Select-Object Name, Status, StartType | ConvertTo-Json"
        
        return await self._execute_command(command)

    async def _open_application(self, app_path: str) -> Dict[str, Any]:
        """Open an application"""
        command = f"Start-Process '{app_path}'"
        return await self._execute_command(command)

    async def _get_clipboard(self) -> Dict[str, Any]:
        """Get clipboard content"""
        command = "Get-Clipboard"
        return await self._execute_command(command)

    async def _set_clipboard(self, content: str) -> Dict[str, Any]:
        """Set clipboard content"""
        command = f"Set-Clipboard -Value '{content}'"
        return await self._execute_command(command)

    async def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot (requires PowerShell screenshot module)"""
        # This would require additional setup
        command = "Take-ScreenShot -Path 'screenshot.png'"
        return await self._execute_command(command)

    def _is_command_safe(self, command: str) -> bool:
        """Basic security check for PowerShell commands"""
        dangerous_patterns = [
            "Remove-Item", "Delete-Item", "Format-Volume", 
            "Restart-Computer", "Stop-Computer", "Remove-ADUser"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return False
        
        return True
