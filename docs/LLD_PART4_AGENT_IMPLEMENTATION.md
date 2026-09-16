# CortexDesk Low-Level Design (LLD) - Part 4: Agent Implementation Details

## Document Overview

This document provides detailed specifications for all agent implementations in the CortexDesk multi-agent system, including orchestration, selection logic, execution logging, memory management, and tool integration.

**Document Parts:**
- Part 1: Architecture & System Design
- Part 2: Data Models & Database Schema
- Part 3: API Specifications
- Part 4: Agent Implementation Details (This document)
- Part 5: Frontend Architecture
- Part 6: Deployment & Infrastructure

---

## 1. Agent System Overview

### 1.1 Agent Architecture

The CortexDesk system uses a hierarchical multi-agent architecture with a supervisor agent that orchestrates specialized sub-agents.

**Agent Hierarchy:**
```
User Request
    ↓
Supervisor Agent (Intent Classification & Orchestration)
    ↓
├── Knowledge Agent (Document search, RAG retrieval)
├── Code Agent (Code analysis, repository search)
├── Windows Agent (Windows automation, file operations)
├── System Agent (System operations, container management)
└── Productivity Agent (Task management, calendar)
    ↓
Result Merging & Response Generation
```

### 1.2 Agent Technology Stack

**Base Framework:**
- Python 3.12
- Transformers 4.36.0 (Hugging Face)
- PyTorch 2.1.0
- Asyncio for async operations

**LLM Integration:**
- Local: GPT-2 (124M parameters)
- Cloud: Groq, RunPod, OpenAI, Anthropic, Azure, Custom (configurable via UI)
- Dynamic configuration switching without backend restart
- Per-user configuration stored in database

**Embedding Model:**
- sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

### 1.3 Agent File Structure

```
backend/app/agents/
├── __init__.py
├── base_agent.py          # Base agent class
├── supervisor_agent.py    # Supervisor agent
├── knowledge_agent.py     # Knowledge agent
├── code_agent.py          # Code agent
├── windows_agent.py       # Windows agent
├── system_agent.py        # System agent
└── productivity_agent.py  # Productivity agent
```

---

## 2. Base Agent Implementation

### 2.1 BaseAgent Class

**File:** `backend/app/agents/base_agent.py`

**Purpose:** Abstract base class for all agents with common functionality.

**Key Methods:**

```python
class BaseAgent:
    def __init__(self, name: str, llm_service):
        self.name = name
        self.llm_service = llm_service
        self.logger = logging.getLogger(f"agent.{name}")
        self.observability_db = observability_db
        
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the agent with input data and context."""
        pass
        
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response using LLM."""
        pass
        
    async def retrieve_memory(
        self,
        query: str,
        memory_type: str = "conversation",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memory from vector database."""
        pass
        
    async def store_memory(
        self,
        content: str,
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store content in memory."""
        pass
        
    async def log_execution(
        self,
        request_id: str,
        status: str,
        execution_time: float,
        result: Optional[Dict[str, Any]] = None
    ):
        """Log agent execution to observability."""
        pass
```

### 2.2 Execution Flow

**Standard Agent Execution:**
1. Receive input data and context
2. Log execution start (observability)
3. Record trace start (observability)
4. Retrieve relevant memory (if needed)
5. Generate response using LLM
6. Store important information in memory
7. Log execution completion (observability)
8. Record trace completion (observability)
9. Return result to supervisor

**Observability Logging:**
```python
async def log_execution(
    self,
    request_id: str,
    status: str,
    execution_time: float,
    result: Optional[Dict[str, Any]] = None
):
    """Log agent execution to observability."""
    await self.observability_db.record_log(
        level="INFO",
        logger_name=self.name,
        message=f"{self.name} agent {status}",
        context={
            "request_id": request_id,
            "execution_time": execution_time,
            "result": result
        }
    )
```

---

## 3. Supervisor Agent

### 3.1 Supervisor Agent Implementation

**File:** `backend/app/agents/supervisor_agent.py`

**Purpose:** Orchestrate sub-agents based on user intent.

**Key Responsibilities:**
- Intent classification
- Agent selection
- Execution plan generation
- Sub-agent orchestration
- Result merging
- Final response generation

### 3.2 Intent Classification

**Keyword-Based Classification:**

