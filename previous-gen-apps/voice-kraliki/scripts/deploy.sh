#!/bin/bash

# voice-kraliki Deployment Script
# ====================================
# Deploy the application to production using PM2 or Docker

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Voice by Kraliki - Deployment${NC}"
echo -e "${GREEN}================================${NC}"

# Check deployment method
if [ "$1" == "docker" ]; then
    echo -e "${YELLOW}Deploying with Docker Compose...${NC}"

    # Build and start containers
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d

    echo -e "${GREEN}✅ Docker deployment complete!${NC}"
    echo "Access the application at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"

elif [ "$1" == "pm2" ] || [ -z "$1" ]; then
    echo -e "${YELLOW}Deploying with PM2...${NC}"

    # Install dependencies
    echo "Installing backend dependencies..."
    cd backend
    pip3 install -r requirements.txt
    cd ..

    echo "Installing frontend dependencies..."
    cd frontend
    npm install

    # Build frontend
    echo "Building frontend..."
    npm run build
    cd ..

    # Setup database
    echo -e "${YELLOW}Setting up database...${NC}"
    if command -v psql &> /dev/null; then
        echo "PostgreSQL found. Run the following to setup database:"
        echo "  psql -U postgres -f backend/setup_database.sql"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL not found. Please install and run:${NC}"
        echo "  psql -U postgres -f backend/setup_database.sql"
    fi

    # Create logs directory
    mkdir -p logs

    # Start with PM2
    echo -e "${YELLOW}Starting services with PM2...${NC}"

    # Check if PM2 is installed
    if ! command -v pm2 &> /dev/null; then
        echo -e "${YELLOW}Installing PM2...${NC}"
        npm install -g pm2
    fi

    # Start services
    pm2 start ecosystem.config.js --env production

    # Save PM2 process list
    pm2 save

    # Setup PM2 startup script
    pm2 startup

    echo -e "${GREEN}✅ PM2 deployment complete!${NC}"
    echo "Commands:"
    echo "  pm2 status        - Check service status"
    echo "  pm2 logs          - View logs"
    echo "  pm2 restart all   - Restart services"
    echo "  pm2 stop all      - Stop services"

else
    echo -e "${RED}Invalid deployment method. Use: ./deploy.sh [docker|pm2]${NC}"
    exit 1
fi

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"

# Health check
echo -e "${YELLOW}Running health check...${NC}"
sleep 5

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null || curl -s http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
fi