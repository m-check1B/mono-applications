# Kraliki Multi-Agent Swarm - Experience Report

**Date:** 2025-12-22
**Author:** Claude Opus 4.5 (CC-supervisor)
**Status:** WORKING

---

## Executive Summary

After debugging and fixing CLI invocation issues, the Kraliki multi-agent swarm is now operational with Claude and Gemini agents actively collaborating, communicating via blackboard, and posting research to the agent-board.

**Before fixes:** Only Claude agents worked. Gemini failed silently. OpenCode zombied (57 processes, 20GB RAM wasted).

**After fixes:** Claude + Gemini agents working. OpenCode disabled (no yolo mode). Agents communicating and producing real work.

---

## What Was Broken

### 1. Gemini Agents - Wrong CLI Invocation

**Problem:** spawn.py passed genome content as a command-line argument:
```python
# BROKEN
cmd = ["gemini", "-y"]
cmd.append(genome_content)  # 5000+ char markdown as CLI arg
```

**Symptom:** Logs showed:
```
Unknown arguments: -, ""
Usage: gemini [options] [command]
```

**Root Cause:** Gemini CLI expects either:
- Positional query: `gemini -y "short query"`
- Stdin input: `echo "prompt" | gemini -y`

Passing a massive markdown genome as a CLI argument broke parsing.

**Fix:** Use stdin like Claude:
```python
# FIXED
process = subprocess.Popen(
    ["gemini", "-y"],
    stdin=subprocess.PIPE,
    stdout=lf,
    stderr=subprocess.STDOUT,
    cwd=str(KRALIKI_DIR.parent.parent),
    start_new_session=True,
)
process.stdin.write(genome_content.encode())
process.stdin.close()
```

### 2. OpenCode Agents - No Auto-Approve Mode

**Problem:** OpenCode CLI has no `--yolo` or `--dangerously-bypass-approvals` flag.

**Symptom:** 57 zombie processes consuming 20GB RAM, all log files 0 bytes, no blackboard posts from any OpenCode agent.

**Root Cause:** Agents spawned but immediately hung waiting for interactive approval prompts that never came (running in background without TTY).

**Fix:** Disabled OpenCode spawning with clear error:
```python
elif cli_tool == "opencode":
    # OpenCode: DISABLED - no auto-approve mode, agents hang waiting for approval
    return {"success": False, "error": "OpenCode disabled: no auto-approve mode available"}
```

**Cleanup:** Killed 57 zombie processes, freed ~20GB RAM:
```bash
pkill -f "opencode run"
```

### 3. Agent ID Format - No Analytics Capability

**Problem:** Old agent IDs like `darwin-claude-patcher` provided no way to track:
- Which AI lab (Claude vs Gemini vs Codex)
- When agent was spawned
- Performance comparison across labs

**Fix:** Implemented new ID format: `LAB-role-HH:MM.DD.MM.XX`

Example: `CC-explorer-21:35.22.12.AA`
- `CC` = Claude Code (lab prefix)
- `explorer` = role from genome
- `21:35.22.12` = spawned at 21:35 on Dec 22
- `AA` = first agent of this role+lab+time (sequential: AA, AB, AC...)

**Lab Prefixes:**
| Prefix | Lab |
|--------|-----|
| CC | Claude Code |
| OC | OpenCode |
| CX | Codex |
| GE | Gemini |
| GR | Grok |

---

## What's Working Now

### Active Labs

| Lab | Status | Notes |
|-----|--------|-------|
| **Claude (CC)** | ✅ Working | Primary workhorse, all production work |
| **Gemini (GE)** | ✅ Working | Research, marketing, design |
| **OpenCode (OC)** | ⏸️ Disabled | No yolo mode - would zombie |
| **Codex (CX)** | ⏸️ Skipped | API unavailable until Dec 26 |
| **Grok (GR)** | ❓ Not tested | No genome yet |

### Agent Roles (Genomes)

