#!/bin/bash
# Voice by Kraliki Docker Configuration Validator
# ======================================
# Validates the production Docker configuration for compliance and security

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

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Functions
log() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN: $1${NC}"
    ((WARNINGS++))
}

# Validation functions
validate_file_exists() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        pass "$description exists: $file"
    else
        fail "$description missing: $file"
    fi
}

validate_docker_compose_syntax() {
    log "Validating Docker Compose syntax..."

    if docker compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
        pass "Docker Compose syntax is valid"
    else
        fail "Docker Compose syntax is invalid"
        docker compose -f "$COMPOSE_FILE" config || true
    fi
}

validate_secrets_configuration() {
    log "Validating Docker secrets configuration..."

    # Check if secrets are defined
    local secrets=$(docker compose -f "$COMPOSE_FILE" config | grep -A 20 "^secrets:" | grep "external: true" | wc -l)

    if [ "$secrets" -gt 0 ]; then
        pass "Docker secrets are configured ($secrets secrets found)"
    else
        fail "No Docker secrets configured"
    fi

    # Check for hardcoded passwords
    if grep -q "password.*:" "$COMPOSE_FILE" | grep -v "PLACEHOLDER\|FILE\|/run/secrets"; then
        fail "Hardcoded passwords detected in compose file"
    else
        pass "No hardcoded passwords detected"
    fi
}

validate_network_security() {
    log "Validating network security configuration..."

    # Check for proper network isolation
    if grep -q "127.0.0.1:" "$COMPOSE_FILE"; then
        pass "Services are bound to localhost (127.0.0.1)"
    else
        warn "Some services may not be bound to localhost"
    fi

    # Check for internal networks
    if grep -q "networks:" "$COMPOSE_FILE" && grep -q "internal: true" "$COMPOSE_FILE"; then
        pass "Internal networks are configured"
    else
        warn "Internal networks may not be properly configured"
    fi

    # Check for unnecessary port exposures
    local exposed_ports=$(grep -c "0.0.0.0:" "$COMPOSE_FILE" || echo 0)
    if [ "$exposed_ports" -eq 0 ]; then
        pass "No services exposed to 0.0.0.0 (good security practice)"
    else
        fail "Services exposed to 0.0.0.0 detected (security risk)"
    fi
}

validate_security_hardening() {
    log "Validating security hardening configuration..."

    # Check for non-root users
    if grep -q "user:" "$COMPOSE_FILE"; then
        pass "Non-root users configured for services"
    else
        warn "Non-root users may not be configured"
    fi

    # Check for security options
    if grep -q "no-new-privileges:true" "$COMPOSE_FILE"; then
        pass "no-new-privileges security option configured"
    else
        fail "no-new-privileges security option missing"
    fi

    # Check for capability dropping
    if grep -q "cap_drop:" "$COMPOSE_FILE"; then
        pass "Capability dropping configured"
    else
        warn "Capability dropping may not be configured"
    fi

    # Check for read-only containers
    if grep -q "read_only: true" "$COMPOSE_FILE"; then
        pass "Read-only containers configured"
    else
        warn "Read-only containers may not be configured"
    fi
}

validate_health_checks() {
    log "Validating health check configuration..."

    # Count health checks
    local health_checks=$(grep -c "healthcheck:" "$COMPOSE_FILE" || echo 0)

    if [ "$health_checks" -ge 3 ]; then
        pass "Health checks configured for multiple services ($health_checks found)"
    else
        warn "Insufficient health checks configured ($health_checks found)"
    fi

    # Check for depends_on with condition
    if grep -q "condition: service_healthy" "$COMPOSE_FILE"; then
        pass "Service dependencies with health conditions configured"
    else
        warn "Service dependencies may not wait for health checks"
    fi
}

validate_resource_limits() {
    log "Validating resource limits configuration..."

    # Check for resource limits
    if grep -q "resources:" "$COMPOSE_FILE" && grep -q "limits:" "$COMPOSE_FILE"; then
        pass "Resource limits configured"
    else
        warn "Resource limits may not be configured"
    fi

    # Check for restart policies
    if grep -q "restart: unless-stopped" "$COMPOSE_FILE"; then
        pass "Appropriate restart policies configured"
    else
        warn "Restart policies may not be configured"
    fi
}

validate_logging_configuration() {
    log "Validating logging configuration..."

    # Check for logging configuration
    if grep -q "logging:" "$COMPOSE_FILE"; then
        pass "Logging configuration found"
    else
        warn "Logging configuration may not be specified"
    fi

    # Check for log rotation
    if grep -q "max-size\|max-file" "$COMPOSE_FILE"; then
        pass "Log rotation configured"
    else
        warn "Log rotation may not be configured"
    fi
}

validate_monitoring_setup() {
    log "Validating monitoring setup..."

    # Check for Prometheus
    if grep -q "prometheus" "$COMPOSE_FILE"; then
        pass "Prometheus monitoring configured"
    else
        warn "Prometheus monitoring not found"
    fi

    # Check for Grafana
    if grep -q "grafana" "$COMPOSE_FILE"; then
        pass "Grafana dashboards configured"
    else
        warn "Grafana dashboards not found"
    fi

    # Check for Loki
    if grep -q "loki" "$COMPOSE_FILE"; then
        pass "Loki log aggregation configured"
    else
        warn "Loki log aggregation not found"
    fi
}

validate_backup_strategy() {
    log "Validating backup strategy..."

    # Check for backup service
    if grep -q "backup" "$COMPOSE_FILE"; then
        pass "Backup service configured"
    else
        warn "Backup service not found"
    fi

    # Check for persistent volumes
    if grep -q "driver: local" "$COMPOSE_FILE" && grep -q "device:" "$COMPOSE_FILE"; then
        pass "Persistent volumes with host bind mounts configured"
    else
        warn "Persistent volumes may not be properly configured"
    fi
}

