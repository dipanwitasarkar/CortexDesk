from typing import Dict, Any, List, Optional
import re
from app.services.llm_service import llm_service


class GuardrailsService:
    """
    Guardrails service for input validation and security.
    Implements input filtering, tool usage control, and safety checks.
    """
    
    def __init__(self):
        # Dangerous patterns for prompt injection
        self.prompt_injection_patterns = [
            r"ignore (all )?(previous|above) instructions",
            r"forget (all )?(previous|above) instructions",
            r"disregard (all )?(previous|above) instructions",
            r"override (all )?(previous|above) instructions",
            r"new instructions?:",
            r"change your instructions",
            r"act as a different",
            r"pretend to be",
            r"roleplay as",
            r"jailbreak",
            r"bypass safety",
            r"ignore rules",
            r"break character",
        ]
        
        # PII patterns (basic)
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
        ]
        
        # Dangerous command patterns
        self.dangerous_command_patterns = [
            r"rm -rf",
            r"del /",
            r"format",
            r"shutdown",
            r"restart",
            r"drop table",
            r"delete from",
            r"truncate",
        ]
        
        # Tool risk levels
        self.tool_risk_levels = {
            "safe": [
                "read_file",
                "list_directory",
                "search_files",
                "get_file_info",
                "get_process",
                "get_service",
                "get_clipboard",
                "execute_query",  # SELECT only
                "list_tables",
                "get_table_info",
                "get_repo",
                "list_repos",
                "get_file",  # GitHub
                "search_code",
                "get_pr",
                "list_prs",
                "get_issue",
                "list_issues",
            ],
            "medium": [
                "write_file",
                "create_directory",
                "open_application",
                "set_clipboard",
                "take_screenshot",
                "insert_record",
                "update_record",
            ],
            "high": [
                "delete_file",
                "execute_command",  # PowerShell
                "delete_record",
                "kill_process",
                "start_service",
                "stop_service",
            ]
        }

    async def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validate user input for security issues.
        
        Returns:
            Dict with 'valid' (bool), 'reason' (str), and 'sanitized' (str)
        """
        # Check for prompt injection
        injection_result = self._check_prompt_injection(user_input)
        if not injection_result["safe"]:
            return {
                "valid": False,
                "reason": f"Prompt injection detected: {injection_result['reason']}",
                "sanitized": None
            }
        
        # Check for PII
        pii_result = self._check_pii(user_input)
        if pii_result["found"]:
            return {
                "valid": False,
                "reason": f"PII detected: {', '.join(pii_result['types'])}",
                "sanitized": pii_result["sanitized"]
            }
        
        # Check for dangerous commands
        command_result = self._check_dangerous_commands(user_input)
        if not command_result["safe"]:
            return {
                "valid": False,
                "reason": f"Dangerous command detected: {command_result['reason']}",
                "sanitized": None
            }
        
        # LLM-based safety check
        llm_safety_result = await self._llm_safety_check(user_input)
        if not llm_safety_result["safe"]:
            return {
                "valid": False,
                "reason": f"Safety concern detected: {llm_safety_result['reason']}",
                "sanitized": None
            }
        
        return {
            "valid": True,
            "reason": "Input passed all safety checks",
            "sanitized": user_input
        }

    def _check_prompt_injection(self, text: str) -> Dict[str, Any]:
        """Check for prompt injection patterns"""
        text_lower = text.lower()
        
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": f"Pattern matched: {pattern}",
                    "pattern": pattern
                }
        
        return {"safe": True}

    def _check_pii(self, text: str) -> Dict[str, Any]:
        """Check for PII and return sanitized version"""
        found_types = []
        sanitized = text
        
        # Check SSN
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
            found_types.append("SSN")
            sanitized = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****", sanitized)
        
        # Check credit card
        if re.search(r"\b\d{16}\b", text):
            found_types.append("Credit Card")
            sanitized = re.sub(r"\b(\d{4})\d{8}(\d{4})\b", r"\1********\2", sanitized)
        
        # Check email
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
            found_types.append("Email")
            sanitized = re.sub(
                r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+)\.([A-Z|a-z]{2,})\b",
                r"***@\2.\3",
                sanitized
            )
        
        # Check phone
        if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text):
            found_types.append("Phone")
            sanitized = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***-***-****", sanitized)
        
        return {
            "found": len(found_types) > 0,
            "types": found_types,
            "sanitized": sanitized if found_types else text
        }

    def _check_dangerous_commands(self, text: str) -> Dict[str, Any]:
        """Check for dangerous command patterns"""
        text_lower = text.lower()
        
        for pattern in self.dangerous_command_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": f"Dangerous pattern: {pattern}",
                    "pattern": pattern
                }
        
        return {"safe": True}

    async def _llm_safety_check(self, text: str) -> Dict[str, Any]:
        """Use LLM to check for safety issues"""
        
        prompt = f"""Analyze the following user input for safety concerns. Check for:
1. Harmful content
2. Illegal activities
3. Hate speech
4. Sexual content
5. Violence
6. Self-harm

User input: {text}

Respond in JSON format with this structure:
{{
    "safe": true/false,
    "reason": "brief explanation if not safe",
    "category": "category of concern if not safe"
}}

If the input is safe, respond with {{"safe": true, "reason": "", "category": ""}}"""

        try:
            response = await llm_service.generate_response(
                [{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            return {
                "safe": result.get("safe", True),
                "reason": result.get("reason", ""),
                "category": result.get("category", "")
            }
        except Exception as e:
            # If LLM check fails, default to safe but log the error
            return {
                "safe": True,
                "reason": f"LLM safety check failed: {str(e)}",
                "category": ""
            }

    def get_tool_risk_level(self, tool_name: str) -> str:
        """Get the risk level of a tool"""
        for level, tools in self.tool_risk_levels.items():
            if tool_name in tools:
                return level
        return "medium"  # Default to medium

    def should_auto_approve(self, tool_name: str) -> bool:
        """Check if a tool should be auto-approved"""
        return tool_name in self.tool_risk_levels["safe"]

    def should_require_confirmation(self, tool_name: str) -> bool:
        """Check if a tool requires user confirmation"""
        return tool_name in self.tool_risk_levels["medium"]

    def should_require_explicit_approval(self, tool_name: str) -> bool:
        """Check if a tool requires explicit approval"""
        return tool_name in self.tool_risk_levels["high"]

    async def validate_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a tool call before execution.
        
        Returns:
            Dict with 'approved' (bool), 'requires_confirmation' (bool), 
            'requires_explicit_approval' (bool), and 'reason' (str)
        """
        risk_level = self.get_tool_risk_level(tool_name)
        
        if risk_level == "safe":
            return {
                "approved": True,
                "requires_confirmation": False,
                "requires_explicit_approval": False,
                "reason": f"Tool '{tool_name}' is safe to execute"
            }
        
        elif risk_level == "medium":
            return {
                "approved": False,
                "requires_confirmation": True,
                "requires_explicit_approval": False,
                "reason": f"Tool '{tool_name}' requires user confirmation"
            }
        
        elif risk_level == "high":
            return {
                "approved": False,
                "requires_confirmation": False,
                "requires_explicit_approval": True,
                "reason": f"Tool '{tool_name}' requires explicit approval due to high risk"
            }
        
        return {
            "approved": False,
            "requires_confirmation": True,
            "requires_explicit_approval": False,
            "reason": f"Tool '{tool_name}' has unknown risk level"
        }

    async def sanitize_output(self, output: str) -> str:
        """Sanitize agent output before sending to user"""
        # Remove any potential system prompts or instructions
        sanitized = output
        
        # Remove common instruction patterns
        instruction_patterns = [
            r"Instructions:.*",
            r"System:.*",
            r"As an AI,.*",
            r"Your task is to:.*",
        ]
        
        for pattern in instruction_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()


guardrails_service = GuardrailsService()
