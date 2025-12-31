---
name: audience-adapt
description: Adapt message tone and style for different audiences
category: communication
source: OpenAI Academy
---

# Adapt Message for Audience

Reframe communication to match the expectations of executives, peers, or customers.

## Prompt Template

```
Reframe this message for [audience type: executives, peers, or customers]. The message was originally written for [context]. Adjust tone, word choice, and style to fit the intended audience. Text: [paste text].
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[audience type]` | Target audience category | "executives", "peers", "customers" |
| `[context]` | Original audience or setting | "internal engineering team", "technical documentation" |
| `[paste text]` | The message to adapt | Technical update, project status, etc. |

## Example Usage

**Input:**
```
Reframe this message for executives. The message was originally written for the engineering team. Adjust tone, word choice, and style to fit the intended audience. Text: "We fixed the race condition in the async job processor that was causing duplicate entries in the database. The hotfix is deployed and we're monitoring the logs."
```

**Output:**
```
We identified and resolved a technical issue that was causing duplicate data entries. The fix is now live and we are actively monitoring to ensure stability.
```

## Audience Guidelines

| Audience | Style Notes |
|----------|-------------|
| Executives | High-level impact, business outcomes, minimal jargon |
| Peers | Technical depth, collaborative tone, shared context |
| Customers | Friendly, reassuring, focus on their experience |

## When to Use

- Escalating issues to leadership
- Communicating technical changes to non-technical stakeholders
- Converting internal updates to customer-facing messages
- Preparing the same news for different departments
