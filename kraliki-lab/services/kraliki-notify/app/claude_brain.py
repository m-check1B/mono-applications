"""Claude AI Brain for Kraliki Telegram Bot.

Uses Claude CLI for intent parsing, executes Kraliki commands directly.
"""

import json
import logging
import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

KRALIKI_ROOT = Path("/home/adminmatej/github/applications/kraliki")
GITHUB_DIR = Path("/home/adminmatej/github")


class ClaudeBrain:
    """Claude-powered brain for the Telegram bot."""

    def __init__(self):
        self.claude_available = self._check_claude()

    def _check_claude(self) -> bool:
        """Check if claude CLI is available."""
        try:
            result = subprocess.run(
                ["which", "claude"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _parse_intent(self, message: str) -> Tuple[str, dict]:
        """Parse user message to determine intent and params.

        Returns: (command, params)
        """
        msg = message.lower().strip()

        # Status/health commands
        if any(x in msg for x in ["status", "health", "how are", "you ok"]):
            return "status", {}

        # Leaderboard
        if "leaderboard" in msg or "leader" in msg or "scores" in msg:
            return "leaderboard", {}

        # List agents
        if "agents" in msg and ("list" in msg or "running" in msg or "show" in msg or "what" in msg):
            return "list_agents", {}

        # List genomes
        if "genome" in msg and ("list" in msg or "available" in msg or "show" in msg):
            return "list_genomes", {}

        # Spawn agent
        spawn_match = re.search(r'spawn\s+(?:a\s+)?(\w+)', msg)
        if spawn_match or "spawn" in msg:
            genome = spawn_match.group(1) if spawn_match else "claude_builder"
            return "spawn_agent", {"genome": genome}

        # Kill agent
        kill_match = re.search(r'kill\s+(?:agent\s+)?(\d+)', msg)
        if kill_match:
            return "kill_agent", {"pid": int(kill_match.group(1))}

        # Read blackboard
        if "blackboard" in msg and ("read" in msg or "show" in msg or "what" in msg):
            return "blackboard_read", {}

        # PM2 status
        if "pm2" in msg and "status" in msg:
            return "pm2_status", {}

        # PM2 restart
        restart_match = re.search(r'restart\s+(\S+)', msg)
        if restart_match and "restart" in msg:
            return "pm2_restart", {"service": restart_match.group(1)}

        # Responses
        if "response" in msg:
            return "responses", {}

        # Default: dump to blackboard
        return "blackboard_post", {"message": message}

    async def execute_command(self, cmd: str, params: dict = None) -> str:
        """Execute a Kraliki command and return result."""
        params = params or {}
        logger.info(f"Executing: {cmd} with {params}")

        try:
            if cmd == "status":
                # Try PM2 first, fall back to simple health check
                try:
                    result = subprocess.run(
                        ["pm2", "jlist"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        online = sum(1 for p in data if p.get("pm2_env", {}).get("status") == "online")
                        return f"✅ System healthy\n📊 PM2: {online}/{len(data)} services online"
                except FileNotFoundError:
                    pass
                # Fallback: check if blackboard is accessible
                try:
                    result = subprocess.run(
                        ["python3", str(KRALIKI_ROOT / "arena" / "blackboard.py"), "read", "-l", "1"],
                        capture_output=True, text=True, timeout=10,
                        cwd=str(KRALIKI_ROOT)
                    )
                    if result.returncode == 0:
                        return "✅ System healthy\n📋 Blackboard accessible"
                except Exception:
                    pass
                return "⚠️ Status check unavailable"

            elif cmd == "list_agents":
                try:
                    result = subprocess.run(
                        ["pgrep", "-af", "(claude|opencode|gemini|codex)"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.stdout.strip():
                        lines = result.stdout.strip().split("\n")
                        agents = []
                        for line in lines[:10]:
                            if "pgrep" not in line:
                                agents.append(f"• {line[:80]}")
                        return f"🤖 *{len(agents)} agents running:*\n" + "\n".join(agents)
                    return "🤖 No agents currently running"
                except FileNotFoundError:
                    return "🤖 Agent listing unavailable (use dashboard at kraliki.verduona.dev)"

            elif cmd == "list_genomes":
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "agents" / "spawn.py"), "--list"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(KRALIKI_ROOT)
                )
                if result.stdout:
                    return f"🧬 *Available genomes:*\n{result.stdout[:1500]}"
                return "No genomes found"

            elif cmd == "spawn_agent":
                genome = params.get("genome", "claude_builder")
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "agents" / "spawn.py"), genome],
                    capture_output=True, text=True, timeout=60,
                    cwd=str(KRALIKI_ROOT)
                )
                output = result.stdout or result.stderr or "Spawn executed"
                return f"🚀 Spawning `{genome}`:\n{output[:500]}"

            elif cmd == "kill_agent":
                pid = params.get("pid")
                import os, signal
                try:
                    os.kill(pid, signal.SIGTERM)
                    return f"☠️ Sent SIGTERM to PID {pid}"
                except Exception as e:
                    return f"❌ Failed to kill {pid}: {e}"

            elif cmd == "blackboard_read":
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "arena" / "blackboard.py"), "read", "-l", "10"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(KRALIKI_ROOT)
                )
                if result.stdout:
                    return f"📋 *Recent blackboard:*\n{result.stdout[:2000]}"
                return "📋 Blackboard is empty"

            elif cmd == "blackboard_post":
                message = params.get("message", "")
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "arena" / "blackboard.py"),
                     "post", "CEO-HUMAN", f"📢 FROM TELEGRAM: {message}", "-t", "general"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(KRALIKI_ROOT)
                )
                return f"✅ Posted to blackboard"

            elif cmd == "leaderboard":
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "arena" / "game_engine.py"), "leaderboard"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(KRALIKI_ROOT)
                )
                if result.stdout:
                    return f"🏆 *Leaderboard:*\n{result.stdout[:1500]}"
                return "🏆 No leaderboard data yet"

            elif cmd == "pm2_status":
                try:
                    result = subprocess.run(
                        ["pm2", "jlist"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        lines = []
                        for p in data[:15]:
                            name = p.get("name", "?")
                            status = p.get("pm2_env", {}).get("status", "?")
                            emoji = "✅" if status == "online" else "❌"
                            lines.append(f"{emoji} {name}")
                        return f"📊 *PM2 Services:*\n" + "\n".join(lines)
                except FileNotFoundError:
                    pass
                return "📊 PM2 status unavailable (use dashboard at kraliki.verduona.dev)"

            elif cmd == "pm2_restart":
                service = params.get("service")
                try:
                    result = subprocess.run(
                        ["pm2", "restart", service],
                        capture_output=True, text=True, timeout=30
                    )
                    if result.returncode == 0:
                        return f"🔄 Restarted `{service}`"
                    return f"❌ Failed to restart: {result.stderr[:200]}"
                except FileNotFoundError:
                    return f"❌ PM2 restart unavailable (use dashboard at kraliki.verduona.dev)"

            elif cmd == "responses":
                # Check blackboard for CEO responses
                result = subprocess.run(
                    ["python3", str(KRALIKI_ROOT / "arena" / "blackboard.py"),
                     "search", "CEO", "-l", "10"],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(KRALIKI_ROOT)
                )
                if result.stdout:
                    return f"📨 *Recent responses:*\n{result.stdout[:2000]}"
                return "📨 No responses found"

            else:
                return f"Unknown command: {cmd}"

        except subprocess.TimeoutExpired:
            return f"⏱️ Command timed out"
        except Exception as e:
            logger.error(f"Command error: {e}")
            return f"❌ Error: {str(e)[:100]}"

    async def process_message(self, message: str, image_description: Optional[str] = None) -> str:
        """Process a user message."""

        # Add image context if present
        if image_description:
            message = f"[Image: {image_description}] {message}"

        # Parse intent
        cmd, params = self._parse_intent(message)
        logger.info(f"Intent: {cmd}, params: {params}")

        # Execute command
        result = await self.execute_command(cmd, params)

        return result

    async def describe_image(self, image_bytes: bytes, caption: Optional[str] = None) -> str:
        """Describe an image using Claude CLI."""
        if not self.claude_available:
            return "Image received (Claude unavailable)"

        import tempfile
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(image_bytes)
                temp_path = f.name

            prompt = "Describe this image in one sentence for a status update."
            if caption:
                prompt += f" Caption: {caption}"

            result = subprocess.run(
                ["claude", "-p", "--output-format", "text"],
                input=f"Describe the image at {temp_path} briefly.",
                capture_output=True, text=True, timeout=30,
                cwd=str(GITHUB_DIR)
            )

            Path(temp_path).unlink(missing_ok=True)
            return result.stdout.strip() or "Image received"

        except Exception as e:
            logger.error(f"Image error: {e}")
            return "Image received"


# Singleton
_brain: Optional[ClaudeBrain] = None


def get_brain() -> ClaudeBrain:
    """Get or create the Claude brain singleton."""
    global _brain
    if _brain is None:
        _brain = ClaudeBrain()
    return _brain
