---
name: prep-questions
description: Generate thoughtful questions to prepare for a meeting
category: meetings
source: OpenAI Academy
---

# Meeting Prep Questions

Prepare insightful questions that demonstrate preparation and add value.

## Prompt Template

```
Suggest thoughtful questions to ask in a meeting about [topic]. The purpose of the meeting is [purpose]. Provide a list of at least 5 questions that show preparation and insight.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[topic]` | Meeting subject | "new vendor selection", "budget planning" |
| `[purpose]` | Goal of the meeting | "evaluate options", "make a decision", "gather feedback" |

## Example Usage

**Input:**
```
Suggest thoughtful questions to ask in a meeting about migrating to a new cloud provider. The purpose of the meeting is to evaluate the migration plan and timeline. Provide a list of at least 5 questions that show preparation and insight.
```

**Output:**
```
PREPARATION QUESTIONS FOR CLOUD MIGRATION MEETING

1. What is our rollback strategy if we encounter critical issues during migration?

2. How will we handle data synchronization between the old and new environments during the transition period?

3. What is the expected performance baseline, and how will we measure success post-migration?

4. Which teams have dependencies on services being migrated, and have they been consulted on the timeline?

5. What are the cost projections for running parallel environments during the migration window?

6. How does this migration timeline align with our product release schedule?

7. What security and compliance audits are required before we can move production workloads?
```

## When to Use

- Before strategy or planning meetings
- Preparing for vendor presentations
- Getting ready for project reviews
- Joining a meeting where you are expected to contribute
