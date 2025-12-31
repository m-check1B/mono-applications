#!/bin/bash
set -e

# Voice by Kraliki Production Setup Script
# This script prepares the production environment

echo "🚀 Voice by Kraliki Production Setup"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}❌ Do not run this script as root${NC}"
  exit 1
fi

# Step 1: Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is not installed${NC}"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose is not installed${NC}"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo -e "${RED}❌ pnpm is not installed${NC}"; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo -e "${RED}❌ openssl is not installed${NC}"; exit 1; }

echo -e "${GREEN}✅ All prerequisites installed${NC}"

# Step 2: Create directory structure
echo -e "\n${YELLOW}📁 Creating directory structure...${NC}"

sudo mkdir -p /opt/cc-lite/{data,logs,backups,uploads,cache}/{postgres,redis,app,nginx,prometheus,grafana,loki}
sudo chown -R $(whoami):$(whoami) /opt/cc-lite

echo -e "${GREEN}✅ Directory structure created${NC}"

# Step 3: Check for .env.production
echo -e "\n${YELLOW}🔐 Checking environment configuration...${NC}"

if [ ! -f .env.production ]; then
  echo -e "${YELLOW}⚠️  .env.production not found. Copying template...${NC}"
  cp .env.production.template .env.production
  echo -e "${RED}❌ CRITICAL: Edit .env.production and replace all CHANGE_ME values!${NC}"
  echo -e "${YELLOW}📝 Opening .env.production for editing...${NC}"
  sleep 2
  ${EDITOR:-nano} .env.production
else
  echo -e "${GREEN}✅ .env.production exists${NC}"
fi

# Step 4: Validate environment file
echo -e "\n${YELLOW}🔍 Validating environment configuration...${NC}"

if grep -q "CHANGE_ME" .env.production 2>/dev/null; then
  echo -e "${RED}❌ WARNING: .env.production contains CHANGE_ME placeholders!${NC}"
  echo -e "${YELLOW}Please edit .env.production before continuing.${NC}"
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
else
  echo -e "${GREEN}✅ No CHANGE_ME placeholders found${NC}"
fi

# Step 5: Generate secrets if missing
echo -e "\n${YELLOW}🔑 Generating missing secrets...${NC}"

pnpm run secrets:generate || echo -e "${YELLOW}⚠️  secrets:generate script not found, skipping${NC}"

# Step 6: Create Docker secrets
echo -e "\n${YELLOW}🐳 Setting up Docker secrets...${NC}"

# Source environment file
set -a
source .env.production
set +a

# Create secrets directory if it doesn't exist
mkdir -p ./secrets

# Function to create Docker secret
create_secret() {
  local secret_name=$1
  local secret_value=$2

  if [ -z "$secret_value" ] || [ "$secret_value" = "CHANGE_ME"* ]; then
    echo -e "${YELLOW}⚠️  Skipping $secret_name (not set)${NC}"
    return
  fi

  # Check if secret already exists
  if docker secret inspect $secret_name >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Secret $secret_name already exists, skipping${NC}"
  else
    echo "$secret_value" | docker secret create $secret_name - 2>/dev/null && \
      echo -e "${GREEN}✅ Created secret: $secret_name${NC}" || \
      echo -e "${YELLOW}⚠️  Failed to create secret: $secret_name${NC}"
  fi
}

# Create all required secrets
create_secret "cc_lite_jwt_secret" "$JWT_SECRET"
create_secret "cc_lite_jwt_refresh_secret" "$JWT_REFRESH_SECRET"
create_secret "cc_lite_db_password" "$DATABASE_URL" # Extract password from URL
create_secret "cc_lite_redis_password" "$REDIS_PASSWORD"
create_secret "cc_lite_session_secret" "$SESSION_SECRET"
create_secret "cc_lite_cookie_secret" "$COOKIE_SECRET"
create_secret "cc_lite_twilio_auth_token" "$TWILIO_AUTH_TOKEN"
create_secret "cc_lite_openai_api_key" "$OPENAI_API_KEY"
create_secret "cc_lite_deepgram_api_key" "$DEEPGRAM_API_KEY"

# Step 7: Install dependencies
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"

pnpm install --frozen-lockfile

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 8: Generate Prisma client
echo -e "\n${YELLOW}🗄️  Generating Prisma client...${NC}"

pnpm prisma generate

echo -e "${GREEN}✅ Prisma client generated${NC}"

# Step 9: Build application
echo -e "\n${YELLOW}🔨 Building application...${NC}"

pnpm build

echo -e "${GREEN}✅ Application built${NC}"

# Step 10: Setup instructions
echo -e "\n${GREEN}✅ Production setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review .env.production and ensure all secrets are set"
echo "2. Run database migrations: pnpm prisma migrate deploy"
echo "3. Start services: docker compose -f infra/docker/production.yml up -d"
echo "4. Check logs: docker compose -f infra/docker/production.yml logs -f"
echo "5. Access application at: https://beta.cc-lite.yourdomain.com"
echo ""
echo -e "${YELLOW}Monitoring:${NC}"
echo "- PM2 Dashboard: pm2 monit"
echo "- Docker Status: docker compose -f infra/docker/production.yml ps"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"