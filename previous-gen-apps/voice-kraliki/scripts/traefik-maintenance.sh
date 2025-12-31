#!/bin/bash
# ============================================================================
# Traefik Maintenance Script
# ============================================================================
# Utility script for common Traefik maintenance tasks
#
# Usage: ./scripts/traefik-maintenance.sh <command>
#
# Commands:
#   status       - Show service status
#   health       - Check health of all services
#   logs         - View recent logs
#   errors       - Show recent errors
#   restart      - Restart Traefik
#   rebuild      - Rebuild and restart all services
#   clean        - Clean up unused resources
#   backup       - Backup configuration and certificates
#   update       - Update Traefik to latest version
#   rotate-logs  - Rotate log files
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILES="-f $PROJECT_ROOT/docker-compose.yml -f $PROJECT_ROOT/docker-compose.traefik.yml"

print_header() {
    echo -e "${GREEN}============================================================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}============================================================================${NC}"
    echo ""
}

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Show service status
cmd_status() {
    print_header "Service Status"
    docker-compose $COMPOSE_FILES ps
    echo ""
    print_info "Use './scripts/traefik-maintenance.sh health' for detailed health checks"
}

# Check service health
cmd_health() {
    print_header "Service Health Checks"

    services=(
        "operator-traefik:Traefik"
        "operator-demo-backend:Backend API"
        "operator-demo-frontend:Frontend"
        "operator-demo-postgres:PostgreSQL"
        "operator-demo-redis:Redis"
        "operator-demo-qdrant:Qdrant"
    )

    for service in "${services[@]}"; do
        IFS=: read -r container_name display_name <<< "$service"

        if docker ps --format "{{.Names}}" | grep -q "^$container_name$"; then
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "unknown")
            if [ "$health" = "healthy" ]; then
                print_success "$display_name is healthy"
            elif [ "$health" = "unknown" ]; then
                print_warning "$display_name is running (no health check)"
            else
                print_error "$display_name is unhealthy: $health"
            fi
        else
            print_error "$display_name is not running"
        fi
    done

    echo ""
    print_info "Testing endpoints..."

    # Test endpoints
    endpoints=(
        "https://api.verduona.dev/health:Backend API"
        "https://operator.verduona.dev:Frontend"
        "https://traefik.verduona.dev/api/overview:Traefik Dashboard"
    )

    for endpoint in "${endpoints[@]}"; do
        IFS=: read -r url name <<< "$endpoint"
        if curl -k -f -s -o /dev/null "$url" 2>/dev/null; then
            print_success "$name is accessible"
        else
            print_error "$name is not accessible"
        fi
    done
}

# View recent logs
cmd_logs() {
    print_header "Recent Logs"
    docker-compose $COMPOSE_FILES logs --tail=50 --follow
}

# Show errors
cmd_errors() {
    print_header "Recent Errors"

    print_info "Traefik errors:"
    docker exec operator-traefik cat /var/log/traefik/traefik.log 2>/dev/null | jq -r 'select(.level=="error") | "\(.time) - \(.message)"' | tail -n 20 || echo "No errors found"

    echo ""
    print_info "Failed requests (HTTP 4xx/5xx):"
    docker exec operator-traefik tail -n 50 /var/log/traefik/access.log 2>/dev/null | grep -E '"(4[0-9]{2}|5[0-9]{2})"' || echo "No failed requests found"

    echo ""
    print_info "Backend errors:"
    docker logs operator-demo-backend 2>&1 | grep -i error | tail -n 20 || echo "No errors found"
}

# Restart Traefik
cmd_restart() {
    print_header "Restarting Traefik"
    docker-compose $COMPOSE_FILES restart traefik
    sleep 5
    print_success "Traefik restarted"
    cmd_health
}

# Rebuild services
cmd_rebuild() {
    print_header "Rebuilding Services"
    print_warning "This will rebuild all containers"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose $COMPOSE_FILES down
        docker-compose $COMPOSE_FILES build --no-cache
        docker-compose $COMPOSE_FILES up -d
        sleep 10
        print_success "Services rebuilt"
        cmd_health
    fi
}

