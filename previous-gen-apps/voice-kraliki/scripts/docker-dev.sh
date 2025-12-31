#!/bin/bash
# Quick start script for Docker development environment

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Voice by Kraliki - Docker Development${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from template...${NC}"
    cp "$PROJECT_ROOT/.env.docker" "$PROJECT_ROOT/.env"
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please edit .env with your API keys and configuration${NC}"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and edit .env first..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Start services
echo ""
echo -e "${BLUE}Starting development services...${NC}"
docker-compose -f "$PROJECT_ROOT/docker-compose.dev.yml" up -d

# Wait for services to be healthy
echo ""
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo ""
echo -e "${BLUE}Checking service health...${NC}"

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend not responding yet (may still be starting)${NC}"
fi

# Check frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Frontend not responding yet (may still be starting)${NC}"
fi

# Check database
if docker-compose -f "$PROJECT_ROOT/docker-compose.dev.yml" exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not ready yet${NC}"
fi

# Check Redis
if docker-compose -f "$PROJECT_ROOT/docker-compose.dev.yml" exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Redis not ready yet${NC}"
fi

# Display access information
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services are starting!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Qdrant:    http://localhost:6333/dashboard"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo "  docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo -e "${BLUE}Stop services:${NC}"
echo "  docker-compose -f docker-compose.dev.yml down"
echo ""
echo -e "${YELLOW}Note: Services may take a few seconds to fully start${NC}"
echo -e "${YELLOW}Check logs if you encounter connection issues${NC}"
echo ""
