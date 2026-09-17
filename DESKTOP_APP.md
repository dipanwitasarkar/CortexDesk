# CortexDesk Desktop App

## Overview

CortexDesk can be launched as a desktop application using the provided launcher scripts. This provides a native-like experience while maintaining the simplicity of the web application.

## Desktop Launcher

### Linux (desktop-app.sh)

```bash
./desktop-app.sh
```

**Features:**
- Checks if backend is running
- Checks if frontend is running (starts it if not)
- Launches in dedicated browser window
- Supports Chrome, Chromium, Firefox
- Auto-detects available browsers

### Windows (desktop-app.bat)

```cmd
desktop-app.bat
```

**Features:**
- Checks if backend is running
- Checks if frontend is running (starts it if not)
- Launches in Chrome app mode
- Windows batch script

### macOS

```bash
./desktop-app.sh
```

**Features:**
- Checks if backend is running
- Checks if frontend is running (starts it if not)
- Launches in Chrome app mode
- macOS shell script

## How It Works

1. **Health Checks:** The launcher verifies that both backend (port 8000) and frontend (port 5173) are running
2. **Auto-Start:** If services aren't running, it starts them automatically
3. **Browser Launch:** Opens the app in a dedicated browser window without address bar
4. **Native Feel:** Provides a desktop-like experience

## Advantages Over Full Desktop App

### ✅ Benefits:
- **No complex dependencies** - No Rust, no system libraries
- **Cross-platform** - Works on any OS with a browser
- **Small size** - Just a simple script
- **Easy to maintain** - No complex build process
- **Fast setup** - Works immediately
- **Automatic updates** - Web app updates automatically

### ⚠️ Limitations:
- Requires browser to be installed
- Not truly "native" (runs in browser)
- No system tray integration
- No native notifications
- No offline support

## Comparison: Launcher vs Full Desktop App

| Feature | Launcher Script | Tauri Desktop App |
|---------|----------------|-------------------|
| Setup Complexity | Very Low | High |
| System Dependencies | None | Many |
| Build Time | None | 5-10 min |
| Bundle Size | ~1KB | ~5-10MB |
| Cross-Platform | Yes | Yes (per-platform builds) |
| Native Integration | Limited | Full |
| System Tray | No | Yes |
| Notifications | Limited | Full |
| Offline Support | No | Yes |
| Auto-Updates | Yes | Manual |
| Maintenance | Minimal | Complex |

## Alternative: Full Desktop App

If you need a truly native desktop app with:
- System tray integration
- Native notifications
- Offline support
- File system integration
- Auto-updates

Then use **Tauri** (requires system dependencies) or **Electron** (larger size).

See `TAURI_DESKTOP_APP.md` for Tauri setup instructions.

## Usage

### Quick Start

1. **Start the launcher:**
   ```bash
   ./desktop-app.sh  # Linux/macOS
   desktop-app.bat  # Windows
   ```

2. **The launcher will:**
   - Check if backend is running (start if not)
   - Check if frontend is running (start if not)
   - Launch CortexDesk in browser app mode

3. **Close the browser window to exit**

### Manual Mode

If you prefer to start services manually:

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Open browser
# Open http://localhost:5173 in browser
```

## Troubleshooting

### Launcher Script Won't Execute

**Linux/macOS:**
```bash
chmod +x desktop-app.sh
```

**Windows:**
- Ensure you have execution permissions
- Run as Administrator if needed

### Browser Won't Open

**Solution:**
- Install Chrome, Chromium, or Firefox
- Or modify the script to use your preferred browser

### Services Won't Start

**Backend:**
```bash
cd backend
source venv/bin/  # Linux/macOS
venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Future Enhancements

If you need more desktop features, consider:

1. **Add System Tray:** Use Electron or Tauri
2. **Add Notifications:** Use Electron or Tauri
3. **Add Offline Support:** Use Service Workers
4. **Add Auto-Updates:** Use Electron or Tauri
5. **Add File System Integration:** Use Electron or Tauri

## Conclusion

The desktop launcher provides a simple, cross-platform way to launch CortexDesk as a desktop app without the complexity of full desktop app frameworks. For most use cases, this provides a good balance between native feel and simplicity.

For truly native features, consider Tauri or Electron when needed.