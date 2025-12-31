import pytest
from httpx import AsyncClient
from app.services import calendar_adapter


@pytest.mark.asyncio
async def test_calendar_event_creation_disabled(async_client: AsyncClient, auth_headers: dict, monkeypatch):
    monkeypatch.setattr(calendar_adapter.settings, "ENABLE_CALENDAR_INTEGRATION", False)
    resp = await async_client.post("/integration/calendar/events", json={"title": "Test"}, headers=auth_headers)
    assert resp.status_code == 503