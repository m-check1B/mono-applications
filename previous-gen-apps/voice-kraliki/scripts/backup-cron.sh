#!/bin/bash
# Backup Cron Setup Script for CC-Lite 2026 (Voice by Kraliki)
# Sets up automated backup schedules
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

show_usage() {
    echo -e "${BLUE}CC-Lite Backup Cron Setup${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [command]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  install     Install cron jobs for automated backups"
    echo "  uninstall   Remove CC-Lite backup cron jobs"
    echo "  status      Show current backup cron jobs"
    echo "  test        Run a test backup now"
    echo ""
    echo -e "${YELLOW}Schedule:${NC}"
    echo "  Daily backup:   02:00 AM (production backup)"
    echo "  Weekly backup:  Sunday 03:00 AM (full backup with verification)"
    echo "  Verification:   06:00 AM (check backup integrity)"
    echo ""
}

install_cron() {
    echo -e "${YELLOW}Installing CC-Lite backup cron jobs...${NC}"

    # Create a temporary crontab file
    local TEMP_CRON=$(mktemp)

    # Get current crontab (excluding our entries)
    crontab -l 2>/dev/null | grep -v "cc-lite.*backup" > "$TEMP_CRON" || true

    # Add new cron entries
    cat >> "$TEMP_CRON" << EOF

# CC-Lite Backup Jobs (added by backup-cron.sh)
# Daily production backup at 2:00 AM
0 2 * * * cd ${PROJECT_DIR} && ${SCRIPT_DIR}/backup-production.sh >> ${PROJECT_DIR}/backups/logs/cron.log 2>&1

# Weekly full backup verification on Sundays at 3:00 AM
0 3 * * 0 cd ${PROJECT_DIR} && ${SCRIPT_DIR}/verify-backups.sh >> ${PROJECT_DIR}/backups/logs/cron.log 2>&1

# Daily backup verification at 6:00 AM
0 6 * * * cd ${PROJECT_DIR} && ${SCRIPT_DIR}/verify-backups.sh --quiet >> ${PROJECT_DIR}/backups/logs/cron.log 2>&1

EOF

    # Install the new crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"

    # Create log directory
    mkdir -p "${PROJECT_DIR}/backups/logs"

    echo -e "${GREEN}Cron jobs installed successfully!${NC}"
    echo ""
    echo "Scheduled jobs:"
    crontab -l | grep -A1 "cc-lite" | grep -v "^--$"
    echo ""
}

uninstall_cron() {
    echo -e "${YELLOW}Removing CC-Lite backup cron jobs...${NC}"

    # Get current crontab (excluding our entries)
    local TEMP_CRON=$(mktemp)
    crontab -l 2>/dev/null | grep -v "cc-lite\|CC-Lite" | grep -v "backup-production.sh\|verify-backups.sh" > "$TEMP_CRON" || true

    # Remove empty lines at the end
    sed -i '/^$/N;/^\n$/d' "$TEMP_CRON"

    # Install the cleaned crontab
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"

    echo -e "${GREEN}Cron jobs removed successfully!${NC}"
}

show_status() {
    echo -e "${BLUE}Current CC-Lite Backup Cron Jobs:${NC}"
    echo ""

    local JOBS=$(crontab -l 2>/dev/null | grep -E "cc-lite|CC-Lite|backup-production|verify-backups" || true)

    if [[ -z "$JOBS" ]]; then
        echo -e "${YELLOW}No CC-Lite backup cron jobs found${NC}"
        echo ""
        echo "Run '$0 install' to set up automated backups"
    else
        echo "$JOBS"
        echo ""
        echo -e "${GREEN}Cron jobs are active${NC}"
    fi
    echo ""

    # Show recent log entries if available
    local LOG_FILE="${PROJECT_DIR}/backups/logs/cron.log"
    if [[ -f "$LOG_FILE" ]]; then
        echo -e "${BLUE}Recent backup log entries:${NC}"
        tail -20 "$LOG_FILE" 2>/dev/null || echo "No log entries yet"
    fi
}

test_backup() {
    echo -e "${YELLOW}Running test backup...${NC}"
    echo ""

    # Run backup
    "${SCRIPT_DIR}/backup-production.sh"

    echo ""
    echo -e "${YELLOW}Running verification...${NC}"
    echo ""

    # Run verification
    "${SCRIPT_DIR}/verify-backups.sh"
}

# Make scripts executable
chmod +x "${SCRIPT_DIR}/backup-production.sh" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/verify-backups.sh" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/restore-db.sh" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/backup-db.sh" 2>/dev/null || true

# Parse command
case "${1:-}" in
    install)
        install_cron
        ;;
    uninstall)
        uninstall_cron
        ;;
    status)
        show_status
        ;;
    test)
        test_backup
        ;;
    *)
        show_usage
        exit 0
        ;;
esac
