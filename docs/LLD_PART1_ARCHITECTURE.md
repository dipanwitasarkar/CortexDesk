# CortexDesk Low-Level Design (LLD) - Part 1: Architecture

## Document Overview

This document provides a comprehensive low-level design of the CortexDesk multi-agent AI system. It covers the complete architecture, data models, API specifications, deployment details, and implementation decisions.

**Document Parts:**
- Part 1: Architecture & System Design (This document)
- Part 2: Data Models & Database Schema
- Part 3: API Specifications
- Part 4: Agent Implementation Details
- Part 5: Frontend Architecture
- Part 6: Deployment & Infrastructure

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                   (React + TypeScript + Vite)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│                   (FastAPI + Python 3.12)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ PostgreSQL   │ │   Redis      │ │   Qdrant     │ │  Local LLM   │
│              │ │              │ │              │ │  (GPT-2)     │
│ Business Data│ │ Runtime State│ │ Vector DB    │ │              │
│ Observability│ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### 1.2 Component Architecture

#### 1.2.1 Frontend (React + TypeScript)

**Technology Stack:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 5.4.21
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **State Management:** React Hooks (useState, useEffect, useContext)
- **HTTP Client:** Fetch API with Vite proxy

**Key Components:**
- `App.tsx` - Main application component with routing and modals
- `ChatInterface.tsx` - Chat interface with message display and input
- `Sidebar.tsx` - Chat list with new chat and delete functionality
- `ObservabilityDashboard.tsx` - System monitoring dashboard
- `DocumentManager.tsx` - Document upload and management
- `MCPManager.tsx` - MCP integration management
- `ToastContainer.tsx` - Toast notification system

**Custom Hooks:**
- `useKeyboardShortcuts` - Keyboard shortcut management
- `useAccessibility` - Accessibility features (screen reader, focus management)
- `useWebSocket` - WebSocket connection management (for future real-time features)
- `useRetry` - Retry logic with exponential backoff

#### 1.2.2 Backend (FastAPI + Python)

**Technology Stack:**
- **Framework:** FastAPI 0.104.1
- **Python Version:** 3.12
- **Async Runtime:** asyncio
- **Database:** PostgreSQL 15 with asyncpg
- **Cache:** Redis 7.2
- **Vector DB:** Qdrant 1.12.0
- **LLM:** Transformers 4.36.0 (GPT-2, sentence-transformers)

**Key Modules:**
- `app/main.py` - Application entry point and startup
- `app/api/main.py` - Main API router with chat and assistant endpoints
- `app/api/documents.py` - Document management API
- `app/api/mcp.py` - MCP integration API
- `app/api/observability.py` - Observability and monitoring API
- `app/api/screenshot.py` - Screenshot capture API
- `app/api/terminal.py` - Terminal command API
- `app/agents/` - Multi-agent system implementation
- `app/services/` - Business logic services
- `app/core/` - Core configuration and utilities
- `app/models/` - Database models

#### 1.2.3 Multi-Agent System

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

**Agent Orchestration Flow:**
1. User message received via `/api/v1/assistant`
2. Supervisor agent classifies intent using keyword matching
3. Supervisor selects appropriate sub-agents based on intent
4. Selected agents execute with individual logging and tracing
5. Results merged and final response generated
6. Complete execution logged to observability system

### 1.3 Data Flow Architecture

#### 1.3.1 Chat Flow

```
User Input (React UI)
    ↓
POST /api/v1/assistant
    ↓
Supervisor Agent (Intent Classification)
    ↓
Agent Selection (Keyword-based)
    ↓
Sub-Agent Execution (with logging)
    ↓
Result Merging
    ↓
Response Generation (GPT-2)
    ↓
Store in PostgreSQL (chats, messages)
    ↓
Store in Redis (runtime state)
    ↓
Return to Frontend
    ↓
Display in UI
```

#### 1.3.2 Document Upload Flow

```
User Uploads Document (React UI)
    ↓
POST /api/v1/documents
    ↓
Store in PostgreSQL (documents table)
    ↓
Generate Embeddings (sentence-transformers)
    ↓
Chunk Document (intelligent segmentation)
    ↓
Store in Qdrant (384-dimensional vectors)
    ↓
Update Document Status (embedding_status, chunk_count)
    ↓
Return to Frontend
    ↓
Display in Document Manager
```

