# CortexDesk

**Your Intelligent Multi-Agent Workspace Assistant**

A multi-agent AI assistant that provides intelligent task automation, document management with RAG, real-time observability, and seamless Windows integration. CortexDesk acts as your Engineering Copilot, Knowledge Assistant, Productivity Manager, and System Administrator in one unified platform.

---

## 🌟 Overview

CortexDesk is a comprehensive multi-agent AI system designed to enhance your productivity and development workflow. It features a sophisticated architecture with separate storage layers for different data types, real-time observability, intelligent document management with RAG capabilities, and a modern React-based frontend with comprehensive UX improvements.

**Current Configuration:**
- **Generation Model:** GPT-2 (local, 124M parameters) - Configurable via UI
- **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2 (local, 384 dimensions)
- **Cost:** Free with local models, paid for cloud providers
- **Privacy:** 100% local data storage
- **Quality:** Configurable - switch between local and cloud models
- **LLM Providers:** Local, Groq, RunPod, OpenAI, Anthropic, Azure, Custom

**Note:** GPT-2 is configured for testing and development. You can switch to cloud models (Groq, RunPod, OpenAI, Anthropic, Azure) directly from the UI for better quality and performance.

### What Makes It Different

- **🤖 Multi-Agent Architecture**: 6 specialized agents with full orchestration and logging
- **📊 Real-Time Observability**: Complete visibility into system performance with auto-refresh and filtering
- **📄 Document Management with RAG**: Upload, search, and retrieve documents with local embeddings
- **🔒 Local-First Privacy**: Your data stays on your machine
- **🧠 Intelligent Memory**: Separate layers for runtime state and long-term storage
- **🎯 Context-Aware**: Understands your current work context
- **⚡ Real-Time Assistance**: Instant help with code, documents, and system tasks
- **🖥️ Native Windows Integration**: Deep integration with Windows features
- **🎨 Modern UX**: Toast notifications, keyboard shortcuts, accessibility features, loading states
- **🔌 MCP Integration**: Manage and monitor Model Context Protocol integrations
- **🗑️ Data Management**: Purge old observability data to manage storage

---

## ✨ Key Features

### 🤖 Multi-Agent System

- **Supervisor Agent**: Intent understanding and orchestration
- **Code Agent**: Repository search, code explanation, architecture analysis
- **Knowledge Agent**: Document search, RAG retrieval, knowledge synthesis
- **Windows Agent**: Application control, file search, screenshot intelligence
- **System Agent**: Container management, terminal intelligence, system diagnostics
- **Productivity Agent**: Task management, work journal, status reports

### 📊 Observability & Monitoring

- **Real-Time Dashboard**: System health, performance metrics, and resource usage
- **Logs & Traces**: Complete visibility into agent execution and system events
- **Database Monitoring**: Track chat history, messages, and agent executions
- **Runtime State**: Monitor Redis cache with categorized key analysis
- **Metrics Collection**: Track agent performance, errors, and system health
- **Data Management**: Delete logs, traces, and metrics with flexible pruning options

### 📄 Document Management with RAG

- **Document Upload**: Add text documents, notes, and knowledge base content
- **Automatic Chunking**: Intelligent text segmentation for optimal retrieval
- **Semantic Search**: Find relevant documents using vector similarity
- **Local Embeddings**: Full RAG support with sentence-transformers/all-MiniLM-L6-v2
- **Document Status**: Track embedding status and chunk count
- **Search Interface**: Query documents with relevance scoring
- **Qdrant Integration**: Vector storage with 384-dimensional embeddings

### 🔧 Core Capabilities

**Code Intelligence:**
- Explain code and architecture
- Search repositories and analyze PRs
- Debug errors and suggest fixes
- Review code quality

**Knowledge Management:**
- Search across documents, notes, and code
- RAG-based information retrieval (with embedding support)
- Document summarization
- Knowledge synthesis

**Windows Automation:**
- Open and control applications
- File search and management
- Screenshot capture and analysis
- Clipboard management

**System Administration:**
- Container management (Docker/Podman)
- Process and service monitoring
- Terminal command analysis
- Log analysis and diagnostics

**Productivity:**
- Task and calendar management
- Work journal with automatic tracking
- Status report generation
- Daily briefings

### 🛡️ Security & Privacy

- **Local-First Data Storage**: All data stored locally
- **Separate Storage Layers**: PostgreSQL for business data + observability, Redis for runtime state, Qdrant for AI memory
- **Security Guardrails**: Input validation and tool risk classification
- **No External API Calls**: Works completely offline with local models
- **Local Embeddings**: sentence-transformers/all-MiniLM-L6-v2 for semantic search without external dependencies
- **Encrypted Storage**: Secure credential and data handling
- **Access Control**: File system and command execution permissions
- **Observability Data Management**: Flexible pruning and deletion of logs/traces/metrics
- **Configuration Validation**: Startup validation for required settings
- **Secret Key Management**: Secure secret key generation and validation

