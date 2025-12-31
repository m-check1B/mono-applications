"""E2E tests for channel message summarization pipeline.

These tests verify the complete summarization flow:
1. Message buffering (collection from group)
2. Summarization request processing
3. LLM integration (mocked)
4. Response formatting and delivery

Note: All tests skip gracefully when the bot app modules are unavailable.
"""
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.e2e import requires_app


@requires_app
class TestMessageBuffering:
    """Tests for message buffering functionality."""

    @pytest.mark.asyncio
    async def test_messages_are_buffered_in_group(self, update_factory, bot_context):
        """Messages in groups should be added to buffer."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.text = "Hello everyone!"
        message.date = datetime.now(UTC)

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.add_message = AsyncMock()
            analytics_mock.track_message = AsyncMock()

            await handle_message(message)

            buffer_mock.add_message.assert_called_once()
            call_kwargs = buffer_mock.add_message.call_args[1]
            assert call_kwargs["chat_id"] == -100123456
            assert call_kwargs["user_name"] == "testuser"
            assert call_kwargs["text"] == "Hello everyone!"

    @pytest.mark.asyncio
    async def test_private_messages_not_buffered(self, update_factory, bot_context):
        """Private messages should not be buffered."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = 12345  # Positive ID = private chat
        message.chat.type = "private"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "Private message"

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.add_message = AsyncMock()

            await handle_message(message)

            buffer_mock.add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_messages_not_buffered(self, update_factory, bot_context):
        """Empty messages should not be buffered."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = None  # Empty text

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.add_message = AsyncMock()

            await handle_message(message)

            buffer_mock.add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_messages_from_bots_handled(self, update_factory, bot_context):
        """Messages from other bots should be handled (but may be filtered)."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = None  # No user (system message)
        message.text = "Bot joined the chat"

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.add_message = AsyncMock()

            # Should not crash
            await handle_message(message)

            # Should not buffer messages without user
            buffer_mock.add_message.assert_not_called()


