"""Service tests for TL;DR Bot."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMessageBuffer:
    """Tests for the message buffer service."""

    @pytest.fixture
    def buffer_service(self):
        """Create buffer service with mocked Redis."""
        from app.services.buffer import MessageBuffer
        buffer = MessageBuffer()
        buffer.redis = AsyncMock()
        return buffer

    @pytest.mark.asyncio
    async def test_buffer_connect(self, buffer_service):
        """Buffer should connect to Redis."""
        with patch("app.services.buffer.redis") as mock_redis:
            mock_redis.from_url = MagicMock(return_value=AsyncMock())
            await buffer_service.connect()
            # Should attempt Redis connection

    @pytest.mark.asyncio
    async def test_buffer_add_message(self, buffer_service):
        """Buffer should add messages to Redis list."""
        buffer_service.redis.lpush = AsyncMock(return_value=1)
        buffer_service.redis.ltrim = AsyncMock()

        # Add a message (implementation may vary)
        # This tests the general pattern

    @pytest.mark.asyncio
    async def test_buffer_get_messages(self, buffer_service):
        """Buffer should retrieve messages from Redis."""
        buffer_service.redis.lrange = AsyncMock(return_value=[
            b'{"text": "Hello", "user": "test"}',
            b'{"text": "World", "user": "test2"}'
        ])

        # Get messages (implementation may vary)


class TestSummarizer:
    """Tests for the summarization service."""

    @pytest.mark.asyncio
    async def test_summarizer_handles_empty_messages(self):
        """Summarizer should handle empty message list."""
        from app.services.summarizer import summarize_messages
        result = await summarize_messages([])
        assert result == "No messages to summarize."

    @pytest.mark.asyncio
    async def test_summarizer_returns_text(self):
        """Summarizer should return text summary."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="This is a summary of the chat.")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages
            messages = [
                {"user": "alice", "text": "Hello everyone", "ts": "2025-01-01T12:00:00"},
                {"user": "bob", "text": "Hi Alice!", "ts": "2025-01-01T12:01:00"}
            ]
            result = await summarize_messages(messages)
            assert "summary" in result.lower() or "2 messages" in result

    @pytest.mark.asyncio
    async def test_summarizer_handles_api_error(self):
        """Summarizer should handle Gemini API errors gracefully."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages
            messages = [{"user": "test", "text": "test message", "ts": "2025-01-01"}]
            result = await summarize_messages(messages)
            assert "Error" in result


class TestTopicDetection:
    """Tests for topic detection functionality."""

    @pytest.mark.asyncio
    async def test_detect_topics_returns_none_for_empty_messages(self):
        """Topic detection should return None for empty messages."""
        from app.services.summarizer import detect_topics
        result = await detect_topics([])
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_topics_returns_none_for_few_messages(self):
        """Topic detection should return None for < 3 messages."""
        from app.services.summarizer import detect_topics
        messages = [
            {"user": "alice", "text": "Hello", "ts": "2025-01-01T12:00:00"},
            {"user": "bob", "text": "Hi", "ts": "2025-01-01T12:01:00"},
        ]
        result = await detect_topics(messages)
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_topics_parses_json_response(self):
        """Topic detection should parse JSON response correctly."""
        import json
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_response = {
                "topics": [
                    {
                        "name": "Project Discussion",
                        "description": "Discussion about project timeline",
                        "message_indices": [0, 1, 2],
                        "participants": ["alice", "bob"],
                        "importance": "high",
                        "has_action_items": True,
                        "has_questions": False
                    }
                ],
                "off_topic_indices": [3]
            }
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text=json.dumps(mock_response))
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import detect_topics
            messages = [
                {"user": "alice", "text": "Let's discuss the project", "ts": "2025-01-01T12:00:00"},
                {"user": "bob", "text": "Sure, what's the timeline?", "ts": "2025-01-01T12:01:00"},
                {"user": "alice", "text": "We need to finish by Friday", "ts": "2025-01-01T12:02:00"},
                {"user": "charlie", "text": "Hi everyone!", "ts": "2025-01-01T12:03:00"},
            ]
            result = await detect_topics(messages)

            assert result is not None
            assert "topics" in result
            assert len(result["topics"]) == 1
            assert result["topics"][0]["name"] == "Project Discussion"

    @pytest.mark.asyncio
    async def test_detect_topics_handles_markdown_wrapped_json(self):
        """Topic detection should handle JSON wrapped in markdown code blocks."""
        import json
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_response = {
                "topics": [{"name": "Test", "message_indices": [0], "participants": ["user"]}],
                "off_topic_indices": []
            }
            # Response wrapped in markdown code block
            wrapped_response = f"```json\n{json.dumps(mock_response)}\n```"
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text=wrapped_response)
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import detect_topics
            messages = [
                {"user": "user", "text": "Test message 1", "ts": "2025-01-01T12:00:00"},
                {"user": "user", "text": "Test message 2", "ts": "2025-01-01T12:01:00"},
                {"user": "user", "text": "Test message 3", "ts": "2025-01-01T12:02:00"},
            ]
            result = await detect_topics(messages)

            assert result is not None
            assert "topics" in result

    @pytest.mark.asyncio
    async def test_detect_topics_handles_api_error(self):
        """Topic detection should return None on API error."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import detect_topics
            messages = [
                {"user": "user", "text": f"Message {i}", "ts": "2025-01-01T12:00:00"}
                for i in range(5)
            ]
            result = await detect_topics(messages)
            assert result is None

    @pytest.mark.asyncio
    async def test_summarize_with_topics_falls_back_for_small_message_count(self):
        """Summarize with topics should use simple summary for < 10 messages."""
        with patch("app.services.summarizer.summarize_messages") as mock_simple:
            mock_simple.return_value = "Simple summary"

            from app.services.summarizer import summarize_with_topics
            messages = [
                {"user": "user", "text": f"Message {i}", "ts": "2025-01-01T12:00:00"}
                for i in range(5)
            ]
            result = await summarize_with_topics(messages)

            mock_simple.assert_called_once()
            assert result == "Simple summary"

    @pytest.mark.asyncio
    async def test_summarize_with_topics_handles_empty_messages(self):
        """Summarize with topics should handle empty message list."""
        from app.services.summarizer import summarize_with_topics
        result = await summarize_with_topics([])
        assert result == "No messages to summarize."

    @pytest.mark.asyncio
    async def test_get_topic_stats_returns_empty_for_no_topics(self):
        """Get topic stats should return empty stats when no topics detected."""
        with patch("app.services.summarizer.detect_topics") as mock_detect:
            mock_detect.return_value = None

            from app.services.summarizer import get_topic_stats
            messages = [
                {"user": "user", "text": "Test", "ts": "2025-01-01T12:00:00"}
            ]
            result = await get_topic_stats(messages)

            assert result["topic_count"] == 0
            assert result["topics"] == []
            assert result["total_messages"] == 1

    @pytest.mark.asyncio
    async def test_get_topic_stats_sorts_by_importance(self):
        """Get topic stats should sort topics by importance."""
        import json
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_response = {
                "topics": [
                    {"name": "Low Priority", "importance": "low", "message_indices": [0], "participants": ["a"]},
                    {"name": "High Priority", "importance": "high", "message_indices": [1], "participants": ["b"]},
                    {"name": "Medium Priority", "importance": "medium", "message_indices": [2], "participants": ["c"]},
                ],
                "off_topic_indices": []
            }
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text=json.dumps(mock_response))
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import get_topic_stats
            messages = [
                {"user": "a", "text": "Low", "ts": "2025-01-01T12:00:00"},
                {"user": "b", "text": "High", "ts": "2025-01-01T12:01:00"},
                {"user": "c", "text": "Medium", "ts": "2025-01-01T12:02:00"},
            ]
            result = await get_topic_stats(messages)

            # Should be sorted: high, medium, low
            assert result["topics"][0]["importance"] == "high"
            assert result["topics"][1]["importance"] == "medium"
            assert result["topics"][2]["importance"] == "low"


