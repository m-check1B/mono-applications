"""Telegram bot command handlers for Sense by Kraliki."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
    ContentType,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.core.config import settings
from app.core.analytics import analytics
from app.services.sensitivity import calculate_sensitivity, get_quick_score
from app.services.dreams import analyze_dream
from app.services.biorhythm import calculate_biorhythm, get_biorhythm_forecast
from app.services.remedies import (
    get_remedies_for_sensitivity,
    get_sleep_remedies,
    get_focus_remedies,
    get_emotional_remedies,
)
from app.data.astro import get_astro_data, get_yearly_forecast
from app.services.storage import storage


router = Router()
logger = logging.getLogger(__name__)

# Track bot startup time and last activity
_bot_start_time: datetime = datetime.now(timezone.utc)
_last_activity: datetime = datetime.now(timezone.utc)


def _update_last_activity():
    """Update the last activity timestamp."""
    global _last_activity
    _last_activity = datetime.now(timezone.utc)


def _format_uptime(start_time: datetime) -> str:
    """Format uptime as human-readable string."""
    delta = datetime.now(timezone.utc) - start_time
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


# FSM States
class UserStates(StatesGroup):
    waiting_for_dream = State()
    waiting_for_birthdate = State()
    waiting_for_location = State()


# User data cache (deprecated - using storage service)
# user_data = {}


def _parse_payment_payload(payload: str) -> tuple[str, int] | None:
    if not payload:
        return None
    parts = payload.split(":", 1)
    if len(parts) != 2:
        return None
    plan, user_id_str = parts[0].strip(), parts[1].strip()
    if plan not in ("sensitive", "empath"):
        return None
    try:
        return plan, int(user_id_str)
    except ValueError:
        return None


def _expected_stars_amount(plan: str) -> int:
    return (
        settings.sensitive_price_stars
        if plan == "sensitive"
        else settings.empath_price_stars
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Welcome message and guided onboarding."""
    user_id = message.from_user.id
    await analytics.track_command("start", user_id)

    # Check if user is already set up
    user_info = await storage.get_user(user_id)
    has_birthdate = "birth_date" in user_info
    has_location = "latitude" in user_info and "longitude" in user_info

    if has_birthdate and has_location:
        # User already set up - show welcome back message
        welcome = """Welcome back to Sense by Kraliki!

Your profile is set up. Try these commands:
/sense - Get your sensitivity score now
/dream - Analyze your dream
/bio - View your biorhythm
/astro - Today's astrological influences
/remedies - Get holistic recommendations

Type /help for all commands."""
        await message.answer(welcome, parse_mode="Markdown")
        return

    # New user or incomplete profile - start guided onboarding
    welcome = """Welcome to Sense by Kraliki - Your Sensitivity Companion

I help you understand how cosmic, earth, and environmental factors affect your wellbeing.

**Quick Setup** (30 seconds)
For the best experience, I need two things:
1. Your birth date (for biorhythm & astro)
2. Your location (for weather impact)

You can skip and add later, but personalized readings work best!"""

    # Create onboarding keyboard
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Setup Now (Recommended)", callback_data="onboard_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Skip → Try /sense", callback_data="onboard_skip"
                )
            ],
        ]
    )

    await message.answer(welcome, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "onboard_start")
async def onboard_start(callback: CallbackQuery, state: FSMContext):
    """Start guided onboarding flow."""
    await callback.answer()

    # Progress indicator
    progress = """**Setup Progress: 1/2**

Please enter your **birth date** in format YYYY-MM-DD

Example: `1990-05-15`

(This enables biorhythm charts and personalized astrology)"""

    await callback.message.answer(progress, parse_mode="Markdown")
    await state.set_state(UserStates.waiting_for_birthdate)


@router.callback_query(F.data == "onboard_skip")
async def onboard_skip(callback: CallbackQuery):
    """Skip onboarding and go straight to trying the bot."""
    await callback.answer()

    skip_msg = """No problem! You can set up later with:
/setbirthday YYYY-MM-DD
/setlocation LAT,LON

Try /sense now to see current cosmic conditions!"""

    await callback.message.answer(skip_msg, parse_mode="Markdown")


