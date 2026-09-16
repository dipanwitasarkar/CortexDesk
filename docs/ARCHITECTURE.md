# Windows AI Assistant - Architecture Documentation

## System Overview

The Windows AI Assistant is a multi-agent AI operating system designed to run locally on Windows laptops while using Dell-hosted LLMs for inference. The system follows a local-first data storage approach, keeping all memory, indexing, agent orchestration, and user data on the local machine.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Electron UI                              │
│                   (React + TypeScript)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│                  (Python 3.12+)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Supervisor Agent                              │
│              (Intent & Orchestration)                        │
└────┬────────┬────────┬────────┬────────┬────────┬───────────┘
     │        │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼        ▼
┌────────┐ ┌───────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│  Code  │ │Knowledge│ │Windows │ │ System │ │Productivity│
│ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │  Agent   │
└───┬────┘ └───┬───┘ └───┬────┘ └───┬────┘ └────┬─────┘
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Filesystem│ │  GitHub  │ │PostgreSQL│ │PowerShell│      │
│  │   MCP    │ │   MCP    │ │   MCP    │ │   MCP    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dell LLM Endpoint                           │
│              (OpenAI-Compatible API)                         │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Memory Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │PostgreSQL│ │  Redis   │ │  Qdrant  │                     │
│  │ (History)│ │ (Cache)  │ │ (RAG)    │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend (Electron + React)

**Purpose**: User interface and interaction layer

**Components**:
- **Electron Main Process**: Application lifecycle, window management
- **React UI**: Chat interface, sidebar, settings
- **State Management**: React hooks for local state
- **API Client**: Axios for HTTP communication

**Key Features**:
- Persistent chat interface
- Real-time streaming responses
- Screenshot capture integration
- File upload interface
- Settings management

### 2. Backend (FastAPI)

**Purpose**: API server, agent orchestration, business logic

**Components**:
- **API Layer**: RESTful endpoints for chat, messages, documents
- **Agent Layer**: Multi-agent system with supervisor pattern
- **Service Layer**: Business logic (LLM, memory, RAG)
- **Data Layer**: Database models and repositories

**Key Features**:
- Async/await for high performance
- CORS configuration for Electron
- Request validation with Pydantic
- Error handling and logging

### 3. Agent System

#### Supervisor Agent
- **Responsibility**: Intent understanding, agent selection, result merging
- **Input**: User message, context
- **Output**: Coordinated response from sub-agents
- **Logic**: Classifies intent, creates execution plan, delegates to agents

#### Code Agent
- **Responsibility**: Code-related tasks
- **Tools**: Filesystem MCP, GitHub MCP
- **Capabilities**: Repository search, code explanation, PR analysis

#### Knowledge Agent
- **Responsibility**: Knowledge retrieval and synthesis
- **Tools**: Qdrant (RAG), memory service
- **Capabilities**: Document search, RAG retrieval, knowledge synthesis

#### Windows Agent
- **Responsibility**: Windows automation
- **Tools**: PowerShell MCP, Filesystem MCP
- **Capabilities**: Application control, file search, clipboard, screenshots

#### System Agent
- **Responsibility**: System administration
- **Tools**: PowerShell MCP
- **Capabilities**: WSL management, container management, process monitoring

#### Productivity Agent
- **Responsibility**: Productivity and work management
- **Tools**: Memory service
- **Capabilities**: Calendar, tasks, emails, work journal, status reports

### 4. MCP Layer (Model Context Protocol)

**Purpose**: Standardized interface for external tools and services

**Implementations**:
- **Filesystem MCP**: Local file operations
- **GitHub MCP**: GitHub API integration
- **PostgreSQL MCP**: Database operations
- **PowerShell MCP**: Windows automation

**Architecture**:
```python
class BaseMCP(ABC):
    @abstractmethod
    async def call_tool(tool_name: str, parameters: dict) -> dict
    @abstractmethod
    async def list_tools() -> list[dict]
    async def health_check() -> bool
```

### 5. Memory Layer

#### PostgreSQL (Source of Truth)
- **Purpose**: Persistent storage
- **Data**: Users, chats, messages, documents, memories, agent executions
- **Schema**: Relational with proper indexes
- **Connection**: Async SQLAlchemy

#### Redis (Short-Term Memory)
- **Purpose**: Fast cache and session state
- **Data**: Conversation context, agent state, response cache
- **TTL**: Configurable expiration
- **Connection**: Async Redis client

#### Qdrant (Long-Term Memory)
- **Purpose**: Semantic search and RAG
- **Data**: Document embeddings, memories
- **Indexing**: Vector similarity search
- **Connection**: Qdrant client

### 6. LLM Integration

**Dell LLM Integration**:
- **Protocol**: OpenAI-compatible API
- **Abstraction**: LangChain OpenAI integration
- **Models**: Configurable model names
- **Streaming**: Supported for real-time responses

**Service Architecture**:
```python
class LLMService:
    def __init__(self):
        self.chat_model = ChatOpenAI(...)  # Dell endpoint
        self.embedding_model = OpenAIEmbeddings(...)  # Dell endpoint
    
    async def generate_response(messages: list) -> str
    async def generate_embedding(text: str) -> list[float]
    async def stream_response(messages: list, callback: callable)
```

## Data Flow

### 1. User Message Flow

```
User Input (Electron UI)
    ↓
HTTP POST /api/v1/assistant
    ↓
FastAPI Backend
    ↓
Supervisor Agent (Intent Classification)
    ↓
Agent Selection & Planning
    ↓
Sub-Agent Execution (with MCP tools)
    ↓
Result Merging
    ↓
Response Generation (Dell LLM)
    ↓
Store in PostgreSQL & Redis
    ↓
Return to Frontend
    ↓
Display in UI
```

### 2. RAG Query Flow

```
User Query
    ↓
Generate Embedding (Dell LLM)
    ↓
Search Qdrant (Vector Similarity)
    ↓
Retrieve Relevant Documents
    ↓
Construct Prompt with Context
    ↓
Generate Response (Dell LLM)
    ↓
Return Answer with Sources
```

### 3. Memory Storage Flow

```
New Information
    ↓
Generate Embedding
    ↓
Store in PostgreSQL (metadata)
    ↓
Store in Qdrant (vector + payload)
    ↓
Cache in Redis (if recent)
    ↓
Update Embedding ID in PostgreSQL
```

## Security Architecture

### 1. Input Guardrails
- **Prompt Injection Detection**: Pattern matching and LLM-based detection
- **Jailbreak Prevention**: System prompt hardening
- **Sensitive Data Detection**: Regex patterns for PII
- **Input Validation**: Pydantic schema validation

### 2. Tool Guardrails
- **Safe Operations**: Read operations auto-approved
- **Medium Risk**: Email drafting, ticket creation (ask confirmation)
- **High Risk**: File deletion, system changes (explicit approval)

### 3. Data Security
- **Local-First**: All data stored locally
- **Encryption**: At-rest encryption for sensitive data
- **Access Control**: User-based access control
- **API Security**: CORS, rate limiting, authentication

## Performance Optimization

### 1. Caching Strategy
- **Redis Cache**: LLM responses, agent states
- **TTL Configuration**: Based on data volatility
- **Cache Invalidation**: On data updates

### 2. Database Optimization
- **Indexing**: Proper indexes on frequent queries
- **Connection Pooling**: Async connection management
- **Query Optimization**: Efficient SQL queries

### 3. Async Operations
- **Async/Await**: Non-blocking I/O operations
- **Concurrent Agents**: Parallel agent execution
- **Streaming Responses**: Real-time LLM streaming

## Scalability Considerations

### 1. Horizontal Scaling
- **Stateless API**: Multiple backend instances
- **Load Balancing**: Distribute requests
- **Session Management**: Redis for shared state

### 2. Vertical Scaling
- **Resource Monitoring**: CPU, memory, disk usage
- **Connection Limits**: Database and Redis limits
- **Queue Management**: Background job processing

### 3. Data Scaling
- **Database Sharding**: For large datasets
- **Qdrant Scaling**: Distributed vector database
- **File Storage**: Object storage for documents

## Monitoring & Observability

### 1. Logging
- **Structured Logging**: JSON format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Manage log file sizes

### 2. Metrics
- **Agent Performance**: Execution time, success rate
- **LLM Usage**: Token count, cost tracking
- **System Health**: Database, Redis, Qdrant status

### 3. Tracing
- **Request Tracing**: End-to-end request tracking
- **Agent Execution**: Agent path and tool calls
- **Error Tracking**: Exception tracking and reporting

## Deployment Architecture

### Local Development
```
Windows Laptop
├── Electron App (Frontend)
├── FastAPI Server (Backend)
├── Podman/Docker (Infrastructure)
│   ├── PostgreSQL
│   ├── Redis
│   └── Qdrant
└── Dell LLM (Remote)
```

### Production Considerations
- **Reverse Proxy**: Nginx for SSL and load balancing
- **Process Manager**: Systemd or supervisor
- **Monitoring**: Prometheus + Grafana
- **Backup**: Database and file backups

## Technology Rationale

### Frontend Stack
- **Electron**: Cross-platform desktop application
- **React**: Component-based UI development
- **TypeScript**: Type safety and better IDE support
- **Tailwind CSS**: Rapid UI development
- **Vite**: Fast build tool and dev server

### Backend Stack
- **FastAPI**: Modern async Python web framework
- **LangChain**: LLM application framework
- **LangGraph**: Agent orchestration
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings

### Infrastructure Stack
- **PostgreSQL**: Reliable relational database
- **Redis**: Fast in-memory data store
- **Qdrant**: Vector database for semantic search
- **Podman**: Daemonless container engine

## Future Enhancements

### Phase 2 Features
- **Guardrails Implementation**: Advanced security filtering
- **Observability**: LangSmith integration
- **Evals**: DeepEval, Ragas integration
- **Screenshot Intelligence**: Vision model integration
- **Terminal Intelligence**: Real-time terminal monitoring

### Enterprise Features
- **Multi-User Support**: Team collaboration
- **Advanced Security**: SSO, RBAC
- **Audit Logging**: Compliance requirements
- **API Rate Limiting**: Production-grade scaling
- **Disaster Recovery**: Backup and restore procedures

## Integration Points

### External Services
- **Dell LLM**: Primary inference endpoint
- **GitHub API**: Code repository integration
- **Future**: Outlook, Teams, Jira, Confluence

### Local System Integration
- **PowerShell**: Windows automation
- **Filesystem**: Local file access
- **Clipboard**: System clipboard
- **Screenshot**: Screen capture API

This architecture provides a solid foundation for a local-first, multi-agent AI assistant that can scale from personal use to enterprise deployment.
