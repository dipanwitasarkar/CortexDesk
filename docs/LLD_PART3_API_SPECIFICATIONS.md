# CortexDesk Low-Level Design (LLD) - Part 3: API Specifications

## Document Overview

This document provides detailed specifications for all API endpoints in the CortexDesk system, including request/response formats, authentication, error handling, and usage examples.

**Document Parts:**
- Part 1: Architecture & System Design
- Part 2: Data Models & Database Schema
- Part 3: API Specifications (This document)
- Part 4: Agent Implementation Details
- Part 5: Frontend Architecture
- Part 6: Deployment & Infrastructure

---

## 1. API Overview

### 1.1 API Technology Stack

**Framework:** FastAPI 0.104.1
**Python Version:** 3.12
**Async Runtime:** asyncio
**API Style:** RESTful
**Data Format:** JSON
**Character Encoding:** UTF-8

### 1.2 API Base URL

**Development:** `http://localhost:8000`
**Production:** `https://api.cortexdesk.com` (future)

**API Version:** v1
**Version Prefix:** `/api/v1`

### 1.3 API Endpoints Summary

**Chat Management:**
- `POST /api/v1/chats` - Create new chat
- `GET /api/v1/chats/{chat_id}` - Get chat with messages
- `GET /api/v1/chats` - List user's chats
- `DELETE /api/v1/chats/{chat_id}` - Delete chat

**Message Management:**
- `POST /api/v1/chats/{chat_id}/messages` - Add message to chat

**Assistant:**
- `POST /api/v1/assistant` - Process message through multi-agent system

**Document Management:**
- `POST /api/v1/documents` - Upload document
- `GET /api/v1/documents` - List user's documents
- `GET /api/v1/documents/{document_id}` - Get document details
- `DELETE /api/v1/documents/{document_id}` - Delete document
- `POST /api/v1/documents/{document_id}/search` - Search documents

**MCP Integration:**
- `GET /api/v1/mcp/integrations` - List MCP integrations
- `GET /api/v1/mcp/integrations/{integration_id}` - Get integration details
- `POST /api/v1/mcp/integrations` - Create MCP integration
- `PUT /api/v1/mcp/integrations/{integration_id}` - Update MCP integration
- `DELETE /api/v1/mcp/integrations/{integration_id}` - Delete MCP integration
- `POST /api/v1/mcp/integrations/{integration_id}/test` - Test MCP connection
- `GET /api/v1/mcp/types` - Get available MCP types

**LLM Configuration:**
- `GET /api/v1/llm/config` - List LLM configurations
- `GET /api/v1/llm/config/{config_id}` - Get specific configuration
- `GET /api/v1/llm/config/active` - Get active configuration
- `POST /api/v1/llm/config` - Create LLM configuration
- `PUT /api/v1/llm/config/{config_id}` - Update LLM configuration
- `DELETE /api/v1/llm/config/{config_id}` - Delete LLM configuration
- `POST /api/v1/llm/config/{config_id}/activate` - Activate LLM configuration
- `GET /api/v1/llm/providers` - Get available LLM providers
- `POST /api/v1/llm/config/test` - Test LLM configuration

**Observability:**
- `GET /api/v1/observability/health` - Get observability health
- `GET /api/v1/observability/metrics` - Get performance metrics
- `GET /api/v1/observability/traces` - Get request traces
- `GET /api/v1/observability/logs` - Get system logs
- `GET /api/v1/observability/performance` - Get system performance
- `GET /api/v1/observability/runtime-state` - Get Redis runtime state
- `GET /api/v1/observability/database` - Get database statistics
- `GET /api/v1/observability/redis` - Get Redis statistics
- `DELETE /api/v1/observability/logs` - Delete logs
- `DELETE /api/v1/observability/traces` - Delete traces
- `DELETE /api/v1/observability/metrics` - Delete metrics
- `GET /api/v1/observability/stats` - Get observability statistics

**Health:**
- `GET /health` - Application health check
- `GET /config` - Application configuration

---

## 2. Authentication & Authorization

### 2.1 Current Authentication

**Status:** No authentication implemented (local development)

**Future Authentication:**
- JWT-based authentication
- Bearer token in Authorization header
- Token refresh mechanism
- Role-based access control

### 2.2 Authorization

**Current:** No authorization (all endpoints public)

**Future Authorization:**
- User-based access control
- Resource ownership validation
- Admin-only endpoints
- API key authentication for external access

---

## 3. Common Response Format

### 3.1 Success Response

**Format:**
```json
{
  "data": {},
  "message": "Success message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3.2 Error Response

**Format:**
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3.3 Validation Error Response

**Format:**
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field is required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 4. Chat Management APIs

### 4.1 Create Chat

**Endpoint:** `POST /api/v1/chats`

**Purpose:** Create a new chat session for a user.

**Request Body:**
```json
{
  "user_id": 1,
  "context": {},
  "meta_data": {}
}
```

**Request Parameters:**
- `user_id` (integer, required): User ID
- `context` (object, optional): Initial chat context
- `meta_data` (object, optional): Additional metadata

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "New conversation",
  "status": "active",
  "context": null,
  "meta_data": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 201: Chat created successfully
- 400: Invalid request data
- 500: Internal server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "context": {"theme": "coding"}
  }'
```

---

### 4.2 Get Chat

**Endpoint:** `GET /api/v1/chats/{chat_id}`

**Purpose:** Get a chat with all its messages.