@router.message(Command("sense"))
async def cmd_sense(message: Message):
    """Get current sensitivity score."""
    user_id = message.from_user.id
    await analytics.track_command("sense", user_id)
    await analytics.track_chart_type("sense", user_id)

    await message.answer("Calculating your sensitivity score...")

    # Get user location if available
    lat, lon = None, None
    birth_date = None

    user_info = await storage.get_user(user_id)
    if user_info:
        lat = user_info.get("latitude")
        lon = user_info.get("longitude")
        birth_date = user_info.get("birth_date")

    try:
        report = await calculate_sensitivity(
            latitude=lat, longitude=lon, birth_date=birth_date
        )

        response = report.to_summary()
        await message.answer(f"```\n{response}\n```", parse_mode="Markdown")

    except Exception:
        logger.exception("Error calculating sensitivity for user_id=%s", user_id)
        await analytics.track_error("sensitivity_calculation", "sense")
        await message.answer(
            "Sorry, I couldn't calculate your sensitivity right now. Please try again soon."
        )


@router.message(Command("dream"))
async def cmd_dream(message: Message, state: FSMContext):
    """Start dream analysis flow."""
    await analytics.track_command("dream", message.from_user.id)

    # Check if dream text is provided with command
    text = message.text.replace("/dream", "").strip()

    if text:
        await process_dream(message, text)
    else:
        await message.answer(
            "Tell me about your dream. Describe it in as much detail as you remember - "
            "the setting, characters, actions, emotions, and any significant objects or symbols."
        )
        await state.set_state(UserStates.waiting_for_dream)


@router.message(UserStates.waiting_for_dream)
async def process_dream_state(message: Message, state: FSMContext):
    """Process dream from state."""
    await process_dream(message, message.text)
    await state.clear()


