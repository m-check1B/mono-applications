#!/usr/bin/env bash
# Magic Box Complete One-Click Setup Script
# Full automated setup: Docker, Traefik, CLIProxyAPI, AI CLIs, mgrep
#
# Usage:
#   curl -fsSL <url>/setup-complete.sh | sudo bash
# Or with options:
#   curl -fsSL ... | sudo bash -s -- --admin-user myuser --api-keys-file /path/to/keys
#
set -euo pipefail

VERSION="2.0.0"
MAGIC_BOX_DIR="/opt/magic-box"
SCRIPT_DIR="${MAGIC_BOX_DIR}/scripts"

# Configuration
ADMIN_USER="${ADMIN_USER:-magicbox}"
SSH_PUB_KEY="${SSH_PUB_KEY:-}"
API_KEYS_FILE="${API_KEYS_FILE:-}"
SKIP_USER_SETUP=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_banner() {
  echo -e "${BLUE}"
  cat <<'BANNER'

  ███╗   ███╗ █████╗  ██████╗ ██╗ ██████╗    ██████╗  ██████╗ ██╗  ██╗
  ████╗ ████║██╔══██╗██╔════╝ ██║██╔════╝    ██╔══██╗██╔═══██╗╚██╗██╔╝
  ██╔████╔██║███████║██║  ███╗██║██║         ██████╔╝██║   ██║ ╚███╔╝
  ██║╚██╔╝██║██╔══██║██║   ██║██║██║         ██╔══██╗██║   ██║ ██╔██╗
  ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║╚██████╗    ██████╔╝╚██████╔╝██╔╝ ██╗
  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝

              Multi-AI Orchestration Platform
                     Complete Setup v${VERSION}

BANNER
  echo -e "${NC}"
}

usage() {
  show_banner
  cat <<'USAGE'
Usage:
  curl -fsSL <url>/setup-complete.sh | sudo bash
  curl -fsSL <url>/setup-complete.sh | sudo bash -s -- [options]

Options:
  --admin-user USER        Admin username (default: magicbox)
  --ssh-key KEY            SSH public key for admin user
  --ssh-key-file PATH      Read SSH key from file
  --api-keys-file PATH     File containing API keys (one per line)
                           Format: ANTHROPIC_API_KEY=sk-ant-...
  --skip-user              Skip user creation
  -h, --help               Show this help

API Keys File Format:
  ANTHROPIC_API_KEY=sk-ant-xxx
  OPENAI_API_KEY=sk-openai-xxx
  GOOGLE_API_KEY=AIzaSy-xxx

Environment Variables:
  ADMIN_USER            Admin username
  SSH_PUB_KEY           SSH public key
  API_KEYS_FILE          Path to API keys file

Example:
  # Interactive (will prompt for API keys)
  curl -fsSL https://example.com/setup-complete.sh | sudo bash

  # Non-interactive with keys file
  curl -fsSL https://example.com/setup-complete.sh | sudo bash -s -- \
    --admin-user myuser \
    --api-keys-file /path/to/keys.txt

USAGE
}

log() {
  echo -e "${GREEN}[+]${NC} $1"
}

log_section() {
  echo ""
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
  echo ""
}

warn() {
  echo -e "${YELLOW}[!]${NC} $1"
}

fail() {
  echo -e "${RED}[✗]${NC} $1" >&2
  exit 1
}

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
      if [[ -f "${2:-}" ]]; then
        SSH_PUB_KEY="$(cat "${2}")"
      fi
      shift 2
      ;;
    --api-keys-file)
      API_KEYS_FILE="${2:-}"
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
      warn "Unknown option: $1"
      shift
      ;;
  esac
done

show_banner

# Check root
if [[ "${EUID}" -ne 0 ]]; then
  fail "This script must be run as root. Use: curl ... | sudo bash"
fi

# Check OS
log_section "Checking System Requirements"

if [[ -f /etc/os-release ]]; then
  source /etc/os-release
  log "Detected: ${PRETTY_NAME:-${ID} ${VERSION_ID}}"
  if [[ "${ID}" != "ubuntu" ]]; then
    warn "This script is optimized for Ubuntu. Proceeding anyway..."
  fi
else
  warn "Could not detect OS version"
fi

# Check architecture
ARCH=$(uname -m)
log "Architecture: ${ARCH}"
if [[ "${ARCH}" != "x86_64" && "${ARCH}" != "aarch64" ]]; then
  fail "Unsupported architecture: ${ARCH}. Magic Box requires x86_64 or aarch64."
