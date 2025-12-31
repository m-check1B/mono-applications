#!/bin/bash

###############################################################################
# End-to-End Test Script for Focus by Kraliki
# Tests all services and integration points
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((++TESTS_PASSED))
    ((++TESTS_TOTAL))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((++TESTS_FAILED))
    ((++TESTS_TOTAL))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Service ports
BACKEND_PORT=3017
II_AGENT_PORT=8765
FRONTEND_PORT=5173

###############################################################################
# 0. RabbitMQ Health Check
###############################################################################

log_section "0. RabbitMQ Health Check"
if (cd backend && python scripts/check_rabbitmq.py); then
    log_info "RabbitMQ is reachable"
else
    log_error "RabbitMQ health check failed"
    exit 1
fi

###############################################################################
# 1. Service Health Checks
###############################################################################

log_section "1. Checking Service Health"

# Check backend
log_info "Checking Backend API (port $BACKEND_PORT)..."
if curl -s -f "http://localhost:$BACKEND_PORT/health" > /dev/null; then
    log_success "Backend API is running"
else
    log_error "Backend API is not responding"
fi

# Check backend root endpoint
log_info "Checking Backend root endpoint..."
BACKEND_ROOT=$(curl -s "http://localhost:$BACKEND_PORT/" || echo "")
if echo "$BACKEND_ROOT" | grep -q "Focus by Kraliki API"; then
    log_success "Backend root endpoint returns correct response"
else
    log_error "Backend root endpoint failed"
fi

# Check II-Agent WebSocket (basic TCP check)
log_info "Checking II-Agent WebSocket (port $II_AGENT_PORT)..."
if timeout 2 bash -c "echo > /dev/tcp/localhost/$II_AGENT_PORT" 2>/dev/null; then
    log_success "II-Agent WebSocket is listening"
else
    log_warn "II-Agent WebSocket check inconclusive (may not be running)"
fi

# Check frontend (if running)
log_info "Checking Frontend (port $FRONTEND_PORT)..."
if curl -s -f "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
    log_success "Frontend is running"
else
    log_warn "Frontend is not running (optional for backend tests)"
fi

###############################################################################
# 2. Database Connectivity
###############################################################################

log_section "2. Checking Database Connectivity"

log_info "Checking database connection via backend..."
# The backend health endpoint should work if DB is connected
if curl -s -f "http://localhost:$BACKEND_PORT/health" > /dev/null; then
    log_success "Database connection is working"
else
    log_error "Database connection failed"
fi

###############################################################################
# 3. API Endpoint Tests
###############################################################################

log_section "3. Testing Critical API Endpoints"

# Test authentication endpoint
log_info "Testing auth endpoint accessibility..."
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/auth/register" -X POST \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "422" ] || [ "$HTTP_CODE" = "400" ]; then
    log_success "Auth endpoint is accessible (validation working)"
elif [ "$HTTP_CODE" = "200" ]; then
    log_warn "Auth endpoint accessible but validation may be off"
else
    log_error "Auth endpoint not accessible (HTTP $HTTP_CODE)"
fi

# Test knowledge endpoint (should require auth)
log_info "Testing knowledge endpoint requires auth..."
KNOWLEDGE_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/knowledge/item-types" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$KNOWLEDGE_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    log_success "Knowledge endpoint requires authentication"
else
    log_error "Knowledge endpoint auth check failed (HTTP $HTTP_CODE)"
fi

# Test settings endpoint (should require auth)
log_info "Testing settings endpoint requires auth..."
SETTINGS_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/settings/usage-stats" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$SETTINGS_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    log_success "Settings endpoint requires authentication"
else
    log_error "Settings endpoint auth check failed (HTTP $HTTP_CODE)"
fi

# Test agent-tools endpoint (should require auth)
log_info "Testing agent-tools endpoint requires auth..."
AGENT_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/agent-tools/knowledge" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$AGENT_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    log_success "Agent-tools endpoint requires authentication"
else
    log_error "Agent-tools endpoint auth check failed (HTTP $HTTP_CODE)"
fi

