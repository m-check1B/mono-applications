#!/bin/bash
# Voice by Kraliki Zero-Downtime Deployment Script
# ========================================
# Implements blue-green deployment strategy for production
# Ensures zero downtime during application updates

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/infra/docker/production.yml"
NEW_IMAGE_TAG="${NEW_IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
HEALTH_CHECK_TIMEOUT="${HEALTH_CHECK_TIMEOUT:-300}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-5}"

# Functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Function to check if service is healthy
check_service_health() {
    local service_name=$1
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1

    log "Checking health of service: $service_name"

    while [ $attempt -le $max_attempts ]; do
        if docker compose -f "$COMPOSE_FILE" ps "$service_name" | grep -q "healthy"; then
            success "Service $service_name is healthy"
            return 0
        fi

        log "Attempt $attempt/$max_attempts - Service $service_name not healthy yet, waiting..."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done

    error "Service $service_name failed to become healthy within $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

# Function to check application endpoint
check_application_endpoint() {
    local url="http://127.0.0.1:3010/health"
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1

    log "Checking application endpoint: $url"

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" >/dev/null 2>&1; then
            success "Application endpoint is responding"
            return 0
        fi

        log "Attempt $attempt/$max_attempts - Endpoint not responding yet, waiting..."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done

    error "Application endpoint failed to respond within $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

# Function to create database backup before deployment
create_backup() {
    log "Creating database backup before deployment..."

    # Run backup service
    docker compose -f "$COMPOSE_FILE" run --rm backup

    if [ $? -eq 0 ]; then
        success "Database backup completed"
    else
        error "Database backup failed"
        return 1
    fi
}

# Function to build new image
build_new_image() {
    log "Building new application image with tag: $NEW_IMAGE_TAG"

    # Build new image with timestamp tag
    docker compose -f "$COMPOSE_FILE" build \
        --build-arg BUILDTIME="$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --build-arg GIT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
        app

    # Tag the image
    docker tag cc-lite-app:latest cc-lite-app:$NEW_IMAGE_TAG

    success "New image built successfully"
}

# Function to perform rolling update
rolling_update() {
    log "Starting rolling update deployment..."

    # Export new image tag for docker-compose
    export IMAGE_TAG=$NEW_IMAGE_TAG

    # Update the application service with rolling update
    log "Updating application service..."
    docker compose -f "$COMPOSE_FILE" up -d --no-deps app

    # Wait for new container to be healthy
    if check_service_health "app"; then
        success "New application container is healthy"
    else
        error "New application container failed health check"
        return 1
    fi

    # Check application endpoint
    if check_application_endpoint; then
        success "Application endpoint is responding correctly"
    else
        error "Application endpoint check failed"
        return 1
    fi

    success "Rolling update completed successfully"
}

# Function to perform blue-green deployment
blue_green_deployment() {
    log "Starting blue-green deployment..."

    # Create new services with blue/green naming
    local current_color=$(docker compose -f "$COMPOSE_FILE" ps app --format "table {{.Names}}" | tail -n +2 | head -n 1 | grep -o "blue\|green" || echo "blue")
    local new_color="green"
    if [ "$current_color" = "green" ]; then
        new_color="blue"
    fi

    log "Current color: $current_color, deploying to: $new_color"

    # Create temporary compose file for new color
    local temp_compose="$PROJECT_ROOT/docker-compose.temp.yml"
    sed "s/cc-lite-app-prod/cc-lite-app-$new_color/g" "$COMPOSE_FILE" > "$temp_compose"

    # Export new image tag
    export IMAGE_TAG=$NEW_IMAGE_TAG

    # Start new version
    log "Starting new version ($new_color)..."
    docker compose -f "$temp_compose" up -d app

    # Wait for new version to be healthy
    if check_service_health "app"; then
        success "New version ($new_color) is healthy"
    else
        error "New version ($new_color) failed health check"
        docker compose -f "$temp_compose" down
        rm -f "$temp_compose"
        return 1
    fi

    # Update nginx configuration to point to new version
    log "Switching traffic to new version..."

    # Here you would update nginx upstream configuration
    # For simplicity, we'll restart nginx to pick up the new backend
    docker compose -f "$COMPOSE_FILE" restart nginx

    # Wait a bit for connections to drain
    sleep 10

    # Stop old version
    log "Stopping old version ($current_color)..."
    docker stop "cc-lite-app-$current_color" 2>/dev/null || true
    docker rm "cc-lite-app-$current_color" 2>/dev/null || true

    # Clean up temporary file
    rm -f "$temp_compose"

    success "Blue-green deployment completed successfully"
}

# Function to perform database migrations
run_migrations() {
    log "Running database migrations..."

    # Run migrations in a temporary container
    docker compose -f "$COMPOSE_FILE" run --rm \
        -e DATABASE_URL="$(docker compose -f "$COMPOSE_FILE" exec -T app printenv DATABASE_URL)" \
        app pnpm prisma migrate deploy

    if [ $? -eq 0 ]; then
        success "Database migrations completed"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Function to validate deployment
validate_deployment() {
    log "Validating deployment..."

    # Check all services are healthy
    local services=("postgres" "redis" "app" "nginx")
    for service in "${services[@]}"; do
        if ! check_service_health "$service"; then
            error "Service $service is not healthy"
            return 1
        fi
    done

    # Check application endpoints
    local endpoints=(
        "http://127.0.0.1:3010/health"
        "http://127.0.0.1:3010/api/health"
        "http://127.0.0.1:3007/"
    )

    for endpoint in "${endpoints[@]}"; do
        log "Testing endpoint: $endpoint"
        if curl -f -s "$endpoint" >/dev/null 2>&1; then
            success "Endpoint $endpoint is responding"
        else
            error "Endpoint $endpoint is not responding"
            return 1
        fi
    done

    # Check metrics endpoint
    log "Testing metrics endpoint..."
    if curl -f -s "http://127.0.0.1:3010/metrics" >/dev/null 2>&1; then
        success "Metrics endpoint is responding"
    else
        warn "Metrics endpoint is not responding (this may be expected)"
    fi

    success "Deployment validation completed successfully"
}

# Function to rollback deployment
rollback_deployment() {
    local previous_tag=${1:-latest}

    error "Rolling back to previous version: $previous_tag"

    # Export previous image tag
    export IMAGE_TAG=$previous_tag

    # Restart application with previous image
    docker compose -f "$COMPOSE_FILE" up -d --no-deps app

    # Wait for rollback to complete
    if check_service_health "app" && check_application_endpoint; then
        success "Rollback completed successfully"
    else
        error "Rollback failed"
        return 1
    fi
}

# Function to cleanup old images
cleanup_old_images() {
    log "Cleaning up old Docker images..."

    # Keep last 5 images
    docker images cc-lite-app --format "table {{.Tag}}" | tail -n +2 | grep -E '^[0-9]{8}-[0-9]{6}$' | sort -r | tail -n +6 | while read tag; do
        log "Removing old image: cc-lite-app:$tag"
        docker rmi "cc-lite-app:$tag" 2>/dev/null || true
    done

    # Clean up dangling images
    docker image prune -f

    success "Image cleanup completed"
}

# Main deployment function
main() {
    local deployment_type="${1:-rolling}"
    local skip_backup="${2:-false}"

    log "Starting Voice by Kraliki zero-downtime deployment"
    log "Deployment type: $deployment_type"
    log "New image tag: $NEW_IMAGE_TAG"

    # Pre-deployment checks
    if ! docker --version >/dev/null 2>&1; then
        error "Docker is not installed or not accessible"
        exit 1
    fi

    if ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose is not installed or not accessible"
        exit 1
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    # Store current image tag for potential rollback
    local current_tag=$(docker compose -f "$COMPOSE_FILE" images app --format "table {{.Tag}}" | tail -n +2 | head -n 1)
    log "Current image tag: $current_tag"

    # Create backup (optional)
    if [ "$skip_backup" != "true" ]; then
        if ! create_backup; then
            error "Backup creation failed, aborting deployment"
            exit 1
        fi
    fi

    # Build new image
    if ! build_new_image; then
        error "Image build failed, aborting deployment"
        exit 1
    fi

    # Run database migrations
    if ! run_migrations; then
        error "Database migrations failed, aborting deployment"
        exit 1
    fi

    # Perform deployment based on type
    case "$deployment_type" in
        "rolling")
            if ! rolling_update; then
                error "Rolling update failed, attempting rollback..."
                rollback_deployment "$current_tag"
                exit 1
            fi
            ;;
        "blue-green")
            if ! blue_green_deployment; then
                error "Blue-green deployment failed, attempting rollback..."
                rollback_deployment "$current_tag"
                exit 1
            fi
            ;;
        *)
            error "Unknown deployment type: $deployment_type"
            error "Supported types: rolling, blue-green"
            exit 1
            ;;
    esac

    # Validate deployment
    if ! validate_deployment; then
        error "Deployment validation failed, attempting rollback..."
        rollback_deployment "$current_tag"
        exit 1
    fi

    # Cleanup old images
    cleanup_old_images

    success "Zero-downtime deployment completed successfully!"
    log "New version is running with tag: $NEW_IMAGE_TAG"
    log "Previous version tag for rollback: $current_tag"
}

# Script usage
usage() {
    echo "Usage: $0 [deployment_type] [skip_backup]"
    echo ""
    echo "deployment_type:"
    echo "  rolling      Rolling update (default)"
    echo "  blue-green   Blue-green deployment"
    echo ""
    echo "skip_backup:"
    echo "  true         Skip database backup"
    echo "  false        Create database backup (default)"
    echo ""
    echo "Environment variables:"
    echo "  NEW_IMAGE_TAG              Tag for new image (default: timestamp)"
    echo "  HEALTH_CHECK_TIMEOUT       Health check timeout in seconds (default: 300)"
    echo "  HEALTH_CHECK_INTERVAL      Health check interval in seconds (default: 5)"
    echo ""
    echo "Examples:"
    echo "  $0                         # Rolling deployment with backup"
    echo "  $0 blue-green              # Blue-green deployment with backup"
    echo "  $0 rolling true            # Rolling deployment without backup"
}

# Handle script arguments
case "${1:-}" in
    "-h"|"--help"|"help")
        usage
        exit 0
        ;;
    *)
        main "${1:-rolling}" "${2:-false}"
        ;;
esac