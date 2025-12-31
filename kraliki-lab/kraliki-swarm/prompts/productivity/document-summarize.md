---
name: document-summarize
description: Summarize documents into key points and recommended actions
category: productivity
source: OpenAI Academy
---

# Summarize Document

Extract essential information and actionable insights from long documents.

## Prompt Template

```
Summarize the following document into 5 key points and 3 recommended actions. The document is [type: report, plan, or notes]. Keep the summary concise and professional. Text: [paste document].
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[type]` | Document category | "report", "plan", "notes", "proposal" |
| `[paste document]` | Full document text | The complete document to summarize |

## Example Usage

**Input:**
```
Summarize the following document into 5 key points and 3 recommended actions. The document is a quarterly sales report. Keep the summary concise and professional. Text:

Q3 2025 Sales Report

Revenue reached $2.4M, up 15% from Q2. Enterprise segment grew 28% driven by 3 large deals (Acme Corp $400K, TechFlow $280K, DataMax $180K). SMB segment declined 8% due to increased competition from new market entrants.

Sales cycle lengthened from 45 to 62 days on average, primarily in enterprise. Win rate improved from 22% to 27%. Pipeline for Q4 stands at $4.1M with 60% probability-weighted.

Team expanded from 8 to 10 reps. New hires ramping but not yet quota-bearing. Two top performers exceeded quota by 40%+. Three reps below 70% of quota - performance plans initiated.

Churn increased to 4.2% from 3.1% last quarter. Exit interviews cite pricing and missing features (API access, SSO). Competitor analysis shows aggressive pricing from NewVendor and FastStart.

Recommendations from sales leadership: 1) Introduce mid-market pricing tier, 2) Accelerate API roadmap, 3) Invest in sales enablement for competitive positioning.
```

**Output:**
```
Q3 2025 SALES REPORT SUMMARY

KEY POINTS:

1. Strong Revenue Growth
   $2.4M revenue (+15% QoQ), driven primarily by enterprise segment (+28%)

2. Enterprise Concentration Risk
   Three large deals account for $860K; sales cycle lengthening to 62 days

3. SMB Segment Weakness
   8% decline due to new competitive entrants; requires strategic response

4. Improving Efficiency
   Win rate up from 22% to 27%; pipeline healthy at $4.1M (60% weighted)

5. Churn Concerns
   Churn increased to 4.2% (from 3.1%); customers citing pricing and feature gaps

RECOMMENDED ACTIONS:

1. Launch Mid-Market Pricing Tier
   Address gap between SMB and enterprise pricing; capture customers leaving for competitors

2. Prioritize API and SSO Features
   Top churn reasons are product gaps; accelerate roadmap items to reduce attrition

3. Develop Competitive Battlecards
   Arm sales team with positioning against NewVendor and FastStart; focus on differentiation
```

## When to Use

- Reviewing lengthy reports before meetings
- Creating executive briefings
- Extracting action items from strategic documents
- Catching up on documents you missed
