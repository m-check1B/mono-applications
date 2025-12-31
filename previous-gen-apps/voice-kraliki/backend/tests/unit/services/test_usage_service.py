"""
Tests for Usage Service - SaaS metering and limits.

Tests cover:
- Recording usage (voice minutes)
- Getting monthly usage totals
- Checking plan limits
- Getting usage statistics
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, PropertyMock
from uuid import uuid4

from app.services.usage_service import (
    UsageService,
    PLAN_LIMITS,
    PLAN_LIMITS_CCLITE,
    PLAN_LIMITS_VOP,
)


@pytest.fixture
def usage_service():
    """Create a UsageService instance."""
    return UsageService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_user_starter():
    """Create a mock starter plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = False
    user.preferences = {"subscription": {"product": "cc_lite", "plan": "starter"}}
    return user


@pytest.fixture
def mock_user_professional():
    """Create a mock professional plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = True
    user.preferences = {"subscription": {"product": "cc_lite", "plan": "professional"}}
    return user


@pytest.fixture
def mock_user_enterprise():
    """Create a mock enterprise plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = True
    user.preferences = {"subscription": {"product": "cc_lite", "plan": "enterprise"}}
    return user


@pytest.fixture
def mock_vop_personal():
    """Create a mock Voice of People personal plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = False
    user.preferences = {"subscription": {"product": "vop", "plan": "personal"}}
    return user


@pytest.fixture
def mock_vop_premium():
    """Create a mock Voice of People premium plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = True
    user.preferences = {"subscription": {"product": "vop", "plan": "premium"}}
    return user


@pytest.fixture
def mock_vop_pro():
    """Create a mock Voice of People pro plan user."""
    user = MagicMock()
    user.id = str(uuid4())
    user.is_premium = True
    user.preferences = {"subscription": {"product": "vop", "plan": "pro"}}
    return user


class TestPlanLimits:
    """Tests for plan limit configuration."""

    def test_starter_limit_is_1000_minutes(self):
        """Test that starter plan has 1000 minute limit."""
        assert PLAN_LIMITS["starter"] == 1000

    def test_professional_limit_is_3000_minutes(self):
        """Test that professional plan has 3000 minute limit."""
        assert PLAN_LIMITS["professional"] == 3000

    def test_enterprise_limit_is_10000_minutes(self):
        """Test that enterprise plan has 10000 minute limit."""
        assert PLAN_LIMITS["enterprise"] == 10000

    def test_all_plans_defined(self):
        """Test that all expected plans are defined."""
        expected_plans_cc_lite = ["starter", "professional", "enterprise"]
        expected_plans_vop = ["personal", "premium", "pro"]
        for plan in expected_plans_cc_lite:
            assert plan in PLAN_LIMITS_CCLITE
        for plan in expected_plans_vop:
            assert plan in PLAN_LIMITS_VOP

    def test_vop_personal_limit_is_100_minutes(self):
        """Test that Voice of People personal plan has 100 minute limit."""
        assert PLAN_LIMITS_VOP["personal"] == 100

    def test_vop_premium_limit_is_500_minutes(self):
        """Test that Voice of People premium plan has 500 minute limit."""
        assert PLAN_LIMITS_VOP["premium"] == 500

    def test_vop_pro_limit_is_2000_minutes(self):
        """Test that Voice of People pro plan has 2000 minute limit."""
        assert PLAN_LIMITS_VOP["pro"] == 2000


