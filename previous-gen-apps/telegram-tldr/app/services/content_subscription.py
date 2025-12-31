"""Content subscription service for personalized topic-based digests.

This service enables users to:
1. Subscribe to specific topics (crypto, tech, deals, etc.)
2. Get personalized digests based on their interests
3. Track topics across multiple groups they're in
"""
import json
import logging
from datetime import UTC, datetime

import google.generativeai as genai
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Default topics that can be subscribed to
DEFAULT_TOPICS = [
    "tech",        # Technology, programming, software
    "crypto",      # Cryptocurrency, blockchain, DeFi
    "deals",       # Sales, discounts, offers
    "news",        # Current events, announcements
    "jobs",        # Job postings, career opportunities
    "events",      # Meetups, conferences, online events
    "learning",    # Tutorials, courses, educational content
    "finance",     # Investing, markets, personal finance
]

# Prompt for extracting topics from messages
TOPIC_EXTRACTION_PROMPT = """Analyze these chat messages and extract the main topics being discussed.

AVAILABLE TOPICS:
{topics}

For each message, determine which topics (if any) it relates to.
Return ONLY a JSON object with this format:
{{"topics": ["topic1", "topic2"], "relevant_messages": [0, 3, 5]}}

Where:
- "topics" is a list of topics from the available list that are present
- "relevant_messages" is a list of message indices (0-based) that are substantive

MESSAGES:
{messages}

Return only valid JSON, no other text.
"""

# Prompt for generating personalized digest
PERSONALIZED_DIGEST_PROMPT = """Create a personalized digest focused on these topics: {topics}

Filter the messages and summarize ONLY content related to these topics.
Ignore any messages not related to the specified topics.

FORMAT:
**Your {topic_count} Topic Digest**

For each topic with relevant content:

**[Topic Name]:**
- Key point 1
- Key point 2
- Links: [if any]

If a topic has no relevant content, skip it entirely.

MESSAGES:
{messages}
"""