### 🎨 User Experience

- **Toast Notifications**: Success, error, warning, and info messages
- **Keyboard Shortcuts**: Ctrl+N (new chat), Ctrl+D (documents), Ctrl+O (observability), Ctrl+M (MCP), Ctrl+L (LLM config), ? (about)
- **Loading States**: Skeleton loaders and progress indicators
- **Error Handling**: User-friendly error messages with retry mechanisms
- **Accessibility**: Screen reader support, keyboard navigation, high contrast mode
- **Real-Time Updates**: Auto-refresh with configurable intervals
- **Data Filtering**: Search and filter logs and traces
- **Drag-and-Drop**: File upload with drag-and-drop support
- **Status Indicators**: Visual status for MCP integrations and connections
- **LLM Configuration**: Switch between local and cloud LLM providers from the UI

### 🔌 LLM Configuration

CortexDesk supports multiple LLM providers that you can configure directly from the UI:

**Supported Providers:**
- **Local**: GPT-2 (free, limited quality)
- **Groq**: Fast, free cloud models (llama2-70b, mixtral-8x7b)
- **RunPod**: Flexible GPU-based models (paid)
- **OpenAI**: GPT-4, GPT-3.5 (paid)
- **Anthropic**: Claude 3 Opus, Sonnet (paid)
- **Azure OpenAI**: Enterprise OpenAI (paid)
- **Custom**: Any OpenAI-compatible endpoint

**Configuration Features:**
- Add multiple LLM configurations
- Switch between providers instantly
- Configure model parameters (temperature, max tokens)
- Test connections before saving
- API key management
- Per-user configuration storage

**How to Configure:**
1. Click the "LLM" button in the header (or press Ctrl+L)
2. Click "Add Configuration"
3. Select your provider
4. Enter required credentials (endpoint, API key)
5. Configure model parameters
6. Test the connection
7. Save and activate the configuration

---

## 🚀 Quick Start

### Prerequisites

**For Web App:**
- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Qdrant 1.12+**

**For Desktop App:**
- **Windows 10/11**
- **Docker Desktop** (for backend services)
- Or manual backend setup (PostgreSQL, Redis, Qdrant, Python)

### Installation

#### Option 1: Web Application (Recommended for Testing)

```bash
# 1. Clone the repository
git clone https://github.com/dipanwitasarkar/CortexDesk.git
cd CortexDesk

# 2. Set up backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Set up frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open browser
# Navigate to http://localhost:5173
```

#### Option 2: Desktop Application

**Download:**
- Windows: Download from GitHub Actions artifacts
- macOS: Download from GitHub Actions artifacts  
- Linux: Download from GitHub Actions artifacts

**Setup (Required):**
The desktop app requires the backend to be running. You have two options:

**Option A: Docker (Recommended)**
```bash
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Clone repository
git clone https://github.com/dipanwitasarkar/CortexDesk.git
cd CortexDesk

# 3. Start backend services
docker-compose up -d

# 4. Install and launch desktop app
# Double-click the downloaded installer
# Launch from Start Menu
```

**Option B: Manual Backend Setup**
```bash
# 1. Install PostgreSQL, Redis, Qdrant manually
# 2. Setup Python backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Install and launch desktop app
# Double-click the downloaded installer
# Launch from Start Menu
```

**Important:** The desktop app connects to the backend at `http://localhost:8000`. Ensure the backend is running before launching the desktop app.

#### Option 3: Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/dipanwitasarkar/CortexDesk.git
cd CortexDesk

# 2. Set up backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python -m uvicorn app.main:app --reload

# 3. Set up frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Open browser
# Navigate to http://localhost:5173
```

### Building Desktop App

```bash
# Linux
cd frontend
npm run tauri:build

# Windows (requires Windows machine)
cd frontend
npm run tauri:build

# macOS (requires macOS machine)
cd frontend
npm run tauri:build
```

**Or use GitHub Actions** for automated cross-platform builds:
- Push to main branch
- Download artifacts from Actions page
- Or create a tag for GitHub Release

### Access Points

- **Desktop App**: Launch from desktop icon
- **Web Interface**: http://localhost:5173 (development)
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📖 Documentation

### User Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive user guide
- **[QUICKSTART.md](QUICKSTART.md)** - 15-minute quick start

### Developer Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - API documentation

---

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- React - UI framework
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Styling
- Lucide Icons - Icon library

**Backend:**
- Python 3.12+ - Backend language
- FastAPI - Web framework
- LangChain - LLM framework
- SQLAlchemy - ORM

**Databases:**
- PostgreSQL - Business data + observability (logs, traces, metrics)
- Redis - Runtime state (2GB limit, allkeys-lru eviction)
- Qdrant v1.12.0 - Vector database for RAG and AI memory

**AI Models:**
- **Generation:** GPT-2 (local) / Groq / RunPod
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2 (local)
- **Purpose:** Chat, agent reasoning, summarization, planning, document embeddings, semantic search, RAG

### System Architecture

```
React Frontend (Web Interface)
    ↓
