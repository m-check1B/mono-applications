# Lab by Kraliki One-Click Setup Guide

Complete automated setup for Lab by Kraliki multi-AI orchestration platform.

## Overview

The `setup-complete.sh` script automates the entire Lab by Kraliki installation process:

1. ✅ Docker & Docker Compose installation
2. ✅ Traefik reverse proxy setup
3. ✅ CLI tools installation (Claude Code, Gemini CLI, OpenAI CLI)
4. ✅ mgrep semantic search service (backend + wrapper)
5. ✅ All services configured to start on boot
6. ✅ Full verification of all components

## Prerequisites

- **OS**: Ubuntu 22.04 (recommended) or compatible Linux distribution
- **Memory**: Minimum 4GB (8GB recommended for multiple users)
- **Disk**: Minimum 10GB free (for models and data)
- **Network**: Internet access for downloading images and packages
- **Privileges**: Root access (for installation)

## Installation Methods

### Method 1: Interactive Installation

```bash
# Download and run (will prompt for SSH key and API keys)
curl -fsSL https://raw.githubusercontent.com/verduona/magic-box/main/scripts/setup-complete.sh | sudo bash
```

You'll be prompted for:
- SSH public key (for admin user)
- Optionally: API keys file path

### Method 2: Non-Interactive with Options

```bash
curl -fsSL https://raw.githubusercontent.com/verduona/magic-box/main/scripts/setup-complete.sh | sudo bash -s -- \
  --admin-user myuser \
  --ssh-key "ssh-ed25519 AAAA..."
```

### Method 3: With API Keys File

Create a file `keys.txt`:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-openai-xxx
GOOGLE_API_KEY=AIzaSy-xxx
```

Then run:
```bash
curl -fsSL ... | sudo bash -s -- \
  --admin-user magicbox \
  --api-keys-file /path/to/keys.txt
```

## Options

| Option | Description | Default |
|---------|-------------|----------|
| `--admin-user USER` | Admin username to create | `magicbox` |
| `--ssh-key KEY` | SSH public key string | Prompted |
| `--ssh-key-file PATH` | Read SSH key from file | - |
| `--api-keys-file PATH` | File with API keys | Prompted |
| `--skip-user` | Skip user creation (already exists) | - |
| `-h, --help` | Show help text | - |

## What Gets Installed

### System Packages

- Docker & Docker Compose
- Node.js & npm
- Python 3 & pip
- Security tools (ufw, fail2ban)

### Docker Services

| Service | Purpose | Port |
|---------|---------|-------|
| Infinity | Embeddings & reranking | 7997 |
| Qdrant | Vector database | 6333 |
| mgrep-backend | Semantic search API | 8001 |
| Traefik | Reverse proxy | 8080/8081 |

All services bind to `127.0.0.1` only (localhost) for security.

### CLI Tools

| Tool | Purpose | Command |
|-------|---------|----------|
| Claude Code | Anthropic AI CLI | `claude` |
| Gemini CLI | Google AI CLI | `gemini` |
| OpenAI CLI | OpenAI AI CLI | `openai` |
| mgrep | Semantic search wrapper | `mgrep` |

### Management CLI

The `magic-box` command provides easy management:

```bash
magic-box status    # Show status of all services
magic-box start     # Start all services
magic-box stop      # Stop all services
magic-box restart   # Restart all services
magic-box logs     # View logs
magic-box config    # Edit API keys
magic-box test      # Test API connections
magic-box verify    # Verify all components
magic-box update    # Pull latest images
```

## Post-Installation

### 1. Verify Installation

```bash
magic-box verify
```

Expected output:
```
Checking services...
  infinity: running
  qdrant: running
  mgrep-backend: running
  traefik: running

Checking CLI tools...
  Claude Code: installed
  Gemini CLI: installed
  OpenAI CLI: installed
  mgrep: installed

All verifications passed! ✓
```

### 2. Check Status

```bash
magic-box status
```

### 3. Configure API Keys (if not set during install)

```bash
magic-box config
```

Edit the `.env` file to add your API keys:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-openai-xxx
GOOGLE_API_KEY=AIzaSy-xxx
```

### 4. Test API Connections

```bash
magic-box test
```

## Integration with Auto-Provisioning

The `auto-provision.sh` script has been updated to use the complete setup:

```bash
# Auto-provision creates VM and runs complete setup
export HCLOUD_TOKEN="your-hetzner-token"

./auto-provision.sh --customer acme --ssh-key admin-key
```

This will:
1. Create Hetzner VM
2. Wait for VM to be ready
3. Upload and execute `setup-complete.sh`
4. Return connection credentials

## Directory Structure

After installation, the Lab by Kraliki workspace is at `/opt/magic-box/`:

```
/opt/magic-box/
├── docker-compose.yml      # Service definitions
├── config/
│   ├── .env               # API keys (create from template)
│   └── .env.template     # Template with placeholders
├── data/
│   ├── qdrant-storage/     # Vector database data
│   ├── infinity-cache/     # Model cache (~4GB)
│   └── mgrep-data/        # mgrep data
├── logs/                  # Service logs
├── prompts/               # Prompt templates
├── patterns/              # Workflow patterns
└── scripts/
    ├── magic-box          # Management CLI
    └── setup-complete.sh  # Setup script
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
magic-box status

# View logs
magic-box logs infinity
magic-box logs qdrant
magic-box logs mgrep-backend

# Restart
magic-box restart
```

### CLI Tools Not Working

```bash
# Verify installation
which claude
which gemini
which openai
which mgrep

# Reinstall if needed
sudo npm install -g @anthropic-ai/claude-code
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker images
docker system prune -a

# Remove Infinity cache (will re-download)
rm -rf /opt/magic-box/data/infinity-cache/*
```

### Models Not Loading

```bash
# Check Infinity logs
docker logs magic-box-infinity -f

# Wait for models to download (first run takes 5-10 minutes)
# Look for "model warmed up" message
```

## Security Features

- ✅ All services bind to `127.0.0.1` (localhost only)
- ✅ SSH hardened (key-only authentication)
- ✅ UFW firewall enabled (SSH only by default)
- ✅ Fail2ban for brute-force protection
- ✅ No exposed ports to the internet
- ✅ API keys stored in `.env` (not in scripts)

## Verification Checklist

Before using Lab by Kraliki in production, verify:

- [ ] All services running (`magic-box status`)
- [ ] All health checks passing
- [ ] All CLI tools installed
- [ ] API keys configured (`magic-box config`)
- [ ] API connections working (`magic-box test`)
- [ ] Full verification passing (`magic-box verify`)

## Support

For issues or questions:
- Check logs: `magic-box logs`
- Run diagnostics: `magic-box verify`
- Documentation: `/opt/magic-box/CLAUDE.md`
- Help: `magic-box help`

## Next Steps

After installation:

1. **Add your API keys** to enable AI functionality
2. **Explore the workspace** at `/opt/magic-box/`
3. **Install prompt library** from `/opt/magic-box/prompts/`
4. **Start using CLI tools**: `claude`, `gemini`, `openai`
5. **Set up mgrep indexing** for your codebase

See `/opt/magic-box/CLAUDE.md` for detailed usage instructions.
