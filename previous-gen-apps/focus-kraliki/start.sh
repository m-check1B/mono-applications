#!/bin/bash
set -e

echo "🚀 Starting Focus by Kraliki with ii-agent..."

# Function to cleanup background jobs on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null || true
    exit
}
trap cleanup SIGINT SIGTERM EXIT

# Export OpenRouter credentials for ii-agent
export OPENAI_API_KEY="${AI_INTEGRATIONS_OPENROUTER_API_KEY}"
export OPENAI_BASE_URL="${AI_INTEGRATIONS_OPENROUTER_BASE_URL}"

# Start backend
echo "📦 Starting backend on http://127.0.0.1:3017..."
cd backend
export PYTHONPATH="$(pwd):$(pwd)/..:$PYTHONPATH"
python -m uvicorn app.main:app --host 127.0.0.1 --port 3017 --reload &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start ii-agent (requires DATABASE_URL to be set to PostgreSQL)
echo "🤖 Starting ii-agent on http://127.0.0.1:8765..."
cd ii-agent
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
export FILE_STORE_PATH="$(pwd)/data"  # Use project directory for file storage
.venv/bin/python ws_server.py --host 127.0.0.1 --port 8765 &
AGENT_PID=$!
cd ..

# Wait for ii-agent to initialize
sleep 2

# Start frontend
echo "🎨 Starting frontend on http://0.0.0.0:5000..."
cd frontend
pnpm dev &
FRONTEND_PID=$!
cd ..

echo "✅ All services running!"
echo "📖 Backend API: http://127.0.0.1:3017/docs"
echo "🤖 ii-agent: http://127.0.0.1:8765"
echo "🌐 Frontend: http://0.0.0.0:5000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes
wait