**Path Parameters:**
- `chat_id` (integer, required): Chat ID

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "New conversation",
  "status": "active",
  "context": null,
  "meta_data": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": [
    {
      "id": 1,
      "chat_id": 1,
      "role": "user",
      "content": "Hello",
      "agent_used": null,
      "tool_calls": null,
      "meta_data": null,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "chat_id": 1,
      "role": "assistant",
      "content": "Hi there!",
      "agent_used": "supervisor",
      "tool_calls": null,
      "meta_data": null,
      "created_at": "2024-01-01T00:00:01Z"
    }
  ]
}
```

**Status Codes:**
- 200: Chat retrieved successfully
- 404: Chat not found
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/chats/1"
```

---

### 4.3 List Chats

**Endpoint:** `GET /api/v1/chats`

**Purpose:** List all chats for a user.

**Query Parameters:**
- `user_id` (integer, required): User ID
- `skip` (integer, optional): Number of chats to skip (default: 0)
- `limit` (integer, optional): Maximum chats to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "New conversation",
    "status": "active",
    "context": null,
    "meta_data": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Code help",
    "status": "active",
    "context": null,
    "meta_data": null,
    "created_at": "2024-01-01T00:01:00Z",
    "updated_at": "2024-01-01T00:01:00Z"
  }
]
```

**Status Codes:**
- 200: Chats retrieved successfully
- 400: Invalid request parameters
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/chats?user_id=1&limit=10"
```

---

### 4.4 Delete Chat

**Endpoint:** `DELETE /api/v1/chats/{chat_id}`

**Purpose:** Delete a chat and all its messages.

**Path Parameters:**
- `chat_id` (integer, required): Chat ID

**Response:**
```json
{
  "message": "Chat deleted successfully"
}
```

**Status Codes:**
- 200: Chat deleted successfully
- 404: Chat not found
- 500: Internal server error

**Side Effects:**
- Deletes all messages in the chat
- Deletes all agent executions for the chat
- Clears Redis conversation history for the chat
- Observability data retained for analysis

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/chats/1"
```

---

## 5. Message Management APIs

### 5.1 Create Message

**Endpoint:** `POST /api/v1/chats/{chat_id}/messages`

**Purpose:** Add a message to a chat.

**Path Parameters:**
- `chat_id` (integer, required): Chat ID

**Request Body:**
```json
{
  "role": "user",
  "content": "Hello, how are you?",
  "agent_used": null,
  "tool_calls": null,
  "meta_data": {}
}
```

**Request Parameters:**
- `role` (string, required): Message role (user, assistant, system)
- `content` (string, required): Message content
- `agent_used` (string, optional): Which agent generated this message
- `tool_calls` (array, optional): Tool call information
- `meta_data` (object, optional): Additional metadata

**Response:**
```json
{
  "id": 3,
  "chat_id": 1,
  "role": "user",
  "content": "Hello, how are you?",
  "agent_used": null,
  "tool_calls": null,
  "meta_data": null,
  "created_at": "2024-01-01T00:00:02Z"
}
```

**Status Codes:**
- 201: Message created successfully
- 400: Invalid request data
- 404: Chat not found
- 500: Internal server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chats/1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hello, how are you?"
  }'
```

---

## 6. Assistant API

### 6.1 Process Message

**Endpoint:** `POST /api/v1/assistant`

**Purpose:** Process a user message through the multi-agent system.

**Request Body:**
```json
{
  "message": "What is Python?",
  "user_id": 1,
  "chat_id": 1,
  "context": {}
}
```

**Request Parameters:**
- `message` (string, required): User message
- `user_id` (integer, required): User ID
- `chat_id` (integer, optional): Chat ID (creates new chat if not provided)
- `context` (object, optional): Additional context

**Response:**
```json
{
  "response": "Python is a high-level programming language...",
  "agents_used": ["knowledge"],
  "agent_results": [
    {
      "agent": "knowledge",
      "success": true,
      "result": {
        "success": true,
        "response": "Python is a high-level programming language...",
        "agent_used": "knowledge",
        "metadata": {}
      },
      "execution_time": 0.004818
    }
  ],
  "execution_plan": {
    "knowledge": "Handle aspects related to: what is, python"
  },
  "chat_id": 1,
  "message_id": 4
}
```

**Status Codes:**
- 200: Message processed successfully
- 400: Invalid request data
- 404: Chat not found (if chat_id provided)
- 500: Agent execution failed

**Side Effects:**
- Creates new chat if chat_id not provided
- Stores user message in database
- Stores assistant response in database
- Stores conversation in Redis
- Logs agent execution to observability
- Records traces for performance analysis

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/assistant" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "user_id": 1,
    "chat_id": 1
  }'
```

---

## 7. Document Management APIs

### 7.1 Upload Document

**Endpoint:** `POST /api/v1/documents`

**Purpose:** Upload a document for RAG retrieval.

**Request Body:**
```json
{
  "user_id": 1,
  "title": "Python Guide",
  "content": "Python is a high-level programming language...",
  "file_name": "python_guide.txt",
  "file_type": "text/plain"
}
```

**Request Parameters:**
- `user_id` (integer, required): User ID
- `title` (string, required): Document title
- `content` (string, required): Document content
- `file_name` (string, optional): Original file name
- `file_type` (string, optional): File MIME type

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Python Guide",
  "content": "Python is a high-level programming language...",
  "file_name": "python_guide.txt",
  "file_type": "text/plain",
  "chunk_count": 0,
  "embedding_status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 201: Document uploaded successfully
- 400: Invalid request data
- 500: Internal server error

**Side Effects:**
- Stores document in PostgreSQL
- Triggers embedding generation (async)
- Updates embedding status to "processing"
- Stores embeddings in Qdrant when complete
- Updates embedding status to "completed"

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "Python Guide",
    "content": "Python is a high-level programming language..."
  }'
```

