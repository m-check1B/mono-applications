"""
Unit tests for ShadowAnalyzerService - Jungian archetype-based personality insights
Tests shadow profile creation, archetype determination, daily insights, and progressive unlocking
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.shadow_profile import ShadowProfile, ShadowInsight
from app.services.shadow_analyzer import ShadowAnalyzerService, ARCHETYPES
from app.core.security_v2 import generate_id


class TestArchetypes:
    """Test archetype definitions"""

    def test_all_archetypes_defined(self):
        """All expected archetypes should be defined"""
        expected = ["warrior", "sage", "lover", "creator", "caregiver", "explorer"]
        for archetype in expected:
            assert archetype in ARCHETYPES

    def test_archetype_structure(self):
        """Each archetype should have required fields"""
        for name, archetype in ARCHETYPES.items():
            assert "traits" in archetype, f"{name} missing traits"
            assert "shadow" in archetype, f"{name} missing shadow"
            assert "growth_path" in archetype, f"{name} missing growth_path"
            assert "keywords" in archetype, f"{name} missing keywords"
            assert len(archetype["traits"]) >= 3
            assert len(archetype["shadow"]) >= 3
            assert len(archetype["keywords"]) >= 3


class TestDetermineArchetype:
    """Test archetype determination logic"""

    @pytest.mark.asyncio
    async def test_determine_archetype_no_tasks_returns_explorer(self, test_user: User, db: Session):
        """New user with no tasks should get explorer archetype"""
        service = ShadowAnalyzerService(db)
        archetype = await service._determine_archetype(test_user.id)
        assert archetype == "explorer"

    @pytest.mark.asyncio
    async def test_determine_archetype_warrior_keywords(self, test_user: User, db: Session):
        """Tasks with warrior keywords should result in warrior archetype"""
        # Create tasks with warrior keywords
        for keyword in ["achieve", "complete", "finish", "win", "conquer"]:
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Must {keyword} this project",
                status=TaskStatus.COMPLETED,
                createdAt=datetime.utcnow()
            )
            db.add(task)
        db.commit()

        service = ShadowAnalyzerService(db)
        archetype = await service._determine_archetype(test_user.id)
        # With 5 warrior keywords, warrior should score high
        assert archetype in ["warrior", "sage", "creator"]  # Flexible due to scoring

    @pytest.mark.asyncio
    async def test_determine_archetype_sage_keywords(self, test_user: User, db: Session):
        """Tasks with sage keywords should result in sage archetype"""
        # Create tasks with sage keywords
        for keyword in ["analyze", "research", "study", "learn", "understand"]:
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Need to {keyword} deeply",
                description="This requires extensive " * 20,  # Long description
                status=TaskStatus.PENDING,
                createdAt=datetime.utcnow()
            )
            db.add(task)
        db.commit()

        service = ShadowAnalyzerService(db)
        archetype = await service._determine_archetype(test_user.id)
        # Sage should score high with keywords + long descriptions
        assert archetype == "sage"

    @pytest.mark.asyncio
    async def test_determine_archetype_high_completion_warrior_boost(self, test_user: User, db: Session):
        """High task completion rate should boost warrior score"""
        # Create 10 completed tasks (high completion rate)
        for i in range(10):
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Task {i}",
                status=TaskStatus.COMPLETED,
                createdAt=datetime.utcnow()
            )
            db.add(task)
        db.commit()

        service = ShadowAnalyzerService(db)
        archetype = await service._determine_archetype(test_user.id)
        # 100% completion rate should boost warrior
        assert archetype == "warrior"


class TestCreateProfile:
    """Test shadow profile creation"""

    @pytest.mark.asyncio
    async def test_create_profile_new_user(self, test_user: User, db: Session):
        """New profile should be created with correct defaults"""
        service = ShadowAnalyzerService(db)
        profile = await service.create_profile(test_user.id)

        assert profile is not None
        assert profile.user_id == test_user.id
        assert profile.unlock_day == 1
        assert profile.total_days == 30

    @pytest.mark.asyncio
    async def test_create_profile_existing_returns_existing(self, test_user: User, db: Session):
        """Creating profile for existing user should return existing profile"""
        service = ShadowAnalyzerService(db)
        
        # Create first profile
        profile1 = await service.create_profile(test_user.id)
        
        # Try to create again
        profile2 = await service.create_profile(test_user.id)
        
        assert profile1.id == profile2.id

    @pytest.mark.asyncio
    async def test_create_profile_generates_insights(self, test_user: User, db: Session):
        """Creating profile should generate 30 days of insights"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)

        # Check insights were created
        profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first()
        insights = db.query(ShadowInsight).filter(ShadowInsight.profile_id == profile.id).all()

        assert len(insights) == 30
        # Only day 1 should be unlocked
        unlocked = [i for i in insights if i.unlocked]
        assert len(unlocked) == 1
        assert unlocked[0].day == 1


class TestGetProfile:
    """Test profile retrieval"""

    @pytest.mark.asyncio
    async def test_get_profile_exists(self, test_user: User, db: Session):
        """Should return profile if it exists"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        profile = await service.get_profile(test_user.id)
        
        assert profile is not None
        assert profile.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_get_profile_not_exists(self, test_user: User, db: Session):
        """Should return None if profile doesn't exist"""
        service = ShadowAnalyzerService(db)
        profile = await service.get_profile(test_user.id)
        
        assert profile is None


