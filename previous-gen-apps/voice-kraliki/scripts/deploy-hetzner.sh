#!/bin/bash

# =============================================================================
# Hetzner Deployment Script for Operator Demo 2026
# =============================================================================
# This script automates the deployment process on Hetzner Cloud servers
#
# Usage:
#   ./scripts/deploy-hetzner.sh [command]
#
# Commands:
#   init       - Initial setup (first time deployment)
#   deploy     - Deploy/update application
#   restart    - Restart all services
#   stop       - Stop all services
#   logs       - View application logs
#   backup     - Create database backup
#   status     - Check service status
#   cleanup    - Clean up old Docker images and containers
#
# Prerequisites:
#   - Docker and Docker Compose installed
#   - .env.production file configured
#   - Git repository cloned
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="operator-demo-2026"
COMPOSE_FILE="docker-compose.hetzner.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# =============================================================================
# Helper Functions
# =============================================================================

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=============================================================================="
    echo " $1"
    echo "=============================================================================="
    echo ""
}

check_requirements() {
    print_info "Checking requirements..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if .env.production exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error "$ENV_FILE not found!"
        print_info "Please copy .env.production.template to .env.production and configure it."
        exit 1
    fi

    print_success "All requirements met!"
}

generate_secrets() {
    print_header "Generating Secure Secrets"

    echo "This will generate secure random secrets for your deployment."
    echo ""
    echo "POSTGRES_PASSWORD (32 chars):"
    openssl rand -base64 32
    echo ""
    echo "REDIS_PASSWORD (32 chars):"
    openssl rand -base64 32
    echo ""
    echo "SECRET_KEY (64 chars):"
    openssl rand -base64 64
    echo ""
    print_warning "Copy these values to your $ENV_FILE file!"
}

# =============================================================================
# Deployment Commands
# =============================================================================

cmd_init() {
    print_header "Initial Setup for Hetzner Deployment"

    check_requirements

    # Create necessary directories
    print_info "Creating directories..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p backend/uploads
    mkdir -p backend/keys

    # Set proper permissions
    print_info "Setting permissions..."
    chmod 755 "$BACKUP_DIR"
    chmod 755 "$LOG_DIR"
    chmod 755 backend/uploads
    chmod 700 backend/keys
    chmod 600 "$ENV_FILE"

    # Generate secrets if needed
    print_info "Need to generate secrets? (y/n)"
    read -r generate
    if [[ "$generate" == "y" ]]; then
        generate_secrets
        print_warning "Please update $ENV_FILE with the generated secrets before continuing."
        exit 0
    fi

    # Pull Docker images
    print_info "Pulling Docker images..."
    docker compose -f "$COMPOSE_FILE" pull

    # Build images
    print_info "Building Docker images..."
    docker compose -f "$COMPOSE_FILE" build --no-cache

    # Start services
    print_info "Starting services..."
    docker compose -f "$COMPOSE_FILE" up -d

    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10

    # Run database migrations
    print_info "Running database migrations..."
    docker compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head || true

    # Create initial admin user (optional)
    print_info "Do you want to create an admin user? (y/n)"
    read -r create_admin
    if [[ "$create_admin" == "y" ]]; then
        docker compose -f "$COMPOSE_FILE" exec backend python -m app.scripts.create_admin || true
    fi

    print_success "Initial setup completed!"
    print_info "Your application should now be running. Check status with: ./scripts/deploy-hetzner.sh status"
}

cmd_deploy() {
    print_header "Deploying Application Update"

    check_requirements

    # Pull latest code (if in git repo)
    if [ -d .git ]; then
        print_info "Pulling latest code from git..."
        git pull origin develop || print_warning "Git pull failed, continuing anyway..."
    fi

    # Pull latest Docker images
    print_info "Pulling latest Docker images..."
    docker compose -f "$COMPOSE_FILE" pull

    # Build images
    print_info "Building Docker images..."
    docker compose -f "$COMPOSE_FILE" build

    # Create backup before deployment
    print_info "Creating pre-deployment backup..."
    cmd_backup

    # Deploy with zero-downtime (recreate containers)
    print_info "Deploying services..."
    docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

    # Run migrations
    print_info "Running database migrations..."
    docker compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head || print_warning "Migration failed"

    # Clean up old images
    print_info "Cleaning up old Docker images..."
    docker image prune -f

    print_success "Deployment completed!"
    cmd_status
}

