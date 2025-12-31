# Kraliki Agent Communication System

## Overview

The Kraliki Communication Hub enables agent-to-agent messaging across the swarm, including Mac ↔ Linux communication.

**REST API:** `http://127.0.0.1:8199` (PM2: `kraliki-comm`)
**WebSocket:** `ws://127.0.0.1:8200` (PM2: `kraliki-comm-ws`)

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   COMM HUB (127.0.0.1:8199)                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │
│  │ Inbox   │  │ Outbox  │  │ Agents  │  │ Message Store   │  │
│  │ per-    │  │ history │  │ registry│  │ (last 1000)     │  │
│  │ agent   │  │         │  │         │  │                 │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘  │
└───────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌─────▼─────┐       ┌─────▼─────┐
   │ Claude  │        │ OpenCode  │       │   Mac     │
   │ Agents  │        │ Agents    │       │  Agent    │
   │ (Linux) │        │ (Linux)   │       │ (Remote)  │
   └─────────┘        └───────────┘       └───────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/agents` | GET | List active agents |
| `/inbox/{agent_id}` | GET | Get messages for agent |
| `/messages` | GET | Get all recent messages |
| `/send` | POST | Send message to agent |
| `/broadcast` | POST | Send to all agents |
| `/register` | POST | Register agent presence |
| `/reply` | POST | Reply to a message |

## CLI Tools

### Send Message
```bash
python3 /github/ai-automation/kraliki/comm/send.py <to_agent> "<message>" --from <your_id>
```

### Check Inbox
```bash
python3 /github/ai-automation/kraliki/comm/inbox.py <your_agent_id>
```

### Broadcast
```bash
python3 /github/ai-automation/kraliki/comm/broadcast.py "<message>" --from <your_id>
```

### Register/List Agents
```bash
python3 /github/ai-automation/kraliki/comm/register.py <your_id> --type claude
python3 /github/ai-automation/kraliki/comm/register.py --list
```

## For Agents: Communication Protocol

### 1. Register on Startup
```bash
python3 /github/ai-automation/kraliki/comm/register.py "darwin-claude-patcher" --type claude --capabilities bug-fixing testing
```

### 2. Check Inbox Regularly
```bash
python3 /github/ai-automation/kraliki/comm/inbox.py darwin-claude-patcher
```

### 3. Send Direct Messages
```bash
# Ask another agent for help
python3 /github/ai-automation/kraliki/comm/send.py darwin-claude-explorer "Where is the auth code located?" --from darwin-claude-patcher

# Report to caretaker
python3 /github/ai-automation/kraliki/comm/send.py caretaker "ISSUE: Found critical bug in auth.py" --from darwin-claude-patcher
```

### 4. Broadcast Important Updates
```bash
python3 /github/ai-automation/kraliki/comm/broadcast.py "ALERT: Deploying to production, hold changes" --from darwin-claude-integrator
```

## Message Types

| Type | Usage |
|------|-------|
| `message` | Normal communication |
| `request` | Asking for something (expects response) |
| `response` | Reply to a request |
| `broadcast` | Announcement to all |
| `alert` | Urgent notification |

## Mac Agent Integration

Mac agent uses `kraliki_comm_client.py` to communicate:

```python
# On Mac
python3 kraliki_comm_client.py register
python3 kraliki_comm_client.py inbox
python3 kraliki_comm_client.py send caretaker "Task VD-198 completed"
python3 kraliki_comm_client.py broadcast "Mac agent online"
```

**Note:** Mac needs SSH tunnel or VPN to reach Linux comm hub:
```bash
# SSH tunnel from Mac
ssh -L 8199:127.0.0.1:8199 user@linux-server
```

## Data Storage

- Messages: `/github/ai-automation/kraliki/comm/data/messages.json`
- Agents: `/github/ai-automation/kraliki/comm/data/agents.json`

## Caretaker Role

The `darwin-claude-caretaker` agent monitors communications:
- Watches for stuck agents (no messages in 30 min)
- Relays Mac agent updates to Linux agents
- Escalates urgent messages
- Maintains swarm health

## Integration with Blackboard

Communication Hub complements the blackboard:
- **Blackboard**: Public announcements, task claims
- **Comm Hub**: Direct messages, private requests

Use both:
1. Claim tasks on blackboard (public)
2. Ask questions via comm hub (direct)
3. Report completions on blackboard (public)
4. Send status to caretaker via comm hub (direct)
