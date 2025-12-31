#!/bin/bash
# Production Backup Script for CC-Lite 2026 (Voice by Kraliki)
# This script creates automated backups of PostgreSQL, Redis, and Qdrant
# Updated: December 26, 2025

set -euo pipefail

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="cc-lite-postgres"
REDIS_CONTAINER="cc-lite-redis"
QDRANT_CONTAINER="cc-lite-qdrant"

# Create backup directories
mkdir -p "${BACKUP_DIR}/postgresql"
mkdir -p "${BACKUP_DIR}/redis"
mkdir -p "${BACKUP_DIR}/qdrant"
mkdir -p "${BACKUP_DIR}/logs"

# Log file for this backup run
LOG_FILE="${BACKUP_DIR}/logs/backup_${TIMESTAMP}.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

log "Starting production backup"

# Check container status
POSTGRES_RUNNING=$(docker ps --filter "name=${POSTGRES_CONTAINER}" --format "{{.Names}}" 2>/dev/null || echo "")
REDIS_RUNNING=$(docker ps --filter "name=${REDIS_CONTAINER}" --format "{{.Names}}" 2>/dev/null || echo "")
QDRANT_RUNNING=$(docker ps --filter "name=${QDRANT_CONTAINER}" --format "{{.Names}}" 2>/dev/null || echo "")

# PostgreSQL Backup
POSTGRES_BACKUP_FILE="${BACKUP_DIR}/postgresql/postgres_backup_${TIMESTAMP}.sql"
if [[ -n "${POSTGRES_RUNNING}" ]]; then
    log "Creating PostgreSQL backup..."
    if docker exec "${POSTGRES_CONTAINER}" pg_dump -U postgres operator_demo > "${POSTGRES_BACKUP_FILE}" 2>>"${LOG_FILE}"; then
        log "Compressing PostgreSQL backup..."
        gzip "${POSTGRES_BACKUP_FILE}"
        POSTGRES_BACKUP_FILE="${POSTGRES_BACKUP_FILE}.gz"
        log "PostgreSQL backup complete: $(du -h "${POSTGRES_BACKUP_FILE}" | cut -f1)"
    else
        log "ERROR: PostgreSQL backup failed"
        POSTGRES_BACKUP_FILE=""
    fi
else
    log "WARNING: PostgreSQL container not running, skipping backup"
    POSTGRES_BACKUP_FILE=""
fi

# Redis Backup
REDIS_BACKUP_FILE="${BACKUP_DIR}/redis/redis_backup_${TIMESTAMP}.rdb"
if [[ -n "${REDIS_RUNNING}" ]]; then
    log "Creating Redis backup..."
    # Get Redis password from environment or use default
    REDIS_PASSWORD="${REDIS_PASSWORD:-change-this-secure-redis-password-min-32-chars}"
    if docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" --no-auth-warning BGSAVE 2>>"${LOG_FILE}"; then
        sleep 5  # Wait for background save to complete
        if docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${REDIS_BACKUP_FILE}" 2>>"${LOG_FILE}"; then
            log "Compressing Redis backup..."
            gzip "${REDIS_BACKUP_FILE}"
            REDIS_BACKUP_FILE="${REDIS_BACKUP_FILE}.gz"
            log "Redis backup complete: $(du -h "${REDIS_BACKUP_FILE}" | cut -f1)"
        else
            log "ERROR: Redis backup copy failed"
            REDIS_BACKUP_FILE=""
        fi
    else
        log "ERROR: Redis BGSAVE failed"
        REDIS_BACKUP_FILE=""
    fi
else
    log "WARNING: Redis container not running, skipping backup"
    REDIS_BACKUP_FILE=""
fi