fi

# Check memory
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
log "Memory: ${TOTAL_MEM} MB"
if [[ "${TOTAL_MEM}" -lt 4000 ]]; then
  warn "Recommended minimum memory is 4GB. You have ${TOTAL_MEM}MB."
fi

# Check disk space
DISK_FREE=$(df -BG / | awk 'NR==2{print $4}')
log "Free disk space: ${DISK_FREE}GB"
if [[ "${DISK_FREE}" -lt 10 ]]; then
  fail "Insufficient disk space. Need at least 10GB free for models."
fi

# Prompt for SSH key if not provided
if [[ -z "${SSH_PUB_KEY}" && "${SKIP_USER_SETUP}" -eq 0 ]]; then
  echo ""
  echo "No SSH key provided. Please paste your SSH public key:"
  echo "(Usually found in ~/.ssh/id_ed25519.pub or ~/.ssh/id_rsa.pub)"
  echo ""
  read -r SSH_PUB_KEY

  if [[ -z "${SSH_PUB_KEY}" ]]; then
    fail "SSH key is required for admin user setup"
  fi
fi

log_section "Installing System Packages"

apt-get update -y
apt-get install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  lsb-release \
  ufw \
  fail2ban \
  htop \
  vim \
  tmux \
  python3 \
  python3-pip \
  nodejs \
  npm

log "System packages installed"

log_section "Installing Docker"

if command -v docker &> /dev/null; then
  log "Docker already installed: $(docker --version)"
else
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  UBUNTU_CODENAME="$(. /etc/os-release && echo "${VERSION_CODENAME:-jammy}")"
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list

  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  systemctl enable docker
  systemctl start docker
  log "Docker installed: $(docker --version)"
fi

if docker compose version &> /dev/null; then
  log "Docker Compose: $(docker compose version --short)"
else
  fail "Docker Compose plugin not found"
fi

log_section "Configuring Security"

ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH

if [[ -f /var/lib/ufw/user.rules ]]; then
  ufw --force enable
  log "Firewall enabled (SSH only)"
else
  log "Firewall rules set (enable manually with: ufw enable)"
fi

systemctl enable fail2ban
systemctl start fail2ban
log "Fail2ban enabled"

sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

if systemctl is-active --quiet ssh; then
  systemctl reload ssh
  log "SSH hardened (key-only auth)"
fi

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  log_section "Creating Admin User: ${ADMIN_USER}"

  if id -u "${ADMIN_USER}" &>/dev/null; then
    log "User ${ADMIN_USER} already exists"
  else
    useradd -m -s /bin/bash "${ADMIN_USER}"
    log "Created user: ${ADMIN_USER}"
  fi

  usermod -aG sudo,docker "${ADMIN_USER}"
  echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${ADMIN_USER}"
  chmod 440 "/etc/sudoers.d/${ADMIN_USER}"

  install -d -m 700 "/home/${ADMIN_USER}/.ssh"
  if ! grep -qF "${SSH_PUB_KEY}" "/home/${ADMIN_USER}/.ssh/authorized_keys" 2>/dev/null; then
    echo "${SSH_PUB_KEY}" >> "/home/${ADMIN_USER}/.ssh/authorized_keys"
  fi
  chown -R "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
  chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"
  log "SSH key configured for ${ADMIN_USER}"
fi

log_section "Setting Up Magic Box Directory Structure"

mkdir -p "${MAGIC_BOX_DIR}"/{config,data,logs,prompts,patterns,scripts}
mkdir -p "${MAGIC_BOX_DIR}/data"/{qdrant-storage,infinity-cache,mgrep-data,cliproxy-logs}

log_section "Configuring API Keys"

read_api_keys_file() {
  local keys_file="${1:-${API_KEYS_FILE}}"
  if [[ -f "${keys_file}" ]]; then
    log "Loading API keys from ${keys_file}"
    source "${keys_file}"
  else
    log "No API keys file provided. You can add them later with: magic-box config"
    ANTHROPIC_API_KEY=""
    OPENAI_API_KEY=""
    GOOGLE_API_KEY=""
  fi
}

read_api_keys_file "${API_KEYS_FILE}"

log_section "Creating Docker Compose Configuration"

