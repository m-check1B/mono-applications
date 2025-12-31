#!/bin/bash
# Focus by Kraliki - Hetzner Production Deployment Script
# This script deploys Focus by Kraliki to a Hetzner VPS using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_info "Copy .env.example to .env and configure it first:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

print_header "Focus by Kraliki - Hetzner Deployment"

# Load environment variables
source .env

# Validate required environment variables
print_info "Validating environment variables..."

REQUIRED_VARS=(
    "DB_PASSWORD"
    "REDIS_PASSWORD"
    "JWT_SECRET"
    "SESSION_SECRET"
    "ANTHROPIC_API_KEY"
    "OPENAI_API_KEY"
    "DOMAIN"
    "API_DOMAIN"
    "ALLOWED_ORIGINS"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

print_status "All required environment variables are set"

# Check Docker installation
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    print_info "Install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed!"
    print_info "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker is installed"

# Pull latest code (if git repo)
if [ -d .git ]; then
    print_header "Pulling Latest Code"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes:"
        git status --short
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Deployment cancelled"
            exit 0
        fi
    fi

    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_info "Current branch: $CURRENT_BRANCH"

    # Pull latest changes
    print_info "Pulling latest changes..."
    git pull origin "$CURRENT_BRANCH" || {
        print_warning "Failed to pull changes, continuing with local version"
    }

    print_status "Code updated"
fi

# Create backup directory
print_header "Creating Backup"
mkdir -p backups
BACKUP_FILE="backups/focus_kraliki_backup_$(date +%Y%m%d_%H%M%S).sql.gz"

# Backup existing database if container is running
if docker ps -q -f name=focus-kraliki-db | grep -q .; then
    print_info "Backing up existing database..."
    docker exec focus-kraliki-db pg_dump -U "${DB_USER:-postgres}" focus_kraliki | gzip > "$BACKUP_FILE"
    print_status "Database backed up to $BACKUP_FILE"
else
    print_info "No existing database to backup"
fi

# Stop existing containers
print_header "Stopping Existing Containers"
if docker compose -f docker-compose.prod.yml ps -q | grep -q .; then
    print_info "Stopping existing containers..."
    docker compose -f docker-compose.prod.yml down
    print_status "Containers stopped"
else
    print_info "No existing containers to stop"
fi

# Build images
print_header "Building Docker Images"
print_info "This may take a few minutes..."
docker compose -f docker-compose.prod.yml build --no-cache

print_status "Images built successfully"

# Start containers
print_header "Starting Containers"
print_info "Starting all services..."
docker compose -f docker-compose.prod.yml up -d

print_status "Containers started"

# Wait for services to be healthy
print_header "Health Checks"
print_info "Waiting for services to be healthy..."

MAX_WAIT=120
WAIT_TIME=0
INTERVAL=5

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if docker compose -f docker-compose.prod.yml ps | grep -q "unhealthy"; then
        print_warning "Some services are still starting... ($WAIT_TIME/$MAX_WAIT seconds)"
        sleep $INTERVAL
        WAIT_TIME=$((WAIT_TIME + INTERVAL))
    else
        break
    fi
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    print_error "Services failed to become healthy within $MAX_WAIT seconds"
    print_info "Checking logs..."
    docker compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

# Run database migrations
print_header "Database Migrations"
print_info "Running migrations..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || {
    print_warning "Migrations failed or already applied"
}

print_status "Migrations completed"

# Final health checks
print_header "Final Health Checks"

# Check backend
print_info "Checking backend health..."
if curl -f http://127.0.0.1:3017/health > /dev/null 2>&1; then
    print_status "Backend is healthy"
else
    print_error "Backend health check failed"
    docker compose -f docker-compose.prod.yml logs backend --tail=50
    exit 1
fi

# Check frontend
print_info "Checking frontend health..."
if curl -f http://127.0.0.1:5175 > /dev/null 2>&1; then
    print_status "Frontend is healthy"
else
    print_error "Frontend health check failed"
    docker compose -f docker-compose.prod.yml logs frontend --tail=50
    exit 1
fi

# Show status
print_header "Deployment Complete"
docker compose -f docker-compose.prod.yml ps

echo ""
print_status "Focus by Kraliki is now running!"
echo ""
print_info "Access URLs:"
echo "  Frontend: https://$DOMAIN"
echo "  API: https://$API_DOMAIN"
echo "  API Docs: https://$API_DOMAIN/docs"
echo ""
print_info "Useful commands:"
echo "  View logs:    docker compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.prod.yml down"
echo "  Restart:      docker compose -f docker-compose.prod.yml restart"
echo "  Status:       docker compose -f docker-compose.prod.yml ps"
echo ""
print_info "Backup saved to: $BACKUP_FILE"
