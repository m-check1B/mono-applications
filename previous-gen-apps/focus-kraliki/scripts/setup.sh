#!/bin/bash
# Focus by Kraliki - Complete Setup Script
# This script sets up both backend and frontend for development

set -e  # Exit on error

echo "🚀 Focus by Kraliki - Complete Setup"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}❌ pnpm not found. Installing...${NC}"
    npm install -g pnpm
fi
echo -e "${GREEN}✅ pnpm found: $(pnpm --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.14+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

# Check uv (Python package manager)
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv not found. Please install uv (https://docs.astral.sh/uv/).${NC}"
    exit 1
fi
echo -e "${GREEN}✅ uv found: $(uv --version)${NC}"

# Check PostgreSQL (optional - can use Docker)
if ! command -v psql &> /dev/null; then
    echo -e "${BLUE}ℹ️  PostgreSQL client not found. You can use Docker instead.${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL found${NC}"
fi

echo ""
echo -e "${BLUE}Setting up Python environment with uv...${NC}"
# uv creates .venv in the project root by default
uv sync --locked

# Ensure backend/.env exists
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo -e "${BLUE}⚠️  Please edit backend/.env with your API keys${NC}"
fi

echo ""
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing frontend dependencies..."
pnpm install

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate the uv environment: source .venv/bin/activate"
echo "2. Edit backend/.env with your API keys (Anthropic, OpenAI, Deepgram)"
echo "3. Set up PostgreSQL database (see docs/BACKEND.md)"
echo "4. Run database migrations: cd backend && alembic upgrade head"
echo "5. Start services with: ./scripts/start.sh"
echo ""
