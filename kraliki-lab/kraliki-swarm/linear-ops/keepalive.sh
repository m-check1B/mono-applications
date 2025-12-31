#!/bin/bash
# GIN Keepalive - ensures orchestrator and dashboard are running
set -euo pipefail

GIN_DIR="/home/adminmatej/github/ai-automation/gin"
LOG_DIR="/home/adminmatej/github/logs/agents"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if PM2 process is running
check_pm2_process() {
    local name=$1
    pm2 show "$name" 2>/dev/null | grep -q "status.*online"
}

# Start PM2 process if not running
ensure_running() {
    local name=$1
    if ! check_pm2_process "$name"; then
        log "Starting $name..."
        pm2 start "$GIN_DIR/ecosystem.config.js" --only "$name" 2>/dev/null || true
    fi
}

# Main keepalive logic
log "GIN Keepalive check"

# Ensure critical processes are running
ensure_running "orchestrator-unified"
ensure_running "gin-dashboard"

# Update heartbeat
echo "$(date +%s)" > /tmp/gin-keepalive.heartbeat

log "Keepalive complete"
