"""Extended tests for bot.py handlers to improve test coverage.

Tests for:
- Payment handlers (process_payment for sub:, content_sub:, newsletter_sub:)
- Newsletter commands (/news with various subcommands)
- Topics and mydigest commands edge cases
- Periodic schedule command variations
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.fixture
def mock_message():
    """Create a mock Telegram message."""
    message = MagicMock()
    message.chat = MagicMock()
    message.chat.id = -100123456
    message.chat.type = "supergroup"
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    message.date = MagicMock()
    return message


@pytest.fixture
def mock_private_message(mock_message):
    """Create a mock private Telegram message."""
    mock_message.chat.type = "private"
    return mock_message


class TestPaymentHandlers:
    """Tests for payment processing handlers."""

    @pytest.mark.asyncio
    async def test_process_payment_newsletter_subscription(self, mock_message):
        """Should process newsletter subscription payment correctly."""
        with (
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_news.get_available_news_topics = AsyncMock(return_value=["tech", "news"])
            mock_news.subscribe_newsletter = AsyncMock()
            mock_analytics.track_subscription = AsyncMock()
            mock_settings.newsletter_price_stars = 250

            mock_message.successful_payment = MagicMock()
            mock_message.successful_payment.invoice_payload = "newsletter_sub:12345"
            mock_message.successful_payment.total_amount = 250

            from app.services.bot import process_payment

            await process_payment(mock_message)

            mock_news.get_available_news_topics.assert_called_once()
            mock_news.subscribe_newsletter.assert_called_once()
            mock_analytics.track_subscription.assert_called_once()
            assert "Newsletter" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_process_payment_no_payment(self, mock_message):
        """Should return early if no successful payment."""
        mock_message.successful_payment = None

        from app.services.bot import process_payment

        await process_payment(mock_message)

        mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_payment_forged_user_id(self, mock_message):
        """Should reject payment when payload user_id doesn't match payer."""
        with (
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_buffer.set_subscribed = AsyncMock()
            mock_settings.subscription_price_stars = 250

            # Payload says user 99999 but message is from user 12345
            mock_message.successful_payment = MagicMock()
            mock_message.successful_payment.invoice_payload = "sub:99999"
            mock_message.successful_payment.total_amount = 250

            from app.services.bot import process_payment

            await process_payment(mock_message)

            mock_buffer.set_subscribed.assert_not_called()
            mock_message.answer.assert_called_once()
            assert "validation failed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_process_payment_wrong_amount(self, mock_message):
        """Should reject payment when amount doesn't match expected price."""
        with (
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_buffer.set_subscribed = AsyncMock()
            mock_settings.subscription_price_stars = 250

            # User pays 100 instead of expected 250
            mock_message.successful_payment = MagicMock()
            mock_message.successful_payment.invoice_payload = "sub:12345"
            mock_message.successful_payment.total_amount = 100

            from app.services.bot import process_payment

            await process_payment(mock_message)

            mock_buffer.set_subscribed.assert_not_called()
            mock_message.answer.assert_called_once()
            assert "amount mismatch" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_process_payment_newsletter_wrong_amount(self, mock_message):
        """Should reject newsletter payment with wrong amount."""
        with (
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_news.get_available_news_topics = AsyncMock(return_value=["tech"])
            mock_news.subscribe_newsletter = AsyncMock()
            mock_settings.newsletter_price_stars = 250

            mock_message.successful_payment = MagicMock()
            mock_message.successful_payment.invoice_payload = "newsletter_sub:12345"
            mock_message.successful_payment.total_amount = 999

            from app.services.bot import process_payment

            await process_payment(mock_message)

            mock_news.subscribe_newsletter.assert_not_called()
            mock_message.answer.assert_called_once()
            assert "amount mismatch" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_process_payment_content_forged(self, mock_message):
        """Should reject content_sub payment with forged user_id."""
        with (
            patch("app.services.bot.content_subscription") as mock_content_sub,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_content_sub.set_content_subscription = AsyncMock()
            mock_settings.subscription_price_stars = 250

            mock_message.successful_payment = MagicMock()
            mock_message.successful_payment.invoice_payload = "content_sub:88888"
            mock_message.successful_payment.total_amount = 250

            from app.services.bot import process_payment

            await process_payment(mock_message)

            mock_content_sub.set_content_subscription.assert_not_called()
            mock_message.answer.assert_called_once()
            assert "validation failed" in mock_message.answer.call_args.args[0]


class TestNewsCommand:
    """Tests for /news command and subcommands."""

    @pytest.mark.asyncio
    async def test_news_status_not_subscribed(self, mock_message):
        """Should show subscribe prompt when not subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=False)
            mock_news.get_user_news_topics = AsyncMock(return_value=[])
            mock_news.get_newsletter_time = AsyncMock(return_value=None)

            mock_message.text = "/news"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Subscribe" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_status_subscribed(self, mock_message):
        """Should show status when subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech", "crypto"])
            mock_news.get_newsletter_time = AsyncMock(return_value=(9, 0))

            mock_message.text = "/news"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            response = mock_message.answer.call_args.args[0]
            assert "Active" in response
            assert "tech" in response

    @pytest.mark.asyncio
    async def test_news_subscribe(self, mock_message):
        """Should trigger newsletter subscribe flow."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.bot") as mock_bot,
            patch("app.services.bot.settings") as mock_settings,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=False)
            mock_bot.send_invoice = AsyncMock()
            mock_settings.telegram_stars_provider_token = ""

            mock_message.text = "/news subscribe"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_bot.send_invoice.assert_called_once()

    @pytest.mark.asyncio
    async def test_news_subscribe_already_subscribed(self, mock_message):
        """Should show message if already subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)

            mock_message.text = "/news subscribe"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "already subscribed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_unsubscribe(self, mock_message):
        """Should unsubscribe from newsletter."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.unsubscribe_newsletter = AsyncMock()

            mock_message.text = "/news unsubscribe"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_news.unsubscribe_newsletter.assert_called_once_with(12345)
            assert "Unsubscribed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_topics_show(self, mock_message):
        """Should show current topics."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.get_available_news_topics = AsyncMock(return_value=["tech", "news", "crypto"])
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech"])

            mock_message.text = "/news topics"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            response = mock_message.answer.call_args.args[0]
            assert "tech" in response

    @pytest.mark.asyncio
    async def test_news_topics_set(self, mock_message):
        """Should set new topics."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.set_user_news_topics = AsyncMock(return_value=True)
            mock_news.get_available_news_topics = AsyncMock(return_value=["tech", "crypto", "news"])

            mock_message.text = "/news topics tech,crypto"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_news.set_user_news_topics.assert_called_once_with(12345, ["tech", "crypto"])
            assert "updated" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_topics_invalid(self, mock_message):
        """Should show error for invalid topics."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.set_user_news_topics = AsyncMock(return_value=False)
            mock_news.get_available_news_topics = AsyncMock(return_value=["tech", "news"])

            mock_message.text = "/news topics invalid,topics"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Invalid" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_show(self, mock_message):
        """Should show current delivery time."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.get_newsletter_time = AsyncMock(return_value=(9, 30))

            mock_message.text = "/news time"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "09:30" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_not_set(self, mock_message):
        """Should show message when no time set."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.get_newsletter_time = AsyncMock(return_value=None)

            mock_message.text = "/news time"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "No delivery time" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_set(self, mock_message):
        """Should set delivery time."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.set_newsletter_time = AsyncMock(return_value=True)

            mock_message.text = "/news time 09:30"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_news.set_newsletter_time.assert_called_once_with(12345, 9, 30)
            assert "09:30" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_invalid_format(self, mock_message):
        """Should show error for invalid time format."""
        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/news time 9am"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Invalid" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_invalid_range(self, mock_message):
        """Should show error for time out of range."""
        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/news time 25:00"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Invalid" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_time_set_fails(self, mock_message):
        """Should show error when time set fails."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.set_newsletter_time = AsyncMock(return_value=False)

            mock_message.text = "/news time 09:00"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Failed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_now_not_subscribed(self, mock_message):
        """Should prompt to subscribe if not subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=False)

            mock_message.text = "/news now"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "premium" in mock_message.answer.call_args.args[0].lower()

    @pytest.mark.asyncio
    async def test_news_now_success(self, mock_message):
        """Should generate and send newsletter."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.newsletter") as mock_newsletter,
            patch("app.services.bot.bot") as mock_bot,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech"])
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={
                    "text": "Newsletter content",
                    "audio_path": None,
                }
            )
            mock_bot.send_audio = AsyncMock()

            mock_message.text = "/news now"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            # Should answer twice: "Generating..." and the newsletter content
            assert mock_message.answer.call_count == 2

    @pytest.mark.asyncio
    async def test_news_now_with_audio(self, mock_message):
        """Should send audio when available."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.newsletter") as mock_newsletter,
            patch("app.services.bot.bot") as mock_bot,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech"])
            mock_newsletter.generate_newsletter = AsyncMock(
                return_value={
                    "text": "Newsletter content",
                    "audio_path": "/tmp/audio.mp3",
                }
            )
            mock_bot.send_audio = AsyncMock()

            mock_message.text = "/news now"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_bot.send_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_news_now_no_content(self, mock_message):
        """Should show message when no content."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.newsletter") as mock_newsletter,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech"])
            mock_newsletter.generate_newsletter = AsyncMock(return_value={"text": None})

            mock_message.text = "/news now"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "No recent news" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_now_error(self, mock_message):
        """Should handle generation errors."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.news_aggregator") as mock_news,
            patch("app.services.bot.newsletter") as mock_newsletter,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_news.is_newsletter_subscriber = AsyncMock(return_value=True)
            mock_news.get_user_news_topics = AsyncMock(return_value=["tech"])
            mock_newsletter.generate_newsletter = AsyncMock(side_effect=Exception("Error"))

            mock_message.text = "/news now"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Error" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_unknown_command(self, mock_message):
        """Should show error for unknown subcommand."""
        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/news unknown"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            assert "Unknown" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_news_no_user(self, mock_message):
        """Should return early if no user."""
        mock_message.from_user = None

        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/news"

            from app.services.bot import cmd_news

            await cmd_news(mock_message)

            mock_message.answer.assert_not_called()


class TestTopicsCommand:
    """Tests for /topics command edge cases."""

    @pytest.mark.asyncio
    async def test_topics_no_user(self, mock_message):
        """Should return early if no user."""
        mock_message.from_user = None

        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/topics"

            from app.services.bot import cmd_topics

            await cmd_topics(mock_message)

            mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_topics_not_pro(self, mock_message):
        """Should show subscribe prompt when not pro."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=False)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)

            mock_message.text = "/topics"

            from app.services.bot import cmd_topics

            await cmd_topics(mock_message)

            assert "Pro feature" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_topics_add_invalid(self, mock_message):
        """Should show error for invalid topics."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.subscribe_to_topics = AsyncMock(return_value=[])
            mock_content.get_available_topics = AsyncMock(return_value=["tech", "crypto"])

            mock_message.text = "/topics add invalid"

            from app.services.bot import cmd_topics

            await cmd_topics(mock_message)

            assert "Invalid" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_topics_remove_not_subscribed(self, mock_message):
        """Should show message when not subscribed to topics."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.unsubscribe_from_topics = AsyncMock(return_value=0)

            mock_message.text = "/topics remove tech"

            from app.services.bot import cmd_topics

            await cmd_topics(mock_message)

            assert "weren't subscribed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_topics_invalid_action(self, mock_message):
        """Should show usage for invalid action."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)

            mock_message.text = "/topics invalid_action"

            from app.services.bot import cmd_topics

            await cmd_topics(mock_message)

            assert "Usage" in mock_message.answer.call_args.args[0]


class TestMydigestCommand:
    """Tests for /mydigest command edge cases."""

    @pytest.mark.asyncio
    async def test_mydigest_no_user(self, mock_message):
        """Should return early if no user."""
        mock_message.from_user = None

        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_mydigest_private_chat(self, mock_private_message):
        """Should prompt to use in group."""
        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_private_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_private_message)

            assert "group" in mock_private_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_mydigest_not_pro(self, mock_message):
        """Should show subscribe prompt when not pro."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=False)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            assert "Pro feature" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_mydigest_no_topics(self, mock_message):
        """Should prompt to add topics when none subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.get_user_topics = AsyncMock(return_value=[])

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            assert "No topics" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_mydigest_no_messages(self, mock_message):
        """Should show message when no messages."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(return_value=[])
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.get_user_topics = AsyncMock(return_value=["tech"])

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            assert "No messages" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_mydigest_no_matching_content(self, mock_message):
        """Should show message when no matching content."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hi", "ts": "2025-01-01"}]
            )
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.get_user_topics = AsyncMock(return_value=["tech"])
            mock_content.generate_personalized_digest = AsyncMock(return_value=None)

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            assert "No content matching" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_mydigest_error(self, mock_message):
        """Should handle errors gracefully."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_messages = AsyncMock(
                return_value=[{"user": "test", "text": "hi", "ts": "2025-01-01"}]
            )
            mock_content.is_content_subscriber = AsyncMock(return_value=False)
            mock_content.get_user_topics = AsyncMock(return_value=["tech"])
            mock_content.generate_personalized_digest = AsyncMock(side_effect=Exception("Error"))

            mock_message.text = "/mydigest"

            from app.services.bot import cmd_mydigest

            await cmd_mydigest(mock_message)

            assert "Error" in mock_message.answer.call_args.args[0]


