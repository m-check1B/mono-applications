# Telegram TL;DR Bot - Project Memory

> **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

Telegram GroupChat TL;DR Bot (Sumarium) - AI-powered chat summarization.

**Branding:** Verduona (non-Kraliki Telegram bot).

**Skill Reference:** See `SKILL.md` for capabilities, architecture, and integration details.

## Project Overview

Telegram bot that summarizes busy group chats. Turns 500+ unread messages into a 30-second read using Gemini AI.

**Tech Stack:**
- Bot: aiogram 3.x
- Server: FastAPI + uvicorn
- AI: Gemini 2.0 Flash
- Storage: Redis (message buffer, usage, subscriptions)
- Payments: Telegram Stars

## Key Directories

```
app/
├── core/           # Config (pydantic-settings)
├── services/
│   ├── bot.py      # Telegram handlers, commands
│   ├── buffer.py   # Redis message storage
│   ├── summarizer.py # Gemini AI integration
│   └── analytics.py  # Usage tracking
├── models/         # (unused currently)
├── schemas/        # (unused currently)
└── main.py         # FastAPI app, lifespan
```

## Development Commands

```bash
# Setup
cd /home/adminmatej/github/applications/telegram-tldr
uv sync
source .venv/bin/activate

# Run (polling mode - dev)
python -m app.main

# Run (Docker - production)
docker compose up -d

# Logs
docker compose logs -f bot

# Stop
docker compose down
```

## Bot Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Onboarding | All |
| `/help` | Command reference | All |
| `/summary [hours]` | Generate digest | Group admins |
| `/status` | Show usage | All |
| `/subscribe` | View payment options | All |
| `/subscribe_stars` | Buy Pro with Telegram Stars (250 Stars) | All |
| `/subscribe_stripe` | Buy Pro with Stripe card payment (€4.99/mo) | All |
| `/subscribe_stripe yearly` | Buy Pro yearly with Stripe (€47.99/yr, 20% off) | All |
| `/manage` | View/cancel subscription | All |
| `/schedule HH:MM` | Daily digest at time (UTC) | Pro only |
| `/periodic 6h/12h/daily/weekly` | Interval-based digests | Pro only |
| `/periodic auto 100` | Trigger after N messages | Pro only |
| `/unschedule` | Disable daily digest | All |
| `/health` | Bot status | All |
| `/stats` | Analytics | Bot admins |
| `/topics` | Manage topic subscriptions | Pro only |
| `/mydigest` | Personalized topic digest | Pro only |
| `/content_subscribe` | Buy Content Pro (400 Stars) | All |

## Configuration

Required in `.env`:
```bash
TELEGRAM_BOT_TOKEN=         # From @BotFather
GEMINI_API_KEY=             # From aistudio.google.com
TELEGRAM_WEBHOOK_URL=       # Production HTTPS URL
TELEGRAM_WEBHOOK_SECRET=    # Webhook security
```

Optional:
```bash
REDIS_URL=redis://localhost:6379/0
ADMIN_USER_IDS=123456,789012
FREE_SUMMARIES=3
SUBSCRIPTION_PRICE_STARS=250
```

## Deployment

- **Domain:** bot.verduona.com
- **Traefik:** Handles TLS, routes to container port 8000
- **Redis:** Dedicated `tldr-redis` container
- **Network:** `tldr-network` + `websites_default`

## Key Patterns

### Message Buffering
- Redis sorted sets (score = timestamp)
- Auto-expire after 24 hours
- Max 500 messages per chat

### Usage Limits
- Free tier: 3 summaries/month
- Pro tier: 250 Stars, unlimited summaries + scheduled digests
- Content Pro tier: 400 Stars, personalized topic subscriptions + mydigest
- Monthly reset on usage counter

### Content Subscriptions
- Users can subscribe to topics: tech, crypto, deals, news, jobs, events, learning, finance
- `/mydigest` generates AI-filtered digest based on subscribed topics only
- Topics stored per-user in Redis sets with 30-day TTL

### Admin-Only Summaries
- Checks if user is group admin before generating
- Prevents spam/abuse of AI API

### Analytics Dashboard
- Web-based dashboard at `/dashboard?token=<TELEGRAM_WEBHOOK_SECRET>`
- API endpoint at `/api/analytics?token=<TELEGRAM_WEBHOOK_SECRET>`
- Shows: all-time stats, daily stats, 7-day trends, command usage, recent errors
- Auto-refreshes every 60 seconds
- Production URL: `https://bot.verduona.com/dashboard?token=<secret>`

## Testing

```bash
# Run tests
cd /home/adminmatej/github/applications/telegram-tldr
pytest

# Test webhook locally (use ngrok or similar)
ngrok http 8000
# Update TELEGRAM_WEBHOOK_URL in .env
```

## Notes

- Webhook mode required for production (Telegram requirement)
- Polling mode available for local development
- Gemini Flash is ~50% cheaper than GPT-4o-mini
- No external payment provider needed (Telegram Stars native)

---

*Part of the GitHub workspace at /home/adminmatej/github*
*See parent @../../../CLAUDE.md for workspace conventions*
