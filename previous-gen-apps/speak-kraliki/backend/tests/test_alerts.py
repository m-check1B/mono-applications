"""
Speak by Kraliki - Alert Tests
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.alert import Alert


@pytest.mark.asyncio
async def test_list_alerts(client: AsyncClient, test_alert, auth_headers):
    """Test listing alerts."""
    response = await client.get("/api/speak/alerts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["type"] == "burnout"
    assert data[0]["severity"] == "high"


@pytest.mark.asyncio
async def test_list_alerts_with_filters(client: AsyncClient, test_alert, auth_headers):
    """Test listing alerts with filters."""
    response = await client.get(
        "/api/speak/alerts?severity=high&type=burnout&is_read=false",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["severity"] == "high"
    assert data[0]["type"] == "burnout"
    assert data[0]["is_read"] == False


@pytest.mark.asyncio
async def test_get_alert(client: AsyncClient, test_alert, auth_headers):
    """Test getting a specific alert."""
    response = await client.get(
        f"/api/speak/alerts/{test_alert.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_alert.id)
    assert data["type"] == "burnout"
    assert data["description"] == "Employee shows signs of burnout"


@pytest.mark.asyncio
async def test_get_nonexistent_alert(client: AsyncClient, auth_headers):
    """Test getting a non-existent alert."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/speak/alerts/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_alert_read_status(
    client: AsyncClient, test_alert, auth_headers, test_session: AsyncSession
):
    """Test updating alert read status."""
    response = await client.patch(
        f"/api/speak/alerts/{test_alert.id}",
        headers=auth_headers,
        json={"is_read": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] == True
    assert data["read_at"] is not None

    result = await test_session.execute(select(Alert).where(Alert.id == test_alert.id))
    alert = result.scalar_one()
    assert alert.is_read == True
    assert alert.read_at is not None


@pytest.mark.asyncio
async def test_update_alert_resolved_status(
    client: AsyncClient, test_alert, auth_headers, test_session: AsyncSession
):
    """Test updating alert resolved status."""
    response = await client.patch(
        f"/api/speak/alerts/{test_alert.id}",
        headers=auth_headers,
        json={"is_resolved": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_resolved"] == True
    assert data["resolved_at"] is not None

    result = await test_session.execute(select(Alert).where(Alert.id == test_alert.id))
    alert = result.scalar_one()
    assert alert.is_resolved == True
    assert alert.resolved_at is not None


@pytest.mark.asyncio
async def test_create_action_from_alert(client: AsyncClient, test_alert, auth_headers):
    """Test creating action from alert."""
    response = await client.post(
        f"/api/speak/alerts/{test_alert.id}/create-action", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "action_id" in data
    assert "message" in data
    assert "created from alert" in data["message"]


@pytest.mark.asyncio
async def test_create_action_from_nonexistent_alert(client: AsyncClient, auth_headers):
    """Test creating action from non-existent alert."""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/speak/alerts/{fake_id}/create-action", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_unread_count(client: AsyncClient, test_alert, auth_headers):
    """Test getting unread alerts count."""
    response = await client.get("/api/speak/alerts/unread-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] >= 1


@pytest.mark.asyncio
async def test_alert_unauthorized(client: AsyncClient, test_alert):
    """Test accessing alerts without auth."""
    response = await client.get("/api/speak/alerts")
    assert response.status_code == 401

    response = await client.get(f"/api/speak/alerts/{test_alert.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_alert_list_enriched_with_department_name(
    client: AsyncClient, test_alert, test_department, auth_headers
):
    """Test that alert list includes department name."""
    response = await client.get("/api/speak/alerts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["department_name"] == "Engineering"
