# Kraliki Swarm CLI - Security Architecture

## Problem

Current swarm CLI runs directly on host with full access to:
- SSH keys (can SSH to production)
- Docker socket (can spawn containers, access other services)
- Production certificates (via /etc/ssl)
- Host filesystem (/home, /etc, /var)
- All secrets in /home/adminmatej/github/secrets

**RISK**: Agents could accidentally access production, modify host system, or leak secrets.

## Solution: Containerized Swarm CLI

### Security Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST SYSTEM                          │
│  /home/adminmatej (no access to container)             │
│  /home/adminmatej/.ssh (NOT mounted)                  │
│  /var/run/docker.sock (NOT mounted)                    │
│                                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │      SWARM CLI CONTAINER (Isolated)                │ │
│  │  - Non-root user (UID 1000)                      │ │
│  │  - No Docker socket                               │ │
│  │  - No SSH keys                                   │ │
│  │  - Read-only root filesystem                       │ │
│  │  - Dropped capabilities                           │ │
│  │  - seccomp profile                               │ │
│  │                                                      │
│  │  /workspace (read-only code)                      │ │
│  │  /workspace/data (read-write, isolated)            │ │
│  │  /workspace/arena (read-write, isolated)          │ │
│  │  /workspace/ai-automation (read-write, isolated)    │ │
│  │  /workspace/brain-2026 (read-write, isolated)      │ │
│  │                                                      │
│  │  Environment Variables:                             │ │
│  │  - LINEAR_API_KEY (from host env)                 │ │
│  │  - ANTHROPIC_API_KEY (from host env)              │ │
│  │  - OPENAI_API_KEY (from host env)                 │ │
│  │  - BLOCKED_HOSTS=production.kraliki.com           │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │      SWARM DASHBOARD (Separate container)          │ │
│  │  - SvelteKit frontend                              │ │
│  │  - WebSocket for real-time updates                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Files

### 1. `Dockerfile.swarm`
Minimal Python image with:
- Non-root user (kraliki, UID 1000)
- Only essential dependencies
- Removed git, curl, gnupg after build
- Health check

### 2. `docker-compose.swarm.yml`
Secure configuration:
- `read_only: true` - Read-only root filesystem
- `cap_drop: [ALL]` - All capabilities dropped
- `no-new-privileges:true` - Cannot gain privileges
- `seccomp:seccomp-profile.json` - Syscall filtering
- No `/var/run/docker.sock` mount
- No `/home/adminmatej/.ssh` mount
- No system directory mounts
- Resource limits (4 CPU, 4GB RAM)

### 3. `.env.swarm.template`
Environment variables (no file secrets):
- `LINEAR_API_KEY` - Not file-mounted
- `ANTHROPIC_API_KEY` - Not file-mounted
- `OPENAI_API_KEY` - Not file-mounted
- `BLOCKED_HOSTS` - Production URLs blocked
- `ALLOWED_DIRECTORIES` - Restricted filesystem access

### 4. `seccomp-profile.json`
Syscall whitelist:
- Only allows necessary syscalls
- Blocks dangerous syscalls (mount, reboot, etc.)
- Reduces attack surface

### 5. `scripts/security-validate.sh`
Pre-flight security check:
- Validates no SSH keys mounted
- Validates no Docker socket mounted
- Validates running as non-root
- Validates no privileged mode
- Validates read-only filesystem
- Validates no system directories mounted
- Validates secrets as env vars only

## Security Checklist

### ✅ What IS Secure

- [x] **Non-root user**: Container runs as UID 1000
- [x] **No Docker socket**: Cannot control Docker daemon
- [x] **No SSH keys**: Cannot SSH to other servers
- [x] **No privileged mode**: Cannot escape container
- [x] **Read-only filesystem**: Cannot modify system files
- [x] **Dropped capabilities**: No extra permissions
- [x] **seccomp profile**: Syscall filtering
- [x] **Network isolation**: Bridge network (not host)
- [x] **Resource limits**: CPU/memory capped
- [x] **No system mounts**: Cannot access /etc, /var, /home
- [x] **Secrets as env vars**: No file mounts
- [x] **Blocked production hosts**: Cannot reach production URLs
- [x] **Health check**: Container monitoring
- [x] **Log rotation**: Prevent disk exhaustion

### ❌ What Agents CANNOT Do

