---
name: email-summarize
description: Summarize long email threads into key points and action items
category: communication
source: OpenAI Academy
---

# Summarize Email Thread

Extract the essential information from lengthy email chains.

## Prompt Template

```
Summarize this email thread into a short recap. The thread includes several back-and-forth messages. Highlight key decisions, action items, and open questions. Email: [paste text].
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[paste text]` | The email thread to summarize | Full email chain with multiple replies |

## Example Usage

**Input:**
```
Summarize this email thread into a short recap. The thread includes several back-and-forth messages. Highlight key decisions, action items, and open questions. Email:

From: Alice
Subject: Re: API Rate Limits
We should increase the rate limit to 1000 requests per minute.

From: Bob
That might cause issues with our infrastructure. Can we do 500 first?

From: Alice
500 works as an initial step. We can monitor and adjust.

From: Carol
Agreed. Who will implement the change?

From: Bob
I can handle it. Need to know the timeline.

From: Alice
End of week would be ideal. Let me know if that's feasible.
```

**Output:**
```
Summary: Discussion about increasing API rate limits

Key Decisions:
- Initial rate limit increase to 500 requests/minute (compromise from original 1000)
- Will monitor performance and adjust as needed

Action Items:
- Bob: Implement rate limit change by end of week
- Team: Monitor infrastructure after deployment

Open Questions:
- Is end of week timeline feasible for Bob?
- What metrics will be used to decide on further increases?
```

## When to Use

- Catching up on threads you were added to late
- Preparing meeting context from prior discussions
- Creating documentation from email decisions
- Briefing stakeholders on conversation outcomes
