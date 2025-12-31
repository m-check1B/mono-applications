# Sense by Kraliki - Project Memory

> **Official Name:** Sense by Kraliki (formerly SenseIt)
> **Domain:** sense.kraliki.com | sense.verduona.dev

> **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

Sense by Kraliki - Telegram sensitivity tracking bot for highly sensitive people (HSPs).

**Skill Reference:** See `SKILL.md` for capabilities, architecture, and integration details.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Sense is an external module integrated with Kraliki Swarm.
========================================

## Project Overview

Telegram bot that combines 9 cosmic/environmental data sources into a unified sensitivity score (0-100). Helps users understand how space weather, seismic activity, moon phases, and more affect their wellbeing.

**Tech Stack:**
- Bot: aiogram 3.x
- AI: Gemini 2.0 Flash (dream analysis)
- Astrology: pyswisseph (Swiss Ephemeris)
- Storage: Persistent (Redis FSM + Redis/Postgres Profile Storage)
- Payments: Telegram Stars

## Key Directories

```
app/
├── core/           # Config, database setup, analytics
├── models/         # SQLAlchemy models (User)
├── bot/
│   └── handlers.py # Telegram commands, payments
├── services/
│   ├── sensitivity.py  # Unified scoring engine
│   ├── dreams.py       # Jungian dream analysis
│   ├── biorhythm.py    # Cycle calculations
│   ├── remedies.py     # Holistic recommendations
│   └── storage.py      # Hybrid persistent storage (Redis/Postgres)
├── data/
│   ├── noaa.py     # Space weather API
│   ├── usgs.py     # Earthquake data
│   ├── weather.py  # Open-Meteo weather
│   ├── schumann.py # Schumann resonance
│   └── astro.py    # Swiss Ephemeris
└── main.py         # Bot entry point
```

## Development Commands

```bash
# Setup
cd /home/adminmatej/github/applications/sense-kraliki
uv sync
source .venv/bin/activate

# Run (polling mode - dev)
python -m app.main

# Run (Docker - production)
docker compose up -d

# Logs
docker compose logs -f sense-kraliki-bot

# Stop
docker compose down
```

## Bot Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Welcome message | All |
| `/sense` | Current sensitivity score | All |
| `/dream [text]` | Jungian dream analysis | All (3 free/mo) |
| `/bio` | Biorhythm chart | Requires birthdate |
| `/astro` | Astrological influences | All |
| `/remedies` | Holistic recommendations | All |
| `/forecast` | 12-month outlook | Premium |
| `/setbirthday` | Set birth date | All |
| `/setlocation` | Set coordinates | All |
| `/subscribe` | Purchase premium | All |
| `/status` | Subscription status | All |
| `/health` | Bot uptime | All |
| `/stats` | Analytics | Admin only |

## Configuration

Required in `.env`:
```bash
TELEGRAM_BOT_TOKEN=         # From @BotFather
GEMINI_API_KEY=             # From aistudio.google.com
```

Optional:
```bash
DATABASE_URL=postgresql+asyncpg://localhost/sense_kraliki
REDIS_URL=redis://localhost:6379/0
ADMIN_USER_IDS=123456,789012
FREE_DREAMS_PER_MONTH=3
SENSITIVE_PRICE_STARS=150
EMPATH_PRICE_STARS=350
```

## Data Sources (9 Total)

1. **NOAA Geomagnetic** - Kp index (0-9)
2. **NOAA Solar** - Flare activity (X/M/C class)
3. **USGS Seismic** - Earthquakes (M4+)
4. **Schumann Resonance** - Earth's EM pulse
5. **Open-Meteo Weather** - Pressure, humidity
6. **Swiss Ephemeris** - Planetary positions
7. **Moon Phase** - Lunar cycle
8. **Mercury Retrograde** - Communication periods
9. **Biorhythm** - Personal cycles (from birthdate)

## Sensitivity Levels

| Score | Level | Color |
|-------|-------|-------|
| 0-19 | Low | Green |
| 20-39 | Moderate | Yellow |
| 40-59 | Elevated | Orange |
| 60-79 | High | Red |
| 80-100 | Extreme | Warning |

## Key Patterns

### Concurrent Data Fetching
All 9 data sources are fetched concurrently using `asyncio.gather()` to minimize latency.

### Sensitivity Scoring
Each source contributes a weighted score to the total:
- Max raw: 140 points
- Normalized: 0-100

### Dream Analysis
Uses Gemini AI with Jungian framework (archetypes, shadow, symbols). Correlates with current cosmic conditions.

## Known Issues

See `AUDIT_REPORT.md` for complete security audit. Key concerns:
- Credentials in `.env` need secrets management

## Blocked By

- **HW-001:** Telegram bot token creation (in humans-work-needed queue)

## Testing

```bash
# Run tests (MUST use venv python)
cd /home/adminmatej/github/applications/sense-kraliki
.venv/bin/python -m pytest tests/test_analytics.py tests/test_handlers.py tests/test_services.py tests/test_persistence.py -v

# Run all tests including e2e
.venv/bin/python -m pytest tests/ -v

# Test specific module
.venv/bin/python -m pytest tests/test_services.py -v

# NOTE: Do NOT use system python (python3 -m pytest) - it lacks required dependencies
```

---

*Part of the GitHub workspace at /home/adminmatej/github*
*See parent @../../../CLAUDE.md for workspace conventions*
