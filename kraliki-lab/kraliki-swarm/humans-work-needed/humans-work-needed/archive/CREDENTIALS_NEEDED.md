# Credentials Required for Human Ops

**DO NOT commit actual credentials to this repo. This file lists what's needed.**

## Accounts Needed

| Service | Account Email | Status | Notes |
|---------|--------------|--------|-------|
| Telegram | Your phone number | Have it? | For @BotFather |
| Cal.com | hello@verduona.com | Create new | Free tier |
| Formspree | hello@verduona.com | Create new | Free tier |
| Cloudflare | ? | Have it? | verduona.com DNS |
| Stripe | ? | Have it? | May need KYC |
| LinkedIn | Personal account | Have it? | For posting |
| Google Cloud | ? | Have it? | Needs billing |

## SSH Access Needed

| Server | IP | User | Auth Method |
|--------|-----|------|-------------|
| Dev Server | 5.9.38.218 | adminmatej | SSH key (have) |
| Prod Server | 5.75.129.12 | adminmatej | SSH key or password |
| Storage Box | u496928.your-storagebox.de:23 | u496928 | Password (in task file) |

## During Task Execution

The Mac agent will prompt you when it needs:
- Login to a service
- 2FA code from your phone
- CAPTCHA solving
- Email verification link clicking

## Security Notes

1. Agent sees your screen - close sensitive tabs
2. Don't leave credentials in clipboard
3. Review agent actions before confirming
4. Can pause/stop agent at any time