class TestContentSubscribeCommand:
    """Tests for /content_subscribe command."""

    @pytest.mark.asyncio
    async def test_content_subscribe_no_user(self, mock_message):
        """Should return early if no user."""
        mock_message.from_user = None

        with patch("app.services.bot.analytics") as mock_analytics:
            mock_analytics.track_command = AsyncMock()

            mock_message.text = "/content_subscribe"

            from app.services.bot import cmd_content_subscribe

            await cmd_content_subscribe(mock_message)

            mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_content_subscribe_already_subscribed(self, mock_message):
        """Should show message if already subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.content_subscription") as mock_content,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_content.is_content_subscriber = AsyncMock(return_value=True)

            mock_message.text = "/content_subscribe"

            from app.services.bot import cmd_content_subscribe

            await cmd_content_subscribe(mock_message)

            assert "already have" in mock_message.answer.call_args.args[0]


class TestPeriodicCommand:
    """Tests for /periodic command variations."""

    @pytest.mark.asyncio
    async def test_periodic_not_subscribed(self, mock_message):
        """Should prompt to subscribe if not subscribed."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=False)

            mock_message.text = "/periodic"

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            assert "Pro feature" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_periodic_auto_with_threshold(self, mock_message):
        """Should set auto-trigger with custom threshold."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value=None)
            mock_buffer.set_periodic_schedule = AsyncMock(return_value=True)

            mock_message.text = "/periodic auto 150"

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            # Should clamp to valid range and use default interval
            mock_buffer.set_periodic_schedule.assert_called_once()
            assert "Auto-trigger" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_periodic_auto_fails(self, mock_message):
        """Should show error when auto-trigger setup fails."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value=None)
            mock_buffer.set_periodic_schedule = AsyncMock(return_value=False)

            mock_message.text = "/periodic auto"

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            assert "Failed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_periodic_invalid_interval(self, mock_message):
        """Should show error for invalid interval."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)

            mock_message.text = "/periodic 8h"  # Invalid

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            assert "Invalid" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_periodic_set_fails(self, mock_message):
        """Should show error when setting fails."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(return_value=None)
            mock_buffer.set_periodic_schedule = AsyncMock(return_value=False)

            mock_message.text = "/periodic daily"

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            assert "Failed" in mock_message.answer.call_args.args[0]

    @pytest.mark.asyncio
    async def test_periodic_with_auto_trigger_preserved(self, mock_message):
        """Should preserve auto-trigger when changing interval."""
        with (
            patch("app.services.bot.analytics") as mock_analytics,
            patch("app.services.bot.buffer") as mock_buffer,
        ):
            mock_analytics.track_command = AsyncMock()
            mock_buffer.is_subscribed = AsyncMock(return_value=True)
            mock_buffer.get_periodic_schedule = AsyncMock(
                return_value={
                    "auto_trigger": True,
                    "message_threshold": 50,
                    "enabled": True,
                }
            )
            mock_buffer.set_periodic_schedule = AsyncMock(return_value=True)

            mock_message.text = "/periodic 12h"

            from app.services.bot import cmd_periodic

            await cmd_periodic(mock_message)

            # Should preserve auto_trigger
            call_kwargs = mock_buffer.set_periodic_schedule.call_args.kwargs
            assert call_kwargs.get("auto_trigger") is True

            # Should mention auto-trigger in response
            assert "50 messages" in mock_message.answer.call_args.args[0]