---

### 7.2 List Documents

**Endpoint:** `GET /api/v1/documents`

**Purpose:** List all documents for a user.

**Query Parameters:**
- `user_id` (integer, required): User ID
- `skip` (integer, optional): Number of documents to skip (default: 0)
- `limit` (integer, optional): Maximum documents to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Python Guide",
    "content": "Python is a high-level programming language...",
    "file_name": "python_guide.txt",
    "file_type": "text/plain",
    "chunk_count": 5,
    "embedding_status": "completed",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Status Codes:**
- 200: Documents retrieved successfully
- 400: Invalid request parameters
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/documents?user_id=1"
```

---

### 7.3 Get Document

**Endpoint:** `GET /api/v1/documents/{document_id}`

**Purpose:** Get document details.

**Path Parameters:**
- `document_id` (integer, required): Document ID

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Python Guide",
  "content": "Python is a high-level programming language...",
  "file_name": "python_guide.txt",
  "file_type": "text/plain",
  "chunk_count": 5,
  "embedding_status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Document retrieved successfully
- 404: Document not found
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/documents/1"
```

---

### 7.4 Delete Document

**Endpoint:** `DELETE /api/v1/documents/{document_id}`

**Purpose:** Delete a document and its embeddings.

**Path Parameters:**
- `document_id` (integer, required): Document ID

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

**Status Codes:**
- 200: Document deleted successfully
- 404: Document not found
- 500: Internal server error

**Side Effects:**
- Deletes document from PostgreSQL
- Deletes embeddings from Qdrant (using MD5 hash of IDs)
- Observability data retained for analysis

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/1"
```

---

### 7.5 Search Documents

**Endpoint:** `POST /api/v1/documents/{document_id}/search`

**Purpose:** Search within a document.

**Path Parameters:**
- `document_id` (integer, required): Document ID

**Request Body:**
```json
{
  "query": "Python programming",
  "limit": 5
}
```

**Request Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Maximum results (default: 5)

**Response:**
```json
{
  "results": [
    {
      "chunk_index": 0,
      "content": "Python is a high-level programming language...",
      "score": 0.95
    }
  ]
}
```

**Status Codes:**
- 200: Search completed successfully
- 404: Document not found
- 500: Internal server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python programming",
    "limit": 5
  }'
```

---

## 8. MCP Integration APIs

### 8.1 List MCP Integrations

**Endpoint:** `GET /api/v1/mcp/integrations`

**Purpose:** List all MCP integrations.

**Response:**
```json
[
  {
    "id": 1,
    "name": "github-integration",
    "type": "github",
    "config": {
      "repository": "user/repo",
      "token": "github_token"
    },
    "description": "GitHub repository access",
    "enabled": true,
    "status": "connected",
    "last_connected": "2024-01-01T00:00:00Z",
    "last_error": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Status Codes:**
- 200: Integrations retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/mcp/integrations"
```

---

### 8.2 Get MCP Integration

**Endpoint:** `GET /api/v1/mcp/integrations/{integration_id}`

**Purpose:** Get MCP integration details.

**Path Parameters:**
- `integration_id` (integer, required): Integration ID

**Response:**
```json
{
  "id": 1,
  "name": "github-integration",
  "type": "github",
  "config": {
    "repository": "user/repo",
    "token": "github_token"
  },
  "description": "GitHub repository access",
  "enabled": true,
  "status": "connected",
  "last_connected": "2024-01-01T00:00:00Z",
  "last_error": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Integration retrieved successfully
- 404: Integration not found
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/mcp/integrations/1"
```

---

### 8.3 Create MCP Integration

**Endpoint:** `POST /api/v1/mcp/integrations`

**Purpose:** Create a new MCP integration.

**Request Body:**
```json
{
  "name": "github-integration",
  "type": "github",
  "config": {
    "repository": "user/repo",
    "token": "github_token"
  },
  "description": "GitHub repository access"
}
```

**Request Parameters:**
- `name` (string, required): Integration name (must be unique)
- `type` (string, required): MCP type (filesystem, github, git, postgresql)
- `config` (object, required): Integration configuration (type-specific)
- `description` (string, optional): Integration description

**Response:**
```json
{
  "id": 1,
  "name": "github-integration",
  "type": "github",
  "config": {
    "repository": "user/repo",
    "token": "github_token"
  },
  "description": "GitHub repository access",
  "enabled": true,
  "status": "disconnected",
  "last_connected": null,
  "last_error": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 201: Integration created successfully
- 400: Invalid request data or duplicate name
- 500: Internal server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/integrations" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-integration",
    "type": "github",
    "config": {
      "repository": "user/repo",
      "token": "github_token"
    },
    "description": "GitHub repository access"
  }'
```

---

### 8.4 Update MCP Integration

**Endpoint:** `PUT /api/v1/mcp/integrations/{integration_id}`

**Purpose:** Update an existing MCP integration.

**Path Parameters:**
- `integration_id` (integer, required): Integration ID

