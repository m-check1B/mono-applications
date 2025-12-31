# Action Required: Rotate Exposed Credentials

**Priority:** CRITICAL
**Due:** Immediately
**Context:** The audit of `telegram-tldr` revealed that real credentials were committed to the `.env` file.

## Required Actions

1.  **Telegram Bot Token:**
    - Go to @BotFather
    - Select the bot (@sumarium_bot)
    - Revoke the old token
    - Generate a new token
    - Save it to `/secrets/telegram_tldr_bot.txt` (or update existing)

2.  **Gemini API Key:**
    - Go to Google AI Studio
    - Revoke the key ending in `...[REDACTED]` (check the .env file if needed to identify)
    - Generate a new key
    - Save it to `/secrets/gemini_api_key.txt`

3.  **Update Secrets:**
    - Ensure `/secrets/` directory contains the new values.
    - Delete the `.env` file in `/github/applications/telegram-tldr/` or replace values with placeholders.

4.  **Confirm:**
    - Move this file to `done/` folder when complete.
