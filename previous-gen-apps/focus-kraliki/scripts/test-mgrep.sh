#!/bin/bash
# Test script for Focus-Kraliki mgrep integration
# Runs semantic search queries to verify integration is working

MGREP_URL="http://localhost:8001"
STORE_ID="focus_kraliki_docs"

echo "Focus-Kraliki Semantic Search Test"
echo "================================"
echo ""
echo "Using mgrep: $MGREP_URL"
echo "Store: $STORE_ID"
echo ""

# Function to run search
run_search() {
    local query="$1"
    echo "Query: $query"
    curl -s -X POST "$MGREP_URL/v1/stores/search" \
        -H 'Content-Type: application/json' \
        -d "{\"query\": \"$query\", \"store_identifiers\": [\"$STORE_ID\"], \"top_k\": 2}" \
        | python3 -c "import sys, json; data=json.load(sys.stdin); results=data.get('data',[]); print(f\"  Found {len(results)} result(s):\"); [print(f\"    - [{r['score']:.3f}] {r['metadata']['file_path'].split('/')[-1]}\") for r in results[:2]]"
    echo ""
}

# Test common task queries
echo "--- Common Task Queries ---"
echo ""

run_search "how to authenticate users"
run_search "database schema setup"
run_search "calendar sync google oauth"
run_search "how to run tests"
run_search "ai agent configuration"
run_search "deployment to production"

echo "================================"
echo "All tests complete!"
echo ""
echo "To run custom searches:"
echo "  curl -X POST $MGREP_URL/v1/stores/search \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"your query\", \"store_identifiers\": [\"$STORE_ID\"]}'"
