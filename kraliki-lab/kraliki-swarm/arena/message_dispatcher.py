#!/usr/bin/env python3
"""Kraliki Message Dispatcher - Intelligent Reactive Agent.

Continuously monitors the blackboard and ACTS when needed.
Not a passive logger - an intelligent agent that decides to act or not.

Runs as a PM2 daemon process.

Actions it can take:
- Spawn an agent to handle a request
- Create a Linear issue for bugs/features
- Escalate to human-work-needed queue
- Route messages between agents
- Do nothing (if no action needed)
"""

import json
import time
import os
import sys
import logging
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [DISPATCHER] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/kraliki-dispatcher.log')
    ]
)
logger = logging.getLogger(__name__)

ARENA_DIR = Path(__file__).parent
DATA_DIR = ARENA_DIR / "data"
DISPATCH_STATE_FILE = DATA_DIR / "dispatcher_state.json"
SPAWN_SCRIPT = ARENA_DIR.parent / "agents" / "spawn.py"
HUMAN_QUEUE_DIR = Path("/home/adminmatej/github/ai-automation/humans-work-needed")

# Import arena modules
sys.path.insert(0, str(ARENA_DIR))
from blackboard import read, post
from memory import remember
from game_engine import award_points


def memory_store(agent: str, key: str, value: str):
    """Store key:value for agent."""
    remember(f"{key}: {value}", agent=agent, tags=[key])


class ReactiveDispatcher:
    """Intelligent dispatcher that decides to act or not."""

    # Keywords that trigger specific actions
    ACTION_TRIGGERS = {
        'BLOCKED': 'escalate_human',      # Needs human intervention
        'URGENT': 'spawn_agent',           # Spawn agent immediately
        'BUG': 'create_issue',             # Create Linear issue
        'FEATURE': 'create_issue',         # Create Linear issue
        'HELP': 'spawn_helper',            # Spawn helper agent
        'REVIEW': 'spawn_reviewer',        # Spawn code reviewer
    }

    # CLI fallback order - try each until one works
    CLI_FALLBACK_ORDER = ['claude', 'opencode', 'gemini', 'codex']

    # Track CLI availability (updated on failures)
    cli_status: Dict[str, dict] = {}

    def __init__(self):
        self.last_message_id = self._load_state()
        self.running = True
        self.processed_requests = set()  # Track what we've already handled
        self.cli_status = {cli: {'available': True, 'last_fail': None, 'fail_count': 0}
                          for cli in self.CLI_FALLBACK_ORDER}
        logger.info(f"Reactive dispatcher initialized, last message: {self.last_message_id}")

    def _load_state(self) -> int:
        """Load last processed message ID."""
        try:
            if DISPATCH_STATE_FILE.exists():
                state = json.loads(DISPATCH_STATE_FILE.read_text())
                return state.get('last_message_id', 0)
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
        return 0

    def _save_state(self):
        """Save current processing state."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            DISPATCH_STATE_FILE.write_text(json.dumps({
                'last_message_id': self.last_message_id,
                'updated': datetime.now().isoformat()
            }, indent=2))
        except Exception as e:
            logger.warning(f"Could not save state: {e}")

    # =========================================================================
    # ACTION METHODS - These actually DO things
    # =========================================================================

    def _is_cli_available(self, cli: str) -> bool:
        """Check if CLI is available (not in cooldown from recent failures)."""
        status = self.cli_status.get(cli, {})
        if not status.get('available', True):
            # Check if cooldown expired (5 min after failure)
            last_fail = status.get('last_fail')
            if last_fail:
                cooldown = timedelta(minutes=5)
                if datetime.now() - datetime.fromisoformat(last_fail) > cooldown:
                    # Reset - give it another chance
                    self.cli_status[cli] = {'available': True, 'last_fail': None, 'fail_count': 0}
                    return True
            return False
        return True

    def _mark_cli_failed(self, cli: str):
        """Mark CLI as temporarily unavailable."""
        status = self.cli_status.get(cli, {'fail_count': 0})
        fail_count = status.get('fail_count', 0) + 1
        self.cli_status[cli] = {
            'available': False,
            'last_fail': datetime.now().isoformat(),
            'fail_count': fail_count
        }
        logger.warning(f"CLI {cli} marked unavailable (fail #{fail_count})")

    def _mark_cli_success(self, cli: str):
        """Mark CLI as available after success."""
        self.cli_status[cli] = {'available': True, 'last_fail': None, 'fail_count': 0}

    def spawn_agent(self, role: str, task: str) -> bool:
        """Spawn an agent to handle a task, with CLI fallback.

        Flow:
        1. Post task to blackboard so agent can read it
        2. Spawn agent (it reads blackboard as first action per genome)
        """
        # Extract role from genome if it's in cli_role format
        if '_' in role:
            parts = role.split('_', 1)
            preferred_cli = parts[0]
            role_name = parts[1]
        else:
            preferred_cli = None
            role_name = role

        # Build fallback order - preferred CLI first, then others
        cli_order = list(self.CLI_FALLBACK_ORDER)
        if preferred_cli and preferred_cli in cli_order:
            cli_order.remove(preferred_cli)
            cli_order.insert(0, preferred_cli)

        # Try each CLI in order
        for cli in cli_order:
            if not self._is_cli_available(cli):
                logger.debug(f"Skipping {cli} - in cooldown")
                continue

            genome = f"{cli}_{role_name}"
            logger.info(f"SPAWNING agent {genome} for: {task[:50]}...")

            try:
                # Post task to blackboard for agent to pick up
                post("DISPATCHER", f"TASK for {genome}: {task}", topic="tasks")

                # Spawn agent (no --task arg, agent reads blackboard)
                result = subprocess.run(
                    ["python3", str(SPAWN_SCRIPT), genome],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"Successfully spawned {genome}")
                    self._mark_cli_success(cli)
                    post("DISPATCHER", f"Spawned {genome} to handle: {task[:100]}", topic="system")
                    return True
                else:
                    # Check for quota/API errors
                    stderr = result.stderr.lower()
                    if any(err in stderr for err in ['quota', 'rate limit', 'api error', 'unavailable', '429', '503']):
                        logger.warning(f"{cli} API unavailable, trying next CLI...")
                        self._mark_cli_failed(cli)
                        continue
                    else:
                        logger.error(f"Failed to spawn {genome}: {result.stderr[:200]}")
                        # Don't mark as failed for non-API errors
                        continue

            except subprocess.TimeoutExpired:
                logger.warning(f"Spawn timed out for {genome}, trying next CLI...")
                self._mark_cli_failed(cli)
                continue
            except Exception as e:
                logger.error(f"Error spawning {genome}: {e}")
                continue

        # All CLIs failed
        logger.error(f"All CLIs failed to spawn agent for task: {task[:50]}")
        post("DISPATCHER", f"FAILED: Could not spawn any agent for: {task[:100]}", topic="system")
        return False

    def create_linear_issue(self, title: str, description: str, labels: List[str] = None) -> bool:
        """Create a Linear issue via MCP."""
        try:
            logger.info(f"CREATING Linear issue: {title}")

            # Use claude CLI to create issue via Linear MCP
            prompt = f"""Create a Linear issue:
