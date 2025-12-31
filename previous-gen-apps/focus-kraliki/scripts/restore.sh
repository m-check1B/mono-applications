#!/bin/bash

# Focus by Kraliki Restore Script
# Restores database from backup

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will replace the current database!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Load environment variables
set -a
source .env 2>/dev/null || echo "Warning: .env file not found"
set +a

echo "🗄️  Starting restore..."

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "📦 Decompressing backup..."
    gunzip -c "$BACKUP_FILE" > /tmp/restore.sql
    SQL_FILE="/tmp/restore.sql"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Restore database
echo "⚡ Restoring database..."
docker-compose exec -T postgres psql -U ${DB_USER:-postgres} -d focus_kraliki < "$SQL_FILE"

# Cleanup temp file
rm -f /tmp/restore.sql

echo "✅ Restore complete!"
echo "🔄 Restarting services..."
docker-compose restart backend

echo "✅ All done!"
