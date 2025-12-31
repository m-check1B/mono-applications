"""Message buffer service using Redis."""

import json
from datetime import datetime, timedelta, UTC

import redis.asyncio as redis

from app.core.config import settings


class MessageBuffer:
    """Store and retrieve chat messages for summarization."""

    def __init__(self):
        self.redis: redis.Redis | None = None
        self.buffer_hours = settings.message_buffer_hours
        self.max_messages = settings.max_messages_per_summary

    async def connect(self):
        """Initialize Redis connection."""
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    def _key(self, chat_id: int) -> str:
        """Generate Redis key for a chat."""
        return f"tldr:chat:{chat_id}:messages"

    def _usage_key(self, chat_id: int) -> str:
        """Generate Redis key for usage tracking."""
        return f"tldr:chat:{chat_id}:usage"

    def _sub_key(self, chat_id: int) -> str:
        """Generate Redis key for subscription status."""
        return f"tldr:chat:{chat_id}:subscription"

    def _schedule_key(self, chat_id: int) -> str:
        """Generate Redis key for scheduled digest preferences."""
        return f"tldr:chat:{chat_id}:schedule"

    def _periodic_key(self, chat_id: int) -> str:
        """Generate Redis key for periodic digest settings."""
        return f"tldr:chat:{chat_id}:periodic"

    def _last_digest_key(self, chat_id: int) -> str:
        """Generate Redis key for last digest timestamp."""
        return f"tldr:chat:{chat_id}:last_digest"

    def _length_key(self, chat_id: int) -> str:
        """Generate Redis key for summary length preference."""
        return f"tldr:chat:{chat_id}:length"

    def _language_key(self, chat_id: int) -> str:
        """Generate Redis key for summary language preference."""
        return f"tldr:chat:{chat_id}:language"

    def _stripe_sub_key(self, chat_id: int) -> str:
        """Generate Redis key for Stripe subscription tracking."""
        return f"tldr:chat:{chat_id}:stripe_subscription"

    async def add_message(
        self, chat_id: int, user_name: str, text: str, timestamp: datetime | None = None
    ):
        """Add a message to the buffer."""
        if not self.redis:
            return

        ts = timestamp or datetime.now(UTC)
        message = json.dumps({"user": user_name, "text": text, "ts": ts.isoformat()})

        key = self._key(chat_id)

        # Add message with score as timestamp
        await self.redis.zadd(key, {message: ts.timestamp()})

        # Set TTL to auto-expire old messages
        await self.redis.expire(key, self.buffer_hours * 3600)

        # Trim to max messages (keep newest)
        await self.redis.zremrangebyrank(key, 0, -self.max_messages - 1)

    async def get_messages(self, chat_id: int, hours: int | None = None) -> list[dict]:
        """Get messages from buffer within time window."""
        if not self.redis:
            return []

        key = self._key(chat_id)
        hours = hours or self.buffer_hours

        # Calculate time window
        min_ts = (datetime.now(UTC) - timedelta(hours=hours)).timestamp()

        # Get messages in time range
        messages = await self.redis.zrangebyscore(key, min_ts, "+inf")

        return [json.loads(m) for m in messages]

    async def get_usage_count(self, chat_id: int) -> int:
        """Get number of summaries used by a chat."""
        if not self.redis:
            return 0

        count = await self.redis.get(self._usage_key(chat_id))
        return int(count) if count else 0

    async def increment_usage(self, chat_id: int) -> int:
        """Increment usage counter, returns new count."""
        if not self.redis:
            return 0

        key = self._usage_key(chat_id)
        count = await self.redis.incr(key)

        # Reset monthly (set expiry to end of month)
        await self.redis.expire(key, 30 * 24 * 3600)

        return count

    async def is_subscribed(self, chat_id: int) -> bool:
        """Check if chat has active subscription.

        Checks both Telegram Stars and Stripe subscriptions.
        """
        if not self.redis:
            return False

        # Check Telegram Stars subscription
        if await self.redis.exists(self._sub_key(chat_id)) > 0:
            return True

        # Check Stripe subscription
        stripe_sub = await self.get_stripe_subscription(chat_id)
        if stripe_sub and stripe_sub.get("status") in ("active", "trialing"):
            return True

        return False

    async def set_subscribed(self, chat_id: int, months: int = 1):
        """Set chat as subscribed."""
        if not self.redis:
            return

        key = self._sub_key(chat_id)
        await self.redis.set(key, "active")
        await self.redis.expire(key, months * 30 * 24 * 3600)

    async def can_summarize(self, chat_id: int) -> tuple[bool, str]:
        """Check if chat can request a summary.

        Returns (allowed, reason).
        """
        # Check subscription first
        if await self.is_subscribed(chat_id):
            return True, "subscribed"

        # Check free tier
        usage = await self.get_usage_count(chat_id)
        if usage < settings.free_summaries:
            remaining = settings.free_summaries - usage
            return True, f"free_tier:{remaining}"

        return False, "limit_reached"

    async def set_schedule(self, chat_id: int, hour: int, minute: int) -> bool:
        """Set scheduled digest time for a chat. Requires active subscription."""
        if not self.redis:
            return False

        # Only subscribers can use scheduled digests
        if not await self.is_subscribed(chat_id):
            return False

        key = self._schedule_key(chat_id)
        schedule_data = json.dumps({"hour": hour, "minute": minute, "enabled": True})
        await self.redis.set(key, schedule_data)
        # Schedule expires with subscription (30 days)
        await self.redis.expire(key, 30 * 24 * 3600)
        return True

    async def remove_schedule(self, chat_id: int) -> bool:
        """Remove scheduled digest for a chat."""
        if not self.redis:
            return False

        key = self._schedule_key(chat_id)
        deleted = await self.redis.delete(key)
        return deleted > 0

    async def get_schedule(self, chat_id: int) -> dict | None:
        """Get scheduled digest settings for a chat."""
        if not self.redis:
            return None

        key = self._schedule_key(chat_id)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def get_all_schedules(self) -> list[tuple[int, dict]]:
        """Get all scheduled digests. Returns list of (chat_id, schedule_data)."""
        if not self.redis:
            return []

        # Scan for all schedule keys
        schedules = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match="tldr:chat:*:schedule", count=100)
            for key in keys:
                # Extract chat_id from key
                parts = key.split(":")
                if len(parts) >= 3:
                    try:
                        chat_id = int(parts[2])
                        data = await self.redis.get(key)
                        if data:
                            schedule = json.loads(data)
                            if schedule.get("enabled"):
                                schedules.append((chat_id, schedule))
                    except (ValueError, json.JSONDecodeError):
                        continue
            if cursor == 0:
                break

        return schedules

    async def set_summary_length(self, chat_id: int, length: str) -> bool:
        """Set preferred summary length for a chat.

        Args:
            chat_id: Telegram chat ID
            length: One of 'short', 'medium', 'long'

        Returns:
            True if set successfully, False otherwise
        """
        if not self.redis:
            return False

        valid_lengths = ("short", "medium", "long")
        if length not in valid_lengths:
            return False

        key = self._length_key(chat_id)
        await self.redis.set(key, length)
        return True

    async def get_summary_length(self, chat_id: int) -> str:
        """Get preferred summary length for a chat.

        Returns:
            Length preference ('short', 'medium', 'long') or default
        """
        if not self.redis:
            return settings.default_summary_length

        key = self._length_key(chat_id)
        length = await self.redis.get(key)
        if length in ("short", "medium", "long"):
            return length
        return settings.default_summary_length

    async def set_summary_language(self, chat_id: int, language: str) -> bool:
        """Set preferred summary language for a chat.

        Args:
            chat_id: Telegram chat ID
            language: Language code ('auto', 'en', 'cs', 'de', etc.)

        Returns:
            True if set successfully, False otherwise
        """
        if not self.redis:
            return False

        key = self._language_key(chat_id)
        await self.redis.set(key, language)
        return True

    async def get_summary_language(self, chat_id: int) -> str:
        """Get preferred summary language for a chat.

        Returns:
            Language code or 'auto' for auto-detection
        """
        if not self.redis:
            return "auto"

        key = self._language_key(chat_id)
        language = await self.redis.get(key)
        return language if language else "auto"

    # ============================================================
    # STRIPE SUBSCRIPTION TRACKING
    # ============================================================

    async def set_stripe_subscription(
        self, chat_id: int, subscription_id: str, status: str = "active"
    ) -> bool:
        """Store Stripe subscription information.

        Args:
            chat_id: Telegram chat ID
            subscription_id: Stripe subscription ID
            status: Subscription status (active, canceled, past_due, etc.)

        Returns:
            True if set successfully
        """
        if not self.redis:
            return False

        key = self._stripe_sub_key(chat_id)
        sub_data = json.dumps(
            {
                "subscription_id": subscription_id,
                "status": status,
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        await self.redis.set(key, sub_data)

        return True

    async def get_stripe_subscription(self, chat_id: int) -> dict | None:
        """Get Stripe subscription information for a chat.

        Args:
            chat_id: Telegram chat ID

        Returns:
            Dict with subscription_id, status, created_at or None
        """
        if not self.redis:
            return None

        key = self._stripe_sub_key(chat_id)
        data = await self.redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def delete_stripe_subscription(self, chat_id: int) -> bool:
        """Delete Stripe subscription information for a chat.

        Args:
            chat_id: Telegram chat ID

        Returns:
            True if deleted
        """
        if not self.redis:
            return False

        key = self._stripe_sub_key(chat_id)
        deleted = await self.redis.delete(key)
        return deleted > 0

    # ============================================================
    # PERIODIC SUMMARIES
    # ============================================================

    async def set_periodic_schedule(
        self,
        chat_id: int,
        interval_hours: int,
        auto_trigger: bool = False,
        message_threshold: int = 100,
    ) -> bool:
        """Set periodic digest schedule for a chat.

        Args:
            chat_id: Telegram chat ID
            interval_hours: Hours between digests (6, 12, 24, 168 for weekly)
            auto_trigger: If True, also trigger when message count exceeds threshold
            message_threshold: Number of messages to trigger auto-digest (when auto_trigger=True)

        Returns:
            True if set successfully, False otherwise
        """
        if not self.redis:
            return False

        # Only subscribers can use periodic digests
        if not await self.is_subscribed(chat_id):
            return False

        valid_intervals = (6, 12, 24, 168)  # 6h, 12h, daily, weekly
        if interval_hours not in valid_intervals:
            return False

        key = self._periodic_key(chat_id)
        periodic_data = json.dumps(
            {
                "interval_hours": interval_hours,
                "auto_trigger": auto_trigger,
                "message_threshold": message_threshold,
                "enabled": True,
            }
        )
        await self.redis.set(key, periodic_data)
        # Expires with subscription (30 days)
        await self.redis.expire(key, 30 * 24 * 3600)

        # Set last digest to now so first one fires after interval
        await self.set_last_digest_time(chat_id)

        return True

    async def get_periodic_schedule(self, chat_id: int) -> dict | None:
        """Get periodic digest settings for a chat."""
        if not self.redis:
            return None

        key = self._periodic_key(chat_id)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def remove_periodic_schedule(self, chat_id: int) -> bool:
        """Remove periodic digest schedule for a chat."""
        if not self.redis:
            return False

        key = self._periodic_key(chat_id)
        deleted = await self.redis.delete(key)
        return deleted > 0

    async def get_all_periodic_schedules(self) -> list[tuple[int, dict]]:
        """Get all periodic digest schedules. Returns list of (chat_id, settings)."""
        if not self.redis:
            return []

        schedules = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match="tldr:chat:*:periodic", count=100)
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 3:
                    try:
                        chat_id = int(parts[2])
                        data = await self.redis.get(key)
                        if data:
                            settings = json.loads(data)
                            if settings.get("enabled"):
                                schedules.append((chat_id, settings))
                    except (ValueError, json.JSONDecodeError):
                        continue
            if cursor == 0:
                break

        return schedules

    async def set_last_digest_time(self, chat_id: int) -> None:
        """Record when the last periodic digest was sent."""
        if not self.redis:
            return

        key = self._last_digest_key(chat_id)
        await self.redis.set(key, datetime.now(UTC).isoformat())
        await self.redis.expire(key, 30 * 24 * 3600)

    async def get_last_digest_time(self, chat_id: int) -> datetime | None:
        """Get timestamp of last periodic digest."""
        if not self.redis:
            return None

        key = self._last_digest_key(chat_id)
        data = await self.redis.get(key)
        if data:
            dt = datetime.fromisoformat(data)
            # Ensure timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        return None

    async def should_send_periodic_digest(self, chat_id: int) -> tuple[bool, str]:
        """Check if periodic digest should be sent now.

        Returns:
            (should_send, reason) where reason is 'interval' or 'threshold' or ''
        """
        settings = await self.get_periodic_schedule(chat_id)
        if not settings or not settings.get("enabled"):
            return False, ""

        # Check subscription still active
        if not await self.is_subscribed(chat_id):
            return False, ""

        interval_hours = settings["interval_hours"]
        last_digest = await self.get_last_digest_time(chat_id)

        # Check interval-based trigger
        if last_digest:
            hours_since = (datetime.now(UTC) - last_digest).total_seconds() / 3600
            if hours_since >= interval_hours:
                return True, "interval"
        else:
            # No last digest recorded, set it and skip this cycle
            await self.set_last_digest_time(chat_id)
            return False, ""

        # Check activity-based trigger (if enabled)
        if settings.get("auto_trigger"):
            threshold = settings.get("message_threshold", 100)
            messages = await self.get_messages(chat_id, hours=interval_hours)
            if len(messages) >= threshold:
                return True, "threshold"

        return False, ""


# Global instance
buffer = MessageBuffer()
