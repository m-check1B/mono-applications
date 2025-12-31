#!/bin/bash
#
# Lab by Kraliki Pro - Reset Demo Environment
# Run between demos to clean up
#

set -e

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GREEN='\033[0;32m'
NC='\033[0m'

echo "Resetting demo environment..."

# 1. Clear demo workspace (but preserve sample projects)
if [ -d "$DEMO_DIR/workspace" ]; then
    rm -rf "$DEMO_DIR/workspace"/*
    echo -e "${GREEN}[OK]${NC} Workspace cleared"
fi

# 2. Clear demo outputs
if [ -d "$DEMO_DIR/outputs/live" ]; then
    rm -rf "$DEMO_DIR/outputs/live"/*
    echo -e "${GREEN}[OK]${NC} Live outputs cleared"
fi

# 3. Reset any temporary files
find "$DEMO_DIR" -name "*.tmp" -delete 2>/dev/null || true
find "$DEMO_DIR" -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo "Demo environment reset complete."
echo "Ready for next demonstration."
echo ""
