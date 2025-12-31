# Mac Computer Use Cookbook: Sense by Kraliki (SenseIt Bot)

**App:** sense-kraliki
**Type:** Telegram Bot (Astrology/Sensitivity Tracking)
**Status:** Development

---

## Purpose

This cookbook provides instructions for Anthropic Mac Computer Use to perform visual and manual testing of the Sense by Kraliki (SenseIt) Telegram bot.

---

## Access Information

### Telegram Bot

| Item | Value |
|------|-------|
| Bot Username | `@SenseItBot` (pending setup) |
| Bot Type | Telegram Bot (polling mode) |
| Access Method | Search in Telegram app |
| Test Account | Use personal Telegram account |

### Bot Status

- [ ] Bot token created via @BotFather
- [ ] Bot deployed and running
- [ ] Bot accessible in Telegram

---

## Visual Elements to Verify

### 1. Welcome Message (/start)

**Expected Elements:**
- Bot name and description
- List of available commands
- Subscription tier info (Free/Sensitive/Empath)

**Screenshot Reference:**
```
Expected format:
------------------------------------------
Welcome to Sense by Kraliki!

Your cosmic sensitivity companion for highly sensitive people.

Available commands:
/sense - Current sensitivity score
/dream - Dream interpretation (Jungian)
/bio - Your biorhythm chart
/astro - Astrological influences
/remedies - Holistic recommendations
...
------------------------------------------
```

### 2. Sensitivity Report (/sense)

**Expected Elements:**
- Sensitivity score (0-100)
- Level indicator (Low/Moderate/Elevated/High/Extreme)
- Color emoji indicator
- Contributing factors with bar charts
- Alerts (if any active)
- Recommendations

**Example Output:**
```
Expected format:
------------------------------------------
[GREEN/YELLOW/ORANGE/RED/WARNING EMOJI] Sensitivity Level: MODERATE (35/100)

Contributing Factors:
  Geomagnetic: [BAR] 8/30
  Solar: [BAR] 0/20
  Seismic: [BAR] 0/10
  Schumann: [BAR] 10/20
  Weather: [BAR] 5/15
  Astrology: [BAR] 12/25
  Biorhythm: [BAR] 0/20

Alerts:
  * Mercury retrograde active

Recommendations:
  * Conditions favorable - good day for productivity
------------------------------------------
```

### 3. Dream Analysis (/dream [text])

**Expected Elements:**
- Jungian interpretation
- Archetypal symbols identified
- Shadow aspects
- Personal growth message
- Correlation with current cosmic conditions

**Test Input:**
```
/dream I was flying over mountains and saw a golden city below
```

### 4. Biorhythm Chart (/bio)

**Expected Elements:**
- Physical, Emotional, Intellectual, Intuitive values (-100 to +100)
- Phase labels (high/rising/falling/low/critical)
- Overall interpretation
- Critical day warnings (if applicable)

**Prerequisites:**
- Must run `/setbirthday YYYY-MM-DD` first

### 5. Astrology Report (/astro)

**Expected Elements:**
- Current moon phase
- Mercury retrograde status
- Major planetary aspects
- Sensitivity implications

---

## Payment Flows

### Subscription Tiers

| Tier | Price (Stars) | Features |
|------|---------------|----------|
| Free | 0 | Basic /sense, 3 dreams/month |
| Sensitive | 150 (~$3) | Unlimited dreams, /forecast |
| Empath | 350 (~$7) | All features, priority support |

### Testing Payments (Test Mode)

**Note:** Telegram Stars payments require production setup. Test in sandbox mode only.

1. **Initiate Subscription:**
   ```
   /subscribe
   ```

2. **Expected Response:**
   - Tier selection menu
   - Price displayed in Telegram Stars
   - Payment button (Telegram Stars)

3. **Verify Payment Handler:**
   - Payment success message
   - Feature unlock confirmation
   - `/status` shows subscription active

**IMPORTANT:** Do NOT complete real payments during testing. Cancel before confirmation.

---

## OAuth/Identity Setup

Sense by Kraliki (SenseIt) does not require OAuth or external identity providers. User identity is based on Telegram user ID.

---

## Test Scenarios

### Scenario 1: New User Flow

1. Open Telegram
2. Search for bot username
3. Send `/start`
4. Verify welcome message appears
5. Send `/sense`
6. Verify sensitivity report displays

### Scenario 2: Personalized Experience

1. Send `/setbirthday 1990-06-15`
2. Send `/bio`
3. Verify biorhythm chart includes all four cycles
4. Send `/setlocation 50.0755, 14.4378`
5. Send `/sense`
6. Verify weather data is now included in report

### Scenario 3: Dream Analysis (Requires Gemini API)

1. Send `/dream I was swimming in a deep ocean and found a treasure chest`
2. Verify Jungian interpretation is returned
3. Check for archetypal symbols (water, depth, treasure)
4. Verify no API errors

### Scenario 4: Premium Feature Access

1. Send `/forecast` (premium feature)
2. Verify appropriate message (upgrade prompt or forecast)
3. Send `/status`
4. Verify subscription status display

---

## Expected States (Screenshots)

### State 1: Initial Bot Contact
- Empty chat with bot
- "START" button visible

### State 2: After /start
- Welcome message displayed
- Command list visible

### State 3: After /sense
- Sensitivity report with score
- Emoji color indicator matching level
- Factor breakdown visible

### State 4: After /bio
- Biorhythm values displayed
- Phase labels for each cycle
- Interpretation text

### State 5: Subscription Prompt
- Tier comparison displayed
- Price in Telegram Stars
- Selection buttons

---

## Verification Checklist

- [ ] Bot responds to /start command
- [ ] /sense returns valid score (0-100)
- [ ] /bio works after setting birthday
- [ ] /astro shows current moon phase
- [ ] /dream returns AI interpretation (when API key configured)
- [ ] /remedies provides recommendations
- [ ] /health shows bot status
- [ ] Location setting affects weather data in /sense
- [ ] Error messages are user-friendly

---

## Known Issues

1. **Bot Token:** Pending creation via @BotFather (blocker: HW-001)
2. **Schumann Data:** May be unavailable if geocenter.info is down
3. **Dream Limits:** Free tier limited to 3 dreams/month

---

## Contact

For testing issues, escalate to development team.

---

*Cookbook for Sense by Kraliki (SenseIt) - Telegram sensitivity tracking bot*
