import pytest
from httpx import AsyncClient
from app.services import calendar_adapter


@pytest.mark.asyncio
async def test_calendar_status_disabled_by_default(async_client: AsyncClient, auth_headers: dict):
    resp = await async_client.get("/integration/calendar/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False


@pytest.mark.asyncio
async def test_calendar_event_creation_with_mock(async_client: AsyncClient, auth_headers: dict, monkeypatch):

    class DummyEvent:
        def __init__(self, id):
            self.id = id

    class DummyService:
        async def create_event(self, event):
            return DummyEvent("evt-1")

    def dummy_get_service():
        return DummyService()

    monkeypatch.setattr(calendar_adapter, "GoogleCalendarService", DummyService)
    monkeypatch.setattr(calendar_adapter, "CalendarEvent", type("CE", (), {"__init__": lambda self, **kw: None}))
    monkeypatch.setattr(calendar_adapter, "get_calendar_service", dummy_get_service)
    monkeypatch.setattr(calendar_adapter.settings, "ENABLE_CALENDAR_INTEGRATION", True)

    resp = await async_client.post("/integration/calendar/events", json={"title": "Test"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["event_id"] == "evt-1"
