from app.agents.base_agent import BaseAgent
from app.mcp.powershell_mcp import PowerShellMCP
from app.mcp.filesystem_mcp import FilesystemMCP
from app.services.screenshot_service import screenshot_service
from typing import Dict, Any, List, Optional
import json


class WindowsAgent(BaseAgent):
    """
    Windows Agent - Handles Windows automation and control.
    Responsibilities:
    - Open applications
    - Search files
    - Clipboard access
    - Screenshot capture
    - Desktop actions
    """
    
    def __init__(self):
        super().__init__(
            name="windows",
            description="Handles Windows automation including application control, file search, clipboard, and screenshots"
        )
        self.powershell_mcp = PowerShellMCP()
        self.filesystem_mcp = FilesystemMCP()

    def get_system_prompt(self) -> str:
        return """You are the Windows Agent for a Windows AI Assistant. Your role is to help users with Windows automation:

1. Open and control applications
2. Search for files and folders
3. Manage clipboard content
4. Capture screenshots
5. Perform desktop actions
6. Navigate the Windows filesystem

You have access to:
- PowerShell commands for system control
- Filesystem operations for file management
- Windows automation capabilities

Always confirm before performing potentially disruptive actions. Be helpful but cautious."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Windows automation requests"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        context = input_data.get("context", {})
        agent_plan = input_data.get("agent_plan", {})
        
        # Determine the type of Windows task
        task_type = await self._classify_task(user_message, context)
        
        # Execute based on task type
        if task_type == "open_application":
            return await self._handle_open_application(user_message, context)
        elif task_type == "file_search":
            return await self._handle_file_search(user_message, context)
        elif task_type == "clipboard":
            return await self._handle_clipboard(user_message, context)
        elif task_type == "screenshot":
            return await self._handle_screenshot(user_message, context)
        elif task_type == "screenshot_analysis":
            return await self._handle_screenshot_analysis(user_message, context)
        elif task_type == "desktop_action":
            return await self._handle_desktop_action(user_message, context)
        else:
            return await self._handle_general_windows_task(user_message, context)

    async def _classify_task(self, user_message: str, context: Dict[str, Any]) -> str:
        """Classify the type of Windows task"""
        
        prompt = f"""Classify the following Windows-related request into one of these categories:
- open_application: Open or launch an application
- file_search: Search for files or folders
- clipboard: Get or set clipboard content
- screenshot: Take a screenshot
- screenshot_analysis: Analyze a screenshot
- desktop_action: Perform desktop actions (create folders, organize files, etc.)
- general: General Windows-related questions

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the category name."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip().lower().replace("-", "_")

    async def _handle_open_application(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle application opening requests"""
        
        # Extract application path or name
        app_info = await self._extract_app_info(user_message, context)
        
        if not app_info.get("app_path"):
            return {
                "response": "I need the application path or name to open it. Please provide the full path to the executable or a well-known application name.",
                "requires_confirmation": True
            }
        
        # Try to open the application
        result = await self.powershell_mcp.call_tool(
            "open_application",
            {"app_path": app_info["app_path"]}
        )
        
        if "error" in result:
            return {
                "response": f"Failed to open application: {result['error']}",
                "error": result["error"]
            }
        
        return {
            "response": f"Successfully opened {app_info['app_path']}",
            "app_path": app_info["app_path"]
        }

    async def _handle_file_search(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file search requests"""
        
        # Extract search parameters
        search_params = await self._extract_file_search_params(user_message, context)
        
        # Perform search
        result = await self.filesystem_mcp.call_tool(
            "search_files",
            {
                "path": search_params.get("path", "."),
                "pattern": search_params.get("pattern", "*")
            }
        )
        
        if "error" in result:
            return {
                "response": f"File search failed: {result['error']}",
                "error": result["error"]
            }
        
        matches = result.get("matches", [])
        
        if not matches:
            return {
                "response": f"No files found matching '{search_params.get('pattern', '*')}' in '{search_params.get('path', '.')}'",
                "matches_found": 0
            }
        
        # Summarize results
        summary = await self._summarize_file_search_results(user_message, matches)
        
        return {
            "response": summary,
            "matches_found": len(matches),
            "matches": matches[:10]  # Limit to first 10 matches
        }

    async def _handle_clipboard(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle clipboard operations"""
        
        # Determine if getting or setting clipboard
        action = await self._determine_clipboard_action(user_message)
        
        if action == "get":
            result = await self.powershell_mcp.call_tool("get_clipboard", {})
            
            if "error" in result:
                return {
                    "response": f"Failed to get clipboard content: {result['error']}",
                    "error": result["error"]
                }
            
            clipboard_content = result.get("output", "")
            
            return {
                "response": f"Clipboard content: {clipboard_content}",
                "clipboard_content": clipboard_content
            }
        
        elif action == "set":
            # Extract content to set
            content = await self._extract_clipboard_content(user_message)
            
            if not content:
                return {
                    "response": "I need the content to set on the clipboard. Please provide the text you want to copy.",
                    "requires_confirmation": True
                }
            
            result = await self.powershell_mcp.call_tool(
                "set_clipboard",
                {"content": content}
            )
            
            if "error" in result:
                return {
                    "response": f"Failed to set clipboard content: {result['error']}",
                    "error": result["error"]
                }
            
            return {
                "response": f"Successfully set clipboard content",
                "content_set": content
            }

    async def _handle_screenshot(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle screenshot requests"""
        
        result = await screenshot_service.capture_screenshot()
        
        if not result["success"]:
            return {
                "response": f"Failed to take screenshot: {result['error']}",
                "error": result["error"]
            }
        
        return {
            "response": f"Screenshot taken successfully and saved to {result['path']}",
            "screenshot_path": result["path"]
        }

    async def _handle_screenshot_analysis(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle screenshot analysis requests"""
        
        # Extract screenshot path from message or context
        screenshot_path = context.get("screenshot_path") or await self._extract_screenshot_path(user_message)
        
        if not screenshot_path:
            return {
                "response": "I need the path to a screenshot to analyze it. Please provide the file path.",
                "requires_confirmation": True
            }
        
        # Determine analysis type
        analysis_type = await self._determine_analysis_type(user_message)
        
        # Perform analysis
        analysis_result = await screenshot_service.analyze_screenshot(screenshot_path, analysis_type)
        
        if not analysis_result["success"]:
            return {
                "response": f"Failed to analyze screenshot: {analysis_result['error']}",
                "error": analysis_result["error"]
            }
        
        # Format the response
        if analysis_type == "general":
            response = f"Screenshot Analysis:\n{analysis_result['description']}"
        elif analysis_type == "ui_elements":
            response = f"UI Elements Analysis:\n{analysis_result['ui_analysis']}"
        elif analysis_type == "text":
            response = f"Text Content:\n{analysis_result['text_content']}"
        elif analysis_type == "actions":
            response = f"Suggested Actions:\n{analysis_result['suggested_actions']}"
        else:
            response = f"Analysis:\n{analysis_result.get('description', 'Analysis complete')}"
        
        return {
            "response": response,
            "analysis_type": analysis_type,
            "screenshot_path": screenshot_path
        }

    async def _handle_desktop_action(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle desktop action requests"""
        
        # Extract action details
        action_details = await self._extract_desktop_action(user_message, context)
        
        if action_details.get("action_type") == "create_folder":
            result = await self.filesystem_mcp.call_tool(
                "create_directory",
                {"path": action_details["path"]}
            )
        elif action_details.get("action_type") == "organize_files":
            # This would require more complex logic
            return {
                "response": "File organization requires more specific instructions. Please provide details about how you want files organized.",
                "requires_confirmation": True
            }
        else:
            return {
                "response": "I'm not sure what desktop action you want to perform. Please be more specific.",
                "requires_confirmation": True
            }
        
        if "error" in result:
            return {
                "response": f"Desktop action failed: {result['error']}",
                "error": result["error"]
            }
        
        return {
            "response": f"Successfully performed desktop action: {action_details['action_type']}",
            "action_details": action_details
        }

    async def _handle_general_windows_task(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general Windows-related questions"""
        
        prompt = f"""Answer this Windows-related question:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Provide helpful, actionable advice for Windows users."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": response
        }

    async def _extract_app_info(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract application information from user message"""
        
        prompt = f"""Extract application information from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- app_path: full path to application executable or well-known app name
- app_name: name of the application"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_file_search_params(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file search parameters from user message"""
        
        prompt = f"""Extract file search parameters from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- path: directory path to search (default: current directory)
- pattern: file pattern to search for (e.g., *.py, *.txt)
- file_name: specific file name to search for"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"pattern": "*"}

    async def _determine_clipboard_action(self, user_message: str) -> str:
        """Determine if user wants to get or set clipboard"""
        
        message_lower = user_message.lower()
        if "copy" in message_lower or "set" in message_lower or "put" in message_lower:
            return "set"
        else:
            return "get"

    async def _extract_clipboard_content(self, user_message: str) -> str:
        """Extract content to set on clipboard"""
        
        prompt = f"""Extract the text content that should be copied to the clipboard from this request:

{user_message}

Respond with just the text content (no JSON, no extra text)."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip()

    async def _extract_desktop_action(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract desktop action details from user message"""
        
        prompt = f"""Extract desktop action details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action_type: type of action (create_folder, organize_files, etc.)
- path: relevant path for the action
- details: any additional details needed"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _summarize_file_search_results(self, user_message: str, matches: List[str]) -> str:
        """Summarize file search results"""
        
        prompt = f"""Summarize these file search results in response to the user's request:

User request: {user_message}

Files found:
{chr(10).join(matches[:20])}

Provide a clear summary highlighting the most relevant files."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _extract_screenshot_path(self, user_message: str) -> Optional[str]:
        """Extract screenshot path from user message"""
        
        prompt = f"""Extract the screenshot file path from this request:

{user_message}

Respond with just the file path, nothing else."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip() if response else None

    async def _determine_analysis_type(self, user_message: str) -> str:
        """Determine the type of screenshot analysis needed"""
        
        message_lower = user_message.lower()
        
        if "ui" in message_lower or "element" in message_lower or "button" in message_lower:
            return "ui_elements"
        elif "text" in message_lower or "ocr" in message_lower or "read" in message_lower:
            return "text"
        elif "action" in message_lower or "suggest" in message_lower or "recommend" in message_lower:
            return "actions"
        else:
            return "general"
