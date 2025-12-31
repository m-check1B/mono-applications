---
name: weekly-plan
description: Build balanced weekly work plans with priorities
category: productivity
source: OpenAI Academy
---

# Create Weekly Plan

Design a balanced week that accounts for deadlines, meetings, and focus time.

## Prompt Template

```
Build a weekly work plan for [describe role or situation]. The week includes deadlines, meetings, and individual focus time. Provide a balanced schedule with recommended priorities.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe role or situation]` | Context for the week | "a senior engineer with 3 days of meetings", "a product manager launching a feature" |

## Example Usage

**Input:**
```
Build a weekly work plan for a senior engineer who needs to complete a feature by Friday, has code reviews to do, a design doc to write, and has meetings on Tuesday and Thursday afternoons. The week includes deadlines, meetings, and individual focus time. Provide a balanced schedule with recommended priorities.
```

**Output:**
```
WEEKLY WORK PLAN: Senior Engineer

WEEK OVERVIEW:
- Primary Goal: Complete feature by Friday
- Secondary: Design doc, code reviews
- Constraints: Meetings Tue/Thu afternoons

---

MONDAY
Morning (4 hrs focus)
- Feature development: Core implementation
- Goal: 40% of feature complete
Afternoon (4 hrs focus)
- Continue feature development
- Code review (1 hour block)

TUESDAY
Morning (4 hrs focus)
- Feature development: Edge cases and testing
- Goal: 65% complete
Afternoon (meetings)
- Team meetings and collaboration
- Quick code reviews between meetings

WEDNESDAY
Morning (4 hrs focus)
- Complete feature implementation
- Goal: 90% complete, ready for review
Afternoon (4 hrs focus)
- Start design doc outline
- Self-review of feature code

THURSDAY
Morning (4 hrs focus)
- Design doc: First draft complete
- Address any feature PR feedback
Afternoon (meetings)
- Team meetings
- Async: Respond to design doc comments

FRIDAY
Morning (3 hrs)
- Feature: Final polish and merge
- Design doc: Incorporate feedback
Afternoon (3 hrs)
- Code reviews backlog
- Week wrap-up and planning

---

TIME ALLOCATION:
- Feature development: 16 hours (50%)
- Design doc: 6 hours (19%)
- Code reviews: 4 hours (12%)
- Meetings: 6 hours (19%)

BUFFER: 2 hours built into Friday for overflow

SUCCESS CRITERIA:
- [ ] Feature merged to main by Friday 3pm
- [ ] Design doc v1 shared for review
- [ ] No code reviews older than 24 hours
```

## When to Use

- Sunday evening or Monday morning planning
- Before busy weeks with multiple deadlines
- When taking on a new project or responsibility
- Returning from vacation to get oriented