- SSH to production (no SSH keys)
- SSH to any server (no SSH keys)
- Spawn containers (no Docker socket)
- Access host filesystem (no mounts)
- Read production certificates (no /etc/ssl mount)
- Modify system files (read-only root)
- Gain root privileges (capabilities dropped)
- Execute dangerous syscalls (seccomp filtering)
- Access production servers (BLOCKED_HOSTS)
- Escape container (no-new-privileges)

### ✅ What Agents CAN Do

- Read/write to /workspace/data
- Read/write to /workspace/arena
- Read/write to /workspace/ai-automation
- Read/write to /workspace/brain-2026
- Read/write to /workspace/marketing-2026
- Make HTTP requests (internet access)
- Query Linear API
- Query Anthropic/OpenAI APIs
- Execute Python code within container
- Read git history (workspace is read-only mount)
- Write files to allowed directories

## Usage

### Setup

```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm

# Copy environment template
cp .env.swarm.template .env.swarm

# Edit with actual API keys
nano .env.swarm
```

### Build and Run

```bash
# Build image
docker compose -f docker-compose.swarm.yml build

# Run security validation first
bash scripts/security-validate.sh

# Start container
docker compose -f docker-compose.swarm.yml up -d

# View logs
docker compose -f docker-compose.swarm.yml logs -f

# Stop container
docker compose -f docker-compose.swarm.yml down
```

### Production Deployment

For production, add:

```yaml
# In docker-compose.swarm.yml
env_file:
  - /home/adminmatej/.secrets/kraliki-swarm-prod.env
```

Never commit `.env.swarm` to git.

## Network Security

### Production Access Blocking

The container should block access to production hosts:

```python
# In swarm code
import os
import requests

BLOCKED_HOSTS = os.getenv('BLOCKED_HOSTS', '').split(',')

def make_request(url):
    host = url.split('/')[2]
    
    if any(blocked in host for blocked in BLOCKED_HOSTS):
        raise SecurityError(f"Access to {host} is blocked")
    
    return requests.get(url)
```

### Firewall Rules (Host-level)

```bash
# Prevent container from reaching production IPs
iptables -I DOCKER-USER -s 172.28.0.0/16 -d <production-ip> -j DROP

# Allow only specific external APIs
iptables -I DOCKER-USER -s 172.28.0.0/16 -d api.anthropic.com -j ACCEPT
iptables -I DOCKER-USER -s 172.28.0.0/16 -d api.openai.com -j ACCEPT
```

## Monitoring

### Container Logs

```bash
# View real-time logs
docker logs -f kraliki-swarm-cli

# Check for security violations
docker logs kraliki-swarm-cli 2>&1 | grep -i "security\|error\|permission denied"
```

### Resource Usage

```bash
# Monitor CPU/memory
docker stats kraliki-swarm-cli

# Check for suspicious activity
docker top kraliki-swarm-cli
```

### File Changes

```bash
# Monitor writes to workspace
inotifywait -m -r /workspace/data -e create,write,delete
```

## Emergency Procedures

### Container Compromise

If you suspect compromise:

```bash
# 1. Stop container immediately
docker compose -f docker-compose.swarm.yml stop

# 2. Inspect changes
docker diff kraliki-swarm-cli

# 3. Save logs
docker logs kraliki-swarm-cli > /tmp/swarm-compromise.log

# 4. Rotate API keys (in production)
# Generate new keys, update .env.swarm

# 5. Investigate
less /tmp/swarm-compromise.log
```

### Resource Exhaustion

If container consumes too many resources:

```bash
# Resource limits will automatically kill processes
# Check why
docker stats kraliki-swarm-cli

# If needed, reduce limits in docker-compose.swarm.yml
deploy.resources.limits.cpus: '2'  # Reduce from 4
deploy.resources.limits.memory: 2G  # Reduce from 4G
```

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [seccomp Profiles](https://docs.docker.com/engine/security/seccomp/)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Container Security Checklist](https://snyk.io/blog/10-docker-image-security-best-practices/)

## Summary

This architecture provides:

✅ **Strong isolation** from host system
✅ **No SSH access** to any server
✅ **No Docker control** from container
✅ **No production access** from dev
✅ **Minimal attack surface** (seccomp, capabilities)
✅ **Filesystem restriction** (read-only, specific mounts)
✅ **Secrets protection** (env vars only)
✅ **Resource limits** (CPU, memory)
✅ **Monitoring and validation**

**Risk Level**: LOW
**Recommended**: YES - Use this for all swarm deployments
