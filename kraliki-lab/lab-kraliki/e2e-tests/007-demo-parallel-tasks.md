# E2E Test: 007 - Parallel Tasks Demo Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | MEDIUM |
| Estimated Duration | 18 minutes |
| Prerequisites | Lab by Kraliki environment, multi-model access |
| Location | Demo environment or customer VM |

## Objective

Verify the Parallel Task Execution demo (12-minute demo for consultancies/research teams) executes multiple concurrent work streams correctly.

## Pre-conditions

1. Lab by Kraliki environment running
2. All models accessible (Claude/Opus, Gemini, Codex)
3. Sample project context loaded
4. API keys configured

## Reference

- Demo script: `/demo/scenarios/parallel-tasks.md`
- Sample project: `/demo/sample-projects/consulting-deck/`

## Test Steps

### Step 1: Environment Verification

| Action | Check all components ready |
|--------|---------------------------|
| Command | `./scripts/demo-start.sh` |
| Expected | All services healthy |
| Verification | Green status for all |

### Step 2: Navigate to Sample Project

| Action | Load consulting project |
|--------|------------------------|
| Command | `cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/consulting-deck` |
| Expected | Project directory accessible |
| Verification | `ls` shows project files |

### Step 3: Execute Parallel Streams

| Action | Launch 4 parallel work streams |
|--------|-------------------------------|
| Command | ```bash
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
``` |
| Expected | Parallel execution begins |
| Verification | Multiple streams started |

### Step 4: Verify Stream 1 (Research)

| Action | Check research stream output |
|--------|----------------------------|
| Expected | - Market size data |
| | - 5 trends identified |
| | - Adoption barriers listed |
| Verification | Research content present |

### Step 5: Verify Stream 2 (Competitive)

| Action | Check competitive stream output |
|--------|--------------------------------|
| Expected | - 10 AI tools listed |
| | - Pricing comparison |
| | - Market gaps identified |
| Verification | Competitive intel present |

### Step 6: Verify Stream 3 (Strategy)

| Action | Check strategy stream output |
|--------|------------------------------|
| Expected | - 5 interview questions |
| | - Barrier hypotheses |
| | - Framework outline |
| Verification | Strategic content present |

### Step 7: Verify Stream 4 (Validation)

| Action | Check validation stream output |
|--------|-------------------------------|
| Expected | - Fact-check results |
| | - Accuracy verification |
| | - Conflict flags (if any) |
| Verification | Validation present |

### Step 8: Verify Parallel Execution

| Action | Confirm streams ran concurrently |
|--------|----------------------------------|
| Expected | - Overlapping execution timestamps |
| | - Total time < sum of individual times |
| Verification | Check logs or timing |

### Step 9: Verify Synthesis

| Action | Check executive briefing output |
|--------|--------------------------------|
| Expected | - Market overview section |
| | - Competitive landscape summary |
| | - Strategic hypotheses |
| | - Stakeholder interview questions |
| | - Validated data |
| Verification | Synthesis document present |

### Step 10: Quality Assessment

| Action | Review synthesis quality |
|--------|-------------------------|
| Expected | - Coherent narrative |
| | - No contradictions |
| | - Actionable insights |
| | - Professional format |
| Verification | Manual review |

### Step 11: Timing Verification

| Action | Record total execution time |
|--------|----------------------------|
| Expected | Complete in under 17 minutes |
| Comparison | Sequential would take 8+ hours |
| Verification | Stopwatch from Step 3 |

### Step 12: Memory Capture

| Action | Verify context retained in mgrep |
|--------|----------------------------------|
| Command | Query mgrep for project-related terms |
| Expected | Context searchable for future reference |
| Verification | mgrep returns relevant results |

## Pass Criteria

- All 4 streams execute successfully
- Parallel execution confirmed (timing)
- Synthesis is coherent and complete
- Total time under 17 minutes
- No stream failures

## Time Comparison Visual

```
SEQUENTIAL APPROACH:
[Research: 2h] -> [Competitive: 2h] -> [Strategy: 2h] -> [Validation: 2h]
Total: 8 hours

TEAM APPROACH:
[Research: 2h]
[Competitive: 2h]      -> [Synthesis meeting: 1h]
[Strategy: 2h]
Total: 3 hours + coordination overhead

LAB BY KRALIKI PARALLEL:
[All 4 streams: 15 min] -> [Auto-synthesis: 2 min]
Total: 17 minutes
```

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| One stream fails | Others should continue |
| Synthesis incomplete | Retry synthesis separately |
| Rate limits hit | Stagger stream starts |
| Memory not captured | Check mgrep service |

## Customization Options

Demo can adapt to:
- Product research (features, pricing, reviews)
- Due diligence (financial, legal, technical)
- Content creation (research, draft, repurpose)

## Related Tests

- 004-demo-quick-audit.md
- 005-demo-agency-website.md
- 006-demo-content-audit.md
