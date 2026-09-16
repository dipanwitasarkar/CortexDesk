from app.agents.base_agent import BaseAgent
from app.mcp.powershell_mcp import PowerShellMCP
from app.services.terminal_service import terminal_service
from typing import Dict, Any, List, Optional
import json


class SystemAgent(BaseAgent):
    """
    System Agent - Handles system administration tasks.
    Responsibilities:
    - WSL management
    - Podman/Docker management
    - Process management
    - Service management
    - System diagnostics
    - Log analysis
    """
    
    def __init__(self):
        super().__init__(
            name="system",
            description="Handles system administration including WSL, Podman, Docker, processes, and diagnostics"
        )
        self.powershell_mcp = PowerShellMCP()

    def get_system_prompt(self) -> str:
        return """You are the System Agent for a Windows AI Assistant. Your role is to help users with system administration:

1. Manage WSL (Windows Subsystem for Linux)
2. Manage Podman and Docker containers
3. Monitor and manage processes
4. Manage Windows services
5. Perform system diagnostics
6. Analyze system logs
7. Monitor system resources

You have access to:
- PowerShell commands for system control
- Process and service management
- Container management commands
- System diagnostics tools

Always be cautious with system operations. Explain potential impacts before executing commands."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process system administration requests"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        context = input_data.get("context", {})
        agent_plan = input_data.get("agent_plan", {})
        
        # Determine the type of system task
        task_type = await self._classify_task(user_message, context)
        
        # Execute based on task type
        if task_type == "wsl_management":
            return await self._handle_wsl_management(user_message, context)
        elif task_type == "container_management":
            return await self._handle_container_management(user_message, context)
        elif task_type == "process_management":
            return await self._handle_process_management(user_message, context)
        elif task_type == "service_management":
            return await self._handle_service_management(user_message, context)
        elif task_type == "system_diagnostics":
            return await self._handle_system_diagnostics(user_message, context)
        elif task_type == "log_analysis":
            return await self._handle_log_analysis(user_message, context)
        elif task_type == "terminal_command":
            return await self._handle_terminal_command(user_message, context)
        else:
            return await self._handle_general_system_task(user_message, context)

    async def _classify_task(self, user_message: str, context: Dict[str, Any]) -> str:
        """Classify the type of system task"""
        
        prompt = f"""Classify the following system-related request into one of these categories:
