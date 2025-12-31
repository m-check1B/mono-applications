#!/bin/bash
# Darwin Morning Digest - Run when you wake up
# Shows overnight swarm activity summary

DARWIN_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DARWIN_DIR"

echo "☀️  DARWIN MORNING DIGEST"
echo "========================="
echo "Generated: $(date)"
echo ""

echo "📊 SWARM STATUS"
echo "---------------"
echo "OpenCode agents: $(opencode session list 2>/dev/null | grep -c Darwin || echo 0)"
echo "Memory files: $(ls arena/memories/*.jsonl 2>/dev/null | wc -l)"
echo ""

echo "🏆 LEADERBOARD"
echo "--------------"
python3 arena/game_engine.py leaderboard 2>/dev/null | head -7
echo ""

echo "📢 RECENT SOCIAL (last 10)"
echo "--------------------------"
python3 arena/social.py feed 10
echo ""

echo "🧠 MEMORIES STORED"
echo "------------------"
for f in arena/memories/*.jsonl; do
    if [ -f "$f" ]; then
        agent=$(basename "$f" .jsonl)
        count=$(wc -l < "$f")
        echo "  $agent: $count memories"
    fi
done
echo ""

echo "⭐ REPUTATION"
echo "-------------"
python3 arena/reputation.py leaderboard 2>/dev/null
echo ""

echo "📋 OVERNIGHT REPORT"
echo "-------------------"
if [ -f "logs/OVERNIGHT_REPORT_$(date +%Y%m%d).md" ]; then
    echo "Available at: logs/OVERNIGHT_REPORT_$(date +%Y%m%d).md"
else
    echo "No overnight report for today"
fi
echo ""

echo "🐕 WATCHDOG STATUS"
echo "------------------"
if tmux has-session -t darwin-night 2>/dev/null; then
    echo "✅ Watchdog running in tmux 'darwin-night'"
    tail -5 "logs/watchdog_$(date +%Y%m%d).log" 2>/dev/null || echo "(no log yet)"
else
    echo "⚠️ Watchdog not running. Start with: tmux attach -t darwin-night"
fi
echo ""

echo "💡 QUICK COMMANDS"
echo "-----------------"
echo "  View social: python3 arena/social.py feed"
echo "  Check leaderboard: python3 arena/game_engine.py leaderboard"
echo "  Spawn agent: ./spawn.sh gen_002_claude_patcher"
echo "  Attach watchdog: tmux attach -t darwin-night"
echo ""

echo "☀️ Good morning!"
