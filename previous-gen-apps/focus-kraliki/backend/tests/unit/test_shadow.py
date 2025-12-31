"""
Shadow Analysis Tests - AI Integration
Target Coverage: 70%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, AsyncMock

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.core.security_v2 import generate_id
from datetime import datetime, timedelta


class TestShadowAnalysis:
    """Test shadow analysis AI integration."""

    @pytest.mark.asyncio
    @patch("app.routers.shadow.anthropic_client")
    async def test_analyze_shadow_success(
        self,
        mock_anthropic,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test successful shadow analysis."""
        # Create test tasks
        tasks = [
            Task(
                id=generate_id(),
                title=f"Task {i}",
                description=f"Description {i}",
                userId=test_user.id,
                status=TaskStatus.PENDING if i % 2 == 0 else TaskStatus.COMPLETED,
                priority=i % 3,
                createdAt=datetime.utcnow() - timedelta(days=i)
            )
            for i in range(10)
        ]

        for task in tasks:
            db.add(task)
        db.commit()

        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"patterns": [{"pattern": "procrastination", "description": "Avoiding high-priority tasks", "frequency": 5, "severity": "high"}], "insights": ["You tend to procrastinate on important tasks"], "recommendations": ["Break tasks into smaller steps"], "shadowScore": 0.75}')]
        mock_anthropic.messages.create.return_value = mock_response

        response = await async_client.post(
            "/shadow/analyze",
            json={"taskPatterns": []},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "patterns" in data
        assert "insights" in data
        assert "recommendations" in data
        assert "shadowScore" in data

        assert len(data["patterns"]) > 0
        assert data["patterns"][0]["pattern"] == "procrastination"
        assert data["shadowScore"] == 0.75

        # Verify Claude was called
        mock_anthropic.messages.create.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.routers.shadow.anthropic_client")
    async def test_analyze_shadow_with_provided_patterns(
        self,
        mock_anthropic,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test shadow analysis with manually provided task patterns."""
        task_patterns = [
            {
                "title": "Important Task",
                "status": "PENDING",
                "priority": 5,
                "createdAt": datetime.utcnow().isoformat(),
                "tags": ["urgent"]
            }
        ]

        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"patterns": [], "insights": ["Test insight"], "recommendations": [], "shadowScore": 0.5}')]
        mock_anthropic.messages.create.return_value = mock_response

        response = await async_client.post(
            "/shadow/analyze",
            json={"taskPatterns": task_patterns},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "insights" in data
        assert len(data["insights"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_shadow_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that shadow analysis requires authentication."""
        response = await async_client.post(
            "/shadow/analyze",
            json={"taskPatterns": []}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("app.routers.shadow.anthropic_client")
    async def test_analyze_shadow_api_error(
        self,
        mock_anthropic,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test shadow analysis handles API errors gracefully."""
        # Mock API error
        mock_anthropic.messages.create.side_effect = Exception("API Error")

        response = await async_client.post(
            "/shadow/analyze",
            json={"taskPatterns": []},
            headers=auth_headers
        )

        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()


class TestShadowInsights:
    """Test shadow insights retrieval and unlock system."""

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_get_insights_empty(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting insights when none exist."""
        mock_db.get.return_value = []

        response = await async_client.get(
            "/shadow/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["insights"] == []
        assert data["total"] == 0
        assert data["currentDay"] == 0

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_get_insights_with_data(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting insights with unlocked data."""
        # Mock insights (3 unlocked, 2 locked)
        mock_insights = [
            {
                "id": generate_id(),
                "userId": test_user.id,
                "category": "shadow_pattern",
                "insight": f"Insight {i}",
                "dayUnlocked": i + 1,
                "acknowledged": False,
                "createdAt": (datetime.utcnow() - timedelta(days=10)).isoformat()
            }
            for i in range(5)
        ]

        mock_db.get.return_value = mock_insights

        response = await async_client.get(
            "/shadow/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Current day should be ~11 (10 days since first insight + 1)
        assert data["currentDay"] > 0
        assert data["total"] > 0
        assert len(data["insights"]) <= data["currentDay"]

    @pytest.mark.asyncio
    async def test_get_insights_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that getting insights requires authentication."""
        response = await async_client.get("/shadow/insights")

        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_acknowledge_insight_success(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test acknowledging an insight."""
        insight_id = generate_id()
        mock_insights = [
            {
                "id": insight_id,
                "userId": test_user.id,
                "category": "shadow_pattern",
                "insight": "Test insight",
                "dayUnlocked": 1,
                "acknowledged": False,
                "createdAt": datetime.utcnow().isoformat()
            }
        ]

        mock_db.get.return_value = mock_insights

        response = await async_client.post(
            f"/shadow/insights/{insight_id}/acknowledge",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "acknowledged" in data["message"].lower()

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_acknowledge_insight_not_found(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test acknowledging non-existent insight."""
        mock_db.get.return_value = []

        response = await async_client.post(
            "/shadow/insights/non-existent-id/acknowledge",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestUnlockSystem:
    """Test 30-day unlock system."""

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_unlock_status_no_insights(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test unlock status when no insights exist."""
        mock_db.get.return_value = []

        response = await async_client.get(
            "/shadow/unlock-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["currentDay"] == 0
        assert data["totalDays"] == 30
        assert data["unlockedInsights"] == 0
        assert data["nextUnlockDay"] == 1

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_unlock_status_with_insights(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test unlock status with existing insights."""
        # Create insights from 5 days ago
        mock_insights = [
            {
                "id": generate_id(),
                "userId": test_user.id,
                "category": "shadow_pattern",
                "insight": f"Insight {i}",
                "dayUnlocked": i + 1,
                "acknowledged": False,
                "createdAt": (datetime.utcnow() - timedelta(days=5)).isoformat()
            }
            for i in range(10)
        ]

        mock_db.get.return_value = mock_insights

        response = await async_client.get(
            "/shadow/unlock-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["currentDay"] == 6  # 5 days ago + 1
        assert data["totalDays"] == 30
        assert data["unlockedInsights"] == 6  # Days 1-6
        assert data["nextUnlockDay"] == 7

    @pytest.mark.asyncio
    @patch("app.routers.shadow.shadow_insights_db")
    async def test_unlock_status_max_30_days(
        self,
        mock_db,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test that unlock status caps at 30 days."""
        # Create insights from 35 days ago
        mock_insights = [
            {
                "id": generate_id(),
                "userId": test_user.id,
                "category": "shadow_pattern",
                "insight": f"Insight {i}",
                "dayUnlocked": i + 1,
                "acknowledged": False,
                "createdAt": (datetime.utcnow() - timedelta(days=35)).isoformat()
            }
            for i in range(5)
        ]

        mock_db.get.return_value = mock_insights

        response = await async_client.get(
            "/shadow/unlock-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["currentDay"] == 30  # Capped at 30
        assert data["nextUnlockDay"] == 30

    @pytest.mark.asyncio
    async def test_unlock_status_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that unlock status requires authentication."""
        response = await async_client.get("/shadow/unlock-status")

        assert response.status_code == 401


class TestShadowPatterns:
    """Test shadow pattern analysis."""

    @pytest.mark.asyncio
    @patch("app.routers.shadow.anthropic_client")
    async def test_analyze_identifies_patterns(
        self,
        mock_anthropic,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test that analysis identifies multiple patterns."""
        # Create varied task patterns
        tasks = []

        # Pattern 1: Procrastination (many pending high-priority)
        for i in range(5):
            tasks.append(Task(
                id=generate_id(),
                title=f"High Priority {i}",
                userId=test_user.id,
                status=TaskStatus.PENDING,
                priority=5,
                createdAt=datetime.utcnow() - timedelta(days=i+10)
            ))

        # Pattern 2: Low energy avoidance (avoiding certain energy levels)
        for i in range(3):
            from app.models.task import EnergyLevel
            tasks.append(Task(
                id=generate_id(),
                title=f"High Energy Task {i}",
                userId=test_user.id,
                status=TaskStatus.PENDING,
                priority=3,
                energyRequired=EnergyLevel.high,
                createdAt=datetime.utcnow() - timedelta(days=i+5)
            ))

        for task in tasks:
            db.add(task)
        db.commit()

        # Mock detailed pattern response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "patterns": [
                {
                    "pattern": "procrastination",
                    "description": "High-priority tasks remain incomplete",
                    "frequency": 5,
                    "severity": "high"
                },
                {
                    "pattern": "energy_avoidance",
                    "description": "Avoiding high-energy tasks",
                    "frequency": 3,
                    "severity": "medium"
                }
            ],
            "insights": [
                "You avoid tasks that require high energy",
                "High-priority items are consistently delayed"
            ],
            "recommendations": [
                "Schedule high-energy tasks for morning",
                "Break high-priority tasks into smaller chunks"
            ],
            "shadowScore": 0.68
        }''')]
        mock_anthropic.messages.create.return_value = mock_response

        response = await async_client.post(
            "/shadow/analyze",
            json={"taskPatterns": []},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["patterns"]) == 2
        assert len(data["insights"]) == 2
        assert len(data["recommendations"]) == 2

        # Verify pattern details
        pattern_names = [p["pattern"] for p in data["patterns"]]
        assert "procrastination" in pattern_names
        assert "energy_avoidance" in pattern_names
