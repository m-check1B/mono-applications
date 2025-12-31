"""Telegram bot service using aiogram."""

import logging
from datetime import UTC, datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    ContentType,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from app.core.config import settings
from app.services.analytics import analytics
from app.services.buffer import buffer
from app.services.content_subscription import content_subscription
from app.services.news_aggregator import news_aggregator
from app.services.newsletter import newsletter
from app.services.payments import (
    payment_service,
    PaymentProvider,
    SubscriptionTier,
)
from app.services.language import (
    SUPPORTED_LANGUAGES,
    get_language_name,
    is_supported_language,
    get_language_distribution,
)
from app.services.summarizer import summarize_messages, summarize_with_topics, get_topic_stats

logger = logging.getLogger(__name__)

# Track bot startup time and last activity
_bot_start_time: datetime = datetime.now(UTC)
_last_activity: datetime = datetime.now(UTC)

# Initialize bot and dispatcher
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()
router = Router()


def _update_last_activity():
    """Update the last activity timestamp."""
    global _last_activity
    _last_activity = datetime.now(UTC)


def _is_admin(user_id: int) -> bool:
    """Check if user is a bot admin."""
    if not settings.admin_user_ids:
        return False
    admin_ids = [int(uid.strip()) for uid in settings.admin_user_ids.split(",") if uid.strip()]
    return user_id in admin_ids


def _format_uptime(start_time: datetime) -> str:
    """Format uptime as human-readable string."""
    delta = datetime.now(UTC) - start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


# ============================================================
# HANDLERS
# ============================================================


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    await analytics.track_command("start")
    await message.answer(
        "**Sumarium** — AI Chat Digest\n\n"
        "Turn 500 unread messages into a 30-second read.\n\n"
        "**Setup:**\n"
        "1. Add me to your group\n"
        "2. Grant admin access\n"
        "3. Send `/summary`\n\n"
        "Try it free — 3 digests/month included.",
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    _update_last_activity()
    await analytics.track_command("help")

    help_text = (
        "**Commands:**\n"
        "`/summary` — digest last 24 hours\n"
        "`/summary 6` — digest last 6 hours\n"
        "`/length short|medium|long` — set summary length\n"
        "`/language en|cs|auto` — set summary language\n"
        "`/topicsummary` — topic-organized digest\n"
        "`/status` — usage & subscription\n"
        "`/health` — bot status & uptime\n\n"
        "**Subscription:**\n"
        "`/subscribe` — view payment options\n"
        "`/subscribe_stars` — pay with Telegram Stars\n"
        "`/subscribe_stripe` — pay with card (auto-renew)\n"
        "`/manage` — view/cancel subscription\n\n"
        "**Automatic Digests (Pro):**\n"
        "`/schedule 09:00` — daily digest at time\n"
        "`/periodic 6h|12h|daily|weekly` — interval-based\n"
        "`/periodic auto 100` — after N messages\n"
        "`/unschedule` — disable scheduled digest\n\n"
        "**Topic Detection (Pro):**\n"
        "`/detecttopics` — see conversation threads\n"
        "`/topics` — manage topic subscriptions\n"
        "`/mydigest` — get personalized digest\n\n"
        "**How it works:**\n"
        "• AI extracts topics, decisions, links\n"
        "• Detects conversation threads\n"
        "• Multi-language support with auto-detection\n"
        "• Skips small talk and noise\n"
        "• Admin-only to prevent spam"
    )

    # Add admin commands if user is admin
    user_id = message.from_user.id if message.from_user else None
    if user_id and _is_admin(user_id):
        help_text += "\n\n**Admin Commands:**\n`/stats` — usage analytics"

    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("length"))
