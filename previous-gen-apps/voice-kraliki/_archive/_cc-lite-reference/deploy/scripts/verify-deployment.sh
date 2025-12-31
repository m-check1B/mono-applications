#!/bin/bash
set -e

# Voice by Kraliki Deployment Verification Script
# Comprehensive health checks for production deployment

echo "🔍 Voice by Kraliki Deployment Verification"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
check_pass() {
  echo -e "${GREEN}✅ PASS${NC}: $1"
  ((PASSED++))
}

check_fail() {
  echo -e "${RED}❌ FAIL${NC}: $1"
  ((FAILED++))
}

check_warn() {
  echo -e "${YELLOW}⚠️  WARN${NC}: $1"
  ((WARNINGS++))
}

check_info() {
  echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# 1. Environment Configuration
echo -e "\n${YELLOW}📋 Checking Environment Configuration...${NC}"

if [ -f .env.production ]; then
  check_pass "Environment file exists"

  # Check for CHANGE_ME placeholders
  CHANGE_ME_COUNT=$(grep -c "CHANGE_ME" .env.production 2>/dev/null || echo "0")
  if [ "$CHANGE_ME_COUNT" -eq 0 ]; then
    check_pass "No CHANGE_ME placeholders found"
  else
    check_fail "Found $CHANGE_ME_COUNT CHANGE_ME placeholders in .env.production"
  fi

  # Check critical variables
  source .env.production 2>/dev/null || true

  [ -n "$DATABASE_URL" ] && check_pass "DATABASE_URL is set" || check_fail "DATABASE_URL not set"
  [ -n "$JWT_SECRET" ] && check_pass "JWT_SECRET is set" || check_fail "JWT_SECRET not set"
  [ -n "$REDIS_URL" ] && check_pass "REDIS_URL is set" || check_fail "REDIS_URL not set"

  # Check demo mode disabled
  if [ "$SEED_DEMO_USERS" = "false" ]; then
    check_pass "Demo mode disabled"
  else
    check_warn "Demo mode is enabled (should be false in production)"
  fi

else
  check_fail "Environment file not found"
fi

# 2. Docker Services
echo -e "\n${YELLOW}🐳 Checking Docker Services...${NC}"

if command -v docker >/dev/null 2>&1; then
  check_pass "Docker is installed"

  # Check if Docker Compose services are running
  if docker compose -f infra/docker/production.yml ps >/dev/null 2>&1; then
    check_info "Docker Compose is configured"

    # Check individual services
    services=("postgres" "redis" "app" "nginx")
    for service in "${services[@]}"; do
      if docker ps | grep -q "cc-lite-$service"; then
        check_pass "Service $service is running"
      else
        check_warn "Service $service is not running"
      fi
    done
  else
    check_warn "Docker Compose services not running"
  fi
else
  check_warn "Docker not installed"
fi

# 3. Database Connectivity
echo -e "\n${YELLOW}🗄️  Checking Database...${NC}"

if [ -n "$DATABASE_URL" ]; then
  if command -v psql >/dev/null 2>&1; then
    if psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
      check_pass "Database connection successful"

      # Check migrations
      if psql "$DATABASE_URL" -c "SELECT * FROM _prisma_migrations LIMIT 1;" >/dev/null 2>&1; then
        check_pass "Database migrations table exists"

        MIGRATION_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM _prisma_migrations;" 2>/dev/null | tr -d ' ')
        check_info "Applied migrations: $MIGRATION_COUNT"
      else
        check_warn "Migrations table not found - run migrations"
      fi
    else
      check_fail "Cannot connect to database"
    fi
  else
    check_warn "psql not installed, skipping database checks"
  fi
else
  check_fail "DATABASE_URL not configured"
fi

# 4. Redis Connectivity
echo -e "\n${YELLOW}🔴 Checking Redis...${NC}"

if [ -n "$REDIS_URL" ]; then
  if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli -u "$REDIS_URL" PING >/dev/null 2>&1; then
      check_pass "Redis connection successful"
    else
      check_fail "Cannot connect to Redis"
    fi
  else
    check_warn "redis-cli not installed, skipping Redis checks"
  fi
else
  check_fail "REDIS_URL not configured"
fi

# 5. Application Health
echo -e "\n${YELLOW}🚀 Checking Application...${NC}"

# Check if app is running
if curl -sf http://localhost:3010/health >/dev/null 2>&1; then
  check_pass "Backend health endpoint responding"

  HEALTH_RESPONSE=$(curl -s http://localhost:3010/health)
  check_info "Health: $HEALTH_RESPONSE"
else
  check_warn "Backend health endpoint not responding"
fi

if curl -sf http://localhost:3007 >/dev/null 2>&1; then
  check_pass "Frontend is accessible"
else
  check_warn "Frontend not accessible"
fi

# 6. SSL/TLS Configuration
echo -e "\n${YELLOW}🔒 Checking SSL/TLS...${NC}"

if [ -f deploy/ssl/fullchain.pem ] && [ -f deploy/ssl/privkey.pem ]; then
  check_pass "SSL certificates found"

  # Check certificate expiration
  if command -v openssl >/dev/null 2>&1; then
    EXPIRY=$(openssl x509 -enddate -noout -in deploy/ssl/fullchain.pem 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
      check_info "Certificate expires: $EXPIRY"
    fi
  fi
else
  check_warn "SSL certificates not found"
fi

# 7. Required Ports
echo -e "\n${YELLOW}🔌 Checking Ports...${NC}"

ports=("3007:Frontend" "3010:Backend" "5432:PostgreSQL" "6379:Redis")
for port_info in "${ports[@]}"; do
  port=$(echo $port_info | cut -d: -f1)
  name=$(echo $port_info | cut -d: -f2)

  if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
    check_pass "Port $port ($name) is listening"
  else
    check_warn "Port $port ($name) not listening"
  fi
done

# 8. Dependencies
echo -e "\n${YELLOW}📦 Checking Dependencies...${NC}"

if [ -d node_modules ]; then
  check_pass "node_modules directory exists"
else
  check_fail "node_modules not found - run pnpm install"
fi

if [ -f pnpm-lock.yaml ]; then
  check_pass "pnpm-lock.yaml exists"
else
  check_warn "pnpm-lock.yaml not found"
fi

# 9. Build Artifacts
echo -e "\n${YELLOW}🔨 Checking Build Artifacts...${NC}"

if [ -d dist ]; then
  check_pass "dist directory exists"

  if [ -f dist/server/server/index.js ]; then
    check_pass "Server bundle found"
  else
    check_warn "Server bundle not found - run pnpm build"
  fi
else
  check_fail "dist directory not found - run pnpm build"
fi

# 10. Logs
echo -e "\n${YELLOW}📝 Checking Logs...${NC}"

if [ -d logs ]; then
  check_pass "logs directory exists"

  LOG_FILES=$(find logs -name "*.log" 2>/dev/null | wc -l)
  check_info "Found $LOG_FILES log files"

  # Check for recent errors
  if [ -f logs/pm2-error.log ]; then
    ERROR_COUNT=$(tail -100 logs/pm2-error.log 2>/dev/null | grep -c "Error" || echo "0")
    if [ "$ERROR_COUNT" -gt 0 ]; then
      check_warn "Found $ERROR_COUNT recent errors in logs"
    else
      check_pass "No recent errors in logs"
    fi
  fi
else
  check_warn "logs directory not found"
fi

# 11. Security Checks
echo -e "\n${YELLOW}🔐 Security Checks...${NC}"

# Check file permissions
if [ -f .env.production ]; then
  PERMS=$(stat -c %a .env.production 2>/dev/null || stat -f %A .env.production 2>/dev/null)
  if [ "$PERMS" = "600" ] || [ "$PERMS" = "400" ]; then
    check_pass ".env.production has secure permissions ($PERMS)"
  else
    check_warn ".env.production permissions are $PERMS (should be 600 or 400)"
  fi
fi

# Check for exposed ports
if command -v ss >/dev/null 2>&1; then
  EXPOSED_PORTS=$(ss -tuln | grep -c "0.0.0.0" || echo "0")
  if [ "$EXPOSED_PORTS" -eq 0 ]; then
    check_pass "No services bound to 0.0.0.0"
  else
    check_warn "$EXPOSED_PORTS services bound to 0.0.0.0 (potential security risk)"
  fi
fi

# 12. Monitoring
echo -e "\n${YELLOW}📊 Checking Monitoring...${NC}"

# Check Prometheus
if curl -sf http://localhost:9090/-/healthy >/dev/null 2>&1; then
  check_pass "Prometheus is healthy"
else
  check_warn "Prometheus not accessible"
fi

# Check Grafana
if curl -sf http://localhost:3000/api/health >/dev/null 2>&1; then
  check_pass "Grafana is healthy"
else
  check_warn "Grafana not accessible"
fi

# 13. API Keys
echo -e "\n${YELLOW}🔑 Checking API Keys...${NC}"

[ -n "$TWILIO_ACCOUNT_SID" ] && check_pass "Twilio credentials configured" || check_warn "Twilio not configured"
[ -n "$OPENAI_API_KEY" ] && check_pass "OpenAI API key configured" || check_warn "OpenAI not configured"
[ -n "$DEEPGRAM_API_KEY" ] && check_pass "Deepgram API key configured" || check_warn "Deepgram not configured"
[ -n "$STRIPE_SECRET_KEY" ] && check_pass "Stripe configured" || check_warn "Stripe not configured"

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}          VERIFICATION SUMMARY          ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"

# Overall status
if [ $FAILED -gt 0 ]; then
  echo -e "\n${RED}❌ Deployment has FAILED checks${NC}"
  echo "Please fix the failed items before proceeding to production."
  exit 1
elif [ $WARNINGS -gt 5 ]; then
  echo -e "\n${YELLOW}⚠️  Deployment has WARNINGS${NC}"
  echo "Review warnings before deploying to production."
  exit 2
else
  echo -e "\n${GREEN}✅ Deployment verification PASSED${NC}"
  echo "System is ready for production!"
  exit 0
fi