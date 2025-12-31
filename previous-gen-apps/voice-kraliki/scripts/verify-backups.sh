#!/bin/bash
# Backup Verification Script for CC-Lite 2026 (Voice by Kraliki)
# Verifies backup integrity and reports status
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

# Configuration
MAX_AGE_HOURS="${MAX_AGE_HOURS:-25}"  # Alert if backup is older than 25 hours

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_backup_exists() {
    local backup_type="$1"
    local pattern="$2"
    local dir="${BACKUP_DIR}/${backup_type}"

    if [[ ! -d "$dir" ]]; then
        echo "MISSING"
        return
    fi

    local latest=$(ls -t "$dir"/${pattern} 2>/dev/null | head -1)
    if [[ -z "$latest" ]]; then
        echo "MISSING"
    else
        echo "$latest"
    fi
}

check_backup_age() {
    local backup_file="$1"

    if [[ ! -f "$backup_file" ]]; then
        echo "N/A"
        return
    fi

    local file_time=$(stat -c %Y "$backup_file" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local age_seconds=$((current_time - file_time))
    local age_hours=$((age_seconds / 3600))

    echo "$age_hours"
}

check_backup_size() {
    local backup_file="$1"

    if [[ ! -f "$backup_file" ]]; then
        echo "0"
        return
    fi

    local size=$(stat -c %s "$backup_file" 2>/dev/null || echo "0")
    echo "$size"
}

human_size() {
    local bytes="$1"
    if [[ $bytes -ge 1073741824 ]]; then
        echo "$(echo "scale=2; $bytes/1073741824" | bc)G"
    elif [[ $bytes -ge 1048576 ]]; then
        echo "$(echo "scale=2; $bytes/1048576" | bc)M"
    elif [[ $bytes -ge 1024 ]]; then
        echo "$(echo "scale=2; $bytes/1024" | bc)K"
    else
        echo "${bytes}B"
    fi
}

verify_gz_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "MISSING"
        return
    fi

    if gzip -t "$file" 2>/dev/null; then
        echo "OK"
    else
        echo "CORRUPT"
    fi
}

# Main verification
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CC-Lite Backup Verification Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
log "Starting backup verification"
echo ""

ISSUES=0
WARNINGS=0

# Check PostgreSQL backups
echo -e "${YELLOW}PostgreSQL Backups:${NC}"
PG_LATEST=$(check_backup_exists "postgresql" "postgres_backup_*.sql.gz")
if [[ "$PG_LATEST" == "MISSING" ]]; then
    echo -e "  Latest:    ${RED}NO BACKUPS FOUND${NC}"
    ((ISSUES++))
else
    PG_AGE=$(check_backup_age "$PG_LATEST")
    PG_SIZE=$(check_backup_size "$PG_LATEST")
    PG_INTEGRITY=$(verify_gz_file "$PG_LATEST")

    echo "  Latest:    $(basename "$PG_LATEST")"
    echo "  Size:      $(human_size $PG_SIZE)"

    if [[ "$PG_AGE" -gt "$MAX_AGE_HOURS" ]]; then
        echo -e "  Age:       ${RED}${PG_AGE}h (TOO OLD)${NC}"
        ((WARNINGS++))
    else
        echo -e "  Age:       ${GREEN}${PG_AGE}h${NC}"
    fi

    if [[ "$PG_INTEGRITY" == "OK" ]]; then
        echo -e "  Integrity: ${GREEN}OK${NC}"
    else
        echo -e "  Integrity: ${RED}${PG_INTEGRITY}${NC}"
        ((ISSUES++))
    fi

    if [[ $PG_SIZE -lt 1024 ]]; then
        echo -e "  Warning:   ${YELLOW}Backup seems too small${NC}"
        ((WARNINGS++))
    fi
fi
echo ""