# Qdrant Backup (vector database)
QDRANT_BACKUP_FILE="${BACKUP_DIR}/qdrant/qdrant_backup_${TIMESTAMP}.tar"
if [[ -n "${QDRANT_RUNNING}" ]]; then
    log "Creating Qdrant vector database backup..."
    # Create snapshot via Qdrant API (internal network)
    QDRANT_HOST="localhost"
    QDRANT_PORT="${QDRANT_PORT:-6337}"

    # Create a snapshot for all collections
    if curl -s -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/snapshots" -o "${BACKUP_DIR}/qdrant/snapshot_response.json" 2>>"${LOG_FILE}"; then
        # Copy the qdrant storage volume
        if docker cp "${QDRANT_CONTAINER}:/qdrant/storage" "${BACKUP_DIR}/qdrant/storage_${TIMESTAMP}" 2>>"${LOG_FILE}"; then
            log "Compressing Qdrant backup..."
            tar -cf "${QDRANT_BACKUP_FILE}" -C "${BACKUP_DIR}/qdrant" "storage_${TIMESTAMP}" 2>>"${LOG_FILE}"
            gzip "${QDRANT_BACKUP_FILE}"
            QDRANT_BACKUP_FILE="${QDRANT_BACKUP_FILE}.gz"
            rm -rf "${BACKUP_DIR}/qdrant/storage_${TIMESTAMP}"
            log "Qdrant backup complete: $(du -h "${QDRANT_BACKUP_FILE}" | cut -f1)"
        else
            log "WARNING: Qdrant storage copy failed, skipping"
            QDRANT_BACKUP_FILE=""
        fi
    else
        log "WARNING: Qdrant snapshot API call failed, skipping"
        QDRANT_BACKUP_FILE=""
    fi
else
    log "WARNING: Qdrant container not running, skipping backup"
    QDRANT_BACKUP_FILE=""
fi

