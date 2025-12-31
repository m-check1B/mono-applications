import asyncio
import os
from aiogram import Bot

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable is required. Set it or run with: BOT_TOKEN=xxx python test_msg.py")
    chat_id = os.getenv("ADMIN_CHAT_ID")
    if not chat_id:
        raise ValueError("ADMIN_CHAT_ID environment variable is required. Set it or run with: ADMIN_CHAT_ID=xxx python test_msg.py")
    
    bot = Bot(token=token)
    try:
        await bot.send_message(chat_id, "✅ **Setup Complete:** Kraliki Notify Bot is online.", parse_mode="Markdown")
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
