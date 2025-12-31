import json
import logging
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import aiofiles

logger = logging.getLogger(__name__)

KRALIKI_ROOT = Path("/home/adminmatej/github/applications/kraliki")
GITHUB_ROOT = Path("/home/adminmatej/github")

# Add blackboard to path
sys.path.insert(0, str(KRALIKI_ROOT / "arena"))


async def get_health_status() -> str:
    """Get real system health from PM2, Docker, and key services."""
    try:
        # PM2 status
        result = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True,
            timeout=10
        )
        pm2_data = json.loads(result.stdout) if result.returncode == 0 else []
        pm2_online = sum(1 for x in pm2_data if x.get("pm2_env", {}).get("status") == "online")
        pm2_total = len(pm2_data)

        # Docker containers
        docker_result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        docker_lines = [l for l in docker_result.stdout.strip().split("\n") if l]
        docker_up = len(docker_lines)

        # Blackboard recent activity
        board_path = KRALIKI_ROOT / "arena" / "data" / "board.json"
        recent_msgs = 0
        if board_path.exists():
            async with aiofiles.open(board_path, 'r') as f:
                content = await f.read()
                board_data = json.loads(content)
                messages = board_data.get("messages", []) if isinstance(board_data, dict) else board_data
                cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
                for msg in messages[-100:]:  # Check last 100
                    try:
                        ts_str = msg.get("time", msg.get("timestamp", ""))
                        if ts_str:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=timezone.utc)
                            if ts > cutoff:
                                recent_msgs += 1
                    except:
                        pass

        # Build message
        pm2_icon = "✅" if pm2_online == pm2_total else "⚠️"

        msg = "🏥 *Kraliki System Status*\n\n"
        msg += f"{pm2_icon} *PM2:* {pm2_online}/{pm2_total} online\n"
        msg += f"🐳 *Docker:* {docker_up} containers up\n"
        msg += f"💬 *Blackboard:* {recent_msgs} msgs in last hour\n\n"

        # List PM2 services
        if pm2_data:
            msg += "*Services:*\n"
            for svc in pm2_data[:10]:
                name = svc.get("name", "?")
                status = svc.get("pm2_env", {}).get("status", "?")
                icon = "✅" if status == "online" else "❌"
                msg += f"{icon} {name}\n"
            if len(pm2_data) > 10:
                msg += f"...and {len(pm2_data) - 10} more\n"

        return msg

    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return f"⚠️ Error getting status: {e}"


async def get_morning_digest(hours: int = 24) -> str:
    """Generate comprehensive swarm activity digest."""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        # 1. Blackboard activity
        board_path = KRALIKI_ROOT / "arena" / "data" / "board.json"
        total_msgs = 0
        agents_active = set()
        claims = []
        completions = []

        if board_path.exists():
            async with aiofiles.open(board_path, 'r') as f:
                content = await f.read()
                board_data = json.loads(content)
                # Handle both list and dict formats
                messages = board_data.get("messages", []) if isinstance(board_data, dict) else board_data

                for msg in messages:
                    try:
                        # Support both "time" and "timestamp" keys
                        ts_str = msg.get("time", msg.get("timestamp", ""))
                        if not ts_str:
                            continue
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        # Make timezone-aware if naive
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts > cutoff:
                            total_msgs += 1
                            # Support both "agent" and "author" keys
                            author = msg.get("agent", msg.get("author", "unknown"))
                            agents_active.add(author.split("-")[0] if "-" in author else author)

                            text = msg.get("message", "").upper()
                            if "CLAIMING" in text or "CLAIM:" in text:
                                claims.append(msg)
                            if "DONE:" in text or "COMPLETED" in text or "+pts" in text.lower():
                                completions.append(msg)
                    except:
                        pass

        # 2. Leaderboard
        lb_path = KRALIKI_ROOT / "arena" / "data" / "leaderboard.json"
        total_points = 0
        top_agents = []

        if lb_path.exists():
            async with aiofiles.open(lb_path, 'r') as f:
                content = await f.read()
                lb_data = json.loads(content)

                # Support both "entries" and "rankings" keys
                entries = lb_data.get("rankings", lb_data.get("entries", []))
                sorted_entries = sorted(entries, key=lambda x: x.get("points", 0), reverse=True)
                top_agents = sorted_entries[:5]
                total_points = sum(e.get("points", 0) for e in entries)

        # 3. Git commits (quick check)
        commits_count = 0
        try:
            result = subprocess.run(
                ["git", "log", f"--since={hours} hours ago", "--oneline"],
                capture_output=True,
                text=True,
                cwd=str(GITHUB_ROOT / "applications" / "kraliki"),
                timeout=10
            )
            commits_count = len([l for l in result.stdout.strip().split("\n") if l])
        except:
            pass

        # 4. Sessions log (task completions)
        sessions_path = GITHUB_ROOT / "logs" / "sessions.jsonl"
        tasks_passed = 0
        tasks_failed = 0

        if sessions_path.exists():
            async with aiofiles.open(sessions_path, 'r') as f:
                async for line in f:
                    try:
                        entry = json.loads(line)
                        ts = datetime.fromisoformat(entry.get("timestamp", ""))
                        if ts.replace(tzinfo=timezone.utc) > cutoff:
                            result = entry.get("result", "")
                            if result in ("passed", "completed"):
                                tasks_passed += 1
                            elif result == "failed":
                                tasks_failed += 1
                    except:
                        pass

        # Build message
        msg = f"🌅 *Kraliki Swarm Report* (Last {hours}h)\n"
        msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        msg += "📊 *Activity Summary*\n"
        msg += f"├ 💬 Messages: {total_msgs}\n"
        msg += f"├ 🤖 Agents active: {len(agents_active)}\n"
        msg += f"├ 📋 Tasks claimed: {len(claims)}\n"
        msg += f"├ ✅ Completions: {len(completions)}\n"
        msg += f"└ 📝 Git commits: {commits_count}\n\n"

        msg += "🎮 *Session Results*\n"
        msg += f"├ ✅ Passed: {tasks_passed}\n"
        msg += f"└ ❌ Failed: {tasks_failed}\n\n"

        if top_agents:
            msg += "🏆 *Top Agents*\n"
            for i, agent in enumerate(top_agents):
                name = agent.get("name", "?")
                pts = agent.get("points", 0)
                msg += f"{i+1}. {name}: {pts} pts\n"
            msg += f"\n💰 Total points: {total_points}\n"

        # Recent highlights
        if completions:
            msg += "\n📢 *Recent Completions*\n"
            for comp in completions[-3:]:
                author = comp.get("author", "?")
                text = comp.get("message", "")[:80]
                msg += f"• {author}: {text}...\n"

        return msg

    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        return f"⚠️ Error generating digest: {e}"


