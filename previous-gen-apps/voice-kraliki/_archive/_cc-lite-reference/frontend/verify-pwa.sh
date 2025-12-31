#!/bin/bash

# PWA Implementation Verification Script
# This script verifies that all PWA components are correctly implemented

echo "======================================"
echo "Voice by Kraliki PWA Implementation Verification"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASS=0
FAIL=0

check_file() {
  local file=$1
  local description=$2

  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $description"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} $description - FILE MISSING: $file"
    ((FAIL++))
  fi
}

echo "1. PWA Core Files"
echo "=================="
check_file "static/manifest.json" "PWA manifest with shortcuts"
check_file "static/service-worker.js" "Service worker with offline caching"
check_file "static/offline.html" "Static offline fallback page"
check_file "src/routes/offline/+page.svelte" "SvelteKit offline route"
echo ""

echo "2. Mobile Components"
echo "===================="
check_file "src/lib/components/mobile/BottomNavigation.svelte" "Bottom navigation component"
check_file "src/lib/components/mobile/FloatingActionButton.svelte" "FAB component"
check_file "src/lib/components/mobile/MobileCard.svelte" "Mobile card component"
check_file "src/lib/components/mobile/CallQueueMobile.svelte" "Mobile call queue"
check_file "src/lib/components/mobile/index.ts" "Mobile components index"
echo ""

echo "3. Layout & Configuration"
echo "========================="
check_file "src/routes/+layout.svelte" "Root layout with PWA meta tags"
check_file "src/app.html" "Base HTML template"
echo ""

echo "4. Icons"
echo "========"
check_file "static/icons/generate-icons.sh" "Icon generation script"
check_file "static/icons/icon-192.png.svg" "192x192 icon"
check_file "static/icons/icon-512.png.svg" "512x512 icon"
echo ""

echo "5. Documentation"
echo "================"
check_file "../PWA_IMPLEMENTATION.md" "PWA implementation guide"
echo ""

# Manifest validation
echo "6. Manifest Validation"
echo "======================"
if [ -f "static/manifest.json" ]; then
  # Check for required fields
  if grep -q '"name"' static/manifest.json && \
     grep -q '"short_name"' static/manifest.json && \
     grep -q '"start_url"' static/manifest.json && \
     grep -q '"display"' static/manifest.json && \
     grep -q '"icons"' static/manifest.json; then
    echo -e "${GREEN}✓${NC} Manifest has required fields"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Manifest missing required fields"
    ((FAIL++))
  fi

  if grep -q '"shortcuts"' static/manifest.json; then
    echo -e "${GREEN}✓${NC} Manifest has app shortcuts"
    ((PASS++))
  else
    echo -e "${YELLOW}⚠${NC} Manifest missing shortcuts (optional)"
  fi
else
  echo -e "${RED}✗${NC} Manifest file not found"
  ((FAIL++))
fi
echo ""

# Service Worker validation
echo "7. Service Worker Validation"
echo "============================"
if [ -f "static/service-worker.js" ]; then
  if grep -q "addEventListener('install'" static/service-worker.js && \
     grep -q "addEventListener('fetch'" static/service-worker.js && \
     grep -q "addEventListener('activate'" static/service-worker.js; then
    echo -e "${GREEN}✓${NC} Service worker has required event listeners"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Service worker missing event listeners"
    ((FAIL++))
  fi

  if grep -q "caches.open" static/service-worker.js; then
    echo -e "${GREEN}✓${NC} Service worker implements caching"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Service worker missing cache implementation"
    ((FAIL++))
  fi
else
  echo -e "${RED}✗${NC} Service worker file not found"
  ((FAIL++))
fi
echo ""

# Layout validation
echo "8. Layout Meta Tags"
echo "==================="
if [ -f "src/routes/+layout.svelte" ]; then
  if grep -q 'serviceWorker' src/routes/+layout.svelte; then
    echo -e "${GREEN}✓${NC} Service worker registration in layout"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Missing service worker registration"
    ((FAIL++))
  fi

  if grep -q 'manifest' src/routes/+layout.svelte; then
    echo -e "${GREEN}✓${NC} Manifest link in layout"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Missing manifest link"
    ((FAIL++))
  fi

  if grep -q 'theme-color' src/routes/+layout.svelte; then
    echo -e "${GREEN}✓${NC} Theme color meta tag"
    ((PASS++))
  else
    echo -e "${RED}✗${NC} Missing theme color"
    ((FAIL++))
  fi

  if grep -q 'viewport-fit=cover' src/routes/+layout.svelte; then
    echo -e "${GREEN}✓${NC} Safe area viewport configuration"
    ((PASS++))
  else
    echo -e "${YELLOW}⚠${NC} Missing safe area viewport (optional)"
  fi
else
  echo -e "${RED}✗${NC} Layout file not found"
  ((FAIL++))
fi
echo ""

# Summary
echo "======================================"
echo "Summary"
echo "======================================"
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed!${NC}"
  echo ""
  echo "Next steps:"
  echo "1. Start dev server: pnpm dev"
  echo "2. Run Lighthouse: lighthouse http://localhost:5173 --view --only-categories=pwa"
  echo "3. Test offline: DevTools > Network > Offline"
  echo "4. Test installation: Chrome > Install Voice by Kraliki"
  echo ""
  exit 0
else
  echo -e "${RED}✗ Some checks failed. Please review the errors above.${NC}"
  echo ""
  exit 1
fi