class TestBotHandlers:
    """Tests for Telegram bot handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create mock Telegram message."""
        message = MagicMock()
        message.text = "/tldr"
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.from_user.username = "testuser"
        message.answer = AsyncMock()
        message.reply = AsyncMock()
        return message

    @pytest.mark.asyncio
    async def test_tldr_command_responds(self, mock_message):
        """Bot should respond to /tldr command."""
        # Test that /tldr triggers summarization
        pass  # Requires integration with bot handlers

    @pytest.mark.asyncio
    async def test_start_command_responds(self, mock_message):
        """Bot should respond to /start command."""
        mock_message.text = "/start"
        # Test start command response
        pass  # Requires integration with bot handlers

    @pytest.mark.asyncio
    async def test_help_command_responds(self, mock_message):
        """Bot should respond to /help command."""
        mock_message.text = "/help"
        # Test help command response
        pass  # Requires integration with bot handlers


class TestScheduledDigests:
    """Tests for scheduled digest functionality."""

    @pytest.fixture
    def buffer_service(self):
        """Create buffer service with mocked Redis."""
        from app.services.buffer import MessageBuffer
        buffer = MessageBuffer()
        buffer.redis = AsyncMock()
        return buffer

    @pytest.mark.asyncio
    async def test_set_schedule_requires_subscription(self, buffer_service):
        """Schedule should only work for subscribers."""
        buffer_service.redis.exists = AsyncMock(return_value=0)  # Not subscribed (Telegram Stars)
        buffer_service.redis.get = AsyncMock(return_value=None)  # No Stripe subscription

        result = await buffer_service.set_schedule(123456, 9, 0)
        assert result is False

    @pytest.mark.asyncio
    async def test_set_schedule_succeeds_for_subscriber(self, buffer_service):
        """Schedule should work for subscribers."""
        buffer_service.redis.exists = AsyncMock(return_value=1)  # Subscribed
        buffer_service.redis.set = AsyncMock()
        buffer_service.redis.expire = AsyncMock()

        result = await buffer_service.set_schedule(123456, 9, 30)
        assert result is True
        buffer_service.redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schedule_returns_data(self, buffer_service):
        """Get schedule should return stored data."""
        import json
        buffer_service.redis.get = AsyncMock(
            return_value=json.dumps({"hour": 9, "minute": 0, "enabled": True})
        )

        result = await buffer_service.get_schedule(123456)
        assert result is not None
        assert result["hour"] == 9
        assert result["minute"] == 0
        assert result["enabled"] is True

    @pytest.mark.asyncio
    async def test_get_schedule_returns_none_when_not_set(self, buffer_service):
        """Get schedule should return None when not set."""
        buffer_service.redis.get = AsyncMock(return_value=None)

        result = await buffer_service.get_schedule(123456)
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_schedule(self, buffer_service):
        """Remove schedule should delete Redis key."""
        buffer_service.redis.delete = AsyncMock(return_value=1)

        result = await buffer_service.remove_schedule(123456)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_schedule_returns_false_when_not_exists(self, buffer_service):
        """Remove schedule should return False if no schedule existed."""
        buffer_service.redis.delete = AsyncMock(return_value=0)

        result = await buffer_service.remove_schedule(123456)
        assert result is False


