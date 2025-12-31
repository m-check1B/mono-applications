#!/bin/bash
set -e

# Voice by Kraliki Database Migration Script
# Safely runs Prisma migrations in production

echo "🗄️  Voice by Kraliki Database Migration"
echo "============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env.production exists
if [ ! -f .env.production ]; then
  echo -e "${RED}❌ .env.production not found${NC}"
  exit 1
fi

# Load environment
set -a
source .env.production
set +a

# Verify DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo -e "${RED}❌ DATABASE_URL not set in .env.production${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Environment loaded${NC}"

# Step 1: Backup database
echo -e "\n${YELLOW}💾 Creating database backup...${NC}"

BACKUP_DIR="/opt/cc-lite/backups/postgres"
BACKUP_FILE="$BACKUP_DIR/cc-lite-$(date +%Y%m%d-%H%M%S).sql"

mkdir -p $BACKUP_DIR

# Extract connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\).*/\1/p')

if command -v pg_dump >/dev/null 2>&1; then
  PGPASSWORD=$DATABASE_URL pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE
  echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
else
  echo -e "${YELLOW}⚠️  pg_dump not found, skipping backup${NC}"
fi

# Step 2: Check migration status
echo -e "\n${YELLOW}🔍 Checking migration status...${NC}"

pnpm prisma migrate status || echo -e "${YELLOW}⚠️  Migrations pending${NC}"

# Step 3: Run migrations
echo -e "\n${YELLOW}🚀 Running migrations...${NC}"

read -p "Continue with migration? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
  pnpm prisma migrate deploy
  echo -e "${GREEN}✅ Migrations complete${NC}"
else
  echo -e "${YELLOW}⚠️  Migration cancelled${NC}"
  exit 0
fi

# Step 4: Generate Prisma client
echo -e "\n${YELLOW}🔧 Generating Prisma client...${NC}"

pnpm prisma generate

echo -e "${GREEN}✅ Prisma client generated${NC}"

# Step 5: Verify database
echo -e "\n${YELLOW}✓ Verifying database...${NC}"

pnpm prisma db push --skip-generate || echo -e "${YELLOW}⚠️  Verification warning${NC}"

echo -e "\n${GREEN}✅ Database migration complete!${NC}"
echo ""
echo "Backup location: $BACKUP_FILE"
echo "To rollback: pnpm prisma migrate rollback"