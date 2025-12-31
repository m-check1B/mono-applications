# Test 005: Astrology Influences

**Feature:** /astro command - astrological planetary positions
**Priority:** P1 (Important)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify the astrology feature correctly calculates and displays current planetary positions, moon phase, and Mercury retrograde status.

## Preconditions

- Bot is running
- Swiss Ephemeris data is available

## Test Steps

### Test 5.1: Basic Astro Command

1. Send `/astro`
2. **Expected:** First message: "Calculating astrological influences..."
3. **Expected:** Response with:
   - Sun sign position
   - Moon sign position
   - Moon phase information
   - Mercury retrograde status
   - Major planetary positions

### Test 5.2: Sun and Moon Signs

1. Send `/astro`
2. **Expected:** Shows current signs:
   - "Sun in [Sign]" (e.g., "Sun in Capricorn")
   - "Moon in [Sign]" (e.g., "Moon in Taurus")

### Test 5.3: Moon Phase Details

1. Send `/astro`
2. **Expected:** Moon phase section with:
   - Phase name (New Moon, Waxing Crescent, First Quarter, etc.)
   - Illumination percentage
   - Phase interpretation for sensitivity

### Test 5.4: Mercury Retrograde

1. Send `/astro`
2. **Expected:** Mercury retrograde status:
   - "Mercury Retrograde: Yes - communications may be challenged"
   - OR "Mercury Retrograde: No"

### Test 5.5: Planetary Positions

1. Send `/astro`
2. **Expected:** Top 5 planetary positions:
   - Planet name
   - Current sign
   - Retrograde indicator (Rx) if applicable

Example:
```
Planetary Positions:
- Mercury in Sagittarius
- Venus in Aquarius (Rx)
- Mars in Leo
- Jupiter in Taurus
- Saturn in Pisces
```

### Test 5.6: Sensitivity Contribution

1. Send `/astro`
2. **Expected:** Shows sensitivity score contribution
   - "Sensitivity contribution: X/25"
   - Range is 0-25 points

### Test 5.7: Full Moon Detection

If current moon is full:
1. Send `/astro`
2. **Expected:** Full Moon indicator
3. Send `/sense`
4. **Expected:** Alert about Full Moon in sensitivity report

### Test 5.8: Retrograde Detection

When planets are retrograde:
1. Send `/astro`
2. **Expected:** (Rx) marker next to retrograde planets
3. Impact on sensitivity score

### Test 5.9: Error Handling

1. If Swiss Ephemeris fails
2. **Expected:** Graceful error message
3. Bot continues functioning

## Success Criteria

- [ ] /astro shows Sun and Moon signs
- [ ] Moon phase with illumination percentage
- [ ] Mercury retrograde status displayed
- [ ] Top planetary positions shown
- [ ] Retrograde indicators (Rx) appear
- [ ] Sensitivity contribution score shown
- [ ] Full moon triggers alerts
- [ ] Error handling is graceful

## Moon Phases

| Phase | Days | Sensitivity Impact |
|-------|------|-------------------|
| New Moon | 0-3 | Low, introspective |
| Waxing Crescent | 3-7 | Building energy |
| First Quarter | 7-10 | Action oriented |
| Waxing Gibbous | 10-14 | Increasing tension |
| Full Moon | 14-17 | Peak sensitivity |
| Waning Gibbous | 17-21 | Release phase |
| Last Quarter | 21-24 | Reflection |
| Waning Crescent | 24-29 | Restful |

## Retrograde Sensitivity

| Planet | Retrograde Impact |
|--------|-------------------|
| Mercury | Communication issues (+5 sensitivity) |
| Venus | Relationship reflection (+3) |
| Mars | Action delays (+4) |
| Jupiter | Expansion pause (+2) |
| Saturn | Discipline review (+2) |

## Notes

- Uses Swiss Ephemeris (pyswisseph) for calculations
- All positions calculated for current UTC time
- Astrology contributes up to 25 points to sensitivity
- Premium users get detailed 12-month forecast
