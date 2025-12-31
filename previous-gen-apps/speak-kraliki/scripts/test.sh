#!/bin/bash
# Speak by Kraliki - Run Tests
# Creates/updates venv with test dependencies and runs pytest

set -e

echo "/// SPEAK by KRALIKI - RUNNING TESTS ///"
echo ""

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

cd "${BACKEND_DIR}"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Check if pip exists and works in venv (venv might be corrupt)
if [ ! -f ".venv/bin/pip" ] || ! .venv/bin/pip --version >/dev/null 2>&1; then
    echo "Venv appears corrupt, recreating..."
    rm -rf .venv
    python3 -m venv .venv
fi

# Install test dependencies
echo "Installing test dependencies..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements-test.txt

# Run tests using the venv's pytest
echo ""
echo "Running tests..."
.venv/bin/pytest tests/ "$@"
