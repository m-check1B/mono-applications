#!/bin/bash
# Quick start for secure Kraliki swarm CLI container

set -e

echo "============================================"
echo "Kraliki Swarm CLI - Secure Container Setup"
echo "============================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to swarm directory
cd "$(dirname "$0")"

# Check if .env.swarm exists
if [ ! -f .env.swarm ]; then
    echo "Creating .env.swarm from template..."
    cp .env.swarm.template .env.swarm
    
    echo ""
    echo "⚠️  IMPORTANT: Edit .env.swarm with your API keys before continuing!"
    echo ""
    read -p "Press Enter to edit .env.swarm with nano..."
    
    nano .env.swarm
    
    echo ""
    echo "Please verify the following in .env.swarm:"
    echo "  - LINEAR_API_KEY is set"
    echo "  - ANTHROPIC_API_KEY is set"
    echo "  - OPENAI_API_KEY is set"
    echo ""
    read -p "Press Enter to continue..."
fi

# Load environment
source .env.swarm

# Verify critical keys
if [ -z "$LINEAR_API_KEY" ] || [ "$LINEAR_API_KEY" = "your-linear-api-key-here" ]; then
    echo "Error: LINEAR_API_KEY is not set in .env.swarm"
    echo "Please edit .env.swarm and add your API key."
    exit 1
fi

# Run security validation
echo ""
echo "Running security validation..."
bash scripts/security-validate.sh

if [ $? -ne 0 ]; then
    echo "Security validation failed. Please fix issues before continuing."
    exit 1
fi

# Check if container already exists
if docker ps -a | grep -q kraliki-swarm-cli; then
    echo ""
    read -p "Container 'kraliki-swarm-cli' already exists. Remove and recreate? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old container..."
        docker compose -f docker-compose.swarm.yml down
    else
        echo "Aborted."
        exit 0
    fi
fi

# Build image
echo ""
echo "Building swarm CLI image..."
docker compose -f docker-compose.swarm.yml build

# Start container
echo ""
echo "Starting swarm CLI container..."
docker compose -f docker-compose.swarm.yml up -d

# Wait for container to be healthy
echo "Waiting for container to be healthy..."
timeout 30 bash -c 'until docker inspect kraliki-swarm-cli | grep -q "\"Status\": \"healthy\""; do sleep 1; done' || echo "Container not healthy yet, continuing anyway..."

# Show logs
echo ""
echo "============================================"
echo "✓ Swarm CLI container is running!"
echo "============================================"
echo ""
echo "Useful commands:"
echo "  View logs:        docker logs -f kraliki-swarm-cli"
echo "  Stop container:    docker compose -f docker-compose.swarm.yml down"
echo "  Restart:          docker restart kraliki-swarm-cli"
echo "  Check health:     docker inspect kraliki-swarm-cli | grep Status"
echo "  Resource usage:   docker stats kraliki-swarm-cli"
echo ""
echo "Security validation:"
echo "  Run again:        bash scripts/security-validate.sh"
echo ""
echo "============================================"
echo "Last 20 lines of logs:"
echo "============================================"
docker logs --tail 20 kraliki-swarm-cli
