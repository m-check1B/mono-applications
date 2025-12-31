# Hard Problem Voting Pattern

**Purpose:** Use multiple AI models to vote on difficult decisions where there's no clear right answer.

## Overview

```
                    ┌───────────────┐
                    │   QUESTION    │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────┐         ┌─────────┐         ┌─────────┐
   │ Claude  │         │ Gemini  │         │ Codex   │
   │  Vote   │         │  Vote   │         │  Vote   │
   └────┬────┘         └────┬────┘         └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                     ┌──────▼──────┐
                     │  AGGREGATE  │
                     │   VOTES     │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │  DECISION   │
                     └─────────────┘
```

## When to Use

- Architectural decisions with tradeoffs
- Technology choices (framework, library)
- Ambiguous requirements interpretation
- Risk assessment
- Code review disagreements
- Design pattern selection

## When NOT to Use

- Clear factual questions (one right answer)
- Simple implementation tasks
- Well-documented best practices
- Time-critical decisions (voting takes time)

## Voting Categories

### 1. Binary Vote
Yes/No decisions.

### 2. Multiple Choice
Choose from N options.

### 3. Ranked Choice
Order preferences 1st, 2nd, 3rd.

### 4. Confidence-Weighted
Vote with confidence score (affects weight).

## Voting Prompt Template

```markdown
# Voting Request

## Question
[Clear statement of what needs to be decided]

## Context
[Relevant background information]

## Options
1. Option A: [Description]
2. Option B: [Description]
3. Option C: [Description]

## Evaluation Criteria
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

## Your Task
Analyze each option against the criteria and cast your vote.

## Required Output Format
```yaml
vote:
  choice: "[Option A|B|C]"
  confidence: [0-100]
  reasoning: |
    Why you chose this option.
  pros:
    - "Advantages of chosen option"
  cons:
    - "Disadvantages/risks of chosen option"
  alternative_consideration: |
    When the other options might be better.
```
```

## Aggregation Rules

### Simple Majority
```python
def simple_majority(votes: List[Vote]) -> str:
    """Winner is option with most votes."""
    counts = Counter(v.choice for v in votes)
    return counts.most_common(1)[0][0]
```

### Confidence-Weighted
```python
def weighted_vote(votes: List[Vote]) -> str:
    """Weight votes by confidence."""
    weighted = defaultdict(float)
    for v in votes:
        weighted[v.choice] += v.confidence / 100
    return max(weighted, key=weighted.get)
```

### Supermajority (2/3)
```python
def supermajority(votes: List[Vote]) -> Optional[str]:
    """Require 2/3 agreement, else escalate."""
    counts = Counter(v.choice for v in votes)
    total = len(votes)
    for choice, count in counts.items():
        if count / total >= 0.67:
            return choice
    return None  # No consensus, escalate to human
```

## Example: Technology Choice

**Question:** Which database should we use for the new project?

```yaml
question: "Select primary database for user management service"

context: |
  - Expected 10K users initially, scaling to 1M
  - Complex relationships between entities
  - Team has SQL experience
  - Deployment on Kubernetes
  - Budget for managed services

options:
  - id: "A"
    name: "PostgreSQL (self-managed)"
    description: "Open-source relational database, self-hosted"

  - id: "B"
    name: "PostgreSQL (managed - RDS/Cloud SQL)"
    description: "Managed PostgreSQL with automatic backups"

  - id: "C"
    name: "MongoDB Atlas"
    description: "Managed document database"

evaluation_criteria:
  - "Scalability to 1M users"
  - "Team expertise alignment"
  - "Operational complexity"
  - "Cost at scale"
  - "Feature requirements (relationships, transactions)"

votes:
  - voter: "claude"
    choice: "B"
    confidence: 85
    reasoning: |
      Managed PostgreSQL offers the best balance:
      - Team already knows SQL
      - Handles relational data well
      - Managed = less ops burden
      - Proven scale to millions of users
    pros:
      - "Familiar to team"
      - "Strong consistency for user data"
      - "Automatic backups and maintenance"
    cons:
      - "Higher cost than self-managed"
      - "Some vendor lock-in"
    alternative_consideration: |
      If budget is very tight, Option A works but needs DevOps expertise.
      If data becomes highly unstructured, reconsider MongoDB.

  - voter: "gemini"
    choice: "B"
    confidence: 80
    reasoning: |
      PostgreSQL is the right choice for relational user data.
      Managed version reduces operational burden significantly.
    pros:
      - "ACID compliance for user transactions"
      - "Rich ecosystem and tooling"
    cons:
      - "Monthly managed service cost"
    alternative_consideration: |
      MongoDB if schema flexibility becomes critical.

  - voter: "codex"
    choice: "B"
    confidence: 90
    reasoning: |
      For user management with relationships (user-roles, user-teams),
      PostgreSQL is the standard choice. Managed = safer for production.
    pros:
      - "Foreign keys enforce data integrity"
      - "Mature query optimizer"
      - "Point-in-time recovery"
    cons:
      - "Schema migrations require planning"
    alternative_consideration: |
      Self-managed (A) if you have dedicated DBA resources.

aggregation:
  method: "confidence_weighted"
  result:
    choice: "B"
    total_confidence: 255
    weighted_score: 2.55  # (0.85 + 0.80 + 0.90)
    consensus: "strong"

decision:
  selected: "PostgreSQL (managed - RDS/Cloud SQL)"
  confidence: "high"
  rationale: |
    Unanimous agreement on Option B with high confidence (80-90%).
    Key factors: team expertise, data relationships, operational simplicity.
  action_items:
    - "Select cloud provider (AWS RDS vs GCP Cloud SQL)"
    - "Define initial schema"
    - "Set up connection pooling"
```