FastAPI Backend
    ↓
Supervisor Agent
    ↓
Specialized Agents (Code, Knowledge, Windows, System, Productivity)
    ↓
MCP Layer (Filesystem, GitHub, PostgreSQL, PowerShell)
    ↓
LLM (gpt2 / Groq / RunPod)
    ↓
Storage Layers:
  - PostgreSQL: Business data + observability
  - Redis: Runtime state (conversation, agent state, caches)
  - Qdrant: AI memory + document embeddings
```

### Storage Architecture

**PostgreSQL (Persistent Storage):**
- Chats and messages
- Users and sessions
- Agent execution history
- Observability logs
- Observability traces
- Observability metrics
- Document metadata

**Redis (Runtime State - Working Memory):**
- Conversation context (last 50 messages, 24h TTL)
- Agent state (4h TTL)
- Response cache (1h TTL)
- Tool cache (5-15 min TTL)
- Screenshot cache (24h TTL)
- Workflow state (4h TTL)
- Memory queue (24h TTL)
- Max memory: 2GB with allkeys-lru eviction

**Qdrant (AI Memory):**
- Long-term memory embeddings
- Document chunks for RAG
- Vector similarity search
- Knowledge base storage

---

## 🎯 Usage Examples

### Code Assistance
```
"Explain the main function in app.py"
"Find all usages of the calculate_total method"
"Analyze this repository architecture"
"Review PR #123"
```

### Knowledge Search
```
"Find documents about WMS architecture"
"What do you know about microservices?"
"Summarize the design document"
"Search for information about authentication"
```

### Document Management
```
"Upload my project documentation"
"Search for information about API endpoints"
"What documents do I have about authentication?"
"Find relevant content about database design"
```

### Windows Automation
```
"Open VS Code"
"Search for Python files in my project"
"Take a screenshot"
"Analyze this screenshot"
```

### System Administration
```
"Check running Docker containers"
"Explain this error: permission denied"
"Show me system resources"
"Analyze terminal output"
```

### Productivity
```
"Add a task: Review PR #123"
"What did I work on this week?"
"Generate my weekly status report"
"Give me my daily briefing"
```

### Observability
```
"Show me system performance metrics"
"What are the recent errors?"
"Check agent execution history"
"Display runtime state information"
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# LLM Configuration (Choose one)
# Option 1: Local GPT-2 + sentence-transformers (default, free, full RAG)
DELL_LLM_ENDPOINT=local
DELL_LLM_API_KEY=
DELL_LLM_MODEL=gpt2
DELL_LLM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Option 2: Groq (free, fast, better quality)
# DELL_LLM_ENDPOINT=https://api.groq.com/openai/v1
# DELL_LLM_API_KEY=your-groq-api-key
# DELL_LLM_MODEL=llama-3.1-8b-instant
# DELL_LLM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Option 3: RunPod (paid, excellent quality)
# DELL_LLM_ENDPOINT=https://api.runpod.ai/v2
# DELL_LLM_API_KEY=your-runpod-api-key
# DELL_LLM_MODEL=qwen-32b-chat
# DELL_LLM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_assistant
DATABASE_SYNC_URL=postgresql://postgres:postgres@localhost:5432/ai_assistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=ai_assistant_memory

# Application Configuration
SECRET_KEY=your-secret-key
DEBUG=True
APP_NAME=CortexDesk
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Redis Configuration

Redis is configured with memory limits and eviction policies in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

**TTL Settings:**
- Session Context: 24h
- Agent State: 4h
- Tool Cache: 5-15 min
- LLM Cache: 1h
- Workflow State: 4h
- Screenshot Cache: 24h

### Observability Data Management

**Delete Logs:**
```bash
# Delete all logs
curl -X DELETE "http://localhost:8000/api/v1/observability/logs?delete_all=true"

# Delete logs older than 7 days
curl -X DELETE "http://localhost:8000/api/v1/observability/logs?before_days=7"

# Delete only ERROR level logs
curl -X DELETE "http://localhost:8000/api/v1/observability/logs?level=ERROR"
```