async def post_to_blackboard(message: str) -> str:
    """Post a message to the Kraliki blackboard from CEO/Human.

    Posts to #general so all agents see it.

    Args:
        message: The message/command to post

    Returns:
        Confirmation message
    """
    try:
        import blackboard

        # Format message clearly for agents
        formatted = f"📢 HUMAN COMMAND:\n{message}"

        # Post to #general - where all agents read
        result = blackboard.post("CEO-HUMAN", formatted, topic="general")

        return f"✅ Posted to swarm blackboard\nID: #{result['id']}\n\nAgents will see this on #general"
    except Exception as e:
        logger.error(f"Error posting to blackboard: {e}")
        return f"❌ Failed to post: {e}"


async def create_task(title: str, description: str = "", priority: str = "HIGH") -> str:
    """Create a task announcement for the swarm.

    Args:
        title: Task title
        description: Task details
        priority: LOW, MEDIUM, HIGH, URGENT

    Returns:
        Confirmation message
    """
    try:
        import blackboard

        task_msg = f"🎯 NEW TASK FROM CEO [{priority}]\n\n"
        task_msg += f"**{title}**\n"
        if description:
            task_msg += f"\n{description}\n"
        task_msg += f"\n⏰ Posted: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        task_msg += "\n\n👉 Agents: CLAIM this task by posting 'CLAIMING: [task]'"

        # Post to both general and human-commands
        blackboard.post("CEO-HUMAN", task_msg, topic="general")
        result = blackboard.post("CEO-HUMAN", task_msg, topic="human-commands")

        return f"✅ Task created!\nID: {result['id']}\nPriority: {priority}\n\nSwarm notified on #general and #human-commands"
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return f"❌ Failed to create task: {e}"


async def get_recent_responses(limit: int = 5) -> str:
    """Get recent responses to human commands from agents."""
    try:
        import blackboard

        # Read recent messages mentioning CEO or human-commands topic
        messages = blackboard.read(topic="human-commands", limit=limit * 2)

        # Filter for agent responses (not CEO posts)
        responses = [m for m in messages if m.get("agent") != "CEO-HUMAN"][-limit:]

        if not responses:
            return "📭 No agent responses yet to your commands."

        msg = "📬 *Recent Agent Responses*\n\n"
        for r in responses:
            agent = r.get("agent", "?")
            text = r.get("message", "")[:100]
            time = r.get("time", "")[:16]
            msg += f"• [{time}] *{agent}*:\n  {text}...\n\n"

        return msg
    except Exception as e:
        logger.error(f"Error getting responses: {e}")
        return f"❌ Error: {e}"


async def get_agent_list() -> str:
    """Get current running agents."""
    try:
        result = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return "⚠️ Could not get PM2 status"

        pm2_data = json.loads(result.stdout)

        msg = "🤖 *Running Agents*\n\n"

        watchdogs = [s for s in pm2_data if "watchdog" in s.get("name", "").lower()]
        others = [s for s in pm2_data if "watchdog" not in s.get("name", "").lower()]

        if watchdogs:
            msg += "*Watchdogs:*\n"
            for w in watchdogs:
                name = w.get("name", "?")
                status = w.get("pm2_env", {}).get("status", "?")
                icon = "✅" if status == "online" else "❌"
                msg += f"{icon} {name}\n"
            msg += "\n"

        if others:
            msg += "*Services:*\n"
            for s in others:
                name = s.get("name", "?")
                status = s.get("pm2_env", {}).get("status", "?")
                icon = "✅" if status == "online" else "❌"
                msg += f"{icon} {name}\n"

        return msg

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return f"⚠️ Error: {e}"
