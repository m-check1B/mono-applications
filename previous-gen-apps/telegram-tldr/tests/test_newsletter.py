"""Tests for newsletter service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.newsletter import (
    NEWSLETTER_TEMPLATE,
    NewsletterService,
    newsletter,
)


@pytest.fixture
def newsletter_service():
    """Newsletter service instance."""
    return NewsletterService()


class TestGenerateNewsletter:
    """Tests for generate_newsletter."""

    @pytest.mark.asyncio
    async def test_empty_topics_returns_empty(self, newsletter_service):
        """Should return empty result for empty topics."""
        result = await newsletter_service.generate_newsletter([])
        assert result["text"] == ""
        assert result["audio_path"] is None
        assert result["articles"] == []

    @pytest.mark.asyncio
    async def test_no_articles_found(self, newsletter_service):
        """Should return empty when no articles found."""
        with patch(
            "app.services.newsletter.news_aggregator.fetch_topic_news",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await newsletter_service.generate_newsletter(["tech"])
            assert result["text"] == ""
            assert result["audio_path"] is None

    @pytest.mark.asyncio
    async def test_generates_newsletter_text(self, newsletter_service):
        """Should generate newsletter text from articles."""
        mock_articles = [
            {
                "title": "New Python Release",
                "summary": "Python 3.13 is out with new features.",
                "source": "TechCrunch",
                "published": datetime.now(UTC),
                "link": "https://example.com/article",
            }
        ]

        mock_response = MagicMock()
        mock_response.text = "📰 **Your December 25, 2024 TL;DR Newsletter**\n\nPython 3.13 released!"

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch(
            "app.services.newsletter.news_aggregator.fetch_topic_news",
            new_callable=AsyncMock,
            return_value=mock_articles,
        ), patch.object(newsletter_service, "_get_model", return_value=mock_model), patch(
            "app.services.newsletter.tts.text_to_speech",
            new_callable=AsyncMock,
            return_value="/tmp/audio.mp3",
        ):
            result = await newsletter_service.generate_newsletter(["tech"], include_audio=True)
            assert "Newsletter" in result["text"]
            assert result["audio_path"] == "/tmp/audio.mp3"
            assert len(result["articles"]) == 1

    @pytest.mark.asyncio
    async def test_skips_audio_when_disabled(self, newsletter_service):
        """Should skip audio generation when include_audio=False."""
        mock_articles = [
            {
                "title": "News Item",
                "summary": "Summary text",
                "source": "Source",
                "published": datetime.now(UTC),
                "link": "https://example.com",
            }
        ]

        mock_response = MagicMock()
        mock_response.text = "Newsletter content"

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch(
            "app.services.newsletter.news_aggregator.fetch_topic_news",
            new_callable=AsyncMock,
            return_value=mock_articles,
        ), patch.object(newsletter_service, "_get_model", return_value=mock_model):
            result = await newsletter_service.generate_newsletter(
                ["tech"], include_audio=False
            )
            assert result["audio_path"] is None

    @pytest.mark.asyncio
    async def test_handles_ai_error(self, newsletter_service):
        """Should handle AI generation errors gracefully."""
        mock_articles = [
            {
                "title": "Article",
                "summary": "Summary",
                "source": "Source",
                "published": datetime.now(UTC),
                "link": "https://example.com",
            }
        ]

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(side_effect=Exception("AI error"))

        with patch(
            "app.services.newsletter.news_aggregator.fetch_topic_news",
            new_callable=AsyncMock,
            return_value=mock_articles,
        ), patch.object(newsletter_service, "_get_model", return_value=mock_model):
            result = await newsletter_service.generate_newsletter(["tech"])
            assert result["text"] == ""
            assert result["audio_path"] is None

    @pytest.mark.asyncio
    async def test_limits_articles_to_20(self, newsletter_service):
        """Should limit articles in result to 20."""
        # Create 30 articles
        mock_articles = [
            {
                "title": f"Article {i}",
                "summary": f"Summary {i}",
                "source": "Source",
                "published": datetime.now(UTC),
                "link": f"https://example.com/{i}",
            }
            for i in range(30)
        ]

        mock_response = MagicMock()
        mock_response.text = "Newsletter content"

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch(
            "app.services.newsletter.news_aggregator.fetch_topic_news",
            new_callable=AsyncMock,
            return_value=mock_articles,
        ), patch.object(newsletter_service, "_get_model", return_value=mock_model), patch(
            "app.services.newsletter.tts.text_to_speech",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await newsletter_service.generate_newsletter(
                ["tech"], include_audio=False
            )
            assert len(result["articles"]) <= 20


class TestFormatArticlesForAI:
    """Tests for _format_articles_for_ai."""

    def test_formats_articles_correctly(self, newsletter_service):
        """Should format articles with index, source, time, and content."""
        articles = [
            {
                "title": "Test Article",
                "summary": "Article summary here",
                "source": "TechNews",
                "published": datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
            }
        ]
        result = newsletter_service._format_articles_for_ai(articles)
        assert "1." in result
        assert "TechNews" in result
        assert "10:30" in result
        assert "Test Article" in result
        assert "Article summary" in result

    def test_limits_to_50_articles(self, newsletter_service):
        """Should limit to 50 articles."""
        articles = [
            {
                "title": f"Article {i}",
                "summary": f"Summary {i}",
                "source": "Source",
                "published": datetime.now(UTC),
            }
            for i in range(100)
        ]
        result = newsletter_service._format_articles_for_ai(articles)
        # Should only contain up to 50
        assert "51." not in result

    def test_handles_missing_published_date(self, newsletter_service):
        """Should handle articles without published date."""
        articles = [
            {
                "title": "No Date Article",
                "summary": "Summary",
                "source": "Source",
                "published": None,
            }
        ]
        result = newsletter_service._format_articles_for_ai(articles)
        assert "??:??" in result

    def test_truncates_long_titles_and_summaries(self, newsletter_service):
        """Should truncate long titles and summaries."""
        articles = [
            {
                "title": "A" * 200,  # Very long title
                "summary": "B" * 500,  # Very long summary
                "source": "Source",
                "published": datetime.now(UTC),
            }
        ]
        result = newsletter_service._format_articles_for_ai(articles)
        # Title limited to 100, summary to 300
        assert "A" * 101 not in result


class TestGetCleanTemplate:
    """Tests for _get_clean_template."""

    def test_replaces_placeholders(self, newsletter_service):
        """Should replace template placeholders."""
        result = newsletter_service._get_clean_template()
        assert "DATE" in result
        assert "CONTENT" in result
        assert "SOURCES" in result
        assert "{date}" not in result
        assert "{content}" not in result
        assert "{sources}" not in result


class TestGetNewsletterStats:
    """Tests for get_newsletter_stats."""

    @pytest.mark.asyncio
    async def test_returns_stats_structure(self, newsletter_service):
        """Should return stats with correct structure."""
        with patch(
            "app.services.newsletter.news_aggregator.get_all_newsletter_subscribers",
            new_callable=AsyncMock,
            return_value=[(123, ["tech"], None)],
        ), patch(
            "app.services.newsletter.news_aggregator.get_available_news_topics",
            new_callable=AsyncMock,
            return_value=["tech", "crypto", "news"],
        ), patch(
            "app.services.newsletter.news_aggregator.get_cached_news",
            new_callable=AsyncMock,
            return_value=[{"title": "Article"}],
        ):
            result = await newsletter_service.get_newsletter_stats()
            assert "total_subscribers" in result
            assert "active_topics" in result
            assert "available_topics" in result
            assert result["total_subscribers"] == 1


class TestNewsletterTemplate:
    """Tests for newsletter template."""

    def test_template_has_required_placeholders(self):
        """Template should have required placeholders."""
        assert "{date}" in NEWSLETTER_TEMPLATE
        assert "{content}" in NEWSLETTER_TEMPLATE
        assert "{sources}" in NEWSLETTER_TEMPLATE

    def test_template_has_emoji(self):
        """Template should include emoji for visual appeal."""
        assert "📰" in NEWSLETTER_TEMPLATE


class TestGlobalInstance:
    """Tests for global newsletter instance."""

    def test_global_instance_exists(self):
        """Should have a global instance."""
        assert newsletter is not None
        assert isinstance(newsletter, NewsletterService)
