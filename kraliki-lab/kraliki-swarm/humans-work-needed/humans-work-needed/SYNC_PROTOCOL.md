# Sync Protocol: Server ↔ Mac

## Repository

**GitHub:** https://github.com/m-check1B/humans-work-needed
**Branches:** `main` (stable), `develop` (default, active work)

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                                │
│            (humans-work-needed repo)                        │
└─────────────────────────────────────────────────────────────┘
              ▲                              ▲
              │ push                         │ push
              │                              │
┌─────────────┴───────────┐    ┌────────────┴────────────────┐
│     DEV SERVER          │    │           MAC               │
│    (5.9.38.218)         │    │    (Claude Desktop)         │
├─────────────────────────┤    ├─────────────────────────────┤
│ • Creates new HW-XXX    │    │ • Executes tasks            │
│ • Updates QUEUE_STATUS  │    │ • Updates HW-XXX files      │
│ • Reads completed tasks │    │ • Pushes after each task    │
│ • Updates features.json │    │                             │
└─────────────────────────┘    └─────────────────────────────┘
```

## Server Side

### Create new tasks
When blocked by human action:
1. Create `HW-XXX_description.md` with instructions
2. Update `QUEUE_STATUS.md`
3. Commit and push:
```bash
cd /home/adminmatej/github/ai-automation/humans-work-needed
git add -A && git commit -m "Add HW-XXX: description" && git push
```

### Check for completed tasks
```bash
cd /home/adminmatej/github/ai-automation/humans-work-needed
git pull

# Check QUEUE_STATUS.md for newly completed items
# Update features.json to unblock features
```

## Mac Side

### Setup (one time)
```bash
git clone git@github.com:m-check1B/humans-work-needed.git
cd humans-work-needed
git checkout develop
```

### Before starting session
```bash
cd ~/humans-work-needed
git pull
```

### After each completed task
1. Update the HW-XXX markdown file (set Status to DONE, add results)
2. Update QUEUE_STATUS.md
3. Commit and push:
```bash
git add -A
git commit -m "Completed HW-XXX: <task name>"
git push
```

## Status Values

In HW-XXX files and QUEUE_STATUS.md:
- `PENDING` - Not started
- `IN PROGRESS` - Mac agent working on it
- `DONE` - Completed
- `BLOCKED` - Needs additional human help
- `NOT NEEDED` - Deferred or obsolete

## Conflict Resolution

- Both sides always pull before pushing
- In case of conflict: Mac version wins (has latest execution state)
- Use short commits to minimize conflicts
