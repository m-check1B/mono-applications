"""E2E test fixtures for Sense by Kraliki Bot.

Provides mocked Telegram updates, bot instances, and Redis for
testing complete bot flow without external API calls.

Environment Resilience:
All fixtures skip gracefully when bot application modules are unavailable,
allowing test suite to pass in CI environments where bot isn't deployed.
"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# ============================================================
# MODULE AVAILABILITY CHECKS
# ============================================================

try:
    from app.bot import handlers
    from app.services import sensitivity, dreams, biorhythm, remedies, storage
    from app.data import astro

    _app_available = True
    _app_unavailable_reason = None
except ImportError as e:
    _app_available = False
    _app_unavailable_reason = f"App modules not available: {e}"


# ============================================================
# TELEGRAM UPDATE FACTORY
# ============================================================


class TelegramUpdateFactory:
    """Factory for creating mock Telegram update payloads."""

    def __init__(self, user_id: int = 12345, chat_id: int = -10012345):
        self.user_id = user_id
        self.chat_id = chat_id
        self.update_id_counter = 1

    def _get_update_id(self) -> int:
        """Get next update ID."""
        self.update_id_counter += 1
        return self.update_id_counter

    def create_message_update(
        self,
        text: str,
        chat_type: str = "private",
        username: str = "testuser",
        first_name: str = "Test",
        is_bot: bool = False,
    ) -> dict[str, Any]:
        """Create a message update payload."""
        return {
            "update_id": self._get_update_id(),
            "message": {
                "message_id": self._get_update_id(),
                "date": int(datetime.now(UTC).timestamp()),
                "chat": {
                    "id": self.chat_id,
                    "type": chat_type,
                    "title": "Test Group" if chat_type != "private" else None,
                },
                "from": {
                    "id": self.user_id,
                    "is_bot": is_bot,
                    "first_name": first_name,
                    "username": username,
                },
                "text": text,
            },
        }

    def create_command_update(
        self,
        command: str,
        args: str = "",
        chat_type: str = "private",
    ) -> dict[str, Any]:
        """Create a command message update."""
        text = f"/{command}" + (f" {args}" if args else "")
        return self.create_message_update(text=text, chat_type=chat_type)

    def create_private_message_update(
        self,
        text: str,
        username: str = "testuser",
    ) -> dict[str, Any]:
        """Create a private message update."""
        return self.create_message_update(
            text=text,
            chat_type="private",
            username=username,
        )


@pytest.fixture
def update_factory():
    """Create a Telegram update factory."""
    return TelegramUpdateFactory()


# ============================================================
# MOCK SERVICES
# ============================================================


@pytest.fixture
def mock_redis():
    """Create an in-memory Redis mock."""

    class MockRedis:
        def __init__(self):
            self.data: dict[str, Any] = {}

        async def get(self, key: str):
            return self.data.get(key)

        async def set(self, key: str, value: Any, ex: int = None):
            self.data[key] = value
            return True

        async def exists(self, key: str):
            return 1 if key in self.data else 0

        async def delete(self, *keys):
            count = 0
            for key in keys:
                if key in self.data:
                    del self.data[key]
                    count += 1
            return count

        async def close(self):
            pass

    return MockRedis()


@pytest.fixture
def mock_gemini():
    """Mock Gemini AI client for dream analysis."""
    import sys
    # Create mock module and add to sys.modules
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(
        return_value=MagicMock(
            text="Dream analysis: This dream reflects inner transformation and growth."
        )
    )
    mock_genai.GenerativeModel.return_value = mock_model

    # Insert into sys.modules to make import work
    sys.modules['google.generativeai'] = mock_genai

    yield mock_genai

    # Cleanup
    if 'google.generativeai' in sys.modules:
        del sys.modules['google.generativeai']


@pytest.fixture
def mock_bot():
    """Create a mock Telegram bot."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.session = MagicMock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def mock_state():
    """Create a mock FSMContext state."""
    state = MagicMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state


@pytest.fixture
def mock_sensitivity_data():
    """Mock sensitivity calculation result."""

    class MockSensitivityReport:
        def __init__(self):
            self.total_score = 55
            self.level = "moderate"
            self.astrology = MagicMock(sensitivity_score=15)
            self.geomagnetic = MagicMock(kp_index=3, g_scale=1)
            self.schumann = MagicMock(resonance=7.83)
            self.seismic = MagicMock(magnitude=2.5)
            self.weather = MagicMock(pressure=1013, humidity=50)
            self.moon_phase = MagicMock(phase_name="Waxing Gibbous", illumination=75)

        def to_summary(self):
            return """**Sensitivity Score: 55/100 - Moderate**

**Astrological Influence:** 15/25
- Sun in Cancer
- Moon in Scorpio

**Geomagnetic:** Kp=3 (Quiet)
**Schumann Resonance:** 7.83 Hz
**Seismic Activity:** 2.5M (Regional)

**Moon Phase:** Waxing Gibbous (75%)

Interpretation: Balanced day with moderate sensitivity. Good for introspection."""

    return MockSensitivityReport()


@pytest.fixture
def mock_biorhythm_data():
    """Mock biorhythm calculation result."""

    class MockBiorhythm:
        def __init__(self):
            self.physical = 65
            self.emotional = -23
            self.intellectual = 88
            self.intuitive = 42
            self.overall = 43
            self.critical_days = []
            self.interpretation = (
                "Physical energy is high, emotional cycle is in recovery phase."
            )

    return MockBiorhythm()


