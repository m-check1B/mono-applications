#!/bin/bash
# Speak by Kraliki - Start Development Environment

set -e

echo "/// SPEAK BY KRALIKI ///"
echo "Starting development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running"
    exit 1
fi

# Start services
docker compose up -d

echo ""
echo "Services started!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Run 'docker compose logs -f' to view logs"