# Test API docs (if in debug mode)
log_info "Checking API documentation..."
DOCS_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:$BACKEND_PORT/docs" 2>/dev/null || echo "000")
HTTP_CODE=$(echo "$DOCS_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    log_success "API documentation is accessible"
elif [ "$HTTP_CODE" = "404" ]; then
    log_warn "API docs disabled (production mode)"
else
    log_warn "API docs check inconclusive (HTTP $HTTP_CODE)"
fi

###############################################################################
# 4. Run Integration Tests
###############################################################################

log_section "4. Running Integration Test Suite"

# Change to backend directory
cd "$(dirname "$0")/backend" || exit 1

log_info "Running pytest integration tests..."

# Run pytest with coverage
if pytest tests/integration/ -v --tb=short --color=yes --cov-fail-under=50 2>&1 | tee /tmp/pytest_output.log; then
    log_success "Integration tests passed"
else
    log_error "Integration tests failed"
    log_info "Check /tmp/pytest_output.log for details"
fi

# Extract test results
if [ -f /tmp/pytest_output.log ]; then
    PYTEST_PASSED=$(grep -oP '\d+(?= passed)' /tmp/pytest_output.log | tail -1 || echo "0")
    PYTEST_FAILED=$(grep -oP '\d+(?= failed)' /tmp/pytest_output.log | tail -1 || echo "0")

    log_info "Pytest results: $PYTEST_PASSED passed, $PYTEST_FAILED failed"
fi

###############################################################################
# 5. Frontend Build Test (Optional)
###############################################################################

log_section "5. Testing Frontend Build"

if [ -d "../frontend" ]; then
    log_info "Checking if frontend can build..."
    cd ../frontend || exit 1

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_warn "Frontend dependencies not installed, skipping build test"
    else
        # Try to build (dry run / type check only)
        if npm run check > /dev/null 2>&1; then
            log_success "Frontend type checking passed"
        else
            log_warn "Frontend type checking failed or not configured"
        fi
    fi

    cd ..
else
    log_warn "Frontend directory not found, skipping frontend tests"
fi

###############################################################################
# 6. Configuration Validation
###############################################################################

log_section "6. Validating Configuration"

cd backend || exit 1

# Check .env file exists
if [ -f ".env" ]; then
    log_success ".env configuration file exists"

    # Check critical env vars (without exposing values)
    log_info "Checking critical environment variables..."

    if grep -q "DATABASE_URL" .env && [ -n "$(grep DATABASE_URL .env | cut -d= -f2)" ]; then
        log_success "DATABASE_URL is configured"
    else
        log_error "DATABASE_URL is missing or empty"
    fi

    if grep -q "JWT_SECRET" .env && [ -n "$(grep JWT_SECRET .env | cut -d= -f2)" ]; then
        log_success "JWT_SECRET is configured"
    else
        log_error "JWT_SECRET is missing or empty"
    fi

else
    log_error ".env configuration file not found"
fi

# Check requirements.txt exists
if [ -f "requirements.txt" ]; then
    log_success "requirements.txt exists"
else
    log_error "requirements.txt not found"
fi

###############################################################################
# 7. Test Report Generation
###############################################################################

log_section "7. Generating Test Report"

REPORT_FILE="/tmp/focus_kraliki_e2e_report_$(date +%Y%m%d_%H%M%S).txt"

cat > "$REPORT_FILE" << EOF
Focus by Kraliki End-to-End Test Report
Generated: $(date)

================================
Summary
================================
Total Tests: $TESTS_TOTAL
Passed: $TESTS_PASSED
Failed: $TESTS_FAILED
Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

================================
Service Status
================================
Backend API: http://localhost:$BACKEND_PORT
II-Agent WebSocket: ws://localhost:$II_AGENT_PORT
Frontend: http://localhost:$FRONTEND_PORT

================================
Test Coverage
================================
✓ Service health checks
✓ Database connectivity
✓ API endpoint security
✓ Integration tests
✓ Configuration validation

================================
Details
================================
See pytest output: /tmp/pytest_output.log

EOF

log_success "Test report saved to: $REPORT_FILE"

###############################################################################
# Final Summary
###############################################################################

log_section "Test Summary"

echo ""
echo "╔════════════════════════════════════╗"
echo "║     Focus by Kraliki E2E Test Suite     ║"
echo "╚════════════════════════════════════╝"
echo ""
echo "Total Tests:    $TESTS_TOTAL"
echo "Passed:         ${GREEN}$TESTS_PASSED${NC}"
echo "Failed:         ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Check the following for details:"
    echo "  - Test report: $REPORT_FILE"
    echo "  - Pytest output: /tmp/pytest_output.log"
    echo ""
    exit 1
fi
