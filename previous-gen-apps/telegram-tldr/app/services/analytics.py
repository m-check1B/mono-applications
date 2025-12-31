"""Usage analytics service for tracking bot metrics in Redis."""

import json
from datetime import UTC, datetime

import redis.asyncio as redis

from app.core.config import settings


class Analytics:
    """Track and retrieve bot usage analytics stored in Redis."""

    # Redis key prefixes
    PREFIX = "tldr:analytics"

    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        """Initialize Redis connection."""
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    def _key(self, metric: str) -> str:
        """Generate Redis key for a metric."""
        return f"{self.PREFIX}:{metric}"

    def _daily_key(self, metric: str, date: datetime | None = None) -> str:
        """Generate Redis key for daily metrics."""
        date = date or datetime.now(UTC)
        date_str = date.strftime("%Y-%m-%d")
        return f"{self.PREFIX}:daily:{date_str}:{metric}"

    def _extract_chat_id(self, key: str) -> int | None:
        """Extract chat_id from Redis key (tldr:chat:{chat_id}:...)."""
        parts = key.split(":")
        if len(parts) < 3:
            return None
        try:
            return int(parts[2])
        except ValueError:
            return None

    # ============================================================
    # TRACKING METHODS
    # ============================================================

    async def track_message(self, chat_id: int, user_id: int):
        """Track a message being processed."""
        if not self.redis:
            return

        pipe = self.redis.pipeline()

        # Increment total messages
        pipe.incr(self._key("messages:total"))

        # Increment daily messages
        pipe.incr(self._daily_key("messages"))
        pipe.expire(self._daily_key("messages"), 90 * 24 * 3600)  # 90 days retention

        # Track unique users (daily)
        pipe.sadd(self._daily_key("users"), str(user_id))
        pipe.expire(self._daily_key("users"), 90 * 24 * 3600)

        # Track active chats (daily)
        pipe.sadd(self._daily_key("chats"), str(chat_id))
        pipe.expire(self._daily_key("chats"), 90 * 24 * 3600)

        # Track all-time unique users and chats
        pipe.sadd(self._key("users:all"), str(user_id))
        pipe.sadd(self._key("chats:all"), str(chat_id))

        await pipe.execute()

    async def track_summary(self, chat_id: int, user_id: int, message_count: int):
        """Track a summary being generated."""
        if not self.redis:
            return

        pipe = self.redis.pipeline()

        # Increment total summaries
        pipe.incr(self._key("summaries:total"))

        # Increment daily summaries
        pipe.incr(self._daily_key("summaries"))
        pipe.expire(self._daily_key("summaries"), 90 * 24 * 3600)

        # Track messages summarized
        pipe.incrby(self._key("messages:summarized"), message_count)
        pipe.incrby(self._daily_key("messages:summarized"), message_count)
        pipe.expire(self._daily_key("messages:summarized"), 90 * 24 * 3600)

        await pipe.execute()

    async def track_error(self, error_type: str, details: str = ""):
        """Track an error occurrence."""
        if not self.redis:
            return

        pipe = self.redis.pipeline()

        # Increment total errors
        pipe.incr(self._key("errors:total"))

        # Increment daily errors
        pipe.incr(self._daily_key("errors"))
        pipe.expire(self._daily_key("errors"), 90 * 24 * 3600)

        # Track error by type
        pipe.incr(self._key(f"errors:type:{error_type}"))

        # Log last 100 errors with details
        error_log = json.dumps(
            {
                "type": error_type,
                "details": details[:500],  # Limit details length
                "ts": datetime.now(UTC).isoformat(),
            }
        )
        pipe.lpush(self._key("errors:log"), error_log)
        pipe.ltrim(self._key("errors:log"), 0, 99)

        await pipe.execute()

    async def track_subscription(self, chat_id: int):
        """Track a new subscription."""
        if not self.redis:
            return

        pipe = self.redis.pipeline()

        pipe.incr(self._key("subscriptions:total"))
        pipe.incr(self._daily_key("subscriptions"))
        pipe.expire(self._daily_key("subscriptions"), 90 * 24 * 3600)

        await pipe.execute()

    async def track_command(self, command: str):
        """Track command usage."""
        if not self.redis:
            return

        pipe = self.redis.pipeline()

        pipe.incr(self._key(f"commands:{command}"))
        pipe.incr(self._daily_key(f"commands:{command}"))
        pipe.expire(self._daily_key(f"commands:{command}"), 90 * 24 * 3600)

        await pipe.execute()

    # ============================================================
    # RETRIEVAL METHODS
    # ============================================================

    async def get_stats(self) -> dict:
        """Get all-time statistics."""
        if not self.redis:
            return {}

        pipe = self.redis.pipeline()

        # All-time counters
        pipe.get(self._key("messages:total"))
        pipe.get(self._key("summaries:total"))
        pipe.get(self._key("messages:summarized"))
        pipe.get(self._key("errors:total"))
        pipe.get(self._key("subscriptions:total"))

        # All-time unique counts
        pipe.scard(self._key("users:all"))
        pipe.scard(self._key("chats:all"))

        results = await pipe.execute()

        return {
            "messages_processed": int(results[0] or 0),
            "summaries_generated": int(results[1] or 0),
            "messages_summarized": int(results[2] or 0),
            "errors_total": int(results[3] or 0),
            "subscriptions_total": int(results[4] or 0),
            "unique_users": results[5] or 0,
            "unique_chats": results[6] or 0,
        }

    async def get_daily_stats(self, date: datetime | None = None) -> dict:
        """Get statistics for a specific day (defaults to today)."""
        if not self.redis:
            return {}

        date = date or datetime.now(UTC)

        pipe = self.redis.pipeline()

        pipe.get(self._daily_key("messages", date))
        pipe.get(self._daily_key("summaries", date))
        pipe.get(self._daily_key("messages:summarized", date))
        pipe.get(self._daily_key("errors", date))
        pipe.get(self._daily_key("subscriptions", date))
        pipe.scard(self._daily_key("users", date))
        pipe.scard(self._daily_key("chats", date))

        results = await pipe.execute()

        return {
            "date": date.strftime("%Y-%m-%d"),
            "messages_processed": int(results[0] or 0),
            "summaries_generated": int(results[1] or 0),
            "messages_summarized": int(results[2] or 0),
            "errors": int(results[3] or 0),
            "new_subscriptions": int(results[4] or 0),
            "active_users": results[5] or 0,
            "active_chats": results[6] or 0,
        }

    async def get_recent_errors(self, limit: int = 10) -> list[dict]:
        """Get recent error logs."""
        if not self.redis:
            return []

        errors = await self.redis.lrange(self._key("errors:log"), 0, limit - 1)
        return [json.loads(e) for e in errors]

    async def get_command_stats(self) -> dict:
        """Get command usage statistics."""
        if not self.redis:
            return {}

        commands = ["start", "help", "summary", "status", "subscribe", "health", "stats"]
        pipe = self.redis.pipeline()

        for cmd in commands:
            pipe.get(self._key(f"commands:{cmd}"))

        results = await pipe.execute()

        return {cmd: int(results[i] or 0) for i, cmd in enumerate(commands)}

    async def get_active_subscription_count(self) -> int:
        """Count chats with active subscriptions (Telegram Stars or Stripe)."""
        if not self.redis:
            return 0

        active_chat_ids: set[int] = set()

        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor, match="tldr:chat:*:subscription", count=200
            )
            for key in keys:
                chat_id = self._extract_chat_id(key)
                if chat_id is not None:
                    active_chat_ids.add(chat_id)
            if cursor == 0:
                break

        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor, match="tldr:chat:*:stripe_subscription", count=200
            )
            if keys:
                values = await self.redis.mget(keys)
                for key, raw in zip(keys, values):
                    if not raw:
                        continue
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if data.get("status") in ("active", "trialing"):
                        chat_id = self._extract_chat_id(key)
                        if chat_id is not None:
                            active_chat_ids.add(chat_id)
            if cursor == 0:
                break

        return len(active_chat_ids)

    async def get_trend_data(self, days: int = 7) -> list[dict]:
        """Get daily statistics for the last N days (for trend charts)."""
        if not self.redis:
            return []

        results = []
        for i in range(days - 1, -1, -1):  # Go backwards from oldest to newest
            from datetime import timedelta
            date = datetime.now(UTC) - timedelta(days=i)
            daily_stats = await self.get_daily_stats(date)
            results.append(daily_stats)

        return results

    async def get_dashboard_data(self) -> dict:
        """Get comprehensive dashboard data for the analytics UI."""
        if not self.redis:
            return {}

        all_time = await self.get_stats()
        today = await self.get_daily_stats()
        commands = await self.get_command_stats()
        active_subscriptions = await self.get_active_subscription_count()
        trends_7d = await self.get_trend_data(7)
        trends_30d = await self.get_trend_data(30)
        recent_errors = await self.get_recent_errors(5)
        total_chats = int(all_time.get("unique_chats", 0) or 0)
        free_chats = max(0, total_chats - active_subscriptions)
        conversion_rate = (
            round((active_subscriptions / total_chats) * 100, 1) if total_chats else 0.0
        )

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "all_time": all_time,
            "today": today,
            "commands": commands,
            "conversion": {
                "premium_chats": active_subscriptions,
                "free_chats": free_chats,
                "conversion_rate": conversion_rate,
            },
            "trends_7d": trends_7d,
            "trends_30d": trends_30d,
            "recent_errors": recent_errors,
        }

    def format_stats_message(self, all_time: dict, daily: dict, commands: dict) -> str:
        """Format statistics as a readable message for admins."""
        return (
            "**📊 Bot Analytics**\n\n"
            "**All-Time Stats:**\n"
            f"• Messages processed: {all_time.get('messages_processed', 0):,}\n"
            f"• Summaries generated: {all_time.get('summaries_generated', 0):,}\n"
            f"• Messages summarized: {all_time.get('messages_summarized', 0):,}\n"
            f"• Unique users: {all_time.get('unique_users', 0):,}\n"
            f"• Unique chats: {all_time.get('unique_chats', 0):,}\n"
            f"• Subscriptions: {all_time.get('subscriptions_total', 0):,}\n"
            f"• Errors: {all_time.get('errors_total', 0):,}\n\n"
            f"**Today ({daily.get('date', 'N/A')}):**\n"
            f"• Messages: {daily.get('messages_processed', 0):,}\n"
            f"• Summaries: {daily.get('summaries_generated', 0):,}\n"
            f"• Active users: {daily.get('active_users', 0):,}\n"
            f"• Active chats: {daily.get('active_chats', 0):,}\n"
            f"• Errors: {daily.get('errors', 0):,}\n\n"
            "**Command Usage (All-Time):**\n"
            f"• /start: {commands.get('start', 0):,}\n"
            f"• /summary: {commands.get('summary', 0):,}\n"
            f"• /help: {commands.get('help', 0):,}\n"
            f"• /status: {commands.get('status', 0):,}\n"
            f"• /subscribe: {commands.get('subscribe', 0):,}"
        )


# Global instance
analytics = Analytics()
