"""
Unit tests for Academy Router
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from app.models.user import User

@pytest.mark.unit
class TestAcademyRouter:
    """Test Academy Router API endpoints"""

    async def test_get_academy_status(self, async_client: AsyncClient):
        """Test getting academy status"""
        response = await async_client.get("/academy/status")
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True
        assert "Level 1" in data["current_launch"]

    async def test_join_waitlist_anonymous(self, async_client: AsyncClient):
        """Test joining waitlist without being logged in"""
        payload = {
            "email": "anon@example.com",
            "name": "Anonymous",
            "source": "website",
            "interest": "L1_STUDENT"
        }
        
        with patch("app.services.n8n_client.N8nClient.orchestrate_flow", return_value=True):
            response = await async_client.post("/academy/waitlist", json=payload)
            
            assert response.status_code == 200
            assert response.json()["success"] is True

    async def test_join_waitlist_authenticated(self, async_client: AsyncClient, auth_headers: dict, test_user: User, db):
        """Test joining waitlist while logged in"""
        payload = {
            "email": test_user.email,
            "name": test_user.firstName,
            "source": "dashboard",
            "interest": "L2_PRO"
        }
        
        with patch("app.services.n8n_client.N8nClient.orchestrate_flow", return_value=True):
            response = await async_client.post("/academy/waitlist", json=payload, headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            
            # Verify user status was updated in DB
            db.refresh(test_user)
            assert test_user.academyStatus == "WAITLIST"
            assert test_user.academyInterest == "L2_PRO"