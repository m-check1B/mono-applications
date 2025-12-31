"""Newsletter digest service for TL;DR.

Generates daily audio/text digests from news sources.
"""

import logging
from datetime import UTC, datetime

import google.generativeai as genai

from app.core.config import settings
from app.services.news_aggregator import news_aggregator
from app.services.tts import tts

logger = logging.getLogger(__name__)


# Template for newsletter digest
NEWSLETTER_TEMPLATE = """📰 **Your {date} TL;DR Newsletter**

{content}

🔗 **Sources:** {sources}

🙏 *Powered by AI - stay informed effortlessly*
"""

# Prompt for generating newsletter
NEWSLETTER_GENERATION_PROMPT = """Create a concise newsletter from these news articles.

TOPICS: {topics}
DATE: {date}

For each topic (if there are relevant articles):

**[Topic Name]:**
• One-line summary of most important story
• 2-3 key bullet points
• Link: [source]

Format as clean, scannable text suitable for Telegram.
Keep under 1000 words total.

ARTICLES:
{articles}

Response format:
{template}
"""


class NewsletterService:
    """Generates daily newsletter digests."""

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Get or initialize Gemini model."""
        if self._model is None:
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(settings.gemini_model)
        return self._model

    async def generate_newsletter(
        self, topics: list[str], hours: int = 24, include_audio: bool = True
    ) -> dict:
        """Generate newsletter digest for given topics.

        Returns dict with:
        - text: Newsletter text content
        - audio_path: Path to audio file (if include_audio)
        - articles: List of articles used
        """
        if not topics:
            return {"text": "", "audio_path": None, "articles": []}

        # Fetch news for all topics
        all_articles = []
        for topic in topics:
            articles = await news_aggregator.fetch_topic_news(topic, hours)
            all_articles.extend(articles)

        if not all_articles:
            logger.warning(f"No articles found for topics: {topics}")
            return {"text": "", "audio_path": None, "articles": []}

        # Format articles for AI
        articles_text = self._format_articles_for_ai(all_articles)

        # Generate newsletter text
        date_str = datetime.now(UTC).strftime("%B %d, %Y")
        template = self._get_clean_template()

        prompt = NEWSLETTER_GENERATION_PROMPT.format(
            topics=", ".join(topics), date=date_str, articles=articles_text, template=template
        )

        try:
            model = self._get_model()
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.5,
                ),
            )

            newsletter_text = response.text

            # Generate audio if requested
            audio_path = None
            if include_audio:
                audio_path = await tts.text_to_speech(newsletter_text)

            return {
                "text": newsletter_text,
                "audio_path": audio_path,
                "articles": all_articles[:20],  # Limit to 20 articles
                "topics": topics,
                "date": date_str,
            }

        except Exception as e:
            logger.error(f"Newsletter generation failed: {e}")
            return {"text": "", "audio_path": None, "articles": []}

    def _format_articles_for_ai(self, articles: list[dict]) -> str:
        """Format articles for AI processing."""
        formatted = []
        for i, article in enumerate(articles[:50]):  # Limit to 50 articles
            title = article.get("title", "")[:100]
            summary = article.get("summary", "")[:300]
            source = article.get("source", "Unknown")
            published = article.get("published")

            pub_str = published.strftime("%H:%M") if published else "??:??"

            formatted.append(f"{i + 1}. [{source} @ {pub_str}] {title}\n   {summary}")

        return "\n\n".join(formatted)

    def _get_clean_template(self) -> str:
        """Get clean template for AI."""
        return (
            NEWSLETTER_TEMPLATE.replace("{date}", "DATE")
            .replace("{content}", "CONTENT")
            .replace("{sources}", "SOURCES")
        )

    async def get_newsletter_stats(self) -> dict:
        """Get statistics about newsletter service.

        Returns:
        - total_subscribers: Number of newsletter subscribers
        - active_topics: List of topics with recent content
        - last_fetch: Time of last news fetch
        """
        subscribers = await news_aggregator.get_all_newsletter_subscribers()

        # Get topics with recent news
        topics_with_news = []
        for topic in await news_aggregator.get_available_news_topics():
            cached = await news_aggregator.get_cached_news(topic)
            if cached:
                topics_with_news.append(topic)

        return {
            "total_subscribers": len(subscribers),
            "active_topics": topics_with_news,
            "available_topics": await news_aggregator.get_available_news_topics(),
        }


# Global instance
newsletter = NewsletterService()