**Delete Traces:**
```bash
# Delete all traces
curl -X DELETE "http://localhost:8000/api/v1/observability/traces?delete_all=true"

# Delete traces older than 30 days
curl -X DELETE "http://localhost:8000/api/v1/observability/traces?before_days=30"
```

**Delete Metrics:**
```bash
# Delete all metrics
curl -X DELETE "http://localhost:8000/api/v1/observability/metrics?delete_all=true"

# Delete metrics older than 7 days
curl -X DELETE "http://localhost:8000/api/v1/observability/metrics?before_days=7"
```

**Get Statistics:**
```bash
curl -s http://localhost:8000/api/v1/observability/stats
```

### Agent Configuration

Configure agents in the application settings:
- Filesystem paths for Code Agent
- Document folders for Knowledge Agent
- Application shortcuts for Windows Agent
- Container connections for System Agent

---

## 🔧 Development

### Project Structure

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
└── docs/                  # Developer documentation
    ├── ARCHITECTURE.md    # System architecture
    └── API_REFERENCE.md   # API documentation
```

### Running Tests

```bash
# Structure tests
cd backend
python3 test_structure.py

# Functional tests (require full environment)
python3 test_new_features.py
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Build Electron app
npm run electron:build

# Output: dist/Windows AI Assistant Setup.exe
```

---

## 📊 Current Status

### MVP Completion: ✅ 100%

All Phase 1 MVP features are complete:

- ✅ React frontend with chat interface
- ✅ FastAPI backend with async operations
- ✅ Multi-agent system (6 agents)
- ✅ Storage layers (PostgreSQL, Redis, Qdrant)
- ✅ MCP integrations (Filesystem, GitHub, PostgreSQL, PowerShell)
- ✅ Persistent chat with message history
- ✅ RAG pipeline with document management
- ✅ Security guardrails
- ✅ Observability & logging system
- ✅ Screenshot intelligence
- ✅ Terminal intelligence
- ✅ Real-time observability dashboard
- ✅ Document management with upload/search
- ✅ Runtime state management
- ✅ Flexible observability data pruning

### New Features (v1.0.0):

**Observability System:**
- Real-time dashboard with 5 tabs (Overview, Logs, Traces, Database, Runtime State)
- PostgreSQL-based logs, traces, and metrics storage
- Redis runtime state monitoring with categorized key analysis
- Flexible data management with delete/prune options
- System health monitoring and performance metrics

**Document Management with RAG:**
- Document upload with automatic chunking
- Local embeddings with sentence-transformers/all-MiniLM-L6-v2
- Semantic search with vector similarity
- Qdrant v1.12.0 vector storage with 384-dimensional embeddings
- Document status tracking (pending, processing, completed, failed)
- Search interface with relevance scoring
- Full RAG support without external dependencies

**Storage Architecture:**
- PostgreSQL for business data and observability
- Redis with 2GB limit and allkeys-lru eviction
- Configurable TTLs for different state types
- Qdrant v1.12.0 for AI memory and document embeddings
- Local-first approach with complete offline capability

### Success Criteria: ✅ 10/10

The assistant successfully handles all planned use cases with enhanced observability and document management capabilities.

---

## 🗺️ Roadmap

### Phase 2 (Future Enhancements)

- User authentication system
- Advanced RAG features
- Streaming responses
- Enhanced screenshot intelligence with vision models
- Terminal monitoring integration
- Microsoft ecosystem integration (Outlook, Teams)
- Plugin system for custom agents
- Multi-user support

### Enterprise Features

- Role-based access control
- Advanced security features
- Audit logging
- Team collaboration
- Advanced monitoring and analytics
- Backup and disaster recovery

---

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation
- Follow the existing code style

---

## 📝 License

Internal Use Only

---

## 🆘 Support

### Getting Help

- **Desktop App (Docker)**: [DOCKER_DESKTOP_APP.md](DOCKER_DESKTOP_APP.md)
- **Desktop App (Tauri)**: [TAURI_DESKTOP_APP.md](TAURI_DESKTOP_APP.md)
- **Low-Level Design**: [docs/LLD_PART1_ARCHITECTURE.md](docs/LLD_PART1_ARCHITECTURE.md)

### Reporting Issues

For bugs or feature requests, please use the appropriate channels within your organization.

---

## 🎉 Acknowledgments

Built with:
- **LangChain** for LLM framework and agent orchestration
- **FastAPI** for the backend framework
- **React** for the frontend UI
- **PostgreSQL** for persistent storage and observability
- **Redis** for runtime state management
- **Qdrant** for vector database and RAG
- **Docker** for container orchestration
- The open-source community for the amazing tools and libraries

---

**Version**: 1.0.0  
**Last Updated**: 2026-09-16  
**Status**: Production Ready ✅  
**Repository**: https://github.com/dipanwitasarkar/CortexDesk
