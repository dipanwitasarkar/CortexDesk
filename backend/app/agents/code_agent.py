from app.agents.base_agent import BaseAgent
from app.mcp.filesystem_mcp import FilesystemMCP
from app.mcp.github_mcp import GitHubMCP
from app.services.llm_service import llm_service
from typing import Dict, Any, List, Optional
import json


class CodeAgent(BaseAgent):
    """
    Code Agent - Handles all code-related tasks.
    Responsibilities:
    - Repository search
    - Code explanation
    - Architecture analysis
    - PR analysis
    - Log analysis
    - Root cause analysis
    """
    
    def __init__(self):
        super().__init__(
            name="code",
            description="Handles code-related tasks including repository search, code explanation, and architecture analysis"
        )
        self.filesystem_mcp = FilesystemMCP()
        self.github_mcp = GitHubMCP()

    def get_system_prompt(self) -> str:
        return """You are the Code Agent for a Windows AI Assistant. Your role is to help users with code-related tasks:

1. Search and analyze code repositories
2. Explain code, functions, and architecture
3. Analyze pull requests and code changes
4. Help with debugging and root cause analysis
5. Review code quality and suggest improvements
6. Find usage patterns across codebases

You have access to:
- Filesystem operations (read files, search files, list directories)
- GitHub operations (get repos, search code, analyze PRs)

Be thorough but concise in your analysis. Focus on practical, actionable insights."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process code-related requests"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        context = input_data.get("context", {})
        agent_plan = input_data.get("agent_plan", {})
        
        # Determine the type of code task
        task_type = await self._classify_task(user_message, context)
        
        # Execute based on task type
        if task_type == "repository_search":
            return await self._handle_repository_search(user_message, context)
        elif task_type == "code_explanation":
            return await self._handle_code_explanation(user_message, context)
        elif task_type == "architecture_analysis":
            return await self._handle_architecture_analysis(user_message, context)
        elif task_type == "pr_analysis":
            return await self._handle_pr_analysis(user_message, context)
        elif task_type == "debugging":
            return await self._handle_debugging(user_message, context)
        else:
            return await self._handle_general_code_task(user_message, context)

    async def _classify_task(self, user_message: str, context: Dict[str, Any]) -> str:
        """Classify the type of code task"""
        
        prompt = f"""Classify the following code-related request into one of these categories:
