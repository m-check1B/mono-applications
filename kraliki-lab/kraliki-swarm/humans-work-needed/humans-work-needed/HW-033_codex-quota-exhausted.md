# HW-033: Codex Monthly Quota Exhausted

**Priority:** LOW (waiting for auto-reset)
**Created:** 2025-12-24
**Resets:** Dec 26, 2025 at 8:36 PM (switched to new account)

## Problem

Codex CLI (OpenAI) has hit its monthly usage limit:
```
error: usage_limit_reached
plan_type: plus
resets_at: Dec 29th, 2025 10:15 PM
```

This is a hard monthly cap, not a temporary rate limit.

## Impact

- Codex agents cannot run until Dec 29
- CX-* genomes (builder, patcher, orchestrator) are blocked
- Other CLIs (Claude, OpenCode) are still working

## Options

| Option | Cost | Time |
|--------|------|------|
| Wait for reset | Free | 5 days (Dec 29) |
| Upgrade to Pro | ~$20/month more | Immediate |
| Buy extra credits | Variable | Immediate |

**Links:**
- Pricing: https://openai.com/chatgpt/pricing
- Usage: https://chatgpt.com/codex/settings/usage

## Recommendation

**Wait for reset.** Claude and OpenCode are sufficient for current workload.
Codex was a nice-to-have parallel stream, not critical path.

## Circuit Breaker

The Kraliki circuit breaker correctly detected this and blocked Codex spawning.
No action needed - it will auto-retry after Dec 29.
