#!/bin/bash
#
# Lab by Kraliki Pro - Run Demo Scenario
# Usage: ./run-scenario.sh <scenario-name>
#

set -e

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCENARIO="$1"

if [ -z "$SCENARIO" ]; then
    echo "Usage: $0 <scenario-name>"
    echo ""
    echo "Available scenarios:"
    echo "  agency-website    - Build a landing page (Build-Audit-Fix pattern)"
    echo "  consulting-deck   - Create analysis deck (Parallel execution)"
    echo "  content-campaign  - Generate content (Multi-stream generation)"
    echo "  quick-audit       - Code/content audit (Fast demo, 5 min)"
    echo ""
    exit 1
fi

SCENARIO_FILE="$DEMO_DIR/scenarios/${SCENARIO}.md"

if [ ! -f "$SCENARIO_FILE" ]; then
    echo "Error: Scenario '$SCENARIO' not found"
    echo "Looking for: $SCENARIO_FILE"
    exit 1
fi

echo "=============================================="
echo "  Starting Demo: $SCENARIO"
echo "=============================================="
echo ""
echo "Scenario details in: $SCENARIO_FILE"
echo ""
echo "Opening scenario guide..."
echo ""

# Display the scenario file for the presenter
cat "$SCENARIO_FILE"

echo ""
echo "=============================================="
echo "  Ready to demonstrate"
echo "=============================================="
echo ""
echo "Presenter: Follow the script above step by step."
echo ""
