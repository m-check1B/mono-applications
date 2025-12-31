#!/usr/bin/env bash
# Lab by Kraliki VM Creation Script
# Creates a Hetzner Cloud VM optimized for Lab by Kraliki deployment
#
# Prerequisites:
#   - hcloud CLI installed and authenticated (https://github.com/hetznercloud/cli)
#   - SSH key registered in Hetzner Cloud
#
# Usage:
#   ./create-vm.sh --name customer-abc --ssh-key my-key-name
#   ./create-vm.sh --name customer-abc --ssh-key my-key-name --size cpx41 --location nbg1
#
set -euo pipefail

# Default values
VM_NAME=""
SSH_KEY_NAME=""
VM_SIZE="cpx31"  # 4 vCPU, 8GB RAM, 160GB NVMe (recommended for 1-3 users)
LOCATION="nbg1"  # Nuremberg, Germany (EU)
IMAGE="ubuntu-22.04"
LABELS="product=magic-box,managed=true"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
  cat <<'USAGE'
Lab by Kraliki VM Creation Script

Creates a Hetzner Cloud VM pre-configured for Lab by Kraliki deployment.

Usage:
  ./create-vm.sh --name <vm-name> --ssh-key <key-name> [options]

Required:
  --name NAME           Unique VM name (e.g., customer-acme, magicbox-prod-01)
  --ssh-key KEY         Name of SSH key registered in Hetzner Cloud

Options:
  --size SIZE           VM size (default: cpx31)
                        Available: cpx11, cpx21, cpx31, cpx41, cpx51
                        Recommended: cpx31 (1-3 users), cpx41 (3-6 users)
  --location LOC        Datacenter location (default: nbg1)
                        EU: nbg1 (Nuremberg), fsn1 (Falkenstein), hel1 (Helsinki)
                        US: ash (Ashburn), hil (Hillsboro)
  --image IMAGE         OS image (default: ubuntu-22.04)
  --labels LABELS       Comma-separated key=value labels
  --dry-run             Show what would be created without doing it
  -h, --help            Show this help

Examples:
  # Basic EU deployment
  ./create-vm.sh --name client-acme --ssh-key admin-key

  # US deployment with larger VM
  ./create-vm.sh --name client-bigcorp --ssh-key admin-key --size cpx41 --location ash

  # Preview creation
  ./create-vm.sh --name test-vm --ssh-key admin-key --dry-run

Pricing (approx as of Dec 2024):
  cpx11 (2 vCPU, 2GB):   ~€5/mo
  cpx21 (3 vCPU, 4GB):   ~€10/mo
  cpx31 (4 vCPU, 8GB):   ~€20/mo (recommended)
  cpx41 (8 vCPU, 16GB):  ~€35/mo
  cpx51 (16 vCPU, 32GB): ~€70/mo

USAGE
}

log() {
  echo -e "${GREEN}==> ${NC}$1"
}

warn() {
  echo -e "${YELLOW}==> WARNING: ${NC}$1"
}

fail() {
  echo -e "${RED}==> ERROR: ${NC}$1" >&2
  exit 1
}

DRY_RUN=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      VM_NAME="${2:-}"
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
    --image)
      IMAGE="${2:-}"
      shift 2
      ;;
    --labels)
      LABELS="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
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

# Validate required arguments
[[ -z "${VM_NAME}" ]] && fail "--name is required"
[[ -z "${SSH_KEY_NAME}" ]] && fail "--ssh-key is required"

# Check hcloud CLI is installed
if ! command -v hcloud &> /dev/null; then
  fail "hcloud CLI not found. Install from: https://github.com/hetznercloud/cli"
fi

# Check hcloud is authenticated
if ! hcloud server list &> /dev/null; then
  fail "hcloud not authenticated. Run: hcloud context create <name>"
fi

# Verify SSH key exists
log "Verifying SSH key '${SSH_KEY_NAME}' exists in Hetzner Cloud..."
if ! hcloud ssh-key describe "${SSH_KEY_NAME}" &> /dev/null; then
  fail "SSH key '${SSH_KEY_NAME}' not found in Hetzner Cloud. Add it first with: hcloud ssh-key create --name ${SSH_KEY_NAME} --public-key-from-file ~/.ssh/id_ed25519.pub"
fi

