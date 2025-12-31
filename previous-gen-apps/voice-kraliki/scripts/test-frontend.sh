#!/bin/bash
# Run frontend linting and type checking

set -e

cd "$(dirname "$0")/../frontend"

echo "Running frontend type check..."
pnpm check

echo "Running frontend format check..."
pnpm run format -- --check

echo "Frontend checks completed successfully!"