async def process_dream(message: Message, dream_text: str):
    """Analyze the dream and send response."""
    user_id = message.from_user.id
    await analytics.track_chart_type("dream", user_id)

    # Check LLM rate limit before making AI call
    allowed, reason = await storage.check_llm_rate_limit(user_id)
    if not allowed:
        await message.answer(f"Rate limit reached: {reason}")
        return

    await message.answer("Analyzing your dream through a Jungian lens...")

    try:
        # Get current sensitivity data for cosmic correlation
        sensitivity_data = None
        try:
            report = await calculate_sensitivity()
            sensitivity_data = {
                "astrology": report.astrology,
                "geomagnetic": report.geomagnetic,
            }
        except Exception:
            logger.exception("Failed to load sensitivity context for dream analysis")

        analysis = await analyze_dream(dream_text, sensitivity_data=sensitivity_data)
        response = analysis.to_summary()

        # Split if too long for Telegram
        if len(response) > 4000:
            parts = [response[i : i + 4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(response)

    except Exception:
        logger.exception("Error analyzing dream for user_id=%s", user_id)
        await analytics.track_error("dream_analysis", "dream")
        await message.answer(
            "Sorry, I couldn't analyze that dream right now. Please try again later."
        )


@router.message(Command("bio"))
async def cmd_biorhythm(message: Message, state: FSMContext):
    """Show biorhythm chart."""
    user_id = message.from_user.id
    await analytics.track_command("bio", user_id)
    await analytics.track_chart_type("bio", user_id)

    user_info = await storage.get_user(user_id)
    if not user_info or "birth_date" not in user_info:
        await message.answer(
            "I need your birth date to calculate biorhythm.\n"
            "Use /setbirthday YYYY-MM-DD to set it."
        )
        return

    birth_date = user_info["birth_date"]
    bio = calculate_biorhythm(birth_date)

    # Create visual representation
    def bar(value: int) -> str:
        # Convert -100 to +100 to 0-20 bar
        pos = int((value + 100) / 10)
        return "░" * pos + "█" + "░" * (20 - pos)

    response = f"""**Biorhythm Report**
Birth Date: {birth_date.strftime("%Y-%m-%d")}

Physical ({bio.physical:+d}):  [{bar(bio.physical)}]
Emotional ({bio.emotional:+d}): [{bar(bio.emotional)}]
Intellectual ({bio.intellectual:+d}): [{bar(bio.intellectual)}]
Intuitive ({bio.intuitive:+d}): [{bar(bio.intuitive)}]

Overall: {bio.overall:+d}
{bio.interpretation}"""

    if bio.critical_days:
        response += f"\n\n⚠️ Critical cycles: {', '.join(bio.critical_days)}"

    await message.answer(response, parse_mode="Markdown")


@router.message(Command("astro"))
async def cmd_astro(message: Message):
    """Show current astrological influences."""
    user_id = message.from_user.id
    await analytics.track_command("astro", user_id)
    await analytics.track_chart_type("astro", user_id)

    await message.answer("Calculating astrological influences...")

    try:
        astro = await get_astro_data()

        response = f"""**Astrological Influences**

☀️ Sun in {astro.sun_sign}
🌙 Moon in {astro.moon_sign}

**Moon Phase:** {astro.moon_phase.phase_name}
Illumination: {astro.moon_phase.illumination}%
{astro.moon_phase.interpretation}

**Mercury Retrograde:** {"Yes - communications may be challenged" if astro.mercury_retrograde else "No"}

**Planetary Positions:**"""

        for transit in astro.major_transits[:5]:
            rx = " (Rx)" if transit.is_retrograde else ""
            response += f"\n• {transit.planet} in {transit.sign}{rx}"

        response += f"\n\nSensitivity contribution: {astro.sensitivity_score}/25"

        await message.answer(response, parse_mode="Markdown")

    except Exception:
        logger.exception("Error fetching astrology data for user_id=%s", user_id)
        await analytics.track_error("astrology_fetch", "astro")
        await message.answer(
            "Sorry, I couldn't fetch astrology data right now. Please try again later."
        )


@router.message(Command("remedies"))
async def cmd_remedies(message: Message):
    """Get personalized remedy recommendations."""
    user_id = message.from_user.id
    await analytics.track_command("remedies", user_id)
    await analytics.track_chart_type("remedies", user_id)

    # Check for specific remedy type
    text = message.text.lower()

    if "sleep" in text:
        plan = get_sleep_remedies()
    elif "focus" in text:
        plan = get_focus_remedies()
    elif "emotional" in text or "anxiety" in text:
        plan = get_emotional_remedies()
    else:
        # Get based on current sensitivity
        try:
            score, level = await get_quick_score()
            plan = get_remedies_for_sensitivity(level)
        except Exception:
            logger.exception("Error fetching quick score for remedies")
            plan = get_remedies_for_sensitivity("moderate")

    response = plan.to_summary()
    await message.answer(f"```\n{response}\n```", parse_mode="Markdown")


@router.message(Command("forecast"))
async def cmd_forecast(message: Message):
    """Show 12-month astrological forecast."""
    user_id = message.from_user.id
    await analytics.track_command("forecast", user_id)
    await analytics.track_chart_type("forecast", user_id)

    birth_date = None
    user_info = await storage.get_user(user_id)
    if user_info:
        birth_date = user_info.get("birth_date")

    await message.answer("Generating your 12-month forecast...")

    try:
        forecasts = await get_yearly_forecast(birth_date or datetime(1990, 1, 1))

        response = "**12-Month Forecast**\n\n"

        for f in forecasts[:6]:  # First 6 months
            retrogrades = ", ".join(f["retrogrades"]) if f["retrogrades"] else "None"
            themes = f["themes"][0] if f["themes"] else "Stable period"

            response += f"**{f['month']}**\n"
            response += f"Sensitivity: {f['sensitivity_level']}\n"
            response += f"Retrogrades: {retrogrades}\n"
            response += f"Theme: {themes}\n\n"

        response += "_Reply /forecast2 for months 7-12_"

        await message.answer(response, parse_mode="Markdown")

    except Exception:
        logger.exception("Error generating forecast for user_id=%s", user_id)
        await analytics.track_error("forecast_generation", "forecast")
        await message.answer(
            "Sorry, I couldn't generate your forecast right now. Please try again later."
        )


@router.message(Command("forecast2"))
async def cmd_forecast2(message: Message):
    """Show months 7-12 of forecast."""
    user_id = message.from_user.id
    await analytics.track_command("forecast2", user_id)

    birth_date = None
    user_info = await storage.get_user(user_id)
    if user_info:
        birth_date = user_info.get("birth_date")

    try:
        forecasts = await get_yearly_forecast(birth_date or datetime(1990, 1, 1))

        response = "**12-Month Forecast (continued)**\n\n"

        for f in forecasts[6:]:  # Months 7-12
            retrogrades = ", ".join(f["retrogrades"]) if f["retrogrades"] else "None"
            themes = f["themes"][0] if f["themes"] else "Stable period"

            response += f"**{f['month']}**\n"
            response += f"Sensitivity: {f['sensitivity_level']}\n"
            response += f"Retrogrades: {retrogrades}\n"
            response += f"Theme: {themes}\n\n"

        await message.answer(response, parse_mode="Markdown")

    except Exception:
        logger.exception("Error generating forecast (part 2) for user_id=%s", user_id)
        await analytics.track_error("forecast_generation", "forecast2")
        await message.answer(
            "Sorry, I couldn't generate the rest of your forecast right now. Please try again later."
        )


@router.message(Command("setbirthday"))
async def cmd_set_birthday(message: Message, state: FSMContext):
    """Set user's birth date."""
    await analytics.track_command("setbirthday", message.from_user.id)

    text = message.text.replace("/setbirthday", "").strip()

    if text:
        try:
            birth_date = datetime.strptime(text, "%Y-%m-%d")
            user_id = message.from_user.id

            await storage.update_user(user_id, {"birth_date": birth_date})
            await message.answer(
                f"Birth date set to {text}. Your biorhythm and forecasts are now personalized!"
            )
        except ValueError:
            await message.answer(
                "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
            )
    else:
        await message.answer("Please provide your birth date: /setbirthday YYYY-MM-DD")
        await state.set_state(UserStates.waiting_for_birthdate)


@router.message(UserStates.waiting_for_birthdate)
async def process_birthdate(message: Message, state: FSMContext):
    """Process birth date from state."""
    try:
        birth_date = datetime.strptime(message.text.strip(), "%Y-%m-%d")
        user_id = message.from_user.id

        await storage.update_user(user_id, {"birth_date": birth_date})

        # Check if user already has location
        user_info = await storage.get_user(user_id)
        if "latitude" in user_info:
            await message.answer("Birth date set! Your readings are now personalized.")
            await state.clear()
            return

        # Continue onboarding flow - ask for location
        progress = """**Setup Progress: 2/2**

Birth date saved!

Now enter your **location** as coordinates: LAT,LON

Example: `50.0755, 14.4378` (Prague)

Tip: Find your coordinates on Google Maps"""

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Skip Location → Done",
                        callback_data="onboard_skip_location",
                    )
                ]
            ]
        )

        await message.answer(progress, reply_markup=keyboard, parse_mode="Markdown")
        await state.set_state(UserStates.waiting_for_location)

    except ValueError:
        await message.answer("Invalid format. Please use YYYY-MM-DD (e.g., 1990-05-15)")


