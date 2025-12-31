# Test 011: Data Sources Integration

**Feature:** All 9 cosmic/environmental data sources
**Priority:** P1 (Important)
**Type:** Telegram Bot / Integration
**Estimated Time:** 5 minutes

## Objective

Verify all 9 data sources are correctly fetched, processed, and contribute to the sensitivity score.

## Preconditions

- Bot is running
- Internet access for external APIs
- User has location and birthdate set for full data

## Data Sources Overview

| Source | API/Method | Contribution | Max Points |
|--------|------------|--------------|------------|
| Geomagnetic | NOAA SWPC | Kp index | 30 |
| Solar Flares | NOAA SWPC | X/M/C class | 20 |
| Earthquakes | USGS | M4+ events | 10 |
| Schumann | Internal calc | Resonance | 20 |
| Weather | Open-Meteo | Pressure/humidity | 15 |
| Astrology | Swiss Ephemeris | Planetary | 25 |
| Biorhythm | Internal calc | Cycles | 20 |
| Moon Phase | Swiss Ephemeris | Lunar cycle | (in astro) |
| Mercury Rx | Swiss Ephemeris | Retrograde | (in astro) |

**Max Raw Total:** 140 points -> Normalized to 0-100

## Test Steps

### Test 11.1: Geomagnetic Data (NOAA)

1. Send `/sense`
2. Check "Geomagnetic" factor in breakdown
3. **Expected:** Shows score 0-30 based on Kp index:
   - Kp 0-3: Low (0-10)
   - Kp 4-5: Moderate (11-20)
   - Kp 6-9: High (21-30)

### Test 11.2: Solar Flare Data (NOAA)

1. Send `/sense`
2. Check "Solar" factor in breakdown
3. **Expected:** Shows score 0-20 based on flare activity:
   - C-class: 0-5
   - M-class: 6-12
   - X-class: 13-20

### Test 11.3: Earthquake Data (USGS)

1. Send `/sense`
2. Check "Seismic" factor in breakdown
3. **Expected:** Shows score 0-10:
   - No M4+ quakes: 0
   - M4-5 quakes: 1-3
   - M5-6 quakes: 4-6
   - M6+ quakes: 7-10

### Test 11.4: Schumann Resonance

1. Send `/sense`
2. Check "Schumann" factor in breakdown
3. **Expected:** Shows score 0-20:
   - Normal (7.83 Hz baseline): Low
   - Elevated activity: Medium
   - Extreme activity: High

### Test 11.5: Weather Data (Open-Meteo)

1. Ensure location is set (`/setlocation 50.0755, 14.4378`)
2. Send `/sense`
3. Check "Weather" factor in breakdown
4. **Expected:** Shows score 0-15 based on:
   - Pressure changes
   - Humidity levels
   - Temperature extremes

### Test 11.6: Weather Without Location

1. Clear location (or new user)
2. Send `/sense`
3. **Expected:** Weather shows 0 or "N/A"
4. Other factors still calculate

### Test 11.7: Astrology Data (Swiss Ephemeris)

1. Send `/sense`
2. Check "Astrology" factor in breakdown
3. **Expected:** Shows score 0-25 based on:
   - Planetary positions
   - Moon phase
   - Mercury retrograde
   - Major aspects

### Test 11.8: Detailed Astro Check

1. Send `/astro`
2. **Expected:** All astrology components:
   - Sun sign
   - Moon sign
   - Moon phase + illumination
   - Mercury retrograde status
   - Planetary positions

### Test 11.9: Biorhythm Data

1. Ensure birthdate is set (`/setbirthday 1990-05-15`)
2. Send `/sense`
3. Check "Biorhythm" factor in breakdown
4. **Expected:** Shows score 0-20:
   - All cycles high: 0-5
   - Mixed cycles: 6-12
   - All cycles low: 13-20

### Test 11.10: Biorhythm Without Birthdate

1. Clear birthdate (or new user)
2. Send `/sense`
3. **Expected:** Biorhythm shows 0 or "N/A"
4. Other factors still calculate

### Test 11.11: API Failure Handling

If external API is down:
1. Bot should not crash
2. **Expected:** Graceful degradation
3. Failed source shows 0 or error indicator
4. Other sources still work

### Test 11.12: Concurrent Fetch Performance

1. Note time when sending `/sense`
2. Note time when response received
3. **Expected:** Response within 5-10 seconds
4. All 7 sources fetched concurrently (asyncio.gather)

### Test 11.13: Moon Phase in Alerts

1. If moon is Full or New
2. Send `/sense`
3. **Expected:** Alert about moon phase
4. "Full Moon - heightened emotions" (if full)

### Test 11.14: Mercury Retrograde Alert

1. If Mercury is retrograde
2. Send `/sense`
3. **Expected:** Alert about Mercury Rx
4. "Mercury retrograde active"

## Success Criteria

- [ ] Geomagnetic data fetches and scores (0-30)
- [ ] Solar flare data fetches and scores (0-20)
- [ ] Earthquake data fetches and scores (0-10)
- [ ] Schumann resonance calculates (0-20)
- [ ] Weather data fetches when location set (0-15)
- [ ] Astrology data calculates (0-25)
- [ ] Biorhythm calculates when birthdate set (0-20)
- [ ] Moon phase included in astrology
- [ ] Mercury retrograde detected
- [ ] Missing data handled gracefully
- [ ] API failures don't crash bot
- [ ] Concurrent fetch is performant

## Data Source Details

### NOAA Space Weather Prediction Center

```
URL: https://services.swpc.noaa.gov/
Endpoints:
- /products/noaa-planetary-k-index.json
- /products/alerts.json
```

### USGS Earthquake Hazards

```
URL: https://earthquake.usgs.gov/
Endpoint: /fdsnws/event/1/query
Params: format=geojson, minmagnitude=4
```

### Open-Meteo Weather

```
URL: https://api.open-meteo.com/v1/forecast
Params: latitude, longitude, current_weather=true
```

### Swiss Ephemeris

```
Library: pyswisseph
Local calculation, no external API
```

## Notes

- All external APIs are free/public
- NOAA and USGS are US government sources
- Open-Meteo is open-source weather
- Swiss Ephemeris is included in package
- Schumann resonance is estimated (no reliable real-time API)
- Biorhythm is deterministic calculation
