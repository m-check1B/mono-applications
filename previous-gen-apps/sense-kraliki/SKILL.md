---
name: sense-kraliki
description: Sense by Kraliki (formerly SenseIt) is a Telegram sensitivity tracking bot for HSPs. Use when working on cosmic/environmental data integration (NOAA, USGS, Schumann), biorhythm calculations, Jungian dream analysis, astrological features (Swiss Ephemeris), or Telegram bot handlers (aiogram). Combines 9 data sources into unified sensitivity scores.
---

# Sense by Kraliki - Sensitivity Tracking Bot

Formerly SenseIt.

Telegram bot that helps highly sensitive people (HSPs) understand how cosmic, earth, and environmental factors affect their wellbeing. Combines 9 data sources into a unified 0-100 sensitivity score.

## When to Use This Skill

- Building or modifying Telegram bot commands (aiogram 3.x)
- Working with cosmic data sources (NOAA space weather, USGS seismic)
- Implementing sensitivity scoring algorithms
- Adding Jungian dream analysis features (Gemini AI)
- Working with biorhythm calculations
- Implementing astrological features (Swiss Ephemeris)
- Adding Telegram Stars payment subscriptions
- Integrating weather data (Open-Meteo)
- Working with Schumann resonance data

## Architecture Overview

```
9 Data Sources → Sensitivity Engine → Unified Score (0-100)
     ↓
User Commands → Telegram Bot → Formatted Reports
     ↓
Premium Features → Telegram Stars Payments
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Bot Framework | aiogram 3.x |
| AI | Gemini 2.0 Flash (dream analysis) |
| Astrology | pyswisseph (Swiss Ephemeris) |
| Storage | Redis/Postgres (optional) |
| Payments | Telegram Stars (XTR) |
| Deployment | Docker + PM2 |

## Data Sources (9 Total)

| Source | Data | Contribution |
|--------|------|--------------|
| NOAA Space Weather | Kp index, geomagnetic activity | 0-30 points |
| NOAA Solar | Solar flares (X/M/C class) | 0-20 points |
| USGS Earthquake | Seismic activity (M4+) | 0-10 points |
| Schumann Resonance | Earth's electromagnetic pulse | 0-20 points |
| Open-Meteo | Pressure, humidity, temperature | 0-15 points |
| Swiss Ephemeris | Planetary positions, retrogrades | 0-25 points |
| Moon Phase | Lunar cycle influence | (included in astro) |
| Biorhythm | Physical/emotional/intellectual cycles | 0-20 points |
| Mercury Retrograde | Communication influence | (included in astro) |

**Max Score:** 140 raw points → Normalized to 0-100

## Key Components

### Bot Handlers (`app/bot/handlers.py`)

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Welcome and onboarding | All |
| `/sense` | Current sensitivity score | All |
| `/dream [text]` | Jungian dream analysis | All (limited free) |
| `/bio` | Biorhythm chart | Requires birthdate |
| `/astro` | Astrological influences | All |
| `/remedies` | Holistic recommendations | All |
| `/forecast` | 12-month outlook | Premium |
| `/setbirthday` | Set birth date | All |
| `/setlocation` | Set coordinates for weather | All |
| `/subscribe` | Purchase premium plan | All |
| `/status` | Subscription status | All |
| `/health` | Bot uptime | All |
| `/stats` | Usage analytics | Admin only |

### Services (`app/services/`)

| File | Purpose |
|------|---------|
| `sensitivity.py` | Unified sensitivity scoring engine |
| `dreams.py` | Jungian dream analysis with Gemini |
| `biorhythm.py` | Physical/emotional/intellectual cycles |
| `remedies.py` | Holistic recommendations based on level |

### Data Fetchers (`app/data/`)

| File | Purpose |
|------|---------|
| `noaa.py` | Space weather (Kp index, solar flares) |
| `usgs.py` | Earthquake data (USGS API) |
| `weather.py` | Open-Meteo weather (pressure, humidity) |
| `schumann.py` | Schumann resonance from geocenter.info |
| `astro.py` | Swiss Ephemeris calculations |

## Sensitivity Levels

| Score | Level | Recommendations |
|-------|-------|-----------------|
| 0-19 | Low | Conditions favorable, good for productivity |
| 20-39 | Moderate | Normal awareness advised |
| 40-59 | Elevated | Reduce stimulants, extra rest |
| 60-79 | High | Avoid major decisions, gentle exercise |
| 80-100 | Extreme | Self-care priority, grounding activities |

## Configuration (.env)

```bash
# Required
TELEGRAM_BOT_TOKEN=       # From @BotFather
GEMINI_API_KEY=           # From aistudio.google.com