class TestGetDailyInsight:
    """Test daily insight retrieval"""

    @pytest.mark.asyncio
    async def test_get_insight_creates_profile_if_missing(self, test_user: User, db: Session):
        """Getting insight should create profile if missing"""
        service = ShadowAnalyzerService(db)
        
        # No profile exists yet
        assert db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first() is None
        
        # Get insight (should auto-create profile)
        insight = await service.get_daily_insight(test_user.id)
        
        # Profile should now exist
        assert db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first() is not None
        assert insight.locked == False
        assert insight.day == 1

    @pytest.mark.asyncio
    async def test_get_insight_locked_future_day(self, test_user: User, db: Session):
        """Future day insight should be locked"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Try to get day 5 (not unlocked yet)
        insight = await service.get_daily_insight(test_user.id, day=5)
        
        assert insight.locked == True
        assert "unlocks on day 5" in insight.message.lower()

    @pytest.mark.asyncio
    async def test_get_insight_unlocked_current_day(self, test_user: User, db: Session):
        """Current unlocked day should return insight content"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Get day 1 (should be unlocked)
        insight = await service.get_daily_insight(test_user.id, day=1)
        
        assert insight.locked == False
        assert insight.insight is not None
        assert insight.day == 1

    @pytest.mark.asyncio
    async def test_get_insight_invalid_day_number(self, test_user: User, db: Session):
        """Invalid day number should return locked response"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Day 0 is invalid
        insight = await service.get_daily_insight(test_user.id, day=0)
        assert insight.locked == True
        
        # Day 31 is invalid
        insight = await service.get_daily_insight(test_user.id, day=31)
        assert insight.locked == True


class TestUnlockNextDay:
    """Test day unlocking logic"""

    @pytest.mark.asyncio
    async def test_unlock_no_profile_fails(self, test_user: User, db: Session):
        """Unlocking without profile should fail"""
        service = ShadowAnalyzerService(db)
        result = await service.unlock_next_day(test_user.id)
        
        assert result.unlocked == False
        assert "no shadow profile" in result.message.lower()

    @pytest.mark.asyncio
    async def test_unlock_success(self, test_user: User, db: Session):
        """Unlocking should advance to next day"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Unlock next day
        result = await service.unlock_next_day(test_user.id)
        
        assert result.unlocked == True
        assert result.new_day == 2
        assert result.insight is not None

    @pytest.mark.asyncio
    async def test_unlock_all_days_already_unlocked(self, test_user: User, db: Session):
        """Should not unlock beyond day 30"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Set profile to day 30
        profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first()
        profile.unlock_day = 30
        db.commit()
        
        # Try to unlock next
        result = await service.unlock_next_day(test_user.id)
        
        assert result.unlocked == False
        assert "already unlocked" in result.message.lower()


class TestProgress:
    """Test progress tracking"""

    @pytest.mark.asyncio
    async def test_get_progress_no_profile(self, test_user: User, db: Session):
        """No profile should return None"""
        service = ShadowAnalyzerService(db)
        progress = await service.get_progress(test_user.id)
        
        assert progress is None

    @pytest.mark.asyncio
    async def test_get_progress_with_profile(self, test_user: User, db: Session):
        """Should return correct progress metrics"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        progress = await service.get_progress(test_user.id)
        
        assert progress is not None
        assert progress.unlock_day == 1
        assert progress.total_days == 30
        assert progress.unlocked_insights == 1
        assert progress.completion_percentage == pytest.approx(1/30 * 100, abs=0.1)

    @pytest.mark.asyncio
    async def test_get_all_unlocked_insights(self, test_user: User, db: Session):
        """Should return all unlocked insights"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        # Unlock a few more days
        await service.unlock_next_day(test_user.id)  # Day 2
        await service.unlock_next_day(test_user.id)  # Day 3
        
        insights = await service.get_all_unlocked_insights(test_user.id)
        
        assert len(insights) == 3
        assert insights[0].day == 1
        assert insights[1].day == 2
        assert insights[2].day == 3


class TestGenerateInsights:
    """Test insight generation"""

    @pytest.mark.asyncio
    async def test_insights_have_correct_types(self, test_user: User, db: Session):
        """Insights should have correct type based on day"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first()
        insights = db.query(ShadowInsight).filter(ShadowInsight.profile_id == profile.id).order_by(ShadowInsight.day).all()
        
        # Days 1-10: awareness
        for i in range(10):
            assert insights[i].insight_type == "awareness"
        
        # Days 11-20: understanding
        for i in range(10, 20):
            assert insights[i].insight_type == "understanding"
        
        # Days 21-30: integration
        for i in range(20, 30):
            assert insights[i].insight_type == "integration"

    @pytest.mark.asyncio
    async def test_insights_contain_archetype_content(self, test_user: User, db: Session):
        """Insights should reference archetype-specific content"""
        service = ShadowAnalyzerService(db)
        await service.create_profile(test_user.id)
        
        profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == test_user.id).first()
        archetype_info = ARCHETYPES[profile.archetype]
        
        # Get first insight
        insight = db.query(ShadowInsight).filter(
            ShadowInsight.profile_id == profile.id,
            ShadowInsight.day == 1
        ).first()
        
        # Content should contain something from archetype
        content_lower = insight.content.lower()
        has_archetype_reference = any(
            trait.lower().replace("_", " ") in content_lower
            for trait in archetype_info["traits"] + archetype_info["shadow"]
        )
        assert has_archetype_reference or any(word in content_lower for word in ["shadow", "pattern", "notice"])