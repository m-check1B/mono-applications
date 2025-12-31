#!/usr/bin/env bash
# Lab by Kraliki Automated VM Provisioning Script
# End-to-end automation: Create VM -> Provision OS -> Deploy Stack -> Return Credentials
#
# This script automates the entire customer onboarding process:
# 1. Creates a Hetzner Cloud VM via API
# 2. Waits for VM to be ready
# 3. Provisions the OS with security hardening
# 4. Deploys the Lab by Kraliki stack
# 5. Outputs connection credentials
#
# Prerequisites:
#   - HCLOUD_TOKEN environment variable (Hetzner API token)
#   - SSH key registered in Hetzner Cloud
#   - curl, jq installed on the control machine
#
# Usage:
#   ./auto-provision.sh --customer acme-corp --ssh-key admin-key
#   ./auto-provision.sh --customer acme-corp --ssh-key admin-key --size cpx41 --location ash
#
# Output (JSON):
#   {
#     "status": "success",
#     "vm_name": "magicbox-acme-corp",
#     "ip": "1.2.3.4",
#     "ssh_user": "magicbox",
#     "ssh_command": "ssh magicbox@1.2.3.4"
#   }
#
set -euo pipefail

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
CUSTOMER_NAME=""
SSH_KEY_NAME=""
VM_SIZE="cpx31"
LOCATION="nbg1"
IMAGE="ubuntu-22.04"
ADMIN_USER="magicbox"
OUTPUT_FORMAT="text"
DRY_RUN=0
VERBOSE=0
WAIT_TIMEOUT=600  # 10 minutes

# Colors (disabled for JSON output)
use_colors() {
  [[ "${OUTPUT_FORMAT}" == "text" ]]
}

RED=""
GREEN=""
YELLOW=""
BLUE=""
NC=""

init_colors() {
  if use_colors; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
  fi
}

usage() {
  cat <<'USAGE'
Lab by Kraliki Automated VM Provisioning

Creates and provisions a complete Lab by Kraliki environment automatically.

Usage:
  ./auto-provision.sh --customer <name> --ssh-key <key-name> [options]

Required:
  --customer NAME       Customer identifier (alphanumeric, used in VM name)
  --ssh-key KEY         Name of SSH key registered in Hetzner Cloud

Options:
  --size SIZE           VM size (default: cpx31)
                        cpx21 (~$10/mo), cpx31 (~$20/mo), cpx41 (~$35/mo)
  --location LOC        Datacenter location (default: nbg1)
                        EU: nbg1, fsn1, hel1
                        US: ash, hil
  --admin-user USER     Admin username (default: magicbox)
  --output FORMAT       Output format: text or json (default: text)
  --dry-run             Show what would be done without doing it
  --verbose             Show detailed progress
  --timeout SECONDS     Wait timeout for VM readiness (default: 600)
  -h, --help            Show this help

Environment:
  HCLOUD_TOKEN          Required. Hetzner Cloud API token

Examples:
  # Basic provisioning
  export HCLOUD_TOKEN="your-token"
  ./auto-provision.sh --customer acme --ssh-key admin-key

  # US deployment with larger VM, JSON output
  ./auto-provision.sh --customer bigcorp --ssh-key admin-key \
    --size cpx41 --location ash --output json

  # Preview without creating
  ./auto-provision.sh --customer test --ssh-key admin-key --dry-run

USAGE
}

log() {
  if use_colors; then
    echo -e "${GREEN}[+]${NC} $1" >&2
  fi
}

log_verbose() {
  if [[ "${VERBOSE}" -eq 1 ]] && use_colors; then
    echo -e "${BLUE}[.]${NC} $1" >&2
  fi
}

warn() {
  if use_colors; then
    echo -e "${YELLOW}[!]${NC} $1" >&2
  fi
}

fail() {
  if [[ "${OUTPUT_FORMAT}" == "json" ]]; then
    echo "{\"status\": \"error\", \"message\": \"$1\"}"
  else
    echo -e "${RED}[x]${NC} $1" >&2
  fi
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --customer)
      CUSTOMER_NAME="${2:-}"
      shift 2
      ;;
    --ssh-key)
      SSH_KEY_NAME="${2:-}"
      shift 2
      ;;
    --size)
      VM_SIZE="${2:-}"
      shift 2
      ;;
    --location)
      LOCATION="${2:-}"
      shift 2
      ;;
    --admin-user)
      ADMIN_USER="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT_FORMAT="${2:-text}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --verbose)
      VERBOSE=1
      shift
      ;;
    --timeout)
      WAIT_TIMEOUT="${2:-600}"
      shift 2
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