async def cmd_length(message: Message):
    """Set or view summary length preference.

    Usage:
    /length - Show current length and options
    /length short - Set to short (brief, 2-3 bullet points)
    /length medium - Set to medium (balanced)
    /length long - Set to long (comprehensive)
    """
    _update_last_activity()
    await analytics.track_command("length")
    chat_id = message.chat.id

    # Parse length argument
    text = message.text or ""
    parts = text.split()

    if len(parts) == 1:
        # Show current setting
        current = await buffer.get_summary_length(chat_id)
        length_descriptions = {
            "short": "Brief summaries (2-3 bullet points per section)",
            "medium": "Balanced summaries (covers main topics with details)",
            "long": "Comprehensive summaries (full context and quotes)",
        }

        await message.answer(
            f"**Summary Length Preference**\n\n"
            f"**Current:** {current.capitalize()}\n"
            f"_{length_descriptions[current]}_\n\n"
            f"**Options:**\n"
            f"`/length short` — Quick overview\n"
            f"`/length medium` — Balanced detail\n"
            f"`/length long` — Full analysis",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Set new length
    requested = parts[1].lower()
    if requested not in ("short", "medium", "long"):
        await message.answer(
            "**Invalid length.**\n\nChoose: `short`, `medium`, or `long`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    success = await buffer.set_summary_length(chat_id, requested)
    if success:
        emoji = {"short": "📝", "medium": "📄", "long": "📚"}.get(requested, "📄")
        await message.answer(
            f"{emoji} **Summary length set to {requested}!**\n\n"
            f"Your next `/summary` will use this preference.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("Failed to set length preference. Please try again.")


@router.message(Command("language", "lang"))
async def cmd_language(message: Message):
    """Set or view summary language preference.

    Usage:
    /language - Show current language and options
    /language auto - Auto-detect from messages
    /language en - Set to English
    /language cs - Set to Czech
    """
    _update_last_activity()
    await analytics.track_command("language")
    chat_id = message.chat.id

    # Parse language argument
    text = message.text or ""
    parts = text.split()

    if len(parts) == 1:
        # Show current setting and detected languages
        current = await buffer.get_summary_language(chat_id)
        current_name = get_language_name(current)

        # Get recent messages to show language distribution
        messages = await buffer.get_messages(chat_id, hours=24)
        distribution = get_language_distribution(messages) if messages else {}

        # Format distribution
        dist_text = ""
        if distribution:
            sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:5]
            dist_parts = [
                f"{get_language_name(lang)}: {count}"
                for lang, count in sorted_dist
                if lang not in ("unknown", "short")
            ]
            if dist_parts:
                dist_text = f"\n\n**Recent messages by language:**\n" + ", ".join(dist_parts)

        # Show popular language options
        popular = ["auto", "en", "cs", "sk", "de", "es", "fr", "ru", "uk", "pl"]

        await message.answer(
            f"**Summary Language Preference**\n\n"
            f"**Current:** {current_name}\n"
            f"_{get_summary_mode_description(current)}_"
            f"{dist_text}\n\n"
            f"**Set language:**\n"
            f"`/language auto` — detect from messages\n"
            f"`/language en` — English\n"
            f"`/language cs` — Czech\n"
            f"`/language de` — German\n"
            f"`/language ru` — Russian\n\n"
            f"_See `/language list` for all languages._",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    requested = parts[1].lower()

    # Handle 'list' command
    if requested == "list":
        lang_list = []
        for code, name in sorted(SUPPORTED_LANGUAGES.items(), key=lambda x: x[1]):
            if code != "auto":
                lang_list.append(f"`{code}` — {name}")

        await message.answer(
            f"**Supported Languages:**\n\n"
            + "\n".join(lang_list)
            + "\n\n_Use `/language CODE` to set._",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Validate language
    if not is_supported_language(requested):
        await message.answer(
            f"**Unknown language code:** `{requested}`\n\n"
            "Use `/language list` to see available options.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Set the language
    success = await buffer.set_summary_language(chat_id, requested)
    if success:
        lang_name = get_language_name(requested)
        emoji = "🌐" if requested == "auto" else "🗣️"
        await message.answer(
            f"{emoji} **Summary language set to {lang_name}!**\n\n"
            f"Your next `/summary` will use this preference.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("Failed to set language preference. Please try again.")


def get_summary_mode_description(language: str) -> str:
    """Get description for a language setting."""
    if language == "auto":
        return "Summaries will match the dominant language of messages."
    return f"Summaries will be written in {get_language_name(language)}."


@router.message(Command("health", "ping"))
async def cmd_health(message: Message):
    """Return bot health status, uptime, and last activity."""
    _update_last_activity()
    await analytics.track_command("health")

    # Check Redis connection
    redis_status = "disconnected"
    try:
        if buffer.redis:
            await buffer.redis.ping()
            redis_status = "connected"
    except Exception as e:
        logger.warning("Redis health check failed: %s", e)

    uptime = _format_uptime(_bot_start_time)
    last_activity_str = _last_activity.strftime("%Y-%m-%d %H:%M:%S UTC")
    started_at = _bot_start_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    health_text = (
        f"**Bot Health Status**\n\n"
        f"**Status:** OK\n"
        f"**Uptime:** {uptime}\n"
        f"**Started:** {started_at}\n"
        f"**Last Activity:** {last_activity_str}\n"
        f"**Redis:** {redis_status}"
    )

    await message.answer(health_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show bot usage statistics (admin only)."""
    await analytics.track_command("stats")
    user_id = message.from_user.id if message.from_user else None

    if not user_id or not _is_admin(user_id):
        await message.answer("This command is only available to bot administrators.")
        return

    # Gather statistics
    all_time = await analytics.get_stats()
    daily = await analytics.get_daily_stats()
    commands = await analytics.get_command_stats()

    # Format and send
    stats_message = analytics.format_stats_message(all_time, daily, commands)
    await message.answer(stats_message, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Check subscription status."""
    await analytics.track_command("status")
    chat_id = message.chat.id

    is_sub = await buffer.is_subscribed(chat_id)
    usage = await buffer.get_usage_count(chat_id)
    length_pref = await buffer.get_summary_length(chat_id)
    lang_pref = await buffer.get_summary_language(chat_id)
    lang_name = get_language_name(lang_pref)

    if is_sub:
        status_text = (
            f"**Status:** Pro (Unlimited)\n"
            f"**Summary length:** {length_pref.capitalize()}\n"
            f"**Summary language:** {lang_name}"
        )
    else:
        remaining = max(0, settings.free_summaries - usage)
        status_text = (
            f"**Status:** Free tier\n"
            f"**Summaries left:** {remaining}/{settings.free_summaries}\n"
            f"**Summary length:** {length_pref.capitalize()}\n"
            f"**Summary language:** {lang_name}"
        )

    await message.answer(status_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    """Generate chat summary."""
    await analytics.track_command("summary")
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    # Check if in group
    if message.chat.type == "private":
        await message.answer("Add me to a group first!")
        return

    # Check if user is admin (optional - can remove for public use)
    if not user_id:
        await message.answer("Could not verify admin status. Please try again.")
        return
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status not in ("administrator", "creator"):
            await message.answer("Only admins can request summaries.")
            return
    except Exception as e:
        logger.warning("Admin check failed for summary in chat %s: %s", chat_id, e)
        await message.answer("Could not verify admin status. Please try again.")
        return

    # Check usage limits
    can_use, reason = await buffer.can_summarize(chat_id)

    if not can_use:
        await message.answer(
            "**Free trial ended!**\n\n"
            f"Get unlimited summaries for {settings.subscription_price_stars} Stars (~$5/month).\n\n"
            "Use `/subscribe` to upgrade.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse hours from command (e.g., /summary 6)
    hours = 24
    if message.text:
        parts = message.text.split()
        if len(parts) > 1:
            try:
                hours = min(int(parts[1]), 24)  # Cap at 24h
            except ValueError:
                pass

    # Get messages and generate summary
    await message.answer("Analyzing messages...")

    messages = await buffer.get_messages(chat_id, hours=hours)

    if not messages:
        await message.answer(
            f"No messages found in the last {hours} hours.\n"
            "Make sure I have permission to read messages!"
        )
        return

    try:
        # Get user's length and language preferences
        length_pref = await buffer.get_summary_length(chat_id)
        lang_pref = await buffer.get_summary_language(chat_id)
        summary = await summarize_messages(messages, length=length_pref, language=lang_pref)

        # Track successful summary
        await analytics.track_summary(chat_id, user_id or 0, len(messages))
    except Exception as e:
        await analytics.track_error("summarization", str(e))
        await message.answer("Error generating summary. Please try again later.")
        return

    # Track usage only for free tier (after successful summary)
    is_subscribed = await buffer.is_subscribed(chat_id)
    if not is_subscribed:
        usage = await buffer.increment_usage(chat_id)
        remaining = max(0, settings.free_summaries - usage)
        summary += f"\n\n_Free summaries remaining: {remaining}_"

    await message.answer(summary, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("topicsummary", "tsummary"))
async def cmd_topicsummary(message: Message):
    """Generate topic-organized chat summary.

    Enhanced summary that detects conversation threads and organizes
    the digest by topic with participant info.
    """
    await analytics.track_command("topicsummary")
    _update_last_activity()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    # Check if in group
    if message.chat.type == "private":
        await message.answer("Add me to a group first!")
        return

    # Check if user is admin
    if not user_id:
        await message.answer("Could not verify admin status. Please try again.")
        return
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status not in ("administrator", "creator"):
            await message.answer("Only admins can request summaries.")
            return
    except Exception as e:
        logger.warning("Admin check failed for topicsummary in chat %s: %s", chat_id, e)
        await message.answer("Could not verify admin status. Please try again.")
        return

    # Check usage limits
    can_use, reason = await buffer.can_summarize(chat_id)

    if not can_use:
        await message.answer(
            "**Free trial ended!**\n\n"
            f"Get unlimited summaries for {settings.subscription_price_stars} Stars (~$5/month).\n\n"
            "Use `/subscribe` to upgrade.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse hours from command
    hours = 24
    if message.text:
        parts = message.text.split()
        if len(parts) > 1:
            try:
                hours = min(int(parts[1]), 24)
            except ValueError:
                pass

    await message.answer("Detecting topics and analyzing messages...")

    # Get messages
    messages = await buffer.get_messages(chat_id, hours=hours)

    if not messages:
        await message.answer(
            f"No messages found in the last {hours} hours.\n"
            "Make sure I have permission to read messages!"
        )
        return

    try:
        # Use enhanced topic summary
        summary = await summarize_with_topics(messages)

        await analytics.track_summary(chat_id, user_id or 0, len(messages))
    except Exception as e:
        await analytics.track_error("topicsummary", str(e))
        await message.answer("Error generating topic summary. Please try again later.")
        return

    # Track usage only for free tier
    is_subscribed = await buffer.is_subscribed(chat_id)
    if not is_subscribed:
        usage = await buffer.increment_usage(chat_id)
        remaining = max(0, settings.free_summaries - usage)
        summary += f"\n\n_Free summaries remaining: {remaining}_"

    await message.answer(summary, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("detecttopics"))
async def cmd_detecttopics(message: Message):
    """Show detected conversation topics without full summary.

    Useful for quickly seeing what topics were discussed.
    Pro feature.
    """
    await analytics.track_command("detecttopics")
    _update_last_activity()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    # Check if in group
    if message.chat.type == "private":
        await message.answer("Add me to a group first!")
        return

    # Check subscription (this is a Pro feature)
    if not await buffer.is_subscribed(chat_id):
        await message.answer(
            "**Topic detection is a Pro feature.**\n\n"
            "Subscribe with `/subscribe` to unlock.\n\n"
            "_Tip: `/summary` works on free tier!_",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse hours
    hours = 24
    if message.text:
        parts = message.text.split()
        if len(parts) > 1:
            try:
                hours = min(int(parts[1]), 24)
            except ValueError:
                pass

    await message.answer("Analyzing conversation threads...")

    messages = await buffer.get_messages(chat_id, hours=hours)

    if not messages or len(messages) < 3:
        await message.answer("Not enough messages to detect topics (need at least 3).")
        return

    try:
        stats = await get_topic_stats(messages)

        if stats["topic_count"] == 0:
            await message.answer("No distinct topics detected in recent messages.")
            return

        # Format topic stats
        response = f"**📊 {stats['topic_count']} Topics Detected**\n\n"

        for i, topic in enumerate(stats["topics"], 1):
            importance_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                topic["importance"], "⚪"
            )
            response += f"{importance_emoji} **{topic['name']}**\n"
            response += f"   _{topic['description']}_\n"
            response += f"   📝 {topic['message_count']} messages • "
            response += f"👥 {', '.join(topic['participants'][:3])}"
            if len(topic["participants"]) > 3:
                response += f" +{len(topic['participants']) - 3} more"
            response += "\n"
            if topic["has_questions"]:
                response += "   ❓ Has unanswered questions\n"
            if topic["has_action_items"]:
                response += "   ✅ Has action items\n"
            response += "\n"

        if stats["off_topic_count"] > 0:
            response += f"_({stats['off_topic_count']} off-topic messages filtered)_\n"

        response += f"\n_Analyzed {stats['total_messages']} messages in last {hours}h_"

        await message.answer(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Topic detection error: {e}")
        await message.answer("Error detecting topics. Please try again later.")


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Handle subscription purchase - shows payment options."""
    await analytics.track_command("subscribe")
    chat_id = message.chat.id

    # Check if already subscribed
    if await buffer.is_subscribed(chat_id):
        await message.answer(
            "**You already have an active subscription!**\n\n"
            "Use `/manage` to view your subscription details.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Check if Stripe is configured
    has_stripe = settings.stripe_api_key and settings.stripe_price_pro_monthly

    if has_stripe:
        # Show both payment options
        await message.answer(
            "**Choose your payment method:**\n\n"
            "**Option 1: Telegram Stars** ⭐\n"
            f"`/subscribe_stars` — {settings.subscription_price_stars} Stars (~$5/month)\n"
            "_One-time purchase, renew manually each month_\n\n"
            "**Option 2: Card Payment** 💳\n"
            "`/subscribe_stripe` — €4.99/month\n"
            "_Auto-renewing subscription via Stripe_\n\n"
            "`/subscribe_stripe yearly` — €47.99/year (20% off)\n"
            "_Best value for long-term users_",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        # Only Telegram Stars available
        await message.answer(
            f"**Get unlimited summaries for {settings.subscription_price_stars} Stars (~$5/month)**\n\n"
            "Use the button below to subscribe:",
            parse_mode=ParseMode.MARKDOWN,
        )
        # Send invoice using Telegram Stars
        await bot.send_invoice(
            chat_id=chat_id,
            title="TL;DR Bot Pro",
            description="Unlimited chat summaries for 1 month",
            payload=f"sub:{chat_id}",
            provider_token=settings.telegram_stars_provider_token,
            currency="XTR",
            prices=[LabeledPrice(label="1 Month Pro", amount=settings.subscription_price_stars)],
        )


@router.message(Command("subscribe_stars"))
async def cmd_subscribe_stars(message: Message):
    """Handle Telegram Stars subscription purchase."""
    await analytics.track_command("subscribe_stars")
    chat_id = message.chat.id

    # Check if already subscribed
    if await buffer.is_subscribed(chat_id):
        await message.answer(
            "**You already have an active subscription!**\n\n"
            "Use `/manage` to view your subscription details.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Send invoice using Telegram Stars
    await bot.send_invoice(
        chat_id=chat_id,
        title="TL;DR Bot Pro",
        description="Unlimited chat summaries for 1 month",
        payload=f"sub:{chat_id}",
        provider_token=settings.telegram_stars_provider_token,
        currency="XTR",
        prices=[LabeledPrice(label="1 Month Pro", amount=settings.subscription_price_stars)],
    )


@router.message(Command("subscribe_stripe"))
async def cmd_subscribe_stripe(message: Message):
    """Handle Stripe subscription purchase with recurring billing.

    Usage:
    /subscribe_stripe - Monthly subscription (€4.99/month)
    /subscribe_stripe yearly - Annual subscription (€47.99/year, 20% off)
    """
    await analytics.track_command("subscribe_stripe")
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    if not user_id:
        await message.answer("Error: Could not identify user.")
        return

    # Check if already subscribed
    if await buffer.is_subscribed(chat_id):
        await message.answer(
            "**You already have an active subscription!**\n\n"
            "Use `/manage` to view or cancel your subscription.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Check if Stripe is configured
    if not settings.stripe_api_key:
        await message.answer(
            "**Stripe payments are not available.**\n\n"
            "Please use `/subscribe_stars` to pay with Telegram Stars instead.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse billing interval from command
    text = message.text or ""
    parts = text.split()
    billing_interval = "monthly"
    if len(parts) > 1 and parts[1].lower() in ("yearly", "annual", "year"):
        billing_interval = "yearly"

    try:
        # Create Stripe checkout session
        result = await payment_service.create_subscription(
            provider=PaymentProvider.STRIPE,
            tier=SubscriptionTier.PRO,
            user_id=user_id,
            billing_interval=billing_interval,
        )

        checkout_url = result.get("checkout_url")
        if checkout_url:
            price_text = "€4.99/month" if billing_interval == "monthly" else "€47.99/year (20% off)"
            await message.answer(
                f"**Complete your subscription:**\n\n"
                f"**Plan:** Pro ({billing_interval})\n"
                f"**Price:** {price_text}\n\n"
                f"[Click here to pay securely via Stripe]({checkout_url})\n\n"
                "_Your subscription will auto-renew. Cancel anytime with `/manage`._",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        else:
            await message.answer("Error creating checkout session. Please try again.")

    except ValueError as e:
        logger.error(f"Stripe subscription error: {e}")
        await message.answer(
            f"**Stripe not fully configured.**\n\n"
            "Please use `/subscribe_stars` to pay with Telegram Stars instead.",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.error(f"Stripe subscription error: {e}")
        await message.answer("Error creating subscription. Please try again later.")


@router.message(Command("manage"))
async def cmd_manage(message: Message):
    """View and manage subscription status.

    Shows current subscription details and provides options to cancel.
    """
    await analytics.track_command("manage")
    _update_last_activity()
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    if not user_id:
        return

    # Check Telegram Stars subscription
    is_stars_sub = await buffer.redis.exists(buffer._sub_key(chat_id)) if buffer.redis else False

    # Check Stripe subscription
    stripe_sub = await buffer.get_stripe_subscription(chat_id)

    if is_stars_sub and not stripe_sub:
        # Telegram Stars subscription
        await message.answer(
            "**Your Subscription**\n\n"
            "**Status:** Active (Telegram Stars)\n"
            "**Type:** Monthly (manual renewal)\n\n"
            "_Your subscription will expire after 30 days. "
            "Use `/subscribe_stars` to renew._",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if stripe_sub:
        status = stripe_sub.get("status", "unknown")
        sub_id = stripe_sub.get("subscription_id", "")

        status_emoji = {
            "active": "✅",
            "trialing": "🔄",
            "past_due": "⚠️",
            "canceled": "❌",
            "unpaid": "❌",
        }.get(status, "❓")

        if status in ("active", "trialing"):
            await message.answer(
                f"**Your Subscription**\n\n"
                f"**Status:** {status_emoji} {status.title()}\n"
                f"**Type:** Stripe (auto-renewing)\n"
                f"**ID:** `{sub_id[:20]}...`\n\n"
                f"**Commands:**\n"
                f"`/manage cancel` — Cancel at end of billing period\n\n"
                f"_You can also manage your subscription at Stripe._",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer(
                f"**Your Subscription**\n\n"
                f"**Status:** {status_emoji} {status.title()}\n\n"
                f"Your subscription is no longer active.\n"
                f"Use `/subscribe` to start a new subscription.",
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    # No subscription
    usage = await buffer.get_usage_count(chat_id)
    remaining = max(0, settings.free_summaries - usage)

    await message.answer(
        "**No Active Subscription**\n\n"
        f"**Free tier:** {remaining}/{settings.free_summaries} summaries remaining\n\n"
        "Use `/subscribe` to unlock unlimited summaries.",
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(Command("manage cancel"))
async def cmd_manage_cancel(message: Message):
    """Cancel Stripe subscription at end of billing period."""
    await analytics.track_command("manage_cancel")
    chat_id = message.chat.id

    # Check for Stripe subscription
    stripe_sub = await buffer.get_stripe_subscription(chat_id)

    if not stripe_sub:
        await message.answer(
            "**No Stripe subscription found.**\n\n"
            "You can only cancel auto-renewing Stripe subscriptions here.\n"
            "Telegram Stars subscriptions expire automatically.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    sub_id = stripe_sub.get("subscription_id")
    status = stripe_sub.get("status")

    if status in ("canceled", "unpaid"):
        await message.answer(
            "**Subscription already cancelled.**\n\n"
            "Use `/subscribe` to start a new subscription.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    try:
        # Cancel at end of period (user keeps access until then)
        cancelled = await payment_service.cancel_subscription(
            provider=PaymentProvider.STRIPE,
            subscription_id=sub_id,
        )

        if cancelled:
            # Update local status
            await buffer.set_stripe_subscription(chat_id, sub_id, "canceled")

            await message.answer(
                "**Subscription cancelled.**\n\n"
                "Your access will continue until the end of your current billing period.\n"
                "You won't be charged again.\n\n"
                "_Changed your mind? Use `/subscribe_stripe` to resubscribe._",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer(
                "**Could not cancel subscription.**\n\n"
                "Please try again or manage your subscription directly on Stripe.",
                parse_mode=ParseMode.MARKDOWN,
            )

    except Exception as e:
        logger.error(f"Subscription cancellation error: {e}")
        await message.answer("Error cancelling subscription. Please try again later.")


@router.message(Command("schedule"))
async def cmd_schedule(message: Message):
    """Set up scheduled daily digest. Usage: /schedule HH:MM (24h UTC format)."""
    await analytics.track_command("schedule")
    chat_id = message.chat.id

    # Check subscription
    if not await buffer.is_subscribed(chat_id):
        await message.answer(
            "**Scheduled digests are a Pro feature.**\n\n"
            "Subscribe with `/subscribe` to unlock daily automated summaries.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse time from command
    time_str = None
    if message.text:
        parts = message.text.split()
        if len(parts) > 1:
            time_str = parts[1]

    if not time_str:
        # Show current schedule or usage
        schedule = await buffer.get_schedule(chat_id)
        if schedule:
            await message.answer(
                f"**Current schedule:** {schedule['hour']:02d}:{schedule['minute']:02d} UTC\n\n"
                "Use `/schedule HH:MM` to change or `/unschedule` to disable.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer(
                "**Set up a daily digest:**\n\n"
                "`/schedule 09:00` — receive summary at 9 AM UTC\n"
                "`/schedule 18:30` — receive summary at 6:30 PM UTC\n\n"
                "Times are in 24-hour UTC format.",
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    # Parse HH:MM format
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid format")
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
    except ValueError:
        await message.answer(
            "**Invalid time format.**\n\n"
            "Use 24-hour UTC format: `/schedule 09:00` or `/schedule 18:30`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Set schedule
    success = await buffer.set_schedule(chat_id, hour, minute)
    if success:
        await message.answer(
            f"**Daily digest scheduled!**\n\n"
            f"You'll receive a summary every day at {hour:02d}:{minute:02d} UTC.\n"
            "Use `/unschedule` to disable.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("Failed to set schedule. Please try again.")


@router.message(Command("unschedule"))
async def cmd_unschedule(message: Message):
    """Disable scheduled daily digest."""
    await analytics.track_command("unschedule")
    chat_id = message.chat.id

    removed = await buffer.remove_schedule(chat_id)
    if removed:
        await message.answer(
            "**Scheduled digest disabled.**\n\nUse `/schedule HH:MM` to enable again.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("No scheduled digest was active.")


@router.message(Command("periodic"))
async def cmd_periodic(message: Message):
    """Set up periodic automatic digests.

    Usage:
    /periodic - Show current settings and options
    /periodic 6h - Every 6 hours
    /periodic 12h - Every 12 hours
    /periodic daily - Every 24 hours
    /periodic weekly - Every week
    /periodic auto 100 - Auto-trigger after 100 messages
    /periodic off - Disable periodic digests
    """
    await analytics.track_command("periodic")
    _update_last_activity()
    chat_id = message.chat.id

    # Check subscription
    if not await buffer.is_subscribed(chat_id):
        await message.answer(
            "**Periodic digests are a Pro feature.**\n\n"
            "Subscribe with `/subscribe` to unlock automatic summaries.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse arguments
    text = message.text or ""
    parts = text.split()

    if len(parts) == 1:
        # Show current settings
        settings = await buffer.get_periodic_schedule(chat_id)
        last_digest = await buffer.get_last_digest_time(chat_id)

        if settings and settings.get("enabled"):
            interval = settings.get("interval_hours", 24)
            interval_names = {6: "6 hours", 12: "12 hours", 24: "daily", 168: "weekly"}
            interval_str = interval_names.get(interval, f"{interval}h")

            auto_str = ""
            if settings.get("auto_trigger"):
                threshold = settings.get("message_threshold", 100)
                auto_str = f"\n**Auto-trigger:** after {threshold} messages"

            last_str = ""
            if last_digest:
                last_str = f"\n**Last digest:** {last_digest.strftime('%Y-%m-%d %H:%M')} UTC"

            await message.answer(
                f"**Periodic Digest Settings**\n\n"
                f"**Interval:** {interval_str}{auto_str}{last_str}\n\n"
                f"**Change interval:**\n"
                f"`/periodic 6h` — every 6 hours\n"
                f"`/periodic 12h` — every 12 hours\n"
                f"`/periodic daily` — once per day\n"
                f"`/periodic weekly` — once per week\n\n"
                f"**Activity trigger:**\n"
                f"`/periodic auto 100` — also trigger after 100 msgs\n\n"
                f"`/periodic off` — disable periodic digests",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer(
                "**Periodic Automatic Digests**\n\n"
                "Get automatic summaries at regular intervals or when activity spikes.\n\n"
                "**Set interval:**\n"
                "`/periodic 6h` — every 6 hours\n"
                "`/periodic 12h` — every 12 hours\n"
                "`/periodic daily` — once per day\n"
                "`/periodic weekly` — once per week\n\n"
                "**Activity trigger:**\n"
                "`/periodic auto 100` — trigger after 100 messages\n\n"
                "_Pro feature: requires active subscription_",
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    arg = parts[1].lower()

    # Handle disable
    if arg == "off":
        removed = await buffer.remove_periodic_schedule(chat_id)
        if removed:
            await message.answer(
                "**Periodic digests disabled.**\n\nUse `/periodic` to set up again.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer("Periodic digests were not enabled.")
        return

    # Handle auto-trigger
    if arg == "auto":
        threshold = 100
        if len(parts) > 2:
            try:
                threshold = int(parts[2])
                threshold = max(20, min(500, threshold))  # Clamp to 20-500
            except ValueError:
                pass

        # Get current interval or use default
        current = await buffer.get_periodic_schedule(chat_id)
        interval = current.get("interval_hours", 24) if current else 24

        success = await buffer.set_periodic_schedule(
            chat_id, interval, auto_trigger=True, message_threshold=threshold
        )

        if success:
            await message.answer(
                f"**Auto-trigger enabled!**\n\n"
                f"You'll get a digest when {threshold} messages accumulate.\n"
                f"_Plus regular interval digests every {interval}h_",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer("Failed to enable auto-trigger. Please try again.")
        return

    # Handle interval settings
    interval_map = {"6h": 6, "12h": 12, "daily": 24, "24h": 24, "weekly": 168, "week": 168}
    interval = interval_map.get(arg)

    if not interval:
        await message.answer(
            "**Invalid interval.**\n\n"
            "Options: `6h`, `12h`, `daily`, `weekly`\n"
            "Or: `/periodic auto 100` for activity-based",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Check if auto-trigger was previously enabled
    current = await buffer.get_periodic_schedule(chat_id)
    auto_trigger = current.get("auto_trigger", False) if current else False
    threshold = current.get("message_threshold", 100) if current else 100

    success = await buffer.set_periodic_schedule(
        chat_id, interval, auto_trigger=auto_trigger, message_threshold=threshold
    )

    if success:
        interval_names = {6: "6 hours", 12: "12 hours", 24: "24 hours", 168: "7 days"}
        interval_str = interval_names.get(interval, f"{interval}h")

        auto_note = ""
        if auto_trigger:
            auto_note = f"\n_Also triggers after {threshold} messages_"

        await message.answer(
            f"**Periodic digest enabled!**\n\n"
            f"You'll receive automatic summaries every {interval_str}.{auto_note}\n\n"
            f"Use `/periodic off` to disable.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("Failed to set periodic schedule. Please try again.")


@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    """Handle pre-checkout validation."""
    await query.answer(ok=True)

def _parse_payment_user_id(payload: str, prefix: str) -> int | None:
    if not payload.startswith(prefix):
        return None
    _, _, raw_id = payload.partition(":")
    if not raw_id:
        return None
    try:
        return int(raw_id)
    except ValueError:
        return None


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_payment(message: Message):
    """Handle successful payment with validation to prevent forged payments."""
    if not message.successful_payment:
        return

    payment = message.successful_payment
    payload = payment.invoice_payload
    total_amount = payment.total_amount

    if payload.startswith("sub:"):
        user_id = _parse_payment_user_id(payload, "sub:")
        if user_id is None:
            logger.warning("Invalid subscription payload: %s", payload)
            await message.answer("Error: Payment validation failed. Please contact support.")
            return

        # Security: Validate user_id matches payer to prevent forged payments
        # For group subscriptions (negative user_id), validate against chat.id
        # For user subscriptions (positive user_id), validate against from_user.id
        if user_id < 0:
            # Group payment - payload must match chat ID
            if user_id != message.chat.id:
                logger.warning(
                    f"Payment forgery detected: group chat_id {user_id} != actual chat.id {message.chat.id}"
                )
                await message.answer("Error: Payment validation failed. Please contact support.")
                return
        else:
            # User payment - payload must match user ID
            if not message.from_user or user_id != message.from_user.id:
                logger.warning(
                    f"Payment forgery detected: payload user_id {user_id} != payer_id {message.from_user.id if message.from_user else None}"
                )
                await message.answer("Error: Payment validation failed. Please contact support.")
                return

        # Security: Validate payment amount matches expected price
        expected_price = settings.subscription_price_stars
        if total_amount != expected_price:
            logger.warning(f"Invalid payment amount: {total_amount} != expected {expected_price}")
            await message.answer("Error: Payment amount mismatch. Please contact support.")
            return

        await buffer.set_subscribed(user_id, months=1)

        # Track subscription analytics
        await analytics.track_subscription(user_id)

        await message.answer(
            "**Thank you for subscribing!**\n\n"
            "You now have unlimited summaries for 1 month.\n"
            "Use `/summary` anytime!",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif payload.startswith("content_sub:"):
        user_id = _parse_payment_user_id(payload, "content_sub:")
        if user_id is None:
            logger.warning("Invalid content subscription payload: %s", payload)
            await message.answer("Error: Payment validation failed. Please contact support.")
            return

        # Security: Validate user_id matches payer to prevent forged payments
        # content_sub is user-only (no group subscriptions)
        if not message.from_user or user_id != message.from_user.id:
            logger.warning(
                f"Payment forgery detected: payload user_id {user_id} != payer_id {message.from_user.id if message.from_user else None}"
            )
            await message.answer("Error: Payment validation failed. Please contact support.")
            return

        # Security: Content Pro uses same price as regular subscription
        expected_price = settings.subscription_price_stars
        if total_amount != expected_price:
            logger.warning(f"Invalid payment amount: {total_amount} != expected {expected_price}")
            await message.answer("Error: Payment amount mismatch. Please contact support.")
            return

        await content_subscription.set_content_subscription(user_id, months=1)

        # Track subscription analytics
        await analytics.track_subscription(message.chat.id)

        await message.answer(
            "**Thank you for your Content Subscription!**\n\n"
            "You now have access to personalized topic digests.\n\n"
            "**Get started:**\n"
            "1. Use `/topics add tech,crypto,deals` to subscribe to topics\n"
            "2. Use `/mydigest` to get your personalized digest",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif payload.startswith("newsletter_sub:"):
        user_id = _parse_payment_user_id(payload, "newsletter_sub:")
        if user_id is None:
            logger.warning("Invalid newsletter subscription payload: %s", payload)
            await message.answer("Error: Payment validation failed. Please contact support.")
            return

        # Security: Validate user_id matches payer to prevent forged payments
        # newsletter_sub is user-only (no group subscriptions)
        if not message.from_user or user_id != message.from_user.id:
            logger.warning(
                f"Payment forgery detected: payload user_id {user_id} != payer_id {message.from_user.id if message.from_user else None}"
            )
            await message.answer("Error: Payment validation failed. Please contact support.")
            return

        # Security: Validate payment amount matches newsletter price
        expected_price = settings.newsletter_price_stars
        if total_amount != expected_price:
            logger.warning(f"Invalid payment amount: {total_amount} != expected {expected_price}")
            await message.answer("Error: Payment amount mismatch. Please contact support.")
            return

        # Subscribe to newsletter with default topics
        default_topics = await news_aggregator.get_available_news_topics()
        await news_aggregator.subscribe_newsletter(user_id, default_topics)

        # Track subscription analytics
        await analytics.track_subscription(message.chat.id)

        await message.answer(
            "**Welcome to TL;DR Newsletter!** 🎉\n\n"
            "You'll receive daily AI-generated news digests.\n\n"
            "**Get started:**\n"
            "• Use `/news topics` to customize your topics\n"
            "• Use `/news time 09:00` to set delivery time\n"
            "• Use `/news now` to get your first digest now",
            parse_mode=ParseMode.MARKDOWN,
        )


# ============================================================
# CONTENT SUBSCRIPTION HANDLERS
# ============================================================


@router.message(Command("topics"))
async def cmd_topics(message: Message):
    """Manage topic subscriptions for personalized digests.

    Usage:
    /topics - Show available topics and current subscriptions
    /topics add crypto,tech - Subscribe to topics
    /topics remove crypto - Unsubscribe from a topic
    """
    await analytics.track_command("topics")
    _update_last_activity()

    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return

    # Check subscription status
    is_pro = await buffer.is_subscribed(
        message.chat.id
    ) or await content_subscription.is_content_subscriber(user_id)
    if not is_pro:
        await message.answer(
            "**Content subscriptions are a Pro feature.**\n\n"
            "Subscribe with `/subscribe` to unlock personalized topic digests.\n\n"
            "**Available topics:** tech, crypto, deals, news, jobs, events, learning, finance",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Parse command arguments
    text = message.text or ""
    parts = text.split(maxsplit=2)

    # Show current subscriptions if no arguments
    if len(parts) == 1:
        available = await content_subscription.get_available_topics()
        current = await content_subscription.get_user_topics(user_id)

        current_str = ", ".join(current) if current else "None"
        available_str = ", ".join(available)

        await message.answer(
            f"**Your Topic Subscriptions**\n\n"
            f"**Subscribed:** {current_str}\n\n"
            f"**Available:** {available_str}\n\n"
            "**Commands:**\n"
            "`/topics add tech,crypto` — subscribe to topics\n"
            "`/topics remove tech` — unsubscribe from topic\n"
            "`/mydigest` — get personalized digest",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    action = parts[1].lower()
    topics_str = parts[2] if len(parts) > 2 else ""
    topics = [t.strip().lower() for t in topics_str.split(",") if t.strip()]

    if action == "add" and topics:
        subscribed = await content_subscription.subscribe_to_topics(user_id, topics)
        if subscribed:
            # Also activate content subscription if not already
            await content_subscription.set_content_subscription(user_id, months=1)
            await message.answer(
                f"**Subscribed to:** {', '.join(subscribed)}\n\n"
                "Use `/mydigest` to get your personalized digest!",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            available = await content_subscription.get_available_topics()
            await message.answer(
                f"**Invalid topics.** Available: {', '.join(available)}",
                parse_mode=ParseMode.MARKDOWN,
            )

    elif action == "remove" and topics:
        removed = await content_subscription.unsubscribe_from_topics(user_id, topics)
        if removed > 0:
            await message.answer(
                f"**Unsubscribed from {removed} topic(s).**", parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.answer("You weren't subscribed to those topics.")

    else:
        await message.answer(
            "**Usage:**\n"
            "`/topics` — show subscriptions\n"
            "`/topics add tech,crypto` — subscribe\n"
            "`/topics remove tech` — unsubscribe",
            parse_mode=ParseMode.MARKDOWN,
        )


@router.message(Command("mydigest"))
async def cmd_mydigest(message: Message):
    """Generate personalized digest based on subscribed topics."""
    await analytics.track_command("mydigest")
    _update_last_activity()

    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id

    if not user_id:
        return

    # Check if in group
    if message.chat.type == "private":
        await message.answer(
            "Use this command in a group to get a digest of messages matching your topics.\n\n"
            "**Tip:** Use `/topics` to manage your subscriptions."
        )
        return

    # Check subscription
    is_pro = await buffer.is_subscribed(
        chat_id
    ) or await content_subscription.is_content_subscriber(user_id)
    if not is_pro:
        await message.answer(
            "**Personalized digests are a Pro feature.**\n\nSubscribe with `/subscribe` to unlock.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Get user's topics
    user_topics = await content_subscription.get_user_topics(user_id)
    if not user_topics:
        await message.answer(
            "**No topics subscribed!**\n\n"
            "Use `/topics add tech,crypto,deals` to subscribe to topics first.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await message.answer(f"Generating your {', '.join(user_topics)} digest...")

    # Get messages from buffer
    messages = await buffer.get_messages(chat_id, hours=24)

    if not messages:
        await message.answer(
            "No messages found in the last 24 hours.\nMake sure I have permission to read messages!"
        )
        return

    try:
        digest = await content_subscription.generate_personalized_digest(user_id, messages)

        if digest:
            await content_subscription.update_last_digest(user_id)
            await message.answer(digest, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.answer(
                f"No content matching your topics ({', '.join(user_topics)}) found in recent messages.\n\n"
                "Try:\n"
                "• Using `/summary` for a full digest\n"
                "• Adding more topics with `/topics add`"
            )

    except Exception as e:
        logger.error(f"Personalized digest error: {e}")
        await message.answer("Error generating personalized digest. Please try again later.")


@router.message(Command("content_subscribe"))
async def cmd_content_subscribe(message: Message):
    """Subscribe to content subscription tier (higher tier than basic Pro)."""
    await analytics.track_command("content_subscribe")
    _update_last_activity()

    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat.id

    if not user_id:
        return

    # Check if already subscribed
    if await content_subscription.is_content_subscriber(user_id):
        await message.answer(
            "**You already have Content Subscription!**\n\n"
            "Use `/topics` to manage subscriptions and `/mydigest` for personalized digests.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Send invoice for content subscription (400 Stars for premium tier)
    await bot.send_invoice(
        chat_id=chat_id,
        title="TL;DR Content Subscription",
        description="Personalized topic digests across all your groups",
        payload=f"content_sub:{user_id}",
        provider_token=settings.telegram_stars_provider_token,  # Configurable: empty for Telegram Stars, or token for Stripe/etc.
        currency="XTR",
        prices=[LabeledPrice(label="1 Month Content Pro", amount=400)],
    )


@router.message(F.text)
async def handle_message(message: Message):
    """Store all text messages in buffer."""
    if message.chat.type == "private":
        return  # Don't buffer private messages

    if not message.text or not message.from_user:
        return

    # Track message analytics
    await analytics.track_message(message.chat.id, message.from_user.id)

    # Get username or first name
    user_name = message.from_user.username or message.from_user.first_name or "Unknown"

    await buffer.add_message(
        chat_id=message.chat.id, user_name=user_name, text=message.text, timestamp=message.date
    )


# ============================================================
# NEWSLETTER COMMANDS
# ============================================================


@router.message(Command("news"))
async def cmd_news(message: Message):
    """Handle newsletter commands.

    Usage:
    /news - Show newsletter status
    /news subscribe - Subscribe to newsletter
    /news unsubscribe - Unsubscribe
    /news topics tech,crypto - Set topics
    /news topics - Show current topics
    /news time 09:00 - Set delivery time (UTC)
    /news now - Get newsletter immediately
    """
    await analytics.track_command("news")
    _update_last_activity()

    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return

    # Parse command arguments
    text = message.text or ""
    parts = text.split(maxsplit=2)

    if len(parts) == 1:
        # Show status
        is_sub = await news_aggregator.is_newsletter_subscriber(user_id)
        topics = await news_aggregator.get_user_news_topics(user_id)
        delivery_time = await news_aggregator.get_newsletter_time(user_id)

        if is_sub:
            time_str = (
                f"{delivery_time[0]:02d}:{delivery_time[1]:02d} UTC" if delivery_time else "Not set"
            )
            status_text = (
                f"**Newsletter Status:** Active\n\n"
                f"**Topics:** {', '.join(topics)}\n"
                f"**Delivery:** {time_str}\n\n"
                f"**Commands:**\n"
                f"`/news topics tech,crypto` — customize topics\n"
                f"`/news time 09:00` — set delivery time\n"
                f"`/news now` — get newsletter now\n"
                f"`/news unsubscribe` — cancel subscription"
            )
        else:
            status_text = (
                "**TL;DR Newsletter**\n\n"
                "Get daily AI-generated summaries of news in topics you care about.\n\n"
                "**Features:**\n"
                "• Daily text digest\n"
                "• Audio version (listen on the go)\n"
                "• Personalized topics\n\n"
                "**Subscribe:** `/news subscribe` (250 Stars/month)"
            )

        await message.answer(status_text, parse_mode=ParseMode.MARKDOWN)
        return

    action = parts[1].lower()
    arg = parts[2] if len(parts) > 2 else ""

    if action == "subscribe":
        # Subscribe to newsletter
        await _handle_newsletter_subscribe(message, user_id)

    elif action == "unsubscribe":
        await _handle_newsletter_unsubscribe(message, user_id)

    elif action == "topics":
        await _handle_newsletter_topics(message, user_id, arg)

    elif action == "time":
        await _handle_newsletter_time(message, user_id, arg)

    elif action == "now":
        await _handle_newsletter_now(message, user_id)

    else:
        await message.answer(
            "**Unknown command.**\n\nUse `/news` to see options.", parse_mode=ParseMode.MARKDOWN
        )


async def _handle_newsletter_subscribe(message: Message, user_id: int):
    """Handle newsletter subscription."""
    # Check if already subscribed
    if await news_aggregator.is_newsletter_subscriber(user_id):
        await message.answer(
            "**You're already subscribed to the newsletter!**\n\n"
            "Use `/news topics` to customize your topics.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Send invoice
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="TL;DR Newsletter",
        description="Daily AI-generated news digests with audio",
        payload=f"newsletter_sub:{user_id}",
        provider_token=settings.telegram_stars_provider_token,  # Configurable: empty for Telegram Stars, or token for Stripe/etc.
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="1 Month Newsletter", amount=250)],
    )


async def _handle_newsletter_unsubscribe(message: Message, user_id: int):
    """Handle newsletter unsubscription."""
    await news_aggregator.unsubscribe_newsletter(user_id)
    await message.answer(
        "**Unsubscribed from newsletter.**\n\n"
        "We hope you enjoyed your daily digests. Come back anytime!",
        parse_mode=ParseMode.MARKDOWN,
    )


async def _handle_newsletter_topics(message: Message, user_id: int, arg: str):
    """Handle newsletter topic customization."""
    available = await news_aggregator.get_available_news_topics()

    if not arg:
        # Show current topics
        current = await news_aggregator.get_user_news_topics(user_id)
        current_str = ", ".join(current)
        available_str = ", ".join(available)

        help_text = (
            f"**Your Newsletter Topics**\n\n"
            f"**Subscribed:** {current_str}\n\n"
            f"**Available:** {available_str}\n\n"
            f"**Set topics:** `/news topics tech,crypto,news`"
        )
        await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Parse topics
    topics = [t.strip().lower() for t in arg.split(",") if t.strip()]

    success = await news_aggregator.set_user_news_topics(user_id, topics)

    if success:
        await message.answer(
            f"**Topics updated:** {', '.join(topics)}\n\n"
            "Your next newsletter will focus on these topics.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer(
            f"**Invalid topics.**\n\n"
            f"Available: {', '.join(available)}\n"
            f"Usage: `/news topics tech,crypto,news`",
            parse_mode=ParseMode.MARKDOWN,
        )


async def _handle_newsletter_time(message: Message, user_id: int, arg: str):
    """Handle newsletter delivery time setting."""
    if not arg:
        # Show current time
        delivery_time = await news_aggregator.get_newsletter_time(user_id)
        if delivery_time:
            time_str = f"{delivery_time[0]:02d}:{delivery_time[1]:02d} UTC"
            await message.answer(
                f"**Your delivery time:** {time_str}\n\n"
                "Use `/news time HH:MM` to change (24h UTC format).",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await message.answer(
                "**No delivery time set.**\n\n"
                "Use `/news time HH:MM` to set your preferred time (24h UTC).\n"
                "Example: `/news time 09:00` for 9 AM UTC",
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    # Parse time
    try:
        parts = arg.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid format")
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid range")
    except ValueError:
        await message.answer(
            "**Invalid time format.**\n\n"
            "Use 24-hour UTC format: `/news time 09:00` or `/news time 18:30`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    success = await news_aggregator.set_newsletter_time(user_id, hour, minute)

    if success:
        await message.answer(
            f"**Delivery time set:** {hour:02d}:{minute:02d} UTC\n\n"
            "You'll receive your newsletter daily at this time.",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.answer("Failed to set delivery time. Please try again.")


async def _handle_newsletter_now(message: Message, user_id: int):
    """Handle immediate newsletter generation."""
    # Check if subscribed
    if not await news_aggregator.is_newsletter_subscriber(user_id):
        await message.answer(
            "**Newsletter is a premium feature.**\n\n"
            "Subscribe with `/news subscribe` to get daily news digests.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await message.answer("Generating your newsletter...")

    # Get user's topics
    topics = await news_aggregator.get_user_news_topics(user_id)

    try:
        result = await newsletter.generate_newsletter(topics, include_audio=True)

        if not result.get("text"):
            await message.answer("No recent news found for your topics. Try again later.")
            return

        # Send text digest
        await message.answer(result["text"], parse_mode=ParseMode.MARKDOWN)

        # Send audio if available
        audio_path = result.get("audio_path")
        if audio_path:
            try:
                from aiogram.types import FSInputFile

                audio_file = FSInputFile(audio_path)
                await bot.send_audio(
                    chat_id=message.chat.id,
                    audio=audio_file,
                    caption="🎧 Audio version of your newsletter",
                )
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")

    except Exception as e:
        logger.error(f"Newsletter generation error: {e}")
        await message.answer("Error generating newsletter. Please try again later.")


# Register router
dp.include_router(router)


async def setup_webhook(webhook_url: str, secret_token: str = None):
    """Set up webhook for the bot."""
    await bot.set_webhook(webhook_url, secret_token=secret_token)
    logger.info(f"Webhook set to {webhook_url}")


async def remove_webhook():
    """Remove webhook."""
    await bot.delete_webhook()


async def process_update(update_data: dict):
    """Process incoming webhook update."""
    from aiogram.types import Update

    update = Update.model_validate(update_data)
    await dp.feed_update(bot, update)
