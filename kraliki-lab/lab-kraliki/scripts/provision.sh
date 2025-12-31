#!/usr/bin/env bash
set -euo pipefail

ADMIN_USER=""
SSH_PUB_KEY=""
SSH_PUB_KEY_FILE=""
ALLOW_HTTP=0
ALLOW_HTTPS=0
MAGIC_BOX_REPO=""
FORCE_OS=0

usage() {
  cat <<'USAGE'
Lab by Kraliki VM provisioning script (Ubuntu 22.04)

Usage:
  sudo ./provision.sh --admin-user magicbox --ssh-key "ssh-ed25519 AAAA..."

Options:
  --admin-user USER        Admin username to create
  --ssh-key KEY            SSH public key string for the admin user
  --ssh-key-file PATH      Read SSH public key from file
  --allow-http             Open port 80 in UFW
  --allow-https            Open port 443 in UFW
  --repo URL               Optional git repo to clone into /opt/magic-box
  --force-os               Skip OS version check
  -h, --help               Show this help text
USAGE
}

log() {
  printf "\n==> %s\n" "$1"
}

fail() {
  printf "\nERROR: %s\n" "$1" >&2
  exit 1
}

if [[ "${EUID}" -ne 0 ]]; then
  fail "Run this script as root (use sudo)."
fi

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
    --allow-http)
      ALLOW_HTTP=1
      shift
      ;;
    --allow-https)
      ALLOW_HTTPS=1
      shift
      ;;
    --repo)
      MAGIC_BOX_REPO="${2:-}"
      shift 2
      ;;
    --force-os)
      FORCE_OS=1
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

# Check OS (Ubuntu 22.04 recommended)
if [[ "${FORCE_OS}" -eq 0 ]]; then
  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "${ID}" != "ubuntu" ]] || [[ "${VERSION_ID}" != "22.04" ]]; then
      fail "This script is optimized for Ubuntu 22.04. Detected: ${ID} ${VERSION_ID}. Use --force-os to override."
    fi
  else
    fail "Could not detect OS version. /etc/os-release missing. Use --force-os to override."
  fi
fi

if [[ -z "${ADMIN_USER}" ]]; then
  fail "--admin-user is required."
fi

if [[ -n "${SSH_PUB_KEY_FILE}" ]]; then
  if [[ ! -f "${SSH_PUB_KEY_FILE}" ]]; then
    fail "SSH key file not found: ${SSH_PUB_KEY_FILE}"
  fi
  SSH_PUB_KEY="$(cat "${SSH_PUB_KEY_FILE}")"
fi

if [[ -z "${SSH_PUB_KEY}" ]]; then
  fail "Provide an SSH public key via --ssh-key or --ssh-key-file."
fi

log "Updating apt and installing base packages"
apt-get update -y
apt-get install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  lsb-release \
  ufw \
  fail2ban

log "Creating admin user: ${ADMIN_USER}"
if id -u "${ADMIN_USER}" >/dev/null 2>&1; then
  log "User ${ADMIN_USER} already exists, skipping creation"
else
  useradd -m -s /bin/bash "${ADMIN_USER}"
fi
usermod -aG sudo "${ADMIN_USER}"

log "Configuring passwordless sudo for ${ADMIN_USER}"
echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${ADMIN_USER}"
chmod 440 "/etc/sudoers.d/${ADMIN_USER}"

log "Configuring SSH access for ${ADMIN_USER}"
install -d -m 700 "/home/${ADMIN_USER}/.ssh"
# Append key if not already present
if ! grep -qF "${SSH_PUB_KEY}" "/home/${ADMIN_USER}/.ssh/authorized_keys" 2>/dev/null; then
  printf "%s\n" "${SSH_PUB_KEY}" >> "/home/${ADMIN_USER}/.ssh/authorized_keys"
fi
chown -R "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"

log "Hardening SSH configuration"
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl reload ssh

log "Installing Docker Engine and Compose plugin"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

UBUNTU_CODENAME="$(. /etc/os-release && echo "${VERSION_CODENAME}")"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin unattended-upgrades
systemctl enable --now docker
usermod -aG docker "${ADMIN_USER}"

log "Configuring unattended-upgrades"
echo 'Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::Package-Blacklist {
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::InstallOnShutdown "false";
Unattended-Upgrade::Mail "root";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
' > /etc/apt/apt.conf.d/50unattended-upgrades
echo 'APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
' > /etc/apt/apt.conf.d/20auto-upgrades


log "Setting up UFW firewall"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
if [[ "${ALLOW_HTTP}" -eq 1 ]]; then
  ufw allow 80/tcp
fi
if [[ "${ALLOW_HTTPS}" -eq 1 ]]; then
  ufw allow 443/tcp
fi
ufw --force enable

log "Enabling fail2ban"
systemctl enable --now fail2ban

log "Preparing /opt/magic-box workspace"
install -d -m 755 /opt/magic-box
chown "${ADMIN_USER}:${ADMIN_USER}" /opt/magic-box

if [[ -n "${MAGIC_BOX_REPO}" ]]; then
  log "Cloning Lab by Kraliki repo"
  sudo -u "${ADMIN_USER}" git clone "${MAGIC_BOX_REPO}" /opt/magic-box/repo
fi

log "Provisioning complete"
cat <<EOF

Next steps:
- SSH as ${ADMIN_USER} and deploy the Lab by Kraliki stack into /opt/magic-box
- Add Traefik + app compose configs as needed
- Run: docker info && docker compose version
EOF
