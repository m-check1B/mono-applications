import asyncio
import os
from aiogram import Bot

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable is required. Set it or run with: BOT_TOKEN=xxx python get_chat_id.py")
    
    bot = Bot(token=token)
    print(f"Bot authorized: {(await bot.get_me()).username}")
    print("Please send a message to the bot (e.g. /start) within the next 30 seconds...")
    
    try:
        # Simple polling for one update
        updates = await bot.get_updates(limit=1, timeout=30)
        if updates:
            chat_id = updates[0].message.chat.id
            print(f"\nSUCCESS! Your Chat ID is: {chat_id}")
            print(f"Update .env with: ADMIN_CHAT_ID={chat_id}")
        else:
            print("\nNo updates received. Did you message the bot?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
