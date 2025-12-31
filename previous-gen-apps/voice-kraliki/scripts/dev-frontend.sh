#!/bin/bash
# Start frontend development server

set -e

cd "$(dirname "$0")/../frontend"

echo "Starting frontend development server..."
echo "Server will be available at http://localhost:5173"
echo ""

pnpm dev