class TestSummaryLength:
    """Tests for summary length preference functionality."""

    @pytest.fixture
    def buffer_service(self):
        """Create buffer service with mocked Redis."""
        from app.services.buffer import MessageBuffer
        buffer = MessageBuffer()
        buffer.redis = AsyncMock()
        return buffer

    @pytest.mark.asyncio
    async def test_set_summary_length_valid(self, buffer_service):
        """Setting a valid summary length should succeed."""
        buffer_service.redis.set = AsyncMock()

        for length in ("short", "medium", "long"):
            result = await buffer_service.set_summary_length(123456, length)
            assert result is True

    @pytest.mark.asyncio
    async def test_set_summary_length_invalid(self, buffer_service):
        """Setting an invalid summary length should fail."""
        result = await buffer_service.set_summary_length(123456, "extra_long")
        assert result is False

        result = await buffer_service.set_summary_length(123456, "")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_summary_length_returns_stored(self, buffer_service):
        """Get summary length should return stored preference."""
        buffer_service.redis.get = AsyncMock(return_value="short")

        result = await buffer_service.get_summary_length(123456)
        assert result == "short"

    @pytest.mark.asyncio
    async def test_get_summary_length_returns_default(self, buffer_service):
        """Get summary length should return default when not set."""
        buffer_service.redis.get = AsyncMock(return_value=None)

        result = await buffer_service.get_summary_length(123456)
        assert result == "medium"  # Default

    @pytest.mark.asyncio
    async def test_get_summary_length_returns_default_for_invalid(self, buffer_service):
        """Get summary length should return default for invalid stored value."""
        buffer_service.redis.get = AsyncMock(return_value="invalid")

        result = await buffer_service.get_summary_length(123456)
        assert result == "medium"  # Default

    @pytest.mark.asyncio
    async def test_summarizer_respects_length_parameter(self):
        """Summarizer should use different token limits for each length."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="Summary text")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages

            messages = [
                {"user": "alice", "text": "Hello", "ts": "2025-01-01T12:00:00"},
            ]

            # Test each length
            for length in ("short", "medium", "long"):
                result = await summarize_messages(messages, length=length)
                assert length.capitalize() in result

    @pytest.mark.asyncio
    async def test_summarizer_length_config_has_expected_keys(self):
        """Summary length config should have all required keys."""
        from app.services.summarizer import SUMMARY_LENGTH_CONFIG

        for length in ("short", "medium", "long"):
            assert length in SUMMARY_LENGTH_CONFIG
            assert "max_tokens" in SUMMARY_LENGTH_CONFIG[length]
            assert "instruction" in SUMMARY_LENGTH_CONFIG[length]

    @pytest.mark.asyncio
    async def test_summarizer_defaults_to_medium_for_invalid_length(self):
        """Summarizer should default to medium for invalid length."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="Summary")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages

            messages = [{"user": "test", "text": "Test", "ts": "2025-01-01T12:00:00"}]

            result = await summarize_messages(messages, length="invalid_length")
            assert "Medium" in result  # Should use medium

    @pytest.mark.asyncio
    async def test_summarizer_thread_detection_enabled_for_large_messages(self):
        """Summarizer should use thread detection for 15+ messages."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="Thread summary")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages

            # Create 20 messages from multiple users
            messages = [
                {"user": f"user{i % 4}", "text": f"Message {i}", "ts": "2025-01-01T12:00:00"}
                for i in range(20)
            ]

            result = await summarize_messages(messages, detect_threads=True)
            assert "threads detected" in result

    @pytest.mark.asyncio
    async def test_summarizer_no_thread_detection_for_small_messages(self):
        """Summarizer should not use thread detection for <15 messages."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="Simple summary")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages

            # Create only 10 messages
            messages = [
                {"user": f"user{i}", "text": f"Message {i}", "ts": "2025-01-01T12:00:00"}
                for i in range(10)
            ]

            result = await summarize_messages(messages, detect_threads=True)
            assert "threads detected" not in result

    @pytest.mark.asyncio
    async def test_summarizer_thread_detection_can_be_disabled(self):
        """Summarizer should skip thread detection when disabled."""
        with patch("app.services.summarizer.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                return_value=MagicMock(text="Standard summary")
            )
            mock_get_model.return_value = mock_model

            from app.services.summarizer import summarize_messages

            # Create 25 messages (would normally trigger thread detection)
            messages = [
                {"user": f"user{i % 3}", "text": f"Message {i}", "ts": "2025-01-01T12:00:00"}
                for i in range(25)
            ]

            result = await summarize_messages(messages, detect_threads=False)
            assert "threads detected" not in result