#### 1.3.3 Observability Flow

```
Agent Execution
    ↓
Log to PostgreSQL (observability_logs table)
    ↓
Record Trace (observability_traces table)
    ↓
Record Metric (observability_metrics table)
    ↓
Frontend Polls /api/v1/observability/*
    ↓
Display in Observability Dashboard
    ↓
User can purge old data (DELETE endpoints)
```

### 1.4 Storage Architecture

#### 1.4.1 PostgreSQL Schema

**Business Data Tables:**
- `users` - User accounts and authentication
- `chats` - Chat sessions with context and metadata
- `messages` - Chat messages with role and content
- `mcp_integrations` - MCP server configurations

**Observability Tables:**
- `observability_logs` - System logs with levels and context
- `observability_traces` - Request traces with timing and hierarchy
- `observability_metrics` - Performance metrics and counters

**Memory Tables:**
- `memories` - Long-term memory embeddings
- `agent_executions` - Agent execution history

#### 1.4.2 Redis Data Structure

**Key Categories:**
- `conversation:{chat_id}` - Chat conversation history
- `agent_state:{chat_id}` - Agent runtime state
- `response:{hash}` - Response cache (1h TTL)
- `tool:{hash}` - Tool execution cache
- `screenshot:{hash}` - Screenshot cache (24h TTL)
- `workflow:{id}` - Long-running workflow progress
- `memory_queue` - Pending memory extraction tasks

**Configuration:**
- Max memory: 2GB
- Eviction policy: allkeys-lru
- Persistence: Disabled (runtime state only)

#### 1.4.3 Qdrant Collections

**Collections:**
- `documents` - Document embeddings for RAG
  - Vector size: 384 dimensions
  - Distance metric: Cosine similarity
  - Payload: document_id, title, content, chunk_index

- `ai_assistant_memory` - Long-term memory embeddings
  - Vector size: 384 dimensions
  - Distance metric: Cosine similarity
  - Payload: memory_type, content, timestamp

### 1.5 Security Architecture

#### 1.5.1 Configuration Validation

**Startup Validation:**
- Required environment variables checked
- Secret key validation (must not be default)
- Database connection validation
- Redis connection validation
- Qdrant connection validation
- Health check endpoint: `/health`

#### 1.5.2 Security Measures

- **Local-First:** All data stored locally, no external API calls
- **Input Validation:** All API inputs validated
- **Secret Management:** Secure secret key generation
- **Access Control:** File system and command execution permissions
- **Error Handling:** No sensitive data in error messages
- **CORS:** Configured for local development only

---

## 2. Technology Stack Details

### 2.1 Backend Dependencies

**Core Framework:**
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `pydantic-settings==2.1.0` - Configuration management

**Database:**
- `sqlalchemy==2.0.23` - ORM
- `asyncpg==0.29.0` - PostgreSQL async driver
- `alembic==1.13.0` - Database migrations

**Cache:**
- `redis==5.0.1` - Redis client
- `hiredis==2.2.3` - Redis C parser

**Vector Database:**
- `qdrant-client==1.12.0` - Qdrant client
- `qdrant-server==1.12.0` - Vector database

**AI/ML:**
- `transformers==4.36.0` - Hugging Face transformers
- `torch==2.1.0` - PyTorch
- `sentence-transformers==2.2.2` - Sentence embeddings
- `accelerate==0.25.0` - Model acceleration

**Utilities:**
- `psutil==5.9.6` - System monitoring
- `python-dotenv==1.0.0` - Environment variables
- `python-multipart==0.0.6` - File uploads
- `aiofiles==23.2.1` - Async file operations

### 2.2 Frontend Dependencies

**Core:**
- `react==18.2.0` - UI framework
- `react-dom==18.2.0` - React DOM
- `typescript==5.3.3` - TypeScript
- `vite==5.4.21` - Build tool

**Styling:**
- `tailwindcss==3.4.0` - CSS framework
- `autoprefixer==10.4.16` - PostCSS plugin
- `postcss==8.4.32` - CSS processor

**Icons:**
- `lucide-react==0.303.0` - Icon library

**Type Definitions:**
- `@types/react==18.2.45` - React types
- `@types/react-dom==18.2.18` - React DOM types

---

