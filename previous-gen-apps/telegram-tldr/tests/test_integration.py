"""Integration tests for TL;DR Bot main flows.

These tests verify end-to-end behavior from Telegram update → bot handler → response.

Main flows tested:
1. New user onboarding (/start → /help → /status)
2. Subscription flow (/subscribe → payment → Pro status)
3. Summary generation flow (messages → /summary → AI response)
4. Scheduled digest flow (/schedule configuration)
5. Content personalization flow (/topics → /mydigest)
6. Error handling and edge cases
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def create_message_mock(
    chat_id: int = -100123456,
    user_id: int = 12345,
    text: str = "/start",
    chat_type: str = "supergroup",
    username: str = "testuser",
):
    """Create a mock message object."""
    message = MagicMock()
    message.answer = AsyncMock()
    message.chat = MagicMock()
    message.chat.id = chat_id
    message.chat.type = chat_type
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.from_user.username = username
    message.from_user.first_name = "Test"
    message.text = text
    message.successful_payment = None
    return message


# ============================================================
# INTEGRATION TESTS: USER ONBOARDING FLOW
# ============================================================


class TestOnboardingFlow:
    """Test the complete new user onboarding experience."""

    @pytest.mark.asyncio
    async def test_start_to_help_flow(self):
        """Test: /start → /help for new user."""
        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_start, cmd_help

            # Step 1: User sends /start
            message = create_message_mock(text="/start")
            await cmd_start(message)

            response = message.answer.call_args[0][0]
            assert "Sumarium" in response
            assert "Add me to your group" in response
            analytics_mock.track_command.assert_called_with("start")

            # Step 2: User sends /help to learn commands
            message = create_message_mock(text="/help")
            with patch("app.services.bot._is_admin", return_value=False):
                await cmd_help(message)

            response = message.answer.call_args[0][0]
            assert "/summary" in response
            assert "/subscribe" in response

    @pytest.mark.asyncio
    async def test_status_shows_free_tier(self):
        """Test that /status shows free tier for new users."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.get_usage_count = AsyncMock(return_value=0)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_status

            message = create_message_mock(text="/status")
            await cmd_status(message)

            response = message.answer.call_args[0][0]
            assert "Free" in response or "free" in response.lower()

    @pytest.mark.asyncio
    async def test_private_summary_requires_group(self):
        """Test that /summary in private chat guides to group."""
        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(chat_id=12345, chat_type="private", text="/summary")
            await cmd_summary(message)

            response = message.answer.call_args[0][0]
            assert "group" in response.lower()


# ============================================================
# INTEGRATION TESTS: SUBSCRIPTION FLOW
# ============================================================


class TestSubscriptionFlow:
    """Test the complete subscription and payment flow."""

    @pytest.mark.asyncio
    async def test_subscribe_sends_invoice(self):
        """Test that /subscribe sends Telegram Stars invoice."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            bot_mock.send_invoice = AsyncMock()
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_subscribe

            message = create_message_mock(text="/subscribe")
            await cmd_subscribe(message)

            bot_mock.send_invoice.assert_called_once()
            call_kwargs = bot_mock.send_invoice.call_args[1]
            assert call_kwargs["currency"] == "XTR"
            assert "Pro" in call_kwargs["title"]

    @pytest.mark.asyncio
    async def test_already_subscribed_skips_invoice(self):
        """Test that already subscribed users can't re-subscribe."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            bot_mock.send_invoice = AsyncMock()
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_subscribe

            message = create_message_mock(text="/subscribe")
            await cmd_subscribe(message)

            response = message.answer.call_args[0][0]
            assert "already" in response.lower()
            bot_mock.send_invoice.assert_not_called()

    @pytest.mark.asyncio
    async def test_successful_payment_grants_pro(self):
        """Test that successful payment grants Pro status."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.settings") as settings_mock,
        ):
            buffer_mock.set_subscribed = AsyncMock()
            analytics_mock.track_subscription = AsyncMock()
            settings_mock.subscription_price_stars = 250

            from app.services.bot import process_payment

            chat_id = -100123456
            message = create_message_mock(chat_id=chat_id)
            message.successful_payment = MagicMock()
            message.successful_payment.invoice_payload = f"sub:{chat_id}"
            message.successful_payment.total_amount = 250

            await process_payment(message)

            buffer_mock.set_subscribed.assert_called_once()
            response = message.answer.call_args[0][0]
            assert "Thank you" in response

    @pytest.mark.asyncio
    async def test_limit_reached_shows_subscribe_prompt(self):
        """Test that reaching usage limit prompts subscription."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.can_summarize = AsyncMock(return_value=(False, "limit_reached"))
            analytics_mock.track_command = AsyncMock()

            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            response = message.answer.call_args[0][0]
            assert "subscribe" in response.lower() or "Stars" in response


# ============================================================
# INTEGRATION TESTS: SUMMARY GENERATION FLOW
# ============================================================


