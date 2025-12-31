"""News aggregation service for TL;DR newsletter.

Fetches and aggregates news from RSS feeds and external sources.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import feedparser
import redis.asyncio as redis
import trafilatura

logger = logging.getLogger(__name__)


# Default RSS feeds by topic
DEFAULT_RSS_FEEDS = {
    "tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
    ],
    "news": [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
    ],
    "deals": [
        "https://www.slickdeals.net/newsearch.php?q=&searcharea=deals&searchin=first&rss=1",
    ],
}


class NewsAggregator:
    """Aggregates news from RSS feeds."""

    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self, redis_client: redis.Redis):
        """Connect using existing Redis client."""
        self.redis = redis_client

    # ============================================================
    # Redis Key Patterns
    # ============================================================

    def _news_items_key(self, topic: str) -> str:
        """Key for news items of a topic."""
        return f"tldr:news:{topic}:items"

    def _news_last_fetched_key(self, topic: str) -> str:
        """Key for last fetch timestamp."""
        return f"tldr:news:{topic}:last_fetched"

    def _user_news_subs_key(self, user_id: int) -> str:
        """Key for user's news topic subscriptions."""
        return f"tldr:user:{user_id}:news_topics"

    def _user_news_digest_time_key(self, user_id: int) -> str:
        """Key for user's newsletter digest time."""
        return f"tldr:user:{user_id}:newsletter_time"

    def _newsletter_subscribers_key(self) -> str:
        """Key for all newsletter subscribers."""
        return "tldr:newsletter:subscribers"

    # ============================================================
    # Feed Fetching
    # ============================================================

    async def fetch_topic_news(self, topic: str, hours: int = 24) -> list[dict]:
        """Fetch recent news for a topic from its RSS feeds.

        Returns list of news items with title, link, published, summary.
        """
        if topic not in DEFAULT_RSS_FEEDS:
            logger.warning(f"Unknown topic: {topic}")
            return []

        feeds = DEFAULT_RSS_FEEDS[topic]
        all_items = []

        # 1. Parse all feeds in parallel threads
        feed_tasks = [asyncio.to_thread(self._parse_feed, feed_url, hours) for feed_url in feeds]
        feed_results = await asyncio.gather(*feed_tasks, return_exceptions=True)
        for i, items in enumerate(feed_results):
            if isinstance(items, Exception):
                logger.error(f"Error fetching feed {feeds[i]}: {items}")
            else:
                all_items.extend(items)

        # 2. Extract full content for items with short summaries (top 15 items only to avoid bloat)
        all_items.sort(key=lambda x: x.get("published", datetime.min), reverse=True)
        top_items = all_items[:15]

        extraction_tasks = []
        for item in top_items:
            if len(item["summary"]) < 200 and item["link"]:
                extraction_tasks.append(self._async_extract_full_content(item))

        if extraction_tasks:
            await asyncio.gather(*extraction_tasks)

        # Store in Redis for quick access
        await self._store_news_items(topic, all_items)

        # Update last fetched timestamp
        await self._update_last_fetched(topic)

        return all_items

    async def _async_extract_full_content(self, item: dict) -> None:
        """Asynchronously extract full content and update the item."""
        link = item["link"]
        try:
            full_content = await asyncio.to_thread(self._extract_full_content, link)
            if full_content and len(full_content) > len(item["summary"]):
                # Limit full content to 1500 chars for the summary field
                item["summary"] = full_content[:1500]
        except Exception as e:
            logger.error(f"Async extraction error for {link}: {e}")

    def _parse_feed(self, feed_url: str, hours: int) -> list[dict]:
        """Parse RSS feed and return recent items."""
        parsed = feedparser.parse(feed_url)
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        items = []
        for entry in parsed.entries:
            # Parse published date
            published = None
            if hasattr(entry, "published_parsed"):
                published = datetime(*entry.published_parsed[:6], tzinfo=UTC)

            # Skip old items
            if published and published < cutoff:
                continue

            # Extract content
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description

            # Clean HTML from summary
            import re

            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary.strip()[:500]  # Limit to 500 chars

            items.append(
                {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": published or datetime.now(UTC),
                    "summary": summary,
                    "source": parsed.feed.get("title", feed_url),
                }
            )

        return items

    def _extract_full_content(self, url: str) -> str | None:
        """Extract full text content from a URL using trafilatura."""
        try:
            # Use a timeout for fetching
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                result = trafilatura.extract(
                    downloaded, include_comments=False, no_fallback=False, include_tables=False
                )
                if result:
                    # Clean up whitespace
                    import re

                    result = re.sub(r"\s+", " ", result).strip()
                    return result
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")

        return None

    # ============================================================
    # Storage
    # ============================================================

    async def _store_news_items(self, topic: str, items: list[dict]) -> None:
        """Store news items in Redis."""
        if not self.redis or not items:
            return

        key = self._news_items_key(topic)

        # Store as JSON list
        import json

        items_json = json.dumps(
            [
                {
                    "title": item["title"],
                    "link": item["link"],
                    "published": item["published"].isoformat() if item["published"] else None,
                    "summary": item["summary"],
                    "source": item["source"],
                }
                for item in items[:100]  # Limit to 100 items
            ]
        )

        await self.redis.set(key, items_json, ex=24 * 3600)  # Expire in 24h

    async def get_cached_news(self, topic: str) -> list[dict]:
        """Get cached news for a topic."""
        if not self.redis:
            return []

        key = self._news_items_key(topic)
        cached = await self.redis.get(key)

        if not cached:
            return []

        import json

        items_data = json.loads(cached)

        # Parse dates
        for item in items_data:
            if item.get("published"):
                item["published"] = datetime.fromisoformat(item["published"])

        return items_data

    async def _update_last_fetched(self, topic: str) -> None:
        """Update last fetched timestamp."""
        if not self.redis:
            return

        key = self._news_last_fetched_key(topic)
        await self.redis.set(key, datetime.now(UTC).isoformat(), ex=48 * 3600)

    # ============================================================
    # Newsletter Subscriptions
    # ============================================================

    async def subscribe_newsletter(self, user_id: int, topics: list[str] = None) -> bool:
        """Subscribe user to newsletter.

        If topics provided, set as user's news topics.
        Otherwise, subscribe to all default topics.
        """
        if not self.redis:
            return False

        # Add to subscribers set
        await self.redis.sadd(self._newsletter_subscribers_key(), str(user_id))

        # Set topics if provided
        if topics:
            key = self._user_news_subs_key(user_id)
            await self.redis.delete(key)  # Clear existing
            for topic in topics:
                if topic in DEFAULT_RSS_FEEDS:
                    await self.redis.sadd(key, topic)
            await self.redis.expire(key, 90 * 24 * 3600)  # 90 days

        return True

    async def unsubscribe_newsletter(self, user_id: int) -> bool:
        """Unsubscribe user from newsletter."""
        if not self.redis:
            return False

        await self.redis.srem(self._newsletter_subscribers_key(), str(user_id))
        await self.redis.delete(self._user_news_subs_key(user_id))

        return True

    async def is_newsletter_subscriber(self, user_id: int) -> bool:
        """Check if user is subscribed to newsletter."""
        if not self.redis:
            return False

        return await self.redis.sismember(self._newsletter_subscribers_key(), str(user_id))

    async def get_user_news_topics(self, user_id: int) -> list[str]:
        """Get user's news topic subscriptions."""
        if not self.redis:
            return list(DEFAULT_RSS_FEEDS.keys())

        key = self._user_news_subs_key(user_id)
        topics = await self.redis.smembers(key)

        if not topics:
            return list(DEFAULT_RSS_FEEDS.keys())

        return list(topics)

    async def set_user_news_topics(self, user_id: int, topics: list[str]) -> bool:
        """Set user's news topic subscriptions."""
        if not self.redis:
            return False

        valid_topics = [t for t in topics if t in DEFAULT_RSS_FEEDS]
        if not valid_topics:
            return False

        key = self._user_news_subs_key(user_id)
        await self.redis.delete(key)
        for topic in valid_topics:
            await self.redis.sadd(key, topic)
        await self.redis.expire(key, 90 * 24 * 3600)

        return True

    async def set_newsletter_time(self, user_id: int, hour: int, minute: int) -> bool:
        """Set user's preferred newsletter delivery time (UTC)."""
        if not self.redis:
            return False

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False

        key = self._user_news_digest_time_key(user_id)
        await self.redis.set(key, f"{hour:02d}:{minute:02d}", ex=90 * 24 * 3600)

        return True

    async def get_newsletter_time(self, user_id: int) -> tuple[int, int] | None:
        """Get user's preferred newsletter delivery time."""
        if not self.redis:
            return None

        key = self._user_news_digest_time_key(user_id)
        time_str = await self.redis.get(key)

        if not time_str:
            return None

        parts = time_str.split(":")
        return (int(parts[0]), int(parts[1]))

    async def get_all_newsletter_subscribers(
        self,
    ) -> list[tuple[int, list[str], tuple[int, int] | None]]:
        """Get all newsletter subscribers with their topics and delivery time.

        Returns list of (user_id, topics, delivery_time) tuples.
        """
        if not self.redis:
            return []

        subscribers = []
        cursor = 0

        while True:
            cursor, user_ids = await self.redis.scan(
                cursor, match=self._newsletter_subscribers_key(), count=100
            )

            for user_key in user_ids:
                # Get subscriber IDs from the set
                ids = await self.redis.smembers(user_key)
                for uid in ids:
                    try:
                        user_id = int(uid)
                        topics = await self.get_user_news_topics(user_id)
                        delivery_time = await self.get_newsletter_time(user_id)
                        subscribers.append((user_id, topics, delivery_time))
                    except (ValueError, Exception):
                        continue

            if cursor == 0:
                break

        return subscribers

    async def get_available_news_topics(self) -> list[str]:
        """Get list of available news topics."""
        return list(DEFAULT_RSS_FEEDS.keys())


# Global instance
news_aggregator = NewsAggregator()
