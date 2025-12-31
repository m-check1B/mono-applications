# HW-026: Setup Jules API for GIN Integration

**Created:** 2025-12-21
**Priority:** HIGH
**Estimated Time:** 15 minutes
**Feature:** W4-017

## Purpose

Enable Jules (Google's async AI coding agent) for parallel work dispatch from GIN. This allows up to 100+ tasks/day to be processed in parallel.

## Steps

### 1. Get Jules API Key

1. Go to https://jules.google.com
2. Sign in with Google account
3. Navigate to **Settings** → **API** (or https://jules.google.com/settings#api)
4. Generate new API key
5. Save to: `/home/adminmatej/github/secrets/jules_api_key.txt`
   ```bash
   echo "YOUR_API_KEY_HERE" > /home/adminmatej/github/secrets/jules_api_key.txt
   chmod 600 /home/adminmatej/github/secrets/jules_api_key.txt
   ```

### 2. Install Jules GitHub App

1. Go to https://github.com/apps/jules-by-google
2. Click **Install**
3. Select the **verduona-digital** organization (or personal repos)
4. Choose **All repositories** or select specific ones:
   - telegram-tldr
   - senseit
   - focus-lite
   - magic-box
   - cc-lite-2026
   - voice-of-people

### 3. Check Subscription Tier

Jules limits by tier:
| Tier | Daily Tasks | Concurrent |
|------|-------------|------------|
| Free | 15 | 3 |
| Pro | 75 | 15 |
| Ultra | 300 | 60 |

Note current tier for rate limiting config.

### 4. Verify Integration

```bash
cd /home/adminmatej/github/ai-automation/gin

# Check quota
python3 jules_integration.py quota

# List connected repos
python3 jules_integration.py sources

# Test dispatch
python3 jules_integration.py test
```

## Expected Output

```
Jules Quota Status:
  Tier: pro
  Daily limit: 75
  Used today: 0
  Remaining: 75
  Reset: 2025-12-22T00:00:00Z

Connected Sources: 6 repositories
  - verduona-digital/telegram-tldr
  - verduona-digital/senseit
  ...
```

## Completion Criteria

- [ ] API key saved to `/github/secrets/jules_api_key.txt`
- [ ] GitHub app installed on repos
- [ ] `python3 jules_integration.py quota` returns valid response
- [ ] `python3 jules_integration.py sources` shows repos

## When Done

Mark this file as complete by moving to archive:
```bash
mv /github/ai-automation/humans-work-needed/HW-026_setup_jules_api.md \
   /github/ai-automation/humans-work-needed/archive/
```

Then update features.json W4-017 if not auto-detected.
