# Mac Computer Use Cookbook: TL;DR Bot

**App:** telegram-tldr
**Type:** Telegram Bot (Group Chat Summarization)
**Status:** Development

---

## Purpose

This cookbook provides instructions for Anthropic Mac Computer Use to perform visual and manual testing of the TL;DR Telegram bot.

---

## Access Information

### Telegram Bot

| Item | Value |
|------|-------|
| Bot Username | Create via @BotFather (e.g., `tldr_test_bot`) |
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
- Bot name and short description
- List of available commands
- Free vs Pro summary limits

**Screenshot Reference:**
```
Expected format:
------------------------------------------
Welcome to TL;DR!

I summarize busy group chats into a 30-second read.

Commands:
/help - Show commands
/summary [hours] - Generate digest (admins)
/status - Usage and tier
/subscribe - Upgrade to Pro
------------------------------------------
```

### 2. Help Message (/help)

**Expected Elements:**
- Command list with short explanations
- Note that /summary requires admin in group chats

### 3. Summary Output (/summary [hours])

**Expected Elements:**
- Time window shown (default + custom hours)
- Bullet list or numbered summary
- If no messages: friendly empty state

**Example Output:**
```
------------------------------------------
TL;DR (last 6 hours)

1) Project update: payment flow finalized
2) Action item: push docs to repo
3) Decision: ship on Friday
------------------------------------------
```

### 4. Status Output (/status)

**Expected Elements:**
- Free vs Pro tier
- Usage counter (summaries this month)
- Reset date or note about monthly reset

### 5. Health Output (/health)

**Expected Elements:**
- Bot uptime or status message
- Dependencies status (Gemini, Redis)

---

## Payment Flows

### Subscription Tiers

| Tier | Price (Stars) | Features |
|------|---------------|----------|
| Free | 0 | 3 summaries/month |
| Pro | 250 (~$5) | Unlimited summaries |

### Testing Payments (Test Mode)

**Note:** Telegram Stars payments require production setup. Test in sandbox mode only.

1. **Initiate Subscription:**
   ```
   /subscribe
   ```

2. **Expected Response:**
   - Tier selection prompt
   - Price displayed in Telegram Stars
   - Payment button (Telegram Stars)

3. **Verify Payment Handler:**
   - Payment success message
   - Tier upgraded to Pro
   - `/status` shows Pro active

**IMPORTANT:** Do NOT complete real payments during testing. Cancel before confirmation.

---

## OAuth/Identity Setup

TL;DR does not require OAuth or external identity providers. User identity is based on Telegram user ID and chat ID.

---

## Test Scenarios

### Scenario 1: New User Flow

1. Open Telegram
2. Search for bot username
3. Send `/start`
4. Verify welcome message appears
5. Send `/help`
6. Verify command list

### Scenario 2: Group Admin Summary

1. Add bot to a test group chat
2. Ensure test user is group admin
3. Send several messages in group
4. Send `/summary 6`
5. Verify summary output includes recent messages

### Scenario 3: Non-Admin Summary Attempt

1. Use a non-admin user in a group
2. Send `/summary`
3. Verify bot responds with admin-only notice

### Scenario 4: Usage Limits

1. Trigger 3 summaries as free user
2. Send `/summary` again
3. Verify upgrade prompt and limit message

### Scenario 5: Payment Flow

1. Send `/subscribe`
2. Verify Telegram Stars payment UI appears
3. Cancel payment
4. Verify no tier change

---

## Expected States (Screenshots)

### State 1: Initial Bot Contact
- Empty chat with bot
- "START" button visible

### State 2: After /start
- Welcome message displayed
- Command list visible

### State 3: Summary Output
- TL;DR header with time window
- Bullet list of key points

### State 4: Usage Limit Reached
- Limit warning displayed
- Upgrade CTA (/subscribe)

### State 5: Payment Prompt
- Tier comparison displayed
- Price in Telegram Stars
- Payment button visible

---

## Verification Checklist

- [ ] Bot responds to /start command
- [ ] /help shows command reference
- [ ] /summary works for group admins
- [ ] /summary is blocked for non-admins
- [ ] /status shows tier and usage
- [ ] /subscribe shows payment prompt
- [ ] Usage limit triggers upgrade prompt
- [ ] /health shows bot status

---

## Known Issues

1. **Bot Token:** Pending creation via @BotFather
2. **Gemini API Key:** Required for summary generation
3. **Webhook URL:** Required for production mode

---

## Contact

For testing issues, escalate to development team.

---

*Cookbook for TL;DR - Telegram group chat summarization bot*
