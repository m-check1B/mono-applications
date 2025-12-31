#!/usr/bin/env python3
"""
Kraliki <-> platform-2026 events-core Bridge

Bidirectional integration between Kraliki agent messaging and
platform-2026's event bus (events-core).

This enables:
1. Kraliki agents to receive events from applications (Focus, Voice, Speak)
2. Applications to receive Kraliki agent messages/alerts as events
3. Unified observability across the entire Verduona ecosystem

Usage:
    # Start the bridge (standalone)
    python events_bridge.py

    # Or import and use programmatically
    from events_bridge import EventsBridge
    bridge = EventsBridge()
    await bridge.start()

Event Type Mappings:
    darwin.agent.*     -> Agent messages from Kraliki to applications
    darwin.task.*      -> Task lifecycle events
    darwin.alert.*     -> Critical alerts from Kraliki
    app.focus.*        -> Focus by Kraliki events to Kraliki
    app.voice.*        -> Voice by Kraliki events to Kraliki
    app.speak.*        -> Speak by Kraliki events to Kraliki
    app.learn.*        -> Learn by Kraliki events to Kraliki
    Legacy app.cclite.* and app.vop.* have been removed in favor of app.voice.* and app.speak.*
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple


# Add platform-2026 to path for events_core import
def _resolve_events_core_path() -> Path:
    env_root = os.getenv("GITHUB_DIR")
    candidates = []
    if env_root:
        candidates.append(
            Path(env_root) / "platform-2026" / "packages" / "events-core" / "src"
        )
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.append(parent / "platform-2026" / "packages" / "events-core" / "src")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return (
        candidates[0]
        if candidates
        else here / "platform-2026" / "packages" / "events-core" / "src"
    )


PLATFORM_2026 = _resolve_events_core_path()
sys.path.insert(0, str(PLATFORM_2026))

try:
    from events_core import create_event_bus, Event, EventPriority
    from events_core.event_bus import BaseEventBus

    EVENTS_CORE_AVAILABLE = True
except ImportError:
    EVENTS_CORE_AVAILABLE = False
    Event = None
    BaseEventBus = None

logger = logging.getLogger(__name__)

# Configuration
KRALIKI_COMM_URL = os.getenv("KRALIKI_COMM_URL", "http://127.0.0.1:8199")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", None)  # None = InMemory
BRIDGE_AGENT_ID = "events-bridge"
POLL_INTERVAL = 2.0  # seconds

# Event type patterns to bridge
DARWIN_TO_EVENTS = {
    "broadcast": "darwin.agent.broadcast",
    "message": "darwin.agent.message",
    "request": "darwin.agent.request",
    "response": "darwin.agent.response",
    "task_complete": "darwin.task.complete",
    "task_failed": "darwin.task.failed",
    "alert": "darwin.alert.general",
}

APP_EVENTS_TO_DARWIN = [
    "app.focus.*",  # Focus by Kraliki events
    "app.voice.*",  # Voice by Kraliki events
    "app.speak.*",  # Speak by Kraliki events
    "app.learn.*",  # Learn by Kraliki events
    "user.*",  # User lifecycle events
    "payment.*",  # Payment events (Stripe)
    "webhook.*",  # External webhook events
]

LEGACY_EVENT_ALIASES = {}


class KralikiCommClient:
    """Client for Kraliki communication hub."""

    def __init__(self, base_url: str = KRALIKI_COMM_URL):
        self.base_url = base_url
        self.last_message_id = 0
        self.consecutive_failures = 0
        self.last_error = None
        self.circuit_breaker_threshold = 10

    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Kraliki comm hub."""
        url = f"{self.base_url}{path}"

        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method=method,
            )
        else:
            req = urllib.request.Request(url, method=method)

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                self.consecutive_failures = 0
                self.last_error = None
                return result
        except urllib.error.URLError as e:
            error_msg = str(e)
            self.consecutive_failures += 1
            self.last_error = error_msg

            if self.consecutive_failures >= self.circuit_breaker_threshold:
                logger.error(
                    f"Circuit breaker: {self.consecutive_failures} consecutive failures. Last error: {error_msg}"
                )
            elif self.consecutive_failures % 5 == 1:
                logger.warning(
                    f"Kraliki comm request failed (attempt {self.consecutive_failures}): {error_msg}"
                )

            return {"error": error_msg}
        except Exception as e:
            error_msg = str(e)
            self.consecutive_failures += 1
            self.last_error = error_msg
            logger.error(f"Unexpected Kraliki comm error: {error_msg}")
            return {"error": error_msg}

    def register(self, agent_id: str = BRIDGE_AGENT_ID) -> bool:
        """Register bridge as an agent."""
        result = self._request(
            "POST",
            "/register",
            {
                "agent_id": agent_id,
                "type": "integration",
                "capabilities": ["events-bridge", "platform-2026", "pub-sub"],
            },
        )
        return result.get("success", False)

    def get_new_messages(self) -> list:
        """Get messages since last check."""
        result = self._request("GET", f"/messages?limit=100")
        messages = result.get("messages", [])

        # Filter to new messages only
        new_messages = [m for m in messages if m.get("id", 0) > self.last_message_id]

        if new_messages:
            self.last_message_id = max(m.get("id", 0) for m in new_messages)

        return new_messages

    def send_message(
        self, to: str, content: str, from_agent: str = BRIDGE_AGENT_ID
    ) -> bool:
        """Send message via Kraliki hub."""
        result = self._request(
            "POST",
            "/send",
            {"from": from_agent, "to": to, "content": content, "type": "event"},
        )
        return result.get("success", False)

    def broadcast(self, content: str, from_agent: str = BRIDGE_AGENT_ID) -> bool:
        """Broadcast to all Kraliki agents."""
        result = self._request(
            "POST", "/broadcast", {"from": from_agent, "content": content}
        )
        return result.get("success", False)

    def health_check(self) -> bool:
        """Check if Kraliki comm hub is healthy."""
        result = self._request("GET", "/health")
        return result.get("status") == "ok"


