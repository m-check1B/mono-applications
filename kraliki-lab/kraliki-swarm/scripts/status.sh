#!/bin/bash
# Darwin2 Status Script
# Quick overview of system state

DARWIN2_DIR="/home/adminmatej/github/ai-automation/darwin2"

echo "========================================"
echo "  DARWIN2 STATUS"
echo "  $(date)"
echo "========================================"
echo ""

# PM2 Status
echo "PM2 PROCESSES:"
echo "--------------"
pm2 list 2>/dev/null | grep darwin2 || echo "  (none running)"
echo ""

# Agent Count
echo "ACTIVE AGENTS:"
echo "--------------"
CLAUDE_COUNT=$(pgrep -f "claude.*darwin2" 2>/dev/null | wc -l)
OPENCODE_COUNT=$(pgrep -f "opencode.*darwin" 2>/dev/null | wc -l)
echo "  Claude: $CLAUDE_COUNT"
echo "  OpenCode: $OPENCODE_COUNT"
echo "  Total: $((CLAUDE_COUNT + OPENCODE_COUNT))"
echo ""

# Leaderboard
echo "LEADERBOARD:"
echo "--------------"
if [ -f "$DARWIN2_DIR/arena/game_engine.py" ]; then
    python3 "$DARWIN2_DIR/arena/game_engine.py" leaderboard 2>/dev/null | head -8 || echo "  (no data)"
fi
echo ""

# Recent Social
echo "RECENT SOCIAL:"
echo "--------------"
if [ -f "$DARWIN2_DIR/arena/social.py" ]; then
    python3 "$DARWIN2_DIR/arena/social.py" feed 2>/dev/null | head -5 || echo "  (no posts)"
fi
echo ""

echo "========================================"
