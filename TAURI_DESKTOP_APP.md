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

⚠️ **Requires System Dependencies:**
The Tauri build requires system-level libraries that need to be installed:

### Linux Dependencies
```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.0-dev \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libsoup-3.0-dev
```

### macOS Dependencies
```bash
brew install openssl@3
```

### Windows Dependencies
- Visual Studio C++ Build Tools
- WebView2 Runtime (usually included with Windows 10+)

## Development Setup

### 1. Install System Dependencies

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.0-dev \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libsoup-3.0-dev
```

**macOS:**
```bash
brew install openssl@3
```

**Windows:**
- Install Visual Studio C++ Build Tools
- WebView2 Runtime is included with Windows 10+

### 2. Install Rust Toolchain

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### 3. Install Tauri CLI

```bash
cd frontend
npm install -D @tauri-apps/cli
```

### 4. Run Development Mode

```bash
cd frontend
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

### Tauri Configuration (`src-tauri/tauri.conf.json`)

```json
{
  "productName": "CortexDesk",
  "version": "1.0.0",
  "identifier": "com.cortezdesk.app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173",
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
    ],
    "security": {
      "csp": null
    },
    "withGlobalTauri": true
  },
  "bundle": {
    "active": true,
    "targets": "all"
  }
}
```

## Platform-Specific Notes

### Linux
- Requires GTK3 and WebKitGTK libraries
- Produces `.deb` and `.AppImage` installers
- Supports system tray integration
- Requires additional system libraries for full functionality

### macOS
- Requires Xcode command line tools
- Produces `.dmg` and `.app` bundles
- Supports code signing (requires Apple Developer account)
- Native macOS look and feel

### Windows
- Requires Visual Studio C++ Build Tools
- Produces `.msi` and `.exe` installers
- WebView2 Runtime included with Windows 10+
- Native Windows integration (notifications, system tray)

## Cross-Platform Features

### ✅ What Works Cross-Platform:
- Core React application
- API communication with backend
- All UI components
- Keyboard shortcuts
- Accessibility features
- Local storage

### ⚠️ Platform-Specific Features:
- Windows Agent (Windows only)
- System tray integration (platform-specific)
- Native notifications (platform-specific)
- File system integration (platform-specific)

## Troubleshooting

### Build Fails with Missing Libraries

**Error:** `Package glib-2.0 was not found`
**Solution:** Install system dependencies (see above)

**Error:** `Package javascriptcoregtk-4.1 was not found`
**Solution:** Install libwebkit2gtk-4.0-dev

### Development Mode Won't Start

**Error:** Vite dev server not starting
**Solution:** Ensure backend is running on http://localhost:8000

**Error:** Desktop window doesn't open
**Solution:** Check Tauri logs in terminal for specific error

### Production Build Fails

**Error:** Build fails on specific platform
**Solution:** Ensure platform-specific dependencies are installed

## Current Limitations

1. **System Dependencies:** Tauri requires system-level libraries that vary by platform
2. **Build Time:** First build takes 5-10 minutes due to Rust compilation
3. **Bundle Size:** Desktop app is larger than web app (~5-10MB vs web)
4. **Platform Testing:** Need to test on each target platform

## Alternative Approaches

If Tauri setup is too complex, consider:

### Option 1: Electron
- Easier setup, more documentation
- Larger bundle size (~100MB+)
- Better ecosystem support

### Option 2: Keep as Web App
- No installation required
- Works in any browser
- Automatic updates
- Smaller footprint

### Option 3: Progressive Web App (PWA)
- Installable from browser
- Works offline
- Cross-platform
- Smaller than desktop app

## Next Steps

1. Install system dependencies for your platform
2. Test development mode: `npm run tauri:dev`
3. Test production build: `npm run tauri:build`
4. Test on target platforms
5. Configure code signing for distribution
6. Set up auto-update mechanism

## Resources

- [Tauri Documentation](https://tauri.app/)
- [Tauri CLI Reference](https://tauri.app/v1/guides/)
- [Cross-Platform Development](https://tauri.app/v1/guides/building/cross-platform)
- [System Requirements](https://tauri.app/v1/guides/getting-started/prerequisites)