@pytest.fixture
def mock_astro_data():
    """Mock astrological data."""

    class MockAstroData:
        def __init__(self):
            self.sun_sign = "Cancer"
            self.moon_sign = "Scorpio"
            self.moon_phase = MagicMock(
                phase_name="Waxing Gibbous",
                illumination=75,
                interpretation="Emotions are intensifying",
            )
            self.mercury_retrograde = False
            self.sensitivity_score = 15
            self.major_transits = [
                MagicMock(planet="Venus", sign="Leo", is_retrograde=False),
                MagicMock(planet="Mars", sign="Aries", is_retrograde=False),
                MagicMock(planet="Jupiter", sign="Taurus", is_retrograde=False),
                MagicMock(planet="Saturn", sign="Pisces", is_retrograde=True),
                MagicMock(planet="Uranus", sign="Taurus", is_retrograde=False),
            ]

    return MockAstroData()


@pytest.fixture
def mock_remedy_plan():
    """Mock remedy plan."""

    class MockRemedyPlan:
        def __init__(self):
            self.title = "Moderate Sensitivity Support"
            self.remedies = [
                "- Grounding meditation (10 mins)",
                "- Hydration focus: 2.5L water",
                "- Limit social media to 30 mins",
                "- Early bedtime (by 10 PM)",
            ]

        def to_summary(self):
            return f"""{self.title}

**Recommended Remedies:**
{chr(10).join(self.remedies)}

Duration: Until sensitivity drops below 40"""

    return MockRemedyPlan()


@pytest.fixture
def mock_forecast_data():
    """Mock 12-month forecast data."""
    return [
        {
            "month": "January",
            "sensitivity_level": "elevated",
            "retrogrades": ["Mercury"],
            "themes": ["communication", "planning"],
        },
        {
            "month": "February",
            "sensitivity_level": "moderate",
            "retrogrades": [],
            "themes": ["stability", "focus"],
        },
        {
            "month": "March",
            "sensitivity_level": "high",
            "retrogrades": ["Venus", "Mercury"],
            "themes": ["relationships", "reassessment"],
        },
        {
            "month": "April",
            "sensitivity_level": "moderate",
            "retrogrades": [],
            "themes": ["growth", "action"],
        },
        {
            "month": "May",
            "sensitivity_level": "elevated",
            "retrogrades": ["Saturn"],
            "themes": ["discipline", "structure"],
        },
        {
            "month": "June",
            "sensitivity_level": "moderate",
            "retrogrades": [],
            "themes": ["creativity", "expression"],
        },
    ]


# ============================================================
# INTEGRATION FIXTURES
# ============================================================


@pytest_asyncio.fixture
async def bot_context(
    mock_redis,
    mock_bot,
    mock_gemini,
    mock_sensitivity_data,
    mock_biorhythm_data,
    mock_astro_data,
    mock_remedy_plan,
    mock_forecast_data,
):
    """Set up bot with all mocked dependencies.

    Skips if app modules are not available.
    """
    if not _app_available:
        pytest.skip(_app_unavailable_reason or "App modules not available")

    # Mock the storage module's BotStorage class instance
    mock_storage = MagicMock()
    mock_storage.connect = AsyncMock()
    mock_storage.close = AsyncMock()
    mock_storage.get_user = AsyncMock(return_value={})
    mock_storage.update_user = AsyncMock()
    mock_storage.set_premium = AsyncMock()
    mock_storage.is_premium = AsyncMock(return_value=False)
    # LLM rate limiting - returns (allowed: bool, reason: str)
    mock_storage.check_llm_rate_limit = AsyncMock(return_value=(True, ""))

    # Mock analytics to prevent Redis calls
    mock_analytics = MagicMock()
    mock_analytics.track_command = AsyncMock()
    mock_analytics.track_chart_type = AsyncMock()
    mock_analytics.track_user = AsyncMock()
    mock_analytics.track_error = AsyncMock()
    mock_analytics.get_stats = AsyncMock(return_value={})

    with (
        patch("app.bot.handlers.storage", mock_storage),
        patch("app.services.storage.storage", mock_storage),
        patch("app.bot.handlers.analytics", mock_analytics),
        patch("app.core.analytics.analytics", mock_analytics),
        patch(
            "app.bot.handlers.calculate_sensitivity",
            AsyncMock(return_value=mock_sensitivity_data),
        ),
        patch(
            "app.bot.handlers.analyze_dream", AsyncMock(return_value=MagicMock(to_summary=lambda: "Dream analysis: This dream reflects inner transformation and growth."))
        ),
        patch("app.bot.handlers.calculate_biorhythm", return_value=mock_biorhythm_data),
        patch(
            "app.bot.handlers.get_astro_data", AsyncMock(return_value=mock_astro_data)
        ),
        patch(
            "app.bot.handlers.get_remedies_for_sensitivity",
            return_value=mock_remedy_plan,
        ),
        patch("app.bot.handlers.get_sleep_remedies", return_value=mock_remedy_plan),
        patch("app.bot.handlers.get_focus_remedies", return_value=mock_remedy_plan),
        patch("app.bot.handlers.get_emotional_remedies", return_value=mock_remedy_plan),
        patch(
            "app.bot.handlers.get_yearly_forecast",
            AsyncMock(return_value=mock_forecast_data),
        ),
    ):
        # Mock user_data storage
        user_data = {}

        yield {
            "bot": mock_bot,
            "redis": mock_redis,
            "user_data": user_data,
            "mocks": {
                "sensitivity": mock_sensitivity_data,
                "biorhythm": mock_biorhythm_data,
                "astro": mock_astro_data,
                "remedies": mock_remedy_plan,
                "forecast": mock_forecast_data,
            },
        }