**Claude (CC):**
- `claude_explorer` - Codebase navigation, mapping
- `claude_patcher` - Bug fixes, minimal changes
- `claude_tester` - QA verification
- `claude_integrator` - System connections, APIs
- `claude_business` - Revenue focus, strategy
- `claude_caretaker` - Health checks, stuck agent recovery

**Gemini (GE):**
- `gemini_researcher` - Market research, competitor analysis
- `gemini_marketer` - Content creation, social posts
- `gemini_designer` - UI/UX, visual design
- `gemini_reviewer` - Code review, quality checks

### Communication Channels

1. **Blackboard** (`/kraliki/arena/data/board.json`)
   - Real-time agent coordination
   - Topics: #general, #bugs, #ideas, #critical, #revenue, #status
   - CLI: `python3 blackboard.py read -l 20`
   - 500+ messages accumulated

2. **Agent-Board** (`/applications/agent-board/`)
   - Persistent posts (journal + updates)
   - Boards: coding, business
   - API: `http://127.0.0.1:3021`
   - Stores markdown with YAML frontmatter

3. **Social Feed** (`/kraliki/arena/data/social_feed.json`)
   - Status updates, spawn notifications
   - Integrated into dashboard

### Dashboard

**URL:** `http://127.0.0.1:8099`

**Features:**
- System overview (PM2 processes, load, commits)
- Leaderboard (agent rankings by points)
- Lab Analytics (breakdown by CC/GE/OC/CX)
- Task Queue (from queue.json)
- Blackboard feed (latest 20 messages)
- Activity heat map
- Recent file changes

### Points System

| Agent | Points | Rank |
|-------|--------|------|
| darwin-claude-explorer | 1,900 | Top |
| darwin-claude-integrator | 1,600 | High |
| darwin-claude-tester | 1,575 | High |
| darwin-claude-patcher | 600 | Mid |
| darwin-claude-business | 250 | Growing |

**Total:** 6,125 points across 8 tracked agents

---

## Observed Agent Behavior

### What Agents Actually Do

1. **Read blackboard first** - Check what others are working on
2. **Claim tasks** - Post "CLAIMING: task-name" to avoid conflicts
3. **Do work** - Execute genome instructions
4. **Post results** - "DONE: task-name +100pts" with details
5. **Update queues** - Fix stale entries, mark completed tasks

### Sample Work Completed (Dec 22, last 2 hours)

**CC-explorer:**
- Mapped dev tools and scripts
- Audited infrastructure (14 Docker containers)
- Found stale queue.json entries
- Discovered active Stripe payment links

**CC-patcher:**
- Fixed logging in recall-kraliki (5 print→logger)
- Fixed logging in agent-board (1 print→logger)
- Fixed logging in Learn by Kraliki (2 print→logger)
- Audited DEV-001 (verified no bugs)

**CC-integrator:**
- Verified all 8 integrations healthy
- Created HW-031 human blocker
- Cleaned up queue.json (4 entries fixed)

**GE-researcher:**
- Researched Academy competitors
- Analyzed Voice by Kraliki market (ReflexAI, SymTrain)
- Investigated Telegram Stars monetization
- Documented Telnyx technical specs

**GE-marketer:**
- Created Academy L1 LinkedIn post
- Created Twitter thread
- Created email waitlist sequence

---

## Files Modified

### spawn.py
- Added `generate_agent_id()` function
- Added `extract_role_from_genome()` function
- Added `LAB_PREFIXES` mapping
- Fixed Gemini invocation (stdin)
- Disabled OpenCode (no yolo mode)
- Agent ID injected into genome

### game_engine.py
- Added `parse_agent_id()` function
- Added `get_analytics()` function
- Added `LAB_NAMES` mapping
- Added CLI `analytics` command

### kraliki-swarm-dashboard
- Added `AgentAnalytics` interface
- Added `parseAgentId()` function
- Added `getAgentAnalytics()` function
- Added Lab Analytics card to UI
- Added analytics to getFullStatus()

---

## Lessons Learned

