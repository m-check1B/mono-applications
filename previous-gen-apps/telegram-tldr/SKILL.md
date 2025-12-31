---
name: telegram-tldr
description: Telegram GroupChat TL;DR Bot (Sumarium). Use when working on Telegram bot commands, message summarization, Redis message buffering, aiogram handlers, Gemini AI integration, Telegram Stars payments/subscriptions, analytics, or webhook/polling deployment.
---

# Telegram TL;DR Bot (Sumarium)

Use this skill to build and operate the Telegram bot that summarizes busy group chats using AI, turning 500+ unread messages into a 30-second read.

**Branding:** Verduona (non-Kraliki Telegram bot).

## Architecture Overview

Review the end-to-end flow to trace messages through buffering, summarization, and delivery.

```
Telegram Group → Message Handler → Redis Buffer
                                       ↓
Admin: /summary → Buffer.get_messages() → Gemini AI
                                              ↓
                                     Markdown Summary → User
```

## Tech Stack

Refer to the core stack when planning integrations or upgrades.

| Layer | Technology |
|-------|------------|
| Bot Framework | aiogram 3.x |
| Web Server | FastAPI + uvicorn |
| AI | Gemini 2.0 Flash |
| Storage | Redis (sorted sets, message buffer) |
| Payments | Telegram Stars (XTR) |
| Deployment | Docker + Traefik |

## Key Components

Use these folders to locate the core runtime logic.

### Services (`app/services/`)

| File | Purpose |
|------|---------|
| `bot.py` | Telegram handlers, commands, payments |
| `buffer.py` | Redis message storage, usage tracking, subscriptions |
| `summarizer.py` | Gemini API integration, prompt engineering |
| `analytics.py` | Usage metrics, command tracking, daily stats |

### Core (`app/core/`)

| File | Purpose |
|------|---------|
| `config.py` | Pydantic settings from .env |

## Bot Commands

Update this list when adding or changing bot behavior.

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Onboarding message | All |
| `/help` | Command reference | All |
| `/summary [hours]` | Generate digest (default 24h, max 24h) | Group admins |
| `/status` | Show subscription/usage | All |
| `/subscribe` | Purchase Pro (250 Stars) | All |
| `/schedule HH:MM` | Set daily digest time (24h UTC) | Pro subscribers |
| `/unschedule` | Disable scheduled daily digest | All |
| `/health` | Bot uptime and Redis status | All |
| `/stats` | Usage analytics | Bot admins only |

## Redis Key Patterns

Keep these key patterns consistent when expanding storage or analytics.

```
tldr:chat:{chat_id}:messages      # Sorted set (score=timestamp)
tldr:chat:{chat_id}:usage         # Integer (monthly counter)
tldr:chat:{chat_id}:subscription  # String "active" (TTL=30 days)
tldr:chat:{chat_id}:schedule      # JSON {"hour": int, "minute": int, "enabled": bool}
tldr:analytics:*                  # All analytics keys
```

## Monetization Model

Align pricing and access controls to these tiers.

- **Free tier:** 3 summaries/month per chat
- **Pro tier:** €4.99/month or €47.99/year (Stripe) OR 250 Telegram Stars/month (~$5)
- **Content Pro tier:** €7.99/month (Stripe) - Advanced content features
- **Payment Methods:** Stripe (Web/Credit Card) and Telegram Stars (In-App)

## Configuration (.env)

Set required and optional variables before running or deploying.

```bash
# Required
TELEGRAM_BOT_TOKEN=       # From @BotFather
GEMINI_API_KEY=           # From aistudio.google.com

# Webhook (production)
TELEGRAM_WEBHOOK_URL=     # https://bot.verduona.com
TELEGRAM_WEBHOOK_SECRET=  # Random string

# Optional
REDIS_URL=redis://localhost:6379/0
ADMIN_USER_IDS=123456,789012  # Comma-separated
FREE_SUMMARIES=3
SUBSCRIPTION_PRICE_STARS=250
MAX_MESSAGES_PER_SUMMARY=500
MESSAGE_BUFFER_HOURS=24
```

## Development

Use these commands for local setup and production containers.

```bash
# Navigate to project
cd /home/adminmatej/github/applications/telegram-tldr

# Setup environment
uv sync
source .venv/bin/activate

# Run in polling mode (dev)
python -m app.main

# Run with Docker (production)
docker compose up -d

# View logs
docker compose logs -f bot
```

## Summary Prompt Structure

Follow this prompt structure when adjusting summarization output:
- **Topics Discussed:** Main conversation themes
- **Key Points:** Important actionable items
- **Links Shared:** URLs mentioned
- **Unanswered Questions:** Open issues
- **Activity:** Message and user counts

## Key Design Decisions

Use these rationale notes when revisiting architecture tradeoffs.

| Decision | Rationale |
|----------|-----------|
| aiogram 3.x | Modern async, type hints, Telegram API v7 |
| Redis sorted sets | Time-range queries, auto-expire, memory efficient |
| Gemini Flash | 50% cheaper than GPT-4o-mini, fast |
| Webhook mode | Required for production (Telegram requirement) |
| Admin-only summary | Prevents spam, usage control |

## Integration Points

Use these integration details when wiring external systems.

- **Traefik:** `bot.verduona.com` → port 8000
- **Redis:** Dedicated instance `tldr-redis`
- **Network:** `tldr-network` (internal), `websites_default` (Traefik)

## Common Tasks

Follow these patterns when extending the bot.

### Add a New Command

1. Add handler in `app/services/bot.py`:
   ```python
   @router.message(Command("mycommand"))
   async def cmd_mycommand(message: Message):
       await analytics.track_command("mycommand")
       await message.answer("Response")
   ```

2. Update `/help` text in `cmd_help()`

3. Add to analytics tracking in `app/services/analytics.py`:
   ```python
   commands = ["start", "help", "summary", ..., "mycommand"]
   ```

### Modify Summarization Prompt

Edit `SUMMARY_PROMPT` in `app/services/summarizer.py`. Keep:
- Clear output format (bullet points, sections)
- Temperature low (0.3) for consistency
- Token limit reasonable (1000)

### Add Rate Limiting

Implement in `app/services/buffer.py`:
- Add Redis key pattern for rate limits
- Check in `can_summarize()` method
- Consider cooldown per chat (e.g., 5 min)

---

*See docker-compose.yml for deployment configuration*
