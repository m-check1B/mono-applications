# Lab by Kraliki - Mac Testing Guide

**Purpose:** Testing Lab by Kraliki via Mac Computer Use (Claude Desktop) with VM setup, AI orchestration testing, and pattern library validation.

---

## Overview

Lab by Kraliki is a B2B product - a pre-configured VM with multi-AI orchestration capabilities. Testing focuses on:

1. **VM Setup Verification** - Demo environment works correctly
2. **AI Orchestration Testing** - Patterns execute as expected
3. **Pattern Library Usage** - Documentation and templates are complete
4. **B2B Demo Readiness** - Sales materials are professional

---

## VM Setup Verification

### Connecting to Demo Environment

```bash
# From Mac terminal
ssh adminmatej@5.9.38.218

# Navigate to Lab by Kraliki
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki
```

### Environment Health Check

```bash
# Run status check
./demo/scripts/demo-start.sh

# Expected output:
# Lab by Kraliki Demo Environment
# ===========================
# Checking dependencies... OK
# Loading sample project... OK
# Initializing semantic search... OK
# Running test prompt... OK
```

### Component Verification

| Component | Check Command | Expected |
|-----------|---------------|----------|
| Claude Code | `claude --version` | Version info displayed |
| Gemini CLI | `gemini --version` | Version info displayed |
| Codex CLI | `codex --version` | Version info displayed |
| mgrep | `curl localhost:8001/health` | Status 200 |

---

## AI Orchestration Testing

### Pattern 1: Build-Audit-Fix

The core pattern that enables quality output from AI agents.

```bash
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/agency-client

claude "Build a landing page for a consulting agency.
Apply the Build-Audit-Fix pattern:
1. Gemini builds initial version
2. Codex audits for issues
3. Fix any problems found"
```

**Expected Behavior:**
1. Claude creates a plan
2. Delegates frontend work to Gemini
3. Codex reviews the output
4. Issues are identified and fixed
5. Final output is clean and professional

**Verification Checklist:**
- [ ] Build phase completes without errors
- [ ] Audit identifies real issues (not false positives)
- [ ] Fix phase addresses audit findings
- [ ] Output is usable for demo purposes

### Pattern 2: Parallel Execution

Multiple independent tasks running concurrently.

```bash
claude "Run these tasks in parallel:
1. Research: Find 5 AI consulting companies
2. Content: Draft a one-page service proposal
3. Social: Create 3 LinkedIn post ideas

Use appropriate workers for each."
```

**Expected Behavior:**
1. Claude identifies independent tasks
2. Multiple workers start simultaneously
3. Results merge into coherent output
4. Context maintained across all tasks

**Verification Checklist:**
- [ ] Tasks execute concurrently (check timing)
- [ ] No task blocks another
- [ ] Results are properly merged
- [ ] Output maintains context

### Pattern 3: Hard Problem Voting

Consensus-based decision making for complex problems.

```bash
claude "Technical decision needed:
Should this B2B SaaS use PostgreSQL or MongoDB?

Get opinions from multiple models:
- Claude: architecture perspective
- Gemini: developer experience
- Codex: performance analysis

Synthesize a recommendation."
```

**Expected Behavior:**
1. Each model provides independent analysis
2. Different perspectives are captured
3. Final recommendation synthesizes all input
4. Reasoning is documented

**Verification Checklist:**
- [ ] Multiple perspectives gathered
- [ ] Synthesis is balanced
- [ ] Recommendation is actionable
- [ ] Trade-offs clearly stated

---

## Pattern Library Usage

### Available Patterns

| Pattern | File | Use Case |
|---------|------|----------|
| Build-Audit-Fix | `patterns/build-audit-fix.md` | Quality output |
| Parallel Execution | `patterns/parallel-execution.md` | Concurrent tasks |
| Hard Problem Voting | `patterns/voting.md` | Complex decisions |

### Testing Pattern Documentation

```bash
# Check pattern library
ls /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/patterns/

# Read a specific pattern
cat patterns/build-audit-fix.md
```

