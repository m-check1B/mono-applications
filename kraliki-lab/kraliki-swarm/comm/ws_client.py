#!/usr/bin/env python3
"""
Kraliki WebSocket Client

Real-time messaging client for agents.
Maintains persistent connection for instant message delivery.

Usage:
  python3 ws_client.py <agent_id> [--type claude]
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Error: websockets not installed. Run: pip3 install websockets")
    sys.exit(1)

WS_URL = "ws://127.0.0.1:8200"


class KralikiClient:
    """WebSocket client for Kraliki communication."""

    def __init__(self, agent_id: str, agent_type: str = "claude"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.websocket = None
        self.connected = False
        self.message_handlers = []

    def on_message(self, handler):
        """Register a message handler callback."""
        self.message_handlers.append(handler)

    async def connect(self):
        """Connect to WebSocket hub."""
        try:
            self.websocket = await websockets.connect(WS_URL)
            self.connected = True

            # Register
            await self.websocket.send(json.dumps({
                "action": "register",
                "agent_id": self.agent_id,
                "type": self.agent_type
            }))

            # Wait for confirmation
            response = await self.websocket.recv()
            data = json.loads(response)

            if data.get("type") == "registered":
                print(f"✅ Connected as {self.agent_id}")
                print(f"   Other agents online: {data.get('connected_agents', [])}")
                return True
            else:
                print(f"❌ Registration failed: {data}")
                return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def send(self, to_agent: str, content: str):
        """Send message to specific agent."""
        if not self.connected:
            print("❌ Not connected")
            return False

        await self.websocket.send(json.dumps({
            "action": "send",
            "to": to_agent,
            "content": content
        }))

        response = await self.websocket.recv()
        data = json.loads(response)

        if data.get("type") == "sent":
            delivered = "✓" if data.get("delivered") else "queued"
            print(f"✉️  Message #{data['message_id']} to {to_agent} ({delivered})")
            return True
        return False

    async def broadcast(self, content: str):
        """Broadcast to all agents."""
        if not self.connected:
            print("❌ Not connected")
            return False

        await self.websocket.send(json.dumps({
            "action": "broadcast",
            "content": content
        }))

        response = await self.websocket.recv()
        data = json.loads(response)

        if data.get("type") == "broadcast_sent":
            print(f"📢 Broadcast #{data['message_id']} sent")
            return True
        return False

    async def list_agents(self):
        """List connected agents."""
        if not self.connected:
            print("❌ Not connected")
            return []

        await self.websocket.send(json.dumps({"action": "agents"}))
        response = await self.websocket.recv()
        data = json.loads(response)

        if data.get("type") == "agents":
            agents = data.get("connected", [])
            print(f"🤖 {len(agents)} agents online: {agents}")
            return agents
        return []

    async def listen(self):
        """Listen for incoming messages."""
        if not self.connected:
            return

        try:
            async for raw_message in self.websocket:
                try:
                    msg = json.loads(raw_message)
                    msg_type = msg.get("type")

                    if msg_type == "message":
                        ts = msg.get("timestamp", "")[:16]
                        print(f"\n📩 [{ts}] From {msg['from']}: {msg['content']}")

                    elif msg_type == "broadcast":
                        ts = msg.get("timestamp", "")[:16]
                        print(f"\n📢 [{ts}] Broadcast from {msg['from']}: {msg['content']}")

                    elif msg_type == "system":
                        print(f"\n🔔 System: {msg['content']}")

                    # Call registered handlers
                    for handler in self.message_handlers:
                        await handler(msg)

                except json.JSONDecodeError:
                    pass

        except websockets.exceptions.ConnectionClosed:
            print("\n⚠️  Connection closed")
            self.connected = False

    async def disconnect(self):
        """Disconnect from hub."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("👋 Disconnected")


async def interactive_mode(agent_id: str, agent_type: str):
    """Run interactive chat mode."""
    client = KralikiClient(agent_id, agent_type)

    if not await client.connect():
        return

    # Start listener in background
    listener_task = asyncio.create_task(client.listen())

    print("\nCommands:")
    print("  /send <agent> <message>  - Send to agent")
    print("  /broadcast <message>     - Send to all")
    print("  /agents                  - List online agents")
    print("  /quit                    - Disconnect")
    print()

    try:
        loop = asyncio.get_event_loop()
        while client.connected:
            # Read input in executor to not block
            try:
                line = await asyncio.wait_for(
                    loop.run_in_executor(None, input, f"[{agent_id}] > "),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                continue
            except EOFError:
                break

            if not line.strip():
                continue

            parts = line.strip().split(maxsplit=2)
            cmd = parts[0].lower()

            if cmd == "/quit":
                break
            elif cmd == "/agents":
                await client.list_agents()
            elif cmd == "/broadcast" and len(parts) > 1:
                await client.broadcast(" ".join(parts[1:]))
            elif cmd == "/send" and len(parts) > 2:
                await client.send(parts[1], parts[2])
            else:
                print("Unknown command. Use /send, /broadcast, /agents, or /quit")

    except KeyboardInterrupt:
        pass
    finally:
        listener_task.cancel()
        await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Kraliki WebSocket Client")
    parser.add_argument("agent_id", help="Your agent ID")
    parser.add_argument("--type", default="claude", help="Agent type")

    args = parser.parse_args()
    asyncio.run(interactive_mode(args.agent_id, args.type))


if __name__ == "__main__":
    main()
