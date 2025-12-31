# CC-Lite Backup & Recovery Guide

**Version:** 1.0.0
**Last Updated:** December 26, 2025
**Status:** Production Ready

## Overview

CC-Lite uses a comprehensive backup strategy covering all persistent data stores:
- **PostgreSQL** - Primary application database
- **Redis** - Session cache and real-time data
- **Qdrant** - Vector database for knowledge base search

## Quick Start

### Manual Backup
```bash
# Run a full backup now
./scripts/backup-production.sh

# Verify backups
./scripts/verify-backups.sh
```

### Setup Automated Backups
```bash
# Install cron jobs
./scripts/backup-cron.sh install

# Check status
./scripts/backup-cron.sh status
```

### Restore from Backup
```bash
# List available backups
./scripts/restore-db.sh --list

# Restore all databases from latest
./scripts/restore-db.sh --all

# Restore specific database
./scripts/restore-db.sh --postgres postgres_backup_20251226_020000.sql.gz
```

## Backup Schedule

| Schedule | Time | Action |
|----------|------|--------|
| Daily | 02:00 AM | Full production backup (PostgreSQL, Redis, Qdrant) |
| Daily | 06:00 AM | Backup integrity verification |
| Weekly | Sunday 03:00 AM | Extended verification with alerts |

## Backup Locations

```
backups/
├── postgresql/           # PostgreSQL SQL dumps
│   ├── postgres_backup_YYYYMMDD_HHMMSS.sql.gz
│   └── latest.sql.gz -> (symlink to latest)
├── redis/                # Redis RDB snapshots
│   ├── redis_backup_YYYYMMDD_HHMMSS.rdb.gz
│   └── latest.rdb.gz -> (symlink to latest)
├── qdrant/               # Qdrant storage snapshots
│   ├── qdrant_backup_YYYYMMDD_HHMMSS.tar.gz
│   └── latest.tar.gz -> (symlink to latest)
└── logs/                 # Backup operation logs
    ├── backup_YYYYMMDD_HHMMSS.log
    └── cron.log
```

## Retention Policy

- **Local backups:** 30 days (configurable via `RETENTION_DAYS` environment variable)
- **S3 backups:** 30 days (if configured)
- **Log files:** 30 days

## S3 Cloud Backup (Optional)

To enable cloud backup to AWS S3, set these environment variables:

```bash
export AWS_S3_BUCKET="your-bucket-name"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

Backups will be uploaded to:
- `s3://{bucket}/cc-lite/backups/postgresql/`
- `s3://{bucket}/cc-lite/backups/redis/`
- `s3://{bucket}/cc-lite/backups/qdrant/`

## Scripts Reference

### backup-production.sh

Full production backup script. Backs up all three databases.

```bash
# Options via environment variables:
BACKUP_DIR=/path/to/backups    # Override backup directory
RETENTION_DAYS=30              # Days to keep backups
REDIS_PASSWORD=xxx             # Redis authentication
QDRANT_PORT=6337               # Qdrant API port
BACKUP_WEBHOOK_URL=xxx         # Slack/webhook notification URL
```

### restore-db.sh

Multi-database restore script with safety prompts.

```bash
# Options:
-p, --postgres <file>    # Restore PostgreSQL
-r, --redis <file>       # Restore Redis
-q, --qdrant <file>      # Restore Qdrant
-a, --all                # Restore all from latest
-l, --list               # List available backups
-h, --help               # Show help
```

### verify-backups.sh

Backup integrity checker. Validates:
- Backup file existence
- File age (warns if > 25 hours old)
- File size (warns if suspiciously small)
- Gzip integrity

```bash
# Options via environment variables:
MAX_AGE_HOURS=25    # Alert threshold for backup age
```

### backup-cron.sh

Cron job management utility.

```bash
./scripts/backup-cron.sh install     # Setup cron jobs
./scripts/backup-cron.sh uninstall   # Remove cron jobs
./scripts/backup-cron.sh status      # Show current jobs
./scripts/backup-cron.sh test        # Run test backup
```

## Disaster Recovery Procedures

### Scenario 1: Complete Data Loss

1. Ensure containers are running:
   ```bash
   docker compose up -d
   ```

2. Restore from latest backups:
   ```bash
   ./scripts/restore-db.sh --all
   ```

3. Verify restoration:
   ```bash
   # Test API health
   curl http://localhost:8000/health

   # Check database connectivity
   docker exec cc-lite-postgres psql -U postgres -d operator_demo -c "SELECT COUNT(*) FROM users;"
   ```

### Scenario 2: PostgreSQL Corruption

1. Stop the backend:
   ```bash
   docker compose stop backend
   ```

2. Restore PostgreSQL:
   ```bash
   ./scripts/restore-db.sh --postgres latest.sql.gz
   ```

3. Restart services:
   ```bash
   docker compose start backend
   ```

### Scenario 3: Point-in-Time Recovery

1. List available backups:
   ```bash
   ./scripts/restore-db.sh --list
   ```

2. Choose a backup from before the incident:
   ```bash
   ./scripts/restore-db.sh --postgres postgres_backup_20251225_020000.sql.gz
   ```

## Monitoring & Alerts

### Webhook Notifications

Set `BACKUP_WEBHOOK_URL` to receive Slack/webhook notifications:

```bash
export BACKUP_WEBHOOK_URL="https://hooks.slack.com/services/xxx"
```

Notifications include:
- Backup completion status
- Individual database backup status
- File sizes
- Any errors or warnings

### Log Monitoring

```bash
# Watch backup logs
tail -f backups/logs/cron.log

# Check latest backup log
ls -lt backups/logs/backup_*.log | head -1 | xargs cat
```

### Health Checks

Run regular verification:
```bash
./scripts/verify-backups.sh
```

Expected output for healthy system:
```
All backups are healthy!
```

## Troubleshooting

### Backup Failed: Container Not Running

Check container status:
```bash
docker ps --filter "name=cc-lite"
```

Start missing containers:
```bash
docker compose up -d
```

### Backup Size is Zero

Check if database has data:
```bash
docker exec cc-lite-postgres psql -U postgres -d operator_demo -c "SELECT COUNT(*) FROM users;"
```

Check disk space:
```bash
df -h
```

### Redis BGSAVE Failed

Check Redis logs:
```bash
docker logs cc-lite-redis --tail 50
```

Ensure Redis has write permissions:
```bash
docker exec cc-lite-redis ls -la /data/
```

### Qdrant Backup Failed

Check Qdrant health:
```bash
curl http://localhost:6337/health
```

Check Qdrant logs:
```bash
docker logs cc-lite-qdrant --tail 50
```

## Security Considerations

1. **Backup Encryption**: Consider encrypting backups before S3 upload
2. **Access Control**: Restrict access to backup directory
3. **Credential Management**: Store passwords in environment variables, not scripts
4. **Network Security**: Backups run over Docker internal network

## Best Practices

1. **Test Restores Regularly**: Quarterly restore tests recommended
2. **Monitor Backup Size Trends**: Unexpected size changes may indicate issues
3. **Keep Off-Site Copies**: Enable S3 backup for disaster recovery
4. **Version Control Scripts**: Keep backup scripts in git
5. **Document Changes**: Update this guide when modifying backup procedures
