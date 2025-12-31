# Test 010: Admin Statistics

**Feature:** /stats command - usage analytics dashboard
**Priority:** P2 (Nice-to-have)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify the admin statistics command shows accurate usage metrics and is restricted to admin users only.

## Preconditions

- Bot is running
- Redis storage is available for analytics
- Admin user IDs configured in ADMIN_USER_IDS

## Test Steps

### Test 10.1: Non-Admin Access Denied

1. As regular user, send `/stats`
2. **Expected:** Access denied message:
   - "This command is only available to administrators."

### Test 10.2: Admin Access Granted

1. As admin user (ID in ADMIN_USER_IDS), send `/stats`
2. **Expected:** Full analytics dashboard displayed

### Test 10.3: Active Users Section

1. Send `/stats` as admin
2. **Expected:** Users section:
   - Daily active users count
   - Weekly active users count
   - Monthly active users count
   - Total users count

### Test 10.4: Charts Generated Section

1. Send `/stats`
2. **Expected:** Charts section showing:
   - sense: today / total
   - dream: today / total
   - bio: today / total
   - astro: today / total
   - remedies: today / total
   - forecast: today / total

### Test 10.5: Top Commands Section

1. Send `/stats`
2. **Expected:** Top 10 commands:
   - Command name
   - Today's count
   - Total count
   - Sorted by total usage

### Test 10.6: Errors Section

1. Send `/stats`
2. **Expected:** Error tracking:
   - Total error count
   - Recent error types (if available)

### Test 10.7: Timestamp

1. Send `/stats`
2. **Expected:** Generation timestamp shown
   - Format: "Generated: YYYY-MM-DD HH:MM:SS"

### Test 10.8: Stats After Activity

1. Perform various bot actions:
   - `/sense` x2
   - `/dream test` x1
   - `/bio` x1
2. Send `/stats`
3. **Expected:** Counts reflect recent activity

### Test 10.9: Stats Format

Verify readable format:

```
Sense by Kraliki Analytics
Generated: 2025-12-25 12:00:00

Active Users
- Daily: 15
- Weekly: 45
- Monthly: 120
- Total: 250

Charts Generated (Today / Total)
- sense: 25 / 1500
- dream: 10 / 450
- bio: 5 / 200
...

Top Commands (Today / Total)
- /sense: 25 / 1500
- /start: 20 / 800
- /help: 15 / 600
...

Errors
- Total: 12
```

### Test 10.10: Error Handling

1. If analytics storage unavailable
2. **Expected:** Error message (not crash)
   - "Error retrieving stats: [details]"

## Success Criteria

- [ ] Non-admins cannot access /stats
- [ ] Admins see full analytics dashboard
- [ ] Active users counts displayed
- [ ] Chart generation counts by type
- [ ] Top commands with usage counts
- [ ] Error tracking visible
- [ ] Timestamp shows generation time
- [ ] Counts update after activity
- [ ] Graceful error handling

## Analytics Tracked

### User Metrics

| Metric | Description |
|--------|-------------|
| Daily Active | Unique users in last 24h |
| Weekly Active | Unique users in last 7 days |
| Monthly Active | Unique users in last 30 days |
| Total | All-time unique users |

### Command Tracking

All commands are tracked:
- /start, /help, /sense, /dream
- /bio, /astro, /remedies, /forecast
- /setbirthday, /setlocation
- /subscribe, /status, /audit
- /health, /stats

### Chart Types

Charts generated for:
- sense: Sensitivity scores
- dream: Dream analyses
- bio: Biorhythm charts
- astro: Astrology reports
- remedies: Remedy plans
- forecast: 12-month forecasts

### Error Tracking

Errors tracked by:
- Type (sensitivity_calculation, dream_analysis, etc.)
- Source command
- Timestamp

## Configuration

```bash
# In .env
ADMIN_USER_IDS=123456,789012  # Comma-separated Telegram user IDs
```

## Notes

- Analytics stored in Redis with daily/weekly/monthly buckets
- Stats are cached briefly for performance
- Error details help with debugging
- Used for business metrics and capacity planning
- Premium: Subscription analytics for revenue tracking
