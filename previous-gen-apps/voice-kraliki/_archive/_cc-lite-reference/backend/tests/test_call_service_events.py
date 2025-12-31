import pytest

from app.services.call_service import CallService
from app.schemas.call import CallCreate
from app.models.call import CallDirection
from app.core.config import settings


class DummySession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        return None

    async def refresh(self, _obj):
        return None


@pytest.mark.asyncio
async def test_create_call_publishes_event(monkeypatch):
    session = DummySession()
    service = CallService(session)

    call_data = CallCreate(
        from_number="+1234567890",
        to_number="+0987654321",
        direction=CallDirection.INBOUND,
        metadata={}
    )

    published = {}

    async def fake_publish_call_started(**kwargs):
        published.update(kwargs)

    monkeypatch.setattr(settings, "ENABLE_EVENTS", True)
    monkeypatch.setattr("app.core.events.event_publisher.publish_call_started", fake_publish_call_started)

    await service.create_call(call_data, organization_id="org-1", agent_id="agent-1")

    # Verify event was published with correct data
    assert "call_id" in published
    assert published["organization_id"] == "org-1"
    # Call ID is a UUID, just verify it's not empty
    assert len(published["call_id"]) > 0
