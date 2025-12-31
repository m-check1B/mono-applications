# Demo Scenario: Parallel Task Execution

**Duration:** 12 minutes
**Pattern:** Parallel Execution
**Target audience:** Consultancies, research teams, product managers

---

## Pre-Demo Setup (30 sec)

```bash
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/consulting-deck
```

---

## Part 1: The Problem (1 min)

### What to Say:

> "You're starting a consulting engagement. Day 1 tasks:
> - Research the market
> - Analyze competitors
> - Draft stakeholder questions
> - Outline the project plan
>
> Sequential execution: 8+ hours
> With a team: Still 4 hours (coordination overhead)
>
> What if you could run all of this in parallel, then synthesize?"

---

## Part 2: Execute Parallel Streams (8 min)

### Step 1: Launch Parallel Work

```bash
claude "I'm starting a consulting project on AI adoption in mid-market B2B.

Execute these tasks IN PARALLEL:

STREAM 1 (Gemini - Research):
- Market size and growth for mid-market B2B AI tools
- Top 5 current trends in AI adoption
- Key barriers to adoption from recent surveys

STREAM 2 (Gemini - Competitive):
- Top 10 AI tools targeting this segment
- Positioning and pricing comparison
- Gaps in the market

STREAM 3 (Opus - Strategy):
- 5 key questions for stakeholder interviews
- Hypothesis about primary adoption barriers
- Initial recommendations framework

STREAM 4 (Codex - Validation):
- Fact-check the research statistics
- Verify competitive intel accuracy
- Flag any conflicting information

When all streams complete, synthesize into an executive briefing."
```

### What to Narrate:

- "Watch the parallel execution - four streams working simultaneously..."
- "Gemini is pulling market data while Opus develops strategy..."
- "Codex will validate everything before we synthesize..."
- "This would normally require 4 different people, 4 meetings, 4 documents..."

### Step 2: Show the Synthesis

Display the consolidated output:
- Market overview (with validated stats)
- Competitive landscape summary
- Strategic hypotheses
- Stakeholder interview questions

---

## Part 3: Time Comparison (1 min)

### Visual Comparison:

```
SEQUENTIAL APPROACH:
[Research: 2h] → [Competitive: 2h] → [Strategy: 2h] → [Validation: 2h]
Total: 8 hours

TEAM APPROACH:
[Research: 2h]
[Competitive: 2h]      → [Synthesis meeting: 1h]
[Strategy: 2h]
Total: 3 hours + coordination overhead

LAB BY KRALIKI PARALLEL:
[All 4 streams: 15 min] → [Auto-synthesis: 2 min]
Total: 17 minutes
```

### What to Say:

> "Same quality output. Fraction of the time.
>
> This isn't about replacing consultants - it's about giving consultants superpowers.
>
> Your senior people spend time on insights and client relationships, not data gathering."

---

## Part 4: Customization (1 min)

### What to Say:

> "This pattern adapts to any parallel workload:
> - Product research (features, pricing, reviews, positioning)
> - Due diligence (financial, legal, technical, reputation)
> - Content creation (research, draft, repurpose, schedule)
>
> You define the streams. Lab by Kraliki executes them simultaneously."

---

## Closing

> "The parallel execution pattern is one of our most powerful.
>
> It's not just faster - it's more thorough. When you're not time-constrained, you explore more angles.
>
> What workflows in your organization involve multiple parallel information streams?"

---

## Technical Notes for Presenter

- If one stream fails, the others continue
- Synthesis waits for all streams to complete
- Each stream can be configured with different models based on task type
- Memory (mgrep) captures everything for future reference

---

*Parallel Tasks Demo Script v1.0*
