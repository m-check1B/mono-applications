#!/usr/bin/env bash
# Lab by Kraliki One-Click Installer
# Run on a fresh Ubuntu 22.04 VM to set up Lab by Kraliki
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/verduona/magic-box/main/scripts/install.sh | sudo bash
#
# Or with options:
#   curl -fsSL ... | sudo bash -s -- --admin-user myuser --ssh-key "ssh-ed25519 AAAA..."
#
set -euo pipefail

VERSION="1.0.0"
MAGIC_BOX_DIR="/opt/magic-box"

# Configuration (can be overridden via arguments)
ADMIN_USER="${ADMIN_USER:-magicbox}"
SSH_PUB_KEY="${SSH_PUB_KEY:-}"
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
                         Installer v${VERSION}

BANNER
  echo -e "${NC}"
}

usage() {
  show_banner
  cat <<'USAGE'
Usage:
  curl -fsSL <url>/install.sh | sudo bash
  curl -fsSL <url>/install.sh | sudo bash -s -- [options]

Options:
  --admin-user USER     Admin username (default: magicbox)
  --ssh-key KEY         SSH public key for admin user
  --ssh-key-file PATH   Read SSH key from file
  --skip-user           Skip user creation
  -h, --help            Show this help

Environment Variables:
  ADMIN_USER            Admin username
  SSH_PUB_KEY           SSH public key

Example:
  # Interactive (will prompt for SSH key)
  curl -fsSL https://example.com/install.sh | sudo bash

  # Non-interactive
  curl -fsSL https://example.com/install.sh | sudo bash -s -- \
    --admin-user myuser \
    --ssh-key "ssh-ed25519 AAAA..."

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

# Start installation
show_banner

# Check root
if [[ "${EUID}" -ne 0 ]]; then
  fail "This script must be run as root. Use: curl ... | sudo bash"
fi

# Check OS
log_section "Checking System Requirements"

if [[ -f /etc/os-release ]]; then
  # shellcheck disable=SC1091
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
  fail "Unsupported architecture: ${ARCH}. Lab by Kraliki requires x86_64 or aarch64."
fi

# Check memory
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
log "Memory: ${TOTAL_MEM} MB"
if [[ "${TOTAL_MEM}" -lt 4000 ]]; then
  warn "Recommended minimum memory is 4GB. You have ${TOTAL_MEM}MB."
fi

# Prompt for SSH key if not provided and not skipping user setup
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
  tmux

log "System packages installed"

log_section "Installing Docker"

# Check if Docker is already installed
if command -v docker &> /dev/null; then
  log "Docker already installed: $(docker --version)"
else
  # Install Docker
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

# Verify Docker Compose
if docker compose version &> /dev/null; then
  log "Docker Compose: $(docker compose version --short)"
else
  fail "Docker Compose plugin not found"
fi

log_section "Configuring Security"

# UFW Firewall
log "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH

# Don't enable yet if this is initial setup (might lock out)
if [[ -f /var/lib/ufw/user.rules ]]; then
  ufw --force enable
  log "Firewall enabled (SSH only)"
else
  log "Firewall rules set (enable manually with: ufw enable)"
fi

# Fail2ban
systemctl enable fail2ban
systemctl start fail2ban
log "Fail2ban enabled"

# Harden SSH
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

# Only reload if sshd is running
if systemctl is-active --quiet ssh; then
  systemctl reload ssh
  log "SSH hardened (key-only auth)"
fi

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  log_section "Creating Admin User: ${ADMIN_USER}"

  # Create user if doesn't exist
  if id -u "${ADMIN_USER}" &>/dev/null; then
    log "User ${ADMIN_USER} already exists"
  else
    useradd -m -s /bin/bash "${ADMIN_USER}"
    log "Created user: ${ADMIN_USER}"
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
  log "SSH key configured for ${ADMIN_USER}"
fi

log_section "Setting Up Lab by Kraliki"

# Create directory structure
mkdir -p "${MAGIC_BOX_DIR}"/{config,data,logs,prompts,patterns,scripts}
mkdir -p "${MAGIC_BOX_DIR}/data"/{qdrant-storage,infinity-cache}

# Create docker-compose.yml
cat > "${MAGIC_BOX_DIR}/docker-compose.yml" <<'COMPOSE'
version: '3.8'

services:
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

networks:
  default:
    name: magic-box-network
COMPOSE

# Create .env template
cat > "${MAGIC_BOX_DIR}/config/.env.template" <<'ENV'
# Lab by Kraliki Configuration
# Copy to .env and add your API keys

# Anthropic (Claude) - Required for orchestration
ANTHROPIC_API_KEY=

# OpenAI (GPT/Codex) - Optional
OPENAI_API_KEY=

# Google (Gemini) - Optional
GOOGLE_API_KEY=

# Service URLs (usually no changes needed)
INFINITY_URL=http://127.0.0.1:7997
QDRANT_URL=http://127.0.0.1:6333
ENV

# Create magic-box CLI
cat > "${MAGIC_BOX_DIR}/scripts/magic-box" <<'CLI'
#!/usr/bin/env bash
set -euo pipefail

MAGIC_BOX_DIR="/opt/magic-box"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_banner() {
  echo -e "${BLUE}"
  echo "  ╔═══════════════════════════════════════════════════════════╗"
  echo "  ║                       LAB BY KRALIKI                            ║"
  echo "  ║            Multi-AI Orchestration Platform                 ║"
  echo "  ╚═══════════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

case "${1:-status}" in
  status)
    show_banner
    echo -e "${GREEN}Service Status:${NC}"
    cd "${MAGIC_BOX_DIR}"
    docker compose ps 2>/dev/null || echo "Services not running"
    echo ""
    echo -e "${GREEN}Health Checks:${NC}"
    curl -sf http://127.0.0.1:7997/health &>/dev/null && echo -e "  Infinity: ${GREEN}✓${NC}" || echo -e "  Infinity: ${RED}✗${NC}"
    curl -sf http://127.0.0.1:6333/healthz &>/dev/null && echo -e "  Qdrant:   ${GREEN}✓${NC}" || echo -e "  Qdrant:   ${RED}✗${NC}"
    ;;
  start)
    cd "${MAGIC_BOX_DIR}" && docker compose up -d
    echo -e "${GREEN}Services started${NC}"
    ;;
  stop)
    cd "${MAGIC_BOX_DIR}" && docker compose down
    echo -e "${GREEN}Services stopped${NC}"
    ;;
  restart)
    cd "${MAGIC_BOX_DIR}" && docker compose restart
    echo -e "${GREEN}Services restarted${NC}"
    ;;
  logs)
    cd "${MAGIC_BOX_DIR}" && docker compose logs -f ${2:-}
    ;;
  config)
    [[ ! -f "${MAGIC_BOX_DIR}/config/.env" ]] && cp "${MAGIC_BOX_DIR}/config/.env.template" "${MAGIC_BOX_DIR}/config/.env"
    ${EDITOR:-nano} "${MAGIC_BOX_DIR}/config/.env"
    ;;
  update)
    cd "${MAGIC_BOX_DIR}" && docker compose pull && echo -e "${GREEN}Images updated. Run 'magic-box restart'${NC}"
    ;;
  *)
    echo "Usage: magic-box {status|start|stop|restart|logs|config|update}"
    ;;