# Optional
DATABASE_URL=postgresql+asyncpg://localhost/sense_kraliki
REDIS_URL=redis://localhost:6379/0
ADMIN_USER_IDS=123456,789012  # Comma-separated

# Subscription pricing (Telegram Stars)
SENSITIVE_PRICE_STARS=150   # ~$3/mo
EMPATH_PRICE_STARS=350      # ~$7/mo
FREE_DREAMS_PER_MONTH=3
```

## Development

```bash
# Navigate to project
cd /home/adminmatej/github/applications/sense-kraliki

# Setup environment
uv sync
source .venv/bin/activate

# Run bot (polling mode)
python -m app.main

# Run with Docker
docker compose up -d

# View logs
docker compose logs -f sense-kraliki-bot
```

## Monetization Model

- **Free tier:** 3 dream analyses/month, basic sensitivity score
- **Sensitive Plan:** 150 Stars (~$3/mo) - Unlimited dreams, full breakdowns
- **Empath Plan:** 350 Stars (~$7/mo) - Everything + 12-month forecasts, personalized remedies

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| aiogram 3.x | Modern async, type hints, Telegram API v7 |
| Swiss Ephemeris | Industry-standard astronomical calculations |
| Gemini Flash | Cost-effective AI for dream analysis |
| 9 data sources | Comprehensive sensitivity picture |
| 0-100 scoring | Intuitive, easy to understand |

## Common Tasks

### Add a New Data Source

1. Create fetcher in `app/data/new_source.py`:
   ```python
   @dataclass
   class NewSourceData:
       value: float
       sensitivity_score: int  # 0-N contribution

   async def get_new_source_data() -> NewSourceData:
       # Fetch and parse data
       pass
   ```

2. Add to `calculate_sensitivity()` in `app/services/sensitivity.py`:
   ```python
   tasks.append(get_new_source_data())
   # Handle result and add to breakdown
   ```

3. Update `SensitivityBreakdown` dataclass with new field

### Add a New Command

1. Add handler in `app/bot/handlers.py`:
   ```python
   @router.message(Command("newcmd"))
   async def cmd_newcmd(message: Message):
       await analytics.track_command("newcmd", message.from_user.id)
       await message.answer("Response")
   ```

2. Update `/help` command text

### Modify Dream Analysis Prompt

Edit `DREAM_ANALYSIS_PROMPT` in `app/services/dreams.py`. Keep:
- Jungian framework (archetypes, shadow, symbols)
- JSON output format for parsing
- Cosmic context integration

## Known Issues (from AUDIT_REPORT.md)

- **Critical:** Credentials in `.env` - use secrets manager in production
- **High:** No `.dockerignore` - secrets could leak to build context
- **Medium:** In-memory user state - needs Redis/Postgres persistence
- **Medium:** No rate limiting on LLM calls - implement quotas

## Integration Points

- **PM2:** Process management via `ecosystem.config.js`
- **Port:** 8000 (internal only)
- **Blocked by:** HW-001 (Telegram bot token creation)

---

*See AUDIT_REPORT.md for security review and recommended fixes*