cmd_restart() {
    print_header "Restarting Services"

    print_info "Restarting all services..."
    docker compose -f "$COMPOSE_FILE" restart

    print_success "Services restarted!"
    sleep 3
    cmd_status
}

cmd_stop() {
    print_header "Stopping Services"

    print_warning "This will stop all services. Continue? (y/n)"
    read -r confirm
    if [[ "$confirm" != "y" ]]; then
        print_info "Aborted."
        exit 0
    fi

    print_info "Stopping all services..."
    docker compose -f "$COMPOSE_FILE" down

    print_success "All services stopped."
}

cmd_logs() {
    print_header "Application Logs"

    if [ -n "$2" ]; then
        # Show logs for specific service
        print_info "Showing logs for $2..."
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100 "$2"
    else
        # Show logs for all services
        print_info "Showing logs for all services (Ctrl+C to exit)..."
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100
    fi
}

cmd_backup() {
    print_header "Creating Database Backup"

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"

    print_info "Creating backup: $BACKUP_FILE"

    # Create backup
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U postgres operator_demo > "$BACKUP_FILE"

    # Compress backup
    print_info "Compressing backup..."
    gzip "$BACKUP_FILE"

    # Remove old backups (keep last 30 days)
    print_info "Removing old backups (older than 30 days)..."
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete

    print_success "Backup created: ${BACKUP_FILE}.gz"

    # Show backup size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    print_info "Backup size: $BACKUP_SIZE"
}

cmd_status() {
    print_header "Service Status"

    # Show Docker container status
    docker compose -f "$COMPOSE_FILE" ps

    echo ""
    print_info "Health Checks:"

    # Check backend health
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend: Healthy (http://localhost:8000)"
    else
        print_error "Backend: Unhealthy"
    fi

    # Check frontend health
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend: Healthy (http://localhost:3000)"
    else
        print_error "Frontend: Unhealthy"
    fi

    echo ""
    print_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

cmd_cleanup() {
    print_header "Cleaning Up Docker Resources"

    print_warning "This will remove unused Docker images, containers, and networks. Continue? (y/n)"
    read -r confirm
    if [[ "$confirm" != "y" ]]; then
        print_info "Aborted."
        exit 0
    fi

    print_info "Cleaning up unused Docker resources..."

    # Remove stopped containers
    docker container prune -f

    # Remove unused images
    docker image prune -a -f

    # Remove unused volumes (be careful!)
    print_warning "Remove unused volumes? This could delete data! (y/n)"
    read -r confirm_volumes
    if [[ "$confirm_volumes" == "y" ]]; then
        docker volume prune -f
    fi

    # Remove unused networks
    docker network prune -f

    print_success "Cleanup completed!"

    # Show disk space
    print_info "Docker disk usage:"
    docker system df
}

cmd_help() {
    cat << EOF
Hetzner Deployment Script for Operator Demo 2026

Usage:
  ./scripts/deploy-hetzner.sh [command]

Commands:
  init       - Initial setup (first time deployment)
  deploy     - Deploy/update application
  restart    - Restart all services
  stop       - Stop all services
  logs       - View application logs (add service name for specific logs)
  backup     - Create database backup
  status     - Check service status
  cleanup    - Clean up old Docker images and containers
  help       - Show this help message

Examples:
  ./scripts/deploy-hetzner.sh init             # First time setup
  ./scripts/deploy-hetzner.sh deploy           # Deploy updates
  ./scripts/deploy-hetzner.sh logs backend     # View backend logs
  ./scripts/deploy-hetzner.sh backup           # Create backup

Prerequisites:
  - Docker and Docker Compose installed
  - .env.production file configured
  - Proper firewall rules configured

For more information, see DEPLOYMENT_HETZNER.md

EOF
}

# =============================================================================
# Main Script Logic
# =============================================================================

case "${1:-help}" in
    init)
        cmd_init
        ;;
    deploy)
        cmd_deploy
        ;;
    restart)
        cmd_restart
        ;;
    stop)
        cmd_stop
        ;;
    logs)
        cmd_logs "$@"
        ;;
    backup)
        cmd_backup
        ;;
    status)
        cmd_status
        ;;
    cleanup)
        cmd_cleanup
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac

exit 0