- repository_search: Search for code in repositories
- code_explanation: Explain specific code or functions
- architecture_analysis: Analyze system or component architecture
- pr_analysis: Analyze pull requests or code changes
- debugging: Help debug errors or issues
- general: General code-related questions

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the category name."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        # Clean and return the classification
        return response.strip().lower().replace("-", "_")

    async def _handle_repository_search(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle repository search requests"""
        
        # Extract search parameters from message
        search_params = await self._extract_search_params(user_message)
        
        # Perform search using appropriate MCP
        if search_params.get("use_github"):
            results = await self.github_mcp.call_tool(
                "search_code",
                {
                    "query": search_params["query"],
                    "owner": search_params.get("owner"),
                    "repo": search_params.get("repo")
                }
            )
        else:
            results = await self.filesystem_mcp.call_tool(
                "search_files",
                {
                    "path": search_params.get("path", "."),
                    "pattern": search_params.get("pattern", "*")
                }
            )
        
        # Analyze and summarize results
        summary = await self._summarize_search_results(user_message, results)
        
        return {
            "response": summary,
            "raw_results": results,
            "search_params": search_params
        }

    async def _handle_code_explanation(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code explanation requests"""
        
        # Extract file path and code context
        file_info = await self._extract_file_info(user_message, context)
        
        if file_info.get("file_path"):
            # Read the file
            file_content = await self.filesystem_mcp.call_tool(
                "read_file",
                {"path": file_info["file_path"]}
            )
            
            if "error" in file_content:
                return {
                    "response": f"Could not read file: {file_content['error']}"
                }
            
            code = file_content["content"]
        else:
            code = file_info.get("code_snippet", "")
        
        if not code:
            return {
                "response": "Could not find code to explain. Please provide a file path or code snippet."
            }
        
        # Generate explanation
        explanation_prompt = f"""Explain the following code clearly and concisely:

{code}

User's specific question: {user_message}

Focus on:
1. What the code does
2. Key components and their roles
3. Any important patterns or design decisions
4. Potential issues or improvements"""

        messages = [{"role": "user", "content": explanation_prompt}]
        explanation = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": explanation,
            "file_path": file_info.get("file_path"),
            "code_length": len(code)
        }

    async def _handle_architecture_analysis(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle architecture analysis requests"""
        
        # Get repository structure
        repo_path = context.get("repository_path", ".")
        structure = await self.filesystem_mcp.call_tool(
            "list_directory",
            {"path": repo_path}
        )
        
        # Analyze key files
        analysis_prompt = f"""Analyze the architecture of this codebase based on the following structure:

Repository structure: {json.dumps(structure, indent=2)}

User's specific question: {user_message}

Provide:
1. High-level architecture overview
2. Key components and their relationships
3. Design patterns used
4. Entry points and main flows
5. Any architectural concerns or recommendations"""

        messages = [{"role": "user", "content": analysis_prompt}]
        analysis = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": analysis,
            "structure": structure
        }

    async def _handle_pr_analysis(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request analysis"""
        
        # Extract PR information
        pr_info = await self._extract_pr_info(user_message, context)
        
        if not pr_info.get("owner") or not pr_info.get("repo") or not pr_info.get("pr_number"):
            return {
                "response": "Please provide the repository owner, name, and PR number."
            }
        
        # Get PR details
        pr_details = await self.github_mcp.call_tool(
            "get_pr",
            {
                "owner": pr_info["owner"],
                "repo": pr_info["repo"],
                "pr_number": pr_info["pr_number"]
            }
        )
        
        # Analyze PR
        analysis_prompt = f"""Analyze this pull request:

PR Details: {json.dumps(pr_details, indent=2)}

User's specific question: {user_message}

Provide:
1. Summary of changes
2. Impact assessment
3. Potential issues or risks
4. Testing recommendations
5. Code quality observations"""

        messages = [{"role": "user", "content": analysis_prompt}]
        analysis = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": analysis,
            "pr_details": pr_details
        }

    async def _handle_debugging(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debugging requests"""
        
        # Extract error information
        error_info = await self._extract_error_info(user_message, context)
        
        debugging_prompt = f"""Help debug this issue:

Error/Issue: {user_message}

Context: {json.dumps(error_info, indent=2) if error_info else "None"}

Provide:
1. Root cause analysis
2. Possible solutions
3. Steps to reproduce (if applicable)
4. Prevention recommendations"""

        messages = [{"role": "user", "content": debugging_prompt}]
        solution = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": solution,
            "error_info": error_info
        }

    async def _handle_general_code_task(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general code-related questions"""
        
        try:
            # Use LLM to generate a response
            prompt = f"""Answer this code-related question:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Provide a clear, helpful response with code examples if relevant."""
            
            response = await llm_service.generate_simple_response(
                message=prompt,
                context=context,
                chat_history=[]
            )
            
            return {"response": response}
        except Exception as e:
            # Fallback response if LLM fails
            return {"response": f"I can help with basic code questions about '{user_message}'. Advanced code analysis features are limited with the local gpt2 model. For full functionality, consider using a more powerful LLM."}

    async def _extract_search_params(self, user_message: str) -> Dict[str, Any]:
        """Extract search parameters from user message"""
        
        try:
            prompt = f"""Extract search parameters from this request:

{user_message}

Respond in JSON format with these fields:
- query: the search query
- use_github: true if this is a GitHub search, false otherwise
- owner: repository owner (if applicable)
- repo: repository name (if applicable)
- path: local path to search (if applicable)
- pattern: file pattern (if applicable)"""
            
            response = await llm_service.generate_simple_response(
                message=prompt,
                context={},
                chat_history=[]
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"query": user_message, "use_github": False}
        except Exception as e:
            # Fallback if LLM fails
            return {"query": user_message, "use_github": False}

    async def _extract_file_info(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file information from user message"""
        
        try:
            prompt = f"""Extract file information from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- file_path: path to the file (if mentioned)
- code_snippet: code snippet (if provided in message)"""
            
            response = await llm_service.generate_simple_response(
                message=prompt,
                context=context,
                chat_history=[]
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            # Fallback if LLM fails
            return {}

    async def _extract_pr_info(self, user_message: str) -> Dict[str, Any]:
        """Extract PR information from user message"""
        
        try:
            prompt = f"""Extract pull request information from this request:

{user_message}

Respond in JSON format with these fields:
- owner: repository owner
- repo: repository name
- pr_number: pull request number"""
            
            response = await llm_service.generate_simple_response(
                message=prompt,
                context={},
                chat_history=[]
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            # Fallback if LLM fails
            return {}

    async def _extract_error_info(self, user_message: str) -> Dict[str, Any]:
        """Extract error information from user message"""
        
        try:
            prompt = f"""Extract error information from this request:

{user_message}

Respond in JSON format with these fields:
- error_message: the error message
- stack_trace: stack trace (if provided)
- code_context: relevant code context (if provided)
- environment: environment details (if provided)"""
            
            response = await llm_service.generate_simple_response(
                message=prompt,
                context={},
                chat_history=[]
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {}
        except Exception as e:
            # Fallback if LLM fails
            return {}

    async def _summarize_search_results(self, user_message: str, results: Dict[str, Any]) -> str:
        """Summarize search results"""
        
        prompt = f"""Summarize these search results in response to the user's request:

User request: {user_message}

Search results: {json.dumps(results, indent=2)}

Provide a clear summary highlighting the most relevant findings."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)
