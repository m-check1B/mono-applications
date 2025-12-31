---
name: priorities-daily
description: Create prioritized daily to-do lists from task lists
category: productivity
source: OpenAI Academy
---

# Document Daily Priorities

Organize and prioritize tasks for maximum daily productivity.

## Prompt Template

```
Create a prioritized to-do list from the following tasks: [paste tasks]. The context is a typical workday with limited time. Suggest which tasks should be done first and why.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[paste tasks]` | Raw list of tasks | Unorganized task list, backlog items |

## Example Usage

**Input:**
```
Create a prioritized to-do list from the following tasks:
- Review PR from teammate
- Write quarterly report (due Friday)
- Fix production bug affecting 5% of users
- Respond to client email from yesterday
- Update project documentation
- Prepare slides for Monday presentation
- Schedule 1:1 with new team member
The context is a typical workday with limited time. Suggest which tasks should be done first and why.
```

**Output:**
```
DAILY PRIORITY LIST

HIGH PRIORITY (Do First)
------------------------
1. Fix production bug affecting 5% of users
   Why: Active customer impact; every hour matters
   Time: 1-2 hours

2. Respond to client email from yesterday
   Why: Client waiting; delays damage relationship
   Time: 15-30 minutes

3. Review PR from teammate
   Why: Unblocks teammate's work; quick win
   Time: 30-45 minutes

MEDIUM PRIORITY (Schedule Today)
--------------------------------
4. Write quarterly report (due Friday)
   Why: Important but has runway; block 2 hours today
   Time: 2 hours (partial progress)

5. Schedule 1:1 with new team member
   Why: Quick calendar action; supports onboarding
   Time: 10 minutes

LOWER PRIORITY (If Time Permits)
--------------------------------
6. Prepare slides for Monday presentation
   Why: Due Monday; can do tomorrow if needed
   Time: 1-2 hours

7. Update project documentation
   Why: No deadline pressure; ongoing task
   Time: 30 minutes to 1 hour

RECOMMENDED DAILY FLOW:
Morning: Items 1-3 (high focus, clear blockers)
After lunch: Item 4 (deep work)
End of day: Items 5-6 (lighter tasks)
Item 7: Defer to tomorrow unless extra time
```

## When to Use

- Start of each workday
- When feeling overwhelmed by tasks
- After returning from time off
- Before weekly planning sessions
