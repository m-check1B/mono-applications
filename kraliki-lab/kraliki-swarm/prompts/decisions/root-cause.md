---
name: root-cause
description: Identify root causes of recurring workplace issues
category: decisions
source: OpenAI Academy
---

# Identify Root Cause

Analyze problems to find underlying causes rather than symptoms.

## Prompt Template

```
Analyze the following workplace issue: [describe issue]. The context is that the problem has occurred multiple times. Identify possible root causes and suggest questions to confirm them.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe issue]` | The recurring problem | "Deployments keep failing on Fridays", "Customer complaints about response time" |

## Example Usage

**Input:**
```
Analyze the following workplace issue: Sprint commitments are consistently missed, with teams delivering 60-70% of planned work. The context is that the problem has occurred multiple times over the last 4 sprints. Identify possible root causes and suggest questions to confirm them.
```

**Output:**
```
ROOT CAUSE ANALYSIS: Missed Sprint Commitments

POSSIBLE ROOT CAUSES:

1. Estimation Accuracy
   - Stories may be under-estimated due to hidden complexity
   - Historical data not used for estimation baseline
   Questions: How are estimates created? Is there a calibration process?

2. Scope Creep
   - New work added mid-sprint without adjusting commitments
   - Urgent requests disrupting planned work
   Questions: How many unplanned items entered recent sprints? Who approves mid-sprint additions?

3. Dependency Delays
   - Blocked by other teams or external vendors
   - Waiting on approvals or resources
   Questions: What percentage of incomplete items were blocked? On what?

4. Capacity Overcommitment
   - Not accounting for meetings, support, and overhead
   - Team velocity expectations unrealistic
   Questions: What is the actual available capacity vs. assumed capacity?

5. Technical Debt
   - Unexpected issues in legacy code slowing progress
   - Lack of test coverage causing rework
   Questions: How much time went to unplanned bug fixes? In which areas?

RECOMMENDED NEXT STEPS:
1. Analyze the last 4 sprints for common patterns
2. Survey team members on perceived blockers
3. Compare estimated vs. actual hours per story type
```

## When to Use

- Investigating recurring project issues
- Post-mortems after failures
- Process improvement initiatives
- Quality or performance problems
