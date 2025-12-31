#!/bin/bash
# Database Restore Script for CC-Lite 2026 (Voice by Kraliki)
# Restores PostgreSQL, Redis, and/or Qdrant from backup files
# Updated: December 26, 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory for relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_DIR}/backups}"

# Container names
POSTGRES_CONTAINER="cc-lite-postgres"
REDIS_CONTAINER="cc-lite-redis"
QDRANT_CONTAINER="cc-lite-qdrant"

show_usage() {
    echo -e "${BLUE}CC-Lite Database Restore Script${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -p, --postgres <file>    Restore PostgreSQL from backup file"
    echo "  -r, --redis <file>       Restore Redis from backup file"
    echo "  -q, --qdrant <file>      Restore Qdrant from backup file"
    echo "  -a, --all                Restore all from latest backups"
    echo "  -l, --list               List available backups"
    echo "  -h, --help               Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 --postgres postgres_backup_20251226_120000.sql.gz"
    echo "  $0 --all"
    echo "  $0 -p latest.sql.gz -r latest.rdb.gz"
    echo ""
}

list_backups() {
    echo -e "${BLUE}Available Backups:${NC}"
    echo ""
    echo -e "${YELLOW}PostgreSQL:${NC}"
    ls -lh "${BACKUP_DIR}/postgresql/" 2>/dev/null | grep -E "\.sql\.gz$" || echo "  No backups found"
    echo ""
    echo -e "${YELLOW}Redis:${NC}"
    ls -lh "${BACKUP_DIR}/redis/" 2>/dev/null | grep -E "\.rdb\.gz$" || echo "  No backups found"
    echo ""
    echo -e "${YELLOW}Qdrant:${NC}"
    ls -lh "${BACKUP_DIR}/qdrant/" 2>/dev/null | grep -E "\.tar\.gz$" || echo "  No backups found"
    echo ""
}

restore_postgres() {
    local backup_file="$1"
    local full_path

    # Resolve path
    if [[ -f "$backup_file" ]]; then
        full_path="$backup_file"
    elif [[ -f "${BACKUP_DIR}/postgresql/$backup_file" ]]; then
        full_path="${BACKUP_DIR}/postgresql/$backup_file"
    else
        echo -e "${RED}PostgreSQL backup not found: $backup_file${NC}"
        return 1
    fi

    echo -e "${YELLOW}Restoring PostgreSQL from: $full_path${NC}"

    # Check container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
        echo -e "${RED}PostgreSQL container not running${NC}"
        return 1
    fi

    # Decompress if needed
    local temp_file="/tmp/restore_postgres_temp.sql"
    if [[ "$full_path" == *.gz ]]; then
        echo -e "${YELLOW}Decompressing backup...${NC}"
        gunzip -c "$full_path" > "$temp_file"
    else
        cp "$full_path" "$temp_file"
    fi

    # Restore database
    echo -e "${YELLOW}Restoring database...${NC}"
    docker cp "$temp_file" "${POSTGRES_CONTAINER}:/tmp/restore.sql"
    docker exec "${POSTGRES_CONTAINER}" psql -U postgres -d operator_demo -f /tmp/restore.sql

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL restored successfully${NC}"
        docker exec "${POSTGRES_CONTAINER}" rm /tmp/restore.sql
        rm "$temp_file"
        return 0
    else
        echo -e "${RED}PostgreSQL restore failed${NC}"
        rm "$temp_file" 2>/dev/null || true
        return 1
    fi
}

restore_redis() {
    local backup_file="$1"
    local full_path

    # Resolve path
    if [[ -f "$backup_file" ]]; then
        full_path="$backup_file"
    elif [[ -f "${BACKUP_DIR}/redis/$backup_file" ]]; then
        full_path="${BACKUP_DIR}/redis/$backup_file"
    else
        echo -e "${RED}Redis backup not found: $backup_file${NC}"
        return 1
    fi

    echo -e "${YELLOW}Restoring Redis from: $full_path${NC}"

    # Check container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        echo -e "${RED}Redis container not running${NC}"
        return 1
    fi

    # Decompress if needed
    local temp_file="/tmp/restore_redis_temp.rdb"
    if [[ "$full_path" == *.gz ]]; then
        echo -e "${YELLOW}Decompressing backup...${NC}"
        gunzip -c "$full_path" > "$temp_file"
    else
        cp "$full_path" "$temp_file"
    fi

    # Stop Redis, replace dump.rdb, restart
    echo -e "${YELLOW}Stopping Redis...${NC}"
    REDIS_PASSWORD="${REDIS_PASSWORD:-change-this-secure-redis-password-min-32-chars}"
    docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" --no-auth-warning SHUTDOWN NOSAVE 2>/dev/null || true

    # Wait for container to restart
    sleep 3

    # Copy backup file
    docker cp "$temp_file" "${REDIS_CONTAINER}:/data/dump.rdb"

    # Restart Redis container to load backup
    docker restart "${REDIS_CONTAINER}"

    # Wait for Redis to be ready
    sleep 5

    if docker exec "${REDIS_CONTAINER}" redis-cli -a "${REDIS_PASSWORD}" --no-auth-warning PING | grep -q PONG; then
        echo -e "${GREEN}Redis restored successfully${NC}"
        rm "$temp_file"
        return 0
    else
        echo -e "${RED}Redis restore failed${NC}"
        rm "$temp_file" 2>/dev/null || true
        return 1
    fi
}