```python
AGENT_KEYWORDS = {
    "code": [
        "code", "repository", "git", "function", "class", "bug", "debug",
        "programming", "algorithm", "data structure", "api", "endpoint",
        "refactor", "optimize", "test", "deployment", "ci/cd"
    ],
    "knowledge": [
        "document", "pdf", "search", "find", "what is", "explain",
        "python", "javascript", "react", "node", "database", "sql",
        "how to", "learn", "tutorial", "guide", "overview"
    ],
    "windows": [
        "open", "launch", "screenshot", "clipboard", "file", "folder",
        "application", "program", "window", "desktop", "shortcut",
        "settings", "control panel", "task manager"
    ],
    "system": [
        "docker", "podman", "wsl", "process", "service", "system",
        "terminal", "command", "shell", "bash", "power",
        "network", "ip", "port", "firewall", "log"
    ],
    "productivity": [
        "calendar", "meeting", "task", "email", "journal",
        "schedule", "reminder", "todo", "deadline", "project",
        "report", "summary", "briefing", "status"
    ]
}
```

**Classification Logic:**

```python
def _classify_intent(self, message: str) -> List[str]:
    """Classify user intent based on keywords."""
    message_lower = message.lower()
    selected_agents = []
    
    for agent, keywords in AGENT_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            selected_agents.append(agent)
    
    # Default to knowledge if no match
    if not selected_agents:
        selected_agents = ["knowledge"]
    
    return selected_agents
```

### 3.3 Agent Selection

**Selection Algorithm:**

```python
def _select_agents(self, message: str) -> List[str]:
    """Select appropriate agents based on message content."""
    selected_agents = self._classify_intent(message)
    
    # Log selection
    self.logger.info(f"Selected agents: {selected_agents}")
    
    return selected_agents
```

**Selection Examples:**
- "What is Python?" → ["knowledge"]
- "Write a function to sort an array" → ["code"]
- "Open Notepad" → ["windows"]
- "Check Docker containers" → ["system"]
- "Schedule a meeting" → ["productivity"]

### 3.4 Execution Plan Generation

**Plan Generation:**

```python
def _generate_execution_plan(self, agents: List[str], message: str) -> Dict[str, str]:
    """Generate execution plan for selected agents."""
    plan = {}
    
    for agent in agents:
        plan[agent] = f"Handle aspects related to: {message[:50]}"
    
    return plan
```

**Example Plan:**
```json
{
  "knowledge": "Handle aspects related to: what is python",
  "code": "Handle aspects related to: function implementation"
}
```

### 3.5 Sub-Agent Orchestration

**Orchestration Flow:**

```python
async def _execute_agents(
    self,
    agents: List[str],
    message: str,
    context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Execute selected agents and collect results."""
    results = []
    
    for agent_name in agents:
        try:
            # Get agent instance
            agent = self._get_agent(agent_name)
            
            # Log execution start
            self.logger.info(f"Executing {agent_name} agent")
            
            # Execute agent
            result = await agent.execute(
                input_data={"message": message},
                context=context
            )
            
            # Collect result
            results.append({
                "agent": agent_name,
                "success": True,
                "result": result,
                "execution_time": result.get("execution_time", 0)
            })
            
        except Exception as e:
            # Log error
            self.logger.error(f"Error executing {agent_name}: {str(e)}")
            
            # Collect error result
            results.append({
                "agent": agent_name,
                "success": False,
                "error": str(e),
                "execution_time": 0
            })
    
    return results
```

### 3.6 Result Merging

**Merging Strategy:**

```python
def _merge_results(self, results: List[Dict[str, Any]]) -> str:
    """Merge results from multiple agents."""
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        return "I encountered an error processing your request."
    
    if len(successful_results) == 1:
        return successful_results[0]["result"].get("response", "")
    
    # Multiple agents: combine responses
    combined_response = "Here's what I found:\n\n"
    for result in successful_results:
        agent_name = result["agent"]
        response = result["result"].get("response", "")
        combined_response += f"**{agent_name.title()}**: {response}\n\n"
    
    return combined_response
```

### 3.7 Complete Supervisor Execution

**Full Execution Flow:**

