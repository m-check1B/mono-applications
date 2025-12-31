#!/bin/bash
#
# Lab by Kraliki Pro - Demo Environment Startup
# Run this before any client demonstration
#

set -e

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "  LAB BY KRALIKI PRO - Demo Environment Setup"
echo "=============================================="
echo ""

# 1. Check core services
echo -e "${YELLOW}[1/5] Checking core services...${NC}"

check_service() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}[OK]${NC} $1 available"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $1 not found"
        return 1
    fi
}

check_service "claude" || echo "    Install: https://claude.ai/code"
check_service "docker" || echo "    Install: docker.io"

# 2. Check mgrep is running
echo ""
echo -e "${YELLOW}[2/5] Checking mgrep semantic search...${NC}"

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}[OK]${NC} mgrep is running on port 8001"
else
    echo -e "  ${YELLOW}[WARN]${NC} mgrep not responding - starting..."
    docker compose -f /home/adminmatej/github/infra/compose/mgrep.yml up -d 2>/dev/null || \
        echo -e "  ${RED}[SKIP]${NC} Could not start mgrep"
fi

# 3. Load sample projects into context
echo ""
echo -e "${YELLOW}[3/5] Preparing sample projects...${NC}"

for project in "$DEMO_DIR/sample-projects"/*; do
    if [ -d "$project" ]; then
        project_name=$(basename "$project")
        echo -e "  ${GREEN}[OK]${NC} $project_name ready"
    fi
done

# 4. Create demo workspace
echo ""
echo -e "${YELLOW}[4/5] Setting up demo workspace...${NC}"

DEMO_WORKSPACE="$DEMO_DIR/workspace"
mkdir -p "$DEMO_WORKSPACE"
echo -e "  ${GREEN}[OK]${NC} Demo workspace: $DEMO_WORKSPACE"

# 5. Final status
echo ""
echo -e "${YELLOW}[5/5] Environment check complete${NC}"
echo ""
echo "=============================================="
echo "  DEMO READY"
echo "=============================================="
echo ""
echo "Quick commands:"
echo "  ./run-scenario.sh agency-website   # Agency demo"
echo "  ./run-scenario.sh consulting-deck  # Consulting demo"
echo "  ./run-scenario.sh content-campaign # Content demo"
echo ""
echo "Sample projects in: $DEMO_DIR/sample-projects/"
echo "Demo workspace in:  $DEMO_WORKSPACE"
echo ""
echo "Tip: Run './demo-reset.sh' between demos"
echo ""
