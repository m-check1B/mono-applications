"""Scheduled digest service."""

import asyncio
import logging
from datetime import UTC, datetime

from aiogram.types import FSInputFile

from app.services.analytics import analytics
from app.services.buffer import buffer
from app.services.news_aggregator import news_aggregator
from app.services.newsletter import newsletter
from app.services.summarizer import summarize_messages

logger = logging.getLogger(__name__)


class DigestScheduler:
    """Handles sending scheduled daily digests to subscribed chats."""

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        self._bot = None
        self._last_run_minute: int = -1

    def set_bot(self, bot):
        """Set the bot instance for sending messages."""
        self._bot = bot

    async def start(self):
        """Start the scheduler background task."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Digest scheduler started")

    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Digest scheduler stopped")

    async def _run_loop(self):
        """Main scheduler loop - checks every minute."""
        while self._running:
            try:
                await self._check_and_send()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await analytics.track_error("scheduler", str(e))

            # Wait 60 seconds before next check
            await asyncio.sleep(60)

    async def _check_and_send(self):
        """Check schedules and send digests for matching times."""
        now = datetime.now(UTC)
        current_minute = now.hour * 60 + now.minute

        # Avoid running twice in the same minute
        if current_minute == self._last_run_minute:
            return
        self._last_run_minute = current_minute

        # Check fixed-time daily digest schedules
        schedules = await buffer.get_all_schedules()

        for chat_id, schedule in schedules:
            schedule_minute = schedule["hour"] * 60 + schedule["minute"]

            if current_minute == schedule_minute:
                # Time to send digest
                await self._send_digest(chat_id)

        # Check periodic interval-based schedules
        await self._check_periodic_schedules()

        # Check newsletter schedules
        await self._check_newsletter_schedules()

    async def _check_periodic_schedules(self):
        """Check periodic schedules and send digests when intervals are met."""
        periodic_schedules = await buffer.get_all_periodic_schedules()

        for chat_id, settings in periodic_schedules:
            should_send, reason = await buffer.should_send_periodic_digest(chat_id)

            if should_send:
                await self._send_periodic_digest(chat_id, reason)

    async def _send_periodic_digest(self, chat_id: int, trigger_reason: str):
        """Send periodic digest to a chat.

        Args:
            chat_id: Telegram chat ID
            trigger_reason: 'interval' or 'threshold'
        """
        if not self._bot:
            logger.warning("Bot not set, cannot send periodic digest")
            return

        # Verify subscription is still active
        if not await buffer.is_subscribed(chat_id):
            await buffer.remove_periodic_schedule(chat_id)
            logger.info(f"Removed expired periodic schedule for chat {chat_id}")
            return

        try:
            # Get settings for interval
            settings = await buffer.get_periodic_schedule(chat_id)
            if not settings:
                return

            hours = settings.get("interval_hours", 24)

            # Get messages from the interval period
            messages = await buffer.get_messages(chat_id, hours=hours)

            if not messages:
                # No messages to summarize
                # Still update last digest time to avoid immediate re-trigger
                await buffer.set_last_digest_time(chat_id)
                return

            # Get user preferences
            length_pref = await buffer.get_summary_length(chat_id)
            lang_pref = await buffer.get_summary_language(chat_id)

            # Generate summary
            summary = await summarize_messages(messages, length=length_pref, language=lang_pref)

            # Determine header based on trigger
            if trigger_reason == "threshold":
                header = f"**🔔 Activity Digest** ({len(messages)} messages)"
            else:
                interval_names = {6: "6-Hour", 12: "12-Hour", 24: "Daily", 168: "Weekly"}
                interval_name = interval_names.get(hours, f"{hours}h")
                header = f"**📅 {interval_name} Digest**"

            # Send to chat
            await self._bot.send_message(
                chat_id=chat_id, text=f"{header}\n\n{summary}", parse_mode="Markdown"
            )

            # Update last digest time
            await buffer.set_last_digest_time(chat_id)

            # Track analytics
            await analytics.track_summary(chat_id, 0, len(messages))
            logger.info(f"Sent periodic digest to chat {chat_id} (trigger: {trigger_reason})")

        except Exception as e:
            logger.error(f"Failed to send periodic digest to chat {chat_id}: {e}")
            await analytics.track_error("periodic_digest", str(e))

    async def _send_digest(self, chat_id: int):
        """Send scheduled digest to a chat."""
        if not self._bot:
            logger.warning("Bot not set, cannot send scheduled digest")
            return

        # Verify subscription is still active
        if not await buffer.is_subscribed(chat_id):
            # Subscription expired, remove schedule
            await buffer.remove_schedule(chat_id)
            logger.info(f"Removed expired schedule for chat {chat_id}")
            return

        try:
            # Get messages from last 24 hours
            messages = await buffer.get_messages(chat_id, hours=24)

            if not messages:
                # No messages to summarize, skip silently
                return

            # Generate summary
            summary = await summarize_messages(messages)

            # Send to chat
            await self._bot.send_message(
                chat_id=chat_id, text=f"**Daily Digest**\n\n{summary}", parse_mode="Markdown"
            )

            # Track analytics
            await analytics.track_summary(chat_id, 0, len(messages))
            logger.info(f"Sent scheduled digest to chat {chat_id}")

        except Exception as e:
            logger.error(f"Failed to send digest to chat {chat_id}: {e}")
            await analytics.track_error("scheduled_digest", str(e))

    async def _check_newsletter_schedules(self):
        """Check and send newsletters for matching times."""
        if not self._bot:
            return

        now = datetime.now(UTC)
        current_minute = now.hour * 60 + now.minute

        # Get all newsletter subscribers
        subscribers = await news_aggregator.get_all_newsletter_subscribers()

        for user_id, topics, delivery_time in subscribers:
            if not delivery_time:
                continue

            schedule_minute = delivery_time[0] * 60 + delivery_time[1]

            if current_minute == schedule_minute:
                # Time to send newsletter
                await self._send_newsletter(user_id, topics)

    async def _send_newsletter(self, user_id: int, topics: list[str]):
        """Send newsletter to user."""
        if not self._bot:
            logger.warning("Bot not set, cannot send newsletter")
            return

        try:
            # Generate newsletter
            result = await newsletter.generate_newsletter(topics, include_audio=True)

            if not result.get("text"):
                logger.warning(f"No newsletter content for user {user_id} topics {topics}")
                return

            # Send text digest
            await self._bot.send_message(
                chat_id=user_id, text=result["text"], parse_mode="Markdown"
            )

            # Send audio if available
            audio_path = result.get("audio_path")
            if audio_path:
                try:
                    audio_file = FSInputFile(audio_path)
                    await self._bot.send_audio(
                        chat_id=user_id, audio=audio_file, caption="🎧 Your daily newsletter audio"
                    )
                except Exception as e:
                    logger.error(f"Failed to send newsletter audio to user {user_id}: {e}")

            logger.info(f"Sent newsletter to user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send newsletter to user {user_id}: {e}")
            await analytics.track_error("newsletter_delivery", str(e))


# Global instance
scheduler = DigestScheduler()