- wsl_management: WSL (Windows Subsystem for Linux) operations
- container_management: Podman or Docker container operations
- process_management: Process monitoring and management
- service_management: Windows service management
- system_diagnostics: System diagnostics and health checks
- log_analysis: System log analysis
- terminal_command: Terminal command analysis and assistance
- general: General system-related questions

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the category name."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip().lower().replace("-", "_")

    async def _handle_wsl_management(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WSL management requests"""
        
        # Extract WSL command details
        wsl_details = await self._extract_wsl_details(user_message, context)
        
        # Build PowerShell command for WSL
        if wsl_details.get("action") == "list":
            command = "wsl --list --verbose"
        elif wsl_details.get("action") == "start":
            command = f"wsl --distribution {wsl_details.get('distribution', '')}"
        elif wsl_details.get("action") == "stop":
            command = f"wsl --terminate {wsl_details.get('distribution', '')}"
        elif wsl_details.get("action") == "execute":
            command = f"wsl --distribution {wsl_details.get('distribution', '')} -- {wsl_details.get('command', '')}"
        else:
            return {
                "response": "I need more specific information about what WSL action you want to perform.",
                "requires_confirmation": True
            }
        
        result = await self.powershell_mcp.call_tool("execute_command", {"command": command})
        
        if "error" in result:
            return {
                "response": f"WSL command failed: {result['error']}",
                "error": result["error"]
            }
        
        return {
            "response": f"WSL command executed successfully",
            "output": result.get("output", ""),
            "command": command
        }

    async def _handle_container_management(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle container management requests"""
        
        # Extract container command details
        container_details = await self._extract_container_details(user_message, context)
        
        # Determine if using Podman or Docker
        container_runtime = container_details.get("runtime", "podman")
        
        # Build container command
        if container_details.get("action") == "list":
            command = f"{container_runtime} ps -a"
        elif container_details.get("action") == "start":
            command = f"{container_runtime} start {container_details.get('container_name', '')}"
        elif container_details.get("action") == "stop":
            command = f"{container_runtime} stop {container_details.get('container_name', '')}"
        elif container_details.get("action") == "logs":
            command = f"{container_runtime} logs {container_details.get('container_name', '')}"
        elif container_details.get("action") == "status":
            command = f"{container_runtime} inspect {container_details.get('container_name', '')}"
        else:
            return {
                "response": "I need more specific information about what container action you want to perform.",
                "requires_confirmation": True
            }
        
        result = await self.powershell_mcp.call_tool("execute_command", {"command": command})
        
        if "error" in result:
            return {
                "response": f"Container command failed: {result['error']}",
                "error": result["error"]
            }
        
        # Analyze the output
        analysis = await self._analyze_container_output(user_message, result.get("output", ""))
        
        return {
            "response": analysis,
            "output": result.get("output", ""),
            "command": command,
            "runtime": container_runtime
        }

    async def _handle_process_management(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle process management requests"""
        
        # Extract process details
        process_details = await self._extract_process_details(user_message, context)
        
        if process_details.get("action") == "list":
            result = await self.powershell_mcp.call_tool("get_process", {})
        elif process_details.get("action") == "info":
            result = await self.powershell_mcp.call_tool(
                "get_process",
                {"name": process_details.get("process_name")}
            )
        elif process_details.get("action") == "kill":
            # This is a dangerous operation, require confirmation
            return {
                "response": f"Killing process '{process_details.get('process_name')}' is a potentially dangerous operation. Please confirm you want to proceed.",
                "requires_confirmation": True,
                "process_name": process_details.get("process_name")
            }
        else:
            return {
                "response": "I need more specific information about what process action you want to perform.",
                "requires_confirmation": True
            }
        
        if "error" in result:
            return {
                "response": f"Process command failed: {result['error']}",
                "error": result["error"]
            }
        
        # Analyze process information
        analysis = await self._analyze_process_info(user_message, result.get("output", ""))
        
        return {
            "response": analysis,
            "process_info": result.get("output", "")
        }

    async def _handle_service_management(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service management requests"""
        
        # Extract service details
        service_details = await self._extract_service_details(user_message, context)
        
        if service_details.get("action") == "list":
            result = await self.powershell_mcp.call_tool("get_service", {})
        elif service_details.get("action") == "info":
            result = await self.powershell_mcp.call_tool(
                "get_service",
                {"name": service_details.get("service_name")}
            )
        elif service_details.get("action") == "start":
            command = f"Start-Service -Name '{service_details.get('service_name')}'"
            result = await self.powershell_mcp.call_tool("execute_command", {"command": command})
        elif service_details.get("action") == "stop":
            command = f"Stop-Service -Name '{service_details.get('service_name')}'"
            result = await self.powershell_mcp.call_tool("execute_command", {"command": command})
        else:
            return {
                "response": "I need more specific information about what service action you want to perform.",
                "requires_confirmation": True
            }
        
        if "error" in result:
            return {
                "response": f"Service command failed: {result['error']}",
                "error": result["error"]
            }
        
        return {
            "response": f"Service operation completed successfully",
            "service_info": result.get("output", "")
        }

    async def _handle_system_diagnostics(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system diagnostics requests"""
        
        # Run diagnostic commands
        diagnostics = {}
        
        # CPU and Memory
        cpu_command = "Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, MaxClockSpeed | ConvertTo-Json"
        cpu_result = await self.powershell_mcp.call_tool("execute_command", {"command": cpu_command})
        diagnostics["cpu"] = cpu_result.get("output", "")
        
        # Memory
        memory_command = "Get-WmiObject Win32_PhysicalMemory | Select-Object Capacity, Speed | ConvertTo-Json"
        memory_result = await self.powershell_mcp.call_tool("execute_command", {"command": memory_command})
        diagnostics["memory"] = memory_result.get("output", "")
        
        # Disk
        disk_command = "Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace | ConvertTo-Json"
        disk_result = await self.powershell_mcp.call_tool("execute_command", {"command": disk_command})
        diagnostics["disk"] = disk_result.get("output", "")
        
        # Analyze diagnostics
        analysis = await self._analyze_diagnostics(user_message, diagnostics)
        
        return {
            "response": analysis,
            "diagnostics": diagnostics
        }

    async def _handle_log_analysis(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle log analysis requests"""
        
        # Extract log details
        log_details = await self._extract_log_details(user_message, context)
        
        # Get log files
        if log_details.get("log_type") == "system":
            command = "Get-EventLog -LogName System -Newest 50 | ConvertTo-Json"
        elif log_details.get("log_type") == "application":
            command = "Get-EventLog -LogName Application -Newest 50 | ConvertTo-Json"
        elif log_details.get("log_type") == "security":
            command = "Get-EventLog -LogName Security -Newest 50 | ConvertTo-Json"
        else:
            command = f"Get-Content '{log_details.get('log_path', '')}' -Tail 50"
        
        result = await self.powershell_mcp.call_tool("execute_command", {"command": command})
        
        if "error" in result:
            return {
                "response": f"Log retrieval failed: {result['error']}",
                "error": result["error"]
            }
        
        # Analyze logs
        analysis = await self._analyze_logs(user_message, result.get("output", ""))
        
        return {
            "response": analysis,
            "log_output": result.get("output", "")
        }

    async def _handle_terminal_command(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle terminal command analysis and assistance"""
        
        # Extract command from message
        command = await self._extract_terminal_command(user_message, context)
        
        if not command:
            return {
                "response": "I need a terminal command to analyze. Please provide the command you want me to help with.",
                "requires_confirmation": True
            }
        
        # Analyze the command
        analysis_result = await terminal_service.analyze_command(command, context)
        
        if not analysis_result["success"]:
            return {
                "response": f"Failed to analyze command: {analysis_result['error']}",
                "error": analysis_result["error"]
            }
        
        analysis = analysis_result["analysis"]
        
        # Format the response
        response_parts = []
        
        if analysis.get("explanation"):
            response_parts.append(f"**Command Explanation:**\n{analysis['explanation']}")
        
        if analysis.get("risk_level") == "high":
            response_parts.append(f"⚠️ **HIGH RISK COMMAND** - This command could be dangerous.")
        elif analysis.get("risk_level") == "medium":
            response_parts.append(f"⚠️ **MEDIUM RISK COMMAND** - Use with caution.")
        
        if analysis.get("suggestions"):
            response_parts.append(f"**Suggestions:**\n{chr(10).join(analysis['suggestions'])}")
        
        if analysis.get("potential_issues"):
            response_parts.append(f"**Potential Issues:**\n{chr(10).join(analysis['potential_issues'])}")
        
        return {
            "response": chr(10).join(response_parts),
            "command": command,
            "analysis": analysis
        }

    async def _handle_general_system_task(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general system-related questions"""
        
        prompt = f"""Answer this system-related question:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Provide helpful, actionable advice for system administration."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": response
        }

    async def _extract_wsl_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract WSL operation details"""
        
        prompt = f"""Extract WSL operation details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (list, start, stop, execute)
- distribution: WSL distribution name (if applicable)
- command: command to execute in WSL (if applicable)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_container_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract container operation details"""
        
        prompt = f"""Extract container operation details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- runtime: container runtime (podman or docker)
- action: type of action (list, start, stop, logs, status)
- container_name: name of the container (if applicable)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"runtime": "podman"}

    async def _extract_process_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract process operation details"""
        
        prompt = f"""Extract process operation details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (list, info, kill)
- process_name: name of the process (if applicable)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_service_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract service operation details"""
        
        prompt = f"""Extract service operation details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (list, info, start, stop)
- service_name: name of the service (if applicable)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_log_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract log analysis details"""
        
        prompt = f"""Extract log analysis details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- log_type: type of log (system, application, security, or custom)
- log_path: path to log file (if custom)
- time_range: time range to analyze (if specified)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _analyze_container_output(self, user_message: str, output: str) -> str:
        """Analyze container command output"""
        
        prompt = f"""Analyze this container command output in response to the user's request:

User request: {user_message}

Container output:
{output}

Provide a clear analysis of the container status and any relevant insights."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _analyze_process_info(self, user_message: str, output: str) -> str:
        """Analyze process information"""
        
        prompt = f"""Analyze this process information in response to the user's request:

User request: {user_message}

Process information:
{output}

Provide a clear analysis of the process status and any relevant insights."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _analyze_diagnostics(self, user_message: str, diagnostics: Dict[str, str]) -> str:
        """Analyze system diagnostics"""
        
        prompt = f"""Analyze these system diagnostics in response to the user's request:

User request: {user_message}

Diagnostics:
{json.dumps(diagnostics, indent=2)}

Provide a clear analysis of system health and any recommendations."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _analyze_logs(self, user_message: str, log_output: str) -> str:
        """Analyze system logs"""
        
        prompt = f"""Analyze these system logs in response to the user's request:

User request: {user_message}

Log output:
{log_output}

Provide a clear analysis of any issues, patterns, or relevant information found in the logs."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _extract_terminal_command(self, user_message: str, context: Dict[str, Any]) -> Optional[str]:
        """Extract terminal command from user message"""
        
        # Check if command is in context
        if context.get("command"):
            return context["command"]
        
        # Try to extract command from message
        prompt = f"""Extract the terminal command from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the command, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip() if response else None
