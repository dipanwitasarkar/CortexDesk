# Windows AI Assistant - Quick Start Guide

Get up and running with the Windows AI Assistant in 15 minutes.

## Prerequisites Check

Ensure you have:
- [ ] Python 3.12+ installed
- [ ] Node.js 18+ installed  
- [ ] Podman or Docker installed
- [ ] Git installed
- [ ] Windows 10/11

## 5-Minute Setup

### 1. Start Infrastructure (2 minutes)

```bash
cd infrastructure
podman-compose up -d
```

Verify services are running:
```bash
podman-compose ps
```

### 2. Configure Backend (2 minutes)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your Dell LLM credentials:
```env
DELL_LLM_ENDPOINT=https://your-dell-endpoint.com/v1
DELL_LLM_API_KEY=your-api-key
```

### 3. Start Backend (1 minute)

```bash
python -m uvicorn app.main:app --reload
```

Backend will be at `http://localhost:8000`

### 4. Start Frontend (1 minute)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be at `http://localhost:5173`

### 5. Run Electron App (optional)

```bash
npm run electron:dev
```

## Verify Installation

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

### Test Assistant
Open `http://localhost:5173` in your browser and try:
- "Hello, can you help me?"
- "What can you do?"
- "Search for Python files in my project"

## First Steps

### 1. Configure Filesystem Access
Add allowed paths in your code:
```python
from app.mcp.filesystem_mcp import FilesystemMCP

filesystem_mcp = FilesystemMCP()
filesystem_mcp.add_allowed_path("C:\\Users\\YourName\\Documents")
```

### 2. Add GitHub Integration (optional)
Set your GitHub token in `.env`:
```env
GITHUB_TOKEN=your-github-token
```

### 3. Add Documents to Knowledge Base
Use the Knowledge Agent to index your documents:
- "Add this PDF to my knowledge base"
- "Index my project documentation"

### 4. Test Different Agents
Try various capabilities:
- **Code Agent**: "Explain the main function in this file"
- **Knowledge Agent**: "Find information about WMS architecture"
- **Windows Agent**: "Open VS Code"
- **System Agent**: "Check running Docker containers"
- **Productivity Agent**: "Create a task for code review"

## Common Issues

### Backend won't start
- Check if port 8000 is available
- Verify Python dependencies are installed
- Check `.env` file is configured

### Frontend won't start
- Check if port 5173 is available
- Verify Node.js version is 18+
- Delete `node_modules` and reinstall

### Database connection error
- Verify PostgreSQL is running: `podman-compose ps`
- Check connection string in `.env`
- Ensure database was created

### Redis connection error
- Verify Redis is running: `podman-compose logs redis`
- Check Redis URL in `.env`
- Test with: `redis-cli ping`

### Qdrant connection error
- Verify Qdrant is running: `podman-compose logs qdrant`
- Check Qdrant URL in `.env`
- Access dashboard: `http://localhost:6333`

## Next Steps

1. **Configure Dell LLM**: Set up your Dell endpoint credentials
2. **Add Your Data**: Index documents and code repositories
3. **Customize Agents**: Modify agent behavior for your needs
4. **Set Up Security**: Configure authentication and guardrails
5. **Explore Features**: Try all agent capabilities

## Getting Help

- Check [SETUP.md](SETUP.md) for detailed setup instructions
- Review [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- See [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) for feature status
- Check logs in backend console for errors

## Tips for Success

1. **Start Small**: Test basic chat before complex features
2. **Configure Paths**: Set up allowed filesystem paths early
3. **Monitor Resources**: Keep an eye on memory and CPU usage
4. **Test Incrementally**: Verify each component before moving to the next
5. **Read Logs**: Check console logs for debugging information

## Example Workflows

### Code Analysis Workflow
1. "Search for Python files in my project"
2. "Explain the main function in app.py"
3. "Find all usages of the calculate_total function"
4. "Review the architecture of this codebase"

### Knowledge Management Workflow
1. "Add this PDF to my knowledge base"
2. "Find information about WMS architecture"
3. "Summarize the design document"
4. "What do you know about my current project?"

### Productivity Workflow
1. "Create a task: Review PR #123"
2. "Add meeting note: Discussed architecture changes"
3. "Generate my weekly status report"
4. "What are my priorities for today?"

### System Administration Workflow
1. "Check running Docker containers"
2. "Show me system resources"
3. "List WSL distributions"
4. "Check recent system logs"

You're now ready to use your Windows AI Assistant! 🚀
