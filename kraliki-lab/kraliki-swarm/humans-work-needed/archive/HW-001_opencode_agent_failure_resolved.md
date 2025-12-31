# HW-001: OpenCode Agent Spawning Failure - RESOLVED

## Issue
All OpenCode agents fail to spawn and execute work.

## Status
**RESOLVED** - 2025-12-24T19:38:00Z

## Root Cause
1. **Linear MCP was disabled** - OpenCode config had `"enabled": false` for Linear MCP
2. **Missing LINEAR_API_KEY environment variable** - Required for Linear MCP to function

## Resolution Applied

### 1. Enabled Linear MCP
Updated `~/.config/opencode/opencode.json`:
- Set `"enabled": true` for Linear MCP
- Confirmed URL: `https://mcp.linear.app/mcp`

### 2. Saved Linear API Key
- Created `/home/adminmatej/secrets/linear_api_key.txt`
- Stored API key: `lin_api_0Y9TbdY5qeVuuyQrZCNRY1Ka4tMLoPE1MZMwMVhF`
- Verified API connection with test query

### 3. Persisted Environment Variable
Added to `~/.bashrc`:
```bash
export LINEAR_API_KEY="$(cat /home/adminmatej/secrets/linear_api_key.txt)"
```

### 4. Verified Resolution
```bash
# Test spawn successful
python3 agents/spawn.py opencode_explorer --dry-run
# Result: {"success": true, "agent_id": "OC-explorer-19:36.24.12.AA", ...}

# Actual spawn successful
python3 agents/spawn.py opencode_explorer
# Result: Agent spawned, ran exploration, completed successfully

# Linear MCP found in logs
# INFO service=mcp key=linear type=remote found
```

## Remaining Notes

### ACP Command Errors
Agents still show `ERROR service=acp-command promise={} reason=NotFoundError`
- This is expected behavior when `opencode acp` server is not running
- Not a blocker - agents spawn and execute successfully
- The ACP (Agent Client Protocol) server is optional for single-agent operation

### Available OpenCode Genomes
All 14 OpenCode genomes are now available:
- opencode_dev_discovery
- opencode_biz_discovery
- opencode_marketer
- opencode_explorer
- opencode_orchestrator
- opencode_rnd
- opencode_caretaker
- opencode_builder
- opencode_integrator
- opencode_patcher
- opencode_reviewer
- opencode_tester
- opencode_business

## Impact
OpenCode agents are now unblocked and can:
- Spawn successfully
- Access Linear MCP for task management
- Execute genomes without NotFoundError crashes
- Participate in Kraliki swarm operations

## Verification Commands
```bash
# Check policy
python3 /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/agents/spawn.py --policy

# Test spawn
python3 /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/agents/spawn.py opencode_explorer --dry-run

# Verify Linear MCP
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $(cat /home/adminmatej/secrets/linear_api_key.txt)" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { viewer { id name } }"}'
```