esac
CLI

chmod +x "${MAGIC_BOX_DIR}/scripts/magic-box"
ln -sf "${MAGIC_BOX_DIR}/scripts/magic-box" /usr/local/bin/magic-box

# Create CLAUDE.md
cat > "${MAGIC_BOX_DIR}/CLAUDE.md" <<'MD'
# Lab by Kraliki Workspace

Multi-AI orchestration platform for 16x productivity.

## Commands

- `magic-box status` - Check services
- `magic-box config` - Edit API keys
- `magic-box logs` - View logs

## Structure

```
/opt/magic-box/
├── config/.env      # API keys
├── data/            # Persistent storage
├── prompts/         # Prompt templates
└── patterns/        # Workflow patterns
```

## Patterns

1. Build-Audit-Fix: Build → Audit → Fix
2. Parallel Execution: Multiple workers
3. Hard Problem Voting: Model consensus
MD

# Set ownership
if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  chown -R "${ADMIN_USER}:${ADMIN_USER}" "${MAGIC_BOX_DIR}"
fi

log "Lab by Kraliki directory structure created"

log_section "Starting Services"

cd "${MAGIC_BOX_DIR}"
docker compose pull
docker compose up -d

log "Waiting for services to initialize..."
sleep 15

# Check health
HEALTHY=0
for i in {1..6}; do
  if curl -sf http://127.0.0.1:6333/healthz &>/dev/null; then
    HEALTHY=1
    break
  fi
  sleep 5
done

if [[ "${HEALTHY}" -eq 1 ]]; then
  log "Services are healthy"
else
  warn "Services may still be initializing. Check with: magic-box status"
fi

log_section "Installation Complete!"

VM_IP=$(hostname -I | awk '{print $1}')

cat <<EOF

════════════════════════════════════════════════════════════════
                     LAB BY KRALIKI READY
════════════════════════════════════════════════════════════════

EOF

if [[ "${SKIP_USER_SETUP}" -eq 0 ]]; then
  echo "SSH Access:"
  echo "  ssh ${ADMIN_USER}@${VM_IP}"
  echo ""
fi

cat <<EOF
Quick Start:
  1. Configure API keys: magic-box config
  2. Check status:       magic-box status
  3. View logs:          magic-box logs

Services (localhost only):
  Infinity (embeddings): 127.0.0.1:7997
  Qdrant (vectors):      127.0.0.1:6333
  Traefik dashboard:     127.0.0.1:8081

Workspace: ${MAGIC_BOX_DIR}

════════════════════════════════════════════════════════════════

EOF
