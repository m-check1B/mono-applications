#!/usr/bin/env bash
# Lab by Kraliki Stack Deployment Script
# Deploys the complete Lab by Kraliki multi-AI orchestration stack
#
# Prerequisites:
#   - Fresh Ubuntu 22.04 VM with Docker installed (from create-vm.sh cloud-init)
#   - Run as root
#
# Usage:
#   sudo ./deploy-stack.sh --admin-user magicbox --ssh-key "ssh-ed25519 AAAA..."
#
set -euo pipefail

# Configuration
ADMIN_USER=""
SSH_PUB_KEY=""
SSH_PUB_KEY_FILE=""
MAGIC_BOX_DIR="/opt/magic-box"
SKIP_USER_SETUP=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
  cat <<'USAGE'
Lab by Kraliki Stack Deployment Script

Deploys the complete Lab by Kraliki multi-AI orchestration platform.

Usage:
  sudo ./deploy-stack.sh --admin-user <username> --ssh-key <public-key>

Required:
  --admin-user USER     Admin username to create (e.g., magicbox)
  --ssh-key KEY         SSH public key string
  --ssh-key-file PATH   Or read SSH key from file

Options:
  --skip-user           Skip user creation (user already exists)
  -h, --help            Show this help

Components Deployed:
  - Semantic search (mgrep + Qdrant + Infinity embeddings)
  - Traefik reverse proxy (localhost only)
  - Lab by Kraliki CLI management tool
  - Pre-configured workspace structure

USAGE
}

log() {
  echo -e "${GREEN}==>${NC} $1"
}

log_section() {
  echo ""
  echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

warn() {
  echo -e "${YELLOW}==> WARNING:${NC} $1"
}

fail() {
  echo -e "${RED}==> ERROR:${NC} $1" >&2
  exit 1
}

# Check root
if [[ "${EUID}" -ne 0 ]]; then
  fail "Run this script as root (use sudo)."
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --admin-user)
      ADMIN_USER="${2:-}"
      shift 2
      ;;
    --ssh-key)
      SSH_PUB_KEY="${2:-}"
      shift 2
      ;;
    --ssh-key-file)
      SSH_PUB_KEY_FILE="${2:-}"
      shift 2
      ;;
    --skip-user)
      SKIP_USER_SETUP=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown option: $1"
      ;;
  esac
done

# Validate
[[ -z "${ADMIN_USER}" ]] && fail "--admin-user is required"

if [[ -n "${SSH_PUB_KEY_FILE}" ]]; then
  [[ ! -f "${SSH_PUB_KEY_FILE}" ]] && fail "SSH key file not found: ${SSH_PUB_KEY_FILE}"
  SSH_PUB_KEY="$(cat "${SSH_PUB_KEY_FILE}")"
fi

[[ -z "${SSH_PUB_KEY}" && "${SKIP_USER_SETUP}" -eq 0 ]] && fail "Provide SSH key via --ssh-key or --ssh-key-file"

# Check Docker
if ! command -v docker &> /dev/null; then
  fail "Docker not installed. Run cloud-init first or install manually."
fi

if ! docker compose version &> /dev/null; then
  fail "Docker Compose plugin not installed."
fi

log_section "Creating Admin User: ${ADMIN_USER}"

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  # Create user
  if id -u "${ADMIN_USER}" &>/dev/null; then
    log "User ${ADMIN_USER} already exists"
  else
    useradd -m -s /bin/bash "${ADMIN_USER}"
    log "Created user ${ADMIN_USER}"
  fi

  # Add to groups
  usermod -aG sudo,docker "${ADMIN_USER}"

  # Passwordless sudo
  echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${ADMIN_USER}"
  chmod 440 "/etc/sudoers.d/${ADMIN_USER}"

  # SSH key
  install -d -m 700 "/home/${ADMIN_USER}/.ssh"
  if ! grep -qF "${SSH_PUB_KEY}" "/home/${ADMIN_USER}/.ssh/authorized_keys" 2>/dev/null; then
    echo "${SSH_PUB_KEY}" >> "/home/${ADMIN_USER}/.ssh/authorized_keys"
  fi
  chown -R "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
  chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"
  log "SSH key configured"
fi

