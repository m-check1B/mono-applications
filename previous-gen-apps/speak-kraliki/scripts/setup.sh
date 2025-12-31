#!/bin/bash
# Speak by Kraliki - Initial Setup

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "${ROOT_DIR}/.env" ]; then
    "${ROOT_DIR}/scripts/generate_env.sh"
    echo "Created root .env with generated secrets"
fi

echo "/// SPEAK BY KRALIKI - SETUP ///"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "Created .env file - please update with your settings"
fi

# Frontend setup
echo ""
echo "Setting up frontend..."
cd ../frontend
npm install

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update backend/.env with your API keys"
echo "  2. Start PostgreSQL (or use Docker: docker compose up -d db)"
echo "  3. Run migrations: cd backend && alembic upgrade head"
echo "  4. Start dev servers: ./scripts/start.sh"
