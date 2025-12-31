# Magic Box VM Setup Guide

One-click provisioning for self-hosted AI orchestration.

## Prerequisites

### VM Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| OS | Ubuntu 22.04+ | Ubuntu 24.04 LTS |
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB SSD | 50+ GB SSD |
| Architecture | x86_64 or arm64 | x86_64 |

### API Keys (At Least One Required)

Before running the setup, obtain API keys for the AI services you want to use:

- **Anthropic (Claude)**: https://console.anthropic.com/
- **OpenAI (GPT/Codex)**: https://platform.openai.com/api-keys
- **Google (Gemini)**: https://aistudio.google.com/app/apikey

## Quick Install (One-Click)

### Option 1: Interactive Setup

SSH into your VM as root and run:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/magic-box/main/scripts/setup-complete.sh | sudo bash
```

The script will:
1. Prompt for your SSH public key (for secure access)
2. Prompt for API keys (optional, can add later)
3. Install all dependencies automatically
4. Start all services
5. Verify the installation

### Option 2: Non-Interactive Setup

Prepare a keys file and run with options:

```bash
# Create API keys file
cat > /tmp/api-keys.txt << 'EOF'
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=AIzaSy-xxxxx
EOF

# Run setup with options
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/magic-box/main/scripts/setup-complete.sh | sudo bash -s -- \
  --admin-user myuser \
  --ssh-key "ssh-ed25519 AAAA... user@host" \
  --api-keys-file /tmp/api-keys.txt
```

### Option 3: Clone and Run

```bash
git clone https://github.com/YOUR_ORG/magic-box.git
cd magic-box
sudo ./scripts/provision.sh
```

## What Gets Installed

### System Packages

- Docker & Docker Compose (container runtime)
- Python 3 with pip (for tooling)
- Node.js & npm (for AI CLI tools)
- git, curl, jq, htop, vim, tmux (utilities)
- ufw, fail2ban (security)

### Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| Infinity | 127.0.0.1:7997 | Embedding & reranking |
| Qdrant | 127.0.0.1:6333 | Vector database |
| mgrep-backend | 127.0.0.1:8001 | Semantic search API |
| Traefik | 127.0.0.1:8080 | Reverse proxy |
| CLIProxyAPI | 127.0.0.1:8888 | Unified AI gateway |

### CLI Tools

- `claude` - Claude Code CLI (Anthropic)
- `gemini` - Gemini CLI (Google)
- `openai` - OpenAI CLI
- `mgrep` - Semantic search wrapper
- `magic-box` - Management CLI

### Directory Structure

```
/opt/magic-box/
|-- docker-compose.yml    # Service definitions
|-- config/
|   |-- .env              # API keys and configuration
|   |-- .env.template     # Configuration template
|-- data/
|   |-- qdrant-storage/   # Vector database storage
|   |-- infinity-cache/   # Embedding model cache
|   |-- mgrep-data/       # Semantic search index
|   |-- cliproxy-logs/    # API usage logs
|-- prompts/              # Prompt templates
|-- patterns/             # Workflow patterns
|-- scripts/              # Management scripts
|-- logs/                 # Application logs
|-- CLAUDE.md             # AI workspace context
```

## Post-Installation

### 1. Verify Installation

```bash
magic-box verify
```

Expected output shows all services running and CLI tools installed.

### 2. Configure API Keys (if not done during setup)

```bash
magic-box config
```

Add your API keys to the `.env` file that opens.

### 3. Check Service Status

```bash
magic-box status
```

### 4. Test API Connections

```bash
magic-box test
```

## Using Magic Box

### Basic Commands

```bash
# Start all services
magic-box start

# Stop all services
magic-box stop

# Restart services
magic-box restart

# View logs
magic-box logs
magic-box logs infinity  # Specific service

# Update container images
magic-box update
```

### Using AI CLI Tools

```bash
# Claude Code
claude "Create a Python script that..."

# With prompt file
claude --prompt "$(cat /opt/magic-box/prompts/orchestrator/task-decomposition.md)" "Build a..."

# Semantic search
mgrep "authentication flow"
```

## Security Notes

All services are bound to `127.0.0.1` (localhost only) by default:

- No services are exposed to the internet
- Access services via SSH tunnel or local terminal
- SSH hardened: key-only authentication
- Fail2ban enabled for brute-force protection
- UFW firewall configured (SSH only)

To access services remotely, use SSH port forwarding:

```bash
# Forward Traefik dashboard
ssh -L 8081:127.0.0.1:8081 user@your-vm-ip

# Then open http://localhost:8081 in your browser
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker status
systemctl status docker

# View container logs
docker compose -f /opt/magic-box/docker-compose.yml logs

# Restart Docker
systemctl restart docker
```

### Permission Issues

```bash
# Ensure user is in docker group
sudo usermod -aG docker $USER

# Re-login or run:
newgrp docker
```

### Health Check Failures

```bash
# Check specific service
docker compose -f /opt/magic-box/docker-compose.yml logs infinity

# Check if port is in use
ss -tlnp | grep 7997
```

### API Key Issues

```bash
# Test API connection
magic-box test

# Edit API keys
magic-box config
```

### Disk Space Issues

```bash
# Check disk space
df -h /opt/magic-box

# Clean up Docker
docker system prune -a
```

## Updating Magic Box

### Update Container Images

```bash
magic-box update
magic-box restart
```

### Update CLI Tools

```bash
npm update -g @anthropic-ai/claude-code openai
```

### Full Reinstall

```bash
# Stop services
magic-box stop

# Re-run setup (preserves data)
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/magic-box/main/scripts/setup-complete.sh | sudo bash -s -- --skip-user
```

## Uninstalling

```bash
# Stop and remove containers
magic-box stop
docker compose -f /opt/magic-box/docker-compose.yml down -v

# Remove installation
sudo rm -rf /opt/magic-box
sudo rm /usr/local/bin/magic-box
sudo rm /usr/local/bin/mgrep

# Remove CLI tools
npm uninstall -g @anthropic-ai/claude-code openai
```

## Support

- Documentation: See `/opt/magic-box/CLAUDE.md` on your VM
- CLI Help: Run `magic-box help`
- Issues: https://github.com/YOUR_ORG/magic-box/issues

---

**Version**: 2.0.0
**Last Updated**: 2025-12-28