```python
async def process_message(
    self,
    message: str,
    user_id: int,
    chat_id: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process user message through multi-agent system."""
    
    # Generate trace ID
    trace_id = str(uuid.uuid4())
    
    # Log start
    self.logger.info(f"Supervisor agent started processing message: {message}")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="supervisor_agent",
        message=f"Supervisor agent started processing message: {message}",
        context={"trace_id": trace_id, "chat_id": chat_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=trace_id,
        span_id=str(uuid.uuid4()),
        operation_name="supervisor.process",
        service_name="supervisor",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    # Intent classification
    self.logger.info("Starting intent classification and agent selection")
    selected_agents = self._select_agents(message)
    
    # Generate execution plan
    execution_plan = self._generate_execution_plan(selected_agents, message)
    
    # Execute agents
    self.logger.info(f"Executing agents: {selected_agents}")
    agent_results = await self._execute_agents(
        agents=selected_agents,
        message=message,
        context=context or {}
    )
    
    # Merge results
    self.logger.info("Merging agent results and generating final response")
    final_response = self._merge_results(agent_results)
    
    # Record trace completion
    await self.observability_db.record_trace(
        trace_id=trace_id,
        span_id=str(uuid.uuid4()),
        operation_name="supervisor.process",
        service_name="supervisor",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        status="success",
        metadata={
            "agents_used": selected_agents,
            "agent_results": agent_results
        }
    )
    
    # Log completion
    self.logger.info(f"Supervisor agent completed successfully with {len(selected_agents)} agents")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="supervisor_agent",
        message="Supervisor agent completed successfully",
        context={
            "trace_id": trace_id,
            "agents_used": selected_agents,
            "agent_count": len(selected_agents)
        }
    )
    
    return {
        "response": final_response,
        "agents_used": selected_agents,
        "agent_results": agent_results,
        "execution_plan": execution_plan,
        "chat_id": chat_id
    }
```

---

## 4. Knowledge Agent

### 4.1 Knowledge Agent Implementation

**File:** `backend/app/agents/knowledge_agent.py`

**Purpose:** Handle document search, RAG retrieval, and knowledge synthesis.

**Key Capabilities:**
- Document search using RAG
- Knowledge synthesis from multiple sources
- Question answering
- Document summarization

### 4.2 Document Search

**RAG Retrieval:**

```python
async def search_documents(
    self,
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Search documents using RAG."""
    
    # Generate query embedding
    query_embedding = await self.llm_service.generate_embedding(query)
    
    # Search Qdrant
    search_results = await self.qdrant_manager.search(
        collection_name="documents",
        query_vector=query_embedding,
        limit=limit
    )
    
    # Format results
    formatted_results = []
    for result in search_results:
        formatted_results.append({
            "content": result.payload.get("content", ""),
            "title": result.payload.get("title", ""),
            "score": result.score,
            "document_id": result.payload.get("document_id")
        })
    
    return formatted_results
```

### 4.3 Knowledge Synthesis

**Synthesis Logic:**

```python
async def synthesize_knowledge(
    self,
    query: str,
    search_results: List[Dict[str, Any]]
) -> str:
    """Synthesize knowledge from search results."""
    
    if not search_results:
        return "I couldn't find relevant information in your documents."
    
    # Build context from search results
    context = "\n\n".join([
        f"Document: {result['title']}\n{result['content']}"
        for result in search_results
    ])
    
    # Generate response using LLM
    prompt = f"""
Based on the following documents, answer the user's question.

Documents:
{context}

Question: {query}

Provide a comprehensive answer based on the documents.
"""
    
    response = await self.llm_service.generate_response(prompt)
    
    return response
```

### 4.4 Knowledge Agent Execution