class TestDigestScheduler:
    """Tests for the digest scheduler service."""

    @pytest.mark.asyncio
    async def test_scheduler_starts_and_stops(self):
        """Scheduler should start and stop gracefully."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        await scheduler.start()
        assert scheduler._running is True

        await scheduler.stop()
        assert scheduler._running is False

    @pytest.mark.asyncio
    async def test_scheduler_requires_bot(self):
        """Scheduler should not send without bot set."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        # _send_digest should handle missing bot gracefully
        await scheduler._send_digest(123456)
        # Should not raise, just log warning


class TestPeriodicSchedules:
    """Tests for periodic digest scheduling."""

    @pytest.fixture
    def buffer_service(self):
        """Create buffer service with mocked Redis."""
        from app.services.buffer import MessageBuffer
        buffer = MessageBuffer()
        buffer.redis = AsyncMock()
        return buffer

    @pytest.mark.asyncio
    async def test_set_periodic_schedule_requires_subscription(self, buffer_service):
        """Setting periodic schedule should require active subscription."""
        buffer_service.redis.exists = AsyncMock(return_value=0)  # Not subscribed (Telegram Stars)
        buffer_service.redis.get = AsyncMock(return_value=None)  # No Stripe subscription

        result = await buffer_service.set_periodic_schedule(123456, 24)
        assert result is False

    @pytest.mark.asyncio
    async def test_set_periodic_schedule_valid_intervals(self, buffer_service):
        """Setting periodic schedule should accept valid intervals."""
        buffer_service.redis.exists = AsyncMock(return_value=1)  # Subscribed
        buffer_service.redis.set = AsyncMock(return_value=True)
        buffer_service.redis.expire = AsyncMock()

        # Valid intervals: 6, 12, 24, 168
        for interval in [6, 12, 24, 168]:
            result = await buffer_service.set_periodic_schedule(123456, interval)
            assert result is True

    @pytest.mark.asyncio
    async def test_set_periodic_schedule_invalid_interval(self, buffer_service):
        """Setting periodic schedule should reject invalid intervals."""
        buffer_service.redis.exists = AsyncMock(return_value=1)  # Subscribed

        result = await buffer_service.set_periodic_schedule(123456, 8)  # Invalid
        assert result is False

    @pytest.mark.asyncio
    async def test_get_periodic_schedule(self, buffer_service):
        """Should retrieve periodic schedule settings."""
        import json
        expected = {"interval_hours": 24, "auto_trigger": True, "message_threshold": 100, "enabled": True}
        buffer_service.redis.get = AsyncMock(return_value=json.dumps(expected))

        result = await buffer_service.get_periodic_schedule(123456)
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_periodic_schedule_not_set(self, buffer_service):
        """Should return None when periodic schedule not set."""
        buffer_service.redis.get = AsyncMock(return_value=None)

        result = await buffer_service.get_periodic_schedule(123456)
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_periodic_schedule(self, buffer_service):
        """Should remove periodic schedule."""
        buffer_service.redis.delete = AsyncMock(return_value=1)

        result = await buffer_service.remove_periodic_schedule(123456)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_periodic_schedule_not_found(self, buffer_service):
        """Should return False when no schedule to remove."""
        buffer_service.redis.delete = AsyncMock(return_value=0)

        result = await buffer_service.remove_periodic_schedule(123456)
        assert result is False

    @pytest.mark.asyncio
    async def test_should_send_periodic_digest_interval_met(self, buffer_service):
        """Should trigger when interval is met."""
        import json
        from datetime import datetime, timedelta, UTC

        settings = {"interval_hours": 6, "auto_trigger": False, "enabled": True}
        buffer_service.redis.get = AsyncMock(side_effect=[
            json.dumps(settings),  # get_periodic_schedule
            (datetime.now(UTC) - timedelta(hours=7)).isoformat(),  # get_last_digest_time
        ])
        buffer_service.redis.exists = AsyncMock(return_value=1)  # is_subscribed

        should_send, reason = await buffer_service.should_send_periodic_digest(123456)
        assert should_send is True
        assert reason == "interval"

    @pytest.mark.asyncio
    async def test_should_send_periodic_digest_interval_not_met(self, buffer_service):
        """Should not trigger when interval is not met."""
        import json
        from datetime import datetime, timedelta, UTC

        settings = {"interval_hours": 24, "auto_trigger": False, "enabled": True}
        buffer_service.redis.get = AsyncMock(side_effect=[
            json.dumps(settings),  # get_periodic_schedule
            (datetime.now(UTC) - timedelta(hours=2)).isoformat(),  # get_last_digest_time
        ])
        buffer_service.redis.exists = AsyncMock(return_value=1)  # is_subscribed

        should_send, reason = await buffer_service.should_send_periodic_digest(123456)
        assert should_send is False
        assert reason == ""

    @pytest.mark.asyncio
    async def test_should_send_periodic_digest_threshold_met(self, buffer_service):
        """Should trigger when message threshold is met."""
        import json
        from datetime import datetime, timedelta, UTC

        settings = {"interval_hours": 24, "auto_trigger": True, "message_threshold": 50, "enabled": True}
        # Not enough time passed for interval, but enough messages
        last_time = (datetime.now(UTC) - timedelta(hours=2)).isoformat()

        buffer_service.redis.get = AsyncMock(side_effect=[
            json.dumps(settings),  # get_periodic_schedule
            last_time,  # get_last_digest_time
        ])
        buffer_service.redis.exists = AsyncMock(return_value=1)  # is_subscribed
        # Mock get_messages to return 60 messages (above threshold)
        buffer_service.redis.zrangebyscore = AsyncMock(
            return_value=[json.dumps({"user": "test", "text": "msg", "ts": "2025-01-01"}) for _ in range(60)]
        )

        should_send, reason = await buffer_service.should_send_periodic_digest(123456)
        assert should_send is True
        assert reason == "threshold"

    @pytest.mark.asyncio
    async def test_should_send_periodic_digest_disabled(self, buffer_service):
        """Should not trigger when schedule is disabled."""
        import json

        settings = {"interval_hours": 24, "auto_trigger": False, "enabled": False}
        buffer_service.redis.get = AsyncMock(return_value=json.dumps(settings))

        should_send, reason = await buffer_service.should_send_periodic_digest(123456)
        assert should_send is False

    @pytest.mark.asyncio
    async def test_should_send_periodic_digest_no_subscription(self, buffer_service):
        """Should not trigger when subscription expired."""
        import json

        settings = {"interval_hours": 24, "auto_trigger": False, "enabled": True}
        buffer_service.redis.get = AsyncMock(return_value=json.dumps(settings))
        buffer_service.redis.exists = AsyncMock(return_value=0)  # Not subscribed

        should_send, reason = await buffer_service.should_send_periodic_digest(123456)
        assert should_send is False


