# CortexDesk Desktop App with Docker

## Overview

CortexDesk desktop app uses Docker to run all backend services (PostgreSQL, Redis, Qdrant, Backend) locally without requiring manual installation of databases. The web app continues to work exactly as before with no changes.

## Architecture

### Web App (Unchanged)
- Backend runs directly on host machine
- PostgreSQL, Redis, Qdrant run directly on host
- Frontend connects via http://localhost:8000
- **No changes to existing setup**

### Desktop App (New)
- Backend runs in Docker container
- PostgreSQL, Redis, Qdrant run in Docker containers
- Tauri desktop app connects to Docker backend
- **Same code, just packaged differently**

## Desktop App Features

### Docker Integration
- **Automatic Docker detection** - Checks if Docker is installed
- **One-click service start** - Starts all containers with single button
- **Service status monitoring** - Shows real-time status of all services
- **Graceful shutdown** - Stops all containers cleanly

### Services Managed
- **PostgreSQL** - Database (port 5432)
- **Redis** - Cache (port 6379)
- **Qdrant** - Vector database (port 6333)
- **Backend** - API server (port 8000)

### User Experience
1. Install Docker Desktop (one-time)
2. Download CortexDesk desktop app
3. Launch app
4. Click "Start Services" button
5. All backend services start automatically
6. Ready to use!

## Files Added

### Docker Configuration
- `docker-compose.yml` - Docker Compose configuration for all services
- `backend/Dockerfile` - Backend container definition

### Tauri Integration
- `frontend/src-tauri/src/lib.rs` - Docker management commands
- `frontend/src-tauri/capabilities/default.json` - Shell execution permissions
- `frontend/src/components/DockerManager.tsx` - Docker management UI

### Frontend Changes
- `frontend/src/App.tsx` - Docker Manager modal integration

## How It Works

### 1. Docker Compose Configuration
```yaml
services:
  postgres:    # PostgreSQL database
  redis:       # Redis cache
  qdrant:      # Vector database
  backend:     # FastAPI backend
```

### 2. Tauri Commands
- `check_docker()` - Check if Docker is installed
- `start_docker_containers()` - Start all containers
- `stop_docker_containers()` - Stop all containers
- `check_containers_status()` - Get container status

### 3. Docker Manager UI
- Shows Docker installation status
- Shows service status (running/stopped)
- Start/Stop buttons
- Real-time status updates
- Service health indicators

## Development

### Web App Development (Unchanged)
```bash
# Terminal 1: Start databases
# PostgreSQL, Redis, Qdrant running on host

# Terminal 2: Start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev

# Open browser: http://localhost:5173
```

### Desktop App Development
```bash
# Terminal 1: Start Docker services
docker-compose up -d

# Terminal 2: Start Tauri dev
cd frontend
npm run tauri:dev
```

## Building Desktop App

### Linux
```bash
cd frontend
npm run tauri:build
```

### Windows
```cmd
cd frontend
npm run tauri:build
```

### macOS
```bash
cd frontend
npm run tauri:build
```

## Customer Distribution

### What Customers Need
1. **Docker Desktop** - One-time installation (free)
2. **CortexDesk Desktop App** - Download and install

### Customer Setup
```cmd
1. Install Docker Desktop (one-time)
2. Download CortexDesk-Setup.exe
3. Double-click to install
4. Launch from Start Menu
5. Click "Start Services" in Docker Manager
6. Ready to use!
```

### What Happens Internally
1. Desktop app checks for Docker
2. Shows Docker Manager if Docker not detected
3. Customer installs Docker Desktop
4. Customer clicks "Start Services"
5. Docker Compose starts all containers
6. Backend becomes available
7. Desktop app connects to backend
8. Ready to use!

## Advantages

### For Developers
- ✅ Same codebase for web and desktop
- ✅ No code changes to backend
- ✅ Easy to test locally
- ✅ Consistent environment
- ✅ Easy to update

### For Customers
- ✅ Simple installation
- ✅ No database setup required
- ✅ Isolated environment
- ✅ Easy to uninstall
- ✅ Cross-platform

### Compared to Manual Setup
- ✅ No PostgreSQL installation
- ✅ No Redis installation
- ✅ No Qdrant installation
- ✅ No Python environment setup
- ✅ No dependency conflicts

## Troubleshooting

### Docker Not Detected
**Error:** "Docker Not Installed"
**Solution:** Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Containers Won't Start
**Error:** "Failed to start containers"
**Solution:** 
- Check Docker Desktop is running
- Check ports 5432, 6379, 6333, 8000 are not in use
- Check Docker has enough resources

### Backend Not Responding
**Error:** Backend containers running but API not accessible
**Solution:**
- Check backend container logs: `docker logs cortexdesk-backend`
- Check backend health: `curl http://localhost:8000/health`
- Restart containers: Click "Stop Services" then "Start Services"

### Port Conflicts
**Error:** Ports already in use
**Solution:**
- Stop other services using ports 5432, 6379, 6333, 8000
- Or modify docker-compose.yml to use different ports

## Data Persistence

### Volumes
Docker volumes persist data:
- `postgres_data` - Database data
- `qdrant_data` - Vector database data
- `backend_venv` - Python virtual environment

### Backup
```bash
# Backup volumes
docker run --rm -v cortexdesk_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
docker run --rm -v cortexdesk_qdrant_data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant-backup.tar.gz /data
```

### Restore
```bash
# Restore volumes
docker run --rm -v cortexdesk_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /
docker run --rm -v cortexdesk_qdrant_data:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant-backup.tar.gz -C /
```

## Security

### Network Isolation
- All services run in Docker network
- Only exposed ports: 5432, 6379, 6333, 8000
- No external network access by default

### Environment Variables
- Database credentials in docker-compose.yml
- For production, use Docker secrets or environment files

## Performance

### Resource Requirements
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** 5GB minimum (10GB recommended)
- **CPU:** 2 cores minimum

### Optimization
- Use Docker resource limits
- Optimize database configurations
- Use container restart policies

## Updates

### Updating Desktop App
1. Build new version: `npm run tauri:build`
2. Distribute new installer
3. Customer installs update
4. Old containers stopped, new started
5. Data preserved in volumes

### Updating Services
1. Update docker-compose.yml
2. Update backend Dockerfile
3. Rebuild: `docker-compose build`
4. Restart: `docker-compose up -d`

## Web App vs Desktop App

| Feature | Web App | Desktop App |
|---------|---------|-------------|
| **Backend** | Host machine | Docker container |
| **Databases** | Host machine | Docker containers |
| **Setup** | Manual | Docker + 1-click |
| **Portability** | Low | High |
| **Isolation** | None | Full |
| **Updates** | Manual | Easy |
| **Code** | Same | Same |

## Summary

The Docker desktop app approach provides:
- ✅ **No code changes** to existing web app
- ✅ **Simple customer setup** (Docker + 1-click)
- ✅ **Cross-platform** (Windows, macOS, Linux)
- ✅ **Isolated environment** (no conflicts)
- ✅ **Easy distribution** (single installer)
- ✅ **Easy updates** (automatic container management)

The web app continues to work exactly as before with zero changes.