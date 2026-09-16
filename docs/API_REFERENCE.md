# Windows AI Assistant - API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. This will be implemented in a future update.

## Endpoints

### Health Check

#### GET /health

Check the health status of the API and connected services.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "running",
    "redis": "connected",
    "qdrant": "connected"
  }
}
```

### Chat Management

#### POST /chats

Create a new chat session.

**Request Body:**
```json
{
  "title": "New Chat",
  "user_id": 1,
  "context": {},
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "New Chat",
  "status": "active",
  "context": null,
  "metadata": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### GET /chats/{chat_id}

Get a chat with its messages.

**Parameters:**
- `chat_id` (path): Chat ID

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "New Chat",
  "status": "active",
  "context": null,
  "metadata": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "messages": [
    {
      "id": 1,
      "chat_id": 1,
      "role": "user",
      "content": "Hello",
      "agent_used": null,
      "tool_calls": null,
      "metadata": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET /chats

List all chats for a user.

**Query Parameters:**
- `user_id` (required): User ID
- `skip` (optional): Number of chats to skip (default: 0)
- `limit` (optional): Number of chats to return (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "New Chat",
    "status": "active",
    "context": null,
    "metadata": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### DELETE /chats/{chat_id}

Delete a chat (soft delete).

**Parameters:**
- `chat_id` (path): Chat ID

**Response:**
```json
{
  "message": "Chat deleted successfully"
}
```

### Message Management

#### POST /chats/{chat_id}/messages

Add a message to a chat.

**Parameters:**
- `chat_id` (path): Chat ID

**Request Body:**
```json
{
  "role": "user",
  "content": "Hello, how are you?",
  "agent_used": null,
  "tool_calls": null,
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 2,
  "chat_id": 1,
  "role": "user",
  "content": "Hello, how are you?",
  "agent_used": null,
  "tool_calls": null,
  "metadata": null,
  "created_at": "2024-01-15T10:30:01Z"
}
```

### Assistant

#### POST /assistant

Process a user message through the multi-agent assistant.

**Request Body:**
```json
{
  "message": "Explain this repository",
  "user_id": 1,
  "chat_id": 1,
  "context": {
    "repository_path": "/path/to/repo"
  },
  "stream": false
}
```

**Response:**
```json
{
  "response": "This repository contains a multi-agent AI assistant system...",
  "agents_used": ["code", "knowledge"],
  "agent_results": [
    {
      "success": true,
      "agent": "code",
      "result": {
        "response": "Repository analysis complete..."
      }
    }
  ],
  "execution_plan": {
    "intent": "repository analysis",
    "agents": ["code"],
    "plan": {
      "code": "Analyze repository structure and key files"
    }
  },
  "chat_id": 1,
  "message_id": 3
}
```

## Data Models

### Chat

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique chat identifier |
| user_id | integer | User ID |
| title | string | Chat title |
| status | string | Chat status (active, archived, deleted) |
| context | object | Chat context (JSON) |
| metadata | object | Additional metadata (JSON) |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Message

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique message identifier |
| chat_id | integer | Chat ID |
| role | string | Message role (user, assistant, system) |
| content | string | Message content |
| agent_used | string | Agent that handled the message |
| tool_calls | array | Tool calls made (JSON) |
| metadata | object | Additional metadata (JSON) |
| created_at | datetime | Creation timestamp |

### Assistant Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User message |
| user_id | integer | Yes | User ID |
| chat_id | integer | No | Chat ID (creates new if not provided) |
| context | object | No | Additional context |
| stream | boolean | No | Enable streaming (default: false) |

### Assistant Response

| Field | Type | Description |
|-------|------|-------------|
| response | string | Assistant response |
| agents_used | array | List of agents used |
| agent_results | array | Individual agent results |
| execution_plan | object | Execution plan used |
| chat_id | integer | Chat ID |
| message_id | integer | Message ID |

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Validation error"
}
```

### 404 Not Found

```json
{
  "detail": "Chat not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Agent execution failed: error message"
}
```

## Rate Limiting

Currently not implemented. Will be added in future updates.

## CORS

The API supports CORS for the following origins (configurable in `.env`):
- `http://localhost:3000`
- `http://localhost:5173`

## Streaming

Streaming responses are supported but not yet implemented in the frontend. To enable streaming:

1. Set `"stream": true` in the assistant request
2. Handle Server-Sent Events (SSE) in the client

## Future Endpoints

Planned endpoints for future releases:

- `/users` - User management
- `/documents` - Document upload and management
- `/memories` - Memory management
- `/agents` - Agent configuration
- `/evals` - Evaluation and testing
- `/admin` - Administrative functions

## WebSocket Support

WebSocket support for real-time communication is planned for future releases.

## SDK Examples

### Python

```python
import requests

# Create chat
chat = requests.post(
    "http://localhost:8000/api/v1/chats",
    json={"user_id": 1, "title": "My Chat"}
).json()

# Send message
response = requests.post(
    "http://localhost:8000/api/v1/assistant",
    json={
        "message": "Hello",
        "user_id": 1,
        "chat_id": chat["id"]
    }
).json()

print(response["response"])
```

### JavaScript

```javascript
// Create chat
const chat = await fetch('http://localhost:8000/api/v1/chats', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, title: 'My Chat' })
}).then(r => r.json());

// Send message
const response = await fetch('http://localhost:8000/api/v1/assistant', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello',
    user_id: 1,
    chat_id: chat.id
  })
}).then(r => r.json());

console.log(response.response);
```

### cURL

```bash
# Create chat
curl -X POST http://localhost:8000/api/v1/chats \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "My Chat"}'

# Send message
curl -X POST http://localhost:8000/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": 1, "chat_id": 1}'
```

## Support

For API issues or questions:
- Check the backend logs for error details
- Verify all services are running (health check)
- Review the implementation status document
- Check the troubleshooting section in SETUP.md
