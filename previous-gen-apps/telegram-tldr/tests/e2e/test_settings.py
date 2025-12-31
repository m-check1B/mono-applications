"""E2E tests for user settings and preferences.

These tests verify:
1. Subscription status management
2. Usage tracking and limits
3. Payment processing (mocked)
4. User state persistence

Note: All tests skip gracefully when the bot app modules are unavailable.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.e2e import requires_app


@requires_app
class TestSubscriptionStatus:
    """Tests for subscription status management."""

    @pytest.mark.asyncio
    async def test_new_chat_starts_unsubscribed(self, mock_redis):
        """New chats should start without subscription."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        is_subscribed = await buffer.is_subscribed(-100123456)
        assert is_subscribed is False

    @pytest.mark.asyncio
    async def test_subscription_can_be_set(self, mock_redis):
        """Subscription can be activated."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        await buffer.set_subscribed(-100123456, months=1)

        # Check subscription status
        key = "tldr:chat:-100123456:subscription"
        assert mock_redis.data.get(key) == "active"

    @pytest.mark.asyncio
    async def test_subscription_has_expiry(self, mock_redis):
        """Subscription should have expiry set."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        await buffer.set_subscribed(-100123456, months=1)

        # Check expiry was set
        key = "tldr:chat:-100123456:subscription"
        assert key in mock_redis.expiry
        # Should be approximately 30 days
        assert mock_redis.expiry[key] >= 29 * 24 * 3600

    @pytest.mark.asyncio
    async def test_subscribed_chat_shows_pro_status(self, bot_context):
        """Subscribed chat should show Pro status."""
        from app.services.bot import cmd_status

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.get_usage_count = AsyncMock(return_value=50)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")
            analytics_mock.track_command = AsyncMock()

            await cmd_status(message)

        response_text = message.answer.call_args[0][0]
        assert "Pro" in response_text
        assert "Unlimited" in response_text


@requires_app
class TestUsageTracking:
    """Tests for usage tracking and limits."""

    @pytest.mark.asyncio
    async def test_new_chat_has_zero_usage(self, mock_redis):
        """New chats should have zero usage count."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        usage = await buffer.get_usage_count(-100123456)
        assert usage == 0

    @pytest.mark.asyncio
    async def test_usage_increments_correctly(self, mock_redis):
        """Usage should increment on each summary."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # First summary
        count1 = await buffer.increment_usage(-100123456)
        assert count1 == 1

        # Second summary
        count2 = await buffer.increment_usage(-100123456)
        assert count2 == 2

        # Third summary
        count3 = await buffer.increment_usage(-100123456)
        assert count3 == 3

    @pytest.mark.asyncio
    async def test_usage_has_monthly_expiry(self, mock_redis):
        """Usage counter should expire monthly."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        await buffer.increment_usage(-100123456)

        key = "tldr:chat:-100123456:usage"
        assert key in mock_redis.expiry
        # Should be approximately 30 days
        assert mock_redis.expiry[key] >= 29 * 24 * 3600

    @pytest.mark.asyncio
    async def test_can_summarize_with_remaining_free_tier(self, mock_redis):
        """Chat with remaining free summaries can summarize."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # Set usage below limit (assuming 3 free)
        mock_redis.data["tldr:chat:-100123456:usage"] = "2"

        can_use, reason = await buffer.can_summarize(-100123456)
        assert can_use is True
        assert "free_tier" in reason

    @pytest.mark.asyncio
    async def test_cannot_summarize_when_limit_reached(self, mock_redis):
        """Chat at limit cannot summarize without subscription."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # Set usage at limit
        mock_redis.data["tldr:chat:-100123456:usage"] = "3"

        can_use, reason = await buffer.can_summarize(-100123456)
        assert can_use is False
        assert reason == "limit_reached"

    @pytest.mark.asyncio
    async def test_subscriber_bypasses_limit(self, mock_redis):
        """Subscribed chat bypasses usage limit."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # Set high usage
        mock_redis.data["tldr:chat:-100123456:usage"] = "100"
        # But also subscribed
        mock_redis.data["tldr:chat:-100123456:subscription"] = "active"

        can_use, reason = await buffer.can_summarize(-100123456)
        assert can_use is True
        assert reason == "subscribed"