class ContentSubscription:
    """Manages user topic subscriptions and personalized content delivery."""

    def __init__(self):
        self.redis: redis.Redis | None = None
        self._model = None

    async def connect(self, redis_client: redis.Redis):
        """Connect using existing Redis client."""
        self.redis = redis_client

    def _get_model(self):
        """Get or initialize Gemini model."""
        if self._model is None:
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(settings.gemini_model)
        return self._model

    # ============================================================
    # Redis Key Patterns
    # ============================================================

    def _user_topics_key(self, user_id: int) -> str:
        """Key for user's subscribed topics."""
        return f"tldr:user:{user_id}:topics"

    def _user_prefs_key(self, user_id: int) -> str:
        """Key for user's content preferences."""
        return f"tldr:user:{user_id}:content_prefs"

    def _user_digest_key(self, user_id: int) -> str:
        """Key for user's last digest timestamp."""
        return f"tldr:user:{user_id}:last_digest"

    def _content_sub_key(self, user_id: int) -> str:
        """Key for user's content subscription status."""
        return f"tldr:user:{user_id}:content_sub"

    def _chat_topics_key(self, chat_id: int) -> str:
        """Key for cached topics in a chat."""
        return f"tldr:chat:{chat_id}:topics_cache"

    # ============================================================
    # Topic Subscription Management
    # ============================================================

    async def get_available_topics(self) -> list[str]:
        """Get list of available topics for subscription."""
        return DEFAULT_TOPICS.copy()

    async def subscribe_to_topics(self, user_id: int, topics: list[str]) -> list[str]:
        """Subscribe user to one or more topics.

        Returns list of successfully subscribed topics.
        """
        if not self.redis:
            return []

        valid_topics = [t for t in topics if t in DEFAULT_TOPICS]
        if not valid_topics:
            return []

        key = self._user_topics_key(user_id)
        for topic in valid_topics:
            await self.redis.sadd(key, topic)

        # Set expiry (30 days, renews on subscription)
        await self.redis.expire(key, 30 * 24 * 3600)

        return valid_topics

    async def unsubscribe_from_topics(self, user_id: int, topics: list[str]) -> int:
        """Unsubscribe user from topics. Returns count of removed topics."""
        if not self.redis:
            return 0

        key = self._user_topics_key(user_id)
        removed = 0
        for topic in topics:
            removed += await self.redis.srem(key, topic)

        return removed

    async def get_user_topics(self, user_id: int) -> list[str]:
        """Get list of topics user is subscribed to."""
        if not self.redis:
            return []

        key = self._user_topics_key(user_id)
        topics = await self.redis.smembers(key)
        return list(topics) if topics else []

    async def set_content_subscription(self, user_id: int, months: int = 1) -> bool:
        """Activate content subscription for user (premium feature)."""
        if not self.redis:
            return False

        key = self._content_sub_key(user_id)
        await self.redis.set(key, "active")
        await self.redis.expire(key, months * 30 * 24 * 3600)
        return True

    async def is_content_subscriber(self, user_id: int) -> bool:
        """Check if user has active content subscription."""
        if not self.redis:
            return False

        key = self._content_sub_key(user_id)
        return await self.redis.exists(key) > 0

    # ============================================================
    # Content Filtering and Delivery
    # ============================================================

    async def extract_topics_from_messages(
        self, messages: list[dict]
    ) -> dict:
        """Use AI to extract topics from messages.

        Returns dict with 'topics' and 'relevant_messages' keys.
        """
        if not messages:
            return {"topics": [], "relevant_messages": []}

        # Format messages
        formatted = []
        for i, msg in enumerate(messages):
            user = msg.get("user", "Unknown")
            text = msg.get("text", "")
            formatted.append(f"{i}. [{user}]: {text}")

        messages_text = "\n".join(formatted[:100])  # Limit to 100 messages
        topics_list = ", ".join(DEFAULT_TOPICS)

        model = self._get_model()

        try:
            response = await model.generate_content_async(
                TOPIC_EXTRACTION_PROMPT.format(
                    topics=topics_list,
                    messages=messages_text
                ),
                generation_config=genai.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.1,
                )
            )

            # Parse JSON response
            result_text = response.text.strip()
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1]
                result_text = result_text.rsplit("```", 1)[0]

            return json.loads(result_text)

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Topic extraction failed: {e}")
            return {"topics": [], "relevant_messages": []}

    async def generate_personalized_digest(
        self,
        user_id: int,
        messages: list[dict]
    ) -> str | None:
        """Generate a personalized digest based on user's topic subscriptions.

        Returns None if user has no subscribed topics or no relevant content.
        """
        if not messages:
            return None

        # Get user's topics
        user_topics = await self.get_user_topics(user_id)
        if not user_topics:
            return None

        # Format messages
        formatted = []
        for msg in messages:
            user = msg.get("user", "Unknown")
            text = msg.get("text", "")
            formatted.append(f"[{user}]: {text}")

        messages_text = "\n".join(formatted[:settings.max_messages_per_summary])
        topics_str = ", ".join(user_topics)

        model = self._get_model()

        try:
            response = await model.generate_content_async(
                PERSONALIZED_DIGEST_PROMPT.format(
                    topics=topics_str,
                    topic_count=len(user_topics),
                    messages=messages_text
                ),
                generation_config=genai.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.3,
                )
            )

            digest = response.text

            # Check if any content was found
            if "no relevant content" in digest.lower():
                return None

            return digest

        except Exception as e:
            logger.error(f"Personalized digest generation failed: {e}")
            return None

    async def update_last_digest(self, user_id: int) -> None:
        """Update timestamp of last digest sent to user."""
        if not self.redis:
            return

        key = self._user_digest_key(user_id)
        await self.redis.set(key, datetime.now(UTC).isoformat())
        await self.redis.expire(key, 7 * 24 * 3600)  # Keep for 7 days

    async def get_last_digest_time(self, user_id: int) -> datetime | None:
        """Get timestamp of last digest sent to user."""
        if not self.redis:
            return None

        key = self._user_digest_key(user_id)
        ts = await self.redis.get(key)
        if ts:
            return datetime.fromisoformat(ts)
        return None

    # ============================================================
    # Bulk Operations for Scheduled Delivery
    # ============================================================

    async def get_all_content_subscribers(self) -> list[tuple[int, list[str]]]:
        """Get all users with content subscriptions and their topics.

        Returns list of (user_id, topics) tuples.
        """
        if not self.redis:
            return []

        subscribers = []
        cursor = 0

        while True:
            cursor, keys = await self.redis.scan(
                cursor, match="tldr:user:*:content_sub", count=100
            )
            for key in keys:
                # Extract user_id from key
                parts = key.split(":")
                if len(parts) >= 3:
                    try:
                        user_id = int(parts[2])
                        topics = await self.get_user_topics(user_id)
                        if topics:
                            subscribers.append((user_id, topics))
                    except ValueError:
                        continue

            if cursor == 0:
                break

        return subscribers


# Global instance
content_subscription = ContentSubscription()
