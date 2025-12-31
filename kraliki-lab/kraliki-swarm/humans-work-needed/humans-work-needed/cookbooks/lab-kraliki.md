# Mac Computer Use Cookbook: Lab by Kraliki

**App:** lab-kraliki
**Description:** B2B Multi-AI Orchestration Stack - the 16x productivity multiplier
**Created:** 2025-12-21
**Linear:** VD-164

---

## Purpose

This cookbook enables Mac Computer Use (Claude Desktop) to perform visual and manual testing of Lab by Kraliki. Since Lab by Kraliki is a B2B product sold as a VM setup, testing focuses on:

1. Demo environment verification
2. Onboarding flow testing
3. B2B sales materials review
4. Pattern library validation

---

## Access Information

### Demo Environment

| Component | Access Method |
|-----------|---------------|
| Demo VM | SSH to dev server (5.9.38.218) |
| Documentation | `/github/applications/lab-kraliki/docs/` |
| Demo Materials | `/github/applications/lab-kraliki/demo/` |
| Pattern Library | `/github/applications/lab-kraliki/patterns/` |
| Landing Page | TBD (lab.kraliki.com) |

### SSH Access

```bash
# Connect to dev server
ssh adminmatej@5.9.38.218

# Navigate to Lab by Kraliki
cd /home/adminmatej/github/applications/lab-kraliki
```

---

## Visual Elements to Verify

### 1. Demo Environment Check

**Path:** `/home/adminmatej/github/applications/lab-kraliki/demo/`

```
Run: ./demo/scripts/demo-start.sh

VERIFY:
[ ] Script executes without errors
[ ] Claude Code responds to test prompt
[ ] mgrep semantic search returns results
[ ] Sample projects accessible
[ ] Demo workspace initialized
```

### 2. Sample Projects Structure

**Path:** `/home/adminmatej/github/applications/lab-kraliki/demo/sample-projects/`

```
VERIFY:
[ ] agency-client/ folder exists with sample files
[ ] consulting-deck/ folder exists with sample files
[ ] content-campaign/ folder exists with sample files
[ ] All projects loadable by AI agents
```

### 3. B2B Demo Scenarios

**Path:** `/home/adminmatej/github/applications/lab-kraliki/demo/scenarios/`

| Scenario | Duration | Target Audience |
|----------|----------|-----------------|
| quick-audit.md | 5 min | Executives |
| agency-website.md | 15 min | Digital agencies |
| content-audit.md | 10 min | SEO/Content teams |
| parallel-tasks.md | 12 min | Consultancies |

```
VERIFY each scenario:
[ ] File exists and is readable
[ ] Instructions are clear and actionable
[ ] Expected outputs documented
[ ] Time estimates realistic
```

### 4. Documentation Quality

**Path:** `/home/adminmatej/github/applications/lab-kraliki/docs/`

| Document | Purpose | Verify |
|----------|---------|--------|
| onboarding-runbook.md | 4-hour customer session | Complete, professional |
| beta-customers.md | Customer tracking | Up to date |
| cli-routing-guide.md | Technical routing | Accurate |
| mvp-technical-spec.md | Tech spec | Complete |

---

## AI Orchestration Testing

### Test 1: Build-Audit-Fix Pattern

```bash
# SSH to dev server
cd /home/adminmatej/github/applications/lab-kraliki/demo/sample-projects/agency-client

# Start Claude orchestrator
claude "Build a simple landing page for a consulting agency. Use the Build-Audit-Fix pattern."

EXPECTED:
[ ] Claude orchestrates the task
[ ] Frontend worker (Gemini) builds initial page
[ ] Audit worker (Codex) reviews for issues
[ ] Claude coordinates fixes
[ ] Final output is clean and usable
```

### Test 2: Parallel Execution Pattern

```bash
claude "Execute in parallel:
1. Research top 3 competitors in consulting
2. Draft a one-page proposal template
3. Create 5 social media post ideas

Use Gemini for research and content."

EXPECTED:
[ ] Multiple tasks start concurrently
[ ] Results merge correctly
[ ] Context maintained across workers
[ ] Output organized by task
```

### Test 3: mgrep Semantic Memory

```bash
# Search for context
mgrep "how to onboard new customer"

# Or via API
curl -s -X POST http://localhost:8001/v1/stores/search \
  -H "Content-Type: application/json" \
  -d '{"query": "onboarding process", "store_identifiers": ["magic_box"], "top_k": 5}'

EXPECTED:
[ ] Returns relevant results from Lab by Kraliki docs
[ ] Pattern library entries included
[ ] Response time < 2 seconds
```