**Verification:**
- [ ] Each pattern has clear documentation
- [ ] Examples are executable
- [ ] Expected outputs are defined
- [ ] Error handling is described

### Demo Scenarios

Located at `/demo/scenarios/`:

| Scenario | Duration | Best For |
|----------|----------|----------|
| quick-audit.md | 5 min | Executives |
| agency-website.md | 15 min | Digital agencies |
| content-audit.md | 10 min | SEO teams |
| parallel-tasks.md | 12 min | Consultancies |

**Test Each Scenario:**
```bash
# Navigate to scenarios
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/scenarios

# Read and execute
cat agency-website.md
# Follow instructions in the file
```

---

## Semantic Memory Testing

### mgrep Integration

Lab by Kraliki uses mgrep for semantic search across all project context.

```bash
# Test semantic search
curl -s -X POST http://localhost:8001/v1/stores/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to onboard a new customer",
    "store_identifiers": ["business_ops"],
    "top_k": 5
  }' | jq '.data[].text'
```

**Verification:**
- [ ] Query returns relevant results
- [ ] Response time under 2 seconds
- [ ] Lab by Kraliki docs included in results
- [ ] Pattern library indexed

### Context Persistence

Test that context persists across sessions:

```bash
# Session 1: Add context
claude "Remember: our target customer is digital agencies"

# Session 2: Recall context
claude "What kind of companies are we targeting?"
```

---

## CLAUDE.md Customization

### Customer Template Testing

Templates at `/templates/claude-md/`:

```bash
ls /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/templates/claude-md/

# Categories:
# - agency/
# - consultancy/
# - legal/
```

**Test Template Application:**
```bash
# Copy template to demo project
cp templates/claude-md/agency/CLAUDE.md demo/sample-projects/agency-client/

# Start Claude with context
cd demo/sample-projects/agency-client
claude "What do you know about this project?"
```

**Verification:**
- [ ] Template loads correctly
- [ ] Context is recognized by Claude
- [ ] Project-specific instructions followed
- [ ] Industry terminology understood

---

## Sample Projects

### Available Projects

| Project | Path | Purpose |
|---------|------|---------|
| Agency Client | `demo/sample-projects/agency-client/` | Agency demos |
| Consulting Deck | `demo/sample-projects/consulting-deck/` | Consultancy demos |
| Content Campaign | `demo/sample-projects/content-campaign/` | Content/SEO demos |

### Testing Sample Projects

```bash
# Agency project
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/agency-client
ls -la
# Should contain: project files, CLAUDE.md, sample assets

# Test execution
claude "Review this project and suggest improvements"
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Demo script fails | Missing npm deps | `npm install` in magic-box/ |
| mgrep no results | Stale index | Reindex: `scripts/index-all-github.sh` |
| Claude timeout | API rate limit | Wait 60s, retry |
| Worker not responding | Missing config | Check ~/.magic-box/.env |

### Debug Commands

```bash
# Check PM2 processes
pm2 status

# View recent logs
pm2 logs --lines 50

# Check API health
curl http://localhost:8001/health

# Verify API keys
cat ~/.magic-box/.env | grep -E "^[A-Z]"
```

---

## Quick Reference

```bash
# Connect
ssh adminmatej@5.9.38.218

# Navigate
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki

# Demo
./demo/scripts/demo-start.sh

# Test orchestration
claude "Hello, what can you do?"

# Check docs
ls docs/

# Test mgrep
curl -s localhost:8001/health
```

---

## Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Onboarding Runbook | `docs/onboarding-runbook.md` | 4-hour customer session |
| B2B Demo Guide | `demo/B2B_DEMO_GUIDE.md` | Sales demo playbook |
| CLI Routing | `docs/cli-routing-guide.md` | Technical routing |
| Cookbook | `/github/ai-automation/humans-work-needed/cookbooks/magic-box.md` | Full testing cookbook |

---

*Version: 1.0*
*Created: 2025-12-21*
*Linear Task: VD-164*
