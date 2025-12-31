# Test 004: Biorhythm Chart

**Feature:** /bio command - personal biorhythm cycles
**Priority:** P1 (Important)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify the biorhythm feature correctly calculates and displays the user's physical, emotional, intellectual, and intuitive cycles.

## Preconditions

- Bot is running
- User has set birthdate via /setbirthday

## Test Steps

### Test 4.1: Basic Biorhythm Command

1. Ensure birthdate is set: `/setbirthday 1990-05-15`
2. Send `/bio`
3. **Expected:** Biorhythm report with:
   - Birth date displayed
   - Physical cycle (-100 to +100)
   - Emotional cycle (-100 to +100)
   - Intellectual cycle (-100 to +100)
   - Intuitive cycle (-100 to +100)
   - Overall score
   - Visual bars for each cycle

### Test 4.2: Visual Bar Display

Verify bar visualization:

```
Physical (+45):  [################     ]
Emotional (-23): [########             ]
Intellectual (+78): [##################   ]
Intuitive (+12): [###########          ]
```

**Expected:**
- Bar position reflects cycle value
- Negative values show bar on left side
- Positive values show bar on right side

### Test 4.3: Without Birthdate

1. Clear birthdate (or use new account)
2. Send `/bio`
3. **Expected:** Error message:
   - "I need your birth date to calculate biorhythm"
   - "Use /setbirthday YYYY-MM-DD to set it"

### Test 4.4: Critical Day Detection

1. Use a birthdate that results in critical day (cycle crossing zero)
2. Send `/bio`
3. **Expected:** Warning about critical cycles
   - "Critical cycles: Physical, Emotional" (example)
   - Recommendation for caution

### Test 4.5: Interpretation Text

1. Send `/bio`
2. **Expected:** Interpretation based on cycles:
   - Low physical: Rest recommended
   - Low emotional: Self-care focus
   - Low intellectual: Avoid complex tasks
   - High cycles: Good day for activities

### Test 4.6: Cycle Periods

Verify correct cycle calculations:

| Cycle | Period | Description |
|-------|--------|-------------|
| Physical | 23 days | Energy, strength |
| Emotional | 28 days | Mood, feelings |
| Intellectual | 33 days | Mental acuity |
| Intuitive | 38 days | Gut feelings |

### Test 4.7: Different Birthdates

Test with various birthdates to ensure calculations work:

1. `/setbirthday 1985-01-01` - 40 years ago
2. `/bio` - Should calculate correctly
3. `/setbirthday 2000-12-31` - Recent
4. `/bio` - Should calculate correctly

### Test 4.8: Biorhythm in Sensitivity Score

1. Send `/sense`
2. Check biorhythm factor in breakdown
3. **Expected:** Biorhythm contributes 0-20 points to total
4. Low biorhythm cycles increase sensitivity

## Success Criteria

- [ ] /bio displays all 4 cycles with values
- [ ] Visual bars render correctly
- [ ] Values are in -100 to +100 range
- [ ] Critical days are detected and warned
- [ ] Interpretation text is contextual
- [ ] Works with any valid birthdate
- [ ] Requires birthdate (prompts if missing)
- [ ] Biorhythm integrates with /sense

## Cycle Interpretation Guide

| Value Range | Meaning | Recommendation |
|-------------|---------|----------------|
| +70 to +100 | Peak | Excellent for activities |
| +30 to +69 | High | Good performance |
| -29 to +29 | Neutral | Normal day |
| -69 to -30 | Low | Take it easy |
| -100 to -70 | Trough | Rest, avoid strain |

## Critical Days

A critical day occurs when any cycle crosses the zero line (transitions between positive and negative). These days may bring:
- Physical: Accident proneness
- Emotional: Mood swings
- Intellectual: Poor judgment
- Intuitive: Uncertainty

## Notes

- Biorhythm is classic 23/28/33 day theory + 38 day intuitive
- Calculations are deterministic (same birthdate = same result)
- Contributes to overall sensitivity score
- Premium users get extended forecast in /forecast
