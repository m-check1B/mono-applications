import asyncio
import pytest

from app.core.events import event_publisher


class DummyMemBus:
    def __init__(self):
        self.handlers = {}

    async def connect(self):
        return None

    async def publish(self, event_type: str, data: dict):
        h = self.handlers.get(event_type)
        if h:
            await h(event_type, data)

    async def subscribe(self, event_type: str, handler):
        self.handlers[event_type] = handler


@pytest.mark.asyncio
async def test_inmemory_events_subscribe_and_publish():
    event_publisher._mem_bus = DummyMemBus()
    event_publisher.is_connected = True

    received = []

    async def handler(event_type: str, data: dict):
        received.append((event_type, data))

    await event_publisher.subscribe("comms.call.started", handler)
    await event_publisher.publish(
        event_type="call.started",
        data={"call_id": "sub-1"},
        organization_id="org",
        user_id="user",
    )

    # Allow async handler to run
    await asyncio.sleep(0.01)

    assert any(ev[0] == "comms.call.started" and ev[1]["data"]["call_id"] == "sub-1" for ev in received)
