#!/usr/bin/env bash
# =============================================================================
# Voice by Kraliki - Production Deployment Script
# =============================================================================
#
# Usage:
#   ./deploy.sh              # Deploy/update the application
#   ./deploy.sh --build      # Force rebuild images
#   ./deploy.sh --logs       # Show logs after deployment
#   ./deploy.sh --restart    # Restart all services
#   ./deploy.sh --status     # Show service status
#   ./deploy.sh --down       # Stop all services
#
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.prod.yml"
ENV_FILE="${SCRIPT_DIR}/.env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose v2 is not available"
        exit 1
    fi

    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Copy .env.production.template to .env.production and fill in secrets"
        exit 1
    fi

    # Validate required secrets
    source "$ENV_FILE"

    if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
        log_error "POSTGRES_PASSWORD is not set in $ENV_FILE"
        exit 1
    fi

    if [[ -z "${REDIS_PASSWORD:-}" ]]; then
        log_error "REDIS_PASSWORD is not set in $ENV_FILE"
        exit 1
    fi

    if [[ -z "${SECRET_KEY:-}" ]]; then
        log_error "SECRET_KEY is not set in $ENV_FILE"
        exit 1
    fi

    # Check Traefik network
    if ! docker network inspect websites_default &> /dev/null; then
        log_warning "Traefik network 'websites_default' does not exist"
        log_info "Creating network..."
        docker network create websites_default
    fi

    log_success "All prerequisites met"
}

build_images() {
    log_info "Building Docker images..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
    log_success "Images built successfully"
}

deploy() {
    log_info "Deploying Voice by Kraliki production..."
    cd "$PROJECT_DIR"

    # Pull latest base images
    log_info "Pulling base images..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull --ignore-pull-failures || true

    # Start services
    log_info "Starting services..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    # Wait for health checks
    log_info "Waiting for services to become healthy..."
    sleep 10

    show_status
}

show_status() {
    log_info "Service status:"
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

    echo ""
    log_info "Health status:"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps --format "table {{.Name}}\t{{.Status}}"
}

show_logs() {
    log_info "Showing logs (Ctrl+C to exit)..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f
}

restart_services() {
    log_info "Restarting all services..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" restart
    log_success "Services restarted"
    show_status
}

stop_services() {
    log_info "Stopping all services..."
    cd "$PROJECT_DIR"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    log_success "Services stopped"
}

# Parse arguments
BUILD=false
LOGS=false
RESTART=false
STATUS=false
DOWN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --logs)
            LOGS=true
            shift
            ;;
        --restart)
            RESTART=true
            shift
            ;;
        --status)
            STATUS=true
            shift
            ;;
        --down)
            DOWN=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Usage: $0 [--build] [--logs] [--restart] [--status] [--down]"
            exit 1
            ;;
    esac
done

# Main execution
echo ""
echo "==================================================="
echo "  Voice by Kraliki - Production Deployment"
echo "==================================================="
echo ""

check_prerequisites

if [[ "$DOWN" == true ]]; then
    stop_services
    exit 0
fi

if [[ "$STATUS" == true ]]; then
    show_status
    exit 0
fi

if [[ "$RESTART" == true ]]; then
    restart_services
    exit 0
fi

if [[ "$BUILD" == true ]]; then
    build_images
fi

deploy

if [[ "$LOGS" == true ]]; then
    show_logs
fi

echo ""
log_success "Deployment complete!"
echo ""
echo "Production URL: https://voice.kraliki.com"
echo "Beta URL:       https://voice.verduona.dev"
echo "API Docs:       https://voice.kraliki.com/docs"
echo ""
