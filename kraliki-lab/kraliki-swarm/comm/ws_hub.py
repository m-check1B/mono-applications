#!/usr/bin/env python3
"""
Kraliki WebSocket Communication Hub

Real-time agent messaging via WebSocket.
Runs alongside REST API for real-time updates.

Port: 8200 (WebSocket)
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import websockets
from websockets.server import serve
from utils import atomic_json_update, load_json_safe

KRALIKI_DIR = Path(__file__).parent.parent
DATA_DIR = KRALIKI_DIR / "comm" / "data"
MESSAGES_FILE = DATA_DIR / "messages.json"
AGENTS_FILE = DATA_DIR / "agents.json"

# Connected clients: {agent_id: websocket}
connected_clients = {}

# Message queue for broadcasting
message_queue = asyncio.Queue()


async def register_client(websocket, agent_id: str, agent_type: str = "unknown"):
    """Register a new WebSocket client."""
    connected_clients[agent_id] = websocket

    # Update agents registry
    def update_reg(agents):
        agents["agents"][agent_id] = {
            "type": agent_type,
            "last_seen": time.time(),
            "connected": True,
            "registered_at": agents.get("agents", {}).get(agent_id, {}).get(
                "registered_at", datetime.now().isoformat()
            )
        }
        return agents
    
    atomic_json_update(AGENTS_FILE, update_reg, {"agents": {}})

    print(f"[WS] {agent_id} connected ({len(connected_clients)} total)")

    # Notify others
    await broadcast_system(f"{agent_id} joined the swarm", exclude=agent_id)


async def unregister_client(agent_id: str):
    """Unregister a WebSocket client."""
    if agent_id in connected_clients:
        del connected_clients[agent_id]

        # Update agents registry
        def update_unreg(agents):
            if agent_id in agents.get("agents", {}):
                agents["agents"][agent_id]["connected"] = False
                agents["agents"][agent_id]["last_seen"] = time.time()
            return agents
            
        atomic_json_update(AGENTS_FILE, update_unreg, {"agents": {}})

        print(f"[WS] {agent_id} disconnected ({len(connected_clients)} remaining)")

        # Notify others
        await broadcast_system(f"{agent_id} left the swarm")


async def broadcast_system(message: str, exclude: str = None):
    """Send system message to all connected clients."""
    msg = {
        "type": "system",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    await broadcast(msg, exclude)


async def broadcast(message: dict, exclude: str = None):
    """Broadcast message to all connected clients."""
    if not connected_clients:
        return

    data = json.dumps(message)
    tasks = []
    for agent_id, ws in connected_clients.items():
        if agent_id != exclude:
            tasks.append(ws.send(data))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def send_to_agent(agent_id: str, message: dict):
    """Send message to specific agent."""
    if agent_id in connected_clients:
        try:
            await connected_clients[agent_id].send(json.dumps(message))
            return True
        except:
            return False
    return False


async def store_message(from_agent: str, to_agent: str, content: str, msg_type: str = "message"):
    """Store message in persistent storage."""
    
    def update_msgs(data):
        msg_id = data.get("next_id", 1)
        message = {
            "id": msg_id,
            "from": from_agent,
            "to": to_agent,
            "content": content,
            "type": msg_type,
            "timestamp": datetime.now().isoformat(),
            "read_by": []
        }

        data["messages"].append(message)
        data["next_id"] = msg_id + 1

        # Keep only last 1000 messages
        if len(data["messages"]) > 1000:
            data["messages"] = data["messages"][-1000:]
        return data

    data = atomic_json_update(MESSAGES_FILE, update_msgs, {"messages": [], "next_id": 1})
    return data["messages"][-1]


async def handle_client(websocket):
    """Handle WebSocket client connection."""
    agent_id = None

    try:
        # Wait for registration message
        async for raw_message in websocket:
            try:
                msg = json.loads(raw_message)
                action = msg.get("action")

                # Registration
                if action == "register":
                    agent_id = msg.get("agent_id", f"agent-{id(websocket)}")
                    agent_type = msg.get("type", "unknown")
                    await register_client(websocket, agent_id, agent_type)

                    # Send confirmation
                    await websocket.send(json.dumps({
                        "type": "registered",
                        "agent_id": agent_id,
                        "connected_agents": list(connected_clients.keys())
                    }))

                # Send direct message
                elif action == "send":
                    to_agent = msg.get("to")
                    content = msg.get("content", "")

                    # Store message
                    stored = await store_message(agent_id, to_agent, content, "message")

                    # Try to deliver in real-time
                    delivered = False
                    if to_agent == "all":
                        await broadcast({
                            "type": "message",
                            "from": agent_id,
                            "content": content,
                            "id": stored["id"],
                            "timestamp": stored["timestamp"]
                        }, exclude=agent_id)
                        delivered = True
                    else:
                        delivered = await send_to_agent(to_agent, {
                            "type": "message",
                            "from": agent_id,
                            "content": content,
                            "id": stored["id"],
                            "timestamp": stored["timestamp"]
                        })

                    # Confirm to sender
                    await websocket.send(json.dumps({
                        "type": "sent",
                        "message_id": stored["id"],
                        "delivered": delivered
                    }))

                # Broadcast
                elif action == "broadcast":
                    content = msg.get("content", "")

                    # Store
                    stored = await store_message(agent_id, "all", content, "broadcast")

                    # Broadcast to all
                    await broadcast({
                        "type": "broadcast",
                        "from": agent_id,
                        "content": content,
                        "id": stored["id"],
                        "timestamp": stored["timestamp"]
                    }, exclude=agent_id)

                    await websocket.send(json.dumps({
                        "type": "broadcast_sent",
                        "message_id": stored["id"]
                    }))

                # List connected agents
                elif action == "agents":
                    await websocket.send(json.dumps({
                        "type": "agents",
                        "connected": list(connected_clients.keys()),
                        "count": len(connected_clients)
                    }))

                # Ping/pong for keepalive
                elif action == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if agent_id:
            await unregister_client(agent_id)


async def main():
    """Run WebSocket server."""
    print("[WS] Kraliki WebSocket Hub starting on 127.0.0.1:8200")
    print("[WS] Protocol:")
    print("  → {action: 'register', agent_id: 'name', type: 'claude'}")
    print("  → {action: 'send', to: 'agent', content: 'message'}")
    print("  → {action: 'broadcast', content: 'message'}")
    print("  → {action: 'agents'}")
    print("  → {action: 'ping'}")

    async with serve(handle_client, "127.0.0.1", 8200):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
