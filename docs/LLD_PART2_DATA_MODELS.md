# CortexDesk Low-Level Design (LLD) - Part 2: Data Models & Database Schema

## Document Overview

This document provides detailed specifications for all data models, database schemas, and their relationships in the CortexDesk system.

**Document Parts:**
- Part 1: Architecture & System Design
- Part 2: Data Models & Database Schema (This document)
- Part 3: API Specifications
- Part 4: Agent Implementation Details
- Part 5: Frontend Architecture
- Part 6: Deployment & Infrastructure

---

## 1. Database Overview

### 1.1 Database Technology

**Primary Database:** PostgreSQL 15
- **Driver:** asyncpg (async PostgreSQL driver)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migration Tool:** Alembic 1.13.0
- **Connection String:** `postgresql+asyncpg://user:password@localhost:5432/cortexdesk`

**Secondary Storage:**
- **Redis 7.2:** Runtime state and caching
- **Qdrant 1.12.0:** Vector database for embeddings

### 1.2 Database Schema Organization

**Schema Categories:**
1. **Business Data:** Users, chats, messages, documents
2. **Observability:** Logs, traces, metrics
3. **Memory:** Long-term memory and agent executions
4. **Integrations:** MCP server configurations

---

## 2. Business Data Models

### 2.1 User Model

**Table:** `users`

**Purpose:** Store user account information and authentication data.

**Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (INTEGER, PRIMARY KEY): Unique user identifier
- `username` (VARCHAR(255), UNIQUE): Display username
- `email` (VARCHAR(255), UNIQUE): User email address
- `hashed_password` (VARCHAR(255)): Hashed password (bcrypt)
- `is_active` (BOOLEAN): Account active status
- `is_superuser` (BOOLEAN): Superuser privileges
- `created_at` (TIMESTAMP): Account creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- UNIQUE index on `username`
- UNIQUE index on `email`
- Index on `is_active`

**Relationships:**
- One-to-many with `chats` (user has many chats)

**Python Model:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    chats = relationship("Chat", back_populates="user")
```

---

### 2.2 Chat Model

**Table:** `chats`

**Purpose:** Store chat session information and context.

**Schema:**
```sql
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    context TEXT,
    meta_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique chat identifier
- `user_id` (INTEGER, FOREIGN KEY): User who owns the chat
- `title` (VARCHAR(255)): Chat title (auto-generated from first message)
- `status` (VARCHAR(50)): Chat status (active, archived, deleted)
- `context` (TEXT): JSON string with chat context
- `meta_data` (TEXT): JSON string with additional metadata
- `created_at` (TIMESTAMP): Chat creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- Index on `user_id`
- Index on `status`
- Index on `created_at` (for sorting)
- Index on `updated_at` (for sorting)

**Relationships:**
- Many-to-one with `users` (chat belongs to user)
- One-to-many with `messages` (chat has many messages)
- One-to-many with `agent_executions` (chat has many executions)

**Status Enum:**
```python
class ChatStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
```

**Python Model:**
```python
class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE, index=True)
    context = Column(Text, nullable=True)
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="chat", cascade="all, delete-orphan")
```

---

### 2.3 Message Model

**Table:** `messages`

**Purpose:** Store individual chat messages with role and content.

**Schema:**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    agent_used VARCHAR(100),
    tool_calls TEXT,
    meta_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique message identifier
- `chat_id` (INTEGER, FOREIGN KEY): Chat this message belongs to
- `role` (VARCHAR(50)): Message role (user, assistant, system)
- `content` (TEXT): Message content
- `agent_used` (VARCHAR(100)): Which agent generated this message
- `tool_calls` (TEXT): JSON string with tool call information
- `meta_data` (TEXT): JSON string with additional metadata
- `created_at` (TIMESTAMP): Message creation timestamp

**Indexes:**
- Index on `chat_id`
- Index on `role`
- Index on `created_at` (for sorting)

**Relationships:**
- Many-to-one with `chats` (message belongs to chat)