@router.message(Command("setlocation"))
async def cmd_set_location(message: Message, state: FSMContext):
    """Set user's location for weather data."""
    user_id = message.from_user.id
    await analytics.track_command("setlocation", user_id)

    text = message.text.replace("/setlocation", "").strip()

    if text:
        # Try to parse as lat,lon
        try:
            parts = text.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            await storage.update_user(user_id, {"latitude": lat, "longitude": lon})

            await message.answer(
                f"Location set to {lat}, {lon}. Weather data will be included in your sensitivity score!"
            )
        except (ValueError, IndexError):
            await message.answer(
                "Please provide coordinates: /setlocation LAT,LON\n"
                "Example: /setlocation 50.0755, 14.4378"
            )
    else:
        await message.answer(
            "Please provide your coordinates: /setlocation LAT,LON\n"
            "Example: /setlocation 50.0755, 14.4378\n\n"
            "Tip: You can find your coordinates on Google Maps"
        )


@router.message(UserStates.waiting_for_location)
async def process_location_state(message: Message, state: FSMContext):
    """Process location from onboarding flow."""
    user_id = message.from_user.id
    try:
        parts = message.text.split(",")
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())

        await storage.update_user(user_id, {"latitude": lat, "longitude": lon})

        # Onboarding complete!
        complete_msg = """**Setup Complete!**

Your profile is ready. You now have access to:
- Personalized biorhythm charts
- Weather-based sensitivity data
- Full astrological readings

Try /sense now to see your personalized sensitivity score!"""

        await message.answer(complete_msg, parse_mode="Markdown")
        await state.clear()

    except (ValueError, IndexError):
        await message.answer(
            "Invalid format. Please use LAT,LON\nExample: 50.0755, 14.4378"
        )


