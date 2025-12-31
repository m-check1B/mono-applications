# HW-002: Linear Sync Path Configuration Error (BLOCKING)

## Issue
Linear sync service fails due to incorrect data path configuration.

## Symptoms
```
2025-12-24T17:44:02: 17:44:02 [LINEAR] Sync error: [Errno 2] No such file or directory: '/home/adminmatej/github/ai-automation/kraliki/data/linear.json.tmp'
```

Repeats every minute since 17:44.

## Root Cause
Linear sync service is configured to use path `/home/adminmatej/github/ai-automation/kraliki/data/`
Actual data path is `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/data/`

## Impact
- Linear data is stale (synced at 2025-12-24T15:38:00Z)
- Cannot determine exact count of pending tasks
- Orchestrator makes decisions based on outdated task information
- 31 GIN tasks shown as pending in stale data

## Priority
**HIGH** - Affects orchestrator decision accuracy

## Files to Fix
- `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/integrations/linear-sync.py` - Update path
- Any config files that define `data_dir` path

## Opened
2025-12-24T18:04:00Z
