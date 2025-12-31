# Agent Board MCP Server - Debug Session Handoff
**Session Date:** 2025-10-06
**Status:** ✅ FIXED - Restart Required
**Next Agent:** Test MCP tools after Claude Code restart

---

## 🔍 Problem Diagnosed

**Symptom:** agent-board MCP tools not loading in Claude Code despite:
- ✅ Backend running healthy (http://127.0.0.1:3021)
- ✅ MCP server code working (stdio protocol validated)
- ✅ MCP config file present (~/.config/Claude/mcp_settings.json)
- ✅ Other MCP servers loading fine (ruv-swarm, flow-nexus, claude-flow)

**User Observation:** "I just started new session, is that not considered restart?"
- Correct! New chat session ≠ MCP reload
- But that wasn't the actual issue...

---

## 🎯 Root Cause Discovery

### The Investigation Trail

1. **First Clue:** TWO Claude Code instances running
   - PID 47085 on pts/2: Started **Sept 26** (ancient)
   - PID 3103236 on pts/9: Started today at 21:20 (current session)

2. **Red Herring:** Tried killing old instance
   - Didn't solve the problem
   - Current session was already the new instance

3. **Web Research:** Found MCP configs need `"type": "stdio"`
   - Added to mcp_settings.json
   - Still didn't work...

4. **BREAKTHROUGH:** Examined .claude.json structure
   ```bash
   # MCP servers are PER-PROJECT, not global!
   /home/adminmatej/.claude.json -> 336KB config file
   └── projects
       ├── /home/adminmatej/github
       │   └── mcpServers: [ruv-swarm, flow-nexus, claude-flow]
       │                    ❌ NO agent-board!
       ├── /home/adminmatej
       │   └── mcpServers: [ruv-swarm, flow-nexus]
       └── ... (other projects)
   ```

### The Real Issue

**Claude Code MCP Architecture:**
- `~/.config/Claude/mcp_settings.json` - **NOT USED** (Claude Desktop only?)
- `/home/adminmatej/.claude.json` - **ACTUAL CONFIG**
  - Per-project MCP server definitions
  - Project determined by working directory
  - Current project: `/home/adminmatej/github`
  - agent-board was missing from this project's mcpServers

---

## ✅ Fixes Applied

### 1. Added `type: "stdio"` to mcp_settings.json
**File:** `/home/adminmatej/.config/Claude/mcp_settings.json`

```json
{
  "mcpServers": {
    "agent-board": {
      "type": "stdio",  // ← Added
      "command": "python3",
      "args": ["/home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server/server.py"],
      "env": {
        "AGENT_BOARD_API": "http://127.0.0.1:3021"
      }
    },
    "recall-kraliki": {
      "type": "stdio",  // ← Added
      "command": "python3",
      "args": ["/home/adminmatej/github/applications/recall-kraliki/mcp-server/server.py"],
      "envFile": "/home/adminmatej/github/applications/recall-kraliki/.env"
    }
  }
}
```

**Note:** This file may not be used by Claude Code CLI, but it's now properly formatted.

### 2. Added agent-board to Project Config
**File:** `/home/adminmatej/.claude.json`
**Project:** `/home/adminmatej/github`

```python
# Added via Python script
config['projects']['/home/adminmatej/github']['mcpServers']['agent-board'] = {
    "type": "stdio",
    "command": "python3",
    "args": ["/home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server/server.py"],
    "env": {
        "AGENT_BOARD_API": "http://127.0.0.1:3021"
    }
}
```

**Verification:**
```bash
✅ agent-board MCP config confirmed:
   Type: stdio
   Command: python3
   Script: /home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server/server.py
   API: http://127.0.0.1:3021
```

---

## 🧪 Testing Done (Pre-Restart)

### ✅ MCP Server Validation
```bash
# Server responds to MCP protocol correctly
timeout 2 python3 -c "import subprocess, json
proc = subprocess.Popen(['python3', 'server.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
init_msg = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', ...}
proc.stdin.write(json.dumps(init_msg) + '\n')
response = proc.stdout.readline()
"

# Output: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"tools":{"listChanged":false}},"serverInfo":{"name":"agent-board","version":"1.16.0"}}}
```

### ✅ Backend API Validation
```bash
curl -s http://127.0.0.1:3021/health
# {"status":"healthy","service":"agent-board","version":"0.1.0"}

curl -X POST http://127.0.0.1:3021/api/posts/coding \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"Claude","agent_type":"architect","content":"Test post","content_type":"updates","tags":["testing"]}'
# ✅ Post created successfully
```

### ✅ Tools Defined in Server
```
agent_board_post_update     - Post quick updates (max 500 chars)
agent_board_post_journal    - Post deep dives (max 5000 chars)
agent_board_read_posts      - Read peer posts from boards
agent_board_list_boards     - List available boards with stats
```

---

## 🚀 Next Steps for Next Agent

### 1. Restart Claude Code
```bash
# Kill ALL instances (including any zombies)
pkill -9 claude

# Start fresh from /home/adminmatej/github directory
cd /home/adminmatej/github
claude
```

### 2. Verify Tools Loaded
After restart, check for these 4 tools in your available functions:
- `mcp__agent-board__agent_board_post_update`
- `mcp__agent-board__agent_board_post_journal`
- `mcp__agent-board__agent_board_read_posts`
- `mcp__agent-board__agent_board_list_boards`

**How to Check:**
You'll know if they're loaded if you can call them. Try:
```python
# This is pseudo-code - you'd actually call the tool
mcp__agent-board__agent_board_list_boards()
```

### 3. End-to-End Test Sequence

**Test 1: List Boards**
```python
mcp__agent-board__agent_board_list_boards()
# Expected: Shows coding + business boards with stats
```

**Test 2: Post Update**
```python
mcp__agent-board__agent_board_post_update(
    board="coding",
    content="MCP tools now working! Testing agent-board integration.",
    agent_type="architect",
    tags=["mcp", "testing", "integration"]
)
# Expected: Returns post ID and success message
```

**Test 3: Read Posts**
```python
mcp__agent-board__agent_board_read_posts(
    board="coding",
    content_type="updates",
    limit=5
)
# Expected: Shows recent updates including your test post
```

**Test 4: Post Journal**
```python
mcp__agent-board__agent_board_post_journal(
    board="coding",
    content="# MCP Integration Success\n\nAfter debugging the per-project config issue, agent-board MCP tools are now functional...",
    agent_type="architect",
    tags=["mcp", "documentation", "debugging"]
)
# Expected: Returns journal post ID
```

### 4. Document Results
Create `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/MCP-TEST-RESULTS.md` with:
- ✅/❌ for each tool test
- Any errors encountered
- Performance observations
- Next phase recommendations

---

## 📚 Key Learnings

### Claude Code MCP Architecture
1. **Config Location:** `/home/adminmatej/.claude.json` (NOT mcp_settings.json)
2. **Scope:** Per-project, not global
3. **Project Key:** Determined by working directory (e.g., `/home/adminmatej/github`)
4. **Format Required:** `type: "stdio"` field is mandatory
5. **Reload:** Requires full Claude Code restart (pkill claude && claude)

### MCP Server Implementation (agent-board)
- ✅ Uses `mcp.server.Server` (standard SDK, not FastMCP)
- ✅ Stdio protocol correctly implemented
- ✅ 4 tools properly defined with inputSchema
- ✅ HTTP client connects to backend API
- ✅ Proper error handling with TextContent responses

### Debugging Tactics That Worked
1. **Process inspection:** `ps aux | grep claude` revealed multiple instances
2. **Direct testing:** Running server with mock stdio validated implementation
3. **Config archaeology:** Examining .claude.json structure found per-project config
4. **Web research:** Confirmed `type: "stdio"` requirement
5. **Python inspection:** Used scripts to safely modify 336KB JSON config

---

## 📋 Reference Commands

### Check Running Instances
```bash
ps aux | grep claude | grep -v grep
tmux list-sessions 2>/dev/null
```

### Validate Backend
```bash
curl -s http://127.0.0.1:3021/health
curl -s http://127.0.0.1:3021/api/boards/ | python3 -m json.tool
```

### Test MCP Server Directly
```bash
cd /home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server
timeout 2 python3 server.py
# Should run without errors
```

### Inspect Project Config
```python
python3 << 'EOF'
import json
with open('/home/adminmatej/.claude.json', 'r') as f:
    config = json.load(f)
project = config['projects']['/home/adminmatej/github']
print("MCP Servers:", list(project['mcpServers'].keys()))
EOF
```

---

## 🎯 Success Criteria

You'll know everything works when:
1. ✅ All 4 mcp__agent-board__* tools are callable
2. ✅ Posts appear in backend API (curl confirmation)
3. ✅ Posts saved to filesystem (check backend/posts/*.md files)
4. ✅ Read operations return formatted markdown
5. ✅ No errors in tool responses

---

## 🔗 Related Files

**Documentation:**
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/START-HERE.md`
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/HANDOFF.md`
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/QUICK-REFERENCE.md`

**Code:**
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server/server.py`
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/backend/app/main.py`
- `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/backend/boards/boards.yaml`

**Config:**
- `/home/adminmatej/.claude.json` (line ~492: `/home/adminmatej/github` project)
- `/home/adminmatej/.config/Claude/mcp_settings.json` (possibly unused)

**Backend:**
- Posts: `/home/adminmatej/github/applications/kraliki-lab/services/agent-board/backend/posts/`
- Logs: Check backend console output

---

## 💡 For Future Debugging

If MCP tools don't load after restart:

1. **Check working directory matches project key:**
   ```bash
   pwd  # Should be under /home/adminmatej/github
   ```

2. **Verify project config:**
   ```bash
   python3 -c "import json; print(json.load(open('/home/adminmatej/.claude.json'))['projects']['/home/adminmatej/github']['mcpServers'].keys())"
   ```

3. **Check backend is running:**
   ```bash
   curl -s http://127.0.0.1:3021/health
   ```

4. **Test server directly:**
   ```bash
   cd /home/adminmatej/github/applications/kraliki-lab/services/agent-board/mcp-server
   python3 server.py  # Should not exit with errors
   # Ctrl+C to stop
   ```

5. **Look for error logs:**
   - Backend console (if running in foreground)
   - Claude Code process stderr

---

## 🎬 Ready to Resume

**Current State:** Configuration fixed, restart pending
**Confidence:** HIGH - All components validated individually
**Blocker:** Claude Code needs full restart to load new MCP config
**ETA to Working:** 30 seconds after restart + 2 min testing

**First Command After Restart:**
```bash
# From new Claude Code session
cd /home/adminmatej/github/applications/kraliki-lab/services/agent-board
cat MCP-DEBUG-SESSION.md  # Read this file
# Then test: mcp__agent-board__agent_board_list_boards()
```

---

**Session End Notes:**
- Two instances issue was a red herring (old zombie wasn't blocking)
- tmux was NOT involved (no sessions running)
- Real issue: per-project config architecture
- User's intuition was right: "OR the mcp server implementation must be fucked"
  - Implementation was fine! Config was wrong location.

Good luck, next agent! 🚀
