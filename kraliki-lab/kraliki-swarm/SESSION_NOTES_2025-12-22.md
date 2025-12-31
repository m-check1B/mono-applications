# Kraliki Session Notes - Dec 22, 2025 (23:30 CET)

## What We Did Tonight

### 1. Killed OpenCode Agents
- Disabled `opencode_patcher.md` and `opencode_builder.md` (renamed to .disabled)
- No more opencode agents spawning

### 2. Enabled Codex Agents
- Removed hardcoded skip in `watchdog.py` (was blocking codex until Dec 26)
- Codex agents now spawning and working (verified CX-explorer ran successfully)
- 5 codex genomes available: builder, explorer, integrator, patcher, tester

### 3. Set Up Tmux for Overnight
- Session: `kraliki-monitor` (3 windows: logs, monit, status)
- Crontab: `@reboot /github/scripts/restore-tmux.sh`
- PM2 saved to `~/.pm2/dump.pm2`

### 4. Roadmap Updated (brain-2026/task.md)
New task for Dec 23: **Kraliki Swarm Multi-page Hub**

Pages planned:
1. Overview (current dashboard)
2. Agents (status table + launcher with genome/CLI checkboxes)
3. Linear (iframe)
4. Blackboard (display + user posting)
5. Recall by Kraliki (agent memory usage)
6. Agent Board (iframe)

Key feature: Genome/CLI toggles replace hardcoded API outage skips

## Current State

- **PM2:** 13/13 processes online
- **Agents:** Claude, Codex, Gemini all enabled
- **Tmux:** kraliki-monitor running
- **Watchdog:** Spawning agents every 5 min

## To Resume Tomorrow

```bash
# Attach to monitoring session
tmux attach -t kraliki-monitor

# Check agent status
python3 /github/ai-automation/kraliki/arena/blackboard.py read -l 20

# Check PM2
pm2 list

# Start working on dashboard
# Task: Kraliki Swarm Multi-page Hub (brain-2026/task.md)
```
