#!/bin/bash
# TL;DR Bot - Run Tests
# Uses the project's virtual environment to ensure all dependencies are available

set -e

echo "/// TL;DR Bot - RUNNING TESTS ///"
echo ""

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/.."

cd "${PROJECT_DIR}"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found. Run: uv sync"
    exit 1
fi

# Run tests using the venv's pytest
echo "Running tests with venv pytest..."
.venv/bin/pytest tests/ "$@"
