# Pattern Proposal: Effort Scaling Rules

## Source
- URL: https://www.anthropic.com/engineering/multi-agent-research-system
- Stars/Citations: Anthropic official engineering blog, used in Claude Research product
- Last Updated: December 2025

## Pattern Description
Explicit effort heuristics embedded in agent prompts to control how many subagents spawn and how many tool calls each makes. Without these rules, agents either over-invest in simple tasks (wasting tokens) or under-invest in complex tasks (producing incomplete results).

## Evidence of Success
- Used in Anthropic's multi-agent research system
- "Cut research time by up to 90% for complex queries"
- Prevents agents from creating token storms on simple lookups
- Prevents agents from giving shallow answers on complex research

## Proposed Effort Tiers

| Task Complexity | Subagents | Tool Calls per Agent |
|-----------------|-----------|---------------------|
| Simple fact-finding | 1 | 3-10 |
| Direct comparison | 2-4 | 10-15 each |
| Complex research | 10+ | 15-30 each with divided responsibilities |

## Proposed Integration

Add to ALL Kraliki genomes in the task execution section:

```markdown
## EFFORT CALIBRATION (REQUIRED)

Before starting any task, classify its complexity:

**SIMPLE (1 agent, 3-10 tool calls)**
- Single fact lookup
- Status check
- Quick fix with known solution
- Reading single file

**MODERATE (2-4 subagents, 10-15 calls each)**
- Comparison between 2-3 options
- Implementation of well-defined feature
- Debugging with known symptom
- Code review of single PR

**COMPLEX (10+ subagents, 15-30 calls each)**
- Architecture research
- Multi-file refactoring
- Investigation with unknown cause
- Feature requiring design decisions

Calibrate your effort to match complexity. Over-investment wastes tokens. Under-investment produces incomplete work.
```

## Affected Files
- genomes/darwin-*.md (all genomes)
- arena/spawner.py (add complexity estimation)

## Risk Assessment
- Risk Level: Low
- Rollback plan: Remove the section from genomes, no code changes

## Success Metrics
- Reduced token usage per task completion
- More complete outputs for complex tasks
- Fewer "too shallow" or "over-engineered" results
- Measurable via fitness.py quality_score distribution