cat > "${MAGIC_BOX_DIR}/docker-compose.yml" <<'COMPOSE'
version: '3.8'

services:
  # Embedding & Reranking Server
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

  # mgrep Backend (semantic search)
  mgrep-backend:
    image: node:18-alpine
    container_name: magic-box-mgrep-backend
    working_dir: /app
    ports:
      - "127.0.0.1:8001:8001"
    volumes:
      - ./data/mgrep-data:/app/data
      - ./data/infinity-cache:/app/.cache:ro
      - ${MAGIC_BOX_DIR}/scripts:/scripts:ro
    environment:
      - NODE_ENV=production
      - INFINITY_URL=http://infinity:7997
      - QDRANT_URL=http://qdrant:6333
      - PORT=8001
    command: sh -c "npm install -g @mixedbread/mgrep-server && mgrep-server"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Reverse Proxy
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
      - "127.0.0.1:8081:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8081/api/overview"]
      interval: 30s
      timeout: 10s
      retries: 3

  # CLIProxyAPI (Unified AI Gateway)
  cliproxyapi:
    image: node:18-alpine
    container_name: magic-box-cliproxyapi
    working_dir: /app
    ports:
      - "127.0.0.1:8888:8888"
    volumes:
      - ./data/cliproxy-logs:/var/log/cliproxy
      - ${MAGIC_BOX_DIR}/config/.env:/app/.env:ro
    environment:
      - NODE_ENV=production
      - CLIPROXY_PORT=8888
      - CLIPROXY_LOG_PATH=/var/log/cliproxy/access.log
      - ${ANTHROPIC_API_KEY:+ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}}
      - ${OPENAI_API_KEY:+OPENAI_API_KEY=${OPENAI_API_KEY}}
      - ${GOOGLE_API_KEY:+GOOGLE_API_KEY=${GOOGLE_API_KEY}}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8888/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: >
      sh -c "npm install -g @mixedbread/cliproxy-api &&
             cliproxy-api --port 8888 --log-path /var/log/cliproxy/access.log"

networks:
  default:
    name: magic-box-network
COMPOSE

log "Created docker-compose.yml"

cat > "${MAGIC_BOX_DIR}/config/.env.template" <<'ENV'
# Magic Box Configuration
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
MGREP_URL=http://127.0.0.1:8001

# CLIProxyAPI
CLIPROXY_PORT=8888
CLIPROXY_LOG_PATH=/var/log/cliproxy/access.log

# Logging
LOG_LEVEL=info
ENV

if [[ -n "${ANTHROPIC_API_KEY}" || -n "${OPENAI_API_KEY}" || -n "${GOOGLE_API_KEY}" ]]; then
  cat > "${MAGIC_BOX_DIR}/config/.env" <<EOF
# Magic Box Configuration - Auto-generated by setup script

# AI API Keys
${ANTHROPIC_API_KEY:+ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}}
${OPENAI_API_KEY:+OPENAI_API_KEY=${OPENAI_API_KEY}}
${GOOGLE_API_KEY:+GOOGLE_API_KEY=${GOOGLE_API_KEY}}

# Service Configuration
INFINITY_URL=http://127.0.0.1:7997
QDRANT_URL=http://127.0.0.1:6333
MGREP_URL=http://127.0.0.1:8001
CLIPROXY_PORT=8888
CLIPROXY_LOG_PATH=/var/log/cliproxy/access.log

LOG_LEVEL=info
EOF
  log "Created .env with API keys"
else
  cp "${MAGIC_BOX_DIR}/config/.env.template" "${MAGIC_BOX_DIR}/config/.env"
  log "Created .env from template (no API keys provided)"
fi

log_section "Installing AI CLI Tools"

install_npm_tool() {
  local package="$1"
  local name="$2"
  local global_name="${3:-$2}"

  if command -v "${global_name}" &> /dev/null; then
    log "${name} already installed: $(${global_name} --version 2>/dev/null || echo 'unknown')"
  else
    log "Installing ${name}..."
    npm install -g "${package}" || {
      warn "Failed to install ${name} via npm. Skipping..."
      return 1
    }
    if command -v "${global_name}" &> /dev/null; then
      log "${name} installed: $(${global_name} --version 2>/dev/null || echo 'installed')"
    else
      warn "${name} installation reported success but command not found"
    fi
  fi
}

# Claude Code CLI (Anthropic)
install_npm_tool "@anthropic-ai/claude-code" "Claude Code" "claude"