## Orchestration Script

```python
#!/usr/bin/env python3
"""
Hard problem voting orchestration for Magic Box.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import List, Optional
from collections import Counter


@dataclass
class Vote:
    voter: str
    choice: str
    confidence: int
    reasoning: str


@dataclass
class VotingResult:
    question: str
    winner: str
    votes: List[Vote]
    consensus_level: str  # unanimous, strong, weak, none
    confidence_score: float


async def collect_vote(voter: str, question: str, options: List[str]) -> Vote:
    """Collect vote from a single model."""
    prompt = f"""
Vote on this question:

{question}

Options:
{chr(10).join(f'- {opt}' for opt in options)}

Respond in JSON format:
{{"choice": "option name", "confidence": 0-100, "reasoning": "why"}}
"""
    # Run the appropriate CLI and parse response
    # (implementation depends on CLI setup)
    pass


async def run_voting(
    question: str,
    options: List[str],
    voters: List[str] = ["claude", "gemini", "codex"]
) -> VotingResult:
    """Run voting across multiple models."""

    # Collect votes in parallel
    votes = await asyncio.gather(
        *[collect_vote(voter, question, options) for voter in voters]
    )

    # Aggregate
    choice_counts = Counter(v.choice for v in votes)
    winner = choice_counts.most_common(1)[0][0]
    winner_count = choice_counts[winner]

    # Determine consensus level
    if winner_count == len(votes):
        consensus = "unanimous"
    elif winner_count >= len(votes) * 0.67:
        consensus = "strong"
    elif winner_count >= len(votes) * 0.5:
        consensus = "weak"
    else:
        consensus = "none"

    # Calculate confidence score
    confidence = sum(v.confidence for v in votes if v.choice == winner) / len(votes)

    return VotingResult(
        question=question,
        winner=winner,
        votes=votes,
        consensus_level=consensus,
        confidence_score=confidence
    )


# Example usage
async def main():
    result = await run_voting(
        question="Which web framework should we use?",
        options=["FastAPI", "Express.js", "Django"]
    )

    print(f"Decision: {result.winner}")
    print(f"Consensus: {result.consensus_level}")
    print(f"Confidence: {result.confidence_score:.0f}%")

    for vote in result.votes:
        print(f"\n{vote.voter}: {vote.choice} ({vote.confidence}%)")
        print(f"  {vote.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Handling No Consensus

When voting doesn't produce a clear winner:

```yaml
no_consensus_protocol:
  threshold: "No option got 50%+ of votes"

  actions:
    1. "Request clarification on requirements"
    2. "Gather more evaluation criteria"
    3. "Run another round with narrowed options"
    4. "Escalate to human decision-maker"

  escalation_format: |
    ## Decision Needed: [Question]

    ### Voting Results
    - Option A: 1 vote (Claude)
    - Option B: 1 vote (Gemini)
    - Option C: 1 vote (Codex)

    ### Key Arguments

    **For Option A:**
    [Claude's reasoning]

    **For Option B:**
    [Gemini's reasoning]

    **For Option C:**
    [Codex's reasoning]

    ### Recommendation
    [Which option to lean towards and why, if any]

    ### Your Input Needed
    Please make the final decision or provide additional context.
```

## Best Practices

1. **Clear options** - Well-defined, mutually exclusive choices
2. **Relevant criteria** - Give voters the right evaluation framework
3. **Independent voting** - Don't show one model's vote to another
4. **Require reasoning** - Votes without justification are less valuable
5. **Set thresholds** - Define what "consensus" means upfront
6. **Escalation path** - Know what to do when voting fails
