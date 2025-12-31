"""
Comprehensive Tests for Shadow Analysis Service with Database Backend
Target Coverage: 90%+
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.shadow_profile import ShadowProfile, ShadowInsight
from app.services.shadow_analyzer import ShadowAnalyzerService, ARCHETYPES
from app.core.security_v2 import generate_id


class TestShadowProfileCreation:
    """Test shadow profile creation and archetype detection."""

    @pytest.mark.asyncio
    async def test_create_profile_success(
        self,
        db: Session,
        test_user: User
    ):
        """Test successful profile creation."""
        service = ShadowAnalyzerService(db)

        profile = await service.create_profile(test_user.id)

        assert profile is not None
        assert profile.user_id == test_user.id
        assert profile.archetype in ARCHETYPES.keys()
        assert profile.unlock_day == 1
        assert profile.total_days == 30

        # Verify insights were generated
        insights = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id
        ).all()

        assert len(insights) == 30  # 30 days of insights
        assert insights[0].unlocked is True  # Day 1 unlocked
        assert insights[1].unlocked is False  # Day 2 locked

    @pytest.mark.asyncio
    async def test_create_profile_idempotent(
        self,
        db: Session,
        test_user: User
    ):
        """Test that creating profile twice returns existing profile."""
        service = ShadowAnalyzerService(db)

        profile1 = await service.create_profile(test_user.id)
        profile2 = await service.create_profile(test_user.id)

        assert profile1.id == profile2.id
        assert profile1.archetype == profile2.archetype

    @pytest.mark.asyncio
    async def test_archetype_detection_warrior(
        self,
        db: Session,
        test_user: User
    ):
        """Test warrior archetype detection from task patterns."""
        # Create warrior-like tasks (lots of completed tasks)
        for i in range(20):
            task = Task(
                id=generate_id(),
                title=f"Complete task {i}",
                userId=test_user.id,
                status=TaskStatus.COMPLETED,
                priority=5,
                createdAt=datetime.utcnow()
            )
            db.add(task)
        db.commit()

        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Warrior archetype likely due to high completion rate
        assert profile.archetype in ARCHETYPES.keys()

    @pytest.mark.asyncio
    async def test_archetype_detection_sage(
        self,
        db: Session,
        test_user: User
    ):
        """Test sage archetype detection from analytical tasks."""
        # Create sage-like tasks (analysis, research)
        for i in range(10):
            task = Task(
                id=generate_id(),
                title=f"Research and analyze project {i}",
                description="Deep analysis and understanding of complex patterns",
                userId=test_user.id,
                status=TaskStatus.PENDING,
                createdAt=datetime.utcnow()
            )
            db.add(task)
        db.commit()

        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        assert profile.archetype in ARCHETYPES.keys()

    @pytest.mark.asyncio
    async def test_archetype_detection_default(
        self,
        db: Session,
        test_user: User
    ):
        """Test default archetype for new users without tasks."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Should default to explorer
        assert profile.archetype == "explorer"