class TestSummaryGenerationFlow:
    """Test the complete summary generation flow."""

    @pytest.mark.asyncio
    async def test_summary_generates_response(self):
        """Test that /summary generates AI response from buffered messages."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.summarize_messages") as summarize_mock,
        ):
            mock_messages = [
                {"user": "alice", "text": "Hello world", "ts": "2025-12-26T10:00:00"},
                {"user": "bob", "text": "Hi there!", "ts": "2025-12-26T10:01:00"},
            ]
            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=mock_messages)
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.increment_usage = AsyncMock(return_value=1)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            summarize_mock.return_value = "**Summary**: Greetings exchanged"
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            summarize_mock.assert_called_once()
            analytics_mock.track_summary.assert_called_once()

            # Last response should contain the summary
            last_call = message.answer.call_args_list[-1]
            response = last_call[0][0]
            assert "Summary" in response

    @pytest.mark.asyncio
    async def test_summary_respects_preferences(self):
        """Test that summary uses length and language preferences."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.summarize_messages") as summarize_mock,
        ):
            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "Test", "ts": "2025-12-26T10:00:00"}]
            )
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.get_summary_length = AsyncMock(return_value="short")
            buffer_mock.get_summary_language = AsyncMock(return_value="cs")

            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            summarize_mock.return_value = "Krátký souhrn"
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            call_kwargs = summarize_mock.call_args[1]
            assert call_kwargs.get("length") == "short"
            assert call_kwargs.get("language") == "cs"

    @pytest.mark.asyncio
    async def test_empty_buffer_shows_message(self):
        """Test that /summary with no messages shows appropriate message."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=[])

            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            calls = message.answer.call_args_list
            any_no_messages = any("no messages" in str(c).lower() for c in calls)
            assert any_no_messages


# ============================================================
# INTEGRATION TESTS: SCHEDULED DIGEST FLOW
# ============================================================


class TestScheduledDigestFlow:
    """Test the scheduled digest setup and management flow."""

    @pytest.mark.asyncio
    async def test_schedule_requires_subscription(self):
        """Test that scheduling requires Pro subscription."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_schedule

            message = create_message_mock(text="/schedule 09:00")
            await cmd_schedule(message)

            response = message.answer.call_args[0][0]
            assert "Pro" in response or "Subscribe" in response

    @pytest.mark.asyncio
    async def test_schedule_sets_time(self):
        """Test that /schedule sets the scheduled time for Pro users."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.set_schedule = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_schedule

            chat_id = -100123456
            message = create_message_mock(chat_id=chat_id, text="/schedule 09:00")
            await cmd_schedule(message)

            buffer_mock.set_schedule.assert_called_once_with(chat_id, 9, 0)
            response = message.answer.call_args[0][0]
            assert "scheduled" in response.lower()

    @pytest.mark.asyncio
    async def test_unschedule_removes_schedule(self):
        """Test that /unschedule removes the scheduled digest."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.remove_schedule = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_unschedule

            message = create_message_mock(text="/unschedule")
            await cmd_unschedule(message)

            buffer_mock.remove_schedule.assert_called()

    @pytest.mark.asyncio
    async def test_periodic_sets_interval(self):
        """Test that /periodic sets the interval for Pro users."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.get_periodic_schedule = AsyncMock(return_value=None)
            buffer_mock.set_periodic_schedule = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_periodic

            chat_id = -100123456
            message = create_message_mock(chat_id=chat_id, text="/periodic 6h")
            await cmd_periodic(message)

            buffer_mock.set_periodic_schedule.assert_called()
            call_args = buffer_mock.set_periodic_schedule.call_args
            assert call_args[0][1] == 6  # 6 hours


# ============================================================
# INTEGRATION TESTS: CONTENT PERSONALIZATION FLOW
# ============================================================


class TestContentPersonalizationFlow:
    """Test the topic subscription and personalized digest flow."""

    @pytest.mark.asyncio
    async def test_topics_shows_available(self):
        """Test that /topics shows available topics for Pro users."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.content_subscription") as content_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            content_mock.is_content_subscriber = AsyncMock(return_value=False)
            content_mock.get_available_topics = AsyncMock(return_value=["tech", "crypto", "deals"])
            content_mock.get_user_topics = AsyncMock(return_value=[])
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_topics

            message = create_message_mock(text="/topics")
            await cmd_topics(message)

            response = message.answer.call_args[0][0]
            assert "tech" in response.lower() or "Available" in response

    @pytest.mark.asyncio
    async def test_topics_add_subscribes(self):
        """Test that /topics add subscribes to topics."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.content_subscription") as content_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            content_mock.is_content_subscriber = AsyncMock(return_value=False)
            content_mock.subscribe_to_topics = AsyncMock(return_value=["tech", "crypto"])
            content_mock.set_content_subscription = AsyncMock()
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_topics

            user_id = 12345
            message = create_message_mock(user_id=user_id, text="/topics add tech,crypto")
            await cmd_topics(message)

            content_mock.subscribe_to_topics.assert_called_with(user_id, ["tech", "crypto"])

    @pytest.mark.asyncio
    async def test_mydigest_requires_topics(self):
        """Test that /mydigest requires topic subscriptions."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.content_subscription") as content_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            content_mock.is_content_subscriber = AsyncMock(return_value=True)
            content_mock.get_user_topics = AsyncMock(return_value=[])
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_mydigest

            message = create_message_mock(text="/mydigest")
            await cmd_mydigest(message)

            response = message.answer.call_args[0][0]
            assert "No topics" in response or "/topics add" in response

    @pytest.mark.asyncio
    async def test_content_subscribe_sends_invoice(self):
        """Test that /content_subscribe sends invoice."""
        with (
            patch("app.services.bot.content_subscription") as content_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            content_mock.is_content_subscriber = AsyncMock(return_value=False)
            bot_mock.send_invoice = AsyncMock()
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_content_subscribe

            message = create_message_mock(text="/content_subscribe")
            await cmd_content_subscribe(message)

            bot_mock.send_invoice.assert_called_once()
            call_kwargs = bot_mock.send_invoice.call_args[1]
            assert call_kwargs["currency"] == "XTR"
            assert "Content" in call_kwargs["title"]


# ============================================================
# INTEGRATION TESTS: ERROR HANDLING
# ============================================================


class TestErrorHandling:
    """Test error handling and edge cases in main flows."""

    @pytest.mark.asyncio
    async def test_non_admin_cannot_summarize(self):
        """Test that non-admins cannot request summaries."""
        with (
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            member_mock = MagicMock()
            member_mock.status = "member"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            response = message.answer.call_args[0][0]
            assert "admin" in response.lower()

    @pytest.mark.asyncio
    async def test_invalid_schedule_time_rejected(self):
        """Test that invalid schedule times are rejected."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.set_schedule = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_schedule

            message = create_message_mock(text="/schedule 25:00")
            await cmd_schedule(message)

            response = message.answer.call_args[0][0]
            assert "Invalid" in response or "format" in response.lower()
            buffer_mock.set_schedule.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_length_rejected(self):
        """Test that invalid length preferences are rejected."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.set_summary_length = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_length

            message = create_message_mock(text="/length xlarge")
            await cmd_length(message)

            response = message.answer.call_args[0][0]
            assert "Invalid" in response or "short" in response.lower()
            buffer_mock.set_summary_length.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_language_rejected(self):
        """Test that unsupported languages are rejected."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.set_summary_language = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_language

            message = create_message_mock(text="/language xyz")
            await cmd_language(message)

            response = message.answer.call_args[0][0]
            assert "Unknown" in response or "list" in response.lower()
            buffer_mock.set_summary_language.assert_not_called()


# ============================================================
# INTEGRATION TESTS: ANALYTICS TRACKING
# ============================================================


class TestAnalyticsTracking:
    """Test that analytics are properly tracked across flows."""

    @pytest.mark.asyncio
    async def test_start_tracks_analytics(self):
        """Test that /start tracks analytics."""
        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_start

            message = create_message_mock(text="/start")
            await cmd_start(message)

            analytics_mock.track_command.assert_called_with("start")

    @pytest.mark.asyncio
    async def test_help_tracks_analytics(self):
        """Test that /help tracks analytics."""
        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            from app.services.bot import cmd_help

            message = create_message_mock(text="/help")
            with patch("app.services.bot._is_admin", return_value=False):
                await cmd_help(message)

            analytics_mock.track_command.assert_called_with("help")

    @pytest.mark.asyncio
    async def test_summary_tracks_analytics(self):
        """Test that summary generation tracks analytics."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.bot") as bot_mock,
            patch("app.services.bot.analytics") as analytics_mock,
            patch("app.services.bot.summarize_messages") as summarize_mock,
        ):
            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "Hello", "ts": "2025-12-26T10:00:00"}]
            )
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            summarize_mock.return_value = "Summary"
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            from app.services.bot import cmd_summary

            message = create_message_mock(text="/summary")
            await cmd_summary(message)

            analytics_mock.track_command.assert_called_with("summary")
            analytics_mock.track_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_buffering_tracks_analytics(self):
        """Test that message buffering tracks analytics."""
        with (
            patch("app.services.bot.buffer") as buffer_mock,
            patch("app.services.bot.analytics") as analytics_mock,
        ):
            buffer_mock.add_message = AsyncMock()
            analytics_mock.track_message = AsyncMock()

            from app.services.bot import handle_message

            message = create_message_mock(text="Hello world!")
            await handle_message(message)

            analytics_mock.track_message.assert_called_once()
            buffer_mock.add_message.assert_called_once()