## 3. Environment Configuration

### 3.1 Backend Environment Variables

**Database:**
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cortexdesk
```

**Redis:**
```bash
REDIS_URL=redis://localhost:6379/0
```

**Qdrant:**
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

**LLM Configuration:**
```bash
LLM_PROVIDER=local
LLM_MODEL=gpt2
LLM_API_KEY=
LLM_API_ENDPOINT=
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

**Embedding Configuration:**
```bash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu
```

**Application:**
```bash
SECRET_KEY=<random-generated-key>
DEBUG=False
AGENT_TIMEOUT=30
```

### 3.2 Frontend Configuration

**Vite Config:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

---

## 4. Deployment Architecture

### 4.1 Development Deployment

**Local Development:**
- Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Frontend: `npm run dev` (Vite dev server on port 5173)
- PostgreSQL: Local instance or Docker
- Redis: Local instance or Docker
- Qdrant: Local instance or Docker

### 4.2 Production Deployment (Future)

**Recommended Architecture:**
- Backend: Gunicorn with Uvicorn workers
- Frontend: Static files served by Nginx
- Database: Managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Cache: Managed Redis (ElastiCache, Memorystore)
- Vector DB: Managed Qdrant Cloud
- LLM: Cloud provider (Groq, RunPod, OpenAI)

---

## 5. Performance Considerations

### 5.1 Backend Performance

**Async Operations:**
- All database operations use async/await
- All external API calls are non-blocking
- Connection pooling for PostgreSQL and Redis

**Caching Strategy:**
- Response caching in Redis (1h TTL)
- Tool execution caching
- Screenshot caching (24h TTL)
- Agent state caching

**Embedding Generation:**
- Local model (no network latency)
- CPU-based (no GPU required)
- Batch processing for multiple documents

### 5.2 Frontend Performance

**Optimizations:**
- Code splitting with React.lazy
- Lazy loading of components
- Skeleton loaders for perceived performance
- Debounced search inputs
- Optimized re-renders with proper dependencies

**Bundle Size:**
- Vite production build optimization
- Tree shaking for unused code
- Minification and compression

---

## 6. Monitoring & Observability

### 6.1 Metrics Collected

**System Metrics:**
- CPU usage percentage
- Memory usage (available, used, total)
- Disk usage (free, used, total)

**Agent Metrics:**
- Agent execution count (success/error)
- Agent execution time
- Agent selection frequency

**Application Metrics:**
- Request count
- Response time
- Error rate

### 6.2 Logging Strategy

**Log Levels:**
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures and exceptions
- DEBUG: Detailed debugging information

**Log Retention:**
- Default: 30 days
- Configurable via purge API
- Manual purge available via UI

### 6.3 Tracing Strategy

**Trace Structure:**
- Trace ID: Correlates all spans in a request
- Span ID: Unique identifier for each operation
- Parent Span ID: Shows hierarchy
- Operation Name: What was executed
- Service Name: Which agent/service
- Duration: Execution time in milliseconds
- Status: Success/error/running
- Metadata: Additional context

**Trace Retention:**
- Default: 30 days
- Configurable via purge API
- Manual purge available via UI

---

## 7. Error Handling Strategy

### 7.1 Backend Error Handling

**Exception Types:**
- HTTPException: API errors with status codes
- ValidationError: Input validation errors
- DatabaseError: Database operation errors
- ConnectionError: External service connection errors

**Error Response Format:**
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 7.2 Frontend Error Handling

**Error Boundaries:**
- React Error Boundary for component errors
- Global error handler for unhandled errors
- User-friendly error messages via toast notifications

**Retry Logic:**
- Exponential backoff for failed requests
- Configurable retry attempts (default: 3)
- User feedback during retry operations

---

## 8. Accessibility Features

### 8.1 Keyboard Navigation

**Keyboard Shortcuts:**
- Ctrl+N: New chat
- Ctrl+D: Toggle documents
- Ctrl+O: Toggle observability
- Ctrl+M: Toggle MCP manager
- ?: Show about
- Escape: Close modals

### 8.2 Screen Reader Support

**ARIA Labels:**
- All interactive elements have aria-labels
- Modals have aria-modal and aria-labelledby
- Status updates use aria-live regions

**Focus Management:**
- Focus trapping in modals
- Visible focus indicators
- Logical tab order

