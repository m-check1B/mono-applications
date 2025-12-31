#!/bin/bash
# Voice by Kraliki Automated Backup Script
# ================================
# Runs automated backups of PostgreSQL and Redis data
# Designed to run in Docker container as backup service

set -euo pipefail

# Configuration from environment variables
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-cc_light_prod}"
POSTGRES_USER="${POSTGRES_USER:-cc_lite_user}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
BACKUP_DIR="/backups"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Create backup directories
mkdir -p "$BACKUP_DIR/postgres" "$BACKUP_DIR/redis"

log "Starting Voice by Kraliki backup process..."

# Wait for services to be ready
log "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
    sleep 5
done

# Read database password from Docker secret
if [ -f "/run/secrets/cc_lite_db_password" ]; then
    export PGPASSWORD=$(cat /run/secrets/cc_lite_db_password)
else
    error_exit "Database password secret not found"
fi

# Generate timestamp for backup files
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# PostgreSQL Backup
log "Creating PostgreSQL backup..."
pg_dump \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=custom \
    --compress=9 \
    --file="$BACKUP_DIR/postgres/cc_light_${TIMESTAMP}.dump" || error_exit "PostgreSQL backup failed"

# Create SQL backup as well for easier restoration
pg_dump \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=plain \
    --file="$BACKUP_DIR/postgres/cc_light_${TIMESTAMP}.sql" || error_exit "PostgreSQL SQL backup failed"

# Compress SQL backup
gzip "$BACKUP_DIR/postgres/cc_light_${TIMESTAMP}.sql"

log "PostgreSQL backup completed successfully"

# Redis Backup (if we can access Redis)
REDIS_PASSWORD=""
if [ -f "/run/secrets/cc_lite_redis_password" ]; then
    REDIS_PASSWORD=$(cat /run/secrets/cc_lite_redis_password)
fi

# Check if Redis is accessible
if command -v redis-cli >/dev/null 2>&1; then
    log "Creating Redis backup..."

    # Create Redis dump
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h redis -a "$REDIS_PASSWORD" --rdb "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb" || log "WARNING: Redis backup failed"
    else
        redis-cli -h redis --rdb "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb" || log "WARNING: Redis backup failed"
    fi

    log "Redis backup completed"
else
    log "Redis CLI not available, skipping Redis backup"
fi

# Create backup manifest
cat > "$BACKUP_DIR/backup_${TIMESTAMP}.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "database": {
        "host": "$POSTGRES_HOST",
        "database": "$POSTGRES_DB",
        "user": "$POSTGRES_USER",
        "files": [
            "postgres/cc_light_${TIMESTAMP}.dump",
            "postgres/cc_light_${TIMESTAMP}.sql.gz"
        ]
    },
    "redis": {
        "host": "redis",
        "files": [
            "redis/redis_${TIMESTAMP}.rdb"
        ]
    },
    "retention_days": $BACKUP_RETENTION_DAYS
}
EOF

log "Backup manifest created"

# Cleanup old backups
log "Cleaning up backups older than $BACKUP_RETENTION_DAYS days..."

# Remove old PostgreSQL backups
find "$BACKUP_DIR/postgres" -name "cc_light_*.dump" -mtime +$BACKUP_RETENTION_DAYS -delete || true
find "$BACKUP_DIR/postgres" -name "cc_light_*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete || true

# Remove old Redis backups
find "$BACKUP_DIR/redis" -name "redis_*.rdb" -mtime +$BACKUP_RETENTION_DAYS -delete || true

# Remove old manifests
find "$BACKUP_DIR" -name "backup_*.json" -mtime +$BACKUP_RETENTION_DAYS -delete || true

log "Cleanup completed"

# Calculate backup sizes
POSTGRES_SIZE=$(du -sh "$BACKUP_DIR/postgres/cc_light_${TIMESTAMP}.dump" 2>/dev/null | cut -f1 || echo "unknown")
REDIS_SIZE=$(du -sh "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb" 2>/dev/null | cut -f1 || echo "unknown")
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "unknown")

log "Backup completed successfully!"
log "PostgreSQL backup size: $POSTGRES_SIZE"
log "Redis backup size: $REDIS_SIZE"
log "Total backup directory size: $TOTAL_SIZE"

# Health check endpoint (for monitoring)
if command -v curl >/dev/null 2>&1; then
    # Report backup status to health check endpoint
    curl -X POST \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"backup\",
            \"status\": \"success\",
            \"timestamp\": \"$TIMESTAMP\",
            \"postgres_size\": \"$POSTGRES_SIZE\",
            \"redis_size\": \"$REDIS_SIZE\"
        }" \
        "http://app:3010/internal/backup-status" 2>/dev/null || true
fi

# If running in cron mode, sleep and repeat
if [ "${BACKUP_MODE:-once}" = "cron" ]; then
    log "Backup service running in cron mode, scheduling next backup..."

    # Calculate sleep time until next backup (daily at 2 AM)
    CURRENT_HOUR=$(date +%H)
    CURRENT_MINUTE=$(date +%M)

    if [ "$CURRENT_HOUR" -lt 2 ]; then
        # Sleep until 2 AM today
        SLEEP_HOURS=$((2 - CURRENT_HOUR))
        SLEEP_MINUTES=$((60 - CURRENT_MINUTE))
    else
        # Sleep until 2 AM tomorrow
        SLEEP_HOURS=$((26 - CURRENT_HOUR))
        SLEEP_MINUTES=$((60 - CURRENT_MINUTE))
    fi

    SLEEP_SECONDS=$(((SLEEP_HOURS * 3600) + (SLEEP_MINUTES * 60)))
    log "Next backup in $SLEEP_HOURS hours and $SLEEP_MINUTES minutes"

    sleep $SLEEP_SECONDS
    exec "$0"  # Re-run this script
else
    log "Backup service completed (one-time mode)"
fi