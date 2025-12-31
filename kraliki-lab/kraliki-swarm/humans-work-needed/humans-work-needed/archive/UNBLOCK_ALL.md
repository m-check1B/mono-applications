# UNBLOCK ALL - Human Tasks Checklist

**Created:** 2025-12-14
**Updated:** 2025-12-20
**Total Tasks:** 10 (HW-011 Redis done ✓)

Do all of these in one session. Estimate: ~45-60 minutes.

---

## PRIORITY HIGH (Do First)

### HW-010: Gemini API Key (CRITICAL)
**Time:** 5 min | **Blocks:** VOICE-001, VOICE-004 (all voice features)

The current Gemini API key has permission issues. Need to regenerate:

1. Go to https://aistudio.google.com/
2. Generate a new API key with Gemini API access
3. Update `/home/adminmatej/github/applications/cc-lite-2026/.env`:
   ```
   GEMINI_API_KEY=<new_key_here>
   ```

**Verify:**
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY" 2>/dev/null | head -20
```

**Result:**
```
New API Key: ________________________________________________
```

---

### HW-001: SenseIt Telegram Bot Token
**Time:** 2 min | **Blocks:** W2-002

1. Open Telegram, message `@BotFather`
2. Send `/newbot`
3. Name: `SenseIt` | Username: `senseit_bot` (or similar)
4. Copy the token

**Result:**
```
Token: ________________________________________________
```

---

### HW-006: DNS Records for verduona.com
**Time:** 10 min | **Blocks:** MB-001, all websites

In Cloudflare (or your DNS provider), add these A records pointing to `5.9.38.218`:

| Done | Name | Value |
|------|------|-------|
| [ ] | @ | 5.9.38.218 |
| [ ] | www | 5.9.38.218 |
| [ ] | business | 5.9.38.218 |
| [ ] | family | 5.9.38.218 |
| [ ] | consulting | 5.9.38.218 |
| [ ] | company | 5.9.38.218 |
| [ ] | demos | 5.9.38.218 |
| [ ] | tldr | 5.9.38.218 |
| [ ] | magicbox | 5.9.38.218 |
| [ ] | inzenyring | 5.9.38.218 |
| [ ] | crm | 5.9.38.218 |

---

### HW-007: Stripe Payment Link for TL;DR Bot
**Time:** 10 min | **Blocks:** W2-006

1. Go to https://dashboard.stripe.com
2. **Products** > **Add product**
   - Name: `TL;DR Bot Pro`
   - Price: `$5.00 USD / month`
3. **Payment Links** > **New**
   - Select product
   - Collect email: Yes
   - After payment redirect: `https://t.me/sumarium_bot?start=paid`
4. Copy the link

**Result:**
```
Payment Link: https://buy.stripe.com/_________________________________
```

---

### HW-003: Production Server Check
**Time:** 5 min | **Blocks:** Website deployment

```bash
ssh adminmatej@5.75.129.12
```

Check what's running on production server OR decide:
- [ ] Use Vercel/Netlify instead
- [ ] Point DNS to dev server (5.9.38.218) - done in HW-006

**Result:**
```
Decision: ________________________________________________
```

---

## PRIORITY MEDIUM

### HW-002: Cal.com Account
**Time:** 10 min | **Blocks:** Booking integration

1. Sign up at https://cal.com (use hello@verduona.com)
2. Create event: "Discovery Call" (15 or 30 min)
3. Get embed code from event settings > Embed

**Result:**
```
Username: ________________________________________________
Event slug: ________________________________________________
```

---

### HW-004: EspoCRM Web-to-Lead
**Time:** 10 min | **Blocks:** Lead capture

1. Access CRM: http://localhost:8080 (VS Code port forward)
2. Login (creds in `/github/secrets/espocrm_creds.txt`)
3. Administration > Lead Capture > Create form
4. Get endpoint URL

**Result:**
```
Endpoint: ________________________________________________
```

---

### HW-005: Form Backend (Formspree)
**Time:** 5 min | **Blocks:** Contact forms

1. Sign up at https://formspree.io/
2. Create a form
3. Get endpoint (e.g., `https://formspree.io/f/xyzabc123`)

**Result:**
```
Formspree endpoint: ________________________________________________
```

---

### HW-008: LinkedIn Post
**Time:** 5 min | **Blocks:** W2-007

Post this to LinkedIn:

```
500+ Telegram messages waiting for you after a meeting.

We've all been there.

So I built @sumarium_bot - a Telegram bot that summarizes your group chats with AI.

How it works:
1. Add the bot to your group
2. Type /summary when you need to catch up
3. Get the key points in seconds, not hours

Free tier: 3 summaries/month
Pro: $5/mo or 250 Telegram Stars

Try it: t.me/sumarium_bot

#telegram #ai #productivity #buildinpublic
```

- [ ] Posted

---

### HW-009: Storage Box SSH Key
**Time:** 2 min | **Blocks:** Remote backups

Run:
```bash
cat ~/.ssh/id_ed25519.pub | ssh -p 23 u496928@u496928.your-storagebox.de install-ssh-key
```

Password: `gdjak172981389LLLAHdas796982394dalUUHKD!`

- [ ] Done

---

## OPTIONAL (Lower Priority)

### Zitadel Google Login
**Time:** 15 min | **Blocks:** Beta testing convenience

1. Google Cloud Console > Create OAuth credentials
2. Redirect URI: `https://identity.missionperfect.cloud/ui/login/login/externalidp/callback`
3. Add to Zitadel: Instance Settings > Identity Providers > Google

**Result:**
```
Client ID: ________________________________________________
```

---

## WHEN DONE

After completing all tasks, tell Claude:

> "All blockers done. Results:
> - Gemini API key: [new key]
> - SenseIt token: [token]
> - DNS: done
> - Stripe: [link]
> - Cal.com: [username/slug]
> - Formspree: [endpoint]
> - LinkedIn: posted
> - SSH key: done"

I'll update all the features.json entries and start the unblocked work.

---

## ✅ COMPLETED BLOCKERS

- [x] HW-011: Redis Setup (2025-12-20) - Running on 127.0.0.1:6380
