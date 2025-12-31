# Kraliki Architecture Plan

**Version:** 2.0
**Date:** 2025-12-22
**Status:** Planning

---

## First Principles

What do we actually need for 24/7 autonomous AI development?

1. **Tasks** - Something to work on (Linear)
2. **Agents** - Workers that do the work (Claude, OpenCode, Gemini, Codex)
3. **Coordination** - So agents don't conflict (Blackboard)
4. **Observability** - See what's happening (Dashboard, Social Feed)
5. **Reliability** - Keep running when things fail (PM2, Health Checks)
6. **Memory** - Learn and remember (mgrep + local memory)

That's it. No highways, no perpetual-duos, no complex orchestrators.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Kraliki Swarm is the product shell. Templates are the delivery surface.
Voice by Kraliki is the core engine for call center templates.
========================================

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         KRALIKI                                  │
│                   /ai-automation/kraliki/                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    CONTROL PLANE                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ Spawner │  │ Health  │  │ Stats   │  │Dashboard│     │   │
│  │  │  (PM2)  │  │ Monitor │  │Collector│  │ (Web)   │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    COORDINATION LAYER                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │ Blackboard  │  │ Social Feed │  │ Game Engine │      │   │
│  │  │ (JSON file) │  │  (Posts)    │  │  (Points)   │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    AGENT SWARM                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ Claude  │  │OpenCode │  │ Gemini  │  │ Codex   │     │   │
│  │  │ Agents  │  │ Agents  │  │ Agents  │  │ Agents  │     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    EXTERNAL SERVICES                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │   │
│  │  │ Linear  │  │  mgrep  │  │ GitHub  │                  │   │
│  │  │  (MCP)  │  │ (Memory)│  │  (Code) │                  │   │
│  │  └─────────┘  └─────────┘  └─────────┘                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Map

### 1. CONTROL PLANE (Infrastructure)

| Component | Source | Action | File |
|-----------|--------|--------|------|
| PM2 Config | GIN | Simplify | `ecosystem.config.js` |
| Health Monitor | GIN | Keep | `health-monitor.py` |
| Stats Collector | GIN | Keep | `stats-collector.py` |
| Dashboard | GIN | Migrate | `/applications/kraliki-swarm/dashboard/` |
| Circuit Breakers | GIN | Keep | `circuit-breakers.json` |

### 2. COORDINATION LAYER (Darwin's Innovation)

| Component | Source | Action | File |
|-----------|--------|--------|------|
| Blackboard | Darwin | Keep | `arena/blackboard.py` |
| Social Feed | Darwin | Keep | `arena/social.py` |
| Game Engine | Darwin | Keep + fix | `arena/game_engine.py` |
| Memory | Darwin | Keep | `arena/memory.py` |
| Reputation | Darwin | Keep | `arena/reputation.py` |

### 3. AGENT SYSTEM

| Component | Source | Action | File |
|-----------|--------|--------|------|
| Spawner | Darwin | Improve | `spawn.py` |
| Genomes | Darwin | Keep | `genomes/*.md` |
| Watchdog | Darwin | Add PM2 | Part of ecosystem.config.js |
| Bootstrap | Darwin | Keep | `bootstrap.sh` |

### 4. INTEGRATIONS

| Component | Source | Action | File |
|-----------|--------|--------|------|
| Linear MCP | GIN | Keep | Via Claude MCP |
| mgrep Memory | GIN | Keep | `memory/mgrep_client.py` |
| Linear Sync | GIN | Keep | `linear-sync.py` |

---

## Directory Structure

```
/ai-automation/kraliki/
├── ecosystem.config.js      # PM2 config (simplified)
├── CLAUDE.md                # Instructions for Claude agents
├── README.md                # Documentation
│
├── control/                 # Control plane
│   ├── health-monitor.py    # From GIN
│   ├── stats-collector.py   # From GIN
│   ├── circuit-breakers.json
│   └── health-status.json
│
├── arena/                   # Coordination layer (from Darwin)
│   ├── blackboard.py
│   ├── social.py
│   ├── game_engine.py
│   ├── memory.py
│   ├── reputation.py
│   └── data/
│       ├── board.json
│       ├── social_feed.json
│       ├── leaderboard.json
│       └── memories/
│
├── agents/                  # Agent management
│   ├── spawn.py             # Unified spawner
│   ├── watchdog.py          # Keep swarm alive
│   └── bootstrap.sh
│
├── genomes/                 # Agent definitions
│   ├── claude_patcher.md
│   ├── claude_explorer.md
│   ├── claude_business.md
│   ├── claude_tester.md
│   ├── opencode_*.md
│   └── gemini_*.md
│
├── integrations/            # External services
│   ├── linear_sync.py
│   └── mgrep_client.py
│
├── logs/                    # All logs here
│   ├── agents/
│   ├── control/
│   └── daily/
│
└── scripts/                 # Utility scripts
    ├── morning.sh
    ├── status.sh
    └── reset.sh
```

---

## What Gets Removed (GIN Cruft)