# Gemini CLI
install_npm_tool "@google-ai/generativelanguage" "Gemini CLI" "gemini" || \
  warn "Gemini CLI may not be available via npm. Manual setup may be required."

# OpenAI CLI
install_npm_tool "openai" "OpenAI CLI" "openai"

log "AI CLI tools installation complete"

log_section "Setting Up mgrep Wrapper"

mkdir -p /usr/local/lib/mgrep
cat > /usr/local/lib/mgrep/mgrep-wrapper.sh <<'MGREP_WRAPPER'
#!/bin/bash
# mgrep wrapper for Magic Box
# Uses local mgrep backend instead of cloud service

MGREP_URL="${MGREP_URL:-http://127.0.0.1:8001}"

usage() {
  echo "Usage: mgrep <query> [options]"
  echo ""
  echo "Semantic search using local Magic Box backend."
  echo ""
  echo "Environment:"
  echo "  MGREP_URL    Backend URL (default: http://127.0.0.1:8001)"
  exit 1
}

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
  usage
fi

if [[ -z "$1" ]]; then
  usage
fi

# Check backend is available
if ! curl -sf "$MGREP_URL/health" &>/dev/null; then
  echo "Error: mgrep backend not responding at $MGREP_URL"
  echo "Run: docker ps | grep mgrep-backend"
  exit 1
fi

# Perform search
QUERY="$1"
shift

curl -s "$MGREP_URL/v1/stores/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"top_k\": 10, \"search_options\": {\"rerank\": true}}" \
  | jq -r '.results[] | "\(.file) \(.score)"'
MGREP_WRAPPER

chmod +x /usr/local/lib/mgrep/mgrep-wrapper.sh
ln -sf /usr/local/lib/mgrep/mgrep-wrapper.sh /usr/local/bin/mgrep
log "Created mgrep wrapper at /usr/local/bin/mgrep"

log_section "Creating Magic Box CLI"

cat > "${MAGIC_BOX_DIR}/scripts/magic-box" <<'CLI'
#!/usr/bin/env bash
set -euo pipefail

MAGIC_BOX_DIR="/opt/magic-box"
COMPOSE_FILE="${MAGIC_BOX_DIR}/docker-compose.yml"
ENV_FILE="${MAGIC_BOX_DIR}/config/.env"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_banner() {
  echo -e "${BLUE}"
  cat <<'BANNER'
  ╔═════════════════════════════════════════════════════════╗
  ║                       MAGIC BOX                            ║
  ║            Multi-AI Orchestration Platform                 ║
  ╚═════════════════════════════════════════════════════════╝
BANNER
  echo -e "${NC}"
}

usage() {
  show_banner
  cat <<'USAGE'
Usage: magic-box <command> [options]

Commands:
  status          Show status of all services
  start           Start all Magic Box services
  stop            Stop all services
  restart         Restart all services
  logs [service]  Show logs (optionally for specific service)
  config          Edit configuration (.env file)
  test            Test API connections and services
  verify          Verify all components are working
  update          Pull latest container images
  help            Show this help

Service names: infinity, qdrant, mgrep-backend, traefik

Examples:
  magic-box status
  magic-box logs infinity
  magic-box verify
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

  # Check mgrep backend
  if curl -sf http://127.0.0.1:8001/health &>/dev/null; then
    echo -e "  mgrep-backend:          ${GREEN}✓ healthy${NC}"
  else
    echo -e "  mgrep-backend:          ${RED}✗ not responding${NC}"
  fi

  # Check Traefik
  if curl -sf http://127.0.0.1:8081/api/overview &>/dev/null; then
    echo -e "  Traefik (proxy):        ${GREEN}✓ healthy${NC}"
  else
    echo -e "  Traefik (proxy):        ${RED}✗ not responding${NC}"
  fi

  echo ""
  log "CLI Tools:"

  command -v claude &>/dev/null && echo -e "  Claude Code:    ${GREEN}✓ installed${NC}" || echo -e "  Claude Code:    ${RED}✗ not found${NC}"
  command -v gemini &>/dev/null && echo -e "  Gemini CLI:    ${GREEN}✓ installed${NC}" || echo -e "  Gemini CLI:    ${RED}✗ not found${NC}"
  command -v openai &>/dev/null && echo -e "  OpenAI CLI:     ${GREEN}✓ installed${NC}" || echo -e "  OpenAI CLI:     ${RED}✗ not found${NC}"
  command -v mgrep &>/dev/null && echo -e "  mgrep:          ${GREEN}✓ installed${NC}" || echo -e "  mgrep:          ${RED}✗ not found${NC}"

  echo ""
  log "Configuration:"
  if [[ -f "${ENV_FILE}" ]]; then
    if grep -q "^ANTHROPIC_API_KEY=sk-" "${ENV_FILE}" 2>/dev/null; then
      echo -e "  Anthropic API key:      ${GREEN}✓ configured${NC}"
    else
      echo -e "  Anthropic API key:      ${YELLOW}○ not set${NC}"
    fi
    if grep -q "^OPENAI_API_KEY=sk-" "${ENV_FILE}" 2>/dev/null; then
      echo -e "  OpenAI API key:         ${GREEN}✓ configured${NC}"
    else
      echo -e "  OpenAI API key:         ${YELLOW}○ not set${NC}"
    fi
    if grep -qE "^GOOGLE_API_KEY=.+" "${ENV_FILE}" 2>/dev/null; then
      echo -e "  Google API key:         ${GREEN}✓ configured${NC}"
    else
      echo -e "  Google API key:         ${YELLOW}○ not set${NC}"
    fi
  else
    warn "Config file not found. Run: magic-box config"
  fi
  echo ""
}