log_section "Setting Up Lab by Kraliki Directory Structure"

mkdir -p "${MAGIC_BOX_DIR}"/{config,data,logs,prompts,patterns,scripts}
mkdir -p "${MAGIC_BOX_DIR}/data"/{qdrant-storage,infinity-cache}

# Create docker-compose.yml for the stack
cat > "${MAGIC_BOX_DIR}/docker-compose.yml" <<'COMPOSE'
version: '3.8'

services:
  # Embedding & Reranking Server (CPU-optimized)
  infinity:
    image: michaelf34/infinity:latest
    container_name: magic-box-infinity
    ports:
      - "127.0.0.1:7997:7997"
    volumes:
      - ./data/infinity-cache:/app/.cache
    command: >
      v2
      --model-id mixedbread-ai/mxbai-embed-large-v1
      --model-id mixedbread-ai/mxbai-rerank-large-v1
      --engine torch
      --device cpu
      --port 7997
    environment:
      - HF_HOME=/app/.cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7997/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: magic-box-qdrant
    ports:
      - "127.0.0.1:6333:6333"
      - "127.0.0.1:6334:6334"
    volumes:
      - ./data/qdrant-storage:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Reverse Proxy (for internal services)
  traefik:
    image: traefik:v3.0
    container_name: magic-box-traefik
    command:
      - "--api.insecure=true"
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "127.0.0.1:8080:80"
      - "127.0.0.1:8081:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped

networks:
  default:
    name: magic-box-network
COMPOSE

log "Created docker-compose.yml"

# Create environment template
cat > "${MAGIC_BOX_DIR}/config/.env.template" <<'ENV_TEMPLATE'
# Lab by Kraliki Configuration
# Copy to .env and fill in your API keys

# =============================================================================
# AI API Keys (at least one required)
# =============================================================================

# Anthropic (Claude) - Required for orchestration
ANTHROPIC_API_KEY=

# OpenAI (GPT/Codex) - Optional, for additional workers
OPENAI_API_KEY=

# Google (Gemini) - Optional, for additional workers
GOOGLE_API_KEY=

# =============================================================================
# Service Configuration (usually no changes needed)
# =============================================================================

# Semantic search
INFINITY_URL=http://127.0.0.1:7997
QDRANT_URL=http://127.0.0.1:6333

# Logging
LOG_LEVEL=info
ENV_TEMPLATE

log "Created .env.template"

# Create the magic-box CLI tool
cat > "${MAGIC_BOX_DIR}/scripts/magic-box" <<'CLI_SCRIPT'
#!/usr/bin/env bash
# Lab by Kraliki CLI - Management tool for Lab by Kraliki platform
set -euo pipefail

MAGIC_BOX_DIR="/opt/magic-box"
COMPOSE_FILE="${MAGIC_BOX_DIR}/docker-compose.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_banner() {
  echo -e "${BLUE}"
  cat <<'BANNER'
  ╔═══════════════════════════════════════════════════════════╗
  ║                       LAB BY KRALIKI                            ║
  ║            Multi-AI Orchestration Platform                 ║
  ╚═══════════════════════════════════════════════════════════╝
BANNER
  echo -e "${NC}"
}

usage() {
  show_banner
  cat <<'USAGE'
Usage: magic-box <command> [options]

Commands:
  status          Show status of all services
  start           Start all Lab by Kraliki services
  stop            Stop all services
  restart         Restart all services
  logs [service]  Show logs (optionally for specific service)
  config          Edit configuration (.env file)
  test            Test API connections
  update          Pull latest container images
  help            Show this help

Service names: infinity, qdrant, traefik

Examples:
  magic-box status
  magic-box logs infinity
  magic-box restart

USAGE
}

log() {
  echo -e "${GREEN}==>${NC} $1"
}

warn() {
  echo -e "${YELLOW}==>${NC} $1"
}

fail() {
  echo -e "${RED}==>${NC} $1" >&2
  exit 1
}

