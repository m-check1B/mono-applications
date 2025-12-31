#!/bin/bash
set -e

echo "🚀 Starting Focus by Kraliki (Production Mode)..."

# Get the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)

cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Export PYTHONPATH relative to project root
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}/backend/vendor"

# Start backend
cd "$PROJECT_ROOT/backend"
echo "📦 Starting backend on http://127.0.0.1:3017..."
uvicorn app.main:app --host 127.0.0.1 --port 3017 &
BACKEND_PID=$!

sleep 3

# Start frontend (using adapter-node build output)
cd "$PROJECT_ROOT/frontend"
echo "🎨 Starting frontend on http://127.0.0.1:${PORT:-5000}..."
BACKEND_URL=http://127.0.0.1:3017 HOST=127.0.0.1 PORT=${PORT:-5000} node build/index.js &
FRONTEND_PID=$!

echo "✅ Both services running in production mode!"
echo "📖 Backend API: http://127.0.0.1:3017"
echo "🌐 Frontend: http://127.0.0.1:5000"

wait