**Execution Flow:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute knowledge agent."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log start
    self.logger.info(f"Knowledge agent started processing")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="knowledge_agent",
        message="Knowledge agent started processing",
        context={"request_id": request_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=context.get("trace_id", str(uuid.uuid4())),
        span_id=request_id,
        operation_name="knowledge.execute",
        service_name="knowledge",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    try:
        message = input_data.get("message", "")
        
        # Search documents
        search_results = await self.search_documents(message)
        
        # Synthesize knowledge
        response = await self.synthesize_knowledge(message, search_results)
        
        execution_time = time.time() - start_time
        
        # Log completion
        self.logger.info(f"Knowledge agent completed successfully")
        await self.observability_db.record_log(
            level="INFO",
            logger_name="knowledge_agent",
            message="Knowledge agent completed successfully",
            context={
                "request_id": request_id,
                "execution_time": execution_time
            }
        )
        
        # Record trace completion
        await self.observability_db.record_trace(
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            span_id=request_id,
            operation_name="knowledge.execute",
            service_name="knowledge",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=execution_time * 1000,
            status="success",
            metadata={
                "agent": "knowledge",
                "search_results_count": len(search_results)
            }
        )
        
        return {
            "success": True,
            "response": response,
            "agent_used": "knowledge",
            "metadata": {
                "search_results": search_results,
                "execution_time": execution_time
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        self.logger.error(f"Knowledge agent failed: {str(e)}")
        await self.observability_db.record_log(
            level="ERROR",
            logger_name="knowledge_agent",
            message=f"Knowledge agent failed: {str(e)}",
            context={"request_id": request_id}
        )
        
        return {
            "success": False,
            "error": str(e),
            "agent_used": "knowledge",
            "metadata": {"execution_time": execution_time}
        }
```

---

## 5. Code Agent

### 5.1 Code Agent Implementation

**File:** `backend/app/agents/code_agent.py`

**Purpose:** Handle code analysis, repository search, and code explanation.

**Key Capabilities:**
- Code explanation
- Repository search
- Bug analysis
- Code review
- Architecture analysis

### 5.2 Code Analysis

**Analysis Logic:**

```python
async def analyze_code(
    self,
    code: str,
    language: str = "python"
) -> Dict[str, Any]:
    """Analyze code and provide insights."""
    
    # Generate analysis prompt
    prompt = f"""
Analyze the following {language} code:

```{language}
{code}
```

Provide:
1. Code summary
2. Key functions/classes
3. Potential issues
4. Suggestions for improvement
"""
    
    # Generate response
    response = await self.llm_service.generate_response(prompt)
    
    return {
        "analysis": response,
        "language": language
    }
```

### 5.3 Repository Search

**Search Implementation:**

```python
async def search_repository(
    self,
    query: str,
    repository_path: str
) -> List[Dict[str, Any]]:
    """Search repository for relevant code."""
    
    # Use ripgrep for fast search
    results = []
    
    # Search for files matching query
    for root, dirs, files in os.walk(repository_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp')):
                file_path = os.path.join(root, file)
                
                # Read file content
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check if query matches
                    if query.lower() in content.lower():
                        results.append({
                            "file_path": file_path,
                            "content": content[:500],  # First 500 chars
                            "match_count": content.lower().count(query.lower())
                        })
    
    # Sort by match count
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return results[:10]  # Return top 10 results
```

### 5.4 Code Agent Execution

**Execution Flow:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute code agent."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log start
    self.logger.info(f"Code agent started processing")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="code_agent",
        message="Code agent started processing",
        context={"request_id": request_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=context.get("trace_id", str(uuid.uuid4())),
        span_id=request_id,
        operation_name="code.execute",
        service_name="code",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    try:
        message = input_data.get("message", "")
        
        # Analyze code in message
        analysis = await self.analyze_code(message)
        
        execution_time = time.time() - start_time
        
        # Log completion
        self.logger.info(f"Code agent completed successfully")
        await self.observability_db.record_log(
            level="INFO",
            logger_name="code_agent",
            message="Code agent completed successfully",
            context={
                "request_id": request_id,
                "execution_time": execution_time
            }
        )
        
        # Record trace completion
        await self.observability_db.record_trace(
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            span_id=request_id,
            operation_name="code.execute",
            service_name="code",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=execution_time * 1000,
            status="success",
            metadata={"agent": "code"}
        )
        
        return {
            "success": True,
            "response": analysis["analysis"],
            "agent_used": "code",
            "metadata": {
                "language": analysis["language"],
                "execution_time": execution_time
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        self.logger.error(f"Code agent failed: {str(e)}")
        await self.observability_db.record_log(
            level="ERROR",
            logger_name="code_agent",
            message=f"Code agent failed: {str(e)}",
            context={"request_id": request_id}
        )
        
        return {
            "success": False,
            "error": str(e),
            "agent_used": "code",
            "metadata": {"execution_time": execution_time}
        }
```

---

## 6. Windows Agent

### 6.1 Windows Agent Implementation

**File:** `backend/app/agents/windows_agent.py`

**Purpose:** Handle Windows automation, file operations, and application control.

**Key Capabilities:**
- Application launch and control
- File search and management
- Screenshot capture
- Clipboard management
- Window management

### 6.2 Application Control

**Launch Application:**

```python
async def launch_application(
    self,
    app_name: str
) -> Dict[str, Any]:
    """Launch Windows application."""
    
    try:
        # Use subprocess to launch application
        process = subprocess.Popen(
            ["start", app_name],
            shell=True
        )
        
        return {
            "success": True,
            "message": f"Launched {app_name}",
            "pid": process.pid
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 6.3 File Operations

**File Search:**

```python
async def search_files(
    self,
    query: str,
    search_path: str = "C:\\"
) -> List[Dict[str, Any]]:
    """Search for files matching query."""
    
    results = []
    
    # Use os.walk for file search
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if query.lower() in file.lower():
                file_path = os.path.join(root, file)
                results.append({
                    "file_path": file_path,
                    "file_name": file,
                    "size": os.path.getsize(file_path)
                })
                
                # Limit results
                if len(results) >= 50:
                    return results
    
    return results
```

### 6.4 Screenshot Capture

**Capture Screenshot:**

```python
async def capture_screenshot(
    self,
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """Capture screenshot."""
    
    try:
        # Use pyautogui for screenshot
        import pyautogui
        screenshot = pyautogui.screenshot()
        
        if save_path:
            screenshot.save(save_path)
        else:
            # Save to temp directory
            import tempfile
            save_path = os.path.join(tempfile.gettempdir(), "screenshot.png")
            screenshot.save(save_path)
        
        return {
            "success": True,
            "path": save_path,
            "size": screenshot.size
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 6.5 Windows Agent Execution

**Execution Flow:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute windows agent."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log start
    self.logger.info(f"Windows agent started processing")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="windows_agent",
        message="Windows agent started processing",
        context={"request_id": request_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=context.get("trace_id", str(uuid.uuid4())),
        span_id=request_id,
        operation_name="windows.execute",
        service_name="windows",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    try:
        message = input_data.get("message", "")
        
        # Parse intent
        if "open" in message.lower():
            # Extract app name
            app_name = message.lower().replace("open", "").strip()
            result = await self.launch_application(app_name)
            response = result.get("message", "Operation completed")
        else:
            # Generate response using LLM
            response = await self.llm_service.generate_response(
                f"Help with Windows automation: {message}"
            )
        
        execution_time = time.time() - start_time
        
        # Log completion
        self.logger.info(f"Windows agent completed successfully")
        await self.observability_db.record_log(
            level="INFO",
            logger_name="windows_agent",
            message="Windows agent completed successfully",
            context={
                "request_id": request_id,
                "execution_time": execution_time
            }
        )
        
        # Record trace completion
        await self.observability_db.record_trace(
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            span_id=request_id,
            operation_name="windows.execute",
            service_name="windows",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=execution_time * 1000,
            status="success",
            metadata={"agent": "windows"}
        )
        
        return {
            "success": True,
            "response": response,
            "agent_used": "windows",
            "metadata": {"execution_time": execution_time}
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        self.logger.error(f"Windows agent failed: {str(e)}")
        await self.observability_db.record_log(
            level="ERROR",
            logger_name="windows_agent",
            message=f"Windows agent failed: {str(e)}",
            context={"request_id": request_id}
        )
        
        return {
            "success": False,
            "error": str(e),
            "agent_used": "windows",
            "metadata": {"execution_time": execution_time}
        }
```

---

## 7. System Agent

### 7.1 System Agent Implementation

**File:** `backend/app/agents/system_agent.py`

**Purpose:** Handle system operations, container management, and terminal intelligence.

**Key Capabilities:**
- Container management (Docker/Podman)
- Process monitoring
- Terminal command analysis
- System diagnostics
- Log analysis

### 7.2 Container Management

**List Containers:**

```python
async def list_containers(
    self,
    container_type: str = "docker"
) -> List[Dict[str, Any]]:
    """List running containers."""
    
    try:
        if container_type == "docker":
            # Use Docker API
            import docker
            client = docker.from_env()
            containers = client.containers.list()
            
            return [
                {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown"
                }
                for container in containers
            ]
        elif container_type == "podman":
            # Use Podman CLI
            result = subprocess.run(
                ["podman", "ps", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            import json
            containers = json.loads(result.stdout)
            
            return containers
        
    except Exception as e:
        self.logger.error(f"Failed to list containers: {str(e)}")
        return []
```

### 7.3 Process Monitoring

**List Processes:**

```python
async def list_processes(
    self,
    filter_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List system processes."""
    
    try:
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                
                # Filter by name if provided
                if filter_name and filter_name.lower() not in proc_info['name'].lower():
                    continue
                
                processes.append({
                    "pid": proc_info['pid'],
                    "name": proc_info['name'],
                    "cpu_percent": proc_info['cpu_percent'],
                    "memory_percent": proc_info['memory_percent']
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes[:50]  # Return top 50
        
    except Exception as e:
        self.logger.error(f"Failed to list processes: {str(e)}")
        return []
```

### 7.4 System Agent Execution

**Execution Flow:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute system agent."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log start
    self.logger.info(f"System agent started processing")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="system_agent",
        message="System agent started processing",
        context={"request_id": request_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=context.get("trace_id", str(uuid.uuid4())),
        span_id=request_id,
        operation_name="system.execute",
        service_name="system",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    try:
        message = input_data.get("message", "")
        
        # Parse intent
        if "docker" in message.lower() or "container" in message.lower():
            containers = await self.list_containers()
            response = f"Found {len(containers)} running containers:\n"
            for container in containers:
                response += f"- {container['name']} ({container['status']})\n"
        else:
            # Generate response using LLM
            response = await self.llm_service.generate_response(
                f"Help with system operations: {message}"
            )
        
        execution_time = time.time() - start_time
        
        # Log completion
        self.logger.info(f"System agent completed successfully")
        await self.observability_db.record_log(
            level="INFO",
            logger_name="system_agent",
            message="System agent completed successfully",
            context={
                "request_id": request_id,
                "execution_time": execution_time
            }
        )
        
        # Record trace completion
        await self.observability_db.record_trace(
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            span_id=request_id,
            operation_name="system.execute",
            service_name="system",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=execution_time * 1000,
            status="success",
            metadata={"agent": "system"}
        )
        
        return {
            "success": True,
            "response": response,
            "agent_used": "system",
            "metadata": {"execution_time": execution_time}
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        self.logger.error(f"System agent failed: {str(e)}")
        await self.observability_db.record_log(
            level="ERROR",
            logger_name="system_agent",
            message=f"System agent failed: {str(e)}",
            context={"request_id": request_id}
        )
        
        return {
            "success": False,
            "error": str(e),
            "agent_used": "system",
            "metadata": {"execution_time": execution_time}
        }
```

---

## 8. Productivity Agent

### 8.1 Productivity Agent Implementation

**File:** `backend/app/agents/productivity_agent.py`

**Purpose:** Handle task management, calendar operations, and productivity features.

**Key Capabilities:**
- Task management
- Calendar integration
- Work journal
- Status reports
- Daily briefings

### 8.2 Task Management

**Create Task:**

```python
async def create_task(
    self,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new task."""
    
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "due_date": due_date,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store in Redis
    await redis_manager.set(
        f"task:{task['id']}",
        json.dumps(task)
    )
    
    return task
```

### 8.3 Productivity Agent Execution

**Execution Flow:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute productivity agent."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log start
    self.logger.info(f"Productivity agent started processing")
    await self.observability_db.record_log(
        level="INFO",
        logger_name="productivity_agent",
        message="Productivity agent started processing",
        context={"request_id": request_id}
    )
    
    # Record trace start
    await self.observability_db.record_trace(
        trace_id=context.get("trace_id", str(uuid.uuid4())),
        span_id=request_id,
        operation_name="productivity.execute",
        service_name="productivity",
        start_time=datetime.utcnow(),
        status="running"
    )
    
    try:
        message = input_data.get("message", "")
        
        # Generate response using LLM
        response = await self.llm_service.generate_response(
            f"Help with productivity: {message}"
        )
        
        execution_time = time.time() - start_time
        
        # Log completion
        self.logger.info(f"Productivity agent completed successfully")
        await self.observability_db.record_log(
            level="INFO",
            logger_name="productivity_agent",
            message="Productivity agent completed successfully",
            context={
                "request_id": request_id,
                "execution_time": execution_time
            }
        )
        
        # Record trace completion
        await self.observability_db.record_trace(
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            span_id=request_id,
            operation_name="productivity.execute",
            service_name="productivity",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_ms=execution_time * 1000,
            status="success",
            metadata={"agent": "productivity"}
        )
        
        return {
            "success": True,
            "response": response,
            "agent_used": "productivity",
            "metadata": {"execution_time": execution_time}
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        self.logger.error(f"Productivity agent failed: {str(e)}")
        await self.observability_db.record_log(
            level="ERROR",
            logger_name="productivity_agent",
            message=f"Productivity agent failed: {str(e)}",
            context={"request_id": request_id}
        )
        
        return {
            "success": False,
            "error": str(e),
            "agent_used": "productivity",
            "metadata": {"execution_time": execution_time}
        }
```

---

## 9. Agent Memory Management

### 9.1 Memory Storage

**Store Memory:**

```python
async def store_memory(
    self,
    content: str,
    memory_type: str = "conversation",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store content in memory."""
    
    # Generate embedding
    embedding = await self.llm_service.generate_embedding(content)
    
    # Store in PostgreSQL
    memory = Memory(
        user_id=metadata.get("user_id", 1),
        memory_type=memory_type,
        content=content,
        embedding_vector=embedding,
        metadata=json.dumps(metadata or {})
    )
    
    async for db in get_async_db():
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
    
    # Store in Qdrant
    await self.qdrant_manager.insert_points(
        collection_name="ai_assistant_memory",
        points=[{
            "id": str(hash(content)),
            "vector": embedding,
            "payload": {
                "memory_type": memory_type,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                **metadata
            }
        }]
    )
    
    return str(memory.id)
```

### 9.2 Memory Retrieval

**Retrieve Memory:**

```python
async def retrieve_memory(
    self,
    query: str,
    memory_type: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Retrieve relevant memory."""
    
    # Generate query embedding
    query_embedding = await self.llm_service.generate_embedding(query)
    
    # Search Qdrant
    search_results = await self.qdrant_manager.search(
        collection_name="ai_assistant_memory",
        query_vector=query_embedding,
        limit=limit,
        filter={"memory_type": memory_type} if memory_type else None
    )
    
    # Format results
    formatted_results = []
    for result in search_results:
        formatted_results.append({
            "content": result.payload.get("content", ""),
            "memory_type": result.payload.get("memory_type", ""),
            "score": result.score,
            "timestamp": result.payload.get("timestamp", "")
        })
    
    return formatted_results
```

---

## 10. Agent Tool Integration

### 10.1 Tool System

**Tool Definition:**

```python
class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        return await self.func(**kwargs)
```

**Tool Registration:**

```python
class BaseAgent:
    def __init__(self, name: str, llm_service):
        self.name = name
        self.llm_service = llm_service
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register agent-specific tools."""
        pass
    
    def register_tool(self, tool: Tool):
        """Register a tool for this agent."""
        self.tools[tool.name] = tool
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        return await tool.execute(**kwargs)
```

### 10.2 Tool Examples

**Knowledge Agent Tools:**

```python
def _register_tools(self):
    """Register knowledge agent tools."""
    
    # Document search tool
    self.register_tool(Tool(
        name="search_documents",
        description="Search documents for relevant information",
        func=self.search_documents
    ))
    
    # Document summary tool
    self.register_tool(Tool(
        name="summarize_document",
        description="Summarize a document",
        func=self.summarize_document
    ))
```

**Code Agent Tools:**

```python
def _register_tools(self):
    """Register code agent tools."""
    
    # Code analysis tool
    self.register_tool(Tool(
        name="analyze_code",
        description="Analyze code and provide insights",
        func=self.analyze_code
    ))
    
    # Repository search tool
    self.register_tool(Tool(
        name="search_repository",
        description="Search repository for relevant code",
        func=self.search_repository
    ))
```

---

## 11. Agent Error Handling

### 11.1 Error Types

**Agent-Specific Errors:**

```python
class AgentError(Exception):
    """Base class for agent errors."""
    pass

class AgentExecutionError(AgentError):
    """Error during agent execution."""
    pass

class AgentTimeoutError(AgentError):
    """Agent execution timeout."""
    pass

class AgentMemoryError(AgentError):
    """Error in memory operations."""
    pass

class AgentToolError(AgentError):
    """Error in tool execution."""
    pass
```

### 11.2 Error Handling Strategy

**Try-Catch Pattern:**

```python
async def execute(
    self,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute agent with error handling."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Execute agent logic
        result = await self._execute_internal(input_data, context)
        
        execution_time = time.time() - start_time
        
        # Log success
        await self.log_execution(request_id, "success", execution_time, result)
        
        return result
        
    except AgentTimeoutError as e:
        execution_time = time.time() - start_time
        
        # Log timeout
        await self.log_execution(request_id, "timeout", execution_time)
        
        return {
            "success": False,
            "error": f"Agent execution timeout: {str(e)}",
            "agent_used": self.name
        }
        
    except AgentToolError as e:
        execution_time = time.time() - start_time
        
        # Log tool error
        await self.log_execution(request_id, "tool_error", execution_time)
        
        return {
            "success": False,
            "error": f"Tool execution error: {str(e)}",
            "agent_used": self.name
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log unexpected error
        await self.log_execution(request_id, "error", execution_time)
        
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "agent_used": self.name
        }
```

---

## 12. Agent Performance Optimization

### 12.1 Caching Strategy

**Response Caching:**

```python
async def generate_response(
    self,
    prompt: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Generate response with caching."""
    
    # Generate cache key
    cache_key = f"response:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    # Check cache
    cached_response = await redis_manager.get(cache_key)
    if cached_response:
        return json.loads(cached_response)
    
    # Generate response
    response = await self.llm_service.generate_response(prompt)
    
    # Cache response
    await redis_manager.set(
        cache_key,
        json.dumps(response),
        ex=3600  # 1 hour TTL
    )
    
    return response
```

### 12.2 Batch Processing

**Batch Memory Retrieval:**

```python
async def retrieve_memory_batch(
    self,
    queries: List[str],
    limit: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieve memory for multiple queries."""
    
    # Generate embeddings for all queries
    embeddings = await asyncio.gather(*[
        self.llm_service.generate_embedding(query)
        for query in queries
    ])
    
    # Search Qdrant for each query
    results = {}
    for query, embedding in zip(queries, embeddings):
        search_results = await self.qdrant_manager.search(
            collection_name="ai_assistant_memory",
            query_vector=embedding,
            limit=limit
        )
        results[query] = search_results
    
    return results
```

---

## 13. Agent Testing

### 13.1 Unit Testing

**Test Example:**

```python
import pytest
from app.agents.knowledge_agent import KnowledgeAgent

@pytest.mark.asyncio
async def test_knowledge_agent_search():
    """Test knowledge agent document search."""
    
    agent = KnowledgeAgent(llm_service=mock_llm_service)
    
    results = await agent.search_documents("Python programming")
    
    assert len(results) > 0
    assert all("content" in result for result in results)
    assert all("score" in result for result in results)
```

### 13.2 Integration Testing

**Test Example:**

```python
@pytest.mark.asyncio
async def test_supervisor_agent_orchestration():
    """Test supervisor agent orchestration."""
    
    supervisor = SupervisorAgent(llm_service=mock_llm_service)
    
    result = await supervisor.process_message(
        message="What is Python?",
        user_id=1
    )
    
    assert "response" in result
    assert "agents_used" in result
    assert "knowledge" in result["agents_used"]
```

---

## 14. Agent Monitoring

### 14.1 Metrics Collection

**Agent Execution Metrics:**

```python
async def log_execution(
    self,
    request_id: str,
    status: str,
    execution_time: float,
    result: Optional[Dict[str, Any]] = None
):
    """Log agent execution and collect metrics."""
    
    # Log to observability
    await self.observability_db.record_log(
        level="INFO",
        logger_name=self.name,
        message=f"{self.name} agent {status}",
        context={
            "request_id": request_id,
            "execution_time": execution_time,
            "result": result
        }
    )
    
    # Record metric
    await self.observability_db.record_metric(
        metric_name=f"agent.{self.name}.{status}",
        metric_value=1.0,
        metric_type="counter",
        tags={"agent": self.name}
    )
    
    # Record execution time metric
    await self.observability_db.record_metric(
        metric_name=f"agent.{self.name}.execution_time",
        metric_value=execution_time,
        metric_type="gauge",
        tags={"agent": self.name}
    )
```

### 14.2 Performance Tracking

**Performance Metrics:**

- Agent execution time (p50, p95, p99)
- Agent success rate
- Agent error rate
- Agent memory usage
- Agent tool execution time

---

## 15. Agent Configuration

### 15.1 Agent Configuration

**Configuration File:**

```python
AGENT_CONFIG = {
    "supervisor": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True
    },
    "knowledge": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True,
        "rag_top_k": 5,
        "rag_threshold": 0.7
    },
    "code": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True,
        "max_file_size": 1024 * 1024  # 1MB
    },
    "windows": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True
    },
    "system": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True
    },
    "productivity": {
        "timeout": 30,
        "max_retries": 3,
        "enable_logging": True
    }
}
```

### 15.2 Dynamic Configuration

**Update Configuration:**

```python
def update_agent_config(agent_name: str, config: Dict[str, Any]):
    """Update agent configuration dynamically."""
    
    if agent_name in AGENT_CONFIG:
        AGENT_CONFIG[agent_name].update(config)
    else:
        raise ValueError(f"Agent {agent_name} not found")
```

---

## 16. Agent Future Enhancements

### 16.1 Planned Features

**Advanced Intent Classification:**
- Use LLM for intent classification instead of keywords
- Support multi-intent detection
- Context-aware intent classification

**Improved Orchestration:**
- Parallel agent execution
- Agent collaboration
- Dynamic agent selection based on performance

**Enhanced Memory:**
- Long-term memory with importance scoring
- Memory consolidation
- Memory pruning

**Tool Integration:**
- MCP tool integration
- Custom tool registration
- Tool composition

---

**End of Part 4: Agent Implementation Details**

Continue to Part 5: Frontend Architecture
