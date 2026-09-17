#!/bin/bash

# CortexDesk Desktop App Launcher
# This script launches the web app in a dedicated browser window

# Configuration
APP_NAME="CortexDesk"
APP_URL="http://localhost:5173"
BACKEND_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   $APP_NAME Desktop App Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if backend is running
echo -e "${GREEN}Checking if backend is running...${NC}"
if curl -s "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo -e "${RED}Please start the backend first:${NC}"
    echo -e "${RED}  cd backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000${NC}"
    exit 1
fi

echo ""

# Check if frontend is running
echo -e "${GREEN}Checking if frontend is running...${NC}"
if curl -s "$APP_URL" > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo -e "${RED}Starting frontend...${NC}"
    cd frontend
    npm run dev > /dev/null 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo ""
    echo -e "${GREEN}Waiting for frontend to be ready...${NC}"
    sleep 5
fi

echo ""
echo -e "${GREEN}Launching $APP_NAME in browser...${NC}"

# Detect OS and launch appropriate browser
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v google-chrome &> /dev/null; then
        google-chrome --app="$APP_URL" --new-window
    elif command -v chromium-browser &> /dev/null; then
        chromium-browser --app="$APP_URL" --new-window
    elif command -v firefox &> /dev/null; then
        firefox --new-window "$APP_URL"
    else
        echo -e "${RED}No supported browser found${NC}"
        echo -e "${RED}Opening in default browser...${NC}"
        xdg-open "$APP_URL"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open -a "Google Chrome" --new --args --app="$APP_URL"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start chrome --app="$APP_URL"
else
    echo -e "${RED}Unknown OS: $OSTYPE${NC}"
    echo -e "${RED}Opening in default browser...${NC}"
    xdg-open "$APP_URL"
fi

echo ""
echo -e "${GREEN}✓ $APP_NAME launched!${NC}"
echo -e "${GREEN}Close the browser window to exit${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop this launcher${NC}"

# Wait for user to exit
wait