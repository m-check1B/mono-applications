# Sense by Kraliki - Environmental Sensitivity Tracker

Formerly SenseIt.

Turn cosmic awareness into actionable wellness intelligence for Highly Sensitive People (HSPs).

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Sense is an external module integrated with Kraliki Swarm.
========================================

## Overview

Sense by Kraliki is a Telegram bot that analyzes 9 environmental and cosmic data points to help highly sensitive people understand why they feel overwhelmed and how to find their balance. By aggregating real-time data from NASA, NOAA, and global environmental sensors, Sense by Kraliki calculates a **Daily Sensitivity Index (DSI)** with personalized, science-backed remedies.

## Product Scope

Sense by Kraliki is a sensitivity intelligence bot for HSPs. It focuses on environmental, cosmic, and biorhythm signals that influence wellbeing and delivers daily insights, alerts, and remedies. It is not an OCR or document analysis product.

## Target Users

- **Highly Sensitive People (HSPs):** Individuals with heightened sensory processing sensitivity
- **Wellness Enthusiasts:** People seeking holistic health insights
- **Biohackers:** Those optimizing their performance through environmental awareness

## Core Features

### 1. Daily Sensitivity Index (DSI)
A unified score (0-100) combining cosmic, geomagnetic, and local environmental factors:
- Geomagnetic storms (Kp index)
- Solar flare activity
- Seismic activity
- Schumann resonance
- Weather patterns (pressure, humidity)
- Astrological influences
- Moon phases
- Mercury retrograde periods
- Personal biorhythms

### 2. Real-time Alerts
Get notified when significant environmental shifts occur that may affect your sensitivity.

### 3. Bi-Weekly Forecasts
Plan high-intensity meetings, social events, or creative work around your projected sensitivity baseline.

### 4. Personalized Remedies
Science-backed suggestions to mitigate environmental impact:
- Grounding exercises for geomagnetic activity
- Screen time limits during solar flares
- Sleep optimization during specific moon phases

### 5. Historical Tracking
See patterns in your wellbeing over months, not just days. Correlate how you felt with what was happening in your environment.

### 6. Dream Analysis (Premium)
Jungian dream analysis using Gemini AI, correlated with current cosmic conditions to reveal subconscious patterns.

## Technology Stack

- **Bot Framework:** aiogram 3.x (async Telegram bot)
- **AI Analysis:** Gemini 2.0 Flash (dream interpretation)
- **Astrology Engine:** pyswisseph (Swiss Ephemeris)
- **Data Sources:** 
  - NOAA (space weather, geomagnetic data)
  - USGS (earthquake data)
  - Open-Meteo (weather API)
  - Schumann resonance monitoring
- **Storage:** Redis/PostgreSQL (optional)
- **Payments:** Telegram Stars

## Pricing (Telegram Stars)

| Level | Price | Features |
|-------|-------|----------|
| **Seeker** | Free | Daily Sensitivity Index, General Alerts |
| **Sensitive** | 150 Stars/mo ($3) | Unlimited detailed analyses, 6-month forecasts, Priority support |
| **Empath** | 350 Stars/mo ($7) | Everything in Sensitive, 12-month forecasts, Personalized remedies, Private HSP Community access |

## Bot Commands

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Welcome message and onboarding | All |
| `/sense` | Current sensitivity score with breakdown | All |
| `/dream [text]` | Jungian dream analysis | All (3 free/mo) |
| `/bio` | Biorhythm chart visualization | Requires birthdate |
| `/astro` | Current astrological influences | All |
| `/remedies` | Holistic recommendations | All |
| `/forecast` | 12-month outlook | Premium |
| `/setbirthday` | Set birth date for personalized readings | All |
| `/setlocation` | Set coordinates for local environmental data | All |
| `/subscribe` | Purchase premium subscription | All |
| `/status` | Check subscription status | All |

## Development

### Setup

```bash
cd applications/sense-kraliki
uv sync
source .venv/bin/activate
```

### Configuration

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

### Running

```bash
# Dev mode (polling)
python -m app.main

# Production (Docker)
docker compose up -d

# Logs
docker compose logs -f sense-kraliki-bot
```

### Testing

```bash
pytest
pytest tests/test_sensitivity.py -v
```

## Security

### Secret Rotation (IMPORTANT)

Production credentials were previously exposed in `.env` file. All secrets have been rotated:

- **Telegram Bot Token:** Regenerated via @BotFather
- **Gemini API Key:** Regenerated via Google AI Studio

If you're deploying this bot, you must:
1. Obtain fresh tokens from their respective platforms
2. Never commit `.env` to version control
3. Use `.env.example` as template only
4. Pre-commit hook prevents accidental secret commits

### Pre-commit Protection

A pre-commit hook is installed to prevent accidental secret commits. It checks for:
- Specific known leaked tokens
- API key patterns (sk-, pk-, AIzaSy, etc.)
- .env files being committed

To bypass temporarily (use with caution):
```bash
git commit --no-verify
```

## Sensitivity Levels

| Score | Level | Color | Description |
|-------|-------|-------|-------------|
| 0-19 | Low | Green | Optimal conditions for sensitive individuals |
| 20-39 | Moderate | Yellow | Slightly elevated sensitivity, practice grounding |
| 40-59 | Elevated | Orange | High sensitivity, plan accordingly |
| 60-79 | High | Red | Very sensitive conditions, minimize stress |
| 80-100 | Extreme | Warning | Extreme environmental sensitivity, rest recommended |

## Data Sources

Sense by Kraliki aggregates data from 9 sources:

1. **NOAA Geomagnetic** - Kp index (0-9 scale)
2. **NOAA Solar** - Flare activity (X/M/C class)
3. **USGS Seismic** - Earthquakes (M4+)
4. **Schumann Resonance** - Earth's electromagnetic pulse
5. **Open-Meteo Weather** - Pressure, humidity, temperature
6. **Swiss Ephemeris** - Planetary positions and aspects
7. **Moon Phase** - Current lunar cycle position
8. **Mercury Retrograde** - Communication and technology periods
9. **Biorhythm** - Personal cycles (physical, emotional, intellectual)

## Project Status

✅ Core bot functionality implemented  
✅ 9 data sources integrated with concurrent fetching  
✅ Sensitivity scoring engine operational  
⏳ Landing page deployment  
⏳ Production bot token provisioning (blocked by HW-001)  
⏳ Redis/Postgres persistence for user state  

## Documentation

- [CLAUDE.md](CLAUDE.md) - Developer memory and architecture details
- [SKILL.md](SKILL.md) - Capabilities and integration guide
- [AUDIT_REPORT.md](AUDIT_REPORT.md) - Security audit findings

## License

Part of Verduona ecosystem. © 2025

---

**Brace the Impact.**  
[Start Sense by Kraliki on Telegram](https://t.me/senseit_bot) | [Privacy Policy] | [Terms of Service]
