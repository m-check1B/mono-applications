# Test 002: Sense Command - Sensitivity Score

**Feature:** /sense command - unified sensitivity score calculation
**Priority:** P0 (Critical)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify that the /sense command correctly calculates and displays the sensitivity score from all 9 data sources.

## Preconditions

- Bot is running
- User has completed onboarding (birthdate + location set) for best results
- External APIs (NOAA, USGS, Open-Meteo) are accessible

## Test Steps

### Test 2.1: Basic Sense Command

1. Send `/sense` to the bot
2. **Expected:** First message: "Calculating your sensitivity score..."
3. Wait for calculation (may take 2-5 seconds due to API calls)
4. **Expected:** Formatted sensitivity report with:
   - Score (0-100)
   - Level (Low/Moderate/Elevated/High/Extreme)
   - Color emoji indicator
   - Contributing factors breakdown

### Test 2.2: Verify Score Components

Check that the response includes all 7 contributing factors:

1. Geomagnetic (from NOAA)
2. Solar (from NOAA flares)
3. Seismic (from USGS earthquakes)
4. Schumann (resonance data)
5. Weather (if location set)
6. Astrology (Swiss Ephemeris)
7. Biorhythm (if birthdate set)

**Expected:** Each factor shows:
- Name with emoji
- Visual bar [##########]
- Score/MaxScore (e.g., "15/30")

### Test 2.3: Score Levels

Verify correct level classification:

| Score Range | Expected Level | Expected Emoji |
|-------------|----------------|----------------|
| 0-19 | LOW | Green circle |
| 20-39 | MODERATE | Yellow circle |
| 40-59 | ELEVATED | Orange circle |
| 60-79 | HIGH | Red circle |
| 80-100 | EXTREME | Warning sign |

### Test 2.4: Alerts Section

When conditions warrant alerts, verify presence of:
- Geomagnetic storm alerts (Kp >= 5)
- Solar flare alerts (significant activity)
- Earthquake alerts (M6+)
- Mercury retrograde alert
- Full moon alert
- Biorhythm critical day alerts

### Test 2.5: Recommendations Section

Verify recommendations appear based on:
- High sensitivity (>60): Rest/grounding suggestions
- Extreme sensitivity (>80): Avoid major decisions
- Weather-specific: Humidity, pressure change tips
- Biorhythm-specific: Based on low cycles

### Test 2.6: Without Location

1. Clear or skip location in user profile
2. Send `/sense`
3. **Expected:** Weather factor shows 0 or "N/A"
4. Other factors still calculate

### Test 2.7: Without Birthdate

1. Clear birthdate from profile
2. Send `/sense`
3. **Expected:** Biorhythm factor shows 0 or "N/A"
4. Other factors still calculate

### Test 2.8: Error Handling

1. If external APIs are down
2. **Expected:** Graceful error message
3. Should not crash the bot

## Success Criteria

- [ ] /sense returns formatted sensitivity report
- [ ] Score is between 0-100
- [ ] Level matches score range correctly
- [ ] All 7 factors display with visual bars
- [ ] Alerts appear when conditions warrant
- [ ] Recommendations are contextual
- [ ] Works with or without location/birthdate
- [ ] Handles API errors gracefully

## Notes

- Calculation may take 2-5 seconds due to external API calls
- All data sources are fetched concurrently (asyncio.gather)
- Max raw score is 140, normalized to 0-100
