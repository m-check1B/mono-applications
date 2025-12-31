
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
from app.main import app
from app.models.employee import Employee
from app.core.database import get_db

@pytest.fixture
def expired_employee():
    employee = MagicMock(spec=Employee)
    employee.id = 1
    employee.first_name = "Test"
    employee.company_id = MagicMock()
    employee.magic_link_token = "expired-token"
    employee.magic_link_expires = datetime.now(timezone.utc) - timedelta(hours=1)
    return employee

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def setup_dependency_override(mock_session):
    async def override_get_db():
        yield mock_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield mock_session
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_start_conversation_expired_link(client: AsyncClient, expired_employee, setup_dependency_override):
    """Test that start-conversation rejects expired magic links."""
    mock_session = setup_dependency_override
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expired_employee
    mock_session.execute.return_value = mock_result
    
    response = await client.post("/api/speak/voice/start?token=expired-token")
    
    assert response.status_code == 410
    assert response.json()["detail"] == "Link has expired"

@pytest.mark.asyncio
async def test_redact_transcript_expired_link(client: AsyncClient, expired_employee, setup_dependency_override):
    """Test that redact-transcript rejects expired magic links."""
    mock_session = setup_dependency_override
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expired_employee
    mock_session.execute.return_value = mock_result
    
    response = await client.post(
        "/api/speak/employee/transcript/expired-token-2/redact",
        json={"turn_indices": [1, 2]}
    )
    
    assert response.status_code == 410
    assert response.json()["detail"] == "Link has expired"

@pytest.mark.asyncio
async def test_list_public_actions_expired_link(client: AsyncClient, expired_employee, setup_dependency_override):
    """Test that list-public-actions rejects expired magic links."""
    mock_session = setup_dependency_override
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expired_employee
    mock_session.execute.return_value = mock_result
    
    response = await client.get("/api/speak/actions/public?token=expired-token")
    
    assert response.status_code == 410
    assert response.json()["detail"] == "Link has expired"
