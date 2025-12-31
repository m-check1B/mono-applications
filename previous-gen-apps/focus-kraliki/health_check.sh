#!/bin/bash

###############################################################################
# Service Health Check Script for Focus by Kraliki
# Checks all services and reports their status
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service ports
BACKEND_PORT=3017
II_AGENT_PORT=8765
FRONTEND_PORT=5173

# Health check results
ALL_HEALTHY=true

# Log functions
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║        Focus by Kraliki Service Health Check           ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
}

print_service() {
    local service=$1
    local status=$2
    local message=$3

    if [ "$status" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} $service: ${GREEN}HEALTHY${NC} - $message"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠${NC} $service: ${YELLOW}WARNING${NC} - $message"
    else
        echo -e "${RED}✗${NC} $service: ${RED}UNHEALTHY${NC} - $message"
        ALL_HEALTHY=false
    fi
}

print_separator() {
    echo ""
    echo "────────────────────────────────────────────────────"
    echo ""
}

###############################################################################
# Backend API Health Check
###############################################################################

check_backend() {
    echo "Checking Backend API (port $BACKEND_PORT)..."

    # Check if port is listening
    if ! timeout 2 bash -c "echo > /dev/tcp/localhost/$BACKEND_PORT" 2>/dev/null; then
        print_service "Backend API" "unhealthy" "Port $BACKEND_PORT is not listening"
        return 1
    fi

    # Check health endpoint
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/health" 2>/dev/null || echo "error\n000")
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
    RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$RESPONSE_BODY" | grep -q "healthy"; then
            print_service "Backend API" "healthy" "Responding on port $BACKEND_PORT"
        else
            print_service "Backend API" "warning" "Port open but health check returned unexpected response"
        fi
    else
        print_service "Backend API" "unhealthy" "Health endpoint returned HTTP $HTTP_CODE"
        return 1
    fi

    # Check root endpoint
    ROOT_RESPONSE=$(curl -s "http://localhost:$BACKEND_PORT/" 2>/dev/null || echo "error")
    if echo "$ROOT_RESPONSE" | grep -q "Focus by Kraliki API"; then
        echo -e "  ${BLUE}ℹ${NC} API version info retrieved successfully"
    else
        echo -e "  ${YELLOW}⚠${NC} Root endpoint returned unexpected response"
    fi
}

###############################################################################
# Database Connection Check
###############################################################################

check_database() {
    echo "Checking Database Connection..."

    # Try to check DB through backend API
    # If backend /health works, DB should be connected
    DB_CHECK=$(curl -s "http://localhost:$BACKEND_PORT/health" 2>/dev/null || echo "error")

    if echo "$DB_CHECK" | grep -q "healthy"; then
        print_service "Database" "healthy" "Connection verified via backend"

        # Additional check: try to access a protected endpoint (should get 401, not 500)
        AUTH_CHECK=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/knowledge/item-types" 2>/dev/null || echo "000")
        HTTP_CODE=$(echo "$AUTH_CHECK" | tail -1)

        if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
            echo -e "  ${BLUE}ℹ${NC} Database queries are working (auth check passed)"
        else
            echo -e "  ${YELLOW}⚠${NC} Database may have issues (unexpected HTTP code: $HTTP_CODE)"
        fi
    else
        print_service "Database" "unhealthy" "Cannot verify connection"
        return 1
    fi
}

###############################################################################
# II-Agent WebSocket Check
###############################################################################