**Request Body:**
```json
{
  "name": "github-integration",
  "type": "github",
  "config": {
    "repository": "user/repo",
    "token": "new_token"
  },
  "description": "Updated description",
  "enabled": true
}
```

**Request Parameters:**
- `name` (string, optional): Integration name
- `type` (string, optional): MCP type
- `config` (object, optional): Integration configuration
- `description` (string, optional): Integration description
- `enabled` (boolean, optional): Integration enabled status

**Response:**
```json
{
  "id": 1,
  "name": "github-integration",
  "type": "github",
  "config": {
    "repository": "user/repo",
    "token": "new_token"
  },
  "description": "Updated description",
  "enabled": true,
  "status": "disconnected",
  "last_connected": "2024-01-01T00:00:00Z",
  "last_error": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:01:00Z"
}
```

**Status Codes:**
- 200: Integration updated successfully
- 400: Invalid request data
- 404: Integration not found
- 500: Internal server error

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/mcp/integrations/1" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "token": "new_token"
    }
  }'
```

---

### 8.5 Delete MCP Integration

**Endpoint:** `DELETE /api/v1/mcp/integrations/{integration_id}`

**Purpose:** Delete an MCP integration.

**Path Parameters:**
- `integration_id` (integer, required): Integration ID

**Response:**
```json
{
  "message": "MCP integration deleted successfully"
}
```

**Status Codes:**
- 200: Integration deleted successfully
- 404: Integration not found
- 500: Internal server error

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/mcp/integrations/1"
```

---

### 8.6 Test MCP Connection

**Endpoint:** `POST /api/v1/mcp/integrations/{integration_id}/test`

**Purpose:** Test connection to an MCP integration.

**Path Parameters:**
- `integration_id` (integer, required): Integration ID

**Response:**
```json
{
  "success": true,
  "message": "Connection test successful",
  "latency_ms": 45.2
}
```

**Status Codes:**
- 200: Connection test completed
- 404: Integration not found
- 500: Internal server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/integrations/1/test"
```

---

### 8.7 Get Available MCP Types

**Endpoint:** `GET /api/v1/mcp/types`

**Purpose:** Get available MCP types with configuration schemas.

**Response:**
```json
{
  "types": [
    {
      "type": "filesystem",
      "name": "Filesystem",
      "description": "Local file operations",
      "config_schema": {
        "type": "object",
        "properties": {
          "root_path": {
            "type": "string",
            "description": "Root directory path"
          }
        },
        "required": ["root_path"]
      }
    },
    {
      "type": "github",
      "name": "GitHub",
      "description": "Repository access",
      "config_schema": {
        "type": "object",
        "properties": {
          "repository": {
            "type": "string",
            "description": "Repository in format owner/repo"
          },
          "token": {
            "type": "string",
            "description": "GitHub personal access token"
          }
        },
        "required": ["repository", "token"]
      }
    },
    {
      "type": "git",
      "name": "Git",
      "description": "Version control",
      "config_schema": {
        "type": "object",
        "properties": {
          "repository_path": {
            "type": "string",
            "description": "Path to git repository"
          }
        },
        "required": ["repository_path"]
      }
    },
    {
      "type": "postgresql",
      "name": "PostgreSQL",
      "description": "Database access",
      "config_schema": {
        "type": "object",
        "properties": {
          "connection_string": {
            "type": "string",
            "description": "PostgreSQL connection string"
          }
        },
        "required": ["connection_string"]
      }
    }
  ]
}
```

**Status Codes:**
- 200: MCP types retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/mcp/types"
```

---

## 9. LLM Configuration APIs

### 9.1 List LLM Configurations

**Endpoint:** `GET /api/v1/llm/config`

**Purpose:** List all LLM configurations for a user.

**Query Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "configurations": [
    {
      "id": 1,
      "provider": "local",
      "model_name": "gpt2",
      "endpoint": null,
      "api_key": null,
      "temperature": 0.7,
      "max_tokens": 1000,
      "is_active": true,
      "created_at": "2026-09-16T16:00:00Z",
      "updated_at": null
    }
  ],
  "count": 1
}
```

**Status Codes:**
- 200: Configurations retrieved successfully
- 500: Internal server error

**Note:** If no local configuration exists, a default local GPT-2 configuration is automatically created.

### 9.2 Get LLM Configuration

**Endpoint:** `GET /api/v1/llm/config/{config_id}`

**Purpose:** Get a specific LLM configuration.

**Path Parameters:**
- `config_id` (integer, required): Configuration ID

**Query Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "id": 1,
  "provider": "local",
  "model_name": "gpt2",
  "endpoint": null,
  "api_key": null,
  "temperature": 0.7,
  "max_tokens": 1000,
  "is_active": true,
  "created_at": "2026-09-16T16:00:00Z",
  "updated_at": null
}
```

**Status Codes:**
- 200: Configuration retrieved successfully
- 404: Configuration not found
- 500: Internal server error

### 9.3 Get Active LLM Configuration

**Endpoint:** `GET /api/v1/llm/config/active`

**Purpose:** Get the active LLM configuration for a user.

