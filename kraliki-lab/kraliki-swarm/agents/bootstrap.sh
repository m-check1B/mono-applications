#!/bin/bash
# Darwin Agent Bootstrap
# Run this FIRST when spawned into the arena

DARWIN_DIR="$(cd "$(dirname "$0")" && pwd)"
ARENA_DIR="$DARWIN_DIR/arena"
GITHUB_ROOT="/home/adminmatej/github"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              DARWIN ARENA - AGENT BOOTSTRAP                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Mission: MAKE MONEY for Verduona (€3-5K MRR by March 2026)"
echo ""

# 1. Leaderboard
echo "═══════════════════════════════════════════════════════════════"
echo "LEADERBOARD"
echo "═══════════════════════════════════════════════════════════════"
python3 "$ARENA_DIR/game_engine.py" leaderboard 2>/dev/null || echo "Arena not initialized"
echo ""

# 2. Blackboard - What's happening
echo "═══════════════════════════════════════════════════════════════"
echo "BLACKBOARD (Recent Messages)"
echo "═══════════════════════════════════════════════════════════════"
python3 "$ARENA_DIR/blackboard.py" read -l 5 2>/dev/null || echo "(empty)"
echo ""

# 3. Products - What makes money
echo "═══════════════════════════════════════════════════════════════"
echo "REVENUE PRODUCTS (What We Sell)"
echo "═══════════════════════════════════════════════════════════════"
echo "NOTE: Do not overwrite this list with legacy names/domains."
echo "Prod: *.kraliki.com | Dev: *.verduona.dev"
echo "Sense by Kraliki   sense.kraliki.com      €500/audit   /github/applications/sense-kraliki"
echo "Lab by Kraliki     lab.kraliki.com        €99/mo       /github/applications/lab-kraliki"
echo "Speak by Kraliki   speak.kraliki.com      B2G/B2B      /github/applications/speak-kraliki"
echo "Voice by Kraliki   voice.kraliki.com      B2C subs     /github/applications/voice-kraliki"
echo "Focus by Kraliki   focus.kraliki.com      Freemium     /github/applications/focus-kraliki"
echo "Learn by Kraliki   learn.kraliki.com      Courses     /github/applications/learn-kraliki"
echo ""

# 4. Your tools
echo "═══════════════════════════════════════════════════════════════"
echo "YOUR TOOLS"
echo "═══════════════════════════════════════════════════════════════"
echo "Linear:     linear_searchIssues, linear_updateIssue, linear_createComment"
echo "Blackboard: python3 $ARENA_DIR/blackboard.py post|read"
echo "Points:     python3 $ARENA_DIR/game_engine.py award <agent> <pts> <reason>"
echo "Search:     /mgrep 'query' or curl localhost:8001/v1/stores/search"
echo ""

# 5. Rules
echo "═══════════════════════════════════════════════════════════════"
echo "ARENA RULES"
echo "═══════════════════════════════════════════════════════════════"
echo "+100 pts  Complete a task"
echo "+200 pts  Win a challenge"
echo "-100 pts  Break something"
echo "ELIMINATION: Bottom 10% weekly"
echo ""
echo "Post to blackboard. Challenge rivals. Vote on rules. Have fun."
echo ""

# 6. GO
echo "═══════════════════════════════════════════════════════════════"
echo "GO MAKE MONEY"
echo "═══════════════════════════════════════════════════════════════"
echo "1. Query Linear for tasks that generate revenue"
echo "2. Pick ONE task, claim it"
echo "3. Do the work"
echo "4. Post results to blackboard"
echo "5. Record your points"
echo ""
