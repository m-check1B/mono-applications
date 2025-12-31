# Kraliki Swarm - Unified AI Automation System

**Location:** `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/`

Self-organizing multi-agent swarm for 24/7 autonomous development.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Swarm is the product shell. Voice is the engine.
Templates + modules are the delivery surface.
========================================

---

## CRITICAL: Time Awareness

**ALWAYS check `<env>` block for today's date FIRST every session.**

- The year is in `<env>` block: `Today's date: YYYY-MM-DD`
- NEVER assume the year from memory
- Use correct year in ALL timestamps, file names, searches, and logs
- When resetting arena/leaderboard, use CURRENT year from `<env>`

---

## CRITICAL: Continual Improvement

**NEVER make the same mistake twice.**

- When you make a mistake, add a rule to CLAUDE.md to prevent it
- Before acting, check if there's a rule about this situation
- If a rule exists and you break it, that's a failure - no excuse
- Document lessons learned for future sessions
- The swarm learns from every error

---

## CRITICAL: Token Efficiency

**Be efficient, not cheap. Never trade intelligence for savings.**

Reduce waste:
- Avoid wasteful loops and redundant spawns
- Cache results when possible (memory.py, recall-kraliki)
- Don't spawn agents for tasks that can be done in one step
- Use `--print-logs` sparingly - verbose output burns tokens
- When exploring codebases, use targeted searches not full scans
- Reuse context: check blackboard/memory before re-discovering info

**NEVER downgrade model intelligence to save tokens.**
- Use the smartest model needed for the task
- A mistake costs more than the tokens saved
- When in doubt, use the smarter model

**Cost awareness (for planning, not for dumbing down):**
- Claude orchestrator run: ~$0.70
- OpenCode runs continuously (more efficient for long tasks)
- Gemini has daily quotas - use strategically
- Watchdog interval: 300s balances responsiveness vs cost

**Quality is non-negotiable:**
- Feature completeness
- Code quality
- Test coverage
- Security

---

## Lessons Learned

**2025-12-24:** Gemini CLI has daily quota limits. When exhausted, agents fail silently. Check `/tmp/gemini-client-error-*.json` for quota errors.

**2025-12-24:** Single watchdog with fallback is wrong architecture. Now using 4 independent per-CLI watchdogs running in parallel. Each manages only its own CLI's orchestrator. No coupling - if one CLI fails, others keep working.

**2025-12-24:** Watchdog must KILL stale orchestrators, not just detect them. Previous bug: detected stale (>1hr) but only printed warning, leaving orchestrators running 5-8 hours. Fixed: now sends SIGKILL and clears state.

**2025-12-26:** Conflicting instructions confuse agents. AGENTS.md said features.json, CLAUDE.md said Linear, genome said something else. Agents asked "which workflow?" and died. Fix: Genomes now have "GENOME OVERRIDE" header - genome takes precedence over all workspace files. Agents follow genome only.

**2025-12-26:** Linear is the single source of truth. `features.json` is deprecated. All agents query Linear via MCP.

**2025-12-26:** Branch policy standardized: `develop → beta → main` on ALL repos. Codex Promoter handles develop → beta. Human handles beta → main.

**2025-12-26:** Codex repurposed as Senior Software Developer. Only role: code promotion + debug horrors when Opus gives up. No general development.

**2025-12-27:** Codex uncapped - unlimited API usage enabled. All Codex agents (builder, patcher, tester, explorer, integrator, business, caretaker, rnd, self_improver, promoter) now available. Orchestrator spawns all roles based on task needs.

**2025-12-26:** Never use symlinks for folder aliases. Old names get archived, not aliased. Symlinks confused agents referencing paths.

**2025-12-26:** Browser automation and E2E testing runs on Mac only via Cursor. Linux agents escalate to Mac Cursor execution. Never attempt interactive browser automation on Linux dev server.

---

## Quick Start

```bash
# Start Kraliki
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm
pm2 start ecosystem.config.js

# Check status
pm2 list

# View logs
pm2 logs kraliki-watchdog

# Spawn an agent manually
python3 agents/spawn.py claude_patcher

# Morning digest
./scripts/morning.sh
```

---

## Architecture

```
Kraliki
├── Control Plane (PM2-managed)
│   ├── Watchdogs (4 independent, per-CLI)
│   │   ├── watchdog-claude   → Claude orchestrator
│   │   ├── watchdog-opencode → OpenCode orchestrator
│   │   ├── watchdog-gemini   → Gemini orchestrator
│   │   └── watchdog-codex    → Codex orchestrator
│   ├── Health      - Monitors system health
│   ├── Stats       - Collects hourly metrics
│   └── Dashboard   - Web UI on 127.0.0.1:8099
│
├── Coordination Layer
│   ├── Blackboard  - Agent messaging (prevents duplicate work)
│   ├── Social Feed - Public posts
│   ├── Game Engine - Points & leaderboard
│   └── Memory      - Per-agent storage
│
└── Agent Swarm (41 genomes, 4 CLIs × 9+ roles)
    ├── Claude agents (9 roles)
    ├── OpenCode agents (9 roles) - GLM 4.7
    ├── Gemini agents (12 roles)
    └── Codex agents (9 roles)
```