validate_ssl_configuration() {
    log "Validating SSL/TLS configuration..."

    # Check for SSL certificate volumes
    if grep -q "ssl\|certs" "$COMPOSE_FILE"; then
        pass "SSL certificate volumes configured"
    else
        warn "SSL certificate configuration not found"
    fi

    # Check for HTTPS ports
    if grep -q "443:443" "$COMPOSE_FILE"; then
        pass "HTTPS port configured"
    else
        warn "HTTPS port not configured"
    fi
}

validate_environment_security() {
    log "Validating environment security..."

    # Check for production environment settings
    if grep -q "NODE_ENV: production" "$COMPOSE_FILE"; then
        pass "Production environment configured"
    else
        fail "Production environment not configured"
    fi

    # Check for debug settings
    if grep -q "ENABLE_DEBUG_LOGGING: false" "$COMPOSE_FILE"; then
        pass "Debug logging disabled in production"
    else
        warn "Debug logging may be enabled in production"
    fi

    # Check for demo users
    if grep -q "SEED_DEMO_USERS: false" "$COMPOSE_FILE"; then
        pass "Demo users disabled in production"
    else
        fail "Demo users may be enabled in production"
    fi
}

validate_database_security() {
    log "Validating database security..."

    # Check for PostgreSQL security
    if grep -q "scram-sha-256" "$COMPOSE_FILE"; then
        pass "PostgreSQL SCRAM-SHA-256 authentication configured"
    else
        warn "PostgreSQL may not use secure authentication"
    fi

    # Check for Redis authentication
    if grep -q "requirepass" "$COMPOSE_FILE"; then
        pass "Redis authentication configured"
    else
        fail "Redis authentication not configured"
    fi
}

# Additional configuration file validations
validate_supporting_files() {
    log "Validating supporting configuration files..."

    # Check for Nginx configuration
    validate_file_exists "$PROJECT_ROOT/deploy/nginx/nginx.prod.conf" "Nginx production configuration"

    # Check for Prometheus configuration
    validate_file_exists "$PROJECT_ROOT/deploy/monitoring/prometheus.yml" "Prometheus configuration"

    # Check for Loki configuration
    validate_file_exists "$PROJECT_ROOT/deploy/monitoring/loki.yml" "Loki configuration"

    # Check for alert rules
    validate_file_exists "$PROJECT_ROOT/deploy/monitoring/rules/cc-lite-alerts.yml" "Prometheus alert rules"

    # Check for setup scripts
    validate_file_exists "$PROJECT_ROOT/deploy/scripts/setup-secrets.sh" "Secrets setup script"
    validate_file_exists "$PROJECT_ROOT/deploy/scripts/backup.sh" "Backup script"
    validate_file_exists "$PROJECT_ROOT/deploy/scripts/zero-downtime-deploy.sh" "Zero-downtime deployment script"

    # Check if scripts are executable
    if [ -x "$PROJECT_ROOT/deploy/scripts/setup-secrets.sh" ]; then
        pass "Secrets setup script is executable"
    else
        warn "Secrets setup script is not executable"
    fi
}

validate_docker_requirements() {
    log "Validating Docker requirements..."

    # Check Docker version
    if command -v docker >/dev/null 2>&1; then
        local docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+')
        pass "Docker is installed (version: $docker_version)"
    else
        fail "Docker is not installed"
    fi

    # Check Docker Compose version
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        local compose_version=$(docker compose version | grep -oE '[0-9]+\.[0-9]+')
        pass "Docker Compose is installed (version: $compose_version)"
    else
        fail "Docker Compose is not installed"
    fi

    # Check Docker daemon
    if docker info >/dev/null 2>&1; then
        pass "Docker daemon is running"
    else
        fail "Docker daemon is not running or not accessible"
    fi
}

# Main validation function
main() {
    echo -e "${BLUE}Voice by Kraliki Docker Configuration Validator${NC}"
    echo "========================================"
    echo

    # Basic file validation
    validate_file_exists "$COMPOSE_FILE" "Docker Compose production file"

    if [ ! -f "$COMPOSE_FILE" ]; then
        fail "Cannot proceed without Docker Compose file"
        exit 1
    fi

    # Run all validations
    validate_docker_requirements
    validate_docker_compose_syntax
    validate_secrets_configuration
    validate_network_security
    validate_security_hardening
    validate_health_checks
    validate_resource_limits
    validate_logging_configuration
    validate_monitoring_setup
    validate_backup_strategy
    validate_ssl_configuration
    validate_environment_security
    validate_database_security
    validate_supporting_files

    # Summary
    echo
    echo -e "${BLUE}Validation Summary${NC}"
    echo "=================="
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo

    # Determine overall result
    if [ "$FAILED" -eq 0 ]; then
        if [ "$WARNINGS" -eq 0 ]; then
            echo -e "${GREEN}🎉 All validations passed! Configuration is production-ready.${NC}"
            exit 0
        else
            echo -e "${YELLOW}⚠️  Configuration is mostly ready, but please review warnings.${NC}"
            exit 0
        fi
    else
        echo -e "${RED}❌ Configuration has critical issues that must be fixed before production deployment.${NC}"
        exit 1
    fi
}

# Help function
usage() {
    echo "Voice by Kraliki Docker Configuration Validator"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "This script validates the production Docker configuration for:"
    echo "  - Security compliance"
    echo "  - Best practices"
    echo "  - Production readiness"
    echo "  - Required file existence"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    "-h"|"--help"|"help")
        usage
        exit 0
        ;;
    *)
        main
        ;;
esac