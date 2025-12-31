#!/bin/bash
# Start backend development server with hot reload

set -e

cd "$(dirname "$0")/../backend"

echo "Starting backend development server..."
echo "Server will be available at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
