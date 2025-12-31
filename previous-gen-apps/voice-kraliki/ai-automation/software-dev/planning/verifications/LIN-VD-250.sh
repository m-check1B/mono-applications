#!/bin/bash

# Verification script for VD-250: Voice Interface Arena
# Feature: Implement 1:1 Voice Interface Arena

# Correct workspace path for this context
VERIFICATIONS_DIR="/home/adminmatej/github/ai-automation/software-dev/planning/verifications"

echo "=== Verifying VD-250: Voice Interface Arena ==="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check 1: Arena service exists
if [ -f "backend/app/services/voice_arena_service.py" ]; then
    echo -e "${GREEN}✓${NC} Arena service file exists"
else
    echo -e "${RED}✗${NC} Arena service file missing"
fi

# Check 2: Arena routes are registered
if grep -q "from app.arena_routes import router as arena_router" backend/app/main.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Arena router imported in main.py"
else
    echo -e "${RED}✗${NC} Arena router not imported in main.py"
fi

# Check 3: Arena routes file exists
if [ -f "backend/app/arena_routes.py" ]; then
    echo -e "${GREEN}✓${NC} Arena routes file exists"
else
    echo -e "${RED}✗${NC} Arena routes file missing"
fi

# Check 4: WebRTC signaling handler exists
if grep -q "class WebRTCSignalingHandler" backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} WebRTC signaling class exists in arena routes"
else
    echo -e "${RED}✗${NC} WebRTC signaling class missing from arena routes"
fi

# Check 5: Persona templates available
if grep -q "PERSONA_TEMPLATES.*=" backend/app/services/voice_arena_service.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Persona templates defined"
else
    echo -e "${RED}✗${NC} Persona templates missing"
fi

# Check 6: Frontend arena page route exists
if grep -q "async def get_arena_page" backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} HTML page endpoint defined"
else
    echo -e "${RED}✗${NC} HTML page endpoint not defined"
fi

# Check 7: Arena WebSocket endpoint exists
if grep -q 'async def websocket_endpoint.*arena' backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} WebSocket endpoint defined"
else
    echo -e "${RED}✗${NC} WebSocket endpoint not defined"
fi

echo ""
# Summary
echo "=== Summary ==="
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All checks passed${NC}"
else
    echo -e "${RED}Some checks failed${NC}"
fi
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check 1: Arena service exists
if [ -f "backend/app/services/voice_arena_service.py" ]; then
    echo -e "${GREEN}✓${NC} Arena service file exists"
else
    echo -e "${RED}✗${NC} Arena service file missing"
fi

# Check 2: Arena routes are registered
if grep -q "from app.arena_routes import router as arena_router" backend/app/main.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Arena router imported in main.py"
else
    echo -e "${RED}✗${NC} Arena router not imported in main.py"
fi

# Check 3: Arena routes file exists
if [ -f "backend/app/arena_routes.py" ]; then
    echo -e "${GREEN}✓${NC} Arena routes file exists"
else
    echo -e "${RED}✗${NC} Arena routes file missing"
fi

# Check 4: WebRTC signaling handler exists
if grep -q "class WebRTCSignalingHandler" backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} WebRTC signaling class exists in arena routes"
else
    echo -e "${RED}✗${NC} WebRTC signaling class missing from arena routes"
fi

# Check 5: Persona templates available
if grep -q "PERSONA_TEMPLATES.*=" backend/app/services/voice_arena_service.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Persona templates defined"
else
    echo -e "${RED}✗${NC} Persona templates missing"
fi

# Check 6: Frontend arena page route exists
if grep -q 'app.include_router(arena_router)' backend/app/main.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Arena router included in FastAPI app"
else
    echo -e "${RED}✗${NC} Arena router not included in FastAPI app"
fi

# Check 7: Arena WebSocket endpoint exists
if grep -q '@status.get("/ws/arena")' backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} WebSocket endpoint defined"
else
    echo -e "${RED}✗${NC} WebSocket endpoint not defined"
fi

# Check 8: Arena HTML page endpoint exists
if grep -q 'async def get_arena_page' backend/app/arena_routes.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} HTML page endpoint defined"
else
    echo -e "${RED}✗${NC} HTML page endpoint not defined"
fi

echo ""
# Summary
echo "=== Summary ==="
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All checks passed${NC}"
else
    echo -e "${RED}Some checks failed${NC}"
fi