init_colors

# Validate required arguments
[[ -z "${CUSTOMER_NAME}" ]] && fail "--customer is required"
[[ -z "${SSH_KEY_NAME}" ]] && fail "--ssh-key is required"

# Validate customer name (alphanumeric and hyphens only)
if ! [[ "${CUSTOMER_NAME}" =~ ^[a-zA-Z0-9-]+$ ]]; then
  fail "Customer name must be alphanumeric with hyphens only"
fi

# Check for Hetzner token
if [[ -z "${HCLOUD_TOKEN:-}" ]]; then
  fail "HCLOUD_TOKEN environment variable is required"
fi

# Check dependencies
for cmd in curl jq ssh-keygen; do
  if ! command -v "${cmd}" &> /dev/null; then
    fail "Required command not found: ${cmd}"
  fi
done

# Hetzner API base URL
HCLOUD_API="https://api.hetzner.cloud/v1"

# API request helper
hcloud_api() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"

  local args=(-sf -X "${method}")
  args+=(-H "Authorization: Bearer ${HCLOUD_TOKEN}")
  args+=(-H "Content-Type: application/json")

  if [[ -n "${data}" ]]; then
    args+=(-d "${data}")
  fi

  curl "${args[@]}" "${HCLOUD_API}${endpoint}"
}

# Generate VM name
VM_NAME="magicbox-${CUSTOMER_NAME}"

log "Starting automated provisioning for: ${CUSTOMER_NAME}"
log_verbose "VM Name: ${VM_NAME}"
log_verbose "Size: ${VM_SIZE}, Location: ${LOCATION}"

# Check if VM already exists
log_verbose "Checking for existing VM..."
existing_vm=$(hcloud_api GET "/servers?name=${VM_NAME}" 2>/dev/null || echo '{"servers":[]}')
if [[ $(echo "${existing_vm}" | jq '.servers | length') -gt 0 ]]; then
  fail "VM '${VM_NAME}' already exists"
fi

# Get SSH key ID
log_verbose "Looking up SSH key: ${SSH_KEY_NAME}"
ssh_keys_response=$(hcloud_api GET "/ssh_keys?name=${SSH_KEY_NAME}" 2>/dev/null || echo '{"ssh_keys":[]}')
SSH_KEY_ID=$(echo "${ssh_keys_response}" | jq -r '.ssh_keys[0].id // empty')

if [[ -z "${SSH_KEY_ID}" ]]; then
  fail "SSH key '${SSH_KEY_NAME}' not found in Hetzner Cloud"
fi
log_verbose "SSH Key ID: ${SSH_KEY_ID}"

# Create cloud-init user data
read -r -d '' CLOUD_INIT <<'CLOUD_INIT_DATA' || true
#cloud-config
package_update: true
package_upgrade: true

packages:
  - ca-certificates
  - curl
  - git
  - gnupg
  - jq
  - lsb-release
  - ufw
  - fail2ban
  - htop
  - vim
  - tmux

write_files:
  - path: /opt/magic-box-init.sh
    permissions: '0755'
    content: |
      #!/bin/bash
      set -e

      # Install Docker
      install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      chmod a+r /etc/apt/keyrings/docker.gpg

      CODENAME=$(. /etc/os-release && echo ${VERSION_CODENAME})
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" > /etc/apt/sources.list.d/docker.list

      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
      systemctl enable docker

      # Configure firewall
      ufw default deny incoming
      ufw default allow outgoing
      ufw allow OpenSSH
      ufw --force enable

      # Enable fail2ban
      systemctl enable fail2ban
      systemctl start fail2ban

      # Harden SSH
      sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
      sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
      systemctl reload ssh

      # Signal completion
      touch /var/lib/cloud/instance/magic-box-init-done

  - path: /etc/motd
    content: |

      =============================================
               LAB BY KRALIKI - Multi-AI Platform
      =============================================
       Run 'magic-box status' to check services
       Run 'magic-box config' to set API keys
      =============================================


runcmd:
  - /opt/magic-box-init.sh
CLOUD_INIT_DATA

# Base64 encode cloud-init for API
CLOUD_INIT_B64=$(echo "${CLOUD_INIT}" | base64 -w0)

if [[ "${DRY_RUN}" -eq 1 ]]; then
  log "DRY RUN - Would create VM with:"
  echo "  Name: ${VM_NAME}"
  echo "  Type: ${VM_SIZE}"
  echo "  Location: ${LOCATION}"
  echo "  Image: ${IMAGE}"
  echo "  SSH Key: ${SSH_KEY_NAME} (ID: ${SSH_KEY_ID})"
  exit 0