class EventsBridge:
    """Bidirectional bridge between Kraliki and events-core."""

    def __init__(
        self,
        darwin_url: str = KRALIKI_COMM_URL,
        rabbitmq_url: Optional[str] = RABBITMQ_URL,
    ):
        self.darwin = KralikiCommClient(darwin_url)
        self.rabbitmq_url = rabbitmq_url
        self.event_bus: Optional[BaseEventBus] = None
        self.running = False
        self._poll_task: Optional[asyncio.Task] = None
        self._processed_events: Set[str] = set()  # Prevent loops

    async def start(self) -> bool:
        """Start the bridge."""
        if not EVENTS_CORE_AVAILABLE:
            logger.error(
                "events-core not available. Install platform-2026/packages/events-core"
            )
            return False

        # Check Kraliki connectivity
        if not self.darwin.health_check():
            logger.warning("Kraliki comm hub not available. Starting anyway...")
        else:
            logger.info("Kraliki comm hub connected")

        # Register as agent
        self.darwin.register()

        # Create event bus
        self.event_bus = create_event_bus(amqp_url=self.rabbitmq_url)
        await self.event_bus.connect()
        logger.info(f"Event bus connected (RabbitMQ: {bool(self.rabbitmq_url)})")

        # Subscribe to application events
        for pattern in APP_EVENTS_TO_DARWIN:
            await self.event_bus.subscribe_typed(pattern, self._handle_app_event)
            logger.debug(f"Subscribed to: {pattern}")

        # Start polling Kraliki messages
        self.running = True
        self._poll_task = asyncio.create_task(self._poll_darwin_messages())

        logger.info("Events bridge started successfully")
        return True

    async def stop(self):
        """Stop the bridge."""
        self.running = False

        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

        if self.event_bus:
            await self.event_bus.close()

        logger.info("Events bridge stopped")

    async def _poll_darwin_messages(self):
        """Poll Kraliki for new messages and publish as events."""
        while self.running:
            try:
                if (
                    self.darwin.consecutive_failures
                    >= self.darwin.circuit_breaker_threshold
                ):
                    wait_time = min(
                        60, 2 ** min(int(self.darwin.consecutive_failures / 5), 6)
                    )
                    logger.warning(
                        f"Circuit breaker active. Waiting {wait_time}s before retry (failures: {self.darwin.consecutive_failures})"
                    )
                    await asyncio.sleep(wait_time)
                    continue

                messages = self.darwin.get_new_messages()

                if isinstance(messages, list):
                    for msg in messages:
                        await self._bridge_darwin_to_events(msg)

                await asyncio.sleep(POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Error polling Kraliki: {e}")
                await asyncio.sleep(POLL_INTERVAL)

    async def _bridge_darwin_to_events(self, message: Dict[str, Any]):
        """Convert Kraliki message to event and publish."""
        msg_id = message.get("id", "")
        event_key = f"darwin-{msg_id}"

        # Prevent loops - don't re-publish our own messages
        if event_key in self._processed_events:
            return
        self._processed_events.add(event_key)

        # Limit set size
        if len(self._processed_events) > 1000:
            self._processed_events = set(list(self._processed_events)[-500:])

        # Skip bridge's own messages
        if message.get("from") == BRIDGE_AGENT_ID:
            return

        # Determine event type
        msg_type = message.get("type", "message")
        event_type = DARWIN_TO_EVENTS.get(msg_type, f"darwin.agent.{msg_type}")

        # Add agent prefix if directed message
        to_agent = message.get("to", "all")
        if to_agent != "all":
            event_type = f"{event_type}.to.{to_agent}"

        # Create event
        event = Event(
            type=event_type,
            data={
                "darwin_message_id": msg_id,
                "from_agent": message.get("from"),
                "to_agent": to_agent,
                "content": message.get("content"),
                "original_type": msg_type,
                "darwin_timestamp": message.get("timestamp"),
            },
            source="kraliki-events-bridge",
            priority=EventPriority.HIGH
            if "alert" in msg_type
            else EventPriority.NORMAL,
            metadata={"bridged_at": datetime.now(timezone.utc).isoformat()},
        )

        # Publish to event bus
        result = await self.event_bus.publish_event(event)

        if result.published:
            logger.debug(f"Bridged Kraliki msg #{msg_id} -> {event_type}")
        else:
            logger.warning(f"Failed to bridge Kraliki msg #{msg_id}")

    async def _handle_app_event(self, event: Event):
        """Handle events from applications and forward to Kraliki."""
        event_key = f"app-{event.id}"

        # Prevent loops
        if event_key in self._processed_events:
            return
        self._processed_events.add(event_key)

        # Skip our own bridged events
        if event.source == "kraliki-events-bridge":
            return

        # Format message for Kraliki
        normalized_type, legacy_type = self._normalize_event_type(event.type)
        content = self._format_event_for_darwin(event, normalized_type, legacy_type)

        # Determine target
        target_agent = event.data.get("target_agent", "all")

        if target_agent == "all":
            success = self.darwin.broadcast(
                content, from_agent=f"events:{normalized_type}"
            )
        else:
            success = self.darwin.send_message(
                to=target_agent, content=content, from_agent=f"events:{normalized_type}"
            )

        if success:
            logger.debug(f"Bridged event {normalized_type} -> Kraliki")
        else:
            logger.warning(f"Failed to bridge event {normalized_type} to Kraliki")

    def _format_event_for_darwin(
        self,
        event: Event,
        event_type: Optional[str] = None,
        legacy_type: Optional[str] = None,
    ) -> str:
        """Format event-core event as Kraliki message content."""
        display_type = event_type or event.type
        parts = [
            f"[EVENT] {display_type}",
            f"Source: {event.source or 'unknown'}",
            f"Priority: {event.priority.value}",
        ]

        if legacy_type and legacy_type != display_type:
            parts.append(f"Legacy Type: {legacy_type}")

        # Add relevant data fields
        if event.data:
            data_preview = json.dumps(event.data, indent=2)[:500]
            parts.append(f"Data:\n{data_preview}")

        return "\n".join(parts)

    def _normalize_event_type(self, event_type: str) -> Tuple[str, Optional[str]]:
        """Normalize legacy app event types to canonical names."""
        for legacy_root, canonical_root in LEGACY_EVENT_ALIASES.items():
            if event_type == legacy_root:
                return canonical_root, event_type
            legacy_prefix = f"{legacy_root}."
            if event_type.startswith(legacy_prefix):
                suffix = event_type[len(legacy_prefix) :]
                return f"{canonical_root}.{suffix}", event_type

        return event_type, None


# Standalone runner
async def main():
    """Run the events bridge standalone."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    bridge = EventsBridge()

    if not await bridge.start():
        logger.error("Failed to start events bridge")
        sys.exit(1)

    logger.info("Events bridge running. Press Ctrl+C to stop.")

    # Setup signal handlers for graceful shutdown
    shutdown_requested = False

    def signal_handler():
        nonlocal shutdown_requested
        if not shutdown_requested:
            logger.info("Received shutdown signal. Gracefully stopping...")
            shutdown_requested = True

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        while not shutdown_requested:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("Poll task cancelled. Stopping...")
                shutdown_requested = True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        logger.info("Shutting down events bridge...")
        await bridge.stop()

    logger.info("Events bridge stopped gracefully")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
