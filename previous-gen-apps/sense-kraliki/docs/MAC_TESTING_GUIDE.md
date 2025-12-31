# Mac Testing Guide for Sense by Kraliki Bot

This guide provides instructions for testing the Sense by Kraliki Telegram bot on macOS, including Python setup, API key configuration, and testing sensitivity calculations.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Python Setup](#python-setup)
3. [Project Setup](#project-setup)
4. [API Keys Configuration](#api-keys-configuration)
5. [Testing Sensitivity Calculations](#testing-sensitivity-calculations)
6. [Bot Testing](#bot-testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- macOS 12 (Monterey) or later
- Homebrew installed (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- Git installed (`brew install git`)
- A Telegram account for bot testing

---

## Python Setup

### Install Python 3.11+

```bash
# Install Python via Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

### Install uv (Fast Python Package Manager)

```bash
# Install uv (recommended for this project)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

Alternatively, use pip:
```bash
pip3 install --upgrade pip
```

---

## Project Setup

### Clone and Setup

```bash
# Clone the repository (adjust path as needed)
git clone <repository-url>
cd sense-kraliki

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Dependencies Overview

The project requires:
- `aiogram>=3.15.0` - Telegram bot framework
- `httpx>=0.28.0` - Async HTTP client for API calls
- `google-generativeai>=0.8.0` - Gemini AI for dream analysis
- `pyswisseph>=2.10.0` - Swiss Ephemeris for astrology calculations
- `pydantic-settings>=2.6.0` - Configuration management

---

## API Keys Configuration

### Required API Keys

Sense by Kraliki uses several data sources. Here is how to obtain and configure each:

### 1. Telegram Bot Token (Required)

```bash
# Steps to obtain:
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot command
# 3. Follow prompts to name your bot
# 4. Copy the token provided
```

### 2. Gemini API Key (Required for Dream Analysis)

```bash
# Steps to obtain:
# 1. Go to https://aistudio.google.com/
# 2. Sign in with Google account
# 3. Navigate to "Get API Key"
# 4. Create new API key
# 5. Copy the key
```

### 3. Data Source APIs (Free, No Keys Required)

The following data sources are 100% free and require no API keys:

| Data Source | API Endpoint | Key Required |
|------------|--------------|--------------|
| NOAA Space Weather | services.swpc.noaa.gov | No |
| USGS Earthquakes | earthquake.usgs.gov | No |
| Open-Meteo Weather | api.open-meteo.com | No |
| Schumann Resonance | geocenter.info | No |

### Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Contents of .env:**
```bash
# Telegram Bot (Required)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Gemini AI (Required for dream analysis)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_VISION_MODEL=gemini-2.0-flash

# Database (optional for local testing)
DATABASE_URL=postgresql+asyncpg://localhost/sense_kraliki
REDIS_URL=redis://localhost:6379/0

# Admin user IDs (comma-separated Telegram user IDs)
ADMIN_USER_IDS=[]
```

---

## Testing Sensitivity Calculations

### Understanding the Sensitivity Score

The sensitivity score (0-100) is calculated from 9 data sources:

| Source | Max Points | Description |
|--------|-----------|-------------|
| Geomagnetic (Kp index) | 30 | Space weather storms |
| Solar Flares | 20 | X-ray flux events |
| Earthquakes | 10 | M5+ seismic activity |
| Schumann Resonance | 20 | Earth's EM pulse |
| Weather | 15 | Pressure, humidity |
| Astrology | 25 | Planetary positions |
| Biorhythm | 20 | Personal cycles |

**Total Max: 140 points, normalized to 0-100**

### Test Sensitivity Calculation Locally

Create a test script `test_sensitivity_local.py`:

```python
#!/usr/bin/env python3
"""Test sensitivity calculations locally."""
import asyncio
from datetime import datetime

# Ensure we're in the project root
import sys
sys.path.insert(0, '.')

from app.services.sensitivity import calculate_sensitivity, SensitivityReport


async def test_sensitivity():
    """Run sensitivity calculation test."""
    print("=" * 60)
    print("SENSE BY KRALIKI SENSITIVITY CALCULATION TEST")
    print("=" * 60)

    # Test without location/birthdate (uses only cosmic data)
    print("\n1. Basic Sensitivity (Cosmic Data Only)")
    print("-" * 40)

    report = await calculate_sensitivity()
    print(report.to_summary())

    # Test with location (adds weather data)
    print("\n\n2. With Location (Prague, Czech Republic)")
    print("-" * 40)

    report_with_location = await calculate_sensitivity(
        latitude=50.0755,
        longitude=14.4378
    )
    print(report_with_location.to_summary())

    # Test with birthdate (adds biorhythm)
    print("\n\n3. With Birth Date (adds biorhythm)")
    print("-" * 40)

    report_full = await calculate_sensitivity(
        latitude=50.0755,
        longitude=14.4378,
        birth_date=datetime(1990, 6, 15)  # Example birthdate
    )
    print(report_full.to_summary())

    # Detailed breakdown
    print("\n\n4. Detailed Breakdown")
    print("-" * 40)
    print(f"Score: {report_full.score}/100")
    print(f"Level: {report_full.level}")
    print(f"Raw breakdown:")
    print(f"  - Geomagnetic: {report_full.breakdown.geomagnetic}/30")
    print(f"  - Solar Flares: {report_full.breakdown.solar_flares}/20")
    print(f"  - Earthquakes: {report_full.breakdown.earthquakes}/10")
    print(f"  - Schumann: {report_full.breakdown.schumann}/20")
    print(f"  - Weather: {report_full.breakdown.weather}/15")
    print(f"  - Astrology: {report_full.breakdown.astrology}/25")
    print(f"  - Biorhythm: {report_full.breakdown.biorhythm}/20")
    print(f"  - Total Raw: {report_full.breakdown.total}/140")
    print(f"  - Normalized: {report_full.breakdown.normalized}/100")


if __name__ == "__main__":
    asyncio.run(test_sensitivity())
```

Run the test:
```bash
# Activate virtual environment
source .venv/bin/activate

# Run sensitivity test
python test_sensitivity_local.py
```

### Test Individual Data Sources

```python
#!/usr/bin/env python3
"""Test individual data sources."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.data.noaa import get_noaa_data
from app.data.usgs import get_earthquake_score
from app.data.weather import fetch_weather
from app.data.schumann import get_schumann_data
from app.data.astro import get_astro_data


async def test_data_sources():
    """Test each data source individually."""

    print("Testing NOAA Data (Space Weather)...")
    noaa = await get_noaa_data()
    if noaa.get("geomagnetic"):
        geo = noaa["geomagnetic"]
        print(f"  Kp Index: {geo.kp_index}")
        print(f"  Level: {geo.level}")
        print(f"  Interpretation: {geo.interpretation}")
    else:
        print("  [No data available]")

    print("\nTesting USGS Data (Earthquakes)...")
    score, quakes = await get_earthquake_score()
    print(f"  Score: {score}/10")
    print(f"  Earthquakes (M5+): {len(quakes)}")
    for q in quakes[:3]:
        print(f"    - M{q.magnitude} {q.location}")

    print("\nTesting Weather Data (Prague)...")
    weather = await fetch_weather(50.0755, 14.4378)
    if weather:
        print(f"  Temperature: {weather.temperature_c}C")
        print(f"  Humidity: {weather.humidity}%")
        print(f"  Pressure: {weather.pressure_hpa} hPa")
        print(f"  Condition: {weather.weather_condition}")
    else:
        print("  [No data available]")

    print("\nTesting Schumann Resonance...")
    schumann = await get_schumann_data()
    if schumann:
        print(f"  Frequency: {schumann.frequency} Hz")
        print(f"  Intensity: {schumann.intensity}")
    else:
        print("  [No data available]")

    print("\nTesting Astrology Data...")
    astro = await get_astro_data()
    if astro:
        print(f"  Moon Phase: {astro.moon_phase.phase_name}")
        print(f"  Mercury Retrograde: {astro.mercury_retrograde}")
    else:
        print("  [No data available]")


if __name__ == "__main__":
    asyncio.run(test_data_sources())
```

### Test Biorhythm Calculations

```python
#!/usr/bin/env python3
"""Test biorhythm calculations."""
from datetime import datetime
import sys
sys.path.insert(0, '.')

from app.services.biorhythm import (
    calculate_biorhythm,
    get_biorhythm_forecast,
    find_next_critical_days
)


def test_biorhythm():
    """Test biorhythm calculations."""

    # Example birth date
    birth_date = datetime(1990, 6, 15)

    print("BIORHYTHM TEST")
    print("=" * 50)
    print(f"Birth Date: {birth_date.strftime('%Y-%m-%d')}")
    print()

    # Current biorhythm
    bio = calculate_biorhythm(birth_date)

    print("Current Biorhythm:")
    print(f"  Physical: {bio.physical:+4d} ({bio.physical_phase})")
    print(f"  Emotional: {bio.emotional:+4d} ({bio.emotional_phase})")
    print(f"  Intellectual: {bio.intellectual:+4d} ({bio.intellectual_phase})")
    print(f"  Intuitive: {bio.intuitive:+4d} ({bio.intuitive_phase})")
    print(f"  Overall: {bio.overall:+4d}")
    print(f"  Interpretation: {bio.interpretation}")
    print(f"  Sensitivity Score: {bio.sensitivity_score}/20")

    if bio.critical_days:
        print(f"  Critical Days: {', '.join(bio.critical_days)}")

    # Upcoming critical days
    print("\n\nUpcoming Critical Days (next 14 days):")
    print("-" * 50)
    critical = find_next_critical_days(birth_date, search_days=14)
    for event in critical[:5]:
        print(f"  {event['date']} (in {event['days_from_now']} days)")
        print(f"    Cycles: {', '.join(event['cycles'])}")
        print(f"    Advice: {event['advice']}")


if __name__ == "__main__":
    test_biorhythm()
```

---

## Bot Testing

### Run the Bot Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Run bot in polling mode (for development)
python -m app.main
```

### Test Bot Commands

Open Telegram and find your test bot, then test these commands:

| Command | Expected Result |
|---------|-----------------|
| `/start` | Welcome message with bot description |
| `/sense` | Current sensitivity score with breakdown |
| `/health` | Bot uptime and status |
| `/astro` | Current astrological influences |
| `/remedies` | Holistic recommendations based on current conditions |

### Test with Birth Date

```
/setbirthday 1990-06-15
/bio
```

Expected: Biorhythm chart with physical, emotional, intellectual, and intuitive cycles.

### Test with Location

```
/setlocation 50.0755, 14.4378
/sense
```

Expected: Sensitivity score now includes weather data from the specified location.

### Test Dream Analysis (Requires Gemini API Key)

```
/dream I was flying over mountains and saw a golden city below
```

Expected: Jungian-style dream analysis with archetypal symbols interpreted.

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'app'"

```bash
# Ensure you're in the project root directory
cd /path/to/sense-kraliki

# Reinstall dependencies
uv sync
source .venv/bin/activate
```

#### 2. "TELEGRAM_BOT_TOKEN is required"

```bash
# Check .env file exists and has the token
cat .env | grep TELEGRAM_BOT_TOKEN

# Ensure no spaces around the = sign
# WRONG: TELEGRAM_BOT_TOKEN = your_token
# RIGHT: TELEGRAM_BOT_TOKEN=your_token
```

#### 3. "Connection refused" on data fetches

```bash
# Test internet connectivity
curl -s https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json | head -c 200

# If blocked, check firewall/VPN settings
```

#### 4. Swiss Ephemeris issues (pyswisseph)

```bash
# Install required system libraries on macOS
brew install swig

# Reinstall pyswisseph
pip uninstall pyswisseph
pip install pyswisseph
```

#### 5. Gemini API errors

- Verify API key at https://aistudio.google.com/
- Check quota limits (free tier has request limits)
- Ensure `GEMINI_API_KEY` is set correctly in `.env`

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_services.py -v

# Run specific test
pytest tests/test_services.py::TestBiorhythmService::test_biorhythm_calculation -v
```

---

## Additional Resources

- **Project CLAUDE.md**: `/applications/sense-kraliki/CLAUDE.md` - Project memory and commands
- **SKILL.md**: `/applications/sense-kraliki/SKILL.md` - Detailed architecture and capabilities
- **AUDIT_REPORT.md**: `/applications/sense-kraliki/AUDIT_REPORT.md` - Security audit findings

---

## Contact

For issues specific to this project, file a GitHub issue or contact the development team.

---

*Generated for Sense by Kraliki Bot - Telegram sensitivity tracking for HSPs*
