# Secure Kraliki Swarm CLI - Quick Start

## One-Command Setup

```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm
bash scripts/secure-start.sh
```

This will:
1. Create `.env.swarm` from template
2. Prompt you to add API keys
3. Run security validation
4. Build container
5. Start isolated swarm CLI

## What You Need

Before running, you'll need these API keys:

1. **Linear API Key** (required)
   - Get from: https://linear.app/settings/api
   - Add to `LINEAR_API_KEY` in `.env.swarm`

2. **Anthropic API Key** (required for Claude agents)
   - Get from: https://console.anthropic.com/settings/keys
   - Add to `ANTHROPIC_API_KEY` in `.env.swarm`

3. **OpenAI API Key** (required for Codex agents)
   - Get from: https://platform.openai.com/api-keys
   - Add to `OPENAI_API_KEY` in `.env.swarm`

## Security Features (Enabled by Default)

✅ **No SSH access** - SSH keys not mounted
✅ **No Docker control** - Docker socket not mounted
✅ **Non-root user** - Runs as UID 1000
✅ **Read-only filesystem** - Cannot modify system
✅ **Dropped capabilities** - No extra permissions
✅ **Blocked production** - Cannot reach production servers
✅ **Secrets as env vars** - No file mounts
✅ **Resource limits** - Max 4 CPU, 4GB RAM

## What Agents CAN Do

- Read/write to `/workspace/data`
- Read/write to `/workspace/arena`
- Read/write to `/workspace/ai-automation`
- Read/write to `/workspace/brain-2026`
- Read/write to `/workspace/marketing-2026`
- Make HTTP requests (internet access)
- Query Linear API
- Query AI APIs (Anthropic/OpenAI)
- Execute Python code within container

## What Agents CANNOT Do

- SSH to production (no SSH keys)
- SSH to any server (no SSH keys)
- Spawn containers (no Docker socket)
- Access host filesystem (no mounts)
- Read production certificates (no /etc/ssl mount)
- Modify system files (read-only root)
- Gain root privileges (capabilities dropped)
- Access production servers (BLOCKED_HOSTS)

## Common Commands

```bash
# View logs
docker logs -f kraliki-swarm-cli

# Stop container
docker compose -f docker-compose.swarm.yml down

# Restart container
docker restart kraliki-swarm-cli

# Check health
docker inspect kraliki-swarm-cli | grep Status

# Resource usage
docker stats kraliki-swarm-cli

# Security validation
bash scripts/security-validate.sh
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs kraliki-swarm-cli

# Check if API keys are set
cat .env.swarm | grep API_KEY
```

### Security validation fails

```bash
# Run manually
bash scripts/security-validate.sh

# Check container configuration
docker inspect kraliki-swarm-cli
```

### Container uses too much CPU/Memory

Edit `docker-compose.swarm.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Reduce from 4
      memory: 2G     # Reduce from 4G
```

Then restart:

```bash
docker compose -f docker-compose.swarm.yml down
docker compose -f docker-compose.swarm.yml up -d
```

## Production Deployment

For production:

1. **Use production API keys**
   ```bash
   # Create production env file
   cp .env.swarm.template .env.swarm-prod
   # Edit with production keys
   nano .env.swarm-prod
   ```

2. **Update docker-compose.swarm.yml**
   ```yaml
   env_file:
     - .env.swarm-prod  # Use production env file
   ```

3. **Add production host blocking**
   ```bash
   # In .env.swarm-prod
   BLOCKED_HOSTS=staging.kraliki.com,dev.kraliki.com
   ```

4. **Start container**
   ```bash
   docker compose -f docker-compose.swarm.yml up -d
   ```

## File Structure After Setup

```
kraliki-swarm/
├── Dockerfile.swarm              # Container image definition
├── docker-compose.swarm.yml     # Secure container config
├── .env.swarm                  # Your API keys (NOT in git!)
├── .env.swarm.template         # Template for new setups
├── seccomp-profile.json        # Syscall filtering
├── scripts/
│   ├── secure-start.sh         # One-command setup
│   └── security-validate.sh    # Security checks
├── SECURITY.md                # This file
└── data/                     # Persistent swarm data (in container)
    └── ...
```

## Important Notes

⚠️ **Never commit `.env.swarm` to git** - It contains API keys
⚠️ **Never mount `/home/adminmatej/.ssh`** - This gives SSH access
⚠️ **Never mount `/var/run/docker.sock`** - This gives Docker control
⚠️ **Never mount `/etc` or `/var`** - This gives host system access
⚠️ **Always run `security-validate.sh`** before starting swarm

## Getting Help

If you encounter issues:

1. Check logs: `docker logs kraliki-swarm-cli`
2. Run security validation: `bash scripts/security-validate.sh`
3. Check container status: `docker inspect kraliki-swarm-cli`
4. See full security docs: `cat SECURITY.md`

## Next Steps

After setup:

1. Monitor logs: `docker logs -f kraliki-swarm-cli`
2. Check security: `bash scripts/security-validate.sh`
3. Review resource usage: `docker stats kraliki-swarm-cli`

For detailed security architecture, see `SECURITY.md`.