cmd_verify() {
  show_banner
  log "Verifying Magic Box Installation..."
  echo ""
  local errors=0

  # Check Docker services
  cd "${MAGIC_BOX_DIR}"
  if ! docker compose ps --quiet 2>/dev/null | grep -q .; then
    warn "No services running. Start with: magic-box start"
    errors=$((errors + 1))
  fi

  # Check each service
  echo "Checking services..."
  for service in infinity qdrant mgrep-backend traefik cliproxyapi; do
    if docker compose ps -q "${service}" 2>/dev/null | grep -q .; then
      echo -e "  ${service}: ${GREEN}running${NC}"
    else
      echo -e "  ${service}: ${RED}not running${NC}"
      errors=$((errors + 1))
    fi
  done

  # Check CLI tools
  echo ""
  echo "Checking CLI tools..."
  for tool in "Claude Code:claude" "Gemini CLI:gemini" "OpenAI CLI:openai" "mgrep:mgrep"; do
    local name="${tool%%:*}"
    local cmd="${tool##*:}"
    if command -v "${cmd}" &>/dev/null; then
      echo -e "  ${name}: ${GREEN}installed${NC}"
    else
      echo -e "  ${name}: ${YELLOW}not installed${NC}"
    fi
  done

  # Check directories
  echo ""
  echo "Checking directories..."
  for dir in config data logs prompts patterns scripts; do
    if [[ -d "${MAGIC_BOX_DIR}/${dir}" ]]; then
      echo -e "  ${dir}: ${GREEN}exists${NC}"
    else
      echo -e "  ${dir}: ${RED}missing${NC}"
      errors=$((errors + 1))
    fi
  done

  echo ""
  if [[ ${errors} -eq 0 ]]; then
    log "All verifications passed! ✓"
    return 0
  else
    warn "Found ${errors} issue(s). See details above."
    return 1
  fi
}

cmd_start() {
  log "Starting Magic Box services..."
  cd "${MAGIC_BOX_DIR}"
  docker compose up -d
  log "Services started. Run 'magic-box status' to verify."
}

cmd_stop() {
  log "Stopping Magic Box services..."
  cd "${MAGIC_BOX_DIR}"
  docker compose down
  log "Services stopped."
}

cmd_restart() {
  log "Restarting Magic Box services..."
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

case "${1:-status}" in
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
  verify)
    cmd_verify
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
CLI

chmod +x "${MAGIC_BOX_DIR}/scripts/magic-box"
ln -sf "${MAGIC_BOX_DIR}/scripts/magic-box" /usr/local/bin/magic-box
log "Created magic-box CLI tool"

cat > "${MAGIC_BOX_DIR}/CLAUDE.md" <<'MD'
# Magic Box Workspace

Multi-AI orchestration platform for 16x productivity.

## Quick Start