# Clean up
cmd_clean() {
    print_header "Cleaning Up Resources"

    print_info "Removing stopped containers..."
    docker-compose $COMPOSE_FILES rm -f

    print_info "Pruning unused Docker resources..."
    docker system prune -f

    print_info "Removing unused volumes (excluding databases)..."
    docker volume prune -f --filter "label!=keep"

    print_success "Cleanup complete"
}

# Backup
cmd_backup() {
    print_header "Creating Backup"

    BACKUP_DIR="$PROJECT_ROOT/backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/traefik-backup-$TIMESTAMP.tar.gz"

    mkdir -p "$BACKUP_DIR"

    print_info "Backing up configuration..."
    tar -czf "$BACKUP_FILE" \
        -C "$PROJECT_ROOT" \
        traefik/ \
        docker-compose.yml \
        docker-compose.traefik.yml \
        docker-compose.prod.yml \
        .env.traefik \
        2>/dev/null

    print_info "Backing up Let's Encrypt certificates..."
    if docker volume ls | grep -q "traefik-letsencrypt"; then
        docker run --rm \
            -v traefik-letsencrypt:/data \
            -v "$BACKUP_DIR":/backup \
            alpine tar -czf "/backup/letsencrypt-$TIMESTAMP.tar.gz" -C /data .
    fi

    print_success "Backup created: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"

    # Keep only last 5 backups
    print_info "Cleaning old backups (keeping last 5)..."
    cd "$BACKUP_DIR" && ls -t traefik-backup-*.tar.gz | tail -n +6 | xargs -r rm
    cd "$BACKUP_DIR" && ls -t letsencrypt-*.tar.gz | tail -n +6 | xargs -r rm
}

# Update Traefik
cmd_update() {
    print_header "Updating Traefik"
    print_warning "This will pull the latest Traefik image and restart the service"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Pulling latest Traefik image..."
        docker-compose $COMPOSE_FILES pull traefik

        print_info "Restarting Traefik..."
        docker-compose $COMPOSE_FILES up -d traefik

        sleep 5
        print_success "Traefik updated"

        # Show version
        version=$(docker exec operator-traefik traefik version | head -n 1)
        print_info "Current version: $version"

        cmd_health
    fi
}

# Rotate logs
cmd_rotate_logs() {
    print_header "Rotating Logs"

    print_info "Rotating Docker logs..."
    docker-compose $COMPOSE_FILES logs --no-color --timestamps > "$PROJECT_ROOT/logs/docker-$(date +%Y%m%d).log" 2>&1

    print_info "Truncating container logs..."
    for container in $(docker-compose $COMPOSE_FILES ps -q); do
        docker inspect --format='{{.LogPath}}' "$container" | xargs -r truncate -s 0
    done

    print_info "Cleaning old log files (keeping last 7 days)..."
    find "$PROJECT_ROOT/logs" -name "docker-*.log" -mtime +7 -delete

    print_success "Log rotation complete"
}

# Show usage
cmd_help() {
    echo "Traefik Maintenance Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  status       - Show service status"
    echo "  health       - Check health of all services"
    echo "  logs         - View recent logs"
    echo "  errors       - Show recent errors"
    echo "  restart      - Restart Traefik"
    echo "  rebuild      - Rebuild and restart all services"
    echo "  clean        - Clean up unused resources"
    echo "  backup       - Backup configuration and certificates"
    echo "  update       - Update Traefik to latest version"
    echo "  rotate-logs  - Rotate log files"
    echo "  help         - Show this help message"
    echo ""
}

# Main
COMMAND="${1:-help}"

case "$COMMAND" in
    status)      cmd_status ;;
    health)      cmd_health ;;
    logs)        cmd_logs ;;
    errors)      cmd_errors ;;
    restart)     cmd_restart ;;
    rebuild)     cmd_rebuild ;;
    clean)       cmd_clean ;;
    backup)      cmd_backup ;;
    update)      cmd_update ;;
    rotate-logs) cmd_rotate_logs ;;
    help|*)      cmd_help ;;
esac