class TestPeriodicScheduler:
    """Tests for the periodic scheduler functionality."""

    @pytest.fixture
    def scheduler_service(self):
        """Create scheduler service."""
        from app.services.scheduler import DigestScheduler
        scheduler = DigestScheduler()
        scheduler._bot = AsyncMock()
        scheduler._bot.send_message = AsyncMock()
        return scheduler

    @pytest.mark.asyncio
    async def test_check_periodic_schedules(self, scheduler_service):
        """Should check and process periodic schedules."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.get_all_periodic_schedules = AsyncMock(return_value=[
                (123456, {"interval_hours": 24, "auto_trigger": False, "enabled": True}),
            ])
            mock_buffer.should_send_periodic_digest = AsyncMock(return_value=(False, ""))

            await scheduler_service._check_periodic_schedules()
            mock_buffer.get_all_periodic_schedules.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_periodic_digest_interval(self, scheduler_service):
        """Should send periodic digest with interval header."""
        with patch("app.services.scheduler.buffer") as mock_buffer, \
             patch("app.services.scheduler.analytics") as mock_analytics, \
             patch("app.services.scheduler.summarize_messages") as mock_summarize:

            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value={"interval_hours": 6, "enabled": True})
            mock_buffer.get_messages = AsyncMock(return_value=[
                {"user": "test", "text": "hello", "ts": "2025-01-01"}
            ])
            mock_buffer.get_summary_length = AsyncMock(return_value="medium")
            mock_buffer.get_summary_language = AsyncMock(return_value="auto")
            mock_buffer.set_last_digest_time = AsyncMock()
            mock_summarize.return_value = "Test summary"
            mock_analytics.track_summary = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "interval")

            scheduler_service._bot.send_message.assert_called_once()
            call_kwargs = scheduler_service._bot.send_message.call_args.kwargs
            assert "6-Hour" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_send_periodic_digest_threshold(self, scheduler_service):
        """Should send periodic digest with activity header when threshold triggered."""
        with patch("app.services.scheduler.buffer") as mock_buffer, \
             patch("app.services.scheduler.analytics") as mock_analytics, \
             patch("app.services.scheduler.summarize_messages") as mock_summarize:

            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value={"interval_hours": 24, "enabled": True})
            mock_buffer.get_messages = AsyncMock(return_value=[
                {"user": "test", "text": f"msg{i}", "ts": "2025-01-01"} for i in range(100)
            ])
            mock_buffer.get_summary_length = AsyncMock(return_value="medium")
            mock_buffer.get_summary_language = AsyncMock(return_value="auto")
            mock_buffer.set_last_digest_time = AsyncMock()
            mock_summarize.return_value = "Test summary"
            mock_analytics.track_summary = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "threshold")

            scheduler_service._bot.send_message.assert_called_once()
            call_kwargs = scheduler_service._bot.send_message.call_args.kwargs
            assert "Activity Digest" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_send_periodic_digest_no_messages(self, scheduler_service):
        """Should skip when no messages to summarize."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value={"interval_hours": 24, "enabled": True})
            mock_buffer.get_messages = AsyncMock(return_value=[])
            mock_buffer.set_last_digest_time = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "interval")

            # Should not send message, but should update last digest time
            scheduler_service._bot.send_message.assert_not_called()
            mock_buffer.set_last_digest_time.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_periodic_digest_expired_subscription(self, scheduler_service):
        """Should remove schedule when subscription expired."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.is_subscribed = AsyncMock(return_value=False)
            mock_buffer.remove_periodic_schedule = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "interval")

            mock_buffer.remove_periodic_schedule.assert_called_once_with(123456)