### 8.3 Visual Accessibility

**High Contrast Mode:**
- Respects prefers-contrast media query
- Enhanced borders for better visibility

**Reduced Motion:**
- Respects prefers-reduced-motion media query
- Disabled animations for sensitive users

---

## 9. Multi-Agent Implementation Details

### 9.1 Supervisor Agent

**Responsibilities:**
- Intent classification using keyword matching
- Agent selection based on intent
- Execution plan generation
- Sub-agent orchestration
- Result merging
- Final response generation

**Agent Selection Logic:**
```python
keywords = {
    "code": ["code", "repository", "git", "function", "class", "bug", "debug"],
    "knowledge": ["document", "pdf", "search", "find", "what is", "explain", "python"],
    "windows": ["open", "launch", "screenshot", "clipboard", "file", "folder"],
    "system": ["docker", "podman", "wsl", "process", "service", "system"],
    "productivity": ["calendar", "meeting", "task", "email", "journal"]
}
```

### 9.2 Sub-Agent Implementation

**Base Agent:**
- Abstract base class for all agents
- Common logging and tracing
- LLM calling interface
- Memory retrieval interface

**Agent Execution Flow:**
1. Agent receives input from supervisor
2. Agent logs start of execution
3. Agent records trace start
4. Agent processes input
5. Agent logs completion
6. Agent records trace completion
7. Agent returns result to supervisor

---

## 10. Data Management Strategy

### 10.1 Document Management

**Upload Process:**
1. User uploads document via UI
2. Document stored in PostgreSQL
3. Document chunked into segments
4. Each chunk embedded using sentence-transformers
5. Embeddings stored in Qdrant
6. Document status updated to "completed"

**Deletion Process:**
1. User deletes document via UI
2. Embeddings deleted from Qdrant (using MD5 hash of IDs)
3. Document deleted from PostgreSQL
4. Status updated to "deleted"

### 10.2 Observability Data Management

**Purge Strategy:**
- Logs: Purge after 7-30 days
- Traces: Purge after 30-90 days
- Metrics: Purge after 1-7 days
- Manual purge available via UI
- Configurable purge days (1-365)

**Purge API:**
```bash
DELETE /api/v1/observability/logs?before_days=7
DELETE /api/v1/observability/traces?before_days=30
DELETE /api/v1/observability/metrics?before_days=1
```

---

## 11. MCP Integration Architecture

### 11.1 MCP Integration Management

**Database Model:**
- `mcp_integrations` table stores MCP server configurations
- Fields: name, type, config, status, enabled, last_connected, last_error

**Available MCP Types:**
- Filesystem (local file operations)
- GitHub (repository access)
- Git (version control)
- PostgreSQL (database access)

**MCP Operations:**
- Create integration with type-specific configuration
- Read integration details
- Update integration configuration
- Delete integration
- Test connection to integration

### 11.2 MCP Status Monitoring

**Status Indicators:**
- Connected: Green checkmark
- Error: Red X with error details
- Connecting: Yellow spinning refresh
- Unknown: Gray refresh

**Health Monitoring:**
- Connection testing with loading states
- Last connection timestamp
- Error message display
- Status badge with color coding

---

## 12. UX Improvements Summary

### 12.1 Implemented UX Features

**Notifications:**
- Toast notification system (success, error, warning, info)
- Auto-dismissal with configurable duration
- Visual feedback for all operations

**Loading States:**
- Skeleton loaders for document list and sidebar
- Progress indicators for file uploads
- Spinners for API calls
- Loading overlays for modals

**Error Handling:**
- User-friendly error messages
- Retry buttons for failed operations
- Clear error descriptions
- Suggested solutions

**Keyboard Shortcuts:**
- Ctrl+N: New chat
- Ctrl+D: Toggle documents
- Ctrl+O: Toggle observability
- Ctrl+M: Toggle MCP manager
- ?: Show about

**Accessibility:**
- Screen reader support with ARIA labels
- Skip-to-content link
- Focus management
- High contrast mode
- Reduced motion support

**Real-Time Updates:**
- Auto-refresh with configurable intervals (5s, 10s, 30s, 1m)
- Manual refresh button
- Last updated timestamp
- Toast notifications for refresh status

