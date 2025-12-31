# HW-001: Create SenseIt Telegram Bot

**Status:** DONE (2025-12-20) - Token already obtained
**Blocks:** W2-002 (SenseIt - finish last 5%)
**Created:** 2025-12-09
**Priority:** HIGH

---

## What You Need To Do

1. Open Telegram
2. Message `@BotFather`
3. Send `/newbot`
4. When asked for name, enter: `SenseIt`
5. When asked for username, enter: `senseit_bot` (or similar if taken)
6. Copy the API token BotFather gives you

---

## Expected Output

A token that looks like:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## When Done

1. Paste the token in the Result section below
2. Change Status above to: **DONE**
3. Save this file

Agent will automatically:
- Update `/github/applications/senseit/.env`
- Start the bot
- Verify it works
- Mark W2-002 as passed

---

## Agent Pre-work Complete (2025-12-20)

- PM2 ecosystem.config.js created
- Python syntax validated
- Config loading verified
- Gemini API key already configured
- Redis connection ready (localhost:6380/2)

**Once token is provided, run:**
```bash
cd /github/applications/senseit
# Update .env with token
pm2 start ecosystem.config.js
pm2 logs senseit-bot
```

---

## Result

```
[PASTE BOT TOKEN HERE]
```