# Upload to S3 (if configured)
if [[ -n "${AWS_S3_BUCKET:-}" && -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
    log "Uploading backups to S3..."

    # Upload PostgreSQL backup
    if [[ -n "${POSTGRES_BACKUP_FILE}" && -f "${POSTGRES_BACKUP_FILE}" ]]; then
        aws s3 cp "${POSTGRES_BACKUP_FILE}" "s3://${AWS_S3_BUCKET}/cc-lite/backups/postgresql/" 2>>"${LOG_FILE}" && \
            log "PostgreSQL backup uploaded to S3"
    fi

    # Upload Redis backup
    if [[ -n "${REDIS_BACKUP_FILE}" && -f "${REDIS_BACKUP_FILE}" ]]; then
        aws s3 cp "${REDIS_BACKUP_FILE}" "s3://${AWS_S3_BUCKET}/cc-lite/backups/redis/" 2>>"${LOG_FILE}" && \
            log "Redis backup uploaded to S3"
    fi

    # Upload Qdrant backup
    if [[ -n "${QDRANT_BACKUP_FILE}" && -f "${QDRANT_BACKUP_FILE}" ]]; then
        aws s3 cp "${QDRANT_BACKUP_FILE}" "s3://${AWS_S3_BUCKET}/cc-lite/backups/qdrant/" 2>>"${LOG_FILE}" && \
            log "Qdrant backup uploaded to S3"
    fi
else
    log "S3 not configured, keeping local backups only"
fi

# Cleanup old backups
log "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."

# Clean up PostgreSQL backups
find "${BACKUP_DIR}/postgresql" -name "*.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Clean up Redis backups
find "${BACKUP_DIR}/redis" -name "*.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Clean up Qdrant backups
find "${BACKUP_DIR}/qdrant" -name "*.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Clean up old log files
find "${BACKUP_DIR}/logs" -name "*.log" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Clean up S3 backups (if configured)
if [[ -n "${AWS_S3_BUCKET:-}" ]]; then
    log "Cleaning up old S3 backups..."
    for backup_type in postgresql redis qdrant; do
        aws s3 ls "s3://${AWS_S3_BUCKET}/cc-lite/backups/${backup_type}/" 2>/dev/null | while read -r line; do
            createDate=$(echo "$line" | awk '{print $1" "$2}')
            createDate=$(date -d "$createDate" +%s 2>/dev/null || echo "0")
            olderThan=$(date -d "$RETENTION_DAYS days ago" +%s)

            if [[ "$createDate" != "0" && $createDate -lt $olderThan ]]; then
                fileName=$(echo "$line" | awk '{print $4}')
                if [[ -n "$fileName" ]]; then
                    aws s3 rm "s3://${AWS_S3_BUCKET}/cc-lite/backups/${backup_type}/$fileName" 2>>"${LOG_FILE}" && \
                        log "Deleted old S3 backup: ${backup_type}/$fileName"
                fi
            fi
        done
    done
fi

# Backup summary
log "=========================================="
log "BACKUP SUMMARY"
log "=========================================="
if [[ -n "${POSTGRES_BACKUP_FILE}" && -f "${POSTGRES_BACKUP_FILE}" ]]; then
    log "PostgreSQL: ${POSTGRES_BACKUP_FILE} ($(du -h "${POSTGRES_BACKUP_FILE}" | cut -f1))"
else
    log "PostgreSQL: SKIPPED or FAILED"
fi
if [[ -n "${REDIS_BACKUP_FILE}" && -f "${REDIS_BACKUP_FILE}" ]]; then
    log "Redis: ${REDIS_BACKUP_FILE} ($(du -h "${REDIS_BACKUP_FILE}" | cut -f1))"
else
    log "Redis: SKIPPED or FAILED"
fi
if [[ -n "${QDRANT_BACKUP_FILE}" && -f "${QDRANT_BACKUP_FILE}" ]]; then
    log "Qdrant: ${QDRANT_BACKUP_FILE} ($(du -h "${QDRANT_BACKUP_FILE}" | cut -f1))"
else
    log "Qdrant: SKIPPED or FAILED"
fi
log "Retention: ${RETENTION_DAYS} days"
log "Log file: ${LOG_FILE}"
log "Production backup completed"

# Create latest symlinks for easy access
ln -sf "$(basename "${POSTGRES_BACKUP_FILE:-/dev/null}")" "${BACKUP_DIR}/postgresql/latest.sql.gz" 2>/dev/null || true
ln -sf "$(basename "${REDIS_BACKUP_FILE:-/dev/null}")" "${BACKUP_DIR}/redis/latest.rdb.gz" 2>/dev/null || true
ln -sf "$(basename "${QDRANT_BACKUP_FILE:-/dev/null}")" "${BACKUP_DIR}/qdrant/latest.tar.gz" 2>/dev/null || true

# Send notification (if webhook configured)
if [[ -n "${BACKUP_WEBHOOK_URL:-}" ]]; then
    BACKUP_STATUS="success"
    [[ -z "${POSTGRES_BACKUP_FILE}" || -z "${REDIS_BACKUP_FILE}" ]] && BACKUP_STATUS="partial"

    curl -s -X POST "${BACKUP_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{
            \"text\": \"CC-Lite backup completed (${BACKUP_STATUS})\",
            \"attachments\": [
                {
                    \"color\": \"$([ \"${BACKUP_STATUS}\" = \"success\" ] && echo \"good\" || echo \"warning\")\",
                    \"fields\": [
                        {\"title\": \"PostgreSQL\", \"value\": \"$([ -n \"${POSTGRES_BACKUP_FILE}\" ] && echo \"OK\" || echo \"SKIP\")\", \"short\": true},
                        {\"title\": \"Redis\", \"value\": \"$([ -n \"${REDIS_BACKUP_FILE}\" ] && echo \"OK\" || echo \"SKIP\")\", \"short\": true},
                        {\"title\": \"Qdrant\", \"value\": \"$([ -n \"${QDRANT_BACKUP_FILE}\" ] && echo \"OK\" || echo \"SKIP\")\", \"short\": true},
                        {\"title\": \"Retention\", \"value\": \"${RETENTION_DAYS} days\", \"short\": true}
                    ]
                }
            ]
        }" 2>/dev/null || true
fi

# Exit with appropriate code
if [[ -z "${POSTGRES_BACKUP_FILE}" ]]; then
    exit 1
fi
exit 0