# HW-014: Gemini API Quota Increase for Live API

**Created:** 2025-12-20
**Priority:** HIGH
**Blocking:** VOICE-001, VOICE-003

## Issue

The Gemini API key used for Live API calls has exceeded quota.

**Error from WebSocket test:**
```
You exceeded your current quota, please check your plan and billing details.
```

## What Works

- GeminiLiveProvider code is complete and correct
- WebSocket connection to `wss://generativelanguage.googleapis.com/ws/...` succeeds
- Setup message sends correctly
- The API key can access `gemini-2.0-flash-exp` (supports `bidiGenerateContent`)

## What's Needed

1. Go to https://aistudio.google.com/
2. Check API key quota and billing
3. Either:
   - Enable billing on the Google Cloud project
   - Increase quota limits
   - Create a new API key with higher quota

## Verification

After resolving, run:
```bash
cd /home/adminmatej/github/applications/cc-lite-2026/backend
source .venv/bin/activate
python3 /tmp/test_gemini_live.py
```

Should output:
```
OK WebSocket connected!
OK Setup message sent
OK Response received
OK Session setup complete!
OK Text message sent
OK AI response
```

## Update Required

If the key changed, update local secrets (do not commit):
1. `/home/adminmatej/github/applications/cc-lite-2026/.env`
2. `/home/adminmatej/github/applications/telegram-tldr/.env`

---

**Status:** PENDING
