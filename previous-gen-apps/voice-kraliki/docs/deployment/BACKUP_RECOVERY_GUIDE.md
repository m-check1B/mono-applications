# Backup & Recovery Guide
## Operator Demo 2026 Production

This guide covers the complete backup and recovery procedures for the Operator Demo 2026 production environment.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Backup Strategy](#backup-strategy)
3. [Automated Backups](#automated-backups)
4. [Manual Backups](#manual-backups)
5. [Recovery Procedures](#recovery-procedures)
6. [Cloud Storage](#cloud-storage)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The backup system protects:

- **PostgreSQL Database**: Application data, user accounts, campaigns
- **Redis Cache**: Session data, temporary data
- **Configuration Files**: Environment settings, SSL certificates
- **Application Code**: Version-controlled deployments

### Backup Objectives

- **RTO (Recovery Time Objective)**: < 1 hour for critical services
- **RPO (Recovery Point Objective)**: < 15 minutes data loss
- **Availability**: 99.9% uptime with quick recovery
- **Security**: Encrypted backups with access controls

---

## 🗄️ Backup Strategy

### Backup Types

#### 1. Full Backups
- **Frequency**: Daily
- **Scope**: Complete database dumps
- **Retention**: 30 days
- **Storage**: Local + Cloud

#### 2. Incremental Backups
- **Frequency**: Hourly (WAL files)
- **Scope**: Transaction logs
- **Retention**: 7 days
- **Storage**: Local only

#### 3. Configuration Backups
- **Frequency**: On change
- **Scope**: Config files, SSL certs
- **Retention**: 90 days
- **Storage**: Git repository + Cloud

### Backup Schedule

| Time | Backup Type | Target | Retention |
|------|-------------|--------|-----------|
| 00:00 | Full PostgreSQL | DB + Cloud | 30 days |
| 00:15 | Full Redis | Cache + Cloud | 30 days |
| Hourly | WAL Files | Local only | 7 days |
| On Change | Configs | Git + Cloud | 90 days |

---

## 🤖 Automated Backups

### Backup Script

Location: `scripts/backup-production.sh`

#### Features
- **PostgreSQL**: pg_dump with compression
- **Redis**: BGSAVE with compression
- **Cloud Upload**: AWS S3 integration
- **Retention**: Automatic cleanup
- **Notifications**: Webhook/email alerts
- **Logging**: Detailed operation logs

#### Configuration

```bash
# Environment variables
BACKUP_DIR=/backups                    # Local backup directory
RETENTION_DAYS=30                      # Retention period
AWS_S3_BUCKET=operator-demo-backups    # S3 bucket name
BACKUP_WEBHOOK_URL=https://hooks.slack.com/...  # Notification webhook
```

#### Cron Job Setup

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/operator-demo-2026/scripts/backup-production.sh

# Hourly WAL backup
0 * * * * /path/to/operator-demo-2026/scripts/backup-wal.sh
```

### Backup Script Details

```bash
#!/bin/bash
# Production Backup Script for Operator Demo 2026

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="operator-demo-postgres"
REDIS_CONTAINER="operator-demo-redis"

# Create backup directory
mkdir -p "${BACKUP_DIR}/postgresql"
mkdir -p "${BACKUP_DIR}/redis"

echo "🔄 Starting production backup at $(date)"

# PostgreSQL Backup
echo "📦 Creating PostgreSQL backup..."
POSTGRES_BACKUP_FILE="${BACKUP_DIR}/postgresql/postgres_backup_${TIMESTAMP}.sql"

docker exec "${POSTGRES_CONTAINER}" pg_dump -U postgres operator_demo > "${POSTGRES_BACKUP_FILE}"

# Compress PostgreSQL backup
echo "🗜️  Compressing PostgreSQL backup..."
gzip "${POSTGRES_BACKUP_FILE}"
POSTGRES_BACKUP_FILE="${POSTGRES_BACKUP_FILE}.gz"

# Redis Backup
echo "📦 Creating Redis backup..."
REDIS_BACKUP_FILE="${BACKUP_DIR}/redis/redis_backup_${TIMESTAMP}.rdb"

docker exec "${REDIS_CONTAINER}" redis-cli BGSAVE
sleep 5  # Wait for background save to complete

docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${REDIS_BACKUP_FILE}"

# Compress Redis backup
echo "🗜️  Compressing Redis backup..."
gzip "${REDIS_BACKUP_FILE}"
REDIS_BACKUP_FILE="${REDIS_BACKUP_FILE}.gz"

# Upload to S3 (if configured)
if [[ -n "${AWS_S3_BUCKET:-}" && -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
    echo "☁️  Uploading backups to S3..."
    
    # Upload PostgreSQL backup
    aws s3 cp "${POSTGRES_BACKUP_FILE}" "s3://${AWS_S3_BUCKET}/backups/postgresql/"
    
    # Upload Redis backup
    aws s3 cp "${REDIS_BACKUP_FILE}" "s3://${AWS_S3_BUCKET}/backups/redis/"
    
    echo "✅ Backups uploaded to S3"
else
    echo "⚠️  S3 not configured, keeping local backups only"
fi

# Cleanup old backups
echo "🧹 Cleaning up old backups (older than ${RETENTION_DAYS} days)..."

# Clean up PostgreSQL backups
find "${BACKUP_DIR}/postgresql" -name "*.gz" -mtime +${RETENTION_DAYS} -delete

# Clean up Redis backups
find "${BACKUP_DIR}/redis" -name "*.gz" -mtime +${RETENTION_DAYS} -delete

# Clean up S3 backups (if configured)
if [[ -n "${AWS_S3_BUCKET:-}" ]]; then
    aws s3 ls "s3://${AWS_S3_BUCKET}/backups/postgresql/" | while read -r line; do
        createDate=$(echo "$line" | awk '{print $1" "$2}')
        createDate=$(date -d "$createDate" +%s)
        olderThan=$(date -d "$RETENTION_DAYS days ago" +%s)
        
        if [[ $createDate -lt $olderThan ]]; then
            fileName=$(echo "$line" | awk '{print $4}')
            if [[ $fileName != "" ]]; then
                aws s3 rm "s3://${AWS_S3_BUCKET}/backups/postgresql/$fileName"
            fi
        fi
    done
fi

echo "✅ Production backup completed at $(date)"
```

---

## 🛠️ Manual Backups

### PostgreSQL Manual Backup

```bash
# Create backup directory
mkdir -p /tmp/manual-backups

# Full database backup
docker exec operator-demo-postgres pg_dump -U postgres operator_demo > /tmp/manual-backups/manual_postgres_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip /tmp/manual-backups/manual_postgres_*.sql

# Schema-only backup
docker exec operator-demo-postgres pg_dump -U postgres --schema-only operator_demo > /tmp/manual-backups/schema_$(date +%Y%m%d_%H%M%S).sql

# Data-only backup
docker exec operator-demo-postgres pg_dump -U postgres --data-only operator_demo > /tmp/manual-backups/data_$(date +%Y%m%d_%H%M%S).sql
```

### Redis Manual Backup

```bash
# Create backup directory
mkdir -p /tmp/manual-backups

# Trigger background save
docker exec operator-demo-redis redis-cli BGSAVE

# Wait for save to complete
while [[ $(docker exec operator-demo-redis redis-cli LASTSAVE) -eq $(docker exec operator-demo-redis redis-cli LASTSAVE) ]]; do
    sleep 1
done

# Copy backup file
docker cp operator-demo-redis:/data/dump.rdb /tmp/manual-backups/manual_redis_$(date +%Y%m%d_%H%M%S).rdb

# Compress backup
gzip /tmp/manual-backups/manual_redis_*.rdb
```

### Configuration Backup

```bash
# Backup environment files
mkdir -p /tmp/manual-backups/config
cp .env.production /tmp/manual-backups/config/
cp .env.traefik /tmp/manual-backups/config/

# Backup Traefik configuration
cp -r traefik/ /tmp/manual-backups/config/

# Backup monitoring configuration
cp -r monitoring/ /tmp/manual-backups/config/

# Backup Docker Compose files
cp docker-compose*.yml /tmp/manual-backups/config/

# Create archive
tar czf /tmp/manual-backups/config_$(date +%Y%m%d_%H%M%S).tar.gz -C /tmp/manual-backups config/
```

---

## 🔄 Recovery Procedures

### Disaster Recovery Scenarios

#### 1. Complete System Recovery

**Scenario**: Total system failure
**Recovery Time**: 1-2 hours

```bash
# Step 1: Restore infrastructure
docker compose -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.prod.yml \
  -f docker-compose.monitoring.yml \
  up -d

# Step 2: Wait for services to be healthy
sleep 60

# Step 3: Restore PostgreSQL
docker exec -i operator-demo-postgres psql -U postgres operator_demo < /backups/postgres/latest_backup.sql.gz

# Step 4: Restore Redis
docker stop operator-demo-redis
docker cp /backups/redis/latest_backup.rdb.gz operator-demo-redis:/data/dump.rdb.gz
docker exec operator-demo-redis gunzip /data/dump.rdb.gz
docker start operator-demo-redis

# Step 5: Verify services
curl -f http://localhost:8000/health
curl -f http://localhost:3000/
```

#### 2. Database Recovery

**Scenario**: Database corruption
**Recovery Time**: 15-30 minutes

```bash
# Step 1: Stop application
docker compose stop backend

# Step 2: Identify latest backup
LATEST_BACKUP=$(ls -t /backups/postgres/postgres_backup_*.sql.gz | head -1)

# Step 3: Restore database
gunzip -c "$LATEST_BACKUP" | docker exec -i operator-demo-postgres psql -U postgres operator_demo

# Step 4: Restart application
docker compose start backend

# Step 5: Verify data integrity
docker exec operator-demo-postgres psql -U postgres operator_demo -c "SELECT COUNT(*) FROM users;"
```

#### 3. Redis Recovery

**Scenario**: Redis data loss
**Recovery Time**: 5-10 minutes

```bash
# Step 1: Stop Redis
docker stop operator-demo-redis

# Step 2: Identify latest backup
LATEST_BACKUP=$(ls -t /backups/redis/redis_backup_*.rdb.gz | head -1)

# Step 3: Restore Redis data
docker cp "$LATEST_BACKUP" operator-demo-redis:/data/dump.rdb.gz
docker exec operator-demo-redis gunzip /data/dump.rdb.gz

# Step 4: Start Redis
docker start operator-demo-redis

# Step 5: Verify Redis
docker exec operator-demo-redis redis-cli ping
docker exec operator-demo-redis redis-cli dbsize
```

#### 4. Point-in-Time Recovery

**Scenario**: Recover to specific time
**Recovery Time**: 30-60 minutes

```bash
# Step 1: Identify base backup
BASE_BACKUP="/backups/postgres/postgres_backup_20251012_000000.sql.gz"

# Step 2: Restore base backup
gunzip -c "$BASE_BACKUP" | docker exec -i operator-demo-postgres psql -U postgres operator_demo

# Step 3: Apply WAL files (if available)
# This requires WAL archiving to be configured
for wal_file in /backups/wal/20251012_*; do
    docker cp "$wal_file" operator-demo-postgres:/var/lib/postgresql/wal/
done

# Step 4: Recover to specific time
docker exec operator-demo-postgres psql -U postgres operator_demo -c "
    SELECT pg_wal_replay_resume();
"
```

### Partial Recovery

#### Single Table Recovery

```bash
# Step 1: Extract table from backup
gunzip -c /backups/postgres/latest_backup.sql.gz | grep -A 1000 "COPY public.users" > /tmp/users_table.sql

# Step 2: Create temporary table
docker exec operator-demo-postgres psql -U postgres operator_demo -c "
    CREATE TABLE users_backup AS TABLE users WITH NO DATA;
"

# Step 3: Restore data
docker exec -i operator-demo-postgres psql -U postgres operator_demo < /tmp/users_table.sql

# Step 4: Verify and merge data
docker exec operator-demo-postgres psql -U postgres operator_demo -c "
    INSERT INTO users SELECT * FROM users_backup ON CONFLICT DO NOTHING;
    DROP TABLE users_backup;
"
```

---

## ☁️ Cloud Storage

### AWS S3 Configuration

#### S3 Bucket Setup

```bash
# Create S3 bucket
aws s3 mb s3://operator-demo-backups

# Configure lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket operator-demo-backups \
  --lifecycle-configuration file://s3-lifecycle.json
```

#### Lifecycle Policy (`s3-lifecycle.json`)

```json
{
  "Rules": [
    {
      "ID": "BackupRetention",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "backups/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

#### IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::operator-demo-backups",
        "arn:aws:s3:::operator-demo-backups/*"
      ]
    }
  ]
}
```

### Alternative Cloud Providers

#### Google Cloud Storage

```bash
# Create bucket
gsutil mb gs://operator-demo-backups

# Upload backup
gsutil cp /backups/postgres/latest.sql.gz gs://operator-demo-backups/postgresql/

# Set lifecycle
gsutil lifecycle set lifecycle.json gs://operator-demo-backups
```

#### Azure Blob Storage

```bash
# Create container
az storage container create --name backups --account-name mystorageaccount

# Upload backup
az storage blob upload \
  --container-name backups \
  --file /backups/postgres/latest.sql.gz \
  --name postgresql/latest.sql.gz
```

---

## 🧪 Testing & Validation

### Backup Testing

#### Automated Testing

```bash
#!/bin/bash
# Backup testing script

# Test backup restoration
TEST_DB="operator_demo_test"

# Create test database
docker exec operator-demo-postgres psql -U postgres -c "CREATE DATABASE $TEST_DB;"

# Restore backup to test database
gunzip -c /backups/postgres/latest_backup.sql.gz | docker exec -i operator-demo-postgres psql -U postgres "$TEST_DB"

# Validate data
USER_COUNT=$(docker exec operator-demo-postgres psql -U postgres "$TEST_DB" -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')

if [[ $USER_COUNT -gt 0 ]]; then
    echo "✅ Backup validation successful: $USER_COUNT users found"
else
    echo "❌ Backup validation failed: no users found"
    exit 1
fi

# Clean up test database
docker exec operator-demo-postgres psql -U postgres -c "DROP DATABASE $TEST_DB;"
```

#### Manual Testing

```bash
# Test PostgreSQL backup
1. Create test data
2. Run backup
3. Restore to test database
4. Verify data integrity

# Test Redis backup
1. Create test data in Redis
2. Run backup
3. Restore Redis
4. Verify data exists
```

### Recovery Drills

#### Monthly Recovery Drill

```bash
# Schedule monthly recovery drill
0 2 1 * * /path/to/recovery-drill.sh

# Recovery drill script
#!/bin/bash
echo "🚨 Starting monthly recovery drill"

# Create test environment
docker compose -f docker-compose.test.yml up -d

# Restore latest backup
./restore-latest-backup.sh

# Run health checks
./health-checks.sh

# Generate report
./generate-drill-report.sh

# Clean up test environment
docker compose -f docker-compose.test.yml down

echo "✅ Recovery drill completed"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backup Fails

**Symptoms**: Backup script exits with error
**Diagnostics**:
```bash
# Check backup logs
tail -f /var/log/backup.log

# Check disk space
df -h /backups

# Check container status
docker ps | grep -E "(postgres|redis)"
```

**Solutions**:
- Free up disk space
- Restart containers
- Check permissions

#### 2. Restore Fails

**Symptoms**: Data restoration fails
**Diagnostics**:
```bash
# Check backup file integrity
gunzip -t /backups/postgres/latest_backup.sql.gz

# Check database connection
docker exec operator-demo-postgres psql -U postgres -c "SELECT 1;"

# Check database size
docker exec operator-demo-postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('operator_demo'));"
```

**Solutions**:
- Verify backup integrity
- Check database permissions
- Ensure sufficient disk space

#### 3. S3 Upload Fails

**Symptoms**: Cloud upload fails
**Diagnostics**:
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://operator-demo-backups

# Check network connectivity
ping s3.amazonaws.com
```

**Solutions**:
- Verify AWS credentials
- Check bucket permissions
- Test network connectivity

### Performance Issues

#### Slow Backups

```bash
# Optimize PostgreSQL backup
docker exec operator-demo-postgres pg_dump -U postgres \
  --no-owner \
  --no-privileges \
  --exclude-table-data='large_table' \
  operator_demo > backup.sql

# Use parallel backup for large databases
pg_dump -U postgres \
  --format=directory \
  --jobs=4 \
  --file=/backup/dir \
  operator_demo
```

#### Large Backup Files

```bash
# Compress backups more efficiently
pigz --best backup.sql

# Split large backups
split -b 1G backup.sql.gz backup_part_

# Use incremental backups
pg_basebackup -U postgres -D /backup/base -Ft -z -P
```

---

## 📚 Additional Resources

### Documentation
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Redis Persistence Documentation](https://redis.io/topics/persistence)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

### Tools

#### Backup Tools
- **pg_dump**: PostgreSQL native backup
- **pg_basebackup**: Physical backup tool
- **Barman**: Professional backup tool
- **WAL-G**: WAL archiving tool

#### Monitoring Tools
- **Prometheus**: Backup metrics
- **Grafana**: Backup dashboards
- **AlertManager**: Backup failure alerts

### Best Practices

1. **3-2-1 Rule**: 3 copies, 2 media, 1 offsite
2. **Regular Testing**: Test restores monthly
3. **Encryption**: Encrypt sensitive backups
4. **Documentation**: Document procedures
5. **Monitoring**: Monitor backup success/failure

---

**Last Updated**: October 12, 2025  
**Version**: 2.0.0  
**Environment**: Production