# Pattern: Parallel Execution

## Overview

This pattern executes multiple independent workstreams simultaneously, then synthesizes results. It's ideal for time-sensitive tasks or comprehensive research.

## When to Use

✅ **Use this pattern when:**
- Multiple independent subtasks exist
- Time is critical
- Subtasks don't depend on each other
- Comprehensive analysis is needed
- Exploring multiple angles simultaneously

❌ **Don't use this pattern when:**
- Tasks have strong dependencies
- Quality/accuracy is more important than speed
- One subtask would block all others if it fails
- Synthesis complexity would exceed benefits of parallelism

## The Process

### Step 1: Identify Parallelizable Workstreams
**Orchestrator analyzes task for parallelization:**

**Questions to ask:**
1. Can we break this into independent streams?
2. What are the natural divisions?
3. Do any streams depend on others?
4. Can we assign different workers to optimize strengths?

**Parallelization Heuristics:**
- **Research streams** = different sources/angles (competitors, market, features)
- **Development streams** = different modules/components (frontend, backend, tests)
- **Content streams** = different deliverables (research, draft, edit, optimize)
- **Analysis streams** = different perspectives (technical, business, user)

### Step 2: Launch Parallel Workstreams
**Orchestrator delegates to workers simultaneously**

**Assignment Strategy:**
| Stream Type | Worker Assignment | Rationale |
|-------------|-------------------|-----------|
| Research | Gemini | Fast at synthesis, multiple sources |
| Frontend | Gemini | Strong at UI/UX |
| Backend | Codex | Better at complex logic |
| Content | Gemini | Natural language strength |
| Validation | Codex | Thorough fact-checking |

**Stream Definition Template:**
```markdown
### Stream 1: [Name] - Worker: [gemini/codex]
**Tasks**: [List of specific tasks]
**Output**: [Expected deliverable]
**Dependencies**: [None or other streams]
**Estimated Time**: [15-30 min]
```

### Step 3: Monitor Progress
**Orchestrator tracks all streams:**

**Monitoring Checklist:**
- [ ] All streams started successfully
- [ ] No streams are blocked/waiting
- [ ] Progress is being made (not stuck)
- [ ] Estimated times are realistic
- [ ] Any failures to handle

**If a Stream Fails:**
1. Determine impact: Does this block other streams or synthesis?
2. Decide: Retry with same worker, switch worker, or adjust scope?
3. Notify: Alert other streams of the failure if they depend on this output
4. Document: Record what went wrong for learning

### Step 4: Synthesize Results
**Orchestrator combines all stream outputs**

**Synthesis Approach:**
1. **Gather** all completed stream outputs
2. **Compare** for consistency (conflicts, contradictions)
3. **Integrate** into coherent deliverable
4. **Validate** against original task requirements
5. **Format** for user consumption

**Conflict Resolution:**
| Conflict Type | Resolution Strategy |
|--------------|-------------------|
| Factual contradictions | Research to determine truth, note uncertainty |
| Stylistic inconsistencies | Apply consistent style across all sections |
| Technical incompatibilities | Choose best approach, document tradeoffs |
| Missing information | Flag for user, suggest data needs |

### Step 5: Quality Check (Optional but Recommended)
**Optional audit pass before delivery**

**When to Skip Audit:**
- Time-critical deliverable
- Low-stakes output (internal notes, prototypes)
- Already confident in output quality

**When to Run Audit:**
- High-stakes deliverables (client work, production code)
- External-facing content (public documentation, marketing)
- Critical systems (security, payments)

## Example Execution

### Task: Competitive Intelligence Report

**Step 1: Identify Streams**
```markdown
### Parallel Workstreams Identified

### Stream 1: Market Leaders Research
- **Worker**: gemini
- **Focus**: Top 5 established competitors
- **Output**: Company profiles with strengths/weaknesses

### Stream 2: Emerging Competitors Research
- **Worker**: gemini
- **Focus**: Top 5 new/innovative players
- **Output**: Company profiles with threat level

### Stream 3: Feature Comparison
- **Worker**: gemini
- **Focus**: Feature sets across all competitors
- **Output**: Feature comparison matrix

### Stream 4: Pricing Analysis
- **Worker**: gemini
- **Focus**: Pricing models and positioning
- **Output**: Pricing comparison table

### Stream 5: Strategic Insights
- **Worker**: codex
- **Focus**: Synthesize findings, identify gaps, provide recommendations
- **Output**: Strategic recommendations (3-5 actionable items)
```

**Step 2: Launch Streams** (All start simultaneously at T+0)
- Streams 1-4 run in parallel (gemini)
- Stream 5 waits for streams 1-4 to complete (codex)

**Step 3: Monitor**
- T+15 min: All 4 research streams reporting progress
- T+25 min: Streams 1-4 complete, stream 5 starts
- T+40 min: Stream 5 complete

**Step 4: Synthesize**
```markdown
# Competitive Intelligence Report

## Market Leaders
[Content from Stream 1]

## Emerging Competitors
[Content from Stream 2]

## Feature Comparison
[Content from Stream 3]

## Pricing Analysis
[Content from Stream 4]

## Strategic Recommendations
[Content from Stream 5 - insights based on all data]
```

**Step 5: Quality Check** (Optional)
- Codex validates facts from research
- Checks for contradictions or inconsistencies
- Confirms recommendations are supported by data

## Time Analysis

### Sequential vs Parallel

| Approach | Time | Notes |
|----------|-------|-------|
| Sequential (Stream 1 → 2 → 3 → 4 → 5) | 100 min | One at a time |
| Parallel (Streams 1-4 simultaneously, then 5) | 40 min | 60% faster |

**Speedup Calculation:**
- Sequential: 4 streams × 25 min each = 100 min + synthesis 15 min = 115 min
- Parallel: 25 min for 4 streams + 15 min synthesis = 40 min
- **Speedup: 2.9× faster**

## Common Pitfalls

### Over-Parallelization
**Symptom**: Too many small streams, high coordination overhead
**Fix**: Combine related streams, aim for 3-5 maximum
**Learning**: Don't parallelize beyond what's manageable

### Dependency Overlook
**Symptom**: Stream 5 blocked waiting for Stream 1, but they were launched as parallel
**Fix**: Identify dependencies upfront, sequence appropriately
**Learning**: Map dependencies before starting streams

### Synthesis Bottleneck
**Symptom**: All streams complete but synthesis takes longer than running them sequentially would have
**Fix**: Stream 5 (synthesis) can start as soon as first stream completes, not wait for all
**Learning**: Overlap synthesis with last streams, pipeline the data

### Conflicting Outputs
**Symptom**: Streams produce contradictory information
**Fix**: Pause, research to resolve, then continue
**Learning**: Document contradictions, provide both perspectives

## Advanced Techniques

### Pipeline Synthesis
**Concept**: Start synthesis as soon as first stream completes, not wait for all.

**Implementation:**
```markdown
Stream 1 completes at T+20 → Start partial synthesis
Stream 2 completes at T+22 → Update synthesis
Stream 3 completes at T+25 → Update synthesis
Stream 4 completes at T+28 → Finalize synthesis
Stream 5 (codex) starts at T+15, runs concurrently, completes at T+40
```

**Benefit**: Reduces overall time vs waiting for all streams

### Adaptive Stream Count
**Concept**: Start with estimated optimal streams, adjust based on task complexity.

**Algorithm:**
1. Start with 3-4 streams
2. If streams are struggling (taking too long), split one stream into two
3. If streams finish too quickly, add more parallelization opportunities
4. Goal: Balance worker utilization with manageable coordination

## Success Metrics

Track these to evaluate pattern effectiveness:

- **Parallel Efficiency**: (Sequential time) / (Parallel time)
- **Stream Success Rate**: % of streams completing without retry
- **Synthesis Quality**: User satisfaction with integrated output
- **Time Savings**: How much faster vs sequential?
- **Coordination Overhead**: Time spent managing streams vs actual work

**Target Metrics:**
- Parallel Efficiency: > 2.0× (at least 2× faster)
- Stream Success Rate: > 90% (most streams succeed on first try)
- Synthesis Quality: > 4/5 user satisfaction