fi

# Create the VM
log "Creating VM: ${VM_NAME}..."

create_payload=$(jq -n \
  --arg name "${VM_NAME}" \
  --arg server_type "${VM_SIZE}" \
  --arg location "${LOCATION}" \
  --arg image "${IMAGE}" \
  --argjson ssh_keys "[${SSH_KEY_ID}]" \
  --arg user_data "${CLOUD_INIT}" \
  '{
    name: $name,
    server_type: $server_type,
    location: $location,
    image: $image,
    ssh_keys: $ssh_keys,
    user_data: $user_data,
    labels: {
      product: "magic-box",
      customer: $name | split("-")[1:] | join("-"),
      managed: "auto-provision"
    },
    start_after_create: true
  }')

create_response=$(hcloud_api POST "/servers" "${create_payload}" 2>/dev/null) || fail "Failed to create VM"

# Extract server info
SERVER_ID=$(echo "${create_response}" | jq -r '.server.id')
VM_IP=$(echo "${create_response}" | jq -r '.server.public_net.ipv4.ip')

if [[ -z "${SERVER_ID}" || "${SERVER_ID}" == "null" ]]; then
  error_msg=$(echo "${create_response}" | jq -r '.error.message // "Unknown error"')
  fail "Failed to create VM: ${error_msg}"
fi

log "VM created with ID: ${SERVER_ID}, IP: ${VM_IP}"

# Wait for VM to be running
log "Waiting for VM to be running..."
start_time=$(date +%s)
while true; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))

  if [[ ${elapsed} -gt ${WAIT_TIMEOUT} ]]; then
    fail "Timeout waiting for VM to be ready"
  fi

  server_status=$(hcloud_api GET "/servers/${SERVER_ID}" 2>/dev/null | jq -r '.server.status')
  log_verbose "VM status: ${server_status} (${elapsed}s elapsed)"

  if [[ "${server_status}" == "running" ]]; then
    break
  fi

  sleep 5
done

log "VM is running"

# Wait for SSH to be available
log "Waiting for SSH to be available..."
ssh_ready=0
for i in {1..60}; do
  if timeout 5 bash -c "echo > /dev/tcp/${VM_IP}/22" 2>/dev/null; then
    ssh_ready=1
    break
  fi
  log_verbose "SSH not ready yet (attempt ${i}/60)"
  sleep 5
done

if [[ ${ssh_ready} -eq 0 ]]; then
  fail "SSH did not become available within timeout"
fi

log "SSH is available"

# Wait for cloud-init to complete
log "Waiting for cloud-init to complete..."
for i in {1..60}; do
  if ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=10 \
      "root@${VM_IP}" "test -f /var/lib/cloud/instance/magic-box-init-done" 2>/dev/null; then
    break
  fi
  log_verbose "Cloud-init still running (attempt ${i}/60)"
  sleep 10
done

log "Cloud-init complete"

# Deploy Lab by Kraliki stack via SSH
log "Deploying Lab by Kraliki stack..."

# Create deploy script
read -r -d '' DEPLOY_SCRIPT <<'DEPLOY_EOF' || true
#!/bin/bash
set -e

ADMIN_USER="$1"
MAGIC_BOX_DIR="/opt/magic-box"

# Create admin user
if ! id -u "${ADMIN_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${ADMIN_USER}"
fi
usermod -aG sudo,docker "${ADMIN_USER}"
echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${ADMIN_USER}"
chmod 440 "/etc/sudoers.d/${ADMIN_USER}"

# Copy SSH key from root to admin user
mkdir -p "/home/${ADMIN_USER}/.ssh"
cp /root/.ssh/authorized_keys "/home/${ADMIN_USER}/.ssh/"
chown -R "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
chmod 700 "/home/${ADMIN_USER}/.ssh"
chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"

# Create Lab by Kraliki directory structure
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

# Anthropic (Claude) - Required
ANTHROPIC_API_KEY=

# OpenAI (GPT/Codex) - Optional
OPENAI_API_KEY=

# Google (Gemini) - Optional
GOOGLE_API_KEY=
ENV

# Create magic-box CLI
cat > "${MAGIC_BOX_DIR}/scripts/magic-box" <<'CLI'
#!/usr/bin/env bash
set -euo pipefail
MAGIC_BOX_DIR="/opt/magic-box"

