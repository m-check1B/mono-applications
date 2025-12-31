#!/bin/bash
# Focus by Kraliki - Start Development Servers
# Starts both backend and frontend in separate terminals

set -e

echo "🚀 Focus by Kraliki - Starting Development Servers"
echo "============================================"
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Starting services in tmux session 'focus-kraliki'..."

    # Create new tmux session
    tmux new-session -d -s focus-kraliki

    # Split window horizontally
    tmux split-window -h -t focus-kraliki

    # Start backend in left pane
    tmux send-keys -t focus-kraliki:0.0 'cd backend && export PYTHONPATH="$(pwd):$(pwd)/..:$PYTHONPATH" && source venv/bin/activate && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3017' C-m

    # Start frontend in right pane
    tmux send-keys -t focus-kraliki:0.1 'cd frontend && pnpm dev' C-m

    # Attach to session
    tmux attach -t focus-kraliki

else
    echo "tmux not found. Starting in background..."
    echo ""

    # Start backend
    echo "Starting backend on http://127.0.0.1:3017"
    cd backend
    export PYTHONPATH="$(pwd):$(pwd)/..:$PYTHONPATH"
    source venv/bin/activate
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3017 &
    BACKEND_PID=$!
    cd ..

    # Start frontend
    echo "Starting frontend on http://127.0.0.1:5175"
    cd frontend
    pnpm dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "✅ Services started!"
    echo "   Backend: http://127.0.0.1:3017"
    echo "   Backend Docs: http://127.0.0.1:3017/docs"
    echo "   Frontend: http://127.0.0.1:5175"
    echo ""
    echo "Press Ctrl+C to stop all services"

    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
fi
