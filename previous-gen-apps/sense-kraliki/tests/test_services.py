"""Service tests for Sense by Kraliki Bot."""
import pytest
from datetime import date
from unittest.mock import AsyncMock, patch, MagicMock


class TestBiorhythmService:
    """Tests for biorhythm calculations."""

    def test_biorhythm_calculation(self):
        """Biorhythm should calculate cycles correctly."""
        from datetime import datetime as dt
        from app.services.biorhythm import calculate_biorhythm

        # Test with known date - use datetime, not date
        birth_date = dt(1990, 1, 1)
        target_date = dt(2024, 1, 1)

        result = calculate_biorhythm(birth_date, target_date)

        # Should return physical, emotional, intellectual values (as dataclass attributes)
        assert hasattr(result, "physical")
        assert hasattr(result, "emotional")
        assert hasattr(result, "intellectual")

    def test_biorhythm_values_in_range(self):
        """Biorhythm values should be between -100 and 100."""
        from datetime import datetime as dt
        from app.services.biorhythm import calculate_biorhythm

        birth_date = dt(1990, 6, 15)
        target_date = dt(2024, 6, 15)

        result = calculate_biorhythm(birth_date, target_date)

        # All values should be in valid range (-100 to 100 per the dataclass)
        assert -100 <= result.physical <= 100
        assert -100 <= result.emotional <= 100
        assert -100 <= result.intellectual <= 100


class TestSensitivityService:
    """Tests for sensitivity analysis."""

    def test_sensitivity_breakdown_dataclass(self):
        """SensitivityBreakdown should calculate total correctly."""
        from app.services.sensitivity import SensitivityBreakdown

        breakdown = SensitivityBreakdown(
            geomagnetic=10,
            solar_flares=5,
            earthquakes=3,
            schumann=8,
            weather=5,
            astrology=10,
            biorhythm=5
        )

        # Total should be sum of all components
        assert breakdown.total == 46


class TestDreamsService:
    """Tests for dream interpretation."""

    def test_dream_analysis_dataclass(self):
        """DreamAnalysis dataclass should store dream data."""
        from app.services.dreams import DreamAnalysis

        analysis = DreamAnalysis(
            dream_text="I was flying",
            symbols=[{"symbol": "flying", "meaning": "freedom", "archetype": "Self"}],
            archetypes=["Self"],
            themes=["freedom", "escape"],
            emotional_tone="positive",
            interpretation="A desire for freedom",
            personal_message="Embrace change",
            questions_to_consider=["What are you trying to escape?"]
        )

        assert analysis.dream_text == "I was flying"
        assert len(analysis.symbols) == 1
        assert "Self" in analysis.archetypes


class TestRemediesService:
    """Tests for remedy suggestions."""

    def test_remedy_dataclass(self):
        """Remedy dataclass should store remedy data."""
        from app.services.remedies import Remedy

        remedy = Remedy(
            category="aromatherapy",
            name="Lavender",
            description="Calming essential oil",
            how_to_use="Diffuse or apply topically"
        )

        assert remedy.category == "aromatherapy"
        assert remedy.name == "Lavender"
        assert remedy.caution is None

    def test_aromatherapy_database_exists(self):
        """AROMATHERAPY database should contain entries."""
        from app.services.remedies import AROMATHERAPY

        assert isinstance(AROMATHERAPY, dict)
        assert len(AROMATHERAPY) > 0


class TestLLMRateLimiting:
    """Tests for LLM rate limiting in storage service.

    Security: Prevents unbounded LLM API usage that could cause cost overruns.
    """

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis_mock = AsyncMock()
        redis_mock.incr = AsyncMock(return_value=1)
        redis_mock.expire = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        return redis_mock

    @pytest.fixture
    def storage_with_redis(self, mock_redis):
        """Create storage with mocked Redis."""
        from app.services.storage import BotStorage

        storage = BotStorage()
        storage.redis = mock_redis
        return storage

    @pytest.mark.asyncio
    async def test_rate_limit_allows_first_request(self, storage_with_redis, mock_redis):
        """First LLM request should be allowed."""
        # Mock is_premium to return False (free user)
        storage_with_redis.is_premium = AsyncMock(return_value=False)

        allowed, reason = await storage_with_redis.check_llm_rate_limit(12345)

        assert allowed is True
        assert reason == ""
        # Should have incremented counters
        assert mock_redis.incr.called

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_after_burst(self, storage_with_redis, mock_redis):
        """Should block requests after burst limit exceeded."""
        storage_with_redis.is_premium = AsyncMock(return_value=False)
        # Simulate 6th request in a minute (burst limit is 5)
        mock_redis.incr = AsyncMock(return_value=6)

        allowed, reason = await storage_with_redis.check_llm_rate_limit(12345)

        assert allowed is False
        assert "wait a minute" in reason.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_free_hourly_limit(self, storage_with_redis, mock_redis):
        """Free user should be blocked after hourly limit."""
        storage_with_redis.is_premium = AsyncMock(return_value=False)

        # First call to incr (minute) returns 1, second (hour) returns 4
        mock_redis.incr = AsyncMock(side_effect=[1, 4, 1])  # minute=1, hour=4, day=1

        allowed, reason = await storage_with_redis.check_llm_rate_limit(12345)

        assert allowed is False
        assert "3/hour" in reason  # Free limit is 3/hour
        assert "subscribe" in reason.lower()  # Should suggest upgrade

    @pytest.mark.asyncio
    async def test_rate_limit_premium_higher_limits(self, storage_with_redis, mock_redis):
        """Premium users should have higher limits."""
        storage_with_redis.is_premium = AsyncMock(return_value=True)

        # Premium can do 20/hour, so 10 should be allowed
        mock_redis.incr = AsyncMock(side_effect=[1, 10, 10])  # minute=1, hour=10, day=10

        allowed, reason = await storage_with_redis.check_llm_rate_limit(12345)

        assert allowed is True
        assert reason == ""

    @pytest.mark.asyncio
    async def test_rate_limit_free_daily_limit(self, storage_with_redis, mock_redis):
        """Free user should be blocked after daily limit."""
        storage_with_redis.is_premium = AsyncMock(return_value=False)

        # Free daily limit is 10
        mock_redis.incr = AsyncMock(side_effect=[1, 1, 11])  # minute=1, hour=1, day=11

        allowed, reason = await storage_with_redis.check_llm_rate_limit(12345)

        assert allowed is False
        assert "10/day" in reason
        assert "subscribe" in reason.lower()

    @pytest.mark.asyncio
    async def test_get_llm_usage_returns_counts(self, storage_with_redis, mock_redis):
        """get_llm_usage should return current usage stats."""
        storage_with_redis.is_premium = AsyncMock(return_value=False)
        mock_redis.get = AsyncMock(side_effect=["2", "5"])  # hour=2, day=5

        usage = await storage_with_redis.get_llm_usage(12345)

        assert usage["hourly"]["used"] == 2
        assert usage["hourly"]["limit"] == 3  # Free limit
        assert usage["daily"]["used"] == 5
        assert usage["daily"]["limit"] == 10  # Free limit
        assert usage["is_premium"] is False

    @pytest.mark.asyncio
    async def test_get_llm_usage_premium_limits(self, storage_with_redis, mock_redis):
        """Premium users should see higher limits."""
        storage_with_redis.is_premium = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(side_effect=["5", "20"])

        usage = await storage_with_redis.get_llm_usage(12345)

        assert usage["hourly"]["limit"] == 20  # Premium limit
        assert usage["daily"]["limit"] == 100  # Premium limit
        assert usage["is_premium"] is True
