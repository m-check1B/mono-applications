#!/bin/bash

# Production Deployment with Full Monitoring Stack
# =========================================
# Deploys Voice Kraliki application with complete APM and monitoring infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo -e "${CYAN}"
cat << "EOF"
  ___                     _              ___
 / _ \ _ __   ___ _ __ __ _| |_ ___  _ __|  _ \  ___ _ __ ___   ___
| | | | '_ \ / _ \ '__/ _` | __/ _ \| '__| | | |/ _ \ '_ ` _ \ / _ \
| |_| | |_) |  __/ | | (_| | || (_) | |  | |_| |  __/ | | | | | (_) |
 \___/| .__/ \___|_|  \__,_|\__\___/|_|  |____/ \___|_| |_| |_|\___/
       |_|                                    APM & Monitoring
EOF
echo -e "${NC}"

echo -e "${BLUE}======================================"
echo "Production Deployment with Monitoring"
echo -e "======================================${NC}"

# Check requirements
check_requirements() {
    local missing_tools=""

    if ! command -v docker &> /dev/null; then
        missing_tools="$missing_tools docker"
    fi

    if ! command -v docker compose &> /dev/null; then
        missing_tools="$missing_tools docker-compose"
    fi

    if [ -n "$missing_tools" ]; then
        echo -e "${RED}Missing required tools: $missing_tools${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ All requirements satisfied${NC}"
}

# Check .env file
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        echo "Creating from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please update .env with your configuration!${NC}"
        echo "  - Set SENTRY_DSN for error tracking"
        echo "  - Update GRAFANA_ADMIN_PASSWORD"
        echo "  - Configure API keys for AI/telephony providers"
        read -p "Press Enter to continue after updating .env..."
    fi
    echo -e "${GREEN}✅ Environment configuration found${NC}"
}

# Stop existing containers
stop_existing() {
    echo -e "${YELLOW}Stopping existing containers...${NC}"

    # Stop main application
    docker compose -f docker-compose.yml down 2>/dev/null || true

    # Stop monitoring stack
    docker compose -f docker-compose.monitoring.prod.yml down 2>/dev/null || true

    echo -e "${GREEN}✅ Existing containers stopped${NC}"
}

# Build and start application
start_application() {
    echo -e "${BLUE}Building application images...${NC}"
    docker compose -f docker-compose.yml build

    echo -e "${BLUE}Starting application services...${NC}"
    docker compose -f docker-compose.yml up -d

    echo -e "${GREEN}✅ Application started${NC}"
}

# Build and start monitoring
start_monitoring() {
    echo -e "${BLUE}Building monitoring images...${NC}"
    docker compose -f docker-compose.monitoring.prod.yml pull

    echo -e "${BLUE}Starting monitoring stack...${NC}"
    docker compose -f docker-compose.monitoring.prod.yml up -d

    echo -e "${GREEN}✅ Monitoring stack started${NC}"
}

# Wait for services to be healthy
wait_for_health() {
    echo ""
    echo -e "${YELLOW}Waiting for services to be healthy...${NC}"

    local max_wait=60
    local count=0

    while [ $count -lt $max_wait ]; do
        # Check backend
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅${NC} Backend API"
            break
        fi

        echo -n "."
        sleep 2
        count=$((count + 2))
    done

    # Check monitoring services
    echo ""
    echo -e "${YELLOW}Checking monitoring services...${NC}"

    # Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Prometheus (http://localhost:9090)"
    else
        echo -e "  ${RED}❌${NC} Prometheus not healthy yet"
    fi

    # Grafana
    if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Grafana (http://localhost:3001)"
    else
        echo -e "  ${RED}❌${NC} Grafana not healthy yet"
    fi

    # Alertmanager
    if curl -s http://localhost:9093/-/healthy > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Alertmanager (http://localhost:9093)"
    else
        echo -e "  ${RED}❌${NC} Alertmanager not healthy yet"
    fi

    # Metrics endpoint
    if curl -s http://localhost:8000/metrics > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Metrics endpoint exposed"
    else
        echo -e "  ${RED}❌${NC} Metrics endpoint not available"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "${CYAN}Application Access:${NC}"
    echo -e "  Frontend: ${BLUE}https://voice.kraliki.com${NC}"
    echo -e "  Backend API: ${BLUE}https://voice.kraliki.com/api${NC}"
    echo -e "  API Docs: ${BLUE}https://voice.kraliki.com/docs${NC}"
    echo ""
    echo -e "${CYAN}Monitoring Access (localhost only):${NC}"
    echo -e "  Grafana: ${BLUE}http://localhost:3001${NC}"
    echo -e "  Prometheus: ${BLUE}http://localhost:9090${NC}"
    echo -e "  Alertmanager: ${BLUE}http://localhost:9093${NC}"
    echo -e "  Node Exporter: ${BLUE}http://localhost:9100/metrics${NC}"
    echo ""
    echo -e "${CYAN}Default Credentials:${NC}"
    echo -e "  Grafana: ${YELLOW}admin / admin${NC} ${RED}(CHANGE IN PRODUCTION!)${NC}"
    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  View logs: ${BLUE}docker logs -f voice-kraliki-backend${NC}"
    echo -e "  Check status: ${BLUE}docker ps${NC}"
    echo -e "  Stop all: ${BLUE}docker compose -f docker-compose.yml -f docker-compose.monitoring.prod.yml down${NC}"
    echo ""
    echo -e "${YELLOW}📝 Read deployment guide: docs/deployment/PRODUCTION_MONITORING_SETUP.md${NC}"
    echo ""
}

# Main execution
main() {
    check_requirements
    check_env
    stop_existing
    start_application
    start_monitoring
    wait_for_health
    show_access_info
}

# Run main
main