**Query Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "id": 1,
  "provider": "local",
  "model_name": "gpt2",
  "endpoint": null,
  "api_key": null,
  "temperature": 0.7,
  "max_tokens": 1000,
  "is_active": true
}
```

**Status Codes:**
- 200: Active configuration retrieved successfully
- 500: Internal server error

**Note:** If no active configuration exists, a default local GPT-2 configuration is automatically created and activated.

### 9.4 Create LLM Configuration

**Endpoint:** `POST /api/v1/llm/config`

**Purpose:** Create a new LLM configuration.

**Request Body:**
```json
{
  "provider": "groq",
  "model_name": "llama2-70b-4096",
  "endpoint": null,
  "api_key": "gsk_...",
  "temperature": 0.7,
  "max_tokens": 1000,
  "user_id": 1
}
```

**Parameters:**
- `provider` (string, required): LLM provider (local, groq, runpod, openai, anthropic, azure, custom)
- `model_name` (string, required): Model name
- `endpoint` (string, optional): API endpoint URL (required for runpod, azure, custom)
- `api_key` (string, optional): API key (required for groq, runpod, openai, anthropic, azure, custom)
- `temperature` (float, optional): Temperature (0.0-2.0, default: 0.7)
- `max_tokens` (integer, optional): Max tokens (default: 1000)
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "id": 2,
  "provider": "groq",
  "model_name": "llama2-70b-4096",
  "endpoint": null,
  "api_key": "***",
  "temperature": 0.7,
  "max_tokens": 1000,
  "is_active": false,
  "created_at": "2026-09-16T16:00:00Z"
}
```

**Status Codes:**
- 200: Configuration created successfully
- 400: Invalid provider or parameters
- 500: Internal server error

**Note:** If this is the first configuration, it will be automatically set as active.

### 9.5 Update LLM Configuration

**Endpoint:** `PUT /api/v1/llm/config/{config_id}`

**Purpose:** Update an existing LLM configuration.

**Path Parameters:**
- `config_id` (integer, required): Configuration ID

**Request Body:**
```json
{
  "provider": "groq",
  "model_name": "mixtral-8x7b-32768",
  "endpoint": null,
  "api_key": "gsk_...",
  "temperature": 0.8,
  "max_tokens": 2000,
  "is_active": true
}
```

**Parameters:**
- `provider` (string, optional): LLM provider
- `model_name` (string, optional): Model name
- `endpoint` (string, optional): API endpoint URL
- `api_key` (string, optional): API key
- `temperature` (float, optional): Temperature
- `max_tokens` (integer, optional): Max tokens
- `is_active` (boolean, optional): Whether to activate this configuration

**Response:**
```json
{
  "id": 2,
  "provider": "groq",
  "model_name": "mixtral-8x7b-32768",
  "endpoint": null,
  "api_key": "***",
  "temperature": 0.8,
  "max_tokens": 2000,
  "is_active": true,
  "updated_at": "2026-09-16T16:05:00Z"
}
```

**Status Codes:**
- 200: Configuration updated successfully
- 400: Invalid parameters
- 404: Configuration not found
- 500: Internal server error

**Note:** If `is_active` is set to true, all other configurations for the user will be deactivated.

### 9.6 Delete LLM Configuration

**Endpoint:** `DELETE /api/v1/llm/config/{config_id}`

**Purpose:** Delete an LLM configuration.

**Path Parameters:**
- `config_id` (integer, required): Configuration ID

**Query Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "message": "Configuration deleted successfully"
}
```

**Status Codes:**
- 200: Configuration deleted successfully
- 400: Cannot delete active configuration
- 404: Configuration not found
- 500: Internal server error

**Note:** Active configurations cannot be deleted. Activate another configuration first.

### 9.7 Activate LLM Configuration

**Endpoint:** `POST /api/v1/llm/config/{config_id}/activate`

**Purpose:** Activate a specific LLM configuration.

**Path Parameters:**
- `config_id` (integer, required): Configuration ID

**Query Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "message": "Configuration activated successfully",
  "configuration": {
    "id": 2,
    "provider": "groq",
    "model_name": "llama2-70b-4096",
    "is_active": true
  }
}
```

**Status Codes:**
- 200: Configuration activated successfully
- 404: Configuration not found
- 500: Internal server error

**Note:** All other configurations for the user will be deactivated.

### 9.8 Get Available LLM Providers

**Endpoint:** `GET /api/v1/llm/providers`

**Purpose:** Get list of available LLM providers with their details.

**Response:**
```json
{
  "providers": [
    {
      "value": "local",
      "name": "Local",
      "description": "Local GPT-2 model (free, limited quality)",
      "requires_endpoint": false,
      "requires_api_key": false,
      "default_model": "gpt2"
    },
    {
      "value": "groq",
      "name": "Groq",
      "description": "Groq Cloud (free, fast, high quality)",
      "requires_endpoint": false,
      "requires_api_key": true,
      "default_model": "llama2-70b-4096"
    },
    {
      "value": "runpod",
      "name": "RunPod",
      "description": "RunPod Cloud (paid, flexible)",
      "requires_endpoint": true,
      "requires_api_key": true,
      "default_model": "custom"
    },
    {
      "value": "openai",
      "name": "OpenAI",
      "description": "OpenAI GPT models (paid, high quality)",
      "requires_endpoint": false,
      "requires_api_key": true,
      "default_model": "gpt-4"
    },
    {
      "value": "anthropic",
      "name": "Anthropic",
      "description": "Anthropic Claude models (paid, high quality)",
      "requires_endpoint": false,
      "requires_api_key": true,
      "default_model": "claude-3-opus-20240229"
    },
    {
      "value": "azure",
      "name": "Azure OpenAI",
      "description": "Azure OpenAI Service (paid, enterprise)",
      "requires_endpoint": true,
      "requires_api_key": true,
      "default_model": "gpt-4"
    },
    {
      "value": "custom",
      "name": "Custom",
      "description": "Custom LLM endpoint",
      "requires_endpoint": true,
      "requires_api_key": true,
      "default_model": "custom"
    }
  ]
}
```