@router.callback_query(F.data == "onboard_skip_location")
async def onboard_skip_location(callback: CallbackQuery, state: FSMContext):
    """Skip location setup and complete onboarding."""
    await callback.answer()
    await state.clear()

    skip_msg = """**Setup Complete!**

Birth date saved. You can add location later with:
/setlocation LAT,LON

Try /sense now to see your sensitivity score!"""

    await callback.message.answer(skip_msg, parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help information."""
    await analytics.track_command("help", message.from_user.id)
    _update_last_activity()
    help_text = """**Sense by Kraliki Commands**

**Daily Check:**
/sense - Current sensitivity score (0-100)
/astro - Astrological influences
/bio - Your biorhythm cycles

**Dream Work:**
/dream - Analyze your dream
/dream [text] - Analyze dream directly

**Support:**
/remedies - Holistic recommendations
/remedies sleep - Sleep support
/remedies focus - Mental clarity
/remedies emotional - Emotional balance
/audit - Book 1-on-1 Sensitivity Audit

**Long-term:**
/forecast - 12-month outlook

**Settings:**
/setbirthday YYYY-MM-DD - For personalized readings
/setlocation LAT,LON - For weather data

**Premium:**
/subscribe - View subscription options
/status - Check your subscription

**System:**
/health - Bot status and uptime
/stats - Usage analytics (admin only)

---
Sense by Kraliki combines NOAA space weather, USGS seismic data, Schumann resonance, Open-Meteo weather, Swiss Ephemeris astrology, and classic biorhythm theory into one unified sensitivity score."""

    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("health", "ping"))
async def cmd_health(message: Message):
    """Return bot health status, uptime, and last activity."""
    await analytics.track_command("health", message.from_user.id)
    _update_last_activity()

    uptime = _format_uptime(_bot_start_time)
    last_activity_str = _last_activity.strftime("%Y-%m-%d %H:%M:%S UTC")
    started_at = _bot_start_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    # Active users count from Redis would require a scan or separate set, omitting for now for performance

    health_text = (
        f"**Bot Health Status**\n\n"
        f"**Status:** OK\n"
        f"**Uptime:** {uptime}\n"
        f"**Started:** {started_at}\n"
        f"**Last Activity:** {last_activity_str}\n"
    )

    await message.answer(health_text, parse_mode="Markdown")


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Show subscription status."""
    user_id = message.from_user.id
    await analytics.track_command("status", user_id)

    # Check subscription
    user_info = await storage.get_user(user_id)
    is_premium = await storage.is_premium(user_id)
    premium_until = user_info.get("premium_until")
    plan = user_info.get("plan", "").title()

    if is_premium and premium_until:
        days_left = (premium_until - datetime.now()).days
        status = f"""**Subscription Status: {plan} Plan**

Expires: {premium_until.strftime("%Y-%m-%d")} ({days_left} days left)

You have access to:
✓ Unlimited dream analyses
✓ Full sensitivity breakdowns
✓ {"12-month" if plan.lower() == "empath" else "6-month"} forecasts
✓ {"Personalized" if plan.lower() == "empath" else "Basic"} remedy plans
{"✓ Priority support" if plan.lower() == "empath" else ""}

Thank you for your support!"""
    else:
        status = f"""**Subscription Status: Free**

Free tier includes:
• {settings.free_dreams_per_month} dream analyses per month
• Basic sensitivity score
• 3-month forecast preview

**Upgrade to Premium:**
Use /subscribe to see available plans."""

    await message.answer(status, parse_mode="Markdown")


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Show subscription options and handle payment."""
    user_id = message.from_user.id
    await analytics.track_command("subscribe", user_id)

    # Check for plan argument
    text = message.text.replace("/subscribe", "").strip().lower()

    # Check if already premium
    is_premium = await storage.is_premium(user_id)
    if is_premium:
        user_info = await storage.get_user(user_id)
        premium_until = user_info.get("premium_until")
        if premium_until and premium_until > datetime.now(timezone.utc):
            await message.answer(
                f"**You're already on the Premium plan!**\n\n"
                f"Expires: {premium_until.strftime('%Y-%m-%d')}\n"
                f"Use /status to see your benefits.",
                parse_mode="Markdown",
            )
            return

    if text in ("sensitive", "1"):
        # Send invoice for Sensitive plan
        await message.answer_invoice(
            title="Sense by Kraliki Sensitive Plan",
            description="1 month of unlimited dream analyses, full sensitivity breakdowns, and 6-month forecasts",
            payload=f"sensitive:{user_id}",
            provider_token=settings.telegram_stars_provider_token,
            currency="XTR",  # Telegram Stars
            prices=[
                LabeledPrice(
                    label="Sensitive Plan (1 month)",
                    amount=settings.sensitive_price_stars,
                )
            ],
        )
    elif text in ("empath", "2"):
        # Send invoice for Empath plan
        await message.answer_invoice(
            title="Sense by Kraliki Empath Plan",
            description="1 month of all premium features: unlimited analyses, 12-month forecasts, personalized remedies",
            payload=f"empath:{user_id}",
            provider_token=settings.telegram_stars_provider_token,
            currency="XTR",  # Telegram Stars
            prices=[
                LabeledPrice(
                    label="Empath Plan (1 month)", amount=settings.empath_price_stars
                )
            ],
        )
    else:
        # Show plan options
        subscribe_text = f"""**Sense by Kraliki Premium Plans**

**1. Sensitive Plan - {settings.sensitive_price_stars} Stars (~$3/mo)**
• Unlimited dream analyses
• Full sensitivity breakdowns
• 6-month forecasts
• Basic remedies

**2. Empath Plan - {settings.empath_price_stars} Stars (~$7/mo)**
• Everything in Sensitive
• Full 12-month forecasts
• Advanced pattern tracking
• Personalized remedy plans
• Priority support

**To subscribe:**
`/subscribe sensitive` or `/subscribe 1`
`/subscribe empath` or `/subscribe 2`

Payment is via Telegram Stars - instant and secure!"""

        await message.answer(subscribe_text, parse_mode="Markdown")


@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    """Handle pre-checkout validation."""
    payload = query.invoice_payload
    parsed = _parse_payment_payload(payload)
    if not parsed:
        await query.answer(ok=False, error_message="Invalid payment payload.")
        return

    plan, payload_user_id = parsed
    if payload_user_id != query.from_user.id:
        logger.warning(
            "Pre-checkout user mismatch payload_user_id=%s query_user_id=%s",
            payload_user_id,
            query.from_user.id,
        )
        await query.answer(ok=False, error_message="Payment user mismatch.")
        return

    expected_amount = _expected_stars_amount(plan)
    if query.currency != "XTR" or query.total_amount != expected_amount:
        logger.warning(
            "Pre-checkout amount mismatch plan=%s currency=%s amount=%s expected=%s",
            plan,
            query.currency,
            query.total_amount,
            expected_amount,
        )
        await query.answer(ok=False, error_message="Invalid payment amount.")
        return

    await query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_payment(message: Message):
    """Handle successful payment."""
    if not message.successful_payment:
        return

    payload = message.successful_payment.invoice_payload
    parsed = _parse_payment_payload(payload)
    if not parsed:
        logger.error("Failed to parse payment payload: %s", payload)
        return

    plan, payload_user_id = parsed

    # SECURITY: Validate user ID matches (defense-in-depth)
    if payload_user_id != message.from_user.id:
        logger.error(
            "Payment user mismatch! payload_user_id=%s from_user_id=%s payload=%s",
            payload_user_id,
            message.from_user.id,
            payload,
        )
        await message.answer(
            "Payment verification failed. Please contact support.",
        )
        return

    # SECURITY: Validate payment amount matches expected plan price
    payment = message.successful_payment
    expected_amount = _expected_stars_amount(plan)
    if payment.currency != "XTR" or payment.total_amount != expected_amount:
        logger.error(
            "Payment amount mismatch! plan=%s currency=%s amount=%s expected=%s",
            plan,
            payment.currency,
            payment.total_amount,
            expected_amount,
        )
        await message.answer(
            "Payment amount verification failed. Please contact support.",
        )
        return

    # Update subscription in persistent storage (use verified from_user.id)
    await storage.set_premium(message.from_user.id, plan, months=1)

    # Track subscription analytics
    await analytics.track_subscription(message.from_user.id, plan)

    await message.answer(
        f"**Thank you for your support!**\n\n"
        f"Your **{plan.title()}** plan is now active for 1 month.\n"
        f"Use /sense, /dream, or /forecast to explore your new tools!",
        parse_mode="Markdown",
    )


@router.message(Command("audit"))
async def cmd_audit(message: Message):
    """Show audit options."""
    user_id = message.from_user.id
    await analytics.track_command("audit", user_id)

    audit_text = f"""**The Reality Check: Professional Sensitivity Audit**

Unlock a deeper understanding of your sensitivity with 'The Reality Check'—our premier B2B consulting service for professionals and teams.

**What's included in this 1-hour session:**
• In-depth analysis of your birth chart and biorhythms
• Review of your dream patterns and subconscious signals
• Environmental assessment (location, workspace, EMF)
• Personalized coping strategies and performance optimization plan
• Direct Q&A with a Sense by Kraliki expert

**Price:** €{settings.audit_price_eur}
**Duration:** 60 minutes via Zoom

[Book Your Reality Check Now]({settings.audit_payment_link})

_After payment, you will receive a calendar link to schedule your session._"""

    await message.answer(audit_text, parse_mode="Markdown")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show usage analytics (admin only)."""
    user_id = message.from_user.id
    await analytics.track_command("stats", user_id)

    # Check if user is admin
    if user_id not in settings.admin_user_ids:
        await message.answer("This command is only available to administrators.")
        return

    try:
        stats = await analytics.get_stats()

        if "error" in stats:
            await message.answer(f"Error retrieving stats: {stats['error']}")
            return

        # Format users section
        users = stats["users"]
        users_text = (
            f"**Active Users**\n"
            f"• Daily: {users['daily_active']}\n"
            f"• Weekly: {users['weekly_active']}\n"
            f"• Monthly: {users['monthly_active']}\n"
            f"• Total: {users['total']}"
        )

        # Format charts section
        charts = stats["charts"]
        charts_text = "**Charts Generated (Today / Total)**\n"
        for chart_type, counts in charts.items():
            charts_text += f"• {chart_type}: {counts['today']} / {counts['total']}\n"

        # Format top commands
        commands = stats["commands"]
        sorted_cmds = sorted(
            commands.items(), key=lambda x: x[1]["total"], reverse=True
        )[:10]
        cmds_text = "**Top Commands (Today / Total)**\n"
        for cmd, counts in sorted_cmds:
            cmds_text += f"• /{cmd}: {counts['today']} / {counts['total']}\n"

        # Errors
        errors = stats["errors"]
        errors_text = f"**Errors**\n• Total: {errors['total']}"

        # Combine response
        response = (
            f"**Sense by Kraliki Analytics**\n"
            f"_Generated: {stats['timestamp'][:19]}_\n\n"
            f"{users_text}\n\n"
            f"{charts_text}\n"
            f"{cmds_text}\n"
            f"{errors_text}"
        )

        await message.answer(response, parse_mode="Markdown")

    except Exception:
        logger.exception("Error fetching stats for admin user_id=%s", user_id)
        await analytics.track_error("stats_fetch", "stats")
        await message.answer("Sorry, couldn't retrieve analytics right now.")


# Catch-all for text messages (could be dreams)
@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    """Handle plain text - might be a dream description."""
    current_state = await state.get_state()

    if current_state is None:
        # Check if it looks like a dream
        text_lower = message.text.lower()
        dream_keywords = [
            "dreamed",
            "dream",
            "dreamt",
            "nightmare",
            "woke up",
            "sleeping",
        ]

        if (
            any(keyword in text_lower for keyword in dream_keywords)
            and len(message.text) > 50
        ):
            await message.answer(
                "That sounds like a dream! Would you like me to analyze it?\n"
                "Reply /dream to start the analysis, or just send /dream followed by your dream description."
            )
        else:
            await message.answer(
                "I didn't understand that command. Use /help to see available commands."
            )
