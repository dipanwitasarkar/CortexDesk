from app.mcp.base_mcp import BaseMCP
from typing import Dict, Any, List, Optional
import httpx
import os


class GitHubMCP(BaseMCP):
    """GitHub operations via MCP"""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__("github")
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call GitHub tools"""
        try:
            if tool_name == "get_repo":
                return await self._get_repo(parameters["owner"], parameters["repo"])
            elif tool_name == "list_repos":
                return await self._list_repos(parameters.get("username"))
            elif tool_name == "get_file":
                return await self._get_file(
                    parameters["owner"],
                    parameters["repo"],
                    parameters["path"],
                    parameters.get("branch", "main")
                )
            elif tool_name == "search_code":
                return await self._search_code(
                    parameters["query"],
                    parameters.get("owner"),
                    parameters.get("repo")
                )
            elif tool_name == "get_pr":
                return await self._get_pr(
                    parameters["owner"],
                    parameters["repo"],
                    parameters["pr_number"]
                )
            elif tool_name == "list_prs":
                return await self._list_prs(
                    parameters["owner"],
                    parameters["repo"],
                    parameters.get("state", "open")
                )
            elif tool_name == "get_issue":
                return await self._get_issue(
                    parameters["owner"],
                    parameters["repo"],
                    parameters["issue_number"]
                )
            elif tool_name == "list_issues":
                return await self._list_issues(
                    parameters["owner"],
                    parameters["repo"],
                    parameters.get("state", "open")
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available GitHub tools"""
        return [
            {
                "name": "get_repo",
                "description": "Get repository information",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"}
                }
            },
            {
                "name": "list_repos",
                "description": "List repositories for a user",
                "parameters": {
                    "username": {"type": "string", "description": "GitHub username"}
                }
            },
            {
                "name": "get_file",
                "description": "Get file content from a repository",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "path": {"type": "string", "description": "File path"},
                    "branch": {"type": "string", "description": "Branch name (default: main)"}
                }
            },
            {
                "name": "search_code",
                "description": "Search code across repositories",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "owner": {"type": "string", "description": "Repository owner (optional)"},
                    "repo": {"type": "string", "description": "Repository name (optional)"}
                }
            },
            {
                "name": "get_pr",
                "description": "Get pull request information",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "pr_number": {"type": "integer", "description": "PR number"}
                }
            },
            {
                "name": "list_prs",
                "description": "List pull requests",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "description": "PR state (open/closed/all)"}
                }
            },
            {
                "name": "get_issue",
                "description": "Get issue information",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "issue_number": {"type": "integer", "description": "Issue number"}
                }
            },
            {
                "name": "list_issues",
                "description": "List issues",
                "parameters": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "description": "Issue state (open/closed/all)"}
                }
            }
        ]

    async def _get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def _list_repos(self, username: Optional[str] = None) -> Dict[str, Any]:
        if not username and not self.token:
            return {"error": "Username or token required"}
        
        url = f"{self.base_url}/user/repos" if self.token else f"{self.base_url}/users/{username}/repos"
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return {"repos": response.json()}

    async def _get_file(self, owner: str, repo: str, path: str, branch: str = "main") -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def _search_code(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
        q = query
        if owner:
            q += f" user:{owner}"
        if repo:
            q += f" repo:{owner}/{repo}" if owner else f" repo:{repo}"
        
        url = f"{self.base_url}/search/code"
        params = {"q": q}
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def _get_pr(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def _list_prs(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state}
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return {"pulls": response.json()}

    async def _get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def _list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state}
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return {"issues": response.json()}
