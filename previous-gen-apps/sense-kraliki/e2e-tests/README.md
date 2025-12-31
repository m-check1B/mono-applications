# Sense by Kraliki E2E Tests

End-to-end test plans for the Sense by Kraliki Telegram sensitivity tracking bot.

## Application Overview

**Sense by Kraliki** is a B2B/B2C sensitivity tracking service that combines 9 cosmic/environmental data sources into a unified sensitivity score (0-100). Helps users understand how space weather, seismic activity, moon phases, and more affect their wellbeing.

- **Type:** Telegram Bot (primary) + Future Web Dashboard
- **Beta URL:** https://sense.verduona.dev (when available)
- **Telegram Bot:** @SenseItBot (Sense by Kraliki, production)
- **Revenue:** B2B audits at EUR 500/audit

## Test Categories

### Bot Commands (Telegram)

| Test File | Feature | Priority |
|-----------|---------|----------|
| 001-start-onboarding.md | /start command and guided setup | P0 |
| 002-sense-command.md | /sense sensitivity score | P0 |
| 003-dream-analysis.md | /dream Jungian analysis | P1 |
| 004-biorhythm.md | /bio personal cycles | P1 |
| 005-astrology.md | /astro planetary influences | P1 |
| 006-remedies.md | /remedies holistic recommendations | P1 |
| 007-settings.md | /setbirthday, /setlocation | P1 |
| 008-subscription.md | /subscribe, /status payments | P0 |
| 009-audit-booking.md | /audit B2B audit feature | P0 |
| 010-admin-stats.md | /stats admin analytics | P2 |

### Data Sources

| Test File | Feature | Priority |
|-----------|---------|----------|
| 011-data-sources.md | All 9 data source integrations | P1 |

## Test Execution

### For Telegram Bot Testing

Tests are designed to be executed via:
1. Direct Telegram interaction with the bot
2. Bot API mocking in pytest (see `/tests/e2e/`)

### For Future Web Dashboard

When the web dashboard is available:
1. CLI Claude creates test plans here
2. Human pastes into Chrome extension
3. Browser agent executes
4. Results written to `results/`

## Running Tests

```bash
# Via pytest (bot API mocking)
cd /home/adminmatej/github/applications/sense-kraliki
pytest tests/e2e/ -v

# Via Chrome extension (future web UI)
# 1. Paste test instructions into Claude Code extension
# 2. Results are written to e2e-tests/results/
```

## Results Structure

```
e2e-tests/
  results/
    001-start-onboarding-PASSED-2025-12-25.md
    002-sense-command-FAILED-2025-12-25.md
    ...
```

## Priority Levels

- **P0:** Critical path - must pass for release
- **P1:** Important features - should pass
- **P2:** Nice-to-have - can be skipped temporarily

## Sensitivity Levels Reference

| Score | Level | Color |
|-------|-------|-------|
| 0-19 | Low | Green |
| 20-39 | Moderate | Yellow |
| 40-59 | Elevated | Orange |
| 60-79 | High | Red |
| 80-100 | Extreme | Warning |

## Bot Commands Reference

| Command | Description | Access |
|---------|-------------|--------|
| /start | Welcome + onboarding | All |
| /sense | Current sensitivity score | All |
| /dream [text] | Jungian dream analysis | All (3 free/mo) |
| /bio | Biorhythm chart | Requires birthdate |
| /astro | Astrological influences | All |
| /remedies | Holistic recommendations | All |
| /forecast | 12-month outlook | Premium |
| /setbirthday | Set birth date | All |
| /setlocation | Set coordinates | All |
| /subscribe | Purchase premium | All |
| /status | Subscription status | All |
| /audit | Book Reality Check | All |
| /health | Bot uptime | All |
| /stats | Analytics | Admin only |