Title: {title}
Description: {description}
Labels: {', '.join(labels or ['stream:asset-engine', 'type:feature', 'phase:apps', 'product:kraliki'])}

Use linear_create_issue to create this."""

            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=60,
                cwd="/home/adminmatej/github"
            )

            if result.returncode == 0:
                logger.info(f"Created Linear issue: {title}")
                post("DISPATCHER", f"Created Linear issue: {title}", topic="system")
                return True
            else:
                logger.warning(f"Could not create issue: {result.stderr[:200]}")
                return False

        except Exception as e:
            logger.error(f"Error creating Linear issue: {e}")
            return False

    def escalate_to_human(self, task: str, reason: str, priority: str = "HIGH") -> bool:
        """Add to human-work-needed queue."""
        try:
            logger.info(f"ESCALATING to human: {reason[:50]}...")

            # Create human work item
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hw_id = f"HW-{timestamp}"

            item_file = HUMAN_QUEUE_DIR / f"{hw_id}_{reason[:30].replace(' ', '_')}.md"

            content = f"""# {hw_id}: {reason}

**Priority:** {priority}
**Created:** {datetime.now().isoformat()}
**Source:** Dispatcher auto-escalation

## Task
{task}

## Why Human Needed
{reason}

## Status
- [ ] Acknowledged
- [ ] In Progress
- [ ] Completed
"""

            item_file.write_text(content)
            logger.info(f"Created human work item: {hw_id}")

            # Update queue status
            self._update_human_queue_status(hw_id, reason, priority)

            post("DISPATCHER", f"Escalated to human: {hw_id} - {reason[:50]}", topic="system")
            return True

        except Exception as e:
            logger.error(f"Error escalating to human: {e}")
            return False

    def _update_human_queue_status(self, hw_id: str, reason: str, priority: str):
        """Update QUEUE_STATUS.md with new item."""
        try:
            status_file = HUMAN_QUEUE_DIR / "QUEUE_STATUS.md"

            new_entry = f"\n| {hw_id} | {reason[:40]} | {priority} | Pending | {datetime.now().strftime('%Y-%m-%d %H:%M')} |"

            if status_file.exists():
                content = status_file.read_text()
                # Insert after header row
                if "| ID |" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('|---'):
                            lines.insert(i + 1, new_entry.strip())
                            break
                    content = '\n'.join(lines)
                else:
                    content += new_entry
                status_file.write_text(content)
        except Exception as e:
            logger.warning(f"Could not update queue status: {e}")

    def route_to_agent(self, target: str, message: str, sender: str) -> bool:
        """Route message to specific agent by posting to their topic."""
        try:
            logger.info(f"ROUTING message from {sender} to {target}")

            post("DISPATCHER", f"[FROM {sender}] {message}", topic=f"agent-{target}")
            return True

        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return False

    # =========================================================================
    # DECISION LOGIC - Evaluate if action is needed
    # =========================================================================

    def evaluate_message(self, msg: dict) -> Tuple[Optional[str], dict]:
        """
        Evaluate a message and decide what action (if any) to take.

        Returns:
            (action_type, action_params) or (None, {}) if no action needed
        """
        content = msg.get('message', '')
        agent = msg.get('agent', 'unknown')

        # Skip messages from DISPATCHER itself (avoid loops)
        if agent == 'DISPATCHER':
            return None, {}

        # Check for direct mentions (@agent-name: message)
        if content.startswith('@'):
            match = re.match(r'@([\w-]+):\s*(.+)', content, re.DOTALL)
            if match:
                target, message = match.groups()
                return 'route', {
                    'target': target,
                    'message': message,
                    'sender': agent
                }

        # Check for action triggers (BLOCKED:, URGENT:, BUG:, etc.)
        for trigger, action in self.ACTION_TRIGGERS.items():
            if content.upper().startswith(f"{trigger}:") or content.upper().startswith(f"{trigger} "):
                payload = content[len(trigger):].strip().lstrip(':').strip()

                if action == 'escalate_human':
                    return 'escalate', {
                        'task': payload,
                        'reason': f"Agent {agent} reported: {trigger}",
                        'priority': 'CRITICAL' if trigger == 'BLOCKED' else 'HIGH'
                    }

                elif action == 'spawn_agent':
                    # Determine which role to spawn (CLI chosen at spawn time with fallback)
                    role = self._select_role_for_task(payload)
                    return 'spawn', {
                        'role': role,
                        'task': payload
                    }

                elif action == 'create_issue':
                    return 'issue', {
                        'title': payload[:100],
                        'description': f"Reported by {agent}:\n\n{payload}",
                        'labels': self._build_linear_labels(trigger, payload)
                    }

                elif action == 'spawn_helper':
                    return 'spawn', {
                        'role': 'explorer',
                        'task': f"Help {agent} with: {payload}"
                    }

                elif action == 'spawn_reviewer':
                    return 'spawn', {
                        'role': 'tester',
                        'task': f"Review for {agent}: {payload}"
                    }

        # Check for REQUEST: pattern
        if content.upper().startswith('REQUEST:'):
            request = content[8:].strip()
            request_id = f"{agent}_{hash(request) % 10000}"

            # Don't process same request twice
            if request_id in self.processed_requests:
                return None, {}

            self.processed_requests.add(request_id)

            # Evaluate if this needs agent spawn or just logging
            if any(kw in request.lower() for kw in ['implement', 'fix', 'build', 'create', 'add']):
                role = self._select_role_for_task(request)
                return 'spawn', {
                    'role': role,
                    'task': request
                }

        # Track CLAIMED/DONE for memory (passive, no action)
        if content.upper().startswith('CLAIMED'):
            task_id = content.split()[1] if len(content.split()) > 1 else 'unknown'
            memory_store(agent, "current_task", task_id)
            memory_store("DISPATCHER", f"task_{task_id}", json.dumps({
                'claimed_by': agent,
                'claimed_at': msg.get('time'),
                'status': 'in_progress'
            }))

        elif content.upper().startswith('DONE'):
            parts = content.split()
            task_id = parts[1] if len(parts) > 1 else 'unknown'

            # Award points if specified
            for part in parts:
                if part.startswith('+') and 'pt' in part.lower():
                    try:
                        points = int(part[1:].replace('pts', '').replace('pt', ''))
                        award_points(agent, points, f"Completed {task_id}")
                    except:
                        pass

            memory_store("DISPATCHER", f"task_{task_id}", json.dumps({
                'completed_by': agent,
                'completed_at': msg.get('time'),
                'status': 'done'
            }))

        elif content.upper().startswith('FINDING'):
            finding = content[7:].strip().lstrip(':').strip()
            memory_store(agent, f"finding_{datetime.now().strftime('%Y%m%d_%H%M%S')}", finding)
            award_points(agent, 5, "Shared finding")

        # No action needed
        return None, {}

    def _select_role_for_task(self, task: str) -> str:
        """Select appropriate role based on task content. CLI is chosen at spawn time."""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ['bug', 'fix', 'error', 'broken', 'crash']):
            return 'patcher'
        elif any(kw in task_lower for kw in ['test', 'verify', 'check', 'review']):
            return 'tester'
        elif any(kw in task_lower for kw in ['explore', 'find', 'search', 'where', 'how']):
            return 'explorer'
        elif any(kw in task_lower for kw in ['integrate', 'connect', 'api', 'webhook']):
            return 'integrator'
        elif any(kw in task_lower for kw in ['revenue', 'business', 'customer', 'sales']):
            return 'business'
        else:
            return 'builder'

    def _build_linear_labels(self, trigger: str, task: str) -> list[str]:
        """Build Linear labels aligned with stream/product/type/phase taxonomy."""
        task_lower = task.lower()
        labels: list[str] = []

        def add(label: str) -> None:
            if label and label not in labels:
                labels.append(label)

        stream_label = "stream:asset-engine"
        if any(kw in task_lower for kw in ["marketing", "sales", "outreach", "academy", "learn", "newsletter"]):
            stream_label = "stream:cash-engine"
        add(stream_label)

        if "marketing" in task_lower or "content" in task_lower or "linkedin" in task_lower:
            add("type:marketing")
        elif "sales" in task_lower or "lead" in task_lower or "customer" in task_lower:
            add("type:sales")
        elif trigger == "BUG":
            add("type:bug")
        elif trigger == "FEATURE":
            add("type:feature")

        product_map = {
            "focus": "product:focus",
            "voice": "product:voice",
            "speak": "product:speak",
            "learn": "product:learn",
            "academy": "product:learn",
            "lab": "product:lab",
            "sense": "product:sense",
            "telegram": "product:telegram-bots",
            "kraliki": "product:kraliki",
        }
        for keyword, label in product_map.items():
            if keyword in task_lower:
                add(label)

        phase_label = "phase:apps"
        if any(kw in task_lower for kw in ["agent", "orchestrator", "swarm"]):
            phase_label = "phase:agents"
        elif any(kw in task_lower for kw in ["infra", "monitor", "stability", "deploy", "incident", "uptime"]):
            phase_label = "phase:stability"
        elif "dashboard" in task_lower:
            phase_label = "phase:dashboard"
        elif any(kw in task_lower for kw in ["strategy", "alignment", "label"]):
            phase_label = "phase:alignment"
        add(phase_label)

        if not any(label.startswith("product:") for label in labels):
            add("product:kraliki")

        return labels

    def execute_action(self, action: str, params: dict) -> bool:
        """Execute the decided action."""
        if action == 'spawn':
            return self.spawn_agent(params['role'], params['task'])
        elif action == 'escalate':
            return self.escalate_to_human(params['task'], params['reason'], params.get('priority', 'HIGH'))
        elif action == 'issue':
            return self.create_linear_issue(params['title'], params['description'], params.get('labels'))
        elif action == 'route':
            return self.route_to_agent(params['target'], params['message'], params['sender'])
        else:
            logger.warning(f"Unknown action: {action}")
            return False

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    def process_message(self, msg: dict):
        """Process a single message - evaluate and act if needed."""
        action, params = self.evaluate_message(msg)

        if action:
            logger.info(f"ACTION DECIDED: {action} with params {params}")
            success = self.execute_action(action, params)
            if not success:
                logger.warning(f"Action {action} failed")
        # else: no action needed, stay silent

    def poll(self):
        """Poll blackboard for new messages."""
        try:
            messages = read(limit=50)
            new_messages = [m for m in messages if m.get('id', 0) > self.last_message_id]

            for msg in new_messages:
                self.process_message(msg)
                self.last_message_id = max(self.last_message_id, msg.get('id', 0))

            if new_messages:
                self._save_state()

        except Exception as e:
            logger.error(f"Error polling blackboard: {e}")

    def run(self, poll_interval: int = 5):
        """Run dispatcher continuously."""
        logger.info(f"Starting reactive dispatcher (poll interval: {poll_interval}s)")

        # Announce startup
        try:
            post("DISPATCHER", "Reactive dispatcher online. Monitoring and ready to act.", topic="system")
        except:
            pass

        while self.running:
            try:
                self.poll()
                time.sleep(poll_interval)
            except KeyboardInterrupt:
                logger.info("Dispatcher shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Dispatcher error: {e}")
                time.sleep(10)

        logger.info("Dispatcher stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Kraliki Reactive Dispatcher")
    parser.add_argument('-i', '--interval', type=int, default=5,
                       help="Poll interval in seconds (default: 5)")
    parser.add_argument('--once', action='store_true',
                       help="Run once and exit (for testing)")

    args = parser.parse_args()

    dispatcher = ReactiveDispatcher()

    if args.once:
        dispatcher.poll()
        print(f"Processed messages up to #{dispatcher.last_message_id}")
    else:
        dispatcher.run(poll_interval=args.interval)


if __name__ == "__main__":
    main()