**Status Codes:**
- 200: Providers retrieved successfully
- 500: Internal server error

### 9.9 Test LLM Configuration

**Endpoint:** `POST /api/v1/llm/config/test`

**Purpose:** Test a LLM configuration without saving it.

**Request Body:**
```json
{
  "provider": "groq",
  "model_name": "llama2-70b-4096",
  "endpoint": null,
  "api_key": "gsk_..."
}
```

**Parameters:**
- `provider` (string, required): LLM provider
- `model_name` (string, required): Model name
- `endpoint` (string, optional): API endpoint URL
- `api_key` (string, optional): API key

**Response:**
```json
{
  "success": true,
  "message": "Configuration is valid",
  "note": "Connection test not implemented yet"
}
```

**Status Codes:**
- 200: Configuration tested successfully
- 400: Invalid configuration
- 500: Internal server error

**Note:** This validates the configuration but does not actually test the connection to the provider.

---

## 10. Observability APIs

### 9.1 Get Observability Health

**Endpoint:** `GET /api/v1/observability/health`

**Purpose:** Get observability system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "components": {
    "observability_db": "active",
    "runtime_state": "active",
    "redis": "connected"
  }
}
```

**Status Codes:**
- 200: Health status retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/health"
```

---

### 9.2 Get Metrics

**Endpoint:** `GET /api/v1/observability/metrics`

**Purpose:** Get performance metrics.

**Query Parameters:**
- `metric_name` (string, optional): Filter by metric name
- `hours` (integer, optional): Time range in hours (default: 24)

**Response:**
```json
{
  "metrics": [
    {
      "id": 1,
      "metric_name": "agent.supervisor.success",
      "metric_value": 1.0,
      "metric_type": "counter",
      "tags": {
        "operation": "process"
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Metrics retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/metrics?hours=24"
```

---

### 9.3 Get Traces

**Endpoint:** `GET /api/v1/observability/traces`

**Purpose:** Get request traces.

**Query Parameters:**
- `trace_id` (string, optional): Filter by trace ID
- `service_name` (string, optional): Filter by service name
- `hours` (integer, optional): Time range in hours (default: 24)

**Response:**
```json
{
  "traces": [
    {
      "id": 1,
      "trace_id": "6283287f-c29b-49ae-a357-6d75c035b445",
      "span_id": "ed08ade9-ca17-4cb8-a5c3-21dbbee41868",
      "parent_span_id": "6283287f-c29b-49ae-a357-6d75c035b445",
      "operation_name": "knowledge.execute",
      "service_name": "knowledge",
      "start_time": "2024-01-01T00:00:00Z",
      "end_time": "2024-01-01T00:00:01Z",
      "duration_ms": 7.223,
      "status": "success",
      "metadata": {
        "agent": "knowledge",
        "success": true
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Traces retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/traces?hours=24"
```

---

### 9.4 Get Logs

**Endpoint:** `GET /api/v1/observability/logs`

**Purpose:** Get system logs.

