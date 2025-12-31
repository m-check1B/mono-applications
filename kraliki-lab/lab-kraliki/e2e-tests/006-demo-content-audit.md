# E2E Test: 006 - Content Audit Demo Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | MEDIUM |
| Estimated Duration | 15 minutes |
| Prerequisites | Lab by Kraliki environment, multi-model access |
| Location | Demo environment or customer VM |

## Objective

Verify the Content Audit demo (10-minute demo for SEO agencies/content teams) executes the multi-model analysis pattern correctly.

## Pre-conditions

1. Lab by Kraliki environment running
2. Access to Gemini, Codex, and Claude
3. Sample content available (URL or file)
4. API keys configured

## Reference

Demo script: `/demo/scenarios/content-audit.md`

## Test Steps

### Step 1: Environment Check

| Action | Verify all models accessible |
|--------|------------------------------|
| Command | `magic-box status` or health check |
| Expected | All CLIs responding |
| Verification | Health check passes |

### Step 2: Prepare Sample Content

| Action | Select content for audit |
|--------|-------------------------|
| Options | - Sample content from `/demo/sample-projects/content-campaign/` |
| | - Public blog post URL |
| | - Sample landing page |
| Expected | Content identified and accessible |
| Verification | Content readable |

### Step 3: Execute Multi-Model Audit

| Action | Run parallel content analysis |
|--------|------------------------------|
| Command | ```bash
claude "I need a comprehensive audit of this content piece.

URL: [content URL or file path]

Execute parallel analysis:
1. GEMINI: SEO audit (keywords, meta, structure, SERP potential)
2. CODEX: Technical audit (readability scores, accessibility, page speed implications)
3. OPUS: Strategic audit (value proposition clarity, conversion optimization, competitive positioning)

Synthesize all findings into a prioritized action list."
``` |
| Expected | Parallel execution begins |
| Verification | Command executes |

### Step 4: Verify Gemini SEO Analysis

| Action | Check SEO audit output |
|--------|------------------------|
| Expected | Analysis includes: |
| | - Keyword assessment |
| | - Meta tag analysis |
| | - Heading structure review |
| | - SERP potential estimate |
| Verification | SEO findings present |

### Step 5: Verify Codex Technical Audit

| Action | Check technical audit output |
|--------|----------------------------|
| Expected | Analysis includes: |
| | - Readability score (Flesch-Kincaid or similar) |
| | - Accessibility issues |
| | - Performance implications |
| Verification | Technical findings present |

### Step 6: Verify Opus Strategic Analysis

| Action | Check strategic audit output |
|--------|----------------------------|
| Expected | Analysis includes: |
| | - Value proposition clarity |
| | - Conversion optimization opportunities |
| | - Competitive positioning insights |
| Verification | Strategic findings present |

### Step 7: Verify Synthesis

| Action | Check consolidated output |
|--------|--------------------------|
| Expected | - Combined findings from all models |
| | - Prioritized action list |
| | - Clear next steps |
| Verification | Synthesis present and coherent |

### Step 8: Parallel Execution Verification

| Action | Confirm parallel execution occurred |
|--------|-----------------------------------|
| Expected | - Models worked concurrently |
| | - Time savings vs sequential |
| Verification | Check timing, logs |

### Step 9: Timing Check

| Action | Record total execution time |
|--------|----------------------------|
| Expected | Complete in under 5 minutes |
| Verification | Stopwatch from Step 3 |

### Step 10: Output Quality Assessment

| Action | Review output quality |
|--------|----------------------|
| Expected | - Actionable recommendations |
| | - Specific issues identified |
| | - Priority rankings |
| | - No contradictions between models |
| Verification | Manual review |

## Pass Criteria

- All three models execute successfully
- SEO, technical, and strategic analyses present
- Synthesis is coherent and actionable
- Parallel execution confirmed
- Total time under 5 minutes

## Sample Audit Categories

### SEO Issues to Find
- Missing meta description
- H1 tag issues
- Keyword optimization gaps
- Internal linking opportunities

### Technical Issues to Find
- Readability too complex
- Image optimization needs
- Mobile responsiveness issues
- Accessibility gaps

### Strategic Issues to Find
- Unclear value proposition
- Weak CTA placement
- Competitive disadvantages
- Conversion barriers

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| One model fails | Others should continue |
| Incomplete synthesis | Retry with explicit instructions |
| Rate limiting | Wait and retry |
| Content inaccessible | Use local file instead |

## ROI Talking Points

During demo, emphasize:
- Time saved: 3 minutes vs 3 hours manual
- Multi-perspective analysis
- Consistent quality across audits
- Scalable to entire content library

## Related Tests

- 004-demo-quick-audit.md
- 005-demo-agency-website.md
- 007-demo-parallel-tasks.md
