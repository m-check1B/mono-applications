"""Kraliki Notify Bot - FastAPI Application with Telegram Webhook.

Provides notifications and monitoring for the Kraliki swarm via Telegram.
Uses webhook mode for production (required when api.telegram.org outbound blocked).

Now powered by Claude AI for intelligent command parsing and execution.
"""

import logging
from contextlib import asynccontextmanager

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, Update, ContentType
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Request

from app.bot import bot, dp
from app.config import settings
from app.services import (
    get_health_status,
    get_morning_digest,
    get_agent_list,
    post_to_blackboard,
    create_task,
    get_recent_responses,
)
from app.claude_brain import get_brain

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Scheduler for periodic jobs
scheduler = AsyncIOScheduler()


# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    is_admin = settings.admin_chat_id and str(message.chat.id) == str(settings.admin_chat_id)

    msg = f"🦜 *Kraliki Swarm Bot*\n\n"
    msg += f"Claude-powered AI swarm admin.\n\n"
    msg += f"Your Chat ID: `{message.chat.id}`\n\n"
    msg += f"Use /help for all commands."

    if is_admin:
        msg += f"\n\n✅ You are admin - full access enabled."
    else:
        msg += f"\n\n_Admin access required for control commands._"

    await message.answer(msg, parse_mode="Markdown")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Show all available commands."""
    is_admin = settings.admin_chat_id and str(message.chat.id) == str(settings.admin_chat_id)

    msg = "🦜 *Kraliki Swarm Bot - Help*\n\n"
    msg += "*Basic Commands:*\n"
    msg += "/start - Bot introduction\n"
    msg += "/help - This help message\n"
    msg += "/status - System health check\n"
    msg += "/digest - 24h activity report\n"
    msg += "/report N - Last N hours report\n"
    msg += "/agents - List running agents\n"

    if is_admin:
        msg += "\n*Admin Commands:*\n"
        msg += "/task [PRIORITY] Title | Desc - Create swarm task\n"
        msg += "/say message - Post to blackboard\n"
        msg += "/responses - Agent responses to you\n"

        msg += "\n*Claude AI Mode:*\n"
        msg += "Just type natural language commands:\n"
        msg += "• _\"spawn a builder\"_\n"
        msg += "• _\"what are the agents doing?\"_\n"
        msg += "• _\"show leaderboard\"_\n"
        msg += "• _\"restart the dashboard\"_\n"
        msg += "• _\"disable gemini due to quota\"_\n"

        msg += "\n*Photo/Document Dump:*\n"
        msg += "Send any image or document - it will be\n"
        msg += "described by Claude and posted to the swarm.\n"

        msg += "\n*Direct Message:*\n"
        msg += "Any text message is processed by Claude AI.\n"
        msg += "It decides: answer, execute command, or post to swarm."
    else:
        msg += "\n_Admin commands available for authorized users._"

    await message.answer(msg, parse_mode="Markdown")


@dp.message(Command("status"))
async def cmd_status(message: Message):
    status_msg = await get_health_status()
    await message.answer(status_msg, parse_mode="Markdown")


@dp.message(Command("digest"))
async def cmd_digest(message: Message):
    digest = await get_morning_digest(hours=24)
    await message.answer(digest, parse_mode="Markdown")


@dp.message(Command("report"))
async def cmd_report(message: Message):
    args = message.text.split()
    hours = 24
    if len(args) > 1 and args[1].isdigit():
        hours = int(args[1])

    digest = await get_morning_digest(hours=hours)
    await message.answer(digest, parse_mode="Markdown")


@dp.message(Command("agents"))
async def cmd_agents(message: Message):
    agents_msg = await get_agent_list()
    await message.answer(agents_msg, parse_mode="Markdown")


@dp.message(Command("task"))
async def cmd_task(message: Message):
    """Create a task for the swarm: /task [priority] Title | Description"""
    if settings.admin_chat_id and str(message.chat.id) != str(settings.admin_chat_id):
        await message.answer("Unauthorized. Only admin can create tasks.")
        return

    text = message.text.replace("/task", "").strip()
    if not text:
        await message.answer(
            "*Create Task*\n\n"
            "Usage: `/task [PRIORITY] Title | Description`\n\n"
            "Examples:\n"
            "* `/task Fix the login bug`\n"
            "* `/task HIGH Deploy voice-kraliki to beta`\n"
            "* `/task URGENT Server is down | Check PM2 and restart`",
            parse_mode="Markdown"
        )
        return

    # Parse priority if present
    priority = "HIGH"
    for p in ["URGENT", "HIGH", "MEDIUM", "LOW"]:
        if text.upper().startswith(p):
            priority = p
            text = text[len(p):].strip()
            break

    # Split title and description
    if "|" in text:
        title, description = text.split("|", 1)
        title = title.strip()
        description = description.strip()
    else:
        title = text
        description = ""

    result = await create_task(title, description, priority)
    await message.answer(result, parse_mode="Markdown")


@dp.message(Command("responses"))
async def cmd_responses(message: Message):
    """Get recent agent responses to human commands."""
    responses = await get_recent_responses()
    await message.answer(responses, parse_mode="Markdown")


@dp.message(Command("say"))
async def cmd_say(message: Message):
    """Post a message directly to blackboard: /say Your message"""
    if settings.admin_chat_id and str(message.chat.id) != str(settings.admin_chat_id):
        await message.answer("Unauthorized.")
        return

    text = message.text.replace("/say", "").strip()
    if not text:
        await message.answer("Usage: `/say Your message to the swarm`", parse_mode="Markdown")
        return

    result = await post_to_blackboard(text)
    await message.answer(result, parse_mode="Markdown")


# Catch-all handler for non-command messages from admin - Claude AI powered
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message):
    """Any non-command message from admin gets processed by Claude AI."""
    if settings.admin_chat_id and str(message.chat.id) != str(settings.admin_chat_id):
        await message.answer(
            "I'm the Kraliki Swarm Bot.\n"
            "Use /start to see available commands."
        )
        return

    # Admin message - process with Claude brain
    brain = get_brain()
    await message.answer("🧠 Processing...")

    try:
        response = await brain.process_message(message.text)
        # Telegram has 4096 char limit, truncate if needed
        if len(response) > 4000:
            response = response[:4000] + "\n\n_(truncated)_"
        await message.answer(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Claude brain error: {e}")
        # Fallback to direct post
        result = await post_to_blackboard(message.text)
        await message.answer(f"⚠️ AI error, posted directly:\n{result}", parse_mode="Markdown")


# Photo handler - dump images to swarm
@dp.message(F.photo)
async def handle_photo(message: Message):
    """Handle photo messages - describe with Claude Vision and post to swarm."""
    if settings.admin_chat_id and str(message.chat.id) != str(settings.admin_chat_id):
        await message.answer("Unauthorized. Only admin can send photos to swarm.")
        return

    await message.answer("📷 Processing image...")

    try:
        # Get the largest photo
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)

        # Read bytes from BytesIO
        image_data = file_bytes.read()

        brain = get_brain()
        caption = message.caption or ""

        # Describe the image
        description = await brain.describe_image(image_data, caption)

        # Post to swarm blackboard
        post_message = f"📷 IMAGE FROM CEO:\n{description}"
        if caption:
            post_message += f"\n\nCaption: {caption}"

        result = await brain.execute_tool("kraliki_blackboard_post", {
            "author": "CEO-HUMAN",
            "message": post_message,
            "topic": "general"
        })

        await message.answer(
            f"✅ *Image posted to swarm*\n\n"
            f"*Description:*\n{description[:500]}{'...' if len(description) > 500 else ''}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Photo handling error: {e}")
        await message.answer(f"❌ Failed to process image: {str(e)[:100]}")


# Document handler - dump documents to swarm
@dp.message(F.document)
async def handle_document(message: Message):
    """Handle document messages - post info to swarm."""
    if settings.admin_chat_id and str(message.chat.id) != str(settings.admin_chat_id):
        await message.answer("Unauthorized. Only admin can send documents to swarm.")
        return

    doc = message.document
    caption = message.caption or ""

    # Post document info to swarm
    brain = get_brain()
    post_message = (
        f"📎 DOCUMENT FROM CEO:\n"
        f"File: {doc.file_name}\n"
        f"Size: {doc.file_size} bytes\n"
        f"Type: {doc.mime_type or 'unknown'}"
    )
    if caption:
        post_message += f"\n\nCaption: {caption}"

    result = await brain.execute_tool("kraliki_blackboard_post", {
        "author": "CEO-HUMAN",
        "message": post_message,
        "topic": "general"
    })

    await message.answer(
        f"✅ *Document info posted to swarm*\n\n"
        f"File: `{doc.file_name}`",
        parse_mode="Markdown"
    )


# --- Jobs ---

async def job_morning_digest():
    if not settings.admin_chat_id:
        logger.warning("No ADMIN_CHAT_ID set, skipping digest.")
        return

    digest = await get_morning_digest()
    await bot.send_message(settings.admin_chat_id, digest, parse_mode="Markdown")


# --- FastAPI Application ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    logger.info("Starting Kraliki Notify Bot...")

    # Set up webhook if URL configured
    # Note: This may fail if outbound to api.telegram.org is blocked
    # In that case, set webhook manually via curl or use existing webhook
    if settings.webhook_url:
        if not settings.webhook_secret:
            logger.error(
                "SECURITY: WEBHOOK_SECRET is required when using webhooks. "
                "Generate a random string and set it in .env"
            )
            raise RuntimeError("WEBHOOK_SECRET is required for webhook mode")

        webhook_url = f"{settings.webhook_url}/webhook"
        try:
            import asyncio
            # Set a timeout for webhook setup (5 seconds)
            await asyncio.wait_for(
                bot.set_webhook(
                    url=webhook_url,
                    secret_token=settings.webhook_secret
                ),
                timeout=5.0
            )
            logger.info(f"Webhook configured at {webhook_url}")
        except asyncio.TimeoutError:
            logger.warning(f"Webhook setup timed out - may need manual setup at {webhook_url}")
        except Exception as e:
            logger.warning(f"Failed to set webhook (may already be set): {e}")
            # Continue anyway - webhook might already be set
    else:
        logger.warning("No WEBHOOK_URL configured - bot won't receive updates")

    # Start scheduler
    scheduler.add_job(job_morning_digest, 'cron', hour=8, minute=0)
    scheduler.start()
    logger.info("Scheduler started (morning digest at 08:00 UTC)")

    yield

    # Shutdown
    logger.info("Shutting down...")
    scheduler.shutdown()
    try:
        await bot.delete_webhook()
    except Exception:
        pass
    await bot.session.close()


app = FastAPI(
    title="Kraliki Notify Bot",
    description="Telegram bot for swarm notifications and monitoring",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "app": "kraliki-notify", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "webhook_configured": bool(settings.webhook_url),
        "admin_configured": bool(settings.admin_chat_id),
    }


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates via webhook.

    Security: Validates X-Telegram-Bot-Api-Secret-Token header.
    """
    # Require secret token for webhook authentication
    if not settings.webhook_secret:
        logger.error("Webhook called but WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_header != settings.webhook_secret:
        logger.warning("Invalid or missing webhook secret token")
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.exception(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


# --- Dev Mode: Polling fallback ---

if __name__ == "__main__":
    import asyncio

    async def run_polling():
        """Run bot in polling mode for development."""
        logger.info("Starting in polling mode (development)...")

        # Remove any existing webhook
        try:
            await bot.delete_webhook()
        except Exception:
            pass

        # Start scheduler
        scheduler.add_job(job_morning_digest, 'cron', hour=8, minute=0)
        scheduler.start()

        # Start polling
        await dp.start_polling(bot)

    asyncio.run(run_polling())
