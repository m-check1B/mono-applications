#!/bin/bash

echo "========================================="
echo "E2E Test Infrastructure Verification"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        return 1
    fi
}

echo "Checking directories..."
check_dir "e2e"
check_dir "e2e/fixtures"
check_dir "e2e/pages"
check_dir "e2e/utils"
check_dir "e2e/tests"
echo ""

echo "Checking configuration files..."
check_file "playwright.config.ts"
check_file "e2e/.gitignore"
echo ""

echo "Checking fixtures..."
check_file "e2e/fixtures/auth.fixture.ts"
check_file "e2e/fixtures/test-data.ts"
echo ""

echo "Checking Page Object Models..."
check_file "e2e/pages/LoginPage.ts"
check_file "e2e/pages/DashboardPage.ts"
check_file "e2e/pages/CallPage.ts"
echo ""

echo "Checking utilities..."
check_file "e2e/utils/helpers.ts"
check_file "e2e/utils/assertions.ts"
echo ""

echo "Checking global setup/teardown..."
check_file "e2e/global-setup.ts"
check_file "e2e/global-teardown.ts"
echo ""

echo "Checking test files..."
check_file "e2e/tests/auth.spec.ts"
check_file "e2e/tests/dashboard.spec.ts"
check_file "e2e/tests/calls.spec.ts"
echo ""

echo "Checking documentation..."
check_file "e2e/README.md"
check_file "e2e/USAGE_EXAMPLES.md"
check_file "e2e/QUICK_REFERENCE.md"
check_file "E2E_INFRASTRUCTURE_SUMMARY.md"
echo ""

echo "Checking npm scripts..."
if grep -q "test:e2e" package.json; then
    echo -e "${GREEN}✓${NC} npm scripts configured"
else
    echo -e "${RED}✗${NC} npm scripts missing"
fi
echo ""

echo "Checking Playwright installation..."
if [ -d "node_modules/@playwright/test" ]; then
    echo -e "${GREEN}✓${NC} Playwright installed"
else
    echo -e "${YELLOW}!${NC} Playwright not installed (run: npm install)"
fi
echo ""

echo "========================================="
echo "Verification complete!"
echo ""
echo "Next steps:"
echo "1. Install Playwright browsers: npx playwright install"
echo "2. Start backend: cd ../backend && python -m uvicorn app.main:app --reload"
echo "3. Start frontend: npm run dev"
echo "4. Run tests: npm run test:e2e"
echo "========================================="
