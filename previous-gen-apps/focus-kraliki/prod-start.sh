#!/usr/bin/env bash
#
# Focus by Kraliki - Production Starter Script
# Starts backend (port 8000) and frontend (port 4173) in production mode
# Includes automatic port clearing and process management
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=4173

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Focus by Kraliki - Production Starter${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to kill process on port
kill_port() {
    local port=$1
    local process=$(lsof -ti:$port 2>/dev/null)

    if [ ! -z "$process" ]; then
        echo -e "${YELLOW}⚠ Port $port is in use by PID $process${NC}"
        echo -e "${YELLOW}  Killing process...${NC}"
        kill -9 $process 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✓ Port $port cleared${NC}"
    else
        echo -e "${GREEN}✓ Port $port is available${NC}"
    fi
}

# Function to check if directory exists
check_dir() {
    local dir=$1
    local name=$2

    if [ ! -d "$dir" ]; then
        echo -e "${RED}✗ $name directory not found: $dir${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Found $name directory${NC}"
}

# Clear ports
echo -e "${BLUE}[1/5] Clearing ports...${NC}"
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT
echo ""

# Check directories
echo -e "${BLUE}[2/5] Checking directories...${NC}"
check_dir "$BACKEND_DIR" "Backend"
check_dir "$FRONTEND_DIR" "Frontend"
echo ""

# Build frontend
echo -e "${BLUE}[3/5] Building frontend...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ node_modules not found, running pnpm install...${NC}"
    pnpm install
fi

echo -e "${YELLOW}  Building production bundle...${NC}"
pnpm build

if [ ! -d "build" ]; then
    echo -e "${RED}✗ Frontend build failed - build directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Start backend
echo -e "${BLUE}[4/5] Starting backend server (production)...${NC}"
echo -e "  Port: ${GREEN}$BACKEND_PORT${NC}"
echo -e "  Directory: $BACKEND_DIR"
echo -e "  URL: ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo ""

cd "$BACKEND_DIR"

# Start backend with production settings
nohup uv run uvicorn app.main:app \
    --host 127.0.0.1 \
    --port $BACKEND_PORT \
    --workers 4 \
    > "$PROJECT_ROOT/backend-prod.log" 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID, 4 workers)${NC}"
echo -e "  Logs: ${YELLOW}$PROJECT_ROOT/backend-prod.log${NC}"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}  Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start within 30 seconds${NC}"
        echo -e "${YELLOW}  Check logs: tail -f $PROJECT_ROOT/backend-prod.log${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend (production preview)
echo -e "${BLUE}[5/5] Starting frontend server (production)...${NC}"
echo -e "  Port: ${GREEN}$FRONTEND_PORT${NC}"
echo -e "  Directory: $FRONTEND_DIR"
echo -e "  URL: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo ""

cd "$FRONTEND_DIR"

# Start frontend preview server
nohup pnpm preview \
    --host 127.0.0.1 \
    --port $FRONTEND_PORT \
    > "$PROJECT_ROOT/frontend-prod.log" 2>&1 &

FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "  Logs: ${YELLOW}$PROJECT_ROOT/frontend-prod.log${NC}"
echo ""

# Wait for frontend to be ready
echo -e "${YELLOW}  Waiting for frontend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Frontend failed to start within 30 seconds${NC}"
        echo -e "${YELLOW}  Check logs: tail -f $PROJECT_ROOT/frontend-prod.log${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Success message
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✓ Production services started!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Services:${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}  (PID: $BACKEND_PID, 4 workers)"
echo -e "  Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC} (PID: $FRONTEND_PID, production build)"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  Backend:  ${YELLOW}tail -f $PROJECT_ROOT/backend-prod.log${NC}"
echo -e "  Frontend: ${YELLOW}tail -f $PROJECT_ROOT/frontend-prod.log${NC}"
echo ""
echo -e "${BLUE}Stop services:${NC}"
echo -e "  Kill all: ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "  Or use:   ${YELLOW}./prod-stop.sh${NC}"
echo ""

# Save PIDs to file
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend-prod.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend-prod.pid"

echo -e "${GREEN}✓ PIDs saved to .backend-prod.pid and .frontend-prod.pid${NC}"
echo ""
