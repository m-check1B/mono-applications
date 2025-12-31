# SSH Cooperation Cookbook

**Purpose:** Enable Claude Desktop on Mac to directly access the Linux dev server, sharing context and continuing work seamlessly.

## Quick Start

### 1. SSH Connection

```bash
# From Mac terminal
ssh adminmatej@5.9.38.218

# Or with specific key
ssh -i ~/.ssh/id_ed25519 adminmatej@5.9.38.218
```

### 2. Start Claude Code on Dev Server

```bash
# Navigate to workspace
cd /home/adminmatej/github

# Start Claude Code
claude

# Or with specific project
cd /home/adminmatej/github/ai-automation/gin
claude
```

## Key Locations

| What | Path |
|------|------|
| Main workspace | `/home/adminmatej/github/` |
| Features to complete | `/github/ai-automation/software-dev/planning/features.json` |
| GIN automation | `/github/ai-automation/gin/` |
| Human work queue | `/github/ai-automation/humans-work-needed/` |
| Applications | `/github/applications/` |
| Logs | `/github/logs/` |

## Context Sync Commands

### Check Current State

```bash
# See what's in progress
cat /home/adminmatej/github/ai-automation/software-dev/planning/features.json | jq '.features[] | select(.passes != true) | {id, title, priority}'

# Check PM2 processes
pm2 status

# Check GIN health
curl -s http://127.0.0.1:8099/health | jq '.processes'

# Recent CEO notes
cat /home/adminmatej/github/ai-automation/gin/CEO-NOTES.md | tail -50
```

### Continue Previous Work

```bash
# Read session notes
cat /home/adminmatej/github/ai-automation/gin/CEO-NOTES.md

# Check what was last completed
grep "completed_at" /home/adminmatej/github/ai-automation/software-dev/planning/features.json | tail -5

# See error log
cat /home/adminmatej/github/logs/health-alerts.json | jq '.[-5:]'
```

## Cooperation Patterns

### Pattern 1: Mac Does Browser, Linux Does Code

**Mac Claude Desktop:**
- Computer Use for browser testing
- OAuth/payment setup (requires GUI)
- Visual verification

**Linux Claude Code:**
- Code changes
- API testing
- Deployment commands
- Log analysis

### Pattern 2: Async Handoff

1. Mac creates issue in `humans-work-needed/`
2. Linux picks up and implements
3. Mac verifies via browser

```bash
# Linux: Check for new human work
ls -lt /home/adminmatej/github/ai-automation/humans-work-needed/*.md | head -5

# Linux: Mark as done
# Edit the HW-XXX file, update Status: Done
```

### Pattern 3: Real-time Sync via Git

```bash
# Linux: Push changes
cd /home/adminmatej/github/ai-automation
git add -A && git commit -m "Session update" && git push

# Mac: Pull changes
git pull

# Continue work on Mac...
```

## Useful Aliases

Add to `~/.bashrc` on dev server:

```bash
alias cdg='cd /home/adminmatej/github'
alias features='cat /home/adminmatej/github/ai-automation/software-dev/planning/features.json | jq ".features[] | select(.passes != true)"'
alias ginhealth='curl -s http://127.0.0.1:8099/health | jq'
alias ceonotes='cat /home/adminmatej/github/ai-automation/gin/CEO-NOTES.md'
alias hwqueue='ls -la /home/adminmatej/github/ai-automation/humans-work-needed/HW-*.md'
```

## Port Forwarding (Optional)

Access dev server services from Mac:

```bash
# Forward GIN dashboard to Mac
ssh -L 8099:127.0.0.1:8099 adminmatej@5.9.38.218

# Then on Mac, open http://localhost:8099

# Forward multiple ports
ssh -L 8099:127.0.0.1:8099 -L 8040:127.0.0.1:8040 adminmatej@5.9.38.218
```

## Security Reminders

- Never expose ports to 0.0.0.0 (see `/github/CLAUDE.md`)
- All services bind to 127.0.0.1 only
- Access via SSH tunnel or Traefik proxy
- Credentials in `/github/secrets/` (gitignored)

## Troubleshooting

### SSH Connection Refused
```bash
# Check if SSH is running on server
# (run from another connection or console)
systemctl status ssh
```

### Claude Code Not Found
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code
```

### PM2 Issues
```bash
# Restart all processes
pm2 restart all

# Check logs
pm2 logs --lines 50
```

---

*Dev Server IP: 5.9.38.218*
*User: adminmatej*
*Created: 2025-12-21*
