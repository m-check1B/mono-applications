#!/bin/bash
# Database Backup Script for CC-Lite 2026 (Voice by Kraliki)
# Backs up PostgreSQL database to local storage and optionally S3
# Updated: December 26, 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups}"
BACKUP_FILE="postgres_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Database configuration from .env or environment
DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/operator_demo}"

# Parse DATABASE_URL
DB_USER=$(echo $DATABASE_URL | sed -E 's|.*://([^:]+):.*|\1|')
DB_PASS=$(echo $DATABASE_URL | sed -E 's|.*://[^:]+:([^@]+)@.*|\1|')
DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:/]+).*|\1|')
DB_PORT=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
DB_NAME=$(echo $DATABASE_URL | sed -E 's|.*/([^?]+).*|\1|')

echo -e "${YELLOW}🔄 Starting database backup...${NC}"
echo "Database: $DB_NAME on $DB_HOST:$DB_PORT"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo -e "${YELLOW}📦 Creating backup: $BACKUP_FILE${NC}"
PGPASSWORD="$DB_PASS" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created successfully${NC}"

    # Compress backup
    echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"

    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Compressed backup: $BACKUP_SIZE${NC}"

    # Upload to S3 if configured
    if [ -n "$AWS_S3_BUCKET" ]; then
        echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
        aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$AWS_S3_BUCKET/postgres/" \
            --storage-class STANDARD_IA

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Backup uploaded to S3${NC}"
        else
            echo -e "${RED}❌ S3 upload failed${NC}"
        fi
    fi

    # Cleanup old backups (local)
    echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo -e "${GREEN}✅ Cleanup completed${NC}"

    # Cleanup old S3 backups
    if [ -n "$AWS_S3_BUCKET" ]; then
        CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)
        aws s3 ls "s3://$AWS_S3_BUCKET/postgres/" | while read -r line; do
            FILE_DATE=$(echo "$line" | awk '{print $4}' | sed -E 's/backup_([0-9]{8})_.*/\1/')
            FILE_NAME=$(echo "$line" | awk '{print $4}')

            if [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
                echo "Deleting old S3 backup: $FILE_NAME"
                aws s3 rm "s3://$AWS_S3_BUCKET/postgres/$FILE_NAME"
            fi
        done
    fi

    echo -e "${GREEN}✅ Backup process completed successfully${NC}"
    echo "Backup location: $BACKUP_DIR/$BACKUP_FILE"

    # Log to syslog if available
    logger -t operator-demo "Database backup completed: $BACKUP_FILE"

else
    echo -e "${RED}❌ Backup failed${NC}"
    logger -t operator-demo "Database backup FAILED"
    exit 1
fi