**Data Filtering:**
- Logs filtering by message and level
- Traces filtering by operation, service, and trace ID
- Real-time filter updates
- Clear filter buttons

**Document Management:**
- Drag-and-drop file upload
- Upload progress indicator
- Toast notifications for upload/search/delete
- File reading and content extraction

**Chat Interface:**
- Typing indicators
- Better error handling
- Improved loading states

**Observability Dashboard:**
- Real-time data refresh
- Filtering and search
- Export functionality
- Data purge management
- Qdrant vector database view

**MCP Integration:**
- Status indicators with color coding
- Connection testing with loading states
- Health monitoring
- Integration templates

---

## 13. Future Enhancements

### 13.1 Planned Features

**WebSocket Support:**
- Real-time chat updates
- Live document processing status
- Real-time MCP connection status
- Live observability data

**Advanced RAG:**
- Hybrid search (keyword + semantic)
- Re-ranking of results
- Citation generation
- Multi-document synthesis

**Enhanced Observability:**
- Distributed tracing across services
- Performance profiling
- Alert thresholds
- Custom dashboards

**Additional MCP Integrations:**
- Slack integration
- Jira integration
- Confluence integration
- Email integration

---

## 14. Troubleshooting Guide

### 14.1 Common Issues

**Frontend Not Loading:**
- Check Vite dev server is running
- Check proxy configuration in vite.config.ts
- Check browser console for errors
- Verify backend is accessible

**No Logs in Observability:**
- Use `/api/v1/assistant` endpoint (not direct message creation)
- Check agent execution is working
- Verify observability_db is functioning
- Check database connection

**Qdrant Deletion Not Working:**
- Check ID conversion logic (string to MD5 hash)
- Verify Qdrant client version (should be 1.12.0)
- Check document has embeddings before deletion
- Verify HTTP API fallback is working

**MCP Tab Not Working:**
- Check secret key validation
- Verify MCP API responses are serializable
- Check MCP database model exists
- Verify MCP endpoints are registered

---

## 15. API Rate Limiting

### 15.1 Current Implementation

**No Rate Limiting:**
- Currently no rate limiting implemented
- All endpoints are unlimited
- Suitable for local development

### 15.2 Future Rate Limiting

**Planned Implementation:**
- Token bucket algorithm
- Per-endpoint limits
- Per-user limits
- Configurable via environment variables

---

## 16. Backup Strategy

### 16.1 Current Backup

**No Automated Backup:**
- No automated backup implemented
- Manual backup required
- Suitable for local development

### 16.2 Future Backup Strategy

**Planned Implementation:**
- PostgreSQL automated backups
- Redis persistence
- Qdrant collection snapshots
- Configurable backup schedules

---

## 17. Scaling Considerations

### 17.1 Current Scalability

**Single Instance:**
- Designed for single-user local deployment
- No horizontal scaling
- Limited by local resources

### 17.2 Future Scaling

**Planned Enhancements:**
- Multi-user support
- Horizontal scaling with load balancer
- Database sharding
- Redis clustering
- Qdrant distributed deployment

---

## 18. Version Control Strategy

### 18.1 Git Workflow

**Branching Strategy:**
- Main branch for production
- Feature branches for new features
- Commit messages follow conventional commits
- Pull requests for code review

### 18.2 Release Strategy

**Versioning:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog maintained
- Tagged releases

---

## 19. Testing Strategy

### 19.1 Current Testing

**No Automated Tests:**
- No unit tests implemented
- No integration tests implemented
- Manual testing only

### 19.2 Future Testing

**Planned Testing:**
- Unit tests for core services
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance tests for scaling

---

## 20. Documentation Strategy

### 20.1 Current Documentation

**Available Documentation:**
- README.md - Project overview and quick start
- QUICKSTART.md - Quick start guide
- SETUP.md - Detailed setup instructions
- USER_GUIDE.md - User guide
- docs/ARCHITECTURE.md - System architecture
- docs/API_REFERENCE.md - API documentation
- docs/LLD_PART*.md - Low-level design (this document)

### 20.2 Documentation Maintenance

**Update Strategy:**
- Documentation updated with each major feature
- API documentation generated from code
- Architecture diagrams kept in sync
- LLD updated for significant changes

---

**End of Part 1: Architecture & System Design**

Continue to Part 2: Data Models & Database Schema
