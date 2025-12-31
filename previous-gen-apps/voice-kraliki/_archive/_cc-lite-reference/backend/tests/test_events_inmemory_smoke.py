import asyncio
import pytest

from app.core.events import event_publisher


class DummyMemBus:
    def __init__(self):
        self.events = []

    async def connect(self):
        return None

    async def publish(self, event_type: str, data: dict):
        self.events.append((event_type, data))

    async def subscribe(self, event_type: str, handler):
        # no-op for this smoke
        return None


@pytest.mark.asyncio
async def test_inmemory_events_publish_smoke(monkeypatch):
    # Inject dummy in-memory bus directly
    event_publisher._mem_bus = DummyMemBus()
    event_publisher.is_connected = True

    await event_publisher.publish(
        event_type="call.started",
        data={"call_id": "test", "from_number": "+1", "to_number": "+1"},
        organization_id="org_test",
        user_id="user_test",
    )

    assert any(ev[0] == "comms.call.started" for ev in event_publisher._mem_bus.events)
