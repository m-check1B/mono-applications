---
name: recommend-option
description: Recommend the best option with clear reasoning
category: decisions
source: OpenAI Academy
---

# Recommend Best Option

Provide a clear recommendation with reasoning and next steps.

## Prompt Template

```
Based on the following background: [describe situation and options], recommend the most suitable option. Explain your reasoning clearly and suggest first steps for implementation.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe situation and options]` | Context and alternatives | "We need to choose between React, Vue, or Svelte for our new frontend..." |

## Example Usage

**Input:**
```
Based on the following background: We are a 5-person startup building a B2B SaaS product. We need to choose a monitoring and observability stack. Options are: A) Datadog (full-featured, expensive), B) Grafana Cloud (good features, moderate cost), C) Self-hosted Prometheus + Grafana (cheap but maintenance overhead). Our priority is getting to market fast with limited DevOps capacity. Recommend the most suitable option. Explain your reasoning clearly and suggest first steps for implementation.
```

**Output:**
```
RECOMMENDATION: Option B - Grafana Cloud

REASONING:

1. Team Size Consideration
   With a 5-person startup and limited DevOps capacity, self-hosting (Option C) would divert engineering time from product development. The maintenance overhead contradicts your market-speed priority.

2. Cost vs. Value Balance
   Datadog (Option A) offers comprehensive features but at a cost that may be premature for an early-stage startup. Grafana Cloud provides 80% of the value at a fraction of the cost.

3. Speed to Market Alignment
   Grafana Cloud offers:
   - Quick setup (hours, not days)
   - Managed infrastructure (no ops burden)
   - Good default dashboards and alerts
   - Clear upgrade path as you scale

4. Future Flexibility
   Grafana Cloud uses open standards (Prometheus metrics, Loki logs). If you outgrow it or need to cut costs later, migration paths exist to self-hosted or other solutions.

WHY NOT THE OTHERS:
- Datadog: Excellent but expensive; save budget for product development
- Self-hosted: Too much operational overhead for current team size

FIRST STEPS:

Week 1:
1. Sign up for Grafana Cloud free tier
2. Install Grafana Agent on production servers
3. Set up basic infrastructure dashboards

Week 2:
4. Configure application metrics export
5. Create 3-5 critical alerts (uptime, error rates, latency)
6. Document runbooks for each alert

Week 3:
7. Add log aggregation with Loki
8. Train team on dashboard usage
9. Review and adjust alert thresholds

ESTIMATED MONTHLY COST: $50-150 at current scale
```

## When to Use

- Concluding a decision-making process
- Providing executive summary recommendations
- Documenting final choices with rationale
- Communicating direction to stakeholders