# Check Redis backups
echo -e "${YELLOW}Redis Backups:${NC}"
REDIS_LATEST=$(check_backup_exists "redis" "redis_backup_*.rdb.gz")
if [[ "$REDIS_LATEST" == "MISSING" ]]; then
    echo -e "  Latest:    ${YELLOW}NO BACKUPS FOUND (may be optional)${NC}"
else
    REDIS_AGE=$(check_backup_age "$REDIS_LATEST")
    REDIS_SIZE=$(check_backup_size "$REDIS_LATEST")
    REDIS_INTEGRITY=$(verify_gz_file "$REDIS_LATEST")

    echo "  Latest:    $(basename "$REDIS_LATEST")"
    echo "  Size:      $(human_size $REDIS_SIZE)"

    if [[ "$REDIS_AGE" -gt "$MAX_AGE_HOURS" ]]; then
        echo -e "  Age:       ${YELLOW}${REDIS_AGE}h${NC}"
        ((WARNINGS++))
    else
        echo -e "  Age:       ${GREEN}${REDIS_AGE}h${NC}"
    fi

    if [[ "$REDIS_INTEGRITY" == "OK" ]]; then
        echo -e "  Integrity: ${GREEN}OK${NC}"
    else
        echo -e "  Integrity: ${RED}${REDIS_INTEGRITY}${NC}"
        ((ISSUES++))
    fi
fi
echo ""

# Check Qdrant backups
echo -e "${YELLOW}Qdrant Backups:${NC}"
QDRANT_LATEST=$(check_backup_exists "qdrant" "qdrant_backup_*.tar.gz")
if [[ "$QDRANT_LATEST" == "MISSING" ]]; then
    echo -e "  Latest:    ${YELLOW}NO BACKUPS FOUND (may be optional)${NC}"
else
    QDRANT_AGE=$(check_backup_age "$QDRANT_LATEST")
    QDRANT_SIZE=$(check_backup_size "$QDRANT_LATEST")
    QDRANT_INTEGRITY=$(verify_gz_file "$QDRANT_LATEST")

    echo "  Latest:    $(basename "$QDRANT_LATEST")"
    echo "  Size:      $(human_size $QDRANT_SIZE)"

    if [[ "$QDRANT_AGE" -gt "$MAX_AGE_HOURS" ]]; then
        echo -e "  Age:       ${YELLOW}${QDRANT_AGE}h${NC}"
        ((WARNINGS++))
    else
        echo -e "  Age:       ${GREEN}${QDRANT_AGE}h${NC}"
    fi

    if [[ "$QDRANT_INTEGRITY" == "OK" ]]; then
        echo -e "  Integrity: ${GREEN}OK${NC}"
    else
        echo -e "  Integrity: ${RED}${QDRANT_INTEGRITY}${NC}"
        ((ISSUES++))
    fi
fi
echo ""

# Backup disk usage
echo -e "${YELLOW}Disk Usage:${NC}"
if [[ -d "$BACKUP_DIR" ]]; then
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    echo "  Total backup size: $TOTAL_SIZE"

    PG_COUNT=$(ls -1 "${BACKUP_DIR}/postgresql"/*.gz 2>/dev/null | wc -l || echo "0")
    REDIS_COUNT=$(ls -1 "${BACKUP_DIR}/redis"/*.gz 2>/dev/null | wc -l || echo "0")
    QDRANT_COUNT=$(ls -1 "${BACKUP_DIR}/qdrant"/*.gz 2>/dev/null | wc -l || echo "0")

    echo "  PostgreSQL backups: $PG_COUNT"
    echo "  Redis backups: $REDIS_COUNT"
    echo "  Qdrant backups: $QDRANT_COUNT"
else
    echo -e "  ${RED}Backup directory not found: ${BACKUP_DIR}${NC}"
    ((ISSUES++))
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [[ $ISSUES -eq 0 && $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}All backups are healthy!${NC}"
    exit 0
elif [[ $ISSUES -eq 0 ]]; then
    echo -e "${YELLOW}Backups are functional with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}Found $ISSUES critical issue(s) and $WARNINGS warning(s)${NC}"
    exit 1
fi
