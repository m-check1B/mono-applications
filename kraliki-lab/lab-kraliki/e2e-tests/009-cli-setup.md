# E2E Test: 009 - CLI Setup Scripts

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 20 minutes |
| Prerequisites | Fresh VM or environment, script access |
| Location | Customer VM or test environment |

## Objective

Verify that the Lab by Kraliki CLI setup scripts work correctly and configure all necessary tools for customer use.

## Pre-conditions

1. Fresh Ubuntu 22.04+ environment
2. SSH access
3. Internet connectivity
4. Sudo/root privileges

## Reference Files

- Main install: `/scripts/install.sh`
- Auto-provision: `/scripts/auto-provision.sh`
- Provisioning API: `/scripts/provision_api.py`

## Test Steps

### Step 1: Script Availability

| Action | Verify scripts are accessible |
|--------|------------------------------|
| Command | `ls -la scripts/` |
| Expected | All required scripts present |
| | - install.sh |
| | - deploy-stack.sh |
| | - create-vm.sh |
| | - provision.sh |
| Verification | Files exist and are executable |

### Step 2: Script Permissions

| Action | Check execute permissions |
|--------|--------------------------|
| Command | `stat scripts/*.sh` |
| Expected | Execute permission set (755 or 700) |
| Verification | Permission bits correct |

### Step 3: Install Script Dry Run

| Action | Check install script syntax |
|--------|----------------------------|
| Command | `bash -n scripts/install.sh` |
| Expected | No syntax errors |
| Verification | Command returns 0 |

### Step 4: Dependency Check

| Action | Run install with dependency check |
|--------|----------------------------------|
| Command | `./scripts/install.sh --check` (if supported) |
| Expected | Lists missing dependencies |
| Verification | Output shows what will be installed |

### Step 5: Docker Installation

| Action | Verify Docker gets installed |
|--------|------------------------------|
| Command | Run install or check Docker |
| Expected | Docker installed and running |
| Verification | `docker --version` works |

### Step 6: Docker Compose Installation

| Action | Verify Docker Compose |
|--------|----------------------|
| Command | `docker compose version` |
| Expected | Compose v2 installed |
| Verification | Version output shown |

### Step 7: Claude CLI Installation

| Action | Verify Claude Code CLI |
|--------|------------------------|
| Command | After install: `claude --version` or `which claude` |
| Expected | Claude CLI accessible |
| Verification | Command found |

### Step 8: Gemini CLI Check

| Action | Verify Gemini CLI (if bundled) |
|--------|-------------------------------|
| Command | `gemini --version` or equivalent |
| Expected | Gemini CLI accessible |
| Verification | Command found or noted as optional |

### Step 9: Codex CLI Check

| Action | Verify Codex CLI (if bundled) |
|--------|------------------------------|
| Command | `codex --version` or equivalent |
| Expected | Codex CLI accessible |
| Verification | Command found or noted as optional |

### Step 10: mgrep Installation

| Action | Verify mgrep service |
|--------|---------------------|
| Command | Check for mgrep container or service |
| Expected | mgrep running or installable |
| Verification | `docker ps` shows mgrep or service exists |

### Step 11: Configuration File Creation

| Action | Check config files created |
|--------|---------------------------|
| Command | `ls -la ~/.magic-box/` or `/opt/magic-box/` |
| Expected | - .env file (or template) |
| | - Config directory |
| | - Prompt library |
| Verification | Files present |

### Step 12: Lab by Kraliki CLI

| Action | Check magic-box command |
|--------|------------------------|
| Command | `magic-box --help` or `magic-box status` |
| Expected | CLI responds with help or status |
| Verification | Output displayed |

### Step 13: API Key Prompting

| Action | Test API key configuration |
|--------|---------------------------|
| Command | `magic-box config` or interactive setup |
| Expected | - Prompts for Anthropic key |
| | - Prompts for OpenAI key |
| | - Prompts for Google key |
| | - Validates format |
| Verification | Configuration flow works |

### Step 14: Service Start

| Action | Start all services |
|--------|-------------------|
| Command | `magic-box start` or `docker compose up -d` |
| Expected | All services start without error |
| Verification | `docker ps` shows healthy containers |

### Step 15: Health Check Script

| Action | Run health verification |
|--------|------------------------|
| Command | `magic-box status` or health endpoint |
| Expected | All green status |
| Verification | No red/failed indicators |

### Step 16: First Run Test

| Action | Execute simple command |
|--------|------------------------|
| Command | `claude "Hello, confirm Lab by Kraliki is working"` |
| Expected | Response received |
| Verification | AI responds appropriately |

## Pass Criteria

- All scripts execute without errors
- Docker and Compose installed
- Claude CLI functional
- Configuration files created
- Services start successfully
- Health check passes
- First command succeeds

## Error Handling Tests

| Scenario | Expected Behavior |
|----------|-------------------|
| Missing API key | Clear error message |
| Invalid API key | Validation error shown |
| Docker not running | Instructions to start Docker |
| Port conflict | Warning with resolution steps |
| Network error | Timeout with retry suggestion |

## Idempotency Test

| Action | Run install script twice |
|--------|--------------------------|
| Expected | Second run completes without breaking first |
| Verification | All services still work after re-run |

## Rollback Test

| Action | Test uninstall or cleanup |
|--------|---------------------------|
| Command | `magic-box uninstall` or cleanup script |
| Expected | Clean removal without leftover files |
| Verification | Services stopped, files removed |

## Common Issues

| Issue | Resolution |
|-------|------------|
| Permission denied | Use sudo or fix ownership |
| curl not found | Install curl first |
| Old Docker version | Update Docker |
| PATH not set | Add to .bashrc/.zshrc |

## Related Tests

- 008-vm-provisioning.md
- 010-onboarding-flow.md