# Check if VM already exists
if hcloud server describe "${VM_NAME}" &> /dev/null; then
  fail "VM '${VM_NAME}' already exists. Choose a different name or delete the existing VM."
fi

# Create cloud-init user data for initial setup
CLOUD_INIT=$(cat <<'CLOUD_INIT_EOF'
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

runcmd:
  # Install Docker
  - install -m 0755 -d /etc/apt/keyrings
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  - chmod a+r /etc/apt/keyrings/docker.gpg
  - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${VERSION_CODENAME}) stable" > /etc/apt/sources.list.d/docker.list
  - apt-get update
  - apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  - systemctl enable docker
  # Configure firewall (SSH only by default)
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw allow OpenSSH
  - ufw --force enable
  # Enable fail2ban
  - systemctl enable fail2ban
  - systemctl start fail2ban
  # Prepare Lab by Kraliki directory
  - mkdir -p /opt/magic-box
  - chmod 755 /opt/magic-box
  # Signal completion
  - touch /var/lib/cloud/instance/magic-box-ready

write_files:
  - path: /etc/motd
    content: |

      ╔═══════════════════════════════════════════════════════════╗
      ║                     LAB BY KRALIKI                              ║
      ║             Multi-AI Orchestration Platform                ║
      ╠═══════════════════════════════════════════════════════════╣
      ║  Run 'magic-box status' to check system status             ║
      ║  Run 'magic-box help' for available commands               ║
      ╚═══════════════════════════════════════════════════════════╝

CLOUD_INIT_EOF
)

log "Creating VM with the following configuration:"
echo "  Name:     ${VM_NAME}"
echo "  Size:     ${VM_SIZE}"
echo "  Location: ${LOCATION}"
echo "  Image:    ${IMAGE}"
echo "  SSH Key:  ${SSH_KEY_NAME}"
echo "  Labels:   ${LABELS}"
echo ""

if [[ "${DRY_RUN}" -eq 1 ]]; then
  warn "DRY RUN - no VM will be created"
  echo ""
  echo "Would execute:"
  echo "  hcloud server create \\"
  echo "    --name ${VM_NAME} \\"
  echo "    --type ${VM_SIZE} \\"
  echo "    --location ${LOCATION} \\"
  echo "    --image ${IMAGE} \\"
  echo "    --ssh-key ${SSH_KEY_NAME} \\"
  echo "    --label ${LABELS//,/ --label } \\"
  echo "    --user-data-from-file <cloud-init>"
  exit 0
fi

# Create temporary file for cloud-init
CLOUD_INIT_FILE=$(mktemp)
echo "${CLOUD_INIT}" > "${CLOUD_INIT_FILE}"
trap "rm -f ${CLOUD_INIT_FILE}" EXIT

log "Creating VM '${VM_NAME}'..."

# Create the VM
hcloud server create \
  --name "${VM_NAME}" \
  --type "${VM_SIZE}" \
  --location "${LOCATION}" \
  --image "${IMAGE}" \
  --ssh-key "${SSH_KEY_NAME}" \
  --label "product=magic-box" \
  --label "managed=true" \
  --user-data-from-file "${CLOUD_INIT_FILE}"

# Get VM IP
VM_IP=$(hcloud server ip "${VM_NAME}")

log "VM created successfully!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  VM Name: ${VM_NAME}"
echo "  IP:      ${VM_IP}"
echo "  Size:    ${VM_SIZE}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
log "The VM is initializing (takes 2-3 minutes for cloud-init to complete)"
echo ""
echo "Next steps:"
echo "  1. Wait for cloud-init to complete:"
echo "     ssh root@${VM_IP} 'cloud-init status --wait'"
echo ""
echo "  2. Deploy the Lab by Kraliki stack:"
echo "     scp deploy-stack.sh root@${VM_IP}:/opt/magic-box/"
echo "     ssh root@${VM_IP} '/opt/magic-box/deploy-stack.sh --admin-user magicbox'"
echo ""
echo "  3. Or use the combined installer:"
echo "     ssh root@${VM_IP} 'curl -fsSL https://raw.githubusercontent.com/verduona/magic-box/main/scripts/install.sh | bash'"
echo ""
echo "SSH command:"
echo "  ssh root@${VM_IP}"
echo ""