1. Configure API keys: `magic-box config`
2. Start services: `magic-box start`
3. Verify installation: `magic-box verify`
4. Check status: `magic-box status`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MAGIC BOX                     │
├─────────────────────────────────────────────────────┤
│                                                 │
│  SERVICES (Docker)                              │
│  ├── Infinity (embeddings)  :127.0.0.1:7997  │
│  ├── Qdrant (vectors)      :127.0.0.1:6333  │
│  ├── mgrep-backend (search):127.0.0.1:8001  │
│  └── Traefik (proxy)      :127.0.0.1:8080  │
│                                                 │
│  CLI TOOLS                                       │
│  ├── Claude Code (Anthropic)                     │
│  ├── Gemini CLI (Google)                         │
│  ├── OpenAI CLI (GPT/Codex)                    │
│  └── mgrep (semantic search)                     │
│                                                 │
└─────────────────────────────────────────────────────┘
```

## Patterns

1. Build-Audit-Fix: Build → Audit → Fix
2. Parallel Execution: Multiple workers on independent tasks
3. Hard Problem Voting: Multiple models vote on decisions

## Commands

- `magic-box status` - Check all services and CLI tools
- `magic-box start` - Start all services
- `magic-box stop` - Stop all services
- `magic-box logs` - View service logs
- `magic-box config` - Edit API keys
- `magic-box test` - Test API connections
- `magic-box verify` - Verify all components
- `magic-box update` - Update container images

## Configuration

Edit `/opt/magic-box/config/.env` to add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-openai-xxx
GOOGLE_API_KEY=AIzaSy-xxx
```

## Workspace Structure

```
/opt/magic-box/
├── docker-compose.yml    # Service definitions
├── config/.env          # API keys
├── data/               # Persistent storage
│   ├── qdrant-storage/
│   ├── infinity-cache/
│   └── mgrep-data/
├── prompts/            # Prompt templates
├── patterns/           # Workflow patterns
└── scripts/            # Management scripts
```
MD

log "Created workspace CLAUDE.md"

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  chown -R "${ADMIN_USER}:${ADMIN_USER}" "${MAGIC_BOX_DIR}"
fi

log_section "Starting Magic Box Services"

cd "${MAGIC_BOX_DIR}"
docker compose pull
docker compose up -d

log "Waiting for services to initialize..."
sleep 15

# Wait for services to be healthy
log "Verifying services are healthy..."
healthy=0
for i in {1..12}; do
  all_healthy=true
  for endpoint in "http://127.0.0.1:7997/health" "http://127.0.0.1:6333/healthz" "http://127.0.0.1:8081/api/overview"; do
    if ! curl -sf "${endpoint}" &>/dev/null; then
      all_healthy=false
      break
    fi
  done

  if [[ "${all_healthy}" == "true" ]]; then
    healthy=1
    break
  fi

  log "Waiting for services... (attempt ${i}/12)"
  sleep 5
done

if [[ "${healthy}" -eq 1 ]]; then
  log "Services are healthy"
else
  warn "Services may still be initializing. Check with: magic-box status"
fi

log_section "Running Full Verification"

sudo -u "${ADMIN_USER}" /usr/local/bin/magic-box verify || {
  warn "Verification found issues. See details above."
}

log_section "Installation Complete!"

VM_IP=$(hostname -I | awk '{print $1}')

cat <<EOF

 ══════════════════════════════════════════════════════════════
                      MAGIC BOX READY
 ══════════════════════════════════════════════════════════════

EOF

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  echo "SSH Access:"
  echo "  ssh ${ADMIN_USER}@${VM_IP}"
  echo ""
fi

cat <<EOF
Quick Start:
  1. Connect: ssh ${ADMIN_USER}@${VM_IP}
  2. Verify:   magic-box verify
  3. Config:   magic-box config (add API keys if not set)
  4. Status:   magic-box status
  5. Work!     Start using CLI tools: claude, gemini, openai

Services (localhost only):
  - Infinity (embeddings): 127.0.0.1:7997
  - Qdrant (vectors):      127.0.0.1:6333
  - mgrep-backend:          127.0.0.1:8001
  - Traefik dashboard:     127.0.0.1:8081

CLI Tools Available:
  - claude    (Claude Code CLI)
  - gemini    (Gemini CLI)
  - openai    (OpenAI CLI)
  - mgrep     (Semantic search)

Workspace: ${MAGIC_BOX_DIR}

Documentation:
  - /opt/magic-box/CLAUDE.md
  - Run: magic-box help

 ══════════════════════════════════════════════════════════════
EOF
