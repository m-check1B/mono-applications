#!/bin/bash

echo "🚀 Starting Focus by Kraliki with ii-agent..."
echo ""

# Set environment variables for ii-agent from Replit secrets
export OPENAI_API_KEY="${AI_INTEGRATIONS_OPENROUTER_API_KEY}"
export OPENAI_BASE_URL="${AI_INTEGRATIONS_OPENROUTER_BASE_URL}"

# Export Python path for ii-agent
export PYTHONPATH="${PWD}/ii-agent/src:${PYTHONPATH}"

# Start both services in parallel
(
  echo "📦 Starting backend on http://127.0.0.1:3017..."
  cd backend && PYTHONPATH=${PWD}:${PYTHONPATH} uvicorn app.main:app --host 127.0.0.1 --port 3017 --reload
) &

(
  echo "🤖 Starting ii-agent on http://127.0.0.1:8765..."
  sleep 3  # Wait for backend to start first
  cd ii-agent && python ws_server.py --host 127.0.0.1 --port 8765
) &

(
  echo "🎨 Starting frontend on http://127.0.0.1:5000..."
  sleep 5  # Wait for both backends
  cd frontend && pnpm dev --host 127.0.0.1 --port 5000
) &

wait

echo "✅ All services running!"
echo "📖 Backend API: http://127.0.0.1:3017/docs"
echo "🤖 ii-agent: http://127.0.0.1:8765"
echo "🎨 Frontend: http://127.0.0.1:5000"
