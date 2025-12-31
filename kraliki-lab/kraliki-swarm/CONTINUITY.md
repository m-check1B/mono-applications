# Kraliki Continuity Ledger

## Goal
Build unified AI automation system (Kraliki) merging GIN infrastructure + Darwin swarm coordination.
**Success criteria:** PM2-managed processes running, agents self-organizing via blackboard/social, dashboard live.

## Constraints/Assumptions
- Reuse GIN dashboard (don't rebuild from scratch)
- Keep simple: ~3k lines vs GIN's 10k
- JSON files for data (Turso/PostgreSQL optional later)
- Gemini/Codex quotas exhausted until Dec 26 / ~12h

## Key Decisions
- **Name:** Kraliki (not Ginwin)
- **Architecture:** Control plane (PM2) + Coordination layer (arena) + Agent swarm
- **Location:** `/ai-automation/kraliki/`
- **Only 4 PM2 processes:** watchdog, health, stats, dashboard
- **5 Claude genomes:** patcher, explorer, tester, business, integrator

## State

### Done
- Architecture plan created (ARCHITECTURE.md)
- Directory structure built
- Control plane migrated from GIN (health-monitor, stats-collector, circuit-breakers)
- Arena migrated from Darwin (blackboard, social, game_engine, memory, reputation)
- New spawner (spawn.py) and watchdog (watchdog.py) created
- PM2 ecosystem.config.js created
- Genomes updated with Kraliki paths
- All 4 PM2 processes running
- Watchdog spawning agents automatically
- Social feed and blackboard working
- **Fixed spawner** to use stdin for Claude (was passing genome as CLI argument)
- **Fixed health-monitor.py** to check Kraliki Swarm endpoint (was checking old TL;DR Bot)
- **Fixed health/stats** to loop continuously (were exiting after one run, causing PM2 restarts)
- **Fixed stats-collector.py** paths (KRALIKI_DIR, FEATURES_FILE=None for Linear)
- **Archived GIN and Darwin v1** to `_templates/` for reference
- **Verified by darwin-claude-tester**: All 4 PM2 processes ONLINE, control plane STABLE
- **First real fix by swarm**: claude_patcher fixed CSRF vulnerability in soldier-portal

### Now
- Kraliki is LIVE and DOING REAL WORK
- **8 PM2 processes**: watchdog, health, stats, dashboard, n8n-api, comm, comm-ws, msg-poller
- **Communication Hub**: REST API (:8199) + WebSocket (:8200) for real-time messaging
- **Caretaker genome** created for permanent swarm supervision
- **Mac Cursor execution**: manual browser tasks run directly in Cursor with `/github` repo access
- Agents spawning every 5 minutes, coordinating via blackboard + direct messaging
- Linear labels: agent-message for inter-agent communication

### Key Finding
- **Mac Cursor is the single path for interactive browser automation**
- Faster, more reliable for E2E testing and visual verification
- All interactive browser tasks should be executed via Cursor on Mac

### Work Completed by Swarm
- **VD-186**: n8n <-> Kraliki bidirectional API bridge (integrator)
- **JWT Security**: gin-dashboard JWKS verification (integrator)
- **Stats-collector**: Fixed GIN_DIR references (tester/patcher)
- **Architecture docs**: Shared on blackboard (explorer)
- **Revenue analysis**: ME-90 blockers identified (business)

### Next
- Get Gemini council when quota resets (Dec 22 evening)
- Add Linear MCP integration for task querying
- Dashboard customization for Kraliki (leaderboard, social feed view)
- Consider Turso/PostgreSQL if JSON files become bottleneck
- **Mac Cursor workflow** - run browser tasks directly via Cursor on Mac

## Open Questions
- Dashboard needs Kraliki-specific views (leaderboard, social) `UNCONFIRMED`
- Should genomes include Codex/Gemini variants? (quota issues) `WAITING`

## Working Set
- `/ai-automation/kraliki/` - Main directory
- `pm2 list` - Check processes
- `python3 arena/social.py feed` - View social
- `python3 agents/spawn.py --list` - List genomes
- `pm2 logs kraliki-watchdog` - View logs

---
*Last updated: 2025-12-22 11:50 CET*
