#!/usr/bin/env bash
#
# Focus by Kraliki - Production Stop Script
# Stops backend and frontend production servers
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Stopping Production Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to kill process
kill_process() {
    local pid=$1
    local name=$2

    if [ -z "$pid" ]; then
        echo -e "${YELLOW}⚠ No PID found for $name${NC}"
        return
    fi

    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Stopping $name (PID: $pid)...${NC}"
        kill $pid 2>/dev/null || kill -9 $pid 2>/dev/null || true
        sleep 1
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${RED}✗ Failed to stop $name${NC}"
        else
            echo -e "${GREEN}✓ $name stopped${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ $name is not running (PID: $pid)${NC}"
    fi
}

# Read PIDs from files
if [ -f "$PROJECT_ROOT/.backend-prod.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend-prod.pid")
    kill_process "$BACKEND_PID" "Backend"
    rm -f "$PROJECT_ROOT/.backend-prod.pid"
fi

if [ -f "$PROJECT_ROOT/.frontend-prod.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend-prod.pid")
    kill_process "$FRONTEND_PID" "Frontend"
    rm -f "$PROJECT_ROOT/.frontend-prod.pid"
fi

# Kill any remaining processes on ports
echo ""
echo -e "${BLUE}Checking ports...${NC}"

# Backend port (8000)
BACKEND_PROC=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PROC" ]; then
    echo -e "${YELLOW}⚠ Found process on port 8000: $BACKEND_PROC${NC}"
    kill -9 $BACKEND_PROC 2>/dev/null || true
    echo -e "${GREEN}✓ Port 8000 cleared${NC}"
else
    echo -e "${GREEN}✓ Port 8000 is free${NC}"
fi

# Frontend port (4173)
FRONTEND_PROC=$(lsof -ti:4173 2>/dev/null)
if [ ! -z "$FRONTEND_PROC" ]; then
    echo -e "${YELLOW}⚠ Found process on port 4173: $FRONTEND_PROC${NC}"
    kill -9 $FRONTEND_PROC 2>/dev/null || true
    echo -e "${GREEN}✓ Port 4173 cleared${NC}"
else
    echo -e "${GREEN}✓ Port 4173 is free${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✓ All production services stopped${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