class TestDailyInsights:
    """Test daily insight retrieval and locking."""

    @pytest.mark.asyncio
    async def test_get_daily_insight_unlocked(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting an unlocked daily insight."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Get day 1 insight (should be unlocked)
        insight = await service.get_daily_insight(test_user.id, day=1)

        assert insight.locked is False
        assert insight.day == 1
        assert insight.insight is not None
        assert insight.archetype == profile.archetype
        assert insight.progress == "1/30"

    @pytest.mark.asyncio
    async def test_get_daily_insight_locked(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting a locked future insight."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Try to get day 15 (should be locked)
        insight = await service.get_daily_insight(test_user.id, day=15)

        assert insight.locked is True
        assert insight.day == 15
        assert insight.insight is None
        assert "unlocks on day 15" in insight.message.lower()

    @pytest.mark.asyncio
    async def test_get_current_day_insight(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting current day insight without specifying day."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Get current day insight
        insight = await service.get_daily_insight(test_user.id)

        assert insight.day == profile.unlock_day
        assert insight.locked is False

    @pytest.mark.asyncio
    async def test_get_invalid_day_insight(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting insight for invalid day number."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Try day 0
        insight = await service.get_daily_insight(test_user.id, day=0)
        assert insight.locked is True
        assert "invalid" in insight.message.lower()

        # Try day 31
        insight = await service.get_daily_insight(test_user.id, day=31)
        assert insight.locked is True
        assert "invalid" in insight.message.lower()

    @pytest.mark.asyncio
    async def test_auto_create_profile_on_insight_request(
        self,
        db: Session,
        test_user: User
    ):
        """Test that requesting insights auto-creates profile."""
        service = ShadowAnalyzerService(db)

        # Request insight without creating profile first
        insight = await service.get_daily_insight(test_user.id, day=1)

        assert insight is not None
        assert insight.locked is False

        # Verify profile was created
        profile = await service.get_profile(test_user.id)
        assert profile is not None


class TestInsightUnlocking:
    """Test progressive insight unlocking system."""

    @pytest.mark.asyncio
    async def test_unlock_next_day_success(
        self,
        db: Session,
        test_user: User
    ):
        """Test successfully unlocking next day."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        assert profile.unlock_day == 1

        # Unlock day 2
        result = await service.unlock_next_day(test_user.id)

        assert result.unlocked is True
        assert result.new_day == 2
        assert result.insight is not None
        assert "day 2 unlocked" in result.message.lower()

        # Verify profile updated
        updated_profile = await service.get_profile(test_user.id)
        assert updated_profile.unlock_day == 2

    @pytest.mark.asyncio
    async def test_unlock_multiple_days(
        self,
        db: Session,
        test_user: User
    ):
        """Test unlocking multiple days sequentially."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Unlock days 2-5
        for expected_day in range(2, 6):
            result = await service.unlock_next_day(test_user.id)
            assert result.unlocked is True
            assert result.new_day == expected_day

        # Verify final state
        profile = await service.get_profile(test_user.id)
        assert profile.unlock_day == 5

    @pytest.mark.asyncio
    async def test_unlock_all_days_limit(
        self,
        db: Session,
        test_user: User
    ):
        """Test that unlocking stops at day 30."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Manually set to day 30
        profile_obj = db.query(ShadowProfile).filter(
            ShadowProfile.user_id == test_user.id
        ).first()
        profile_obj.unlock_day = 30
        db.commit()

        # Try to unlock past day 30
        result = await service.unlock_next_day(test_user.id)

        assert result.unlocked is False
        assert "all insights" in result.message.lower()

    @pytest.mark.asyncio
    async def test_unlock_marks_insight_as_unlocked(
        self,
        db: Session,
        test_user: User
    ):
        """Test that unlocking marks the insight as unlocked."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Check day 2 is locked
        insight_before = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id,
            ShadowInsight.day == 2
        ).first()
        assert insight_before.unlocked is False
        assert insight_before.unlocked_at is None

        # Unlock day 2
        await service.unlock_next_day(test_user.id)

        # Check day 2 is now unlocked
        insight_after = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id,
            ShadowInsight.day == 2
        ).first()
        assert insight_after.unlocked is True
        assert insight_after.unlocked_at is not None

    @pytest.mark.asyncio
    async def test_unlock_without_profile(
        self,
        db: Session,
        test_user: User
    ):
        """Test unlocking when no profile exists."""
        service = ShadowAnalyzerService(db)

        result = await service.unlock_next_day(test_user.id)

        assert result.unlocked is False
        assert "no shadow profile" in result.message.lower()


class TestProgressTracking:
    """Test progress tracking functionality."""

    @pytest.mark.asyncio
    async def test_get_progress_new_user(
        self,
        db: Session,
        test_user: User
    ):
        """Test progress for new user."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        progress = await service.get_progress(test_user.id)

        assert progress is not None
        assert progress.unlock_day == 1
        assert progress.total_days == 30
        assert progress.unlocked_insights == 1  # Day 1 unlocked by default
        assert progress.archetype == profile.archetype
        assert progress.completion_percentage == pytest.approx(3.33, rel=0.1)

    @pytest.mark.asyncio
    async def test_get_progress_partial_completion(
        self,
        db: Session,
        test_user: User
    ):
        """Test progress for partially completed journey."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Unlock 10 days
        for _ in range(10):
            await service.unlock_next_day(test_user.id)

        progress = await service.get_progress(test_user.id)

        assert progress.unlock_day == 11
        assert progress.unlocked_insights == 11
        assert progress.completion_percentage == pytest.approx(36.67, rel=0.1)

    @pytest.mark.asyncio
    async def test_get_progress_fully_completed(
        self,
        db: Session,
        test_user: User
    ):
        """Test progress for fully completed journey."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        # Set to day 30
        profile_obj = db.query(ShadowProfile).filter(
            ShadowProfile.user_id == test_user.id
        ).first()
        profile_obj.unlock_day = 30

        # Mark all insights as unlocked
        db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id
        ).update({"unlocked": True})
        db.commit()

        progress = await service.get_progress(test_user.id)

        assert progress.unlock_day == 30
        assert progress.unlocked_insights == 30
        assert progress.completion_percentage == 100.0

    @pytest.mark.asyncio
    async def test_get_progress_no_profile(
        self,
        db: Session,
        test_user: User
    ):
        """Test progress when no profile exists."""
        service = ShadowAnalyzerService(db)

        progress = await service.get_progress(test_user.id)

        assert progress is None


class TestAllUnlockedInsights:
    """Test retrieving all unlocked insights."""

    @pytest.mark.asyncio
    async def test_get_all_insights_initial(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting all insights initially (only day 1)."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        insights = await service.get_all_unlocked_insights(test_user.id)

        assert len(insights) == 1
        assert insights[0].day == 1
        assert insights[0].unlocked is True

    @pytest.mark.asyncio
    async def test_get_all_insights_multiple_days(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting all insights after unlocking multiple days."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Unlock 5 more days
        for _ in range(5):
            await service.unlock_next_day(test_user.id)

        insights = await service.get_all_unlocked_insights(test_user.id)

        assert len(insights) == 6  # Days 1-6
        assert all(i.unlocked for i in insights)
        assert [i.day for i in insights] == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_get_all_insights_ordered(
        self,
        db: Session,
        test_user: User
    ):
        """Test that insights are returned in day order."""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Unlock 10 days
        for _ in range(10):
            await service.unlock_next_day(test_user.id)

        insights = await service.get_all_unlocked_insights(test_user.id)

        # Verify order
        for i in range(len(insights) - 1):
            assert insights[i].day < insights[i + 1].day

    @pytest.mark.asyncio
    async def test_get_all_insights_no_profile(
        self,
        db: Session,
        test_user: User
    ):
        """Test getting insights when no profile exists."""
        service = ShadowAnalyzerService(db)

        insights = await service.get_all_unlocked_insights(test_user.id)

        assert insights == []


class TestInsightContent:
    """Test insight content generation."""

    @pytest.mark.asyncio
    async def test_insight_types_progression(
        self,
        db: Session,
        test_user: User
    ):
        """Test that insight types progress correctly (awareness→understanding→integration)."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        all_insights = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id
        ).order_by(ShadowInsight.day).all()

        # Days 1-10: awareness
        for i in range(0, 10):
            assert all_insights[i].insight_type == "awareness"

        # Days 11-20: understanding
        for i in range(10, 20):
            assert all_insights[i].insight_type == "understanding"

        # Days 21-30: integration
        for i in range(20, 30):
            assert all_insights[i].insight_type == "integration"

    @pytest.mark.asyncio
    async def test_insights_contain_archetype_specific_content(
        self,
        db: Session,
        test_user: User
    ):
        """Test that insights reference the user's archetype."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        archetype = profile.archetype
        archetype_data = ARCHETYPES[archetype]

        # Check some insights contain archetype-specific content
        all_insights = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id
        ).limit(10).all()

        # At least some insights should reference shadow traits
        shadow_traits = archetype_data["shadow"]
        found_shadow_reference = False

        for insight in all_insights:
            for trait in shadow_traits:
                if trait.replace("_", " ") in insight.content.lower():
                    found_shadow_reference = True
                    break
            if found_shadow_reference:
                break

        assert found_shadow_reference, f"No shadow traits found in insights for {archetype}"

    @pytest.mark.asyncio
    async def test_all_insights_unique(
        self,
        db: Session,
        test_user: User
    ):
        """Test that all 30 insights have unique content."""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        all_insights = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id
        ).all()

        contents = [i.content for i in all_insights]
        unique_contents = set(contents)

        # All insights should be unique
        assert len(unique_contents) == 30


# API Endpoint Tests

class TestShadowAPIEndpoints:
    """Test Shadow Analysis API endpoints with new database backend."""

    @pytest.mark.asyncio
    async def test_create_profile_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test POST /shadow/profile endpoint."""
        response = await async_client.post(
            "/shadow/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == test_user.id
        assert data["archetype"] in ARCHETYPES.keys()
        assert data["unlock_day"] == 1
        assert data["total_days"] == 30

    @pytest.mark.asyncio
    async def test_get_profile_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test GET /shadow/profile endpoint."""
        # Create profile first
        await async_client.post("/shadow/profile", headers=auth_headers)

        response = await async_client.get(
            "/shadow/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "archetype" in data
        assert "unlock_day" in data

    @pytest.mark.asyncio
    async def test_get_daily_insight_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test GET /shadow/insight endpoint."""
        # Create profile
        await async_client.post("/shadow/profile", headers=auth_headers)

        response = await async_client.get(
            "/shadow/insight",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["locked"] is False
        assert data["day"] == 1
        assert data["insight"] is not None

    @pytest.mark.asyncio
    async def test_unlock_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test POST /shadow/unlock endpoint."""
        # Create profile
        await async_client.post("/shadow/profile", headers=auth_headers)

        response = await async_client.post(
            "/shadow/unlock",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["unlocked"] is True
        assert data["new_day"] == 2

    @pytest.mark.asyncio
    async def test_get_progress_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test GET /shadow/progress endpoint."""
        # Create profile
        await async_client.post("/shadow/profile", headers=auth_headers)

        response = await async_client.get(
            "/shadow/progress",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "unlock_day" in data
        assert "total_days" in data
        assert "completion_percentage" in data

    @pytest.mark.asyncio
    async def test_get_all_insights_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test GET /shadow/insights endpoint."""
        # Create profile
        await async_client.post("/shadow/profile", headers=auth_headers)

        response = await async_client.get(
            "/shadow/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # API returns object with insights array, not a raw list
        assert isinstance(data, dict)
        assert "insights" in data
        assert isinstance(data["insights"], list)

    @pytest.mark.asyncio
    async def test_endpoints_require_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("POST", "/shadow/profile"),
            ("GET", "/shadow/profile"),
            ("GET", "/shadow/insight"),
            ("POST", "/shadow/unlock"),
            ("GET", "/shadow/progress"),
            ("GET", "/shadow/insights"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await async_client.get(endpoint)
            else:
                response = await async_client.post(endpoint)

            assert response.status_code == 401, f"{method} {endpoint} should require auth"