**Role Enum:**
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
```

**Python Model:**
```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False, index=True)
    content = Column(Text, nullable=False)
    agent_used = Column(String(100), nullable=True)
    tool_calls = Column(Text, nullable=True)
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    chat = relationship("Chat", back_populates="messages")
```

---

### 2.4 Document Model

**Table:** `documents`

**Purpose:** Store uploaded documents and their processing status.

**Schema:**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    chunk_count INTEGER DEFAULT 0,
    embedding_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique document identifier
- `user_id` (INTEGER, FOREIGN KEY): User who uploaded the document
- `title` (VARCHAR(255)): Document title
- `content` (TEXT): Document content
- `file_name` (VARCHAR(255)): Original file name
- `file_type` (VARCHAR(100)): File type (txt, md, pdf, etc.)
- `chunk_count` (INTEGER): Number of chunks after segmentation
- `embedding_status` (VARCHAR(50)): Embedding processing status
- `created_at` (TIMESTAMP): Document creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- Index on `user_id`
- Index on `embedding_status`
- Index on `created_at` (for sorting)

**Relationships:**
- Many-to-one with `users` (document belongs to user)

**Embedding Status Enum:**
```python
class EmbeddingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Python Model:**
```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(100), nullable=True)
    chunk_count = Column(Integer, default=0)
    embedding_status = Column(Enum(EmbeddingStatus), default=EmbeddingStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User")
```

---

### 2.5 MCP Integration Model

**Table:** `mcp_integrations`

**Purpose:** Store Model Context Protocol (MCP) server configurations.

**Schema:**
```sql
CREATE TABLE mcp_integrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(100) NOT NULL,
    config TEXT NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'disconnected',
    last_connected TIMESTAMP WITH TIME ZONE,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique integration identifier
- `name` (VARCHAR(255), UNIQUE): Integration name
- `type` (VARCHAR(100)): MCP type (filesystem, github, git, postgresql)
- `config` (TEXT): JSON string with integration configuration
- `description` (TEXT): Integration description
- `enabled` (BOOLEAN): Integration enabled status
- `status` (VARCHAR(50)): Connection status (connected, disconnected, error)
- `last_connected` (TIMESTAMP): Last successful connection timestamp
- `last_error` (TEXT): Last error message
- `created_at` (TIMESTAMP): Integration creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- UNIQUE index on `name`
- Index on `type`
- Index on `status`
- Index on `enabled`

**Status Enum:**
```python
class MCPStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"
```

**Python Model:**
```python
class MCPIntegration(Base):
    __tablename__ = "mcp_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    config = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    status = Column(Enum(MCPStatus), default=MCPStatus.DISCONNECTED, index=True)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 2.6 LLM Configuration Model

**Table:** `llm_configurations`

**Purpose:** Store user-specific LLM provider configurations with dynamic switching capability.

**Schema:**
```sql
CREATE TABLE llm_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(500),
    api_key TEXT,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique configuration identifier
- `user_id` (INTEGER, FOREIGN KEY): User who owns this configuration
- `provider` (VARCHAR(50)): LLM provider (local, groq, runpod, openai, anthropic, azure, custom)
- `model_name` (VARCHAR(100)): Model name (e.g., gpt2, llama2-70b, gpt-4)
- `endpoint` (VARCHAR(500)): API endpoint URL (for custom providers)
- `api_key` (TEXT): API key for cloud providers
- `temperature` (FLOAT): Temperature parameter (0.0-2.0)
- `max_tokens` (INTEGER): Maximum tokens to generate
- `is_active` (BOOLEAN): Whether this is the active configuration
- `created_at` (TIMESTAMP): Configuration creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `provider`
- INDEX on `is_active`

**Constraints:**
- FOREIGN KEY on `user_id` references `users(id)` ON DELETE CASCADE
- `provider` must be one of: local, groq, runpod, openai, anthropic, azure, custom
- `temperature` must be between 0.0 and 2.0
- `max_tokens` must be positive

**Python Model:**
```python
class LLMProvider(enum.Enum):
    LOCAL = "local"
    GROQ = "groq"
    RUNPOD = "runpod"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    CUSTOM = "custom"