| Component | Why Remove |
|-----------|-----------|
| 6 Highways | Replaced by Darwin swarm coordination |
| CEO Orchestrator | Agents self-organize via blackboard |
| Perpetual Duo | Replaced by watchdog + spawner |
| Multiple orchestrators | One spawner rules them all |
| features.json | Linear is source of truth |
| Council | Agents coordinate via social feed |
| Batch Executor | Agents pick their own work |
| Workers (dev, bizdev, marketing, tester) | Replaced by genomes |

**Lines removed:** ~8000 (GIN highways, orchestrators)
**Lines kept:** ~2000 (Darwin arena) + ~1000 (GIN infra)
**Net:** ~3000 lines total (70% reduction)

---

## PM2 Configuration (Simplified)

Only 4 processes needed:

```javascript
module.exports = {
  apps: [
    {
      name: 'kraliki-watchdog',
      script: 'agents/watchdog.py',
      // Keeps swarm alive, spawns agents
    },
    {
      name: 'kraliki-health',
      script: 'control/health-monitor.py',
      // Monitors system health
    },
    {
      name: 'kraliki-stats',
      script: 'control/stats-collector.py',
      // Collects metrics hourly
    },
    {
      name: 'kraliki-swarm-dashboard',
      script: 'build/index.js',
      cwd: '/applications/kraliki-swarm-dashboard',
      // Web UI
    }
  ]
}
```

---

## Dashboard Migration

From GIN dashboard, keep:
- SvelteKit framework
- Zitadel auth integration
- Style 2026 CSS
- Health endpoint

Add Darwin features:
- Leaderboard view
- Social feed view
- Agent status (running/idle)
- Memory browser
- Spawn controls

---

## Agent Roles

### Linux Agents (Kraliki Swarm)

| Agent | CLI | Role | Best For |
|-------|-----|------|----------|
| **claude_patcher** | claude | Bug fixer | Minimal surgical fixes |
| **claude_explorer** | claude | Navigator | Codebase exploration, helping others |
| **claude_tester** | claude | QA | Verify other agents' work |
| **claude_business** | claude | Revenue | ME-90 strategy, business tasks |
| **claude_integrator** | claude | Glue | APIs, n8n, system connections |
| **claude_caretaker** | claude | Supervisor | Permanent swarm health monitor |
| **opencode_patcher** | opencode | Bug fixer | Fast patches, simple fixes |
| **opencode_builder** | opencode | Builder | New features, scaffolding |

### Mac Agents (External)

| Agent | Platform | Role | Best For |
|-------|----------|------|----------|
| **Mac Cursor Operator** | Cursor (Mac) | **E2E QA Champion** | Browser automation, visual testing, OAuth/payment flows, manual verification |
| Claude Desktop | Claude | General | Complex reasoning tasks on Mac when Cursor is not available |

### Communication

- **Linux ↔ Linux**: Direct via comm hub (REST :8199, WebSocket :8200)
- **Mac ↔ Linux**: Escalate via Linear with `mac-cursor` label or comment; no bridge/polling
- **All agents**: Blackboard for public announcements, Social feed for status

---

## Agent Lifecycle

```
1. Watchdog checks: "Do we have 3+ active agents?"
   │
   ├── NO → Spawn agents from genome pool
   │
   └── YES → Sleep 5 minutes, repeat

2. Agent starts:
   │
   ├── Read blackboard (what's claimed?)
   ├── Query Linear (what's available?)
   ├── Post to social: "CLAIMING: task-id"
   ├── Do the work
   ├── Post result to social
   ├── Update game engine (+points)
   └── Exit (or continue if more work)

3. Health monitor:
   │
   ├── Check agent count
   ├── Check API quotas
   ├── Check error rates
   └── Trip circuit breakers if needed
```

---

## Verification Checklist

After build, verify:

- [ ] PM2 starts all 4 processes
- [ ] Dashboard loads at 127.0.0.1:8099
- [ ] Health endpoint returns JSON
- [ ] Watchdog spawns agents when count < 3
- [ ] Agents can read blackboard
- [ ] Agents can post to social
- [ ] Game engine awards points
- [ ] Stats collector runs hourly
- [ ] Linear MCP accessible to agents
- [ ] mgrep memory working

---

## Test Plan (Machine Building Machine)

Kraliki tests itself:

1. **Spawn Test Agent** with genome:
   ```
   Mission: Verify Kraliki is working
   Tasks:
   - Post to social feed
   - Read blackboard
   - Store a memory
   - Query Linear
   - Report results
   ```

2. **Verify outputs:**
   - Social post exists
   - Memory file created
   - Points awarded
   - No errors in logs

3. **Stress test:**
   - Spawn 5 agents simultaneously
   - Check for conflicts
   - Verify coordination

---

## Milestones

| # | Milestone | Gemini Review |
|---|-----------|---------------|
| M1 | Architecture plan complete | Yes - this doc |
| M2 | Directory structure created | No |
| M3 | Control plane migrated | Yes |
| M4 | Arena migrated | No |
| M5 | Dashboard migrated | Yes - UI/UX |
| M6 | Verification complete | Yes |
| M7 | Self-test passes | Yes - final |

---

*Plan created: 2025-12-22*
*Ready for Gemini council review*
