# Mac Computer Use Testing Guide

**Purpose:** Automated browser testing of production apps using Claude Desktop Computer Use on Mac.

## Prerequisites

1. Claude Desktop with Computer Use enabled
2. SSH access to dev server (5.9.38.218)
3. Browser (Safari/Chrome) with access to beta URLs

## Beta App URLs to Test

| App | URL | Key Flows |
|-----|-----|-----------|
| Speak by Kraliki | https://speak.verduona.dev | Login → Voice recording → Transcript → Submit |
| Voice by Kraliki | https://voice.verduona.dev | Login → Create campaign → Voice call → Analytics |
| Focus by Kraliki | https://focus.verduona.dev | Login → Create task → Timer → Complete |
| Learn by Kraliki | https://learn.verduona.dev | Login → Browse courses → Enroll |

## Test Scenarios

### 1. Speak by Kraliki

```
TEST: Employee Feedback Flow
1. Open https://speak.verduona.dev
2. Navigate to login or use magic link
3. Grant microphone permission when prompted
4. Click "Start Recording" or voice button
5. Speak: "I think our team communication could be improved"
6. Wait for transcription
7. Review transcript
8. Click Submit/Send
9. Verify confirmation message

EXPECTED:
- Transcription appears within 5 seconds
- Submit completes without error
- Confirmation shown
```

### 2. Voice by Kraliki Voice Call

```
TEST: AI Voice Call
1. Open https://voice.verduona.dev
2. Login with test account
3. Navigate to Campaigns
4. Click "New Campaign" or similar
5. Fill campaign details
6. Click "Start Call" or voice button
7. Wait for Gemini connection
8. Have brief conversation
9. End call
10. Check call analytics

EXPECTED:
- Voice connects within 3 seconds
- AI responds appropriately
- Analytics show call duration
```

### 3. Focus by Kraliki Task Flow

```
TEST: Task Creation and Timer
1. Open https://focus.verduona.dev
2. Login or create account
3. Click "New Task"
4. Enter task: "Test the app for 5 minutes"
5. Set timer to 5 minutes
6. Start timer
7. Complete task
8. Verify task shows as completed

EXPECTED:
- Timer counts down correctly
- Task marked complete
- History updated
```

## Human-Only Actions (Cannot Automate)

These require manual action in BotFather, Stripe, etc:

### Telegram Payments (HW-023)
1. Open Telegram → @BotFather
2. `/mybots` → Select @sumarium_bot
3. Payments → Telegram Stars → Enable
4. Repeat for @senseit_ai_bot

### Stripe Setup (HW-025)
1. Login to stripe.com/dashboard
2. Create Payment Links for:
   - Focus by Kraliki Pro: €9/month
   - Lab by Kraliki Demo: Free (lead capture)
3. Copy link URLs to .env files

### DNS Records (HW-017)
1. Login to Cloudflare
2. Add A records:
   - voice.kraliki.com → 5.9.38.218
   - speak.kraliki.com → 5.9.38.218
   - focus.kraliki.com → 5.9.38.218
   - learn.kraliki.com → 5.9.38.218
   - lab.kraliki.com → 5.9.38.218

## Verification Checklist

After Computer Use testing, verify:

- [ ] Speak by Kraliki voice recording works
- [ ] Speak by Kraliki transcription accurate
- [ ] Voice by Kraliki call connects
- [ ] Voice by Kraliki AI responds
- [ ] Focus by Kraliki timer works
- [ ] Focus by Kraliki tasks persist
- [ ] Speak by Kraliki feedback flow works
- [ ] Learn by Kraliki onboarding flows load
- [ ] All apps mobile responsive
- [ ] No console errors (check DevTools)

## Reporting Issues

After testing, create issues in Linear or update features.json:

```bash
# SSH to dev server
ssh adminmatej@5.9.38.218

# Add bug to features.json
cd /home/adminmatej/github/ai-automation/software-dev/planning
# Edit features.json with new bug fix feature
```

## Quick SSH Commands

```bash
# Connect to dev server
ssh adminmatej@5.9.38.218

# Check app logs
pm2 logs

# Check health
curl http://127.0.0.1:8099/health

# View features status
cat /home/adminmatej/github/ai-automation/software-dev/planning/features.json | jq '.features[] | select(.passes != true)'
```

---

*Created: 2025-12-21*
*For: Mac Claude Desktop Computer Use*
