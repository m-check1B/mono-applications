# Test 007: User Settings

**Feature:** /setbirthday, /setlocation commands
**Priority:** P1 (Important)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify users can set and update their personal settings (birthdate and location) for personalized readings.

## Preconditions

- Bot is running
- Redis storage is available

## Test Steps

### Test 7.1: Set Birthday with Command

1. Send `/setbirthday 1990-05-15`
2. **Expected:** Confirmation message:
   - "Birth date set to 1990-05-15"
   - "Your biorhythm and forecasts are now personalized!"

### Test 7.2: Set Birthday Interactive

1. Send `/setbirthday` (no date)
2. **Expected:** Prompt for date format
3. Send `1985-12-25`
4. **Expected:** Confirmation of date set

### Test 7.3: Invalid Birthday Format

Test various invalid formats:

1. `/setbirthday invalid` -> Error
2. `/setbirthday 15-05-1990` -> Error (wrong format)
3. `/setbirthday 1990/05/15` -> Error (slashes)
4. `/setbirthday 1990-13-45` -> Error (invalid date)

**Expected:** Each shows error with correct format example

### Test 7.4: Set Location with Command

1. Send `/setlocation 50.0755, 14.4378`
2. **Expected:** Confirmation:
   - "Location set to 50.0755, 14.4378"
   - "Weather data will be included in your sensitivity score!"

### Test 7.5: Set Location Variations

Test valid coordinate formats:

1. `/setlocation 50.0755,14.4378` (no space)
2. `/setlocation 50.0755, 14.4378` (with space)
3. `/setlocation -33.8688, 151.2093` (negative lat - Sydney)

**Expected:** All should be accepted

### Test 7.6: Invalid Location Format

Test invalid formats:

1. `/setlocation invalid` -> Error
2. `/setlocation 50.0755` -> Error (missing longitude)
3. `/setlocation Prague` -> Error (city name not supported)

**Expected:** Each shows error with correct format example

### Test 7.7: Set Location Interactive

1. Send `/setlocation` (no coordinates)
2. **Expected:** Prompt for coordinates with example
3. Includes Google Maps tip for finding coordinates

### Test 7.8: Update Existing Settings

1. Set birthday: `/setbirthday 1990-01-01`
2. Update birthday: `/setbirthday 1991-06-15`
3. **Expected:** New date replaces old
4. Send `/bio` to verify new date is used

### Test 7.9: Settings Persistence

1. Set birthday and location
2. Restart bot (or wait for next session)
3. Send `/bio`
4. **Expected:** Settings persisted, biorhythm works

### Test 7.10: Settings in Onboarding

1. Start fresh account
2. Send `/start` and begin onboarding
3. Enter birthdate when prompted
4. Enter location when prompted
5. **Expected:** Both settings saved through onboarding flow

## Success Criteria

- [ ] /setbirthday accepts YYYY-MM-DD format
- [ ] /setbirthday rejects invalid formats with helpful error
- [ ] /setlocation accepts LAT,LON coordinates
- [ ] /setlocation handles negative coordinates
- [ ] /setlocation rejects invalid formats with helpful error
- [ ] Settings persist across sessions
- [ ] Settings update correctly (overwrite old values)
- [ ] Onboarding flow sets both correctly

## Storage Schema

```json
{
  "user_id": 12345,
  "birth_date": "1990-05-15T00:00:00",
  "latitude": 50.0755,
  "longitude": 14.4378,
  "premium": false,
  "premium_until": null,
  "plan": null
}
```

## Coordinate Reference

| City | Coordinates |
|------|-------------|
| Prague | 50.0755, 14.4378 |
| New York | 40.7128, -74.0060 |
| London | 51.5074, -0.1278 |
| Tokyo | 35.6762, 139.6503 |
| Sydney | -33.8688, 151.2093 |
| Sao Paulo | -23.5505, -46.6333 |

## Notes

- Birth date is required for /bio and personalized /forecast
- Location is required for weather-based sensitivity data
- Both are optional but recommended for best experience
- Data stored in Redis (or PostgreSQL when configured)
- Settings are private and not shared