---

## Payment Flows

### Current Status: Not Yet Implemented

Lab by Kraliki billing will use Stripe. Current pricing model:

| Tier | Price | Status |
|------|-------|--------|
| Starter | EUR 299/mo | Not live |
| Pro | EUR 499/mo | Not live |
| Enterprise | EUR 10K+/yr | Custom quotes |

### Future Payment Testing (When Live)

```
TEST: Demo Request Flow
1. Visit landing page (lab.kraliki.com)
2. Fill demo request form
3. Verify lead captured in CRM
4. Check email confirmation sent

TEST: Stripe Checkout (Test Mode)
1. Use Stripe test card: 4242 4242 4242 4242
2. Complete checkout flow
3. Verify subscription created
4. Check VM provisioning triggered
```

---

## OAuth/Identity Setup

### Current Status: Not Required

Lab by Kraliki uses SSH access for customer VMs. No OAuth flows needed for MVP.

### Future Considerations

If dashboard added:
- Zitadel integration (identity.verduona.com)
- Google OAuth for enterprise SSO
- API key management for CLIProxyAPI

---

## Expected States (Screenshots)

Since Lab by Kraliki is primarily CLI-based, expected states are command outputs rather than visual screenshots.

### Healthy Environment

```
$ lab-kraliki status

Lab by Kraliki Environment Status
============================
[ OK ] CLIProxyAPI     : Running on 127.0.0.1:8000
[ OK ] Claude Code     : Installed, v1.x.x
[ OK ] Gemini CLI      : Installed, configured
[ OK ] Codex CLI       : Installed, configured
[ OK ] mgrep           : Running on 127.0.0.1:8001
[ OK ] Demo workspace  : /home/user/lab-kraliki-demo

Ready to work!
```

### Demo Execution Output

```
$ ./demo/scripts/demo-start.sh

Lab by Kraliki Demo Environment
===========================
Checking dependencies... OK
Loading sample project... OK
Initializing semantic search... OK
Running test prompt... OK

Demo ready! Try:
  claude "Hello, describe what you can do"

Press Ctrl+C to exit demo mode.
```

---

## Testing Checklist

### Pre-Testing

- [ ] SSH access to dev server working
- [ ] Lab by Kraliki repo up to date (git pull)
- [ ] Demo scripts executable
- [ ] API keys configured (if testing live orchestration)

### Core Functionality

- [ ] Demo start script runs clean
- [ ] Sample projects load correctly
- [ ] Build-Audit-Fix pattern works
- [ ] Parallel execution pattern works
- [ ] mgrep returns relevant results

### Documentation

- [ ] Onboarding runbook complete and accurate
- [ ] B2B demo guide covers all scenarios
- [ ] CLI routing guide matches current setup
- [ ] Beta customers doc up to date

### Sales Materials

- [ ] Demo scenarios are compelling
- [ ] Time estimates are realistic
- [ ] Output examples are professional
- [ ] Objection handling matrix complete

---

## Reporting Issues

### If Tests Fail

1. Document the failure:
   ```bash
   # SSH to dev server
   cd /home/adminmatej/github/ai-automation/humans-work-needed
   # Create issue: HW-XXX_lab-kraliki-bug.md
   ```

2. Update features.json if needed:
   ```bash
   cd /home/adminmatej/github/ai-automation/software-dev/planning
   # Add bug fix feature with appropriate priority
   ```

3. Notify via Linear:
   - Label: bug, lab-kraliki
   - Priority based on severity

### Common Issues

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Demo script fails | Missing dependencies | Run `npm install` in lab-kraliki |
| mgrep no results | Index stale | Reindex: `scripts/index-all-github.sh` |
| Claude not responding | API key invalid | Check ~/.lab-kraliki/.env |
| Slow responses | Rate limiting | Wait 60s, try again |

---

## Quick Reference

```bash
# SSH Connection
ssh adminmatej@5.9.38.218

# Navigate to Lab by Kraliki
cd /home/adminmatej/github/applications/lab-kraliki

# Run demo
./demo/scripts/demo-start.sh

# Check health
lab-kraliki status

# View documentation
ls docs/

# Test mgrep
curl -s -X POST http://localhost:8001/v1/stores/search \
  -H "Content-Type: application/json" \
  -d '{"query": "magic box orchestration", "store_identifiers": ["business_ops"], "top_k": 3}'
```

---

*Cookbook Version: 1.0*
*Created: 2025-12-21*
*For: Mac Claude Desktop Computer Use*
*Linear Task: VD-164*
