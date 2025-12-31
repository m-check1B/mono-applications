---
name: compare-options
description: Evaluate multiple options with pros, cons, and risks
category: decisions
source: OpenAI Academy
---

# Compare Options

Systematically evaluate alternatives for better decision-making.

## Prompt Template

```
Compare the following two or more possible solutions: [list options]. The decision needs to be made in [timeframe]. Evaluate pros, cons, and potential risks for each option.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[list options]` | Solutions to compare | "Option A: Build in-house, Option B: Buy vendor solution" |
| `[timeframe]` | Decision deadline | "this week", "by end of month" |

## Example Usage

**Input:**
```
Compare the following two or more possible solutions: Option A: Use PostgreSQL with read replicas, Option B: Migrate to CockroachDB, Option C: Implement application-level sharding. The decision needs to be made in two weeks. Evaluate pros, cons, and potential risks for each option.
```

**Output:**
```
DATABASE SCALING OPTIONS COMPARISON

OPTION A: PostgreSQL with Read Replicas
Pros:
- Minimal code changes required
- Team already has PostgreSQL expertise
- Proven technology, extensive documentation
Cons:
- Write scaling still limited to primary node
- Replication lag can cause read inconsistency
Risks:
- May become bottleneck again within 12 months
- Failover complexity in multi-region setup

OPTION B: Migrate to CockroachDB
Pros:
- Automatic horizontal scaling
- Strong consistency with distributed writes
- PostgreSQL-compatible wire protocol
Cons:
- Learning curve for operations team
- Higher infrastructure costs
- Migration effort is significant
Risks:
- Potential compatibility issues with existing queries
- Vendor lock-in concerns

OPTION C: Application-Level Sharding
Pros:
- Full control over data distribution
- Can optimize for specific access patterns
Cons:
- Significant development effort
- Cross-shard queries become complex
- Ongoing maintenance burden
Risks:
- Architecture complexity increases bug surface
- Resharding is painful as data grows

SUMMARY TABLE:
| Criteria        | Option A | Option B | Option C |
|-----------------|----------|----------|----------|
| Implementation  | Low      | Medium   | High     |
| Scalability     | Medium   | High     | High     |
| Team Readiness  | High     | Low      | Medium   |
| Long-term Risk  | Medium   | Low      | Medium   |
```

## When to Use

- Technology or vendor selection
- Build vs. buy decisions
- Process or workflow changes
- Strategic direction choices
