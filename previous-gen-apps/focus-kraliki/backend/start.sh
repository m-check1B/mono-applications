#!/bin/bash

echo "🚀 Starting Focus by Kraliki FastAPI Backend"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your API keys"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Ensure vendor packages are on PYTHONPATH
export PYTHONPATH="$(pwd):$(pwd)/..:$PYTHONPATH"

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start server
echo "✨ Starting uvicorn server on http://127.0.0.1:3017"
echo "📖 API docs: http://127.0.0.1:3017/docs"
echo ""
python -m uvicorn app.main:app --host 127.0.0.1 --port 3017 --reload