cmd_status() {
  show_banner
  log "Service Status:"
  echo ""

  cd "${MAGIC_BOX_DIR}"

  # Check Docker services
  if docker compose ps --quiet 2>/dev/null | grep -q .; then
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
  else
    warn "No services running"
  fi

  echo ""
  log "Health Checks:"

  # Check Infinity
  if curl -sf http://127.0.0.1:7997/health &>/dev/null; then
    echo -e "  Infinity (embeddings):  ${GREEN}✓ healthy${NC}"
  else
    echo -e "  Infinity (embeddings):  ${RED}✗ not responding${NC}"
  fi

  # Check Qdrant
  if curl -sf http://127.0.0.1:6333/healthz &>/dev/null; then
    echo -e "  Qdrant (vector DB):     ${GREEN}✓ healthy${NC}"
  else
    echo -e "  Qdrant (vector DB):     ${RED}✗ not responding${NC}"
  fi

  # Check Traefik
  if curl -sf http://127.0.0.1:8081/api/overview &>/dev/null; then
    echo -e "  Traefik (proxy):        ${GREEN}✓ healthy${NC}"
  else
    echo -e "  Traefik (proxy):        ${RED}✗ not responding${NC}"
  fi

  echo ""
  log "Configuration:"
  if [[ -f "${MAGIC_BOX_DIR}/config/.env" ]]; then
    # Check for API keys (show if set, not the actual value)
    if grep -q "^ANTHROPIC_API_KEY=sk-" "${MAGIC_BOX_DIR}/config/.env" 2>/dev/null; then
      echo -e "  Anthropic API key:      ${GREEN}✓ configured${NC}"
    else
      echo -e "  Anthropic API key:      ${YELLOW}○ not set${NC}"
    fi
    if grep -q "^OPENAI_API_KEY=sk-" "${MAGIC_BOX_DIR}/config/.env" 2>/dev/null; then
      echo -e "  OpenAI API key:         ${GREEN}✓ configured${NC}"
    else
      echo -e "  OpenAI API key:         ${YELLOW}○ not set${NC}"
    fi
    if grep -qE "^GOOGLE_API_KEY=.+" "${MAGIC_BOX_DIR}/config/.env" 2>/dev/null; then
      echo -e "  Google API key:         ${GREEN}✓ configured${NC}"
    else
      echo -e "  Google API key:         ${YELLOW}○ not set${NC}"
    fi
  else
    warn "Config file not found. Run: magic-box config"
  fi
  echo ""
}

cmd_start() {
  log "Starting Lab by Kraliki services..."
  cd "${MAGIC_BOX_DIR}"
  docker compose up -d
  log "Services started. Run 'magic-box status' to verify."
}

cmd_stop() {
  log "Stopping Lab by Kraliki services..."
  cd "${MAGIC_BOX_DIR}"
  docker compose down
  log "Services stopped."
}

cmd_restart() {
  log "Restarting Lab by Kraliki services..."
  cd "${MAGIC_BOX_DIR}"
  docker compose restart
  log "Services restarted."
}

cmd_logs() {
  local service="${1:-}"
  cd "${MAGIC_BOX_DIR}"
  if [[ -n "${service}" ]]; then
    docker compose logs -f "${service}"
  else
    docker compose logs -f
  fi
}

cmd_config() {
  local env_file="${MAGIC_BOX_DIR}/config/.env"
  local template="${MAGIC_BOX_DIR}/config/.env.template"

  if [[ ! -f "${env_file}" ]]; then
    if [[ -f "${template}" ]]; then
      cp "${template}" "${env_file}"
      log "Created ${env_file} from template"
    else
      fail "No template found at ${template}"
    fi
  fi

  # Use $EDITOR or fall back to nano/vim
  local editor="${EDITOR:-nano}"
  if ! command -v "${editor}" &>/dev/null; then
    editor="vim"
  fi

  "${editor}" "${env_file}"
}

cmd_test() {
  log "Testing API connections..."
  echo ""

  local env_file="${MAGIC_BOX_DIR}/config/.env"
  if [[ ! -f "${env_file}" ]]; then
    warn "No .env file found. Run 'magic-box config' first."
    return 1
  fi

  # shellcheck disable=SC1090
  source "${env_file}"

  # Test Anthropic
  if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    log "Testing Anthropic API..."
    if curl -sf https://api.anthropic.com/v1/messages \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}' \
      &>/dev/null; then
      echo -e "  Anthropic:  ${GREEN}✓ connected${NC}"
    else
      echo -e "  Anthropic:  ${RED}✗ failed${NC}"
    fi
  else
    echo -e "  Anthropic:  ${YELLOW}○ not configured${NC}"
  fi

  # Test OpenAI
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    log "Testing OpenAI API..."
    if curl -sf https://api.openai.com/v1/models \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      &>/dev/null; then
      echo -e "  OpenAI:     ${GREEN}✓ connected${NC}"
    else
      echo -e "  OpenAI:     ${RED}✗ failed${NC}"
    fi
  else
    echo -e "  OpenAI:     ${YELLOW}○ not configured${NC}"
  fi

  echo ""
}