**Query Parameters:**
- `level` (string, optional): Filter by log level (INFO, WARNING, ERROR, DEBUG)
- `hours` (integer, optional): Time range in hours (default: 24)

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "level": "INFO",
      "logger_name": "supervisor_agent",
      "message": "Supervisor agent started processing message",
      "context": {
        "trace_id": "6283287f-c29b-49ae-a357-6d75c035b445",
        "chat_id": 1
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Logs retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/logs?level=INFO&hours=24"
```

---

### 9.5 Get Performance Metrics

**Endpoint:** `GET /api/v1/observability/performance`

**Purpose:** Get system performance metrics (CPU, memory, disk).

**Response:**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "cpu": {
    "percent": 25.5,
    "count": 8
  },
  "memory": {
    "percent": 65.2,
    "available": 3435973888,
    "total": 17179869184,
    "used": 13738895296
  },
  "disk": {
    "percent": 45.8,
    "free": 500000000000,
    "total": 1000000000000,
    "used": 500000000000
  }
}
```

**Status Codes:**
- 200: Performance metrics retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/performance"
```

---

### 9.6 Get Runtime State

**Endpoint:** `GET /api/v1/observability/runtime-state`

**Purpose:** Get Redis runtime state and cached data.

**Response:**
```json
{
  "key_categories": {
    "conversation": 5,
    "agent_state": 3,
    "response_cache": 10,
    "tool_cache": 2,
    "screenshot_cache": 1,
    "workflow": 0,
    "memory_queue": 0,
    "other": 15
  },
  "sample_data": {
    "conversation": {
      "key": "conversation:1",
      "value": "[{\"id\":1,\"role\":\"user\",\"content\":\"Hello\"}]",
      "total_keys": 5
    },
    "agent_state": {
      "key": "agent_state:1",
      "value": "{\"current_agent\":\"knowledge\"}",
      "total_keys": 3
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Runtime state retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/runtime-state"
```

---

### 9.7 Get Database Statistics

**Endpoint:** `GET /api/v1/observability/database`

**Purpose:** Get database statistics and recent data.

**Response:**
```json
{
  "table_stats": {
    "chats": 10,
    "messages": 150,
    "users": 5,
    "memories": 25,
    "agent_executions": 30
  },
  "recent_chats": [
    {
      "id": 1,
      "title": "New conversation",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "recent_messages": [
    {
      "id": 1,
      "chat_id": 1,
      "role": "user",
      "content": "Hello",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "recent_executions": [
    {
      "id": 1,
      "chat_id": 1,
      "agent_name": "knowledge",
      "status": "completed",
      "execution_time": 0.004818,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Database statistics retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/database"
```

---

### 9.8 Get Redis Statistics

**Endpoint:** `GET /api/v1/observability/redis`

**Purpose:** Get Redis cache statistics and data.

**Response:**
```json
{
  "redis_info": {
    "used_memory_human": "256.00M",
    "connected_clients": 5,
    "total_keys": 36,
    "uptime_in_seconds": 3600
  },
  "key_categories": {
    "metric": 10,
    "timing": 5,
    "gauge": 8,
    "error": 2,
    "chat": 5,
    "other": 6
  },
  "sample_data": {
    "metric": {
      "key": "metric:cpu_usage",
      "value": "25.5",
      "total_keys": 10
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Redis statistics retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/redis"
```

---

### 9.9 Delete Logs

**Endpoint:** `DELETE /api/v1/observability/logs`

**Purpose:** Delete observability logs.

**Query Parameters:**
- `before_days` (integer, optional): Delete logs older than X days
- `level` (string, optional): Delete logs of specific level
- `logger_name` (string, optional): Delete logs from specific logger
- `delete_all` (boolean, optional): Delete all logs regardless of date

**Response:**
```json
{
  "message": "Deleted 100 logs",
  "deleted_count": 100,
  "filters": {
    "delete_all": false,
    "before_days": 7,
    "before_date": "2023-12-25T00:00:00Z",
    "level": null,
    "logger_name": null
  }
}
```

**Status Codes:**
- 200: Logs deleted successfully
- 500: Internal server error

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/observability/logs?before_days=7"
```

---

### 9.10 Delete Traces

**Endpoint:** `DELETE /api/v1/observability/traces`

**Purpose:** Delete observability traces.

**Query Parameters:**
- `before_days` (integer, optional): Delete traces older than X days
- `service_name` (string, optional): Delete traces from specific service
- `delete_all` (boolean, optional): Delete all traces regardless of date

**Response:**
```json
{
  "message": "Deleted 50 traces",
  "deleted_count": 50,
  "filters": {
    "delete_all": false,
    "before_days": 30,
    "before_date": "2023-12-02T00:00:00Z",
    "service_name": null
  }
}
```

**Status Codes:**
- 200: Traces deleted successfully
- 500: Internal server error

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/observability/traces?before_days=30"
```

---

### 9.11 Delete Metrics

**Endpoint:** `DELETE /api/v1/observability/metrics`

**Purpose:** Delete observability metrics.

**Query Parameters:**
- `before_days` (integer, optional): Delete metrics older than X days
- `metric_name` (string, optional): Delete specific metric
- `delete_all` (boolean, optional): Delete all metrics regardless of date

**Response:**
```json
{
  "message": "Deleted 200 metrics",
  "deleted_count": 200,
  "filters": {
    "delete_all": false,
    "before_days": 1,
    "before_date": "2023-12-31T00:00:00Z",
    "metric_name": null
  }
}
```

**Status Codes:**
- 200: Metrics deleted successfully
- 500: Internal server error

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/observability/metrics?before_days=1"
```

---

### 9.12 Get Observability Statistics

**Endpoint:** `GET /api/v1/observability/stats`

**Purpose:** Get observability data statistics.

**Response:**
```json
{
  "log_count": 1000,
  "trace_count": 500,
  "metric_count": 200,
  "total": 1700,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Statistics retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/stats"
```

---

## 10. Health APIs

### 10.1 Application Health Check

**Endpoint:** `GET /health`

**Purpose:** Check application health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "configuration": "valid",
  "services": {
    "api": "running",
    "redis": "connected",
    "qdrant": "connected"
  }
}
```

**Status Codes:**
- 200: Application is healthy
- 503: Service unavailable

**Example:**
```bash
curl -X GET "http://localhost:8000/health"
```

---

### 10.2 Get Configuration

**Endpoint:** `GET /config`

**Purpose:** Get application configuration (excluding secrets).

**Response:**
```json
{
  "app_name": "CortexDesk",
  "version": "1.0.0",
  "environment": "development",
  "llm_provider": "local",
  "llm_model": "gpt2",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_device": "cpu",
  "agent_timeout": 30,
  "debug": false
}
```

**Status Codes:**
- 200: Configuration retrieved successfully
- 500: Internal server error

**Example:**
```bash
curl -X GET "http://localhost:8000/config"
```

---

## 11. Error Handling

### 11.1 HTTP Status Codes

**Success Codes:**
- 200 OK: Request succeeded
- 201 Created: Resource created successfully
- 204 No Content: Request succeeded but no content returned

**Client Error Codes:**
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Authentication required
- 403 Forbidden: Access denied
- 404 Not Found: Resource not found
- 405 Method Not Allowed: HTTP method not supported
- 409 Conflict: Resource conflict
- 422 Unprocessable Entity: Validation error
- 429 Too Many Requests: Rate limit exceeded

**Server Error Codes:**
- 500 Internal Server Error: Server error
- 502 Bad Gateway: Upstream service error
- 503 Service Unavailable: Service temporarily unavailable
- 504 Gateway Timeout: Upstream service timeout

### 11.2 Error Response Format

**Standard Error Response:**
```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Validation Error Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field is required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 11.3 Common Error Scenarios

**Chat Not Found:**
```json
{
  "detail": "Chat not found",
  "status_code": 404,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Invalid User ID:**
```json
{
  "detail": "User not found",
  "status_code": 404,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Agent Execution Failed:**
```json
{
  "detail": "Agent execution failed: Connection timeout",
  "status_code": 500,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Document Upload Failed:**
```json
{
  "detail": "Failed to process document: File too large",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 12. Rate Limiting

### 12.1 Current Status

**Status:** No rate limiting implemented (local development)

### 12.2 Future Rate Limiting Strategy

**Planned Implementation:**
- Token bucket algorithm
- Per-endpoint limits
- Per-user limits
- Configurable via environment variables

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded",
  "status_code": 429,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 13. API Versioning

### 13.1 Current Version

**Version:** v1
**Version Prefix:** `/api/v1`

### 13.2 Versioning Strategy

**URL Versioning:**
- Current: `/api/v1/chats`
- Future: `/api/v2/chats`

**Header Versioning:**
- Current: Not implemented
- Future: `Accept: application/vnd.cortexdesk.v1+json`

**Deprecation Policy:**
- Deprecated endpoints supported for 6 months
- Sunset date documented in changelog
- Warning header added to deprecated endpoints

---

## 14. API Security

### 14.1 Current Security

**Status:** No authentication (local development)

### 14.2 Future Security Measures

**Authentication:**
- JWT-based authentication
- Bearer token in Authorization header
- Token refresh mechanism
- API key authentication for external access

**Authorization:**
- User-based access control
- Resource ownership validation
- Admin-only endpoints
- Role-based permissions

**CORS:**
- Configured for local development only
- Future: Configurable allowed origins

**Input Validation:**
- All inputs validated using Pydantic schemas
- SQL injection prevention via ORM
- XSS prevention via proper escaping

---

## 15. API Testing

### 15.1 Manual Testing Examples

**Test Chat Creation:**
```bash
curl -X POST "http://localhost:8000/api/v1/chats" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

**Test Assistant:**
```bash
curl -X POST "http://localhost:8000/api/v1/assistant" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?", "user_id": 1}'
```

**Test Document Upload:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "Test", "content": "Test content"}'
```

**Test Observability:**
```bash
curl -X GET "http://localhost:8000/api/v1/observability/logs"
curl -X GET "http://localhost:8000/api/v1/observability/traces"
curl -X GET "http://localhost:8000/api/v1/observability/performance"
```

---

## 16. API Documentation Generation

### 16.1 OpenAPI/Swagger

**Current Status:** FastAPI auto-generates OpenAPI schema

**Access:**
- Development: `http://localhost:8000/docs`
- JSON Schema: `http://localhost:8000/openapi.json`

**Features:**
- Interactive API documentation
- Try-it-out functionality
- Schema validation
- Request/response examples

---

## 17. API Best Practices

### 17.1 RESTful Design Principles

**Resource Naming:**
- Use nouns for resource names (chats, messages, documents)
- Use plural nouns for collections
- Use kebab-case for URLs

**HTTP Methods:**
- GET: Retrieve resources
- POST: Create resources
- PUT: Update resources (full update)
- PATCH: Partial resource update
- DELETE: Remove resources

**Status Codes:**
- Use appropriate HTTP status codes
- Return 404 for not found
- Return 400 for client errors
- Return 500 for server errors

### 17.2 API Design Guidelines

**Request/Response:**
- Use JSON for data exchange
- Use consistent field naming (snake_case)
- Include timestamps in ISO 8601 format
- Include relevant metadata

**Pagination:**
- Use `skip` and `limit` for pagination
- Return total count when possible
- Default limit: 50 items

**Filtering:**
- Use query parameters for filtering
- Support multiple filter criteria
- Document available filters

**Sorting:**
- Use `sort` query parameter
- Default sort: most recent first
- Support ascending/descending order

---

## 18. API Performance

### 18.1 Performance Considerations

**Database Queries:**
- Use async operations
- Implement connection pooling
- Use indexes for common queries
- Avoid N+1 queries

**Caching:**
- Cache frequently accessed data
- Use Redis for runtime caching
- Implement cache invalidation
- Set appropriate TTL values

**Response Time Targets:**
- Simple queries: < 100ms
- Complex queries: < 500ms
- Agent execution: < 10s
- Document upload: < 30s

---

## 19. API Monitoring

### 19.1 Metrics to Track

**Request Metrics:**
- Request count per endpoint
- Request duration (p50, p95, p99)
- Error rate per endpoint
- Request rate per user

**Business Metrics:**
- Chats created per day
- Messages sent per day
- Documents uploaded per day
- Agent execution success rate

**System Metrics:**
- Database connection pool usage
- Redis memory usage
- Qdrant query performance
- CPU and memory usage

---

## 20. API Deprecation Policy

### 20.1 Deprecation Process

**Deprecation Timeline:**
1. Announce deprecation in changelog
2. Add deprecation warning to response headers
3. Support deprecated endpoint for 6 months
4. Remove deprecated endpoint
5. Update documentation

**Deprecation Header:**
```
Warning: This endpoint is deprecated and will be removed on 2024-07-01. Use /api/v2/chats instead.
```

---

**End of Part 3: API Specifications**

Continue to Part 4: Agent Implementation Details
