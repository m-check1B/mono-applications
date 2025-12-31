"""Extended tests for scheduler.py to improve test coverage."""
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest


class TestDigestSchedulerExtended:
    """Extended tests for DigestScheduler to cover missing lines."""

    @pytest.fixture
    def scheduler_service(self):
        """Create scheduler service with mocked bot."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        scheduler._bot = AsyncMock()
        scheduler._bot.send_message = AsyncMock()
        scheduler._bot.send_audio = AsyncMock()
        return scheduler

    @pytest.mark.asyncio
    async def test_send_digest_without_bot(self):
        """Should warn and return when bot is not set."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        # Bot not set
        await scheduler._send_digest(123456)
        # Should not raise, just log warning

    @pytest.mark.asyncio
    async def test_send_digest_subscription_expired(self, scheduler_service):
        """Should remove schedule when subscription expired."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.is_subscribed = AsyncMock(return_value=False)
            mock_buffer.remove_schedule = AsyncMock()

            await scheduler_service._send_digest(123456)

            mock_buffer.remove_schedule.assert_called_once_with(123456)
            scheduler_service._bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_digest_no_messages(self, scheduler_service):
        """Should skip silently when no messages."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(return_value=[])

            await scheduler_service._send_digest(123456)

            scheduler_service._bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_digest_success(self, scheduler_service):
        """Should send digest successfully."""
        with (
            patch("app.services.scheduler.buffer") as mock_buffer,
            patch("app.services.scheduler.analytics") as mock_analytics,
            patch("app.services.scheduler.summarize_messages") as mock_summarize,
        ):
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hello", "ts": "2025-01-01"}]
            )
            mock_summarize.return_value = "Test summary"
            mock_analytics.track_summary = AsyncMock()

            await scheduler_service._send_digest(123456)

            scheduler_service._bot.send_message.assert_called_once()
            call_kwargs = scheduler_service._bot.send_message.call_args.kwargs
            assert "Daily Digest" in call_kwargs["text"]
            mock_analytics.track_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_digest_handles_error(self, scheduler_service):
        """Should handle errors gracefully."""
        with (
            patch("app.services.scheduler.buffer") as mock_buffer,
            patch("app.services.scheduler.analytics") as mock_analytics,
            patch("app.services.scheduler.summarize_messages") as mock_summarize,
        ):
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hello", "ts": "2025-01-01"}]
            )
            mock_summarize.side_effect = Exception("API error")
            mock_analytics.track_error = AsyncMock()

            await scheduler_service._send_digest(123456)

            mock_analytics.track_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_and_send_skips_same_minute(self, scheduler_service):
        """Should skip if already ran this minute."""
        scheduler_service._last_run_minute = (
            datetime.now(UTC).hour * 60 + datetime.now(UTC).minute
        )

        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.get_all_schedules = AsyncMock()

            await scheduler_service._check_and_send()

            mock_buffer.get_all_schedules.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_and_send_runs_at_scheduled_time(self, scheduler_service):
        """Should send digest at scheduled time."""
        scheduler_service._last_run_minute = -1

        now = datetime.now(UTC)
        current_minute = now.hour * 60 + now.minute

        with (
            patch("app.services.scheduler.buffer") as mock_buffer,
            patch.object(scheduler_service, "_send_digest") as mock_send,
            patch.object(
                scheduler_service, "_check_periodic_schedules"
            ) as mock_periodic,
            patch.object(
                scheduler_service, "_check_newsletter_schedules"
            ) as mock_newsletter,
        ):
            mock_buffer.get_all_schedules = AsyncMock(
                return_value=[
                    (123456, {"hour": now.hour, "minute": now.minute}),
                ]
            )
            mock_periodic.return_value = None
            mock_newsletter.return_value = None

            await scheduler_service._check_and_send()

            mock_send.assert_called_once_with(123456)

    @pytest.mark.asyncio
    async def test_check_newsletter_schedules_without_bot(self, scheduler_service):
        """Should return early when bot not set."""
        scheduler_service._bot = None

        await scheduler_service._check_newsletter_schedules()
        # Should not raise

    @pytest.mark.asyncio
    async def test_check_newsletter_schedules_at_time(self, scheduler_service):
        """Should send newsletter at scheduled time."""
        now = datetime.now(UTC)

        with (
            patch("app.services.scheduler.news_aggregator") as mock_aggregator,
            patch.object(scheduler_service, "_send_newsletter") as mock_send,
        ):
            mock_aggregator.get_all_newsletter_subscribers = AsyncMock(
                return_value=[
                    (12345, ["tech", "crypto"], (now.hour, now.minute)),
                ]
            )

            await scheduler_service._check_newsletter_schedules()

            mock_send.assert_called_once_with(12345, ["tech", "crypto"])

    @pytest.mark.asyncio
    async def test_check_newsletter_schedules_skips_no_time(self, scheduler_service):
        """Should skip subscribers without delivery time."""
        with (
            patch("app.services.scheduler.news_aggregator") as mock_aggregator,
            patch.object(scheduler_service, "_send_newsletter") as mock_send,
        ):
            mock_aggregator.get_all_newsletter_subscribers = AsyncMock(
                return_value=[
                    (12345, ["tech"], None),  # No delivery time
                ]
            )

            await scheduler_service._check_newsletter_schedules()

            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_newsletter_without_bot(self):
        """Should warn when bot not set."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        await scheduler._send_newsletter(12345, ["tech"])
        # Should not raise

    @pytest.mark.asyncio
    async def test_send_newsletter_success(self, scheduler_service):
        """Should send newsletter text and audio."""
        with patch("app.services.scheduler.newsletter") as mock_newsletter:
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={
                    "text": "Newsletter content",
                    "audio_path": "/tmp/audio.mp3",
                }
            )

            with patch("app.services.scheduler.FSInputFile") as mock_input:
                mock_input.return_value = MagicMock()

                await scheduler_service._send_newsletter(12345, ["tech"])

                scheduler_service._bot.send_message.assert_called_once()
                scheduler_service._bot.send_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_newsletter_no_content(self, scheduler_service):
        """Should skip when no newsletter content."""
        with patch("app.services.scheduler.newsletter") as mock_newsletter:
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={"text": None}
            )

            await scheduler_service._send_newsletter(12345, ["tech"])

            scheduler_service._bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_newsletter_text_only(self, scheduler_service):
        """Should send text only when no audio."""
        with patch("app.services.scheduler.newsletter") as mock_newsletter:
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={
                    "text": "Newsletter content",
                    "audio_path": None,
                }
            )

            await scheduler_service._send_newsletter(12345, ["tech"])

            scheduler_service._bot.send_message.assert_called_once()
            scheduler_service._bot.send_audio.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_newsletter_handles_audio_error(self, scheduler_service):
        """Should handle audio send errors gracefully."""
        with patch("app.services.scheduler.newsletter") as mock_newsletter:
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={
                    "text": "Newsletter content",
                    "audio_path": "/tmp/audio.mp3",
                }
            )

            scheduler_service._bot.send_audio = AsyncMock(
                side_effect=Exception("Audio error")
            )

            with patch("app.services.scheduler.FSInputFile"):
                await scheduler_service._send_newsletter(12345, ["tech"])

            # Text should still be sent
            scheduler_service._bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_newsletter_handles_error(self, scheduler_service):
        """Should handle newsletter generation errors."""
        with (
            patch("app.services.scheduler.newsletter") as mock_newsletter,
            patch("app.services.scheduler.analytics") as mock_analytics,
        ):
            mock_newsletter.generate_newsletter = AsyncMock(
                side_effect=Exception("Generation error")
            )
            mock_analytics.track_error = AsyncMock()

            await scheduler_service._send_newsletter(12345, ["tech"])

            mock_analytics.track_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_loop_handles_errors(self, scheduler_service):
        """Should handle errors in run loop gracefully."""
        scheduler_service._running = True

        with (
            patch("app.services.scheduler.analytics") as mock_analytics,
            patch.object(
                scheduler_service, "_check_and_send"
            ) as mock_check,
            patch("asyncio.sleep") as mock_sleep,
        ):
            # First call raises error, second call normal, third stops
            call_count = 0

            async def check_side_effect():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Check error")
                scheduler_service._running = False

            mock_check.side_effect = check_side_effect
            mock_analytics.track_error = AsyncMock()
            mock_sleep.return_value = None

            await scheduler_service._run_loop()

            mock_analytics.track_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_periodic_digest_no_settings(self, scheduler_service):
        """Should return when no periodic settings found."""
        with patch("app.services.scheduler.buffer") as mock_buffer:
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value=None)

            await scheduler_service._send_periodic_digest(123456, "interval")

            scheduler_service._bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_periodic_digest_weekly_header(self, scheduler_service):
        """Should use Weekly header for 168h interval."""
        with (
            patch("app.services.scheduler.buffer") as mock_buffer,
            patch("app.services.scheduler.analytics") as mock_analytics,
            patch("app.services.scheduler.summarize_messages") as mock_summarize,
        ):
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(
                return_value={"interval_hours": 168, "enabled": True}
            )
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hello", "ts": "2025-01-01"}]
            )
            mock_buffer.get_summary_length = AsyncMock(return_value="medium")
            mock_buffer.get_summary_language = AsyncMock(return_value="auto")
            mock_buffer.set_last_digest_time = AsyncMock()
            mock_summarize.return_value = "Test summary"
            mock_analytics.track_summary = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "interval")

            call_kwargs = scheduler_service._bot.send_message.call_args.kwargs
            assert "Weekly" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_send_periodic_digest_handles_error(self, scheduler_service):
        """Should handle errors in periodic digest gracefully."""
        with (
            patch("app.services.scheduler.buffer") as mock_buffer,
            patch("app.services.scheduler.analytics") as mock_analytics,
            patch("app.services.scheduler.summarize_messages") as mock_summarize,
        ):
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(
                return_value={"interval_hours": 24, "enabled": True}
            )
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hello", "ts": "2025-01-01"}]
            )
            mock_buffer.get_summary_length = AsyncMock(return_value="medium")
            mock_buffer.get_summary_language = AsyncMock(return_value="auto")
            mock_summarize.side_effect = Exception("Summarize error")
            mock_analytics.track_error = AsyncMock()

            await scheduler_service._send_periodic_digest(123456, "interval")

            mock_analytics.track_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_periodic_digest_without_bot(self):
        """Should warn when bot not set for periodic digest."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        await scheduler._send_periodic_digest(123456, "interval")
        # Should not raise


class TestSchedulerStartStop:
    """Tests for scheduler start/stop lifecycle."""

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Should not start if already running."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        scheduler._running = True

        await scheduler.start()
        # Should not create another task if already running

    @pytest.mark.asyncio
    async def test_stop_cancels_task(self):
        """Should cancel task when stopping."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        await scheduler.start()
        assert scheduler._running is True
        assert scheduler._task is not None

        await scheduler.stop()
        assert scheduler._running is False

    @pytest.mark.asyncio
    async def test_set_bot(self):
        """Should set bot instance."""
        from app.services.scheduler import DigestScheduler

        scheduler = DigestScheduler()
        mock_bot = MagicMock()

        scheduler.set_bot(mock_bot)

        assert scheduler._bot is mock_bot