check_ii_agent() {
    echo "Checking II-Agent WebSocket (port $II_AGENT_PORT)..."

    # Check if port is listening
    if timeout 2 bash -c "echo > /dev/tcp/localhost/$II_AGENT_PORT" 2>/dev/null; then
        print_service "II-Agent WebSocket" "healthy" "Listening on port $II_AGENT_PORT"

        # Try to check if it's actually a WebSocket server
        # Send a basic HTTP request and check for upgrade headers
        WS_CHECK=$(echo -e "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc -w 1 localhost $II_AGENT_PORT 2>/dev/null || echo "")

        if echo "$WS_CHECK" | grep -qi "upgrade"; then
            echo -e "  ${BLUE}ℹ${NC} WebSocket upgrade headers detected"
        fi
    else
        print_service "II-Agent WebSocket" "warning" "Not running or port $II_AGENT_PORT not accessible"
        echo -e "  ${YELLOW}⚠${NC} This is optional if II-Agent is not deployed"
    fi
}

###############################################################################
# Frontend Check
###############################################################################

check_frontend() {
    echo "Checking Frontend (port $FRONTEND_PORT)..."

    # Check if port is listening
    if curl -s -f "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        print_service "Frontend" "healthy" "Serving on port $FRONTEND_PORT"

        # Check if it's actually the Svelte app (look for common markers)
        FRONTEND_HTML=$(curl -s "http://localhost:$FRONTEND_PORT" 2>/dev/null || echo "")
        if echo "$FRONTEND_HTML" | grep -qi "vite\|svelte\|focus"; then
            echo -e "  ${BLUE}ℹ${NC} Frontend application detected"
        fi
    else
        print_service "Frontend" "warning" "Not running on port $FRONTEND_PORT"
        echo -e "  ${YELLOW}⚠${NC} Frontend is optional for backend-only operations"
    fi
}

###############################################################################
# Critical Endpoints Check
###############################################################################

check_critical_endpoints() {
    echo "Checking Critical API Endpoints..."

    local endpoints_ok=true

    # Test knowledge endpoint
    KNOWLEDGE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/knowledge/item-types" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$KNOWLEDGE" | tail -1)

    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo -e "  ${GREEN}✓${NC} /knowledge/item-types (requires auth: ✓)"
    else
        echo -e "  ${RED}✗${NC} /knowledge/item-types (unexpected code: $HTTP_CODE)"
        endpoints_ok=false
    fi

    # Test agent-tools endpoint
    AGENT_TOOLS=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/agent-tools/knowledge" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$AGENT_TOOLS" | tail -1)

    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo -e "  ${GREEN}✓${NC} /agent-tools/knowledge (requires auth: ✓)"
    else
        echo -e "  ${RED}✗${NC} /agent-tools/knowledge (unexpected code: $HTTP_CODE)"
        endpoints_ok=false
    fi

    # Test settings endpoint
    SETTINGS=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/settings/usage-stats" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$SETTINGS" | tail -1)

    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo -e "  ${GREEN}✓${NC} /settings/usage-stats (requires auth: ✓)"
    else
        echo -e "  ${RED}✗${NC} /settings/usage-stats (unexpected code: $HTTP_CODE)"
        endpoints_ok=false
    fi

    # Test knowledge-ai endpoint
    KNOWLEDGE_AI=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/knowledge-ai/chat" -X POST \
        -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$KNOWLEDGE_AI" | tail -1)

    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "422" ]; then
        echo -e "  ${GREEN}✓${NC} /knowledge-ai/chat (requires auth: ✓)"
    else
        echo -e "  ${RED}✗${NC} /knowledge-ai/chat (unexpected code: $HTTP_CODE)"
        endpoints_ok=false
    fi

    if [ "$endpoints_ok" = true ]; then
        print_service "Critical Endpoints" "healthy" "All endpoints properly secured"
    else
        print_service "Critical Endpoints" "unhealthy" "Some endpoints have issues"
    fi
}

###############################################################################
# Main Execution
###############################################################################

print_header

echo "Timestamp: $(date)"
echo ""

print_separator

# Run all checks
check_backend
print_separator

check_database
print_separator

check_ii_agent
print_separator

check_frontend
print_separator

check_critical_endpoints
print_separator

# Summary
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║                  Summary                          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✓ All critical services are healthy${NC}"
    echo ""
    echo "System is ready for:"
    echo "  • API requests on http://localhost:$BACKEND_PORT"
    echo "  • II-Agent connections on ws://localhost:$II_AGENT_PORT"
    echo "  • Frontend access on http://localhost:$FRONTEND_PORT"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some services are unhealthy${NC}"
    echo ""
    echo "Please check the detailed output above."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure all services are started"
    echo "  2. Check logs in backend/logs/ (if available)"
    echo "  3. Verify .env configuration"
    echo "  4. Check database connection"
    echo ""
    exit 1
fi