@requires_app
class TestPaymentProcessing:
    """Tests for Telegram Stars payment processing."""

    @pytest.mark.asyncio
    async def test_pre_checkout_query_approved(self, bot_context):
        """Pre-checkout query should be approved."""
        from app.services.bot import process_pre_checkout

        query = MagicMock()
        query.answer = AsyncMock()

        await process_pre_checkout(query)

        query.answer.assert_called_once_with(ok=True)

    @pytest.mark.asyncio
    async def test_successful_payment_activates_subscription(self, bot_context):
        """Successful payment should activate subscription."""
        from app.services.bot import process_payment

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.successful_payment = MagicMock()
        message.successful_payment.invoice_payload = "sub:-100123456"
        message.successful_payment.total_amount = 250

        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.settings") as settings_mock,
        ):
            buffer_mock.set_subscribed = AsyncMock()
            analytics_mock.track_subscription = AsyncMock()
            settings_mock.subscription_price_stars = 250

            await process_payment(message)

            buffer_mock.set_subscribed.assert_called_once_with(-100123456, months=1)

    @pytest.mark.asyncio
    async def test_successful_payment_tracks_analytics(self, bot_context):
        """Successful payment should track subscription analytics."""
        from app.services.bot import process_payment

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.successful_payment = MagicMock()
        message.successful_payment.invoice_payload = "sub:-100123456"
        message.successful_payment.total_amount = 250

        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.settings") as settings_mock,
        ):
            buffer_mock.set_subscribed = AsyncMock()
            analytics_mock.track_subscription = AsyncMock()
            settings_mock.subscription_price_stars = 250

            await process_payment(message)

            analytics_mock.track_subscription.assert_called_once_with(-100123456)

    @pytest.mark.asyncio
    async def test_successful_payment_sends_confirmation(self, bot_context):
        """Successful payment should send confirmation message."""
        from app.services.bot import process_payment

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.successful_payment = MagicMock()
        message.successful_payment.invoice_payload = "sub:-100123456"
        message.successful_payment.total_amount = 250

        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.settings") as settings_mock,
        ):
            buffer_mock.set_subscribed = AsyncMock()
            analytics_mock.track_subscription = AsyncMock()
            settings_mock.subscription_price_stars = 250

            await process_payment(message)

            message.answer.assert_called()
            response_text = message.answer.call_args[0][0]
            assert "Thank you" in response_text
            assert "unlimited" in response_text.lower()

    @pytest.mark.asyncio
    async def test_payment_without_payload_handled(self, bot_context):
        """Payment without successful_payment should be handled."""
        from app.services.bot import process_payment

        message = MagicMock()
        message.answer = AsyncMock()
        message.successful_payment = None

        # Should not crash
        await process_payment(message)

        # Should not send any message
        message.answer.assert_not_called()


@requires_app
class TestUserStateManagement:
    """Tests for user state management."""

    @pytest.mark.asyncio
    async def test_status_shows_remaining_summaries(self, bot_context):
        """Status should show remaining free summaries."""
        from app.services.bot import cmd_status

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.settings") as settings_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.get_usage_count = AsyncMock(return_value=1)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")
            settings_mock.free_summaries = 3
            analytics_mock.track_command = AsyncMock()

            await cmd_status(message)

        response_text = message.answer.call_args[0][0]
        # Should show remaining (3-1=2)
        assert "2" in response_text or "remaining" in response_text.lower()

    @pytest.mark.asyncio
    async def test_usage_tracked_after_summary(self, bot_context):
        """Usage should be incremented after successful summary."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with (
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.summarize_messages") as summarize_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "Hello", "ts": "2025-12-21T10:00:00"}]
            )
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.increment_usage = AsyncMock(return_value=1)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            summarize_mock.return_value = "Summary..."
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            await cmd_summary(message)

            # Verify usage was incremented
            buffer_mock.increment_usage.assert_called_once_with(-100123456)

    @pytest.mark.asyncio
    async def test_usage_not_tracked_for_subscribers(self, bot_context):
        """Usage should not be incremented for subscribers."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with (
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.summarize_messages") as summarize_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "subscribed"))
            buffer_mock.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "Hello", "ts": "2025-12-21T10:00:00"}]
            )
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.increment_usage = AsyncMock()
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            summarize_mock.return_value = "Summary..."
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            await cmd_summary(message)

            # Usage should NOT be incremented for subscribers
            buffer_mock.increment_usage.assert_not_called()


@requires_app
class TestAnalyticsTracking:
    """Tests for analytics tracking."""

    @pytest.mark.asyncio
    async def test_command_usage_tracked(self, mock_redis):
        """Command usage should be tracked."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_command("summary")

        # Check command was tracked
        key = "tldr:analytics:commands:summary"
        assert key in mock_redis.data
        assert mock_redis.data[key] == "1"

    @pytest.mark.asyncio
    async def test_message_tracking(self, mock_redis):
        """Message processing should be tracked."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_message(chat_id=-100123456, user_id=12345)

        # Check message was tracked
        total_key = "tldr:analytics:messages:total"
        assert total_key in mock_redis.data

    @pytest.mark.asyncio
    async def test_summary_tracking(self, mock_redis):
        """Summary generation should be tracked."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_summary(chat_id=-100123456, user_id=12345, message_count=50)

        # Check summary was tracked
        total_key = "tldr:analytics:summaries:total"
        assert total_key in mock_redis.data

    @pytest.mark.asyncio
    async def test_error_tracking(self, mock_redis):
        """Errors should be tracked."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_error("api_error", "Rate limit exceeded")

        # Check error was tracked
        total_key = "tldr:analytics:errors:total"
        assert total_key in mock_redis.data

    @pytest.mark.asyncio
    async def test_subscription_tracking(self, mock_redis):
        """Subscriptions should be tracked."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_subscription(chat_id=-100123456)

        # Check subscription was tracked
        total_key = "tldr:analytics:subscriptions:total"
        assert total_key in mock_redis.data


@requires_app
class TestAdminPrivileges:
    """Tests for admin-specific features."""

    @pytest.mark.asyncio
    async def test_admin_check_with_valid_admin(self):
        """Admin check should return True for valid admin."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = "12345,67890"

            assert _is_admin(12345) is True
            assert _is_admin(67890) is True

    @pytest.mark.asyncio
    async def test_admin_check_with_non_admin(self):
        """Admin check should return False for non-admin."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = "12345,67890"

            assert _is_admin(99999) is False

    @pytest.mark.asyncio
    async def test_admin_check_with_empty_config(self):
        """Admin check should return False when no admins configured."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = ""

            assert _is_admin(12345) is False

    @pytest.mark.asyncio
    async def test_admin_check_with_none_config(self):
        """Admin check should return False when admin_user_ids is None."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = None

            assert _is_admin(12345) is False
