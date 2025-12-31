"""Sense by Kraliki - Sensitivity Tracking Bot main entry point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.core.config import settings
from app.bot.handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and run the bot."""
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    # Initialize bot with default properties
    bot = Bot(token=settings.telegram_bot_token)

    # Initialize storage (Redis)
    # We use Redis for both FSM and our custom BotStorage
    redis_instance = Redis.from_url(settings.redis_url, decode_responses=True)
    fsm_storage = RedisStorage(redis=redis_instance)

    # Initialize dispatcher with persistent storage
    dp = Dispatcher(storage=fsm_storage)

    # Register routers
    dp.include_router(router)

    # Initialize database
    from app.core.database import init_db
    await init_db()

    # Initialize our custom storage service
    from app.services.storage import storage
    await storage.connect()

    # Log startup
    logger.info("Starting Sense by Kraliki bot with persistent Redis storage...")

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await storage.close()
        await redis_instance.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
