# CortexDesk Desktop App

## Overview

CortexDesk desktop app is a Tauri-based desktop application that provides a native desktop experience for the CortexDesk web application. The desktop app requires the backend to be running separately (either via Docker or manual setup).

## Architecture

### Web App (Unchanged)
- Backend runs directly on host machine
- PostgreSQL, Redis, Qdrant run directly on host
- Frontend connects via http://localhost:8000
- **No changes to existing setup**

### Desktop App (New)
- Frontend runs in Tauri desktop window
- Backend must be running separately (Docker or manual)
- Desktop app connects to backend at http://localhost:8000
- **Same code, just packaged as desktop app**

## Desktop App Features

### Current Implementation
- **Native Desktop Window** - Tauri-based desktop application
- **Cross-Platform** - Builds for Windows, macOS, and Linux
- **Same UI as Web App** - Identical functionality and features
- **No Backend Management** - Backend must be started separately

### What the Desktop App Does NOT Include
- ❌ Backend (Python/FastAPI)
- ❌ PostgreSQL database
- ❌ Redis cache
- ❌ Qdrant vector database
- ❌ Docker management UI
- ❌ One-click service start
- ❌ Automatic backend startup

## Installation

### Prerequisites

**Required:**
- Backend running at http://localhost:8000
- Either Docker Desktop (for Docker setup) or manual database installation

**For Docker Setup:**
- Docker Desktop installed
- Clone the repository

**For Manual Setup:**
- PostgreSQL 15+ installed
- Redis 7+ installed
- Qdrant 1.12+ installed
- Python 3.10+ installed

### Installation Steps

#### Option 1: Docker Setup (Recommended)

**1. Install Docker Desktop**
```cmd
Download from: https://www.docker.com/products/docker-desktop
Install and start Docker Desktop
```

**2. Clone Repository**
```bash
git clone https://github.com/dipanwitasarkar/CortexDesk.git
cd CortexDesk
```

**3. Start Backend Services**
```bash
docker-compose up -d
```

**4. Download Desktop App**
- Download from GitHub Actions artifacts
- Or build manually: `cd frontend && npm run tauri:build`

**5. Install Desktop App**
- Windows: Run the .msi or .exe installer
- macOS: Open the .dmg file
- Linux: Install the .deb or run the .AppImage

**6. Launch Desktop App**
- Launch from Start Menu or Applications
- Desktop app will connect to backend at http://localhost:8000

#### Option 2: Manual Backend Setup

**1. Install Databases**
- Install PostgreSQL 15+
- Install Redis 7+
- Install Qdrant 1.12+

**2. Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**3. Download and Install Desktop App**
- Download from GitHub Actions artifacts
- Install the desktop app

**4. Launch Desktop App**
- Launch from Start Menu or Applications
- Desktop app will connect to backend at http://localhost:8000

## Docker Configuration

### docker-compose.yml
```yaml
services:
  postgres:    # PostgreSQL database
  redis:       # Redis cache
  qdrant:      # Vector database
  backend:     # FastAPI backend
```

### Backend Dockerfile
- Python 3.11 base image
- All dependencies installed
- Backend runs on port 8000

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

### GitHub Actions
- Automated builds on push to main
- Download artifacts from Actions page
- Create tags for GitHub Releases

## Troubleshooting

### Desktop App Won't Connect to Backend

**Error:** Backend connection failed
**Solution:**
- Ensure backend is running at http://localhost:8000
- Check backend logs: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Check if port 8000 is blocked by firewall
- Verify backend health: `curl http://localhost:8000/health`

### Docker Services Won't Start

**Error:** Docker containers not starting
**Solution:**
- Ensure Docker Desktop is running
- Check Docker Desktop settings
- Try restarting Docker Desktop
- Check for port conflicts (5432, 6379, 6333, 8000)

### Manual Database Setup Issues

**Error:** Database connection failed
**Solution:**
- Verify PostgreSQL is running
- Check database credentials in .env file
- Ensure database exists: `createdb cortexdesk`
- Check PostgreSQL logs

## Current Limitations

**Desktop App:**
- ❌ No automatic backend startup
- ❌ No Docker management UI
- ❌ No one-click service start
- ❌ Backend must be started manually

**Future Enhancements:**
- ✅ Bundle backend in desktop app (estimated 1-2 months work)
- ✅ Use embedded databases (SQLite instead of PostgreSQL)
- ✅ Auto-start backend on app launch
- ✅ Service management UI

## Summary

**Current State:**
- Desktop app is a frontend wrapper only
- Backend must be started separately (Docker or manual)
- Docker configuration provided for easy backend setup
- Cross-platform builds available via GitHub Actions

**User Experience:**
1. Install Docker Desktop (one-time)
2. Clone repository
3. Start Docker services
4. Install desktop app
5. Launch desktop app
6. Ready to use

**Web App vs Desktop App:**
- **Web App:** Backend runs on host, browser UI
- **Desktop App:** Backend runs on host, native desktop UI
- **Same functionality, different UI delivery**