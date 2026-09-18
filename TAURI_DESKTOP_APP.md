# CortexDesk Desktop App - Tauri Setup Guide

## Overview

CortexDesk can be packaged as a cross-platform desktop application using Tauri. This allows the web application to run as a native desktop app on Windows, macOS, and Linux.

## Current Status

✅ **Completed:**
- Tauri CLI installed
- Tauri project initialized
- Configuration updated for CortexDesk
- Window settings configured (1200x800, resizable)
- Tauri API package installed
- Rust toolchain installed
- All system dependencies installed
- Tauri app successfully builds and runs

✅ **Working:**
- Development mode: `npm run tauri:dev`
- Desktop app launches successfully
- Cross-platform compatibility configured

## Current Implementation

### What the Desktop App Includes
- ✅ Frontend (React app)
- ✅ Tauri desktop wrapper
- ✅ Native desktop window
- ✅ Cross-platform builds (Windows, macOS, Linux)

### What the Desktop App Does NOT Include
- ❌ Backend (Python/FastAPI)
- ❌ PostgreSQL database
- ❌ Redis cache
- ❌ Qdrant vector database
- ❌ Docker management UI
- ❌ Automatic backend startup

### How It Works
The desktop app is a **frontend-only wrapper** that connects to a backend running at `http://localhost:8000`. The backend must be started separately (either via Docker or manual setup).

## Development Setup

### 1. Install System Dependencies

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.0-dev \
  libwebkit2gtk-4.1-dev \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libsoup-3.0-dev \
  libjavascriptcoregtk-4.0-dev \
  libjavascriptcoregtk-4.1-dev
```

**macOS:**
```bash
brew install openssl@3
```

**Windows:**
- Visual Studio C++ Build Tools
- WebView2 Runtime (included with Windows 10+)

### 2. Install Rust Toolchain

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### 3. Install Tauri CLI

```bash
cd frontend
npm install -D @tauri-apps/cli @tauri-apps/api
```

### 4. Run Development Mode

**Linux (with display):**
```bash
cd frontend
npm run tauri:dev
```

**Linux (headless/remote):**
```bash
# Start virtual display
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Run Tauri
cd frontend
npm run tauri:dev
```

**Linux (VNC Access for Remote SSH):**
```bash
# 1. Set up VNC server
sudo apt-get install -y tightvncserver xfce4 xfce4-goodies
vncserver :1 -geometry 1920x1080 -depth 24

# 2. Set VNC password (you'll be prompted)

# 3. Start websockify for browser access
sudo apt-get install -y websockify novnc
websockify --web=/usr/share/novnc 6080 localhost:5901 &

# 4. Access from browser
# Navigate to: http://<vm-ip>:6080/vnc.html
# Enter VNC password

# 5. Run Tauri in VNC session
cd frontend
export DISPLAY=:1
npm run tauri:dev
```

This will:
- Start the Vite dev server (http://localhost:5173)
- Build the Tauri desktop app
- Launch the desktop application window

### 5. Build for Production

```bash
cd frontend
npm run tauri:build
```

This will create platform-specific installers in `src-tauri/target/release/bundle/`:

**Linux:** `.deb`, `.AppImage`
**macOS:** `.dmg`, `.app`
**Windows:** `.msi`, `.exe`

## Configuration

### tauri.conf.json
```json
{
  "productName": "CortexDesk",
  "version": "1.0.0",
  "identifier": "com.cortezdesk",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://172.40.238.188:5173",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  },
  "app": {
    "windows": [
      {
        "title": "CortexDesk - AI Assistant",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false,
        "center": true
      }
    ]
  }
}
```

### API Configuration

The desktop app uses a centralized API configuration file (`frontend/src/config.ts`):

```typescript
// API Configuration
export const API_BASE_URL = 'http://172.40.238.188:8000';
```

**For local development:** Change to `http://localhost:8000`
**For VNC access:** Use the network IP address
**For production:** Update to your backend URL

All frontend components use this centralized configuration instead of hardcoded URLs.

## Backend Setup (Required)

The desktop app requires the backend to be running. You have two options:

### Option A: Docker (Recommended)

```bash
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Clone repository
git clone https://github.com/dipanwitasarkar/CortexDesk.git
cd CortexDesk

# 3. Start backend services
docker-compose up -d

# 4. Verify services are running
docker-compose ps
```

### Option B: Manual Setup

```bash
# 1. Install PostgreSQL, Redis, Qdrant manually

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database credentials
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Building for Different Platforms

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

## GitHub Actions

Automated cross-platform builds are configured in `.github/workflows/build-desktop.yml`:

- Triggers on push to main
- Builds for Windows, macOS, and Linux
- Uploads artifacts to Actions page
- Creates GitHub Releases on tags

## Troubleshooting

### GTK Initialization Failed

**Error:** `Failed to initialize GTK`
**Solution:** Tauri requires a display server. On headless/remote systems, use Xvfb:

```bash
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
npm run tauri:dev
```

### Build Fails with Missing Libraries

**Error:** Package not found
**Solution:** Install system dependencies (see above)

### Backend Connection Failed

**Error:** Desktop app can't connect to backend
**Solution:**
- Ensure backend is running at http://localhost:8000
- Check backend health: `curl http://localhost:8000/health`
- Verify backend is accessible

## Current Limitations

**Desktop App:**
- ❌ No automatic backend startup
- ❌ Backend must be started manually
- ❌ No embedded databases
- ❌ No service management UI

**Future Enhancements:**
- ✅ Bundle backend in desktop app (estimated 1-2 months work)
- ✅ Use embedded databases (SQLite instead of PostgreSQL)
- ✅ Auto-start backend on app launch
- ✅ Service management UI

## Summary

**Current State:**
- Desktop app is a frontend wrapper only
- Backend must be started separately (Docker or manual)
- Cross-platform builds available
- GitHub Actions for automated builds

**User Experience:**
1. Install Docker Desktop (one-time)
2. Clone repository
3. Start Docker services
4. Install desktop app
5. Launch desktop app
6. Ready to use

**Platform Agnostic:**
- ✅ Works on Linux
- ✅ Works on macOS
- ✅ Works on Windows
- ✅ Same codebase for all platforms