case "${1:-status}" in
  status)
    echo "Lab by Kraliki Status:"
    cd "${MAGIC_BOX_DIR}" && docker compose ps 2>/dev/null || echo "Services not running"
    echo ""
    echo "Health:"
    curl -sf http://127.0.0.1:7997/health &>/dev/null && echo "  Infinity: OK" || echo "  Infinity: DOWN"
    curl -sf http://127.0.0.1:6333/healthz &>/dev/null && echo "  Qdrant: OK" || echo "  Qdrant: DOWN"
    ;;
  start) cd "${MAGIC_BOX_DIR}" && docker compose up -d ;;
  stop) cd "${MAGIC_BOX_DIR}" && docker compose down ;;
  restart) cd "${MAGIC_BOX_DIR}" && docker compose restart ;;
  logs) cd "${MAGIC_BOX_DIR}" && docker compose logs -f ${2:-} ;;
  config)
    [[ ! -f "${MAGIC_BOX_DIR}/config/.env" ]] && cp "${MAGIC_BOX_DIR}/config/.env.template" "${MAGIC_BOX_DIR}/config/.env"
    ${EDITOR:-nano} "${MAGIC_BOX_DIR}/config/.env"
    ;;
  update) cd "${MAGIC_BOX_DIR}" && docker compose pull ;;
  *) echo "Usage: magic-box {status|start|stop|restart|logs|config|update}" ;;
esac
CLI

chmod +x "${MAGIC_BOX_DIR}/scripts/magic-box"
ln -sf "${MAGIC_BOX_DIR}/scripts/magic-box" /usr/local/bin/magic-box

# Create CLAUDE.md
cat > "${MAGIC_BOX_DIR}/CLAUDE.md" <<'MD'
# Lab by Kraliki Workspace

Multi-AI orchestration platform for 16x productivity.

## Quick Start

1. Configure API keys: `magic-box config`
2. Check status: `magic-box status`
3. View logs: `magic-box logs`

## Patterns

- Build-Audit-Fix: Build -> Audit -> Incorporate feedback
- Parallel Execution: Multiple workers on independent tasks
- Hard Problem Voting: Multiple models vote on decisions
MD

# Set ownership
chown -R "${ADMIN_USER}:${ADMIN_USER}" "${MAGIC_BOX_DIR}"

# Start services
cd "${MAGIC_BOX_DIR}"
docker compose pull
docker compose up -d

echo "Lab by Kraliki deployed successfully"
DEPLOY_EOF

# Execute deploy script on VM
echo "${DEPLOY_SCRIPT}" | ssh -o StrictHostKeyChecking=no "root@${VM_IP}" "cat > /tmp/deploy.sh && chmod +x /tmp/deploy.sh && /tmp/deploy.sh ${ADMIN_USER}"

log "Stack deployment complete"

# Wait for services to be healthy
log "Waiting for services to be healthy..."
for i in {1..30}; do
  if ssh -o StrictHostKeyChecking=no "${ADMIN_USER}@${VM_IP}" "curl -sf http://127.0.0.1:6333/healthz" 2>/dev/null; then
    break
  fi
  sleep 5
done

log "Provisioning complete!"

# Output results
if [[ "${OUTPUT_FORMAT}" == "json" ]]; then
  jq -n \
    --arg status "success" \
    --arg vm_name "${VM_NAME}" \
    --arg vm_id "${SERVER_ID}" \
    --arg ip "${VM_IP}" \
    --arg ssh_user "${ADMIN_USER}" \
    --arg ssh_command "ssh ${ADMIN_USER}@${VM_IP}" \
    --arg size "${VM_SIZE}" \
    --arg location "${LOCATION}" \
    '{
      status: $status,
      vm_name: $vm_name,
      vm_id: $vm_id,
      ip: $ip,
      ssh_user: $ssh_user,
      ssh_command: $ssh_command,
      size: $size,
      location: $location,
      next_steps: [
        "SSH to the VM: ssh " + $ssh_user + "@" + $ip,
        "Configure API keys: magic-box config",
        "Check status: magic-box status"
      ]
    }'
else
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "                  LAB BY KRALIKI PROVISIONED"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "  Customer:     ${CUSTOMER_NAME}"
  echo "  VM Name:      ${VM_NAME}"
  echo "  VM ID:        ${SERVER_ID}"
  echo "  IP Address:   ${VM_IP}"
  echo "  Size:         ${VM_SIZE}"
  echo "  Location:     ${LOCATION}"
  echo ""
  echo "  SSH Command:  ssh ${ADMIN_USER}@${VM_IP}"
  echo ""
  echo "  Next Steps:"
  echo "    1. SSH to the VM"
  echo "    2. Run: magic-box config (to add API keys)"
  echo "    3. Run: magic-box status (to verify services)"
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
fi