class TestRecordUsage:
    """Tests for recording usage."""

    def test_record_usage_creates_record(self, usage_service, mock_db):
        """Test that record_usage creates a new usage record."""
        user_id = "123"
        quantity = 300  # 5 minutes in seconds

        result = usage_service.record_usage(
            mock_db, user_id=user_id, quantity=quantity, service_type="voice_minutes"
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_record_usage_with_reference_id(self, usage_service, mock_db):
        """Test recording usage with a reference ID."""
        user_id = "123"
        quantity = 600
        reference_id = "call_12345"

        usage_service.record_usage(
            mock_db,
            user_id=user_id,
            quantity=quantity,
            service_type="voice_minutes",
            reference_id=reference_id,
        )

        mock_db.add.assert_called_once()
        added_record = mock_db.add.call_args[0][0]
        assert added_record.reference_id == reference_id

    def test_record_usage_default_service_type(self, usage_service, mock_db):
        """Test that default service type is voice_minutes."""
        user_id = "123"
        quantity = 120

        usage_service.record_usage(mock_db, user_id=user_id, quantity=quantity)

        added_record = mock_db.add.call_args[0][0]
        assert added_record.service_type == "voice_minutes"


class TestGetMonthlyUsage:
    """Tests for getting monthly usage totals."""

    def test_get_monthly_usage_returns_sum(self, usage_service, mock_db):
        """Test that monthly usage returns total seconds."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 6000  # 100 minutes in seconds
        mock_db.execute.return_value = mock_result

        result = usage_service.get_monthly_usage(mock_db, user_id=123)

        assert result == 6000
        mock_db.execute.assert_called_once()

    def test_get_monthly_usage_returns_zero_when_none(self, usage_service, mock_db):
        """Test that monthly usage returns 0 when no records."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_db.execute.return_value = mock_result

        result = usage_service.get_monthly_usage(mock_db, user_id=123)

        assert result == 0

    def test_get_monthly_usage_filters_by_service_type(self, usage_service, mock_db):
        """Test that monthly usage filters by service type."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1000
        mock_db.execute.return_value = mock_result

        result = usage_service.get_monthly_usage(mock_db, user_id=123, service_type="tokens")

        assert result == 1000


class TestCheckLimit:
    """Tests for checking plan limits."""

    def test_check_limit_starter_under_limit(self, usage_service, mock_db, mock_user_starter):
        """Test starter user under limit returns True."""
        # Setup: User has used 500 minutes (30000 seconds)
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_starter

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 30000  # 500 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_user_starter.id)

        assert result is True  # Under 1000 minute limit

    def test_check_limit_starter_over_limit(self, usage_service, mock_db, mock_user_starter):
        """Test starter user over limit returns False."""
        # Setup: User has used 1200 minutes (72000 seconds)
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_starter

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 72000  # 1200 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_user_starter.id)

        assert result is False  # Over 1000 minute limit

    def test_check_limit_professional_higher_limit(
        self, usage_service, mock_db, mock_user_professional
    ):
        """Test professional user has 3000 minute limit."""
        # Setup: User has used 2000 minutes (120000 seconds)
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_professional

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 120000  # 2000 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_user_professional.id)

        assert result is True  # Under 3000 minute limit

    def test_check_limit_user_not_found(self, usage_service, mock_db):
        """Test check_limit returns False when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = usage_service.check_limit(mock_db, user_id="nonexistent")

        assert result is False

    def test_check_limit_non_voice_service_always_true(self, usage_service, mock_db):
        """Test that non-voice_minutes services always return True."""
        result = usage_service.check_limit(mock_db, user_id="any", service_type="tokens")

        assert result is True
        mock_db.execute.assert_not_called()

    def test_check_limit_vop_personal_under_limit(self, usage_service, mock_db, mock_vop_personal):
        """Test Voice of People personal user under limit returns True."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_personal

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 3000  # 50 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_vop_personal.id)

        assert result is True  # Under 100 minute limit

    def test_check_limit_vop_premium_under_limit(self, usage_service, mock_db, mock_vop_premium):
        """Test Voice of People premium user under limit returns True."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_premium

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 15000  # 250 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_vop_premium.id)

        assert result is True  # Under 500 minute limit

    def test_check_limit_vop_pro_under_limit(self, usage_service, mock_db, mock_vop_pro):
        """Test Voice of People pro user under limit returns True."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_pro

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 60000  # 1000 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.check_limit(mock_db, user_id=mock_vop_pro.id)

        assert result is True  # Under 2000 minute limit


class TestGetUsageStats:
    """Tests for getting usage statistics."""

    def test_get_usage_stats_returns_correct_structure(
        self, usage_service, mock_db, mock_user_starter
    ):
        """Test that usage stats return correct structure."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_starter

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 18000  # 300 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_user_starter.id)

        assert "plan" in result
        assert "limit_minutes" in result
        assert "used_minutes" in result
        assert "remaining_minutes" in result
        assert "percent_used" in result

    def test_get_usage_stats_calculates_correctly(self, usage_service, mock_db, mock_user_starter):
        """Test usage stats calculations are correct."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_starter

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 30000  # 500 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_user_starter.id)

        assert result["plan"] == "starter"
        assert result["limit_minutes"] == 1000
        assert result["used_minutes"] == 500.0
        assert result["remaining_minutes"] == 500.0
        assert result["percent_used"] == 50.0

    def test_get_usage_stats_user_not_found(self, usage_service, mock_db):
        """Test usage stats returns empty dict when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = usage_service.get_usage_stats(mock_db, user_id="nonexistent")

        assert result == {}

    def test_get_usage_stats_remaining_not_negative(
        self, usage_service, mock_db, mock_user_starter
    ):
        """Test remaining minutes never goes negative."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_starter

        # User has exceeded limit: 1200 minutes (72000 seconds)
        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 72000

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_user_starter.id)

        assert result["remaining_minutes"] == 0  # Not negative

    def test_get_usage_stats_professional_plan(
        self, usage_service, mock_db, mock_user_professional
    ):
        """Test usage stats for professional plan."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user_professional

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 60000  # 1000 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_user_professional.id)

        assert result["plan"] == "professional"
        assert result["limit_minutes"] == 3000
        assert result["percent_used"] == pytest.approx(33.33, rel=0.01)

    def test_get_usage_stats_vop_personal_plan(self, usage_service, mock_db, mock_vop_personal):
        """Test usage stats for Voice of People personal plan."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_personal

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 3000  # 50 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_vop_personal.id)

        assert result["plan"] == "personal"
        assert result["limit_minutes"] == 100
        assert result["percent_used"] == pytest.approx(50.0, rel=0.01)

    def test_get_usage_stats_vop_premium_plan(self, usage_service, mock_db, mock_vop_premium):
        """Test usage stats for Voice of People premium plan."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_premium

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 15000  # 250 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_vop_premium.id)

        assert result["plan"] == "premium"
        assert result["limit_minutes"] == 500
        assert result["percent_used"] == pytest.approx(50.0, rel=0.01)

    def test_get_usage_stats_vop_pro_plan(self, usage_service, mock_db, mock_vop_pro):
        """Test usage stats for Voice of People pro plan."""
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_vop_pro

        mock_usage_result = MagicMock()
        mock_usage_result.scalar.return_value = 60000  # 1000 minutes

        mock_db.execute.side_effect = [mock_user_result, mock_usage_result]

        result = usage_service.get_usage_stats(mock_db, user_id=mock_vop_pro.id)

        assert result["plan"] == "pro"
        assert result["limit_minutes"] == 2000
        assert result["percent_used"] == pytest.approx(50.0, rel=0.01)


class TestUsageServiceSingleton:
    """Tests for the usage_service singleton."""

    def test_usage_service_singleton_exists(self):
        """Test that usage_service singleton is exported."""
        from app.services.usage_service import usage_service as singleton

        assert singleton is not None
        assert isinstance(singleton, UsageService)
