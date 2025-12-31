# HW-009: Configure SSH Key for Hetzner Storage Box

**Created:** 2025-12-13
**Priority:** MEDIUM
**Status:** Pending
**Blocks:** Remote PostgreSQL backup upload

## Context

PostgreSQL backup script is working (local backups created successfully), but SSH key access to Hetzner Storage Box needs to be reconfigured. The key was working in October 2025 but is no longer valid.

## Action Required

Run this command to add your SSH key to the Storage Box:

```bash
cat ~/.ssh/id_ed25519.pub | ssh -p 23 u496928@u496928.your-storagebox.de install-ssh-key
```

You'll be prompted for the Storage Box password (stored in password manager):
- **Password:** `gdjak172981389LLLAHdas796982394dalUUHKD!`

## Verification

After adding the key, verify with:

```bash
ssh -p 23 u496928@u496928.your-storagebox.de "ls -la backups/"
```

Should list contents without password prompt.

## Impact

- **Without fix:** PostgreSQL backups stored locally only (~7 days retention)
- **With fix:** Backups uploaded to Storage Box (additional offsite protection)

## Related

- PostgreSQL backup script: `/home/adminmatej/bin/pg-backup.sh`
- Local backup location: `/home/adminmatej/backups/postgres/`
- Timer: `systemctl --user status pg-backup.timer`