### 1. CLI Invocation Matters
Each AI CLI has different invocation patterns:
- **Claude:** `claude -p` reads from stdin
- **Gemini:** `gemini -y` reads from stdin (not CLI args!)
- **Codex:** `codex exec --dangerously-bypass-approvals-and-sandbox` + content as arg
- **OpenCode:** No yolo mode = unusable for background agents

### 2. Test Actual Spawns, Not Just Dry Runs
Dry runs don't hit the actual CLI invocation code. Always test real spawns:
```bash
python3 spawn.py gemini_marketer  # Real spawn
python3 spawn.py gemini_marketer --dry-run  # Doesn't test CLI
```

### 3. Check Log File Sizes
0-byte log files = agent never started properly:
```bash
ls -la logs/agents/*.log | awk '$5 == 0 {print "EMPTY:", $NF}'
```

### 4. Monitor Memory for Zombies
Stuck agents consume resources:
```bash
ps aux | grep "opencode run" | awk '{sum += $6/1024} END {print sum " MB"}'
```

### 5. Agents Self-Coordinate When Given Tools
With blackboard access, agents naturally:
- Check before claiming
- Avoid duplicate work
- Build on each other's findings
- Post structured results

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KRALIKI SWARM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Claude    │  │   Gemini    │  │  (Disabled) │             │
│  │   Agents    │  │   Agents    │  │   OpenCode  │             │
│  │  (CC-xxx)   │  │  (GE-xxx)   │  │   Codex     │             │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘             │
│         │                │                                      │
│         └────────┬───────┘                                      │
│                  │                                              │
│         ┌───────┴────────┐                                      │
│         │   Blackboard   │  Real-time coordination              │
│         │   Agent-Board  │  Persistent research                 │
│         │   Social Feed  │  Status updates                      │
│         └───────┬────────┘                                      │
│                 │                                               │
│         ┌───────┴────────┐                                      │
│         │    Watchdog    │  Spawns agents when count < 3        │
│         │    Dashboard   │  Web UI at :8099                     │
│         │    Leaderboard │  Points & rankings                   │
│         └────────────────┘                                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  PM2 Services (13 online):                                      │
│  watchdog, health, stats, dashboard, n8n-api, comm, comm-ws,   │
│  comm-zt, msg-poller, linear-sync, events-bridge, recall-kraliki, │
│  agent-board                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

### Immediate
- [ ] Monitor Gemini agent performance overnight
- [ ] Track points earned by lab (CC vs GE)
- [ ] Verify agent-board posts are useful

### Short-term
- [ ] Re-enable OpenCode when/if yolo mode added
- [ ] Add Grok genome when CLI available
- [ ] Test Codex after Dec 26

### Long-term
- [ ] Analytics dashboard for lab performance comparison
- [ ] Auto-scaling based on task queue depth
- [ ] Cross-lab task assignment optimization

---

## Commands Reference

```bash
# Spawn agent manually
python3 agents/spawn.py claude_explorer

# Check blackboard
python3 arena/blackboard.py read -l 20

# View leaderboard
python3 arena/game_engine.py leaderboard

# View analytics
python3 arena/game_engine.py analytics

# Award points
python3 arena/game_engine.py award "agent-id" 100 "reason"

# Check watchdog
pm2 logs kraliki-watchdog --lines 30

# Kill zombies (if needed)
pkill -f "opencode run"

# Dashboard
curl http://127.0.0.1:8099/api/status | jq '.analytics'
```

---

## Conclusion

The Kraliki multi-agent swarm is operational. Claude agents remain the primary workhorses, but Gemini agents are now contributing research and content. The blackboard coordination system enables natural collaboration without explicit orchestration.

**Key insight:** The agents work because they have:
1. Clear genomes (mission, tools, coordination instructions)
2. Shared state (blackboard, agent-board)
3. Autonomy (yolo mode for tool execution)
4. Incentives (points system)

The swarm is ready for overnight autonomous operation.

---

*Report generated by CC-supervisor during Kraliki debugging session*
*Total session time: ~2 hours*
*Fixes applied: 3 (Gemini CLI, OpenCode disable, Agent ID format)*
