# HW-027: Configure Darwin2 Telegram Notification Chat

## Priority: Low (nice-to-have monitoring)
## Effort: ~5 minutes
## Blocks: VD-205 (full activation only)

## What

Set up a Telegram chat/channel to receive Darwin2 agent completion notifications.

## Why

Darwin2 agents can now send notifications when they complete high-value tasks (+100pts).
This provides real-time visibility into autonomous agent activity.

## Options

**Option A: Personal Chat (Quickest)**
1. Message @sumarium_bot (TL;DR Bot) with `/start`
2. Run this to get your chat ID:
   ```bash
   curl "https://api.telegram.org/bot8556386028:AAGzb1iCyuNGzzMxOvW3Dnwyr5w1obz_KvI/getUpdates" | jq '.result[-1].message.chat.id'
   ```
3. Add to `/github/secrets/darwin2_telegram.env`:
   ```
   DARWIN2_TELEGRAM_CHAT_ID=YOUR_CHAT_ID
   ```

**Option B: Channel (Better for team)**
1. Create Telegram channel `#darwin2-alerts`
2. Add @sumarium_bot as admin
3. Get channel ID (starts with -100)
4. Add to darwin2_telegram.env

## Files to Update

- `/github/secrets/darwin2_telegram.env` - Set DARWIN2_TELEGRAM_CHAT_ID

## Test

```bash
cd /github/ai-automation/darwin2
python3 integrations/telegram_notify.py test
```

## Note

The integration is fully built and hooked into Darwin2's game engine.
Without the chat ID, notifications are silently skipped (no errors).
