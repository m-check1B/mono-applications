# E2E Test: 005 - Agency Website Demo Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 20 minutes |
| Prerequisites | Lab by Kraliki environment, Claude/Gemini/Codex CLIs |
| Location | Demo environment or customer VM |

## Objective

Verify the Agency Website Build demo (15-minute demo for digital agencies) executes the full Build-Audit-Fix pattern correctly.

## Pre-conditions

1. Lab by Kraliki environment running
2. All three CLIs accessible (Claude, Gemini, Codex)
3. Sample project loaded
4. API keys configured for all providers

## Reference

- Demo script: `/demo/scenarios/agency-website.md`
- Sample project: `/demo/sample-projects/agency-client/`

## Test Steps

### Step 1: Environment Verification

| Action | Run demo startup script |
|--------|------------------------|
| Command | `./scripts/demo-start.sh` |
| Expected | All components healthy |
| Verification | Green checkmarks for all services |

### Step 2: Load Project Files

| Action | Navigate to sample project |
|--------|---------------------------|
| Command | `cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/agency-client` |
| Expected | Directory exists with PROJECT.md and content.md |
| Verification | `ls -la` shows expected files |

### Step 3: Review Project Brief

| Action | Display project requirements |
|--------|----------------------------|
| Command | `cat PROJECT.md` |
| Expected | - Client name (Acme Corp or similar) |
| | - Brand specifications |
| | - Page requirements |
| Verification | Requirements clearly documented |

### Step 4: Review Content

| Action | Display content file |
|--------|---------------------|
| Command | `cat content.md` |
| Expected | - Headlines |
| | - Copy sections |
| | - CTAs |
| Verification | Content ready for use |

### Step 5: Execute Build-Audit-Fix

| Action | Trigger the pattern with Claude |
|--------|--------------------------------|
| Command | ```bash
claude "I need to build a landing page for Acme Corp.

Read the brief in PROJECT.md and content in content.md.

Execute the Build-Audit-Fix pattern:
1. GEMINI: Build the initial HTML/CSS landing page following the brand specs
2. CODEX: Audit the output for accessibility (WCAG 2.1 AA), SEO, and performance
3. OPUS: Fix all audit findings and deliver the final version

Start with Gemini building the page."
``` |
| Expected | Pattern execution begins |
| Verification | Claude acknowledges and starts orchestration |

### Step 6: Verify Gemini Build Phase

| Action | Monitor Gemini output |
|--------|----------------------|
| Expected | - HTML structure generated |
| | - CSS styling applied |
| | - Content integrated |
| | - Brand colors used |
| Verification | HTML/CSS output visible |

### Step 7: Verify Codex Audit Phase

| Action | Monitor Codex output |
|--------|---------------------|
| Expected | Audit covers: |
| | - Accessibility (WCAG 2.1 AA) |
| | - SEO (meta tags, headings, alt text) |
| | - Performance (image optimization suggestions) |
| Verification | Audit findings listed |

### Step 8: Verify Opus Fix Phase

| Action | Monitor Opus output |
|--------|---------------------|
| Expected | - Audit issues addressed |
| | - Fixes applied to code |
| | - Final version produced |
| Verification | Fixed code output visible |

### Step 9: Output File Verification

| Action | Check for generated files |
|--------|--------------------------|
| Expected | Landing page HTML file created |
| Verification | File exists and contains valid HTML |

### Step 10: Visual Verification

| Action | Open generated page in browser |
|--------|-------------------------------|
| Expected | - Page renders correctly |
| | - Brand elements visible |
| | - Mobile-responsive |
| Verification | Open HTML file in browser |

### Step 11: Accessibility Verification

| Action | Check accessibility of output |
|--------|------------------------------|
| Expected | - Proper heading hierarchy |
| | - Alt text on images |
| | - Color contrast adequate |
| Verification | Browser accessibility tools |

### Step 12: Timing Verification

| Action | Record total execution time |
|--------|----------------------------|
| Expected | Complete demo in under 15 minutes |
| Verification | Stopwatch from Step 5 to completion |

## Pass Criteria

- All three AI phases execute successfully
- Valid HTML/CSS output produced
- Page renders correctly in browser
- Audit findings are addressed
- Total time under 15 minutes

## Quality Checks

| Check | Expected |
|-------|----------|
| HTML Valid | No major validation errors |
| CSS Valid | No broken styles |
| Responsive | Works on mobile viewport |
| Brand Match | Colors/fonts match brief |
| Content Complete | All content sections present |

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Gemini timeout | Check Gemini API status |
| Codex not responding | Verify OpenAI key |
| Incomplete output | Check token limits |
| File not saved | Check write permissions |

## Demo Rescue Options

If live demo fails:
1. Show pre-recorded video at `/demo/outputs/before-after/`
2. Walk through static output files
3. Focus on methodology explanation

## Related Tests

- 004-demo-quick-audit.md
- 006-demo-content-audit.md
- 007-demo-parallel-tasks.md
