---
name: risk-assessment
description: Assess risks of a plan with likelihood, impact, and mitigations
category: decisions
source: OpenAI Academy
---

# Risk Assessment

Evaluate potential risks and develop mitigation strategies.

## Prompt Template

```
Assess the potential risks of the following plan: [describe plan]. The plan is set to start on [date]. List risks by likelihood and impact, and suggest mitigation strategies.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe plan]` | The initiative to assess | "Migrating production database over the weekend" |
| `[date]` | When the plan starts | "January 15", "next quarter" |

## Example Usage

**Input:**
```
Assess the potential risks of the following plan: Launching a new pricing tier that removes the free plan and introduces a $9/month starter tier. The plan is set to start on February 1st. List risks by likelihood and impact, and suggest mitigation strategies.
```

**Output:**
```
RISK ASSESSMENT: Pricing Tier Change

Launch Date: February 1st

RISK MATRIX:

| Risk | Likelihood | Impact | Priority |
|------|------------|--------|----------|
| User churn from free tier | High | High | Critical |
| Negative PR/social media | Medium | High | High |
| Support ticket surge | High | Medium | High |
| Payment processing issues | Low | High | Medium |
| Competitor exploitation | Medium | Medium | Medium |

DETAILED ANALYSIS:

1. User Churn from Free Tier (Critical)
   Likelihood: High | Impact: High
   Description: Free users may leave rather than convert
   Mitigation:
   - Grandfather existing free users for 6 months
   - Offer 50% discount for first 3 months
   - Communicate value of paid features clearly

2. Negative PR/Social Media (High)
   Likelihood: Medium | Impact: High
   Description: Public backlash on Twitter/forums
   Mitigation:
   - Prepare FAQ and talking points
   - Draft response templates for common concerns
   - Have leadership ready for direct engagement

3. Support Ticket Surge (High)
   Likelihood: High | Impact: Medium
   Description: Billing questions overwhelm support team
   Mitigation:
   - Create self-service help articles
   - Add temporary support staff for first 2 weeks
   - Implement chatbot for common questions

4. Payment Processing Issues (Medium)
   Likelihood: Low | Impact: High
   Description: Technical issues with billing integration
   Mitigation:
   - Test payment flows thoroughly before launch
   - Have rollback plan ready
   - Monitor payment success rates in real-time

OVERALL RISK LEVEL: High
RECOMMENDATION: Proceed with enhanced mitigations in place
```

## When to Use

- Before major launches or changes
- Planning risky technical work
- Evaluating new initiatives
- Change management preparation
