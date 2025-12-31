# Human Work Queue

**GitHub:** https://github.com/m-check1B/humans-work-needed

Tasks requiring human action. Syncs between dev server and Mac for Computer Use automation.

---

## Status: EMPTY

No human blockers. All features unblocked.

See `QUEUE_STATUS.md` for history.

---

## Usage

### When Agent Hits Blocker

1. Create `HW-XXX_description.md`
2. Update `QUEUE_STATUS.md`
3. `git push`

### Mac Pickup

```bash
git clone git@github.com:m-check1B/humans-work-needed.git
cd humans-work-needed
# Check QUEUE_STATUS.md for tasks
```

---

## Files

| File | Purpose |
|------|---------|
| `QUEUE_STATUS.md` | Current status |
| `MAC_AGENT_PROMPT.md` | Claude Desktop prompt |
| `SYNC_PROTOCOL.md` | Server-Mac sync |
| `archive/` | Completed tasks |
