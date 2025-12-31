---
name: brainstorm-solutions
description: Generate diverse solutions to workplace challenges
category: productivity
source: OpenAI Academy
---

# Brainstorm Solutions

Generate creative, varied approaches to solving problems.

## Prompt Template

```
Brainstorm potential solutions to the following workplace challenge: [describe challenge]. Provide at least 5 varied ideas, noting pros and cons for each.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe challenge]` | The problem to solve | "Low team morale after layoffs", "Technical debt slowing feature development" |

## Example Usage

**Input:**
```
Brainstorm potential solutions to the following workplace challenge: Our engineering team spends 40% of their time on support and maintenance, leaving insufficient time for new feature development. Provide at least 5 varied ideas, noting pros and cons for each.
```

**Output:**
```
BRAINSTORM: Reducing Engineering Support Burden

SOLUTION 1: Dedicated Support Rotation
Create a weekly rotation where 1-2 engineers handle all support, freeing others for deep work.

Pros:
- Protected focus time for most of the team
- Clear ownership of support issues
- Skills distribution across team

Cons:
- Rotation weeks are low-productivity for feature work
- May create knowledge silos if rotation is infrequent


SOLUTION 2: Tiered Support Escalation
Have customer success handle L1, create runbooks for L2, and only escalate L3 to engineering.

Pros:
- Reduces interrupt volume significantly
- Forces documentation improvement
- Scales better as company grows

Cons:
- Requires investment in training and documentation
- Initial setup takes 2-4 weeks


SOLUTION 3: Office Hours Model
Engineers available for support questions only during 2-hour daily window.

Pros:
- Batches interruptions into predictable times
- Easy to implement immediately
- Maintains engineer involvement

Cons:
- May delay urgent issues
- Stakeholders may resist limited access


SOLUTION 4: Invest in Self-Service
Build better admin tools, dashboards, and self-service features for common requests.

Pros:
- Permanent reduction in support volume
- Improves product for all customers
- Compounds over time

Cons:
- Requires upfront development investment
- Takes 1-2 quarters to see results


SOLUTION 5: Hire Support Engineer Role
Bring in a dedicated support engineer or SRE to own operational issues.

Pros:
- Specialist expertise for support
- Immediate relief for product engineers
- Career path for ops-minded engineers

Cons:
- Additional headcount cost
- May take time to find right candidate


SOLUTION 6: Reduce Technical Debt
Allocate 20% of each sprint to fixing root causes of recurring issues.

Pros:
- Addresses underlying problems
- Reduces future support volume
- Improves code quality

Cons:
- Slower feature velocity initially
- Hard to quantify ROI for stakeholders


RECOMMENDED STARTING POINT:
Combine Solutions 2 and 3 for immediate relief (tiered escalation + office hours), then invest in Solution 4 (self-service) for long-term improvement.
```

## When to Use

- Strategic planning sessions
- Problem-solving meetings
- Innovation workshops
- Breaking out of conventional thinking