restore_qdrant() {
    local backup_file="$1"
    local full_path

    # Resolve path
    if [[ -f "$backup_file" ]]; then
        full_path="$backup_file"
    elif [[ -f "${BACKUP_DIR}/qdrant/$backup_file" ]]; then
        full_path="${BACKUP_DIR}/qdrant/$backup_file"
    else
        echo -e "${RED}Qdrant backup not found: $backup_file${NC}"
        return 1
    fi

    echo -e "${YELLOW}Restoring Qdrant from: $full_path${NC}"

    # Check container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER}$"; then
        echo -e "${RED}Qdrant container not running${NC}"
        return 1
    fi

    # Decompress backup
    local temp_dir="/tmp/restore_qdrant_temp"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"

    echo -e "${YELLOW}Decompressing backup...${NC}"
    tar -xzf "$full_path" -C "$temp_dir"

    # Find the storage directory in the extracted backup
    local storage_dir=$(find "$temp_dir" -type d -name "storage_*" | head -1)
    if [[ -z "$storage_dir" ]]; then
        echo -e "${RED}Invalid Qdrant backup format${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    # Stop Qdrant
    echo -e "${YELLOW}Stopping Qdrant...${NC}"
    docker stop "${QDRANT_CONTAINER}"

    # Replace storage
    docker cp "${storage_dir}/." "${QDRANT_CONTAINER}:/qdrant/storage/"

    # Restart Qdrant
    docker start "${QDRANT_CONTAINER}"

    # Wait for Qdrant to be ready
    sleep 5

    QDRANT_PORT="${QDRANT_PORT:-6337}"
    if curl -s "http://localhost:${QDRANT_PORT}/health" | grep -q "ok\|healthy"; then
        echo -e "${GREEN}Qdrant restored successfully${NC}"
        rm -rf "$temp_dir"
        return 0
    else
        echo -e "${RED}Qdrant restore failed${NC}"
        rm -rf "$temp_dir"
        return 1
    fi
}

# Parse arguments
POSTGRES_BACKUP=""
REDIS_BACKUP=""
QDRANT_BACKUP=""
RESTORE_ALL=false

if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--postgres)
            POSTGRES_BACKUP="$2"
            shift 2
            ;;
        -r|--redis)
            REDIS_BACKUP="$2"
            shift 2
            ;;
        -q|--qdrant)
            QDRANT_BACKUP="$2"
            shift 2
            ;;
        -a|--all)
            RESTORE_ALL=true
            shift
            ;;
        -l|--list)
            list_backups
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            # Assume it's a postgres backup for backward compatibility
            POSTGRES_BACKUP="$1"
            shift
            ;;
    esac
done

# Confirmation
echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database(s)!${NC}"
echo ""
if [[ -n "$POSTGRES_BACKUP" ]] || [[ "$RESTORE_ALL" == true ]]; then
    echo "  PostgreSQL: ${POSTGRES_BACKUP:-latest.sql.gz}"
fi
if [[ -n "$REDIS_BACKUP" ]] || [[ "$RESTORE_ALL" == true ]]; then
    echo "  Redis: ${REDIS_BACKUP:-latest.rdb.gz}"
fi
if [[ -n "$QDRANT_BACKUP" ]] || [[ "$RESTORE_ALL" == true ]]; then
    echo "  Qdrant: ${QDRANT_BACKUP:-latest.tar.gz}"
fi
echo ""
read -p "Are you sure you want to proceed? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Perform restores
EXIT_CODE=0

if [[ "$RESTORE_ALL" == true ]]; then
    POSTGRES_BACKUP="${POSTGRES_BACKUP:-latest.sql.gz}"
    REDIS_BACKUP="${REDIS_BACKUP:-latest.rdb.gz}"
    QDRANT_BACKUP="${QDRANT_BACKUP:-latest.tar.gz}"
fi

if [[ -n "$POSTGRES_BACKUP" ]]; then
    restore_postgres "$POSTGRES_BACKUP" || EXIT_CODE=1
fi

if [[ -n "$REDIS_BACKUP" ]]; then
    restore_redis "$REDIS_BACKUP" || EXIT_CODE=1
fi

if [[ -n "$QDRANT_BACKUP" ]]; then
    restore_qdrant "$QDRANT_BACKUP" || EXIT_CODE=1
fi

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Restore process completed successfully${NC}"
    logger -t cc-lite "Database restore completed"
else
    echo -e "${YELLOW}⚠️  Restore completed with some failures${NC}"
    logger -t cc-lite "Database restore completed with failures"
fi

exit $EXIT_CODE
