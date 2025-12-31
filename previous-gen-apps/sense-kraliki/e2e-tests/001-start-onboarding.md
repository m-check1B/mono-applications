# Test 001: Start Command and Onboarding Flow

**Feature:** /start command and guided user setup
**Priority:** P0 (Critical)
**Type:** Telegram Bot
**Estimated Time:** 5 minutes

## Objective

Verify that new users receive a proper welcome message and can complete the guided onboarding flow (birthdate + location setup).

## Preconditions

- Bot is running and accessible
- User has not interacted with bot before (or user data cleared)
- Telegram client available

## Test Steps

### Test 1.1: New User Welcome

1. Open Telegram and start a chat with @SenseItBot (Sense by Kraliki)
2. Send `/start`
3. **Expected:** Welcome message appears with:
   - "Welcome to Sense by Kraliki - Your Sensitivity Companion"
   - Explanation of what the bot does
   - Two inline buttons: "Setup Now (Recommended)" and "Skip"

### Test 1.2: Start Onboarding Flow

1. Click "Setup Now (Recommended)" button
2. **Expected:** Bot asks for birthdate in YYYY-MM-DD format
3. Send `1990-05-15`
4. **Expected:** Birthdate confirmed, now asks for location as LAT,LON
5. Send `50.0755, 14.4378` (Prague coordinates)
6. **Expected:** Setup complete message with:
   - Confirmation of both settings
   - Instructions to try /sense

### Test 1.3: Skip Onboarding

1. Start fresh (clear user data or use different account)
2. Send `/start`
3. Click "Skip" button
4. **Expected:** Skip confirmation with commands to set up later

### Test 1.4: Invalid Birthdate Format

1. Initiate onboarding
2. When asked for birthdate, send `invalid-date`
3. **Expected:** Error message asking for YYYY-MM-DD format

### Test 1.5: Invalid Location Format

1. Complete birthdate step
2. When asked for location, send `invalid`
3. **Expected:** Error message asking for LAT,LON format

### Test 1.6: Returning User Welcome

1. Complete onboarding fully
2. Send `/start` again
3. **Expected:** Different welcome message:
   - "Welcome back to Sense by Kraliki!"
   - No onboarding prompts
   - Just command suggestions

## Success Criteria

- [ ] New user sees welcome message with setup buttons
- [ ] Onboarding flow collects birthdate successfully
- [ ] Onboarding flow collects location successfully
- [ ] Invalid inputs show helpful error messages
- [ ] Returning users see different welcome message
- [ ] All inline buttons respond correctly

## Notes

- Location is optional; user can skip it
- Birthdate is required for /bio and /forecast commands
- Data persists in Redis storage
