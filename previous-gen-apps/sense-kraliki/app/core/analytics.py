"""Usage analytics tracking for Sense by Kraliki bot.

Tracks:
- Charts/reports generated (by type)
- Active users (daily/weekly/monthly)
- Command usage counts
- Errors encountered

All data stored in Redis with appropriate TTLs.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis key prefixes
KEY_PREFIX = "sense-kraliki:analytics"
LEGACY_KEY_PREFIX = "senseit:analytics"
KEY_DAILY_USERS = f"{KEY_PREFIX}:daily_users"
KEY_WEEKLY_USERS = f"{KEY_PREFIX}:weekly_users"
KEY_MONTHLY_USERS = f"{KEY_PREFIX}:monthly_users"
KEY_COMMAND_COUNT = f"{KEY_PREFIX}:commands"
KEY_CHART_TYPE = f"{KEY_PREFIX}:chart_types"
KEY_ERRORS = f"{KEY_PREFIX}:errors"
KEY_TOTAL_USERS = f"{KEY_PREFIX}:total_users"

# TTLs in seconds
DAY_TTL = 86400  # 24 hours
WEEK_TTL = 604800  # 7 days
MONTH_TTL = 2592000  # 30 days


class Analytics:
    """Analytics tracking using Redis."""

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _legacy_key(self, key: str) -> str:
        """Map a current key to its legacy prefix."""
        if key.startswith(KEY_PREFIX):
            return key.replace(KEY_PREFIX, LEGACY_KEY_PREFIX, 1)
        return key

    async def _get_union_cardinality(self, *keys: str) -> int:
        """Return cardinality of the union for one or more Redis sets."""
        r = await self.get_redis()
        if not keys:
            return 0
        if len(keys) == 1:
            return await r.scard(keys[0])
        members = await r.sunion(*keys)
        return len(members)

    async def _get_counter_with_legacy(self, key: str) -> int:
        """Get counter value by summing current and legacy keys."""
        r = await self.get_redis()
        current = await r.get(key) or "0"
        legacy = await r.get(self._legacy_key(key)) or "0"
        return int(current) + int(legacy)

    def _get_date_key(self, prefix: str, date: Optional[datetime] = None) -> str:
        """Get date-based key for tracking."""
        if date is None:
            date = datetime.now(timezone.utc)
        return f"{prefix}:{date.strftime('%Y-%m-%d')}"

    def _get_week_key(self, prefix: str, date: Optional[datetime] = None) -> str:
        """Get week-based key for tracking."""
        if date is None:
            date = datetime.now(timezone.utc)
        year, week, _ = date.isocalendar()
        return f"{prefix}:{year}-W{week:02d}"

    def _get_month_key(self, prefix: str, date: Optional[datetime] = None) -> str:
        """Get month-based key for tracking."""
        if date is None:
            date = datetime.now(timezone.utc)
        return f"{prefix}:{date.strftime('%Y-%m')}"

    async def track_user(self, user_id: int):
        """Track a user activity (daily/weekly/monthly active users)."""
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Track in daily set
            daily_key = self._get_date_key(KEY_DAILY_USERS, now)
            await r.sadd(daily_key, str(user_id))
            await r.expire(daily_key, DAY_TTL)

            # Track in weekly set
            weekly_key = self._get_week_key(KEY_WEEKLY_USERS, now)
            await r.sadd(weekly_key, str(user_id))
            await r.expire(weekly_key, WEEK_TTL)

            # Track in monthly set
            monthly_key = self._get_month_key(KEY_MONTHLY_USERS, now)
            await r.sadd(monthly_key, str(user_id))
            await r.expire(monthly_key, MONTH_TTL)

            # Track total unique users (no expiry)
            await r.sadd(KEY_TOTAL_USERS, str(user_id))

        except Exception:
            logger.exception("Failed to track user %s", user_id)

    async def track_command(self, command: str, user_id: int):
        """Track command usage."""
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Track user activity
            await self.track_user(user_id)

            # Increment command counter (daily)
            daily_key = f"{KEY_COMMAND_COUNT}:{command}:{now.strftime('%Y-%m-%d')}"
            await r.incr(daily_key)
            await r.expire(daily_key, MONTH_TTL)

            # Increment total command counter
            total_key = f"{KEY_COMMAND_COUNT}:{command}:total"
            await r.incr(total_key)

        except Exception:
            logger.exception("Failed to track command %s for user %s", command, user_id)

    async def track_chart_type(self, chart_type: str, user_id: int):
        """Track chart/report type generated.

        Chart types: sense, dream, bio, astro, remedies, forecast
        """
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Increment chart type counter (daily)
            daily_key = f"{KEY_CHART_TYPE}:{chart_type}:{now.strftime('%Y-%m-%d')}"
            await r.incr(daily_key)
            await r.expire(daily_key, MONTH_TTL)

            # Increment total chart type counter
            total_key = f"{KEY_CHART_TYPE}:{chart_type}:total"
            await r.incr(total_key)

        except Exception:
            logger.exception("Failed to track chart type %s for user %s", chart_type, user_id)

    async def track_error(self, error_type: str, command: str):
        """Track an error occurrence."""
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Increment error counter (daily)
            daily_key = f"{KEY_ERRORS}:{error_type}:{now.strftime('%Y-%m-%d')}"
            await r.incr(daily_key)
            await r.expire(daily_key, MONTH_TTL)

            # Track which command caused the error
            cmd_error_key = f"{KEY_ERRORS}:by_command:{command}:{now.strftime('%Y-%m-%d')}"
            await r.incr(cmd_error_key)
            await r.expire(cmd_error_key, MONTH_TTL)

            # Increment total error counter
            total_key = f"{KEY_ERRORS}:total"
            await r.incr(total_key)

        except Exception:
            logger.exception("Failed to track error %s for command %s", error_type, command)

    async def track_subscription(self, user_id: int, plan: str):
        """Track a subscription purchase."""
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Increment subscription counter by plan (daily)
            daily_key = f"{KEY_PREFIX}:subscriptions:{plan}:{now.strftime('%Y-%m-%d')}"
            await r.incr(daily_key)
            await r.expire(daily_key, MONTH_TTL)

            # Increment total subscription counter by plan
            total_key = f"{KEY_PREFIX}:subscriptions:{plan}:total"
            await r.incr(total_key)

        except Exception:
            logger.exception("Failed to track subscription %s for user %s", plan, user_id)

    async def get_stats(self) -> dict:
        """Get comprehensive analytics stats."""
        try:
            r = await self.get_redis()
            now = datetime.now(timezone.utc)

            # Get active users
            daily_key = self._get_date_key(KEY_DAILY_USERS, now)
            weekly_key = self._get_week_key(KEY_WEEKLY_USERS, now)
            monthly_key = self._get_month_key(KEY_MONTHLY_USERS, now)

            daily_users = await self._get_union_cardinality(daily_key, self._legacy_key(daily_key))
            weekly_users = await self._get_union_cardinality(weekly_key, self._legacy_key(weekly_key))
            monthly_users = await self._get_union_cardinality(monthly_key, self._legacy_key(monthly_key))
            total_users = await self._get_union_cardinality(KEY_TOTAL_USERS, self._legacy_key(KEY_TOTAL_USERS))

            # Get chart type stats
            chart_types = ["sense", "dream", "bio", "astro", "remedies", "forecast"]
            chart_stats = {}
            for ct in chart_types:
                daily = await self._get_counter_with_legacy(
                    f"{KEY_CHART_TYPE}:{ct}:{now.strftime('%Y-%m-%d')}"
                )
                total = await self._get_counter_with_legacy(f"{KEY_CHART_TYPE}:{ct}:total")
                chart_stats[ct] = {
                    "today": daily,
                    "total": total
                }

            # Get command stats
            commands = ["start", "sense", "dream", "bio", "astro", "remedies", "forecast",
                       "setbirthday", "setlocation", "help", "health", "status", "subscribe", "stats"]
            command_stats = {}
            for cmd in commands:
                daily = await self._get_counter_with_legacy(
                    f"{KEY_COMMAND_COUNT}:{cmd}:{now.strftime('%Y-%m-%d')}"
                )
                total = await self._get_counter_with_legacy(f"{KEY_COMMAND_COUNT}:{cmd}:total")
                command_stats[cmd] = {
                    "today": daily,
                    "total": total
                }

            # Get error stats
            total_errors = await self._get_counter_with_legacy(f"{KEY_ERRORS}:total")

            return {
                "users": {
                    "daily_active": daily_users,
                    "weekly_active": weekly_users,
                    "monthly_active": monthly_users,
                    "total": total_users
                },
                "charts": chart_stats,
                "commands": command_stats,
                "errors": {
                    "total": total_errors
                },
                "timestamp": now.isoformat()
            }

        except Exception:
            logger.exception("Failed to get stats")
            return {
                "error": "Failed to retrieve stats",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Singleton instance
analytics = Analytics()
