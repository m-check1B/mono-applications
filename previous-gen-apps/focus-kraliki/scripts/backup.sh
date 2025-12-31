#!/bin/bash

# Focus by Kraliki Backup Script
# Backs up database and important data

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="focus_kraliki_backup_${TIMESTAMP}.sql"

# Detect compose file
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps -q &>/dev/null; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "🗄️  Starting backup..."
echo "📝 Using compose file: $COMPOSE_FILE"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables
set -a
source .env 2>/dev/null || echo "Warning: .env file not found"
set +a

# Backup PostgreSQL database
echo "📦 Backing up PostgreSQL database..."
docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U ${DB_USER:-postgres} focus_kraliki > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
echo "🗜️  Compressing backup..."
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Remove backups older than 30 days
echo "🧹 Cleaning old backups..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)
echo "✅ Backup complete: ${BACKUP_FILE}.gz (${BACKUP_SIZE})"
echo "📍 Location: $BACKUP_DIR/${BACKUP_FILE}.gz"

# List recent backups
echo ""
echo "📋 Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5
