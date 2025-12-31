#!/bin/bash
# ============================================================================
# Traefik Setup Script
# ============================================================================
# This script sets up Traefik reverse proxy for the operator-demo-multiprovider
# project. It handles both development (self-signed) and production (Let's Encrypt)
# configurations.
#
# Usage:
#   ./scripts/setup-traefik.sh [dev|prod]
#
# Arguments:
#   dev  - Set up for development with self-signed certificates (default)
#   prod - Set up for production with Let's Encrypt
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODE="${1:-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TRAEFIK_DIR="$PROJECT_ROOT/traefik"
CERTS_DIR="$TRAEFIK_DIR/certs"

# Functions
print_header() {
    echo ""
    echo -e "${GREEN}============================================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Validate mode
if [[ "$MODE" != "dev" && "$MODE" != "prod" ]]; then
    print_error "Invalid mode: $MODE"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

print_header "Traefik Setup Script - $MODE mode"

# Check if Docker is running
print_step "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check if docker-compose is available
print_step "Checking docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi
print_success "docker-compose is available"

# Create necessary directories
print_step "Creating directories..."
mkdir -p "$TRAEFIK_DIR/certs"
mkdir -p "$TRAEFIK_DIR/config"
chmod 755 "$TRAEFIK_DIR"
chmod 755 "$CERTS_DIR"
print_success "Directories created"

# Development mode setup
if [ "$MODE" = "dev" ]; then
    print_header "Development Mode Setup"

    # Generate self-signed certificates
    print_step "Generating self-signed certificates..."
    if [ -f "$CERTS_DIR/verduona.dev.crt" ] && [ -f "$CERTS_DIR/verduona.dev.key" ]; then
        print_warning "Certificates already exist. Skipping generation."
        read -p "Do you want to regenerate them? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            bash "$SCRIPT_DIR/generate-dev-certs.sh"
        fi
    else
        bash "$SCRIPT_DIR/generate-dev-certs.sh"
    fi

    # Add hostnames to /etc/hosts
    print_step "Checking /etc/hosts configuration..."
    HOSTS_ENTRIES=(
        "127.0.0.1 operator.verduona.dev"
        "127.0.0.1 api.verduona.dev"
        "127.0.0.1 docs.verduona.dev"
        "127.0.0.1 traefik.verduona.dev"
        "127.0.0.1 pgadmin.verduona.dev"
        "127.0.0.1 redis.verduona.dev"
    )

    MISSING_ENTRIES=()
    for entry in "${HOSTS_ENTRIES[@]}"; do
        if ! grep -q "$entry" /etc/hosts 2>/dev/null; then
            MISSING_ENTRIES+=("$entry")
        fi
    done

    if [ ${#MISSING_ENTRIES[@]} -gt 0 ]; then
        print_warning "Some hostnames are missing from /etc/hosts"
        echo ""
        echo "The following entries need to be added:"
        echo ""
        for entry in "${MISSING_ENTRIES[@]}"; do
            echo "  $entry"
        done
        echo ""
        read -p "Add these entries to /etc/hosts? (requires sudo) (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for entry in "${MISSING_ENTRIES[@]}"; do
                echo "$entry" | sudo tee -a /etc/hosts > /dev/null
                print_success "Added: $entry"
            done
        else
            print_warning "Skipping /etc/hosts update. You'll need to add these manually."
        fi
    else
        print_success "All hostnames are already in /etc/hosts"
    fi

    # Set development environment
    print_step "Setting environment variables..."
    export TRAEFIK_ENV=development
    print_success "Environment set to development"

    # Trust CA certificate
    print_step "Trust CA certificate..."
    echo ""
    print_warning "To avoid browser security warnings, you should trust the CA certificate."
    echo ""
    echo "Run ONE of these commands based on your system:"
    echo ""
    echo -e "${GREEN}macOS:${NC}"
    echo "  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $CERTS_DIR/ca.crt"
    echo ""
    echo -e "${GREEN}Linux (Ubuntu/Debian):${NC}"
    echo "  sudo cp $CERTS_DIR/ca.crt /usr/local/share/ca-certificates/operator-demo-ca.crt"
    echo "  sudo update-ca-certificates"
    echo ""
    echo -e "${GREEN}Firefox (any OS):${NC}"
    echo "  Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import"
    echo "  Then select: $CERTS_DIR/ca.crt"
    echo ""

# Production mode setup
else
    print_header "Production Mode Setup"

    print_step "Checking environment variables..."

    # Check for required environment variables
    if [ -z "$CF_API_EMAIL" ] || [ -z "$CF_DNS_API_TOKEN" ]; then
        print_warning "Cloudflare credentials not found in environment"
        echo ""
        echo "For Let's Encrypt DNS challenge, you need to set:"
        echo "  - CF_API_EMAIL"
        echo "  - CF_DNS_API_TOKEN"
        echo ""
        echo "You can set these in .env or .env.traefik file"
        echo ""
        read -p "Continue without Let's Encrypt? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Cloudflare credentials found"
    fi

    # Set production environment
    print_step "Setting environment variables..."
    export TRAEFIK_ENV=production
    print_success "Environment set to production"

    # Check DNS configuration
    print_step "Checking DNS configuration..."
    print_warning "Make sure your DNS records point to this server:"
    echo ""
    echo "  A    verduona.dev          → $(curl -s ifconfig.me)"
    echo "  A    *.verduona.dev        → $(curl -s ifconfig.me)"
    echo ""
    echo "Or individual records:"
    echo "  A    operator.verduona.dev → $(curl -s ifconfig.me)"
    echo "  A    api.verduona.dev      → $(curl -s ifconfig.me)"
    echo "  A    docs.verduona.dev     → $(curl -s ifconfig.me)"
    echo "  A    traefik.verduona.dev  → $(curl -s ifconfig.me)"
    echo ""
    read -p "Are your DNS records configured? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Please configure DNS records before starting Traefik"
        exit 1
    fi

    # Create Let's Encrypt storage
    print_step "Creating Let's Encrypt storage..."
    docker volume create traefik-letsencrypt
    print_success "Let's Encrypt storage created"
fi

# Start services
print_header "Starting Services"

print_step "Stopping existing containers..."
docker-compose -f "$PROJECT_ROOT/docker-compose.yml" -f "$PROJECT_ROOT/docker-compose.traefik.yml" down
print_success "Existing containers stopped"

print_step "Building containers..."
docker-compose -f "$PROJECT_ROOT/docker-compose.yml" -f "$PROJECT_ROOT/docker-compose.traefik.yml" build
print_success "Containers built"

print_step "Starting containers..."
docker-compose -f "$PROJECT_ROOT/docker-compose.yml" -f "$PROJECT_ROOT/docker-compose.traefik.yml" up -d
print_success "Containers started"

# Wait for services to be healthy
print_step "Waiting for services to be healthy..."
sleep 10

# Check service health
print_step "Checking service health..."
services=("operator-traefik" "operator-demo-backend" "operator-demo-frontend")
all_healthy=true

for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "health=healthy" --format "{{.Names}}" | grep -q "$service"; then
        print_success "$service is healthy"
    else
        print_warning "$service is not healthy yet"
        all_healthy=false
    fi
done

# Final output
print_header "Setup Complete!"

if [ "$MODE" = "dev" ]; then
    echo -e "${GREEN}Development environment is ready!${NC}"
    echo ""
    echo "You can now access:"
    echo ""
    echo "  Frontend:   https://operator.verduona.dev"
    echo "  Backend:    https://api.verduona.dev"
    echo "  Docs:       https://docs.verduona.dev"
    echo "  Dashboard:  https://traefik.verduona.dev (admin/admin)"
    echo ""
    echo "Optional admin tools (start with --profile admin-tools):"
    echo "  pgAdmin:    https://pgadmin.verduona.dev"
    echo "  Redis:      https://redis.verduona.dev"
    echo ""
else
    echo -e "${GREEN}Production environment is ready!${NC}"
    echo ""
    echo "Services are available at:"
    echo ""
    echo "  Frontend:   https://operator.verduona.dev"
    echo "  Backend:    https://api.verduona.dev"
    echo "  Docs:       https://docs.verduona.dev"
    echo "  Dashboard:  https://traefik.verduona.dev"
    echo ""
fi

echo "View logs:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.traefik.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.traefik.yml down"
echo ""

if [ "$all_healthy" = true ]; then
    print_success "All services are healthy!"
else
    print_warning "Some services are not healthy yet. Check logs for details."
fi

echo ""
