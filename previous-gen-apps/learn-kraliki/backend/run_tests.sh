#!/bin/bash
# Run tests for Learn by Kraliki backend
# This script activates the virtual environment and runs pytest

cd "$(dirname "$0")"

# Activate virtual environment
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run: python -m venv .venv"
    exit 1
fi

# Run pytest
python -m pytest tests/ "$@"
