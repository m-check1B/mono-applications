#!/bin/bash
# Start mgrep services and index Focus by Kraliki documentation

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Focus by Kraliki Semantic Search Setup"
echo "================================"

# 1. Start mgrep services
echo "Note: Focus-Kraliki uses workspace mgrep (port 8001) by default."
echo "      To use standalone mgrep (port 8002), uncomment the docker compose command below."
# docker compose -f docker-compose.mgrep.yml up -d

# Wait for services to be ready
sleep 3

# Check if mgrep backend is running
if ! curl -s --connect-timeout 5 http://localhost:8001/v1/stores >/dev/null 2>&1; then
    echo "Warning: mgrep backend not responding, continuing anyway..."
fi

# 2. Index documentation
echo "Indexing documentation to workspace mgrep..."
python3 scripts/index-docs.py

echo ""
echo "Setup complete!"
echo ""
echo "Search examples:"
echo "  curl -X POST http://localhost:8001/v1/stores/search \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"how to authenticate users\", \"store_identifiers\": [\"focus_kraliki_docs\"]}'"
echo ""
echo "Run test queries:"
echo "  ./scripts/test-mgrep.sh"
