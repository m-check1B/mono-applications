#!/bin/bash
set -e

# Voice by Kraliki Quick Deploy to verduona.dev
# This script deploys Voice by Kraliki with Docker + Host Nginx

echo "🚀 Voice by Kraliki Quick Deploy for verduona.dev"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cc-lite.verduona.dev"
APP_DIR="/home/adminmatej/github/apps/cc-lite"

cd $APP_DIR

# Step 1: Install/verify host Nginx
echo -e "\n${YELLOW}📦 Step 1: Check Host Nginx${NC}"
if ! command -v nginx >/dev/null 2>&1; then
    echo -e "${YELLOW}Installing Nginx...${NC}"
    sudo apt-get update
    sudo apt-get install -y nginx certbot python3-certbot-nginx
else
    echo -e "${GREEN}✅ Nginx already installed${NC}"
fi

# Step 2: Setup SSL certificate
echo -e "\n${YELLOW}🔒 Step 2: Setup SSL Certificate${NC}"
if [ ! -f /etc/letsencrypt/live/verduona.dev/fullchain.pem ]; then
    echo -e "${YELLOW}Getting SSL certificate for $DOMAIN...${NC}"
    echo -e "${YELLOW}This will ask you some questions...${NC}"
    sudo certbot certonly --nginx -d $DOMAIN
else
    echo -e "${GREEN}✅ SSL certificate exists${NC}"
fi

# Step 3: Configure host Nginx
echo -e "\n${YELLOW}⚙️  Step 3: Configure Host Nginx${NC}"
sudo cp deploy/host-nginx/cc-lite.verduona.dev.conf /etc/nginx/sites-available/$DOMAIN
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx configured${NC}"

# Step 4: Create .env.production if not exists
echo -e "\n${YELLOW}📝 Step 4: Environment Configuration${NC}"
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating .env.production from template...${NC}"
    cp .env.production.template .env.production

    # Auto-configure domain
    sed -i "s|https://beta.cc-lite.yourdomain.com|https://$DOMAIN|g" .env.production
    sed -i "s|beta.cc-lite.yourdomain.com|$DOMAIN|g" .env.production

    echo -e "${RED}⚠️  IMPORTANT: Edit .env.production and add your credentials!${NC}"
    echo -e "${YELLOW}Press Enter when ready to continue...${NC}"
    read
else
    echo -e "${GREEN}✅ .env.production exists${NC}"
fi

# Step 5: Create data directories
echo -e "\n${YELLOW}📁 Step 5: Create Data Directories${NC}"
sudo mkdir -p /opt/cc-lite/{data,logs,backups,uploads}/{postgres,redis,app}
sudo chown -R $(whoami):$(whoami) /opt/cc-lite
echo -e "${GREEN}✅ Directories created${NC}"

# Step 6: Build and start with Docker Compose
echo -e "\n${YELLOW}🐳 Step 6: Docker Compose Build & Start${NC}"

# Use simplified docker-compose for host nginx setup
cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: cc-lite-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: cc_light
      POSTGRES_USER: cc_lite_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme123}
    volumes:
      - /opt/cc-lite/data/postgres:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cc_lite_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: cc-lite-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD:-changeme456}
    volumes:
      - /opt/cc-lite/data/redis:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cc-lite-app
    restart: unless-stopped
    env_file:
      - .env.production
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://cc_lite_user:${DB_PASSWORD:-changeme123}@postgres:5432/cc_light
      REDIS_URL: redis://:${REDIS_PASSWORD:-changeme456}@redis:6379
    volumes:
      - /opt/cc-lite/logs/app:/app/logs
      - /opt/cc-lite/uploads:/app/uploads
    ports:
      - "127.0.0.1:3007:3007"
      - "127.0.0.1:3010:3010"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3010/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

echo -e "${GREEN}✅ Created simplified docker-compose.simple.yml${NC}"

# Install dependencies and build
pnpm install --frozen-lockfile
pnpm prisma generate
pnpm build

# Start services
docker compose -f docker-compose.simple.yml up -d --build

echo -e "${GREEN}✅ Docker containers started${NC}"

# Step 7: Run database migrations
echo -e "\n${YELLOW}🗄️  Step 7: Database Migrations${NC}"
sleep 10  # Wait for DB to be ready
pnpm prisma migrate deploy
echo -e "${GREEN}✅ Migrations complete${NC}"

# Step 8: Verify deployment
echo -e "\n${YELLOW}✅ Step 8: Verify Deployment${NC}"

sleep 5

# Check services
docker compose -f docker-compose.simple.yml ps

# Check health
if curl -sf http://localhost:3010/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -sf http://localhost:3007 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend not accessible${NC}"
fi

# Test HTTPS
if curl -sf https://$DOMAIN/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ HTTPS is working${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS not responding yet (may need a moment)${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "          DEPLOYMENT COMPLETE! 🎉"
echo "=========================================="
echo ""
echo "📍 Application URL: https://$DOMAIN"
echo "🔍 Health Check: https://$DOMAIN/health"
echo "📊 API: https://$DOMAIN/api"
echo ""
echo "📝 Default Test Account:"
echo "   Email: test.assistant@stack2025.com"
echo "   Password: Stack2025!Test@Assistant#Secure$2024"
echo ""
echo "🐛 Bug Reports: Built-in (bottom-right corner)"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:    docker compose -f docker-compose.simple.yml logs -f"
echo "   Restart:      docker compose -f docker-compose.simple.yml restart"
echo "   Stop:         docker compose -f docker-compose.simple.yml down"
echo "   Update:       git pull && bash deploy/QUICK_DEPLOY.sh"
echo ""
echo "🤖 AI Agent Testing:"
echo "   Direct OpenAI/Claude agents to: https://$DOMAIN"
echo "   They can click, fill forms, and provide feedback"
echo ""
echo -e "${GREEN}✅ Ready for beta testing!${NC}"