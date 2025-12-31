#!/usr/bin/env python3
"""Kraliki Swarm Father.

A 'smart' agent spawner that:
1. Reads the blackboard for requests and status.
2. Analyzes current swarm population.
3. Uses an LLM to decide which agents to spawn.
4. Spawns agents via spawn.py.

Runs as a PM2-managed process.
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

KRALIKI_DIR = Path(__file__).parent.parent
ARENA_DIR = KRALIKI_DIR / "arena"
AGENTS_DIR = KRALIKI_DIR / "agents"
CONFIG_DIR = KRALIKI_DIR / "control"
LOGS_DIR = KRALIKI_DIR / "logs" / "control"

# Configuration
CHECK_INTERVAL = 600  # 10 minutes
MAX_TOTAL_AGENTS = 10

def get_active_agents() -> list:
    """Get list of active agent processes."""
    try:
        cli_patterns = ["claude", "opencode", "gemini", "codex", "grok"]
        pattern = "|".join(cli_patterns)
        
        result = subprocess.run(
            ["pgrep", "-f", f"({pattern}).*kraliki"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            return result.stdout.strip().split("\n")
        return []
    except Exception:
        return []

def read_blackboard() -> str:
    """Read recent blackboard messages."""
    try:
        from arena import blackboard
        messages = blackboard.read(limit=20)
        formatted = ""
        for m in messages:
            formatted += f"[{m['time']}] {m['agent']}: {m['message']}\n"
        return formatted
    except Exception as e:
        return f"Error reading blackboard: {e}"

def decide_spawns(blackboard_context: str, active_agents: list) -> list:
    """Call Gemini to decide which agents to spawn."""
    prompt = f"""
You are the Kraliki Swarm Father. Your job is to decide which agents to spawn based on the current context.

CURRENT ACTIVE AGENTS:
{json.dumps(active_agents, indent=2)}

RECENT BLACKBOARD MESSAGES:
{blackboard_context}

AVAILABLE GENOMES:
- gemini_builder: Build features, code.
- gemini_patcher: Fix bugs.
- gemini_tester: Verify work.
- gemini_explorer: Map codebase.
- gemini_researcher: Market/tech research.
- gemini_designer: UI/UX.
- gemini_integrator: API/Integrations.

CIRCUIT BREAKERS:
(Assume Claude and Codex are currently limited, prefer Gemini)

DECISION RULES:
1. Don't spawn more than 3 agents at once.
2. Only spawn if there is a clear need or a request on the blackboard.
3. Avoid duplicate roles if they are already active and not stuck.

OUTPUT FORMAT:
Return a JSON list of genome names to spawn. Example: ["gemini_builder", "gemini_patcher"]
Return only the JSON list.
"""
    try:
        # Call Gemini CLI
        result = subprocess.run(
            ["gemini", "-y"],
            input=prompt.encode(),
            capture_output=True,
            text=False, # Use bytes for input
        )
        output = result.stdout.decode().strip()
        # Find JSON list in output
        start = output.find("[")
        end = output.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(output[start:end])
        return []
    except Exception as e:
        print(f"Error deciding spawns: {e}")
        return []

def spawn_agent(genome_name: str):
    """Execute spawn.py."""
    try:
        subprocess.run(
            ["python3", str(AGENTS_DIR / "spawn.py"), genome_name],
            cwd=str(KRALIKI_DIR),
        )
    except Exception as e:
        print(f"Error spawning {genome_name}: {e}")

def run_cycle():
    print(f"[{datetime.now().isoformat()}] Swarm Father cycle start.")
    
    # 1. Read context
    bb_context = read_blackboard()
    active = get_active_agents()
    
    if len(active) >= MAX_TOTAL_AGENTS:
        print(f"Max agents reached ({len(active)}). Skipping spawn.")
        return

    # 2. Decide
    to_spawn = decide_spawns(bb_context, active)
    
    # 3. Spawn
    if to_spawn:
        print(f"Decided to spawn: {to_spawn}")
        for genome in to_spawn:
            spawn_agent(genome)
            time.sleep(5) # Throttle
    else:
        print("No spawns needed.")

def main():
    print("Kraliki Swarm Father active.")
    sys.path.insert(0, str(ARENA_DIR))
    
    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"Error in Swarm Father loop: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
