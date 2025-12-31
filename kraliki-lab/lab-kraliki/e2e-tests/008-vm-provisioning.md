# E2E Test: 008 - VM Provisioning Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 30 minutes |
| Prerequisites | Hetzner account, API access, provisioning scripts |
| Location | Admin/provisioning environment |

## Objective

Verify that the Lab by Kraliki VM provisioning process works end-to-end, from VM creation to a fully functional Lab by Kraliki environment.

## Pre-conditions

1. Hetzner Cloud API token available
2. Provisioning scripts accessible
3. Base image prepared (if applicable)
4. Network connectivity

## Reference Files

- Create VM script: `/scripts/create-vm.sh`
- Deploy stack script: `/scripts/deploy-stack.sh`
- Install script: `/scripts/install.sh`
- Provision script: `/scripts/provision.sh`
- Auto-provision: `/scripts/auto-provision.sh`

## Test Steps

### Step 1: API Credential Verification

| Action | Verify Hetzner API access |
|--------|---------------------------|
| Command | `hcloud server list` (or API call) |
| Expected | API responds with server list |
| Verification | No authentication errors |

### Step 2: VM Creation

| Action | Create new Lab by Kraliki VM |
|--------|------------------------|
| Command | `./scripts/create-vm.sh [parameters]` |
| Expected | - VM created on Hetzner |
| | - IP address assigned |
| | - SSH access enabled |
| Verification | VM appears in Hetzner console |

### Step 3: SSH Access Verification

| Action | SSH into new VM |
|--------|-----------------|
| Command | `ssh root@[NEW_VM_IP]` |
| Expected | SSH connection successful |
| Verification | Shell prompt appears |

### Step 4: Deploy Stack

| Action | Deploy Lab by Kraliki stack to VM |
|--------|------------------------------|
| Command | `./scripts/deploy-stack.sh [VM_IP]` |
| Expected | - Docker installed |
| | - Compose files deployed |
| | - Services configured |
| Verification | Script completes without error |

### Step 5: Install Lab by Kraliki Components

| Action | Run installation script |
|--------|------------------------|
| Command | On VM: `./scripts/install.sh` |
| Expected | - CLIProxyAPI installed |
| | - Claude CLI installed |
| | - Gemini CLI installed |
| | - Codex CLI installed |
| | - mgrep installed |
| Verification | Each component confirms installation |

### Step 6: API Key Configuration

| Action | Configure customer API keys |
|--------|----------------------------|
| Command | `magic-box config` or edit `.env` |
| Expected | - Anthropic key set |
| | - OpenAI key set (optional) |
| | - Google key set (optional) |
| Verification | Keys saved securely |

### Step 7: Service Startup

| Action | Start all Lab by Kraliki services |
|--------|------------------------------|
| Command | `docker compose up -d` or `magic-box start` |
| Expected | All services start |
| Verification | `docker ps` shows running containers |

### Step 8: Health Check

| Action | Run system health check |
|--------|------------------------|
| Command | `magic-box status` |
| Expected | All components green: |
| | - CLIProxyAPI: OK |
| | - Claude CLI: OK |
| | - Gemini CLI: OK |
| | - Codex CLI: OK |
| | - mgrep: OK |
| Verification | Health check passes |

### Step 9: Claude CLI Test

| Action | Test Claude CLI response |
|--------|-------------------------|
| Command | `claude "Hello, confirm you're working"` |
| Expected | Claude responds |
| Verification | Response received |

### Step 10: mgrep Test

| Action | Test semantic search |
|--------|---------------------|
| Command | `mgrep "test query"` or API call |
| Expected | mgrep responds (may be empty) |
| Verification | No errors |

### Step 11: End-to-End Workflow Test

| Action | Run simple workflow |
|--------|---------------------|
| Command | Quick audit demo pattern |
| Expected | Workflow completes |
| Verification | Output produced |

### Step 12: Network Security Check

| Action | Verify services are not publicly exposed |
|--------|----------------------------------------|
| Command | From external: `nmap [VM_IP]` |
| Expected | Only SSH (22) and necessary ports open |
| | Services bound to 127.0.0.1 |
| Verification | Port scan results |

### Step 13: Cleanup (if test VM)

| Action | Destroy test VM |
|--------|-----------------|
| Command | `hcloud server delete [VM_NAME]` |
| Expected | VM removed |
| Verification | VM no longer in list |

## Pass Criteria

- VM creation succeeds
- All components install correctly
- Health check passes
- Claude CLI responds
- mgrep operational
- Network security verified
- End-to-end workflow completes

## VM Specifications

| Spec | Requirement |
|------|-------------|
| Type | CPX31 or higher |
| vCPUs | 4+ |
| RAM | 8 GB+ |
| Storage | 160 GB+ NVMe |
| OS | Ubuntu 22.04 or similar |

## Common Issues

| Issue | Resolution |
|-------|------------|
| SSH timeout | Check firewall, SSH key |
| Docker install fails | Check OS compatibility |
| API key invalid | Verify key format |
| Port conflicts | Check existing services |
| Disk space | Use larger VM size |

## Automation Readiness

For production, verify:
- [ ] Scripts are idempotent
- [ ] Error handling present
- [ ] Rollback procedures exist
- [ ] Logging enabled
- [ ] Metrics collected

## Related Tests

- 009-cli-setup.md
- 010-onboarding-flow.md
