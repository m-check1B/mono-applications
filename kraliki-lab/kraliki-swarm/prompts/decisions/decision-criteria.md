---
name: decision-criteria
description: Define weighted decision criteria for multi-stakeholder choices
category: decisions
source: OpenAI Academy
---

# Define Decision Criteria

Create a clear, weighted framework for making complex decisions.

## Prompt Template

```
Help define clear decision-making criteria for [describe decision]. The context is that multiple stakeholders are involved. Provide a short list of weighted criteria to guide the choice.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe decision]` | The decision to be made | "selecting a new project management tool", "choosing office location" |

## Example Usage

**Input:**
```
Help define clear decision-making criteria for selecting a new customer support platform. The context is that multiple stakeholders are involved including support team, engineering, finance, and leadership. Provide a short list of weighted criteria to guide the choice.
```

**Output:**
```
DECISION CRITERIA: Customer Support Platform Selection

WEIGHTED CRITERIA:

1. Ease of Use for Support Team (25%)
   - Intuitive interface, minimal training needed
   - Support team uses it daily; adoption is critical
   Measured by: Demo feedback scores, training time estimate

2. Integration Capabilities (20%)
   - Must integrate with CRM, Slack, and ticketing systems
   - Engineering needs manageable integration effort
   Measured by: API quality, existing integration count

3. Total Cost of Ownership (20%)
   - Licensing, implementation, and ongoing costs
   - Finance needs predictable budgeting
   Measured by: 3-year TCO calculation

4. Reporting and Analytics (15%)
   - Leadership needs visibility into support metrics
   - Must support custom dashboards
   Measured by: Reporting feature checklist

5. Scalability (10%)
   - Handle growth from 10 to 50 support agents
   - Performance at volume
   Measured by: Vendor case studies, tier pricing

6. Security and Compliance (10%)
   - SOC2, GDPR compliance required
   - SSO integration needed
   Measured by: Compliance certifications

SCORING GUIDE:
- 1 = Does not meet requirement
- 2 = Partially meets requirement
- 3 = Fully meets requirement
- 4 = Exceeds requirement

Use: Sum of (Score x Weight) for each option
```

## When to Use

- Multi-stakeholder decisions
- Vendor or tool selection
- Strategic choices with competing priorities
- Building alignment before evaluation
