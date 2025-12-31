#!/bin/bash
# Run backend tests using UV and pytest

set -e

cd "$(dirname "$0")/../backend"

echo "Running backend tests..."
uv run pytest tests/ -v

echo "Backend tests completed successfully!"