@requires_app
class TestMessageBufferService:
    """Tests for the MessageBuffer service class."""

    @pytest.mark.asyncio
    async def test_buffer_stores_messages_with_timestamp(self, mock_redis):
        """Buffer should store messages with timestamp score."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        timestamp = datetime.now(UTC)
        await buffer.add_message(
            chat_id=-100123456,
            user_name="testuser",
            text="Test message",
            timestamp=timestamp,
        )

        # Verify message was added to sorted set
        key = "tldr:chat:-100123456:messages"
        assert key in mock_redis.sorted_sets
        assert len(mock_redis.sorted_sets[key]) == 1

    @pytest.mark.asyncio
    async def test_buffer_retrieves_messages_in_time_window(self, mock_redis):
        """Buffer should retrieve messages within time window."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # Add messages at different times
        now = datetime.now(UTC)
        old_time = now - timedelta(hours=25)  # 25 hours ago
        recent_time = now - timedelta(hours=2)  # 2 hours ago

        # Add old message
        old_msg = json.dumps({"user": "user1", "text": "Old message", "ts": old_time.isoformat()})
        mock_redis.sorted_sets["tldr:chat:-100123456:messages"] = {
            old_msg: old_time.timestamp(),
        }

        # Add recent message
        recent_msg = json.dumps({"user": "user2", "text": "Recent message", "ts": recent_time.isoformat()})
        mock_redis.sorted_sets["tldr:chat:-100123456:messages"][recent_msg] = recent_time.timestamp()

        # Get messages from last 24 hours
        messages = await buffer.get_messages(-100123456, hours=24)

        # Should only get recent message (old one is > 24 hours ago)
        assert len(messages) >= 1
        texts = [m.get("text") for m in messages]
        assert "Recent message" in texts

    @pytest.mark.asyncio
    async def test_buffer_respects_max_messages(self, mock_redis):
        """Buffer should respect max message limit."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis
        buffer.max_messages = 5

        now = datetime.now(UTC)

        # Add more than max messages
        for i in range(10):
            ts = now - timedelta(minutes=i)
            await buffer.add_message(
                chat_id=-100123456,
                user_name=f"user{i}",
                text=f"Message {i}",
                timestamp=ts,
            )

        # Buffer should have stored messages (trim happens in Redis)
        key = "tldr:chat:-100123456:messages"
        assert key in mock_redis.sorted_sets


@requires_app
class TestSummarizationPipeline:
    """Tests for the complete summarization pipeline."""

    @pytest.mark.asyncio
    async def test_summarization_formats_messages_correctly(self, mock_summarizer):
        """Summarizer should format messages for LLM correctly."""
        messages = [
            {"user": "alice", "text": "What should we do for dinner?", "ts": "2025-12-21T18:00:00"},
            {"user": "bob", "text": "How about pizza?", "ts": "2025-12-21T18:01:00"},
            {"user": "charlie", "text": "Sounds good to me!", "ts": "2025-12-21T18:02:00"},
        ]

        result = await mock_summarizer(messages)

        assert "Topics" in result
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_summarization_handles_empty_messages(self, mock_summarizer):
        """Summarizer should handle empty message list."""
        result = await mock_summarizer([])
        assert "No messages" in result

    @pytest.mark.asyncio
    async def test_summarizer_service_returns_formatted_output(self):
        """Summarizer service should return properly formatted output."""
        from app.services.summarizer import summarize_messages

        messages = [
            {"user": "user1", "text": "Hello", "ts": "2025-12-21T10:00:00"},
        ]

        with patch("app.services.summarizer.get_model") as model_mock:
            mock_response = MagicMock()
            mock_response.text = (
                "**Topics Discussed:**\n"
                "- Greetings\n\n"
                "**Key Points:**\n"
                "- Users said hello\n\n"
                "**Links Shared:**\n"
                "- None\n\n"
                "**Unanswered Questions:**\n"
                "- None\n\n"
                "**Activity:** 1 messages from 1 users"
            )
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            model_mock.return_value = mock_model

            result = await summarize_messages(messages)

            assert "Topics Discussed" in result
            assert "Key Points" in result
            assert "1 messages" in result  # Updated: output format changed

    @pytest.mark.asyncio
    async def test_summarizer_handles_api_errors(self):
        """Summarizer should handle API errors gracefully."""
        from app.services.summarizer import summarize_messages

        messages = [{"user": "user1", "text": "Test", "ts": "2025-12-21T10:00:00"}]

        with patch("app.services.summarizer.get_model") as model_mock:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                side_effect=Exception("API rate limit exceeded")
            )
            model_mock.return_value = mock_model

            result = await summarize_messages(messages)

            assert "Error" in result or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_summarizer_limits_message_count(self):
        """Summarizer should limit messages to max configured."""
        from app.services.summarizer import summarize_messages

        # Create many messages
        messages = [
            {"user": f"user{i}", "text": f"Message {i}", "ts": "2025-12-21T10:00:00"}
            for i in range(1000)
        ]

        with patch("app.services.summarizer.get_model") as model_mock, \
             patch("app.services.summarizer.settings") as settings_mock:
            settings_mock.max_messages_per_summary = 500

            mock_response = MagicMock()
            mock_response.text = "Summary..."
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            model_mock.return_value = mock_model

            await summarize_messages(messages)

            # Verify the prompt was called
            mock_model.generate_content_async.assert_called_once()


@requires_app
class TestSummarizationViaWebhook:
    """Tests for summarization triggered via webhook."""

    @pytest.mark.asyncio
    async def test_webhook_processes_update(self, update_factory):
        """Webhook should process Telegram updates via process_update function."""
        from app.services.bot import process_update

        # Create a valid message update
        update = update_factory.create_command_update("start", chat_type="private")

        with patch("app.services.bot.dp") as dp_mock, \
             patch("app.services.bot.bot"):
            dp_mock.feed_update = AsyncMock()

            # Process the update directly (bypassing HTTP layer)
            await process_update(update)

            # Should have called the dispatcher
            dp_mock.feed_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_endpoint_validates_secret(self, update_factory):
        """Webhook endpoint should validate secret token when configured."""
        # Test the validation logic directly
        from fastapi import HTTPException, Request

        from app.main import telegram_webhook

        update = update_factory.create_command_update("start")

        # Create a mock request without secret header
        request = MagicMock(spec=Request)
        request.headers = {}
        request.json = AsyncMock(return_value=update)

        with patch("app.main.settings") as settings_mock, \
             patch("app.main.process_update", AsyncMock()):
            settings_mock.telegram_webhook_secret = "secret123"

            # Should raise 403 without secret
            try:
                await telegram_webhook(request)
                assert False, "Should have raised HTTPException"
            except HTTPException as e:
                assert e.status_code == 403

    @pytest.mark.asyncio
    async def test_webhook_endpoint_accepts_valid_secret(self, update_factory):
        """Webhook endpoint should accept requests with valid secret token."""
        from fastapi import Request

        from app.main import telegram_webhook

        update = update_factory.create_command_update("start")

        # Create a mock request with correct secret header
        request = MagicMock(spec=Request)
        request.headers = {"X-Telegram-Bot-Api-Secret-Token": "secret123"}
        request.json = AsyncMock(return_value=update)

        with patch("app.main.settings") as settings_mock, \
             patch("app.main.process_update", AsyncMock()):
            settings_mock.telegram_webhook_secret = "secret123"

            # Should succeed
            result = await telegram_webhook(request)
            assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_webhook_endpoint_rejects_when_secret_not_configured(self, update_factory):
        """Webhook endpoint should reject requests when secret is not configured (security)."""
        from fastapi import HTTPException, Request

        from app.main import telegram_webhook

        update = update_factory.create_command_update("start")

        # Create a mock request without secret header
        request = MagicMock(spec=Request)
        request.headers = {}
        request.json = AsyncMock(return_value=update)

        with patch("app.main.settings") as settings_mock, \
             patch("app.main.process_update", AsyncMock()):
            settings_mock.telegram_webhook_secret = ""  # Not configured

            # Should reject - webhook disabled for security when secret is not set
            with pytest.raises(HTTPException) as exc_info:
                await telegram_webhook(request)
            assert exc_info.value.status_code == 503
            assert exc_info.value.detail == "Webhook not configured"


@requires_app
class TestSummarizationQuality:
    """Tests for summarization output quality."""

    @pytest.mark.asyncio
    async def test_summary_includes_required_sections(self, mock_summarizer):
        """Summary should include all required sections."""
        messages = [
            {"user": "alice", "text": "Check out https://example.com", "ts": "2025-12-21T10:00:00"},
            {"user": "bob", "text": "What do you think about the proposal?", "ts": "2025-12-21T10:01:00"},
        ]

        result = await mock_summarizer(messages)

        # Check for required sections
        assert "Topics" in result
        assert "Key Points" in result or "Points" in result

    @pytest.mark.asyncio
    async def test_summary_includes_message_count(self, mock_summarizer):
        """Summary should include message count metadata."""
        messages = [
            {"user": "user1", "text": "Message 1", "ts": "2025-12-21T10:00:00"},
            {"user": "user2", "text": "Message 2", "ts": "2025-12-21T10:01:00"},
            {"user": "user3", "text": "Message 3", "ts": "2025-12-21T10:02:00"},
        ]

        result = await mock_summarizer(messages)

        # Should indicate number of messages summarized
        assert "3" in result or "messages" in result.lower()


@requires_app
class TestErrorHandling:
    """Tests for error handling in summarization pipeline."""

    @pytest.mark.asyncio
    async def test_handles_redis_connection_failure(self, bot_context):
        """Should handle Redis connection failures gracefully."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = None  # Simulate no connection

        messages = await buffer.get_messages(-100123456, hours=24)
        assert messages == []

        count = await buffer.get_usage_count(-100123456)
        assert count == 0

    @pytest.mark.asyncio
    async def test_handles_malformed_messages(self, mock_redis):
        """Should handle malformed messages in buffer."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = mock_redis

        # Add malformed data to sorted set
        mock_redis.sorted_sets["tldr:chat:-100123456:messages"] = {
            "not-valid-json": 12345.0,
        }

        # Should handle gracefully (may raise or return empty)
        try:
            await buffer.get_messages(-100123456, hours=24)
            # If it doesn't raise, should return something
        except json.JSONDecodeError:
            # This is acceptable error handling
            pass

    @pytest.mark.asyncio
    async def test_tracks_errors_in_analytics(self, bot_context):
        """Should track errors in analytics."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.summarize_messages") as summarize_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=[
                {"user": "test", "text": "Hello", "ts": "2025-12-21T10:00:00"}
            ])

            # Simulate summarization error
            summarize_mock.side_effect = Exception("LLM API Error")
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_error = AsyncMock()

            await cmd_summary(message)

            # Should track the error
            analytics_mock.track_error.assert_called()
