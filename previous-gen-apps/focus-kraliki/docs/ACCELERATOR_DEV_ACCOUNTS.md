# Accelerator Developer Accounts

Created: 2025-12-28 for Monday accelerator onboarding

## Account Credentials

| Email | Name | Password | User ID | Role |
|-------|------|----------|---------|------|
| dev1@accelerator.kraliki.dev | Accelerator Dev 1 | AccelDev2025x1 | NIQ1mj5uXSrso5tqOBdQCQ | AGENT* |
| dev2@accelerator.kraliki.dev | Accelerator Dev 2 | AccelDev2025x2 | d0dMRv4Q02yfbh5CIORzWA | AGENT* |
| dev3@accelerator.kraliki.dev | Accelerator Dev 3 | AccelDev2025x3 | QES7t3FLFbZqjvhjmVK_zA | AGENT* |

*Role needs to be upgraded to SUPERVISOR - see below.

## Role Upgrade Required

The accounts were created with default AGENT role. To enable Dev tier access:

```bash
# SSH to production and run psql
psql $DATABASE_URL -f scripts/upgrade-accelerator-roles.sql
```

Or directly:
```sql
UPDATE users
SET role = 'SUPERVISOR'
WHERE email IN (
    'dev1@accelerator.kraliki.dev',
    'dev2@accelerator.kraliki.dev',
    'dev3@accelerator.kraliki.dev'
);
```

## Role Tiers

| Role | Tier | Access |
|------|------|--------|
| AGENT | User | App docs only, basic features |
| SUPERVISOR | Dev | Technical docs, CLAUDE.md, advanced features |
| ADMIN | Admin | Full ecosystem docs, system config |

## Login URL

https://focus.verduona.dev/login

## Notes

- Passwords should be changed on first login
- Accounts can be personalized later with real names/emails
- Use `/help` in Focus to access tiered documentation (once implemented)
