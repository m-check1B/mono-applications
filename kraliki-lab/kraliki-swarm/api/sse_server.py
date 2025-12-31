#!/usr/bin/env python3
"""SSE (Server-Sent Events) endpoint for real-time agent activity streaming.

From OpenCode research - enables real-time dashboard updates.

Usage:
    python3 sse_server.py  # Starts on 127.0.0.1:8098

Events:
    - agent_spawn: New agent started
    - agent_complete: Agent finished
    - agent_error: Agent failed
    - blackboard_post: New blackboard message
    - health_update: System health change
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Set, AsyncGenerator

# Check for optional dependencies
try:
    from aiohttp import web
    import aiohttp_sse
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    web = None
    aiohttp_sse = None

# Event queue for broadcasting
event_queues: Set[asyncio.Queue] = set()

# Kraliki paths
KRALIKI_DIR = Path(__file__).parent.parent
LOGS_DIR = KRALIKI_DIR / "logs"
BLACKBOARD_FILE = KRALIKI_DIR / "arena" / "blackboard.json"


async def broadcast_event(event_type: str, data: dict):
    """Broadcast event to all connected clients."""
    event = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    dead_queues = set()
    for queue in event_queues:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            dead_queues.add(queue)

    # Clean up dead queues
    for q in dead_queues:
        event_queues.discard(q)


async def sse_handler(request):
    """SSE endpoint handler."""
    queue = asyncio.Queue(maxsize=100)
    event_queues.add(queue)

    async with aiohttp_sse.sse_response(request) as resp:
        # Send initial connection event
        await resp.send(json.dumps({
            "type": "connected",
            "timestamp": datetime.now().isoformat(),
            "data": {"message": "SSE stream established"}
        }))

        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                await resp.send(json.dumps(event))
        except asyncio.TimeoutError:
            # Send keepalive
            await resp.send(json.dumps({
                "type": "keepalive",
                "timestamp": datetime.now().isoformat()
            }))
        except asyncio.CancelledError:
            pass
        finally:
            event_queues.discard(queue)

    return resp


async def health_handler(request):
    """Health check endpoint."""
    return web.json_response({
        "status": "ok",
        "connected_clients": len(event_queues),
        "timestamp": datetime.now().isoformat()
    })


async def post_event_handler(request):
    """HTTP endpoint to post events (for internal use)."""
    try:
        data = await request.json()
        event_type = data.get("type", "custom")
        event_data = data.get("data", {})

        await broadcast_event(event_type, event_data)

        return web.json_response({
            "status": "broadcasted",
            "clients": len(event_queues)
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


# File watcher for blackboard changes
async def watch_blackboard():
    """Watch blackboard file for changes and broadcast."""
    last_mtime = 0
    last_count = 0

    while True:
        try:
            if BLACKBOARD_FILE.exists():
                mtime = BLACKBOARD_FILE.stat().st_mtime
                if mtime > last_mtime:
                    last_mtime = mtime
                    with open(BLACKBOARD_FILE) as f:
                        messages = json.load(f)

                    # Broadcast new messages
                    if len(messages) > last_count:
                        for msg in messages[last_count:]:
                            await broadcast_event("blackboard_post", msg)
                        last_count = len(messages)
        except Exception as e:
            pass  # Ignore errors, keep watching

        await asyncio.sleep(2)  # Check every 2 seconds


# File watcher for agent logs
async def watch_agent_logs():
    """Watch for new agent log files."""
    seen_logs = set()

    agent_logs_dir = LOGS_DIR / "agents"
    agent_logs_dir.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            current_logs = set(f.name for f in agent_logs_dir.glob("*.log"))
            new_logs = current_logs - seen_logs

            for log_name in new_logs:
                # Extract agent_id from filename
                agent_id = log_name.replace(".log", "")
                await broadcast_event("agent_spawn", {
                    "agent_id": agent_id,
                    "log_file": str(agent_logs_dir / log_name)
                })

            seen_logs = current_logs
        except Exception as e:
            pass

        await asyncio.sleep(5)


async def start_watchers(app):
    """Start background file watchers."""
    app['blackboard_watcher'] = asyncio.create_task(watch_blackboard())
    app['agent_watcher'] = asyncio.create_task(watch_agent_logs())


async def stop_watchers(app):
    """Stop background file watchers."""
    app['blackboard_watcher'].cancel()
    app['agent_watcher'].cancel()


def create_app():
    """Create the aiohttp application."""
    app = web.Application()

    # Routes
    app.router.add_get('/events', sse_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_post('/event', post_event_handler)

    # Start/stop hooks
    app.on_startup.append(start_watchers)
    app.on_cleanup.append(stop_watchers)

    return app


# Standalone event posting function (for use by other modules)
def post_event_sync(event_type: str, data: dict, host: str = "127.0.0.1", port: int = 8098):
    """Synchronously post an event to the SSE server."""
    import requests
    try:
        requests.post(
            f"http://{host}:{port}/event",
            json={"type": event_type, "data": data},
            timeout=1
        )
    except Exception:
        pass  # Best effort


if __name__ == "__main__":
    import sys

    if not AIOHTTP_AVAILABLE:
        print("ERROR: SSE server requires aiohttp and aiohttp-sse")
        print("Install with: pip install aiohttp aiohttp-sse")
        sys.exit(1)

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8098

    print(f"Starting SSE server on 127.0.0.1:{port}")
    print(f"  Events endpoint: http://127.0.0.1:{port}/events")
    print(f"  Health endpoint: http://127.0.0.1:{port}/health")
    print(f"  Post endpoint:   http://127.0.0.1:{port}/event")

    app = create_app()
    web.run_app(app, host="127.0.0.1", port=port)