cmd_update() {
  log "Pulling latest container images..."
  cd "${MAGIC_BOX_DIR}"
  docker compose pull
  log "Images updated. Run 'magic-box restart' to apply."
}

# Main
case "${1:-help}" in
  status)
    cmd_status
    ;;
  start)
    cmd_start
    ;;
  stop)
    cmd_stop
    ;;
  restart)
    cmd_restart
    ;;
  logs)
    cmd_logs "${2:-}"
    ;;
  config)
    cmd_config
    ;;
  test)
    cmd_test
    ;;
  update)
    cmd_update
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    fail "Unknown command: ${1}. Run 'magic-box help' for usage."
    ;;
esac
CLI_SCRIPT

chmod +x "${MAGIC_BOX_DIR}/scripts/magic-box"
log "Created magic-box CLI tool"

# Symlink to /usr/local/bin
ln -sf "${MAGIC_BOX_DIR}/scripts/magic-box" /usr/local/bin/magic-box
log "Installed magic-box to /usr/local/bin"

# Create basic CLAUDE.md for workspace
cat > "${MAGIC_BOX_DIR}/CLAUDE.md" <<'CLAUDE_MD'
# Lab by Kraliki Workspace

Multi-AI orchestration platform.

## Quick Commands

- `magic-box status` - Check system health
- `magic-box logs` - View service logs
- `magic-box config` - Edit API keys

## Workspace Structure

```
/opt/magic-box/
├── docker-compose.yml  # Service definitions
├── config/             # Configuration files
│   └── .env            # API keys (create from .env.template)
├── data/               # Persistent data
│   ├── qdrant-storage/ # Vector database
│   └── infinity-cache/ # Model cache
├── prompts/            # Prompt templates
├── patterns/           # Workflow patterns
└── logs/               # Execution logs
```

## Available AI Workers

Configure API keys in `magic-box config`:
- Claude (Anthropic) - Required, orchestrator
- GPT/Codex (OpenAI) - Optional, backend/audit worker
- Gemini (Google) - Optional, frontend/research worker

## Core Patterns

1. **Build-Audit-Fix**: Build → Audit → Incorporate feedback
2. **Parallel Execution**: Multiple workers on independent tasks
3. **Hard Problem Voting**: Multiple models vote on complex decisions
CLAUDE_MD

log "Created workspace CLAUDE.md"

# Set ownership
chown -R "${ADMIN_USER}:${ADMIN_USER}" "${MAGIC_BOX_DIR}"

log_section "Starting Lab by Kraliki Services"

cd "${MAGIC_BOX_DIR}"
docker compose pull
docker compose up -d

# Wait for services to be healthy
log "Waiting for services to initialize..."
sleep 10

log_section "Deployment Complete!"

# Get IP for instructions
VM_IP=$(hostname -I | awk '{print $1}')

cat <<EOF

═══════════════════════════════════════════════════════════════
                    LAB BY KRALIKI READY
═══════════════════════════════════════════════════════════════

SSH Access:
  ssh ${ADMIN_USER}@${VM_IP}

Quick Start:
  1. Connect: ssh ${ADMIN_USER}@${VM_IP}
  2. Configure: magic-box config
     (Add your API keys: ANTHROPIC_API_KEY, etc.)
  3. Verify: magic-box status
  4. Start working!

Service Ports (localhost only):
  - Infinity (embeddings): 127.0.0.1:7997
  - Qdrant (vectors):      127.0.0.1:6333
  - Traefik dashboard:     127.0.0.1:8081

Documentation:
  /opt/magic-box/CLAUDE.md

═══════════════════════════════════════════════════════════════

EOF
