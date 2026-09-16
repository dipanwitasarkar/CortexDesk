# Windows AI Assistant - Setup Guide

This guide will help you set up and run the Windows AI Assistant on your local machine.

## Prerequisites

### Required Software

- **Python 3.12+**: [Download here](https://www.python.org/downloads/)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Podman or Docker**: 
  - Podman: [Download here](https://podman.io/getting-started/installation)
  - Docker: [Download here](https://www.docker.com/products/docker-desktop/)
- **Git**: [Download here](https://git-scm.com/downloads)
- **Windows 10/11**: Required for Windows-specific features

### Optional Software

- **VS Code**: Recommended for development [Download here](https://code.visualstudio.com/)
- **Postman**: For API testing [Download here](https://www.postman.com/downloads/)

## Project Structure

```
windows-ai-assistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # Agent implementations
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── mcp/            # MCP integrations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Electron + React frontend
│   ├── electron/          # Electron main process
│   ├── src/               # React source
│   ├── package.json
│   └── vite.config.ts
├── infrastructure/         # Docker Compose configuration
│   └── docker-compose.yml
└── docs/                  # Documentation
```

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd windows-ai-assistant
```

### 2. Set Up Local Infrastructure

Start the local services (PostgreSQL, Redis, Qdrant):

```bash
cd infrastructure
podman-compose up -d
```

Or if using Docker:

```bash
docker-compose up -d
```

Verify services are running:

```bash
podman-compose ps
```

Expected output:
```
NAME                       STATUS
ai-assistant-postgres      Up (healthy)
ai-assistant-redis         Up (healthy)
ai-assistant-qdrant        Up (healthy)
```

### 3. Configure Backend

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Create environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Dell LLM Configuration
DELL_LLM_ENDPOINT=https://your-dell-endpoint.com/v1
DELL_LLM_API_KEY=your-api-key
DELL_LLM_MODEL=your-model-name
DELL_LLM_EMBEDDING_MODEL=your-embedding-model

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_assistant
DATABASE_SYNC_URL=postgresql://postgres:postgres@localhost:5432/ai_assistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=ai_assistant_memory

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
```

### 4. Start Backend Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 5. Configure Frontend

```bash
cd frontend
npm install
```

### 6. Start Frontend Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 7. Run Electron App

For development with hot reload:

```bash
npm run electron:dev
```

This will start both the Vite dev server and Electron.

## Verification

### Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

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

### Test API Endpoints

```bash
# Create a chat
curl -X POST http://localhost:8000/api/v1/chats \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "Test Chat"}'

# Send a message to assistant
curl -X POST http://localhost:8000/api/v1/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": 1}'
```

## Dell LLM Configuration

### Setting Up Dell LLM Endpoint

1. Obtain your Dell LLM endpoint URL and API key
2. Configure in `.env` file:

```env
DELL_LLM_ENDPOINT=https://your-dell-endpoint.com/v1
DELL_LLM_API_KEY=your-api-key
DELL_LLM_MODEL=gpt-4
DELL_LLM_EMBEDDING_MODEL=text-embedding-ada-002
```

### Testing Dell LLM Connection

The backend will automatically test the connection on startup. You can also test manually:

```python
from app.services.llm_service import llm_service

async def test_llm():
    response = await llm_service.generate_response([
        {"role": "user", "content": "Hello, can you hear me?"}
    ])
    print(response)
```

## MCP Configuration

### Filesystem MCP

Configure allowed paths in your code:

```python
from app.mcp.filesystem_mcp import FilesystemMCP

filesystem_mcp = FilesystemMCP()
filesystem_mcp.add_allowed_path("/home/user/projects")
filesystem_mcp.add_allowed_path("C:\\Users\\user\\Documents")
```

### GitHub MCP

Set up GitHub token for private repositories:

```env
GITHUB_TOKEN=your-github-personal-access-token
```

### PowerShell MCP

PowerShell MCP works automatically on Windows. No additional configuration needed.

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Verify PostgreSQL is running:
   ```bash
   podman-compose logs postgres
   ```

2. Check connection string in `.env`

3. Test connection manually:
   ```bash
   psql -h localhost -U postgres -d ai_assistant
   ```

### Redis Connection Issues

1. Verify Redis is running:
   ```bash
   podman-compose logs redis
   ```

2. Test connection:
   ```bash
   redis-cli ping
   ```

### Qdrant Connection Issues

1. Verify Qdrant is running:
   ```bash
   podman-compose logs qdrant
   ```

2. Check Qdrant web UI: http://localhost:6333/dashboard

### Frontend Build Issues

If you encounter build errors:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Electron Issues

If Electron fails to start:

1. Check Electron version compatibility
2. Verify main.ts path in package.json
3. Check console for error messages

## Development Workflow

### Backend Development

1. Make changes to backend code
2. Backend auto-reloads with `--reload` flag
3. Test changes via API or frontend

### Frontend Development

1. Make changes to React components
2. Frontend hot-reloads automatically
3. Test changes in browser or Electron

### Adding New Agents

1. Create new agent in `backend/app/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods
4. Register in `SupervisorAgent`

### Adding New MCP Integrations

1. Create new MCP in `backend/app/mcp/`
2. Inherit from `BaseMCP`
3. Implement required methods
4. Use in agents as needed

## Production Deployment

### Backend Deployment

1. Set `DEBUG=False` in `.env`
2. Use production ASGI server (Gunicorn):
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
3. Set up proper logging
4. Configure reverse proxy (nginx)

### Frontend Deployment

1. Build for production:
   ```bash
   npm run build
   ```
2. Build Electron app:
   ```bash
   npm run electron:build
   ```
3. Distribute built executable

### Infrastructure Deployment

1. Use production-grade database
2. Set up Redis clustering
3. Configure Qdrant for production
4. Set up monitoring and backups

## Security Considerations

1. Never commit `.env` file
2. Use strong `SECRET_KEY`
3. Implement proper authentication
4. Use HTTPS in production
5. Regularly update dependencies
6. Implement rate limiting
7. Set up proper CORS configuration

## Next Steps

1. Configure your Dell LLM endpoint
2. Set up authentication system
3. Add your documents to knowledge base
4. Configure allowed filesystem paths
5. Set up GitHub integration
6. Implement guardrails and security
7. Set up observability and monitoring
8. Add screenshot intelligence
9. Add terminal intelligence

## Support

For issues and questions:
- Check the documentation in `docs/`
- Review error logs in backend console
- Check browser console for frontend errors
- Verify all services are running