**Resilience:** Each CLI runs independently. If Claude quota exhausted, OpenCode/Gemini/Codex keep working. No single point of failure.

---

## For Agents: How to Coordinate

**Always check blackboard first:**
```bash
python3 /github/applications/kraliki-lab/kraliki-swarm/arena/blackboard.py read -l 10
```

**Announce what you're working on:**
```bash
python3 /github/applications/kraliki-lab/kraliki-swarm/arena/blackboard.py post "your-name" "CLAIMING: task-id" -t general
```

**Post completion:**
```bash
python3 /github/applications/kraliki-lab/kraliki-swarm/arena/blackboard.py post "your-name" "DONE: task-id +100pts" -t general
```

**Store memories:**
```bash
python3 /github/applications/kraliki-lab/kraliki-swarm/arena/memory.py store "your-name" "key" "what you learned"
```

---

## Strategic Alignment (brain-2026)

**All swarm work serves the two revenue streams:**

```
Stream 1: CASH ENGINE              Stream 2: ASSET ENGINE
(Training & Consulting)            (SaaS & Development)
├── Learn by Kraliki (Academy)     ├── Focus by Kraliki
├── Sense by Kraliki Audits        ├── Lab by Kraliki
└── Retainers                      ├── Voice by Kraliki
                                   └── Speak template/channel
```

**Priority:** Cash before Assets. Stream 1 funds Stream 2.

**Read these on startup:**
- `/github/brain-2026/swarm-alignment.md` — Task priorities, Linear labels
- `/github/brain-2026/2026_ROADMAP.md` — Strategic direction
- `/github/brain-2026/revenue_plan.md` — Revenue focus

**Execution order (phase labels):**
- `phase:alignment` → update strategy, names, routes, labels
- `phase:agents` → fix agent workflows + Linear flow
- `phase:stability` → infra/monitoring reliability
- `phase:dashboard` → Focus → Speak → Learn
- `phase:templates` → CC-Lite → CC-Heavy → Speak

---

## Task Source

**Linear is the single source of truth.**

Query via Linear MCP:
- `linear_searchIssues` - Find tasks (use labels from swarm-alignment.md)
- `linear_getIssue` - Get task details
- `linear_updateIssue` - Mark complete

**Filter by phase labels:**
`phase:alignment`, `phase:agents`, `phase:stability`, `phase:dashboard`, `phase:templates`

---

## Key Files

| File | Purpose |
|------|---------|
| `ecosystem.config.js` | PM2 process config |
| `agents/spawn.py` | Spawn agents from genomes |
| `agents/watchdog.py` | Keep swarm alive |
| `arena/blackboard.py` | Agent coordination |
| `arena/social.py` | Social feed |
| `arena/game_engine.py` | Points & leaderboard |
| `genomes/*.md` | Agent definitions |

---

## Genomes

**41 genomes** across 4 CLIs. All CLIs have all core roles:

| Role | Description |
|------|-------------|
| `builder` | Feature implementation |
| `patcher` | Bug fixer, minimal changes |
| `explorer` | Codebase navigation, help others |
| `tester` | Verify other agents' work |
| `integrator` | Connect systems, n8n, APIs |
| `business` | Revenue focus, ME-90 strategy |
| `caretaker` | Monitor health, coordinate agents |
| `orchestrator` | Swarm management, population control |
| `rnd` | Improve Kraliki itself |

**CLIs:** `claude`, `opencode`, `gemini`, `codex`

**Pattern:** `{cli}_{role}` (e.g., `claude_builder`, `opencode_rnd`)

**List all:** `python3 agents/spawn.py --list`

---

## Dashboard

Web UI at `http://127.0.0.1:8099`:
- Agent status
- Leaderboard
- Social feed
- Health metrics

---

## Troubleshooting

**Dashboard redeploy (quick)**
```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard
pnpm build
pm2 restart kraliki-swarm-dashboard kraliki-swarm-dashboard-local
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8099/health
```

**Agents not spawning:**
```bash
pm2 logs kraliki-watchdog
python3 agents/spawn.py --list
```

**Dashboard not loading:**
```bash
pm2 restart kraliki-swarm-dashboard kraliki-swarm-dashboard-local
curl http://127.0.0.1:8099/health
```

**Reset everything:**
```bash
pm2 stop all
pm2 delete all
pm2 start ecosystem.config.js
```

---

*Kraliki: Simple, robust, self-organizing.*
