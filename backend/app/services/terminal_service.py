from typing import Dict, Any, Optional, List
import re
import json
from app.services.llm_service import llm_service
from app.services.observability import logger, performance_monitor
from datetime import datetime


class TerminalService:
    """
    Terminal intelligence service for monitoring, analyzing, and assisting with terminal commands.
    Supports PowerShell, WSL, and general terminal analysis.
    """
    
    def __init__(self):
        self.logger = logger
        self.command_patterns = {
            'error': [
                r'error:',
                r'failed',
                r'exception',
                r'cannot',
                r'unable to',
                r'permission denied',
                r'command not found',
                r'no such file'
            ],
            'warning': [
                r'warning:',
                r'deprecated',
                r'notice:'
            ],
            'success': [
                r'success',
                r'completed',
                r'done',
                r'finished'
            ]
        }
    
    async def analyze_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a terminal command and provide insights.
        
        Args:
            command: The terminal command to analyze
            context: Additional context (shell type, directory, etc.)
        """
        try:
            self.logger.info(f"Analyzing command: {command[:50]}...")
            
            analysis = {
                "command": command,
                "command_type": self._classify_command(command),
                "risk_level": self._assess_risk(command),
                "explanation": await self._explain_command(command),
                "suggestions": await self._suggest_improvements(command),
                "potential_issues": self._identify_potential_issues(command),
                "context": context or {}
            }
            
            await performance_monitor.track_agent_performance(
                agent_name="terminal_service",
                operation="analyze_command",
                duration=0.1,  # Placeholder
                success=True
            )
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Command analysis error: {str(e)}")
            await performance_monitor.track_error(e, {"operation": "analyze_command", "command": command})
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_output(self, output: str, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze terminal output to detect errors, warnings, and important information.
        
        Args:
            output: The terminal output to analyze
            command: The command that produced the output (optional)
        """
        try:
            self.logger.info(f"Analyzing terminal output: {len(output)} characters")
            
            analysis = {
                "has_errors": self._detect_errors(output),
                "has_warnings": self._detect_warnings(output),
                "error_details": self._extract_error_details(output),
                "warning_details": self._extract_warning_details(output),
                "success_indicators": self._detect_success(output),
                "recommendations": await self._generate_output_recommendations(output, command),
                "summary": await self._summarize_output(output, command)
            }
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Output analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def explain_error(self, error_message: str, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Explain a terminal error and suggest solutions.
        
        Args:
            error_message: The error message to explain
            command: The command that produced the error (optional)
        """
        try:
            prompt = f"""Explain this terminal error and provide solutions:

Error: {error_message}
Command: {command if command else 'Unknown'}

Provide:
1. What the error means in plain language
2. Common causes of this error
3. Step-by-step solutions to fix it
4. Prevention tips for the future
5. Alternative approaches if applicable"""

            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Explain errors clearly and provide practical solutions."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "explanation": response,
                "error_message": error_message,
                "command": command
            }
            
        except Exception as e:
            self.logger.error(f"Error explanation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def suggest_command(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Suggest a terminal command based on user intent.
        
        Args:
            intent: What the user wants to do
            context: Additional context (current directory, OS, etc.)
        """
        try:
            prompt = f"""Suggest a terminal command for this intent:

Intent: {intent}
Context: {json.dumps(context, indent=2) if context else 'None'}

Provide:
1. The suggested command
2. Explanation of what it does
3. Any required parameters or flags
4. Potential risks or side effects
5. Alternative commands if applicable"""

            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Suggest appropriate commands based on user intent."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "success": True,
                "suggestion": response,
                "intent": intent
            }
            
        except Exception as e:
            self.logger.error(f"Command suggestion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_history(self, history: List[str], limit: int = 10) -> Dict[str, Any]:
        """
        Analyze terminal command history to identify patterns and provide insights.
        
        Args:
            history: List of terminal commands from history
            limit: Number of recent commands to analyze
        """
        try:
            recent_commands = history[-limit:] if len(history) > limit else history
            
            analysis = {
                "command_frequency": self._analyze_command_frequency(recent_commands),
                "common_patterns": self._identify_common_patterns(recent_commands),
                "potential_issues": self._identify_history_issues(recent_commands),
                "productivity_insights": await self._generate_productivity_insights(recent_commands),
                "suggestions": await self._generate_history_suggestions(recent_commands)
            }
            
            return {
                "success": True,
                "analysis": analysis,
                "analyzed_count": len(recent_commands)
            }
            
        except Exception as e:
            self.logger.error(f"History analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _classify_command(self, command: str) -> str:
        """Classify the type of command"""
        command_lower = command.lower().strip()
        
        if command_lower.startswith(('git ', 'hg ', 'svn ')):
            return 'version_control'
        elif command_lower.startswith(('npm ', 'yarn ', 'pip ', 'conda ')):
            return 'package_manager'
        elif command_lower.startswith(('docker ', 'podman ', 'kubectl ')):
            return 'container'
        elif command_lower.startswith(('ls ', 'cd ', 'pwd ', 'mkdir ', 'rm ')):
            return 'file_system'
        elif command_lower.startswith(('grep ', 'find ', 'locate ')):
            return 'search'
        elif command_lower.startswith(('ps ', 'top ', 'htop ', 'kill ')):
            return 'process'
        elif command_lower.startswith(('systemctl ', 'service ')):
            return 'service'
        elif command_lower.startswith(('curl ', 'wget ', 'ssh ')):
            return 'network'
        elif any(char in command for char in ['|', '>', '<', '&', ';']):
            return 'pipeline'
        else:
            return 'general'
    
    def _assess_risk(self, command: str) -> str:
        """Assess the risk level of a command"""
        command_lower = command.lower()
        
        high_risk_patterns = [
            'rm -rf', 'del /', 'format', 'shutdown', 'reboot',
            'dd if=', 'mkfs', 'fdisk', 'chmod 777', 'chown -R'
        ]
        
        medium_risk_patterns = [
            'rm ', 'del ', 'mv ', 'cp ', 'chmod ', 'chown ',
            'kill ', 'pkill ', 'killall '
        ]
        
        for pattern in high_risk_patterns:
            if pattern in command_lower:
                return 'high'
        
        for pattern in medium_risk_patterns:
            if pattern in command_lower:
                return 'medium'
        
        return 'low'
    
    async def _explain_command(self, command: str) -> str:
        """Explain what a command does"""
        try:
            prompt = f"Explain what this terminal command does: {command}"
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Explain commands clearly and concisely."},
                {"role": "user", "content": prompt}
            ])
            return response
        except Exception:
            return f"Command: {command}"
    
    async def _suggest_improvements(self, command: str) -> List[str]:
        """Suggest improvements to a command"""
        try:
            prompt = f"Suggest improvements or alternatives for this command: {command}"
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Suggest command improvements."},
                {"role": "user", "content": prompt}
            ])
            return [response]  # Would parse into multiple suggestions
        except Exception:
            return []
    
    def _identify_potential_issues(self, command: str) -> List[str]:
        """Identify potential issues with a command"""
        issues = []
        command_lower = command.lower()
        
        if 'sudo' in command_lower:
            issues.append("Requires sudo privileges")
        
        if '~' in command and not command.startswith('cd'):
            issues.append("Tilde expansion may not work in all contexts")
        
        if '&' in command_lower and command_lower.endswith('&'):
            issues.append("Command will run in background")
        
        if command_lower.count('|') > 3:
            issues.append("Complex pipeline may be hard to debug")
        
        return issues
    
    def _detect_errors(self, output: str) -> bool:
        """Detect if output contains errors"""
        output_lower = output.lower()
        return any(pattern in output_lower for pattern in self.command_patterns['error'])
    
    def _detect_warnings(self, output: str) -> bool:
        """Detect if output contains warnings"""
        output_lower = output.lower()
        return any(pattern in output_lower for pattern in self.command_patterns['warning'])
    
    def _detect_success(self, output: str) -> bool:
        """Detect if output indicates success"""
        output_lower = output.lower()
        return any(pattern in output_lower for pattern in self.command_patterns['success'])
    
    def _extract_error_details(self, output: str) -> List[str]:
        """Extract error details from output"""
        errors = []
        for pattern in self.command_patterns['error']:
            matches = re.finditer(pattern, output, re.IGNORECASE)
            for match in matches:
                # Get context around the error
                start = max(0, match.start() - 50)
                end = min(len(output), match.end() + 50)
                errors.append(output[start:end].strip())
        return errors[:5]  # Limit to first 5 errors
    
    def _extract_warning_details(self, output: str) -> List[str]:
        """Extract warning details from output"""
        warnings = []
        for pattern in self.command_patterns['warning']:
            matches = re.finditer(pattern, output, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(output), match.end() + 30)
                warnings.append(output[start:end].strip())
        return warnings[:5]  # Limit to first 5 warnings
    
    async def _generate_output_recommendations(self, output: str, command: Optional[str]) -> List[str]:
        """Generate recommendations based on output"""
        if self._detect_errors(output):
            return ["Review the error messages above", "Check command syntax", "Verify permissions"]
        elif self._detect_warnings(output):
            return ["Review warnings", "Consider updating deprecated features"]
        else:
            return []
    
    async def _summarize_output(self, output: str, command: Optional[str]) -> str:
        """Summarize terminal output"""
        try:
            prompt = f"Summarize this terminal output: {output[:500]}..."
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Summarize output concisely."},
                {"role": "user", "content": prompt}
            ])
            return response
        except Exception:
            return output[:200] + "..."
    
    def _analyze_command_frequency(self, commands: List[str]) -> Dict[str, int]:
        """Analyze frequency of command types"""
        frequency = {}
        for cmd in commands:
            cmd_type = self._classify_command(cmd)
            frequency[cmd_type] = frequency.get(cmd_type, 0) + 1
        return frequency
    
    def _identify_common_patterns(self, commands: List[str]) -> List[str]:
        """Identify common patterns in command history"""
        patterns = []
        
        # Check for common command sequences
        for i in range(len(commands) - 1):
            if commands[i].startswith('git ') and commands[i+1].startswith('git '):
                patterns.append("Sequential git operations")
        
        # Check for repeated commands
        from collections import Counter
        cmd_starts = [cmd.split()[0] if cmd.split() else '' for cmd in commands]
        common_starts = Counter(cmd_starts).most_common(3)
        
        for cmd, count in common_starts:
            if count > 1:
                patterns.append(f"Frequent use of {cmd}")
        
        return patterns
    
    def _identify_history_issues(self, commands: List[str]) -> List[str]:
        """Identify potential issues in command history"""
        issues = []
        
        for cmd in commands:
            risk = self._assess_risk(cmd)
            if risk == 'high':
                issues.append(f"High risk command: {cmd[:50]}...")
        
        return issues
    
    async def _generate_productivity_insights(self, commands: List[str]) -> List[str]:
        """Generate productivity insights from command history"""
        try:
            prompt = f"Analyze these terminal commands and provide productivity insights: {commands[:10]}"
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a productivity expert. Analyze command patterns."},
                {"role": "user", "content": prompt}
            ])
            return [response]
        except Exception:
            return []
    
    async def _generate_history_suggestions(self, commands: List[str]) -> List[str]:
        """Generate suggestions based on command history"""
        try:
            prompt = f"Suggest improvements or aliases based on these commands: {commands[:10]}"
            response = await llm_service.generate_response([
                {"role": "system", "content": "You are a terminal expert. Suggest improvements."},
                {"role": "user", "content": prompt}
            ])
            return [response]
        except Exception:
            return []


terminal_service = TerminalService()
