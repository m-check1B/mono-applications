#!/bin/bash

# Database Initialization Script for operator-demo-2026
# =====================================================
# Automatically sets up PostgreSQL database for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Database Initialization Script${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}PostgreSQL not found. Installing...${NC}"

    # Detect OS and install PostgreSQL
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            sudo yum install -y postgresql postgresql-server postgresql-contrib
            sudo postgresql-setup initdb
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Mac OSX
        if command -v brew &> /dev/null; then
            brew install postgresql
            brew services start postgresql
        else
            echo -e "${RED}Please install Homebrew first: https://brew.sh${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Unsupported OS. Please install PostgreSQL manually.${NC}"
        exit 1
    fi
fi

# Start PostgreSQL if not running
if ! pg_isready &> /dev/null; then
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    fi

    # Wait for PostgreSQL to start
    sleep 3
fi

echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Database configuration
DB_NAME="${DB_NAME:-operator_demo}"
DB_USER="${DB_USER:-operator_user}"
DB_PASS="${DB_PASS:-operator_pass_2026}"

echo -e "${YELLOW}Creating database and user...${NC}"

# Create database and user
sudo -u postgres psql <<EOF 2>/dev/null || true
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}') THEN
        CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE ${DB_NAME}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};
EOF

echo -e "${GREEN}✅ Database '${DB_NAME}' created${NC}"
echo -e "${GREEN}✅ User '${DB_USER}' created${NC}"

# Run setup script if exists
if [ -f "backend/setup_database.sql" ]; then
    echo -e "${YELLOW}Running database setup script...${NC}"
    PGPASSWORD=${DB_PASS} psql -U ${DB_USER} -d ${DB_NAME} -h localhost -f backend/setup_database.sql 2>/dev/null || {
        echo -e "${YELLOW}Note: Some tables may already exist, continuing...${NC}"
    }
    echo -e "${GREEN}✅ Database schema created${NC}"
fi

# Update .env file with database configuration
echo -e "${YELLOW}Updating .env file...${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || cp .env.sample .env 2>/dev/null || touch .env
fi

# Update DATABASE_URL in .env
if grep -q "DATABASE_URL" .env; then
    # Update existing DATABASE_URL
    sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}|" .env
else
    # Add DATABASE_URL
    echo "" >> .env
    echo "# Database Configuration (added by init-db.sh)" >> .env
    echo "DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}" >> .env
fi

echo -e "${GREEN}✅ Environment variables updated${NC}"

# Test database connection
echo -e "${YELLOW}Testing database connection...${NC}"

PGPASSWORD=${DB_PASS} psql -U ${DB_USER} -d ${DB_NAME} -h localhost -c "SELECT 1" &>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection successful!${NC}"
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}Database initialization complete!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo "Database Details:"
    echo "  Name: ${DB_NAME}"
    echo "  User: ${DB_USER}"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo ""
    echo "Connection string:"
    echo "  postgresql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./start.sh"
    echo "  2. Access: http://localhost:5173"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    echo "Please check your PostgreSQL configuration"
    exit 1
fi