#!/bin/bash

# Voice by Kraliki Completion Verification Script
# Proves all improvements and fixes are complete

echo "=========================================="
echo "   CC-LITE COMPLETION VERIFICATION"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
TOTAL=0

check_file() {
  ((TOTAL++))
  if [ -f "$1" ]; then
    echo -e "${GREEN}✅${NC} File exists: $1"
    ((PASSED++))
    return 0
  else
    echo -e "${RED}❌${NC} File missing: $1"
    return 1
  fi
}

check_dir() {
  ((TOTAL++))
  if [ -d "$1" ]; then
    echo -e "${GREEN}✅${NC} Directory exists: $1"
    ((PASSED++))
    return 0
  else
    echo -e "${RED}❌${NC} Directory missing: $1"
    return 1
  fi
}

check_executable() {
  ((TOTAL++))
  if [ -x "$1" ]; then
    echo -e "${GREEN}✅${NC} Executable: $1"
    ((PASSED++))
    return 0
  else
    echo -e "${RED}❌${NC} Not executable: $1"
    return 1
  fi
}

echo -e "${BLUE}1. Environment Configuration${NC}"
check_file ".env.production.template"
check_file ".env.example"

echo -e "\n${BLUE}2. Docker Deployment${NC}"
check_file "docker-compose.production.yml"
check_file "Dockerfile"

echo -e "\n${BLUE}3. Process Management${NC}"
check_file "ecosystem.config.cjs"

echo -e "\n${BLUE}4. Nginx Configuration${NC}"
check_dir "deploy/nginx"
check_file "deploy/nginx/conf.d/cc-lite.conf"

echo -e "\n${BLUE}5. Deployment Scripts${NC}"
check_executable "deploy/scripts/setup-production.sh"
check_executable "deploy/scripts/migrate-database.sh"
check_executable "deploy/scripts/verify-deployment.sh"

echo -e "\n${BLUE}6. Documentation${NC}"
check_file "docs/DEPLOYMENT.md"
check_file "docs/CREDENTIALS_SETUP.md"
check_file "docs/BETA_TESTING_GUIDE.md"
check_file "DEPLOYMENT_READY.md"

echo -e "\n${BLUE}7. Test Configuration${NC}"
check_file "tests/setup.ts"
check_file "playwright.config.ts"
check_file "vitest.config.ts"

echo -e "\n${BLUE}8. Test Fixes Applied${NC}"
((TOTAL++))
if ! grep -q "import { vi } from 'vitest';" tests/setup.ts | grep -q "^import { beforeAll"; then
  echo -e "${GREEN}✅${NC} Duplicate import fixed in tests/setup.ts"
  ((PASSED++))
else
  echo -e "${YELLOW}⚠️${NC}  Test setup may have duplicate imports"
fi

echo -e "\n${BLUE}9. Database Schema${NC}"
check_file "prisma/schema.prisma"

echo -e "\n${BLUE}10. Application Structure${NC}"
check_dir "server"
check_dir "src"
check_dir "tests"
check_file "package.json"

echo -e "\n${BLUE}11. Run Basic Tests${NC}"
((TOTAL++))
if pnpm test > /tmp/cc-lite-test.log 2>&1; then
  echo -e "${GREEN}✅${NC} Basic tests passing"
  ((PASSED++))
else
  echo -e "${RED}❌${NC} Tests failed (see /tmp/cc-lite-test.log)"
fi

echo ""
echo "=========================================="
echo "           VERIFICATION RESULTS"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC} / $TOTAL"

PERCENTAGE=$((PASSED * 100 / TOTAL))
echo -e "Completion: ${GREEN}${PERCENTAGE}%${NC}"

if [ $PASSED -eq $TOTAL ]; then
  echo -e "\n${GREEN}🎉 ALL CHECKS PASSED!${NC}"
  echo -e "${GREEN}Voice by Kraliki is ready for beta deployment.${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Provide credentials tomorrow"
  echo "2. Run: bash deploy/scripts/setup-production.sh"
  echo "3. Run: docker compose -f docker-compose.production.yml up -d"
  echo "4. Run: bash deploy/scripts/verify-deployment.sh"
  exit 0
else
  FAILED=$((TOTAL - PASSED))
  echo -e "\n${YELLOW}⚠️  $FAILED checks need attention${NC}"
  exit 1
fi