class LLMConfiguration(Base):
    __tablename__ = "llm_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(LLMProvider), nullable=False, default=LLMProvider.LOCAL)
    model_name = Column(String(100), nullable=False, default="gpt2")
    endpoint = Column(String(500), nullable=True)
    api_key = Column(Text, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", backref="llm_configurations")
```

**Supported Providers:**
- **local**: GPT-2 (free, limited quality)
- **groq**: Groq Cloud (free, fast, high quality)
- **runpod**: RunPod Cloud (paid, flexible)
- **openai**: OpenAI GPT models (paid, high quality)
- **anthropic**: Anthropic Claude models (paid, high quality)
- **azure**: Azure OpenAI Service (paid, enterprise)
- **custom**: Any OpenAI-compatible endpoint

**Default Configuration:**
- Provider: local
- Model: gpt2
- Temperature: 0.7
- Max Tokens: 1000
- Is Active: True

**Business Rules:**
- Each user can have multiple LLM configurations
- Only one configuration can be active per user at a time
- Default local configuration is created automatically for new users
- Configurations can be switched without restarting the backend
- API keys are stored in the database (should be encrypted in production)

---

## 3. Observability Data Models

### 3.1 Observability Log Model

**Table:** `observability_logs`

**Purpose:** Store system logs with levels and context for debugging and monitoring.

**Schema:**
```sql
CREATE TABLE observability_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(50) NOT NULL,
    logger_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique log identifier
- `level` (VARCHAR(50)): Log level (INFO, WARNING, ERROR, DEBUG)
- `logger_name` (VARCHAR(255)): Name of the logger that generated the log
- `message` (TEXT): Log message
- `context` (TEXT): JSON string with additional context
- `timestamp` (TIMESTAMP): Log creation timestamp

**Indexes:**
- Index on `level`
- Index on `logger_name`
- Index on `timestamp` (for sorting and time-based queries)
- Composite index on `(level, timestamp)`

**Level Enum:**
```python
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
```

**Python Model:**
```python
class ObservabilityLog(Base):
    __tablename__ = "observability_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False, index=True)
    logger_name = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

---

### 3.2 Observability Trace Model

**Table:** `observability_traces`

**Purpose:** Store request traces with timing and hierarchy for performance analysis.

**Schema:**
```sql
CREATE TABLE observability_traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    parent_span_id VARCHAR(255),
    operation_name VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms FLOAT,
    status VARCHAR(50) NOT NULL,
    meta_data TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique trace identifier
- `trace_id` (VARCHAR(255)): Correlates all spans in a request
- `span_id` (VARCHAR(255)): Unique identifier for this span
- `parent_span_id` (VARCHAR(255)): Parent span ID (shows hierarchy)
- `operation_name` (VARCHAR(255)): What operation was performed
- `service_name` (VARCHAR(255)): Which service/agent performed it
- `start_time` (TIMESTAMP): Span start time
- `end_time` (TIMESTAMP): Span end time
- `duration_ms` (FLOAT): Duration in milliseconds
- `status` (VARCHAR(50)): Span status (success, error, running)
- `meta_data` (TEXT): JSON string with additional metadata
- `timestamp` (TIMESTAMP): Trace creation timestamp

**Indexes:**
- Index on `trace_id`
- Index on `span_id`
- Index on `service_name`
- Index on `status`
- Index on `start_time` (for time-based queries)
- Composite index on `(trace_id, start_time)`

**Status Enum:**
```python
class TraceStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"
```

**Python Model:**
```python
class ObservabilityTrace(Base):
    __tablename__ = "observability_traces"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(255), nullable=False, index=True)
    span_id = Column(String(255), nullable=False, index=True)
    parent_span_id = Column(String(255), nullable=True)
    operation_name = Column(String(255), nullable=False)
    service_name = Column(String(255), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    meta_data = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

---

### 3.3 Observability Metric Model

**Table:** `observability_metrics`

**Purpose:** Store performance metrics and counters for monitoring.

**Schema:**
```sql
CREATE TABLE observability_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    tags TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique metric identifier
- `metric_name` (VARCHAR(255)): Metric name (e.g., agent.supervisor.success)
- `metric_value` (FLOAT): Metric value
- `metric_type` (VARCHAR(50)): Metric type (gauge, counter, histogram)
- `tags` (TEXT): JSON string with metric tags
- `timestamp` (TIMESTAMP): Metric creation timestamp

**Indexes:**
- Index on `metric_name`
- Index on `metric_type`
- Index on `timestamp` (for time-based queries)
- Composite index on `(metric_name, timestamp)`

**Metric Type Enum:**
```python
class MetricType(str, Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"
```

**Python Model:**
```python
class ObservabilityMetric(Base):
    __tablename__ = "observability_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False, index=True)
    tags = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

---

## 4. Memory Data Models

### 4.1 Memory Model

**Table:** `memories`

**Purpose:** Store long-term memory embeddings for RAG retrieval.

**Schema:**
```sql
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding_vector FLOAT[],
    metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique memory identifier
- `user_id` (INTEGER, FOREIGN KEY): User who owns this memory
- `memory_type` (VARCHAR(50)): Memory type (conversation, document, system)
- `content` (TEXT): Memory content
- `embedding_vector` (FLOAT[]): Embedding vector (384 dimensions)
- `metadata` (TEXT): JSON string with additional metadata
- `created_at` (TIMESTAMP): Memory creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes:**
- Index on `user_id`
- Index on `memory_type`
- Index on `created_at` (for sorting)

**Relationships:**
- Many-to-one with `users` (memory belongs to user)

**Memory Type Enum:**
```python
class MemoryType(str, Enum):
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    SYSTEM = "system"
    AGENT_EXECUTION = "agent_execution"
```

**Python Model:**
```python
class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type = Column(Enum(MemoryType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding_vector = Column(ARRAY(Float), nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User")
```

---

### 4.2 Agent Execution Model

**Table:** `agent_executions`

**Purpose:** Store agent execution history for analysis and debugging.

**Schema:**
```sql
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    input_prompt TEXT NOT NULL,
    output_response TEXT,
    error_message TEXT,
    execution_time FLOAT,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` (SERIAL, PRIMARY KEY): Unique execution identifier
- `chat_id` (INTEGER, FOREIGN KEY): Chat this execution belongs to
- `agent_name` (VARCHAR(100)): Name of the agent that executed
- `input_prompt` (TEXT): Input prompt given to the agent
- `output_response` (TEXT): Response from the agent
- `error_message` (TEXT): Error message if execution failed
- `execution_time` (FLOAT): Execution time in seconds
- `status` (VARCHAR(50)): Execution status (completed, failed, running)
- `created_at` (TIMESTAMP): Execution creation timestamp

**Indexes:**
- Index on `chat_id`
- Index on `agent_name`
- Index on `status`
- Index on `created_at` (for sorting)

**Relationships:**
- Many-to-one with `chats` (execution belongs to chat)

**Status Enum:**
```python
class ExecutionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    RUNNING = "running"
```

**Python Model:**
```python
class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    input_prompt = Column(Text, nullable=False)
    output_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    chat = relationship("Chat", back_populates="agent_executions")
```

---

## 5. Redis Data Structures

### 5.1 Key Naming Convention

**Format:** `{category}:{identifier}`

**Categories:**
- `conversation:{chat_id}` - Chat conversation history
- `agent_state:{chat_id}` - Agent runtime state
- `response:{hash}` - Response cache
- `tool:{hash}` - Tool execution cache
- `screenshot:{hash}` - Screenshot cache
- `workflow:{id}` - Long-running workflow progress
- `memory_queue` - Pending memory extraction tasks

### 5.2 Conversation Data Structure

**Key:** `conversation:{chat_id}`

**Value:** JSON array of messages
```json
[
  {
    "id": 1,
    "role": "user",
    "content": "Hello",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "Hi there!",
    "timestamp": "2024-01-01T00:00:01Z"
  }
]
```

**TTL:** No expiration (stored until chat deletion)

### 5.3 Agent State Data Structure

**Key:** `agent_state:{chat_id}`

**Value:** JSON object with agent state
```json
{
  "current_agent": "knowledge",
  "context": {
    "user_intent": "search",
    "selected_agents": ["knowledge"]
  },
  "execution_plan": {
    "knowledge": "Search for information"
  }
}
```

**TTL:** 24 hours

### 5.4 Response Cache Data Structure

**Key:** `response:{hash}`

**Hash:** MD5 hash of (message + chat_id)

**Value:** JSON object with response
```json
{
  "response": "Generated response",
  "agents_used": ["knowledge"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**TTL:** 1 hour (3600 seconds)

### 5.5 Tool Cache Data Structure

**Key:** `tool:{hash}`

**Hash:** MD5 hash of (tool_name + parameters)

**Value:** JSON object with tool result
```json
{
  "result": "Tool execution result",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**TTL:** 30 minutes (1800 seconds)

### 5.6 Screenshot Cache Data Structure

**Key:** `screenshot:{hash}`

**Hash:** MD5 hash of screenshot content

**Value:** Binary screenshot data (base64 encoded)

**TTL:** 24 hours (86400 seconds)

### 5.7 Workflow Data Structure

**Key:** `workflow:{id}`

**Value:** JSON object with workflow progress
```json
{
  "status": "running",
  "progress": 50,
  "current_step": "Processing documents",
  "total_steps": 10,
  "started_at": "2024-01-01T00:00:00Z"
}
```

**TTL:** 7 days (604800 seconds)

### 5.8 Memory Queue Data Structure

**Key:** `memory_queue`

**Value:** Redis list of pending memory extraction tasks

**Format:** JSON strings
```json
{
  "task_id": "uuid",
  "type": "conversation",
  "chat_id": 1,
  "priority": "high"
}
```

**TTL:** No expiration (processed by background worker)

---

## 6. Qdrant Collections

### 6.1 Documents Collection

**Collection Name:** `documents`

**Purpose:** Store document embeddings for RAG retrieval.

**Configuration:**
```json
{
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  },
  "optimizer": {
    "type": "hnsw",
    "hnsw": {
      "m": 16,
      "ef_construct": 100
    }
  }
}
```

**Payload Schema:**
```json
{
  "document_id": 12,
  "title": "Document Title",
  "content": "Document content chunk",
  "chunk_index": 0,
  "total_chunks": 5
}
```

**Point ID Strategy:** MD5 hash of `{document_id}_chunk_{chunk_index}` converted to integer

**Operations:**
- Insert: When document is uploaded and chunked
- Search: When user queries documents
- Delete: When document is deleted

### 6.2 AI Assistant Memory Collection

**Collection Name:** `ai_assistant_memory`

**Purpose:** Store long-term memory embeddings for the AI assistant.

**Configuration:**
```json
{
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  },
  "optimizer": {
    "type": "hnsw",
    "hnsw": {
      "m": 16,
      "ef_construct": 100
    }
  }
}
```

**Payload Schema:**
```json
{
  "memory_type": "conversation",
  "user_id": 1,
  "content": "Memory content",
  "timestamp": "2024-01-01T00:00:00Z",
  "chat_id": 1
}
```

**Point ID Strategy:** MD5 hash of `{memory_type}_{user_id}_{timestamp}` converted to integer

**Operations:**
- Insert: When important information is identified
- Search: When retrieving relevant context
- Delete: When memory is no longer relevant

---

## 7. Data Relationships

### 7.1 Entity Relationship Diagram

```
User (1) ──────< (N) Chat (1) ──────< (N) Message
  │                │
  │                │
  │                └─────< (N) AgentExecution
  │
  └─────< (N) Document
  │
  └─────< (N) Memory

MCPIntegration (standalone)
```

### 7.2 Cascade Delete Rules

**User Deletion:**
- Cascades to: chats, documents, memories
- Does NOT delete: observability data (kept for analysis)

**Chat Deletion:**
- Cascades to: messages, agent_executions
- Does NOT delete: observability data (kept for analysis)

**Document Deletion:**
- Does NOT cascade (manual deletion required)
- Qdrant embeddings deleted separately via API

---

## 8. Data Validation Rules

### 8.1 Input Validation

**User Input:**
- Username: 3-50 characters, alphanumeric + underscore
- Email: Valid email format
- Password: Minimum 8 characters (hashed before storage)

**Chat Input:**
- Title: 1-255 characters
- Message: 1-10000 characters
- Context: Valid JSON if provided

**Document Input:**
- Title: 1-255 characters
- Content: 1-100000 characters
- File type: Valid MIME type if provided

### 8.2 Business Logic Validation

**Chat Creation:**
- User must exist (auto-created if not)
- Title auto-generated from first message if "New conversation"
- Status defaults to "active"

**Message Creation:**
- Chat must exist
- Role must be valid enum value
- Content cannot be empty

**Document Upload:**
- User must exist
- Title is required
- Content is required
- Embedding status defaults to "pending"

**MCP Integration:**
- Name must be unique
- Type must be valid MCP type
- Config must be valid JSON
- Status defaults to "disconnected"

---

## 9. Data Migration Strategy

### 9.1 Alembic Configuration

**Migration Directory:** `backend/alembic/versions`

**Migration Naming:** `{revision}_{description}.py`

**Migration Commands:**
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### 9.2 Current Migration State

**Initial Schema:** All tables created via SQLAlchemy `create_all`

**Future Migrations:**
- Add new columns to existing tables
- Create new tables for features
- Add indexes for performance
- Modify constraints

---

## 10. Data Retention Policies

### 10.1 Business Data Retention

**Chats:**
- Active chats: Retained indefinitely
- Archived chats: Retained for 1 year
- Deleted chats: Soft delete, purged after 30 days

**Messages:**
- Retained as long as parent chat exists
- Purged when parent chat is purged

**Documents:**
- Retained indefinitely unless manually deleted
- No automatic purging

**MCP Integrations:**
- Retained indefinitely unless manually deleted
- No automatic purging

### 10.2 Observability Data Retention

**Logs:**
- Default retention: 30 days
- Configurable via purge API
- Manual purge available via UI

**Traces:**
- Default retention: 30 days
- Configurable via purge API
- Manual purge available via UI

**Metrics:**
- Default retention: 7 days
- Configurable via purge API
- Manual purge available via UI

### 10.3 Runtime Data Retention

**Redis Data:**
- Conversation history: No expiration (until chat deletion)
- Agent state: 24 hours
- Response cache: 1 hour
- Tool cache: 30 minutes
- Screenshot cache: 24 hours
- Workflow data: 7 days
- Memory queue: No expiration (processed by worker)

**Qdrant Data:**
- Document embeddings: Retained as long as document exists
- Memory embeddings: Retained indefinitely unless manually deleted

---

## 11. Data Backup Strategy

### 11.1 PostgreSQL Backup

**Current:** No automated backup

**Recommended:**
```bash
# Full backup
pg_dump -U username -d cortexdesk > backup_$(date +%Y%m%d).sql

# Schema only backup
pg_dump -U username -d cortexdesk --schema-only > schema_backup.sql

# Data only backup
pg_dump -U username -d cortexdesk --data-only > data_backup.sql
```

### 11.2 Redis Backup

**Current:** No persistence (runtime state only)

**Recommended:**
```bash
# Save RDB snapshot
redis-cli BGSAVE

# Copy RDB file
cp dump.rdb backup_$(date +%Y%m%d).rdb
```

### 11.3 Qdrant Backup

**Current:** No automated backup

**Recommended:**
```bash
# Export collection snapshot
curl -X POST "http://localhost:6333/collections/documents/snapshots/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "snapshot=@snapshot.tar"

# Download snapshot
curl -X GET "http://localhost:6333/collections/documents/snapshots/{snapshot_id}" \
  --output snapshot.tar
```

---

## 12. Data Security

### 12.1 Encryption

**Passwords:**
- Hashed using bcrypt before storage
- Salt included in hash
- No plain text storage

**API Keys:**
- Stored in environment variables
- Not logged in observability data
- Masked in error messages

**Secret Key:**
- Generated randomly on first startup
- Must be changed from default
- Used for JWT token signing

### 12.2 Access Control

**Database Access:**
- Application user with limited privileges
- No direct database access from frontend
- Connection string in environment variables

**Redis Access:**
- No authentication (local only)
- Protected by network isolation
- Future: Add Redis AUTH

**Qdrant Access:**
- No authentication (local only)
- Protected by network isolation
- Future: Add Qdrant API key

---

## 13. Data Consistency

### 13.1 Transaction Management

**Database Transactions:**
- All multi-step operations use transactions
- Rollback on error
- Commit only on success

**Example:**
```python
async def create_chat_with_message(chat_data, message_data):
    async with db.begin():
        # Create chat
        chat = Chat(**chat_data)
        db.add(chat)
        await db.flush()
        
        # Create message
        message = Message(chat_id=chat.id, **message_data)
        db.add(message)
        
        # Commit both
        await db.commit()
```

### 13.2 Cache Consistency

**Cache Invalidation:**
- Document deletion invalidates Qdrant embeddings
- Chat deletion invalidates Redis conversation history
- Message addition invalidates response cache

**Cache Update Strategy:**
- Write-through cache (write to DB and cache)
- Cache-aside (read from cache, miss then load from DB)
- Write-behind (write to cache, async write to DB)

---

## 14. Data Performance Optimization

### 14.1 Database Indexing

**Current Indexes:**
- All foreign keys indexed
- All enum fields indexed
- Timestamp fields indexed for sorting
- Composite indexes for common queries

**Future Indexes:**
- Full-text search indexes on message content
- GIN indexes on JSON fields
- Partial indexes for active records only

### 14.2 Query Optimization

**N+1 Query Prevention:**
- Use eager loading with `selectinload`
- Use joinedload for related data
- Batch loading where possible

**Example:**
```python
# Bad: N+1 queries
chats = await db.execute(select(Chat))
for chat in chats:
    messages = await db.execute(select(Message).where(Message.chat_id == chat.id))

# Good: Single query with eager loading
chats = await db.execute(
    select(Chat).options(selectinload(Chat.messages))
)
```

### 14.3 Connection Pooling

**PostgreSQL Pool:**
- Min connections: 5
- Max connections: 20
- Pool timeout: 30 seconds

**Redis Pool:**
- Max connections: 50
- Connection timeout: 5 seconds

---

## 15. Data Cleanup Jobs

### 15.1 Scheduled Cleanup

**Recommended Jobs:**
- Daily: Purge observability data older than retention period
- Weekly: Archive old chats
- Monthly: Compress old logs

**Implementation:**
```python
# Using Celery or APScheduler
@celery.task
def purge_old_observability_data():
    # Purge logs older than 30 days
    await observability_db.delete_logs(before_days=30)
    
    # Purge traces older than 30 days
    await observability_db.delete_traces(before_days=30)
    
    # Purge metrics older than 7 days
    await observability_db.delete_metrics(before_days=7)
```

---

## 16. Data Export/Import

### 16.1 Export Formats

**Chat Export:**
- JSON: Complete chat with messages
- Markdown: Formatted conversation
- Plain text: Raw message content

**Document Export:**
- Original format (txt, md, pdf)
- JSON: With metadata
- Markdown: Formatted content

**Observability Export:**
- CSV: Logs and traces
- JSON: Complete data with metadata
- Plain text: Human-readable format

### 16.2 Import Formats

**Chat Import:**
- JSON: Complete chat with messages
- CSV: Message list with timestamps

**Document Import:**
- Text files (.txt, .md)
- Markdown files (.md)
- PDF files (.pdf) - with text extraction

---

## 17. Data Versioning

### 17.1 Schema Versioning

**Current Version:** v1.0.0

**Versioning Strategy:**
- Major version: Breaking schema changes
- Minor version: Non-breaking additions
- Patch version: Bug fixes

**Migration Path:**
- Always forward-compatible
- Rollback scripts for major versions
- Test migrations in staging first

---

## 18. Data Monitoring

### 18.1 Database Health Checks

**PostgreSQL Health:**
- Connection pool status
- Query performance metrics
- Table size monitoring
- Index usage statistics

**Redis Health:**
- Memory usage percentage
- Connection count
- Key count by category
- Eviction statistics

**Qdrant Health:**
- Collection statistics
- Index status
- Memory usage
- Query performance

### 18.2 Data Quality Checks

**Consistency Checks:**
- Orphaned records detection
- Foreign key integrity
- Duplicate detection
- Data validation

**Example:**
```python
# Check for orphaned messages
orphaned_messages = await db.execute(
    select(Message).where(
        ~Message.chat_id.in_(select(Chat.id))
    )
)
```

---

## 19. Data Recovery

### 19.1 Point-in-Time Recovery

**PostgreSQL:**
- Use WAL archives for PITR
- Restore to specific timestamp
- Requires WAL archiving configuration

**Redis:**
- Restore from RDB snapshot
- Limited to last save point
- No point-in-time recovery

**Qdrant:**
- Restore from collection snapshot
- Limited to snapshot points
- No point-in-time recovery

### 19.2 Disaster Recovery

**Backup Strategy:**
- Daily full backups
- Hourly incremental backups
- Offsite backup storage
- Backup integrity verification

**Recovery Procedure:**
1. Stop application
2. Restore database from backup
3. Restore Redis from snapshot
4. Restore Qdrant from snapshot
5. Verify data integrity
6. Start application

---

## 20. Data Privacy

### 20.1 PII Handling

**Personally Identifiable Information:**
- Usernames and emails stored in database
- No PII in logs or traces
- PII masked in error messages

**Data Anonymization:**
- Option to anonymize chat data
- Remove user identifiers from exports
- Hash sensitive identifiers

### 20.2 Data Deletion

**Right to be Forgotten:**
- User can request account deletion
- All associated data deleted
- Observability data retained for analysis only

**Deletion Process:**
1. Mark user account as deleted
2. Anonymize chat data
3. Delete user account after retention period
4. Keep observability data for analysis

---

**End of Part 2: Data Models & Database Schema**

Continue to Part 3: API Specifications
