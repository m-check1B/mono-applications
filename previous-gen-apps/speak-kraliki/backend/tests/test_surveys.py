"""
Speak by Kraliki - Survey Tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.survey import Survey
from app.models.conversation import Conversation


@pytest.mark.asyncio
async def test_list_surveys(client: AsyncClient, test_survey, auth_headers):
    """Test listing surveys."""
    response = await client.get("/api/speak/surveys", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Monthly Check-in"


@pytest.mark.asyncio
async def test_create_survey(client: AsyncClient, auth_headers):
    """Test creating a survey."""
    response = await client.post(
        "/api/speak/surveys",
        headers=auth_headers,
        json={
            "name": "New Survey",
            "description": "Test survey description",
            "frequency": "weekly",
            "questions": [
                {"id": 1, "question": "How is your work-life balance?", "follow_up_count": 1},
                {"id": 2, "question": "Any feedback for management?", "follow_up_count": 2},
            ],
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Survey"
    assert data["status"] == "draft"
    assert len(data["questions"]) == 2


@pytest.mark.asyncio
async def test_get_survey(client: AsyncClient, test_survey, auth_headers):
    """Test getting a specific survey."""
    response = await client.get(
        f"/api/speak/surveys/{test_survey.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_survey.id)
    assert data["name"] == "Monthly Check-in"


@pytest.mark.asyncio
async def test_get_nonexistent_survey(client: AsyncClient, auth_headers):
    """Test getting a non-existent survey."""
    import uuid
    fake_id = uuid.uuid4()
    response = await client.get(
        f"/api/speak/surveys/{fake_id}",
        headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_survey(client: AsyncClient, test_survey, auth_headers):
    """Test updating a survey."""
    response = await client.patch(
        f"/api/speak/surveys/{test_survey.id}",
        headers=auth_headers,
        json={
            "name": "Updated Survey Name",
            "description": "Updated description",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Survey Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_launch_survey(
    client: AsyncClient,
    test_survey,
    test_employee,
    auth_headers,
    test_session: AsyncSession
):
    """Test launching a survey."""
    response = await client.post(
        f"/api/speak/surveys/{test_survey.id}/launch",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["invited_count"] == 1

    # Verify survey status changed
    result = await test_session.execute(
        select(Survey).where(Survey.id == test_survey.id)
    )
    survey = result.scalar_one()
    assert survey.status == "active"

    # Verify conversation was created
    conv_result = await test_session.execute(
        select(Conversation).where(Conversation.survey_id == test_survey.id)
    )
    conversations = conv_result.scalars().all()
    assert len(conversations) == 1
    assert conversations[0].status == "invited"


@pytest.mark.asyncio
async def test_launch_already_active_survey(
    client: AsyncClient,
    test_survey,
    test_employee,
    auth_headers,
    test_session: AsyncSession
):
    """Test launching an already active survey fails."""
    # First launch
    await client.post(
        f"/api/speak/surveys/{test_survey.id}/launch",
        headers=auth_headers
    )

    # Try to launch again
    response = await client.post(
        f"/api/speak/surveys/{test_survey.id}/launch",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "cannot be launched" in response.json()["detail"]


@pytest.mark.asyncio
async def test_pause_survey(
    client: AsyncClient,
    test_survey,
    test_employee,
    auth_headers,
    test_session: AsyncSession
):
    """Test pausing an active survey."""
    # First launch
    await client.post(
        f"/api/speak/surveys/{test_survey.id}/launch",
        headers=auth_headers
    )

    # Pause
    response = await client.post(
        f"/api/speak/surveys/{test_survey.id}/pause",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify status
    result = await test_session.execute(
        select(Survey).where(Survey.id == test_survey.id)
    )
    survey = result.scalar_one()
    assert survey.status == "paused"


@pytest.mark.asyncio
async def test_get_survey_stats(
    client: AsyncClient,
    test_survey,
    test_conversation,
    auth_headers
):
    """Test getting survey statistics."""
    response = await client.get(
        f"/api/speak/surveys/{test_survey.id}/stats",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_invited" in data
    assert "total_completed" in data
    assert "completion_rate" in data


@pytest.mark.asyncio
async def test_survey_unauthorized(client: AsyncClient, test_survey):
    """Test accessing surveys without auth."""
    response = await client.get("/api/speak/surveys")
    assert response.status_code == 401

    response = await client.get(f"/api/speak/surveys/{test_survey.id}")
    assert response.status_code == 401
