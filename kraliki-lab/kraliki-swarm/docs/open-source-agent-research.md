# Open Source AI Agent Research for Kraliki

*Research Date: 2025-12-24*

## Executive Summary

Analyzed 4 open source AI agent projects to identify features for Kraliki swarm improvement:

| Project | Stars | Key Insight |
|---------|-------|-------------|
| **OpenCode** | 41.8k | Client/server architecture, SSE for real-time, permission system |
| **Cline** | 56.3k | MCP protocol, structured prompts, YOLO mode, task loop pattern |
| **Roo Code** | 21.4k | Memory Bank, Boomerang Tasks, Mode system, checkpoints |
| **Agent Zero** | 7.4k | Multi-agent coordination, hierarchical memory, tool delegation |

---

## High-Priority Adoptions for Kraliki

### 1. Memory Bank Pattern (from Roo Code)

**Problem:** Current `arena/memory.py` is key-value only. Context lost between sessions.

**Solution:** Structured markdown files per project:
```
/kraliki/memory-bank/
├── activeContext.md    # Current session state
├── progress.md         # Task tracking
├── decisionLog.md      # Why decisions were made
└── systemPatterns.md   # Recurring patterns
```

**Implementation:** Create `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/memory-bank/`

### 2. SSE Endpoint for Real-Time Updates (from OpenCode)

**Problem:** Dashboard polls for status. No real-time agent activity streaming.

**Solution:** Add Server-Sent Events endpoint:
```typescript
// /api/events/+server.ts
export const GET: RequestHandler = async () => {
  const stream = new ReadableStream({
    start(controller) {
      Bus.subscribe('agent:*', (event) => {
        controller.enqueue(`data: ${JSON.stringify(event)}\n\n`);
      });
    }
  });
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' }
  });
};
```

### 3. Boomerang-Style Task Hierarchy (from Roo Code)

**Problem:** Swarm Father spawns agents but no parent-child relationship.

**Solution:** Add hierarchy to task_manager:
```json
{
  "id": "DEV-002",
  "parent_id": "DEV-001",
  "subtask_results": [],
  "status": "delegated"
}
```
- Orchestrator creates subtasks, waits for completion
- Child results bubble up as summaries only
- Context isolation prevents pollution

### 4. Permission System (from OpenCode)

**Problem:** All agents have same permissions regardless of role.

**Solution:** Per-genome permission config:
```json
{
  "permission": {
    "edit": "allow",
    "bash": {
      "git push": "ask",
      "rm -rf": "deny",
      "*": "allow"
    }
  }
}
```
- Three states: `allow`, `ask`, `deny`
- Doom loop prevention (3x identical call detection)
- Per-genome overrides

### 5. Checkpoint/Rollback System (from Roo Code)

**Problem:** No way to undo agent changes if something goes wrong.

**Solution:** Git-based snapshots:
```bash
# Before task starts
git stash push -m "checkpoint-$(date +%s)"

# Or tar-based
tar -czf /tmp/checkpoint-$(date +%Y%m%d-%H%M%S).tar.gz ./
```

---

## Medium-Priority Adoptions

### 6. Structured System Prompts (from Cline)

10-section structure for genomes:
1. Role definition
2. Tool invocation format
3. MCP services list
4. File operation guidance
5. ACT vs PLAN modes
6. Capabilities
7. Rules/constraints
8. System information
9. Objectives
10. Custom guidelines

### 7. Token Tracking & Cost Dashboard (from OpenCode)

```typescript
// Track per-session
const usage = {
  session_id: "...",
  tokens_in: 1500,
  tokens_out: 3200,
  cost_usd: 0.04,
  model: "claude-3-opus"
};
```

### 8. Mode Switching UI (from OpenCode/Roo Code)

- **Plan Mode:** Read-only analysis (explorer, rnd)
- **Build Mode:** Full modification (builder, patcher)
- Visual indicator in dashboard

### 9. Consecutive Mistake Tracking (from Cline)

```python
if consecutive_failures >= MAX_CONSECUTIVE_MISTAKES:
    agent.terminate("Too many consecutive failures")
    blackboard.post(agent_id, "FAILED: Max mistakes reached")
```

### 10. Unified Provider Layer (from Roo Code)

Use LiteLLM pattern for all CLI calls:
- Configure models via YAML
- Cost tracking per model
- Automatic fallback chains
- Replace hard-coded `gemini -y` calls

---

## Architecture Patterns to Adopt

### From OpenCode

```
Client/Server Model:
- HTTP server exposes REST API
- SSE at /sse for real-time updates
- Enables remote control (mobile apps)
- Session management with sharing URLs
```

### From Cline

```
Task Loop Pattern:
async initiateTaskLoop(userContent) {
  while (!this.abort) {
    const didEnd = await this.recursivelyMakeClineRequests();
    if (!toolsUsed) this.consecutiveMistakeCount++;
    if (didEnd) break;
  }
}
```

### From Roo Code

```
Boomerang Tasks:
Orchestrator
├── Analyzes complex task
├── Creates subtasks with new_task tool
├── Delegates to specialized modes
├── Receives summary results only (attempt_completion)
└── Continues orchestration
```

---

## Tool Standardization (MCP Protocol)

All three projects use/support MCP:

```json
{
  "mcp": {
    "linear": {
      "type": "remote",
      "url": "https://mcp.linear.app/mcp",
      "enabled": true
    },
    "local-tools": {
      "type": "local",
      "command": ["python", "mcp-server.py"]
    }
  }
}
```

**Benefit:** Each CLI (Claude, OpenCode, Gemini, Codex) can expose tools as MCP servers, enabling cross-agent tool sharing.

---

## Quick Wins (This Week)

1. **Create Memory Bank directory** for Kraliki itself
2. **Add checkpoint script** to spawn.py (tar before task)
3. **Add parent_id field** to task queue
4. **Add consecutive_failures counter** to agent spawn
5. **Add restricted commands list** to genomes

---

## Implementation Priority

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P0 | Memory Bank | Low | High |
| P0 | Checkpoints | Low | High |
| P1 | SSE Events | Medium | High |
| P1 | Task Hierarchy | Medium | High |
| P1 | Permission System | Medium | Medium |
| P2 | Token Tracking | Low | Medium |
| P2 | Mode Switching | Low | Medium |
| P2 | Structured Prompts | Medium | Medium |
| P3 | LiteLLM Layer | High | Medium |
| P3 | Full MCP | High | Medium |

---

## Sources

- [sst/opencode](https://github.com/sst/opencode) - 41.8k stars
- [cline/cline](https://github.com/cline/cline) - 56.3k stars
- [RooCodeInc/Roo-Code](https://github.com/RooCodeInc/Roo-Code) - 21.4k stars
- [frdel/agent-zero](https://github.com/frdel/agent-zero) - 7.4k stars
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [DeepWiki sst/opencode](https://deepwiki.com/sst/opencode)
- [Cline Source Analysis](https://zjy365.dev/blog/cline-source-code-analysis)
- [Roo Code Docs](https://docs.roocode.com)
