# Lab by Kraliki Pro - 4-Hour Onboarding Session Runbook

**Version:** 1.0
**Last Updated:** December 2025
**Purpose:** Step-by-step guide for delivering the Lab by Kraliki Pro onboarding session

---

## Session Overview

| Aspect | Details |
|--------|---------|
| Duration | 4 hours (with breaks) |
| Format | Remote (screen share) or on-site |
| Participants | 1-3 customer team members |
| Deliverables | Working Lab by Kraliki, CLAUDE.md configured, first workflow completed |
| Price | €2,500 one-time (included with Pro/Enterprise tiers) |

## Success Criteria

By the end of the session, the customer will have:

1. A fully operational Lab by Kraliki environment
2. Custom CLAUDE.md configured for their business context
3. Completed their first multi-AI workflow end-to-end
4. Understanding of the core patterns (Build-Audit-Fix, Parallel Execution)
5. Confidence to work independently

---

## Pre-Session Checklist (Day Before)

### For Onboarding Lead

- [ ] Customer's VM provisioned and tested (Hetzner CPX31/41)
- [ ] SSH access credentials prepared (send via secure channel)
- [ ] Customer's industry/use case reviewed for context
- [ ] Backup demo environment ready (in case of issues)
- [ ] Calendar confirmed with customer

### For Customer (Send 24h Before)

```
Subject: Lab by Kraliki Onboarding - Prep Checklist

Hi [Name],

Tomorrow's session will be most productive if you have:

1. API Keys ready (at least one):
   - Anthropic (Claude) - Required
   - OpenAI (GPT/Codex) - Optional but recommended
   - Google (Gemini) - Optional but recommended

2. A laptop with:
   - Terminal access (Mac/Linux) or WSL (Windows)
   - SSH client installed
   - VS Code (recommended) with Remote-SSH extension

3. First project idea:
   - A real task you want to accomplish
   - Something that would normally take 4-8 hours
   - Examples: landing page, code audit, documentation

See you tomorrow!
```

---

## Session Structure

### Hour 1: Environment Setup & Orientation (60 min)

**0:00 - 0:10 | Welcome & Context Setting**

- Introduce yourself and the Lab by Kraliki concept
- Confirm customer's goals for the session
- Set expectations: "By the end, you'll have completed real work"

**0:10 - 0:30 | Environment Access**

```bash
# Customer connects to their VM
ssh customer@[vm-ip]

# Verify environment
magic-box status

# Expected output:
# ✓ CLIProxyAPI running
# ✓ Claude Code ready
# ✓ Gemini CLI ready
# ✓ Codex CLI ready
# ✓ mgrep semantic search active
```

**0:30 - 0:50 | Core Components Tour**

Walk through each component with live demonstration:

| Component | What It Does | Demo Command |
|-----------|--------------|--------------|
| CLIProxyAPI | Unified AI gateway | `magic-box api test` |
| Claude Code | Orchestrator | `claude "hello"` |
| Gemini CLI | Frontend/Research worker | `gemini "hello"` |
| Codex CLI | Backend/Audit worker | `codex "hello"` |
| mgrep | Semantic memory | `mgrep "test query"` |

**0:50 - 1:00 | API Key Configuration**

```bash
# Configure customer's API keys
magic-box config

# Or manually edit
nano ~/.magic-box/.env

# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# GOOGLE_API_KEY=...
```

---

### Hour 2: CLAUDE.md Customization (45 min + 15 min break)

**1:00 - 1:15 | CLAUDE.md Concept**

Explain the purpose:
- Project memory that persists across sessions
- Custom instructions for their business context
- Industry-specific patterns and terminology
- Security and compliance considerations

**1:15 - 1:45 | Build Their CLAUDE.md**

Work with customer to create their custom CLAUDE.md:

```markdown
# [Company Name] - Project Memory

## Business Context
[One paragraph about what they do]

## Our Terminology
[Industry-specific terms and definitions]

## Quality Standards
[Their specific requirements - code style, branding, compliance]

## Common Tasks
[Frequent workflows they'll use]

## Forbidden Actions
[Things the AI should never do for their context]
```

**1:45 - 2:00 | BREAK (15 min)**

Send them a resource:
- Link to pattern library
- Example CLAUDE.md from similar industry

---

### Hour 3: First Real Workflow (60 min)

**2:00 - 2:10 | Pattern Introduction**

Explain the Build-Audit-Fix pattern:

```
User Input → Opus (plan) → Gemini (build) → Codex (audit) → Opus (fix) → Output
```

**2:10 - 2:50 | Live Workflow Execution**

Work on the customer's real project:

1. **Define the task** (5 min)
   - What are we building?
   - What's the expected output?
   - What would success look like?

2. **Execute with Claude orchestrating** (30 min)
   ```bash
   claude "Build a [customer's task]. Use the Build-Audit-Fix pattern."
   ```

3. **Observe and explain** (5 min)
   - Point out how agents collaborate
   - Show how mgrep retains context
   - Highlight quality improvements from audit

**2:50 - 3:00 | Review Output**

- Did it meet expectations?
- What would they have done differently?
- Time comparison: How long would this take traditionally?

---

### Hour 4: Advanced Patterns & Independence (45 min + 15 min wrap-up)

**3:00 - 3:15 | Parallel Execution Pattern**

Demonstrate concurrent work:

```bash
claude "I need three things done in parallel:
1. Research competitor pricing
2. Draft an email template
3. Outline a blog post structure

Use parallel execution with Gemini for research and content."
```

**3:15 - 3:30 | Hard Problem Voting Pattern**

For complex decisions:

```bash
claude "I have a technical decision: Should we use PostgreSQL or MongoDB for this use case?

Get opinions from all available models and synthesize a recommendation."
```

**3:30 - 3:45 | Customer Solo Practice**

Have them run a workflow independently while you observe:

- Choose a new task
- Configure the approach
- Execute and iterate
- You only help if stuck

**3:45 - 4:00 | Wrap-Up & Next Steps**

**Document handoff:**
- SSH credentials (already sent)
- Support channel access
- Pattern library location
- How to reach us for questions

**Customer commitments:**
- First solo project within 48 hours
- Document one friction point
- Check-in call in 1 week

**Follow-up schedule:**
- Day 3: Async check-in message
- Day 7: 30-min call to address questions
- Day 30: Review call (optional upsell for advanced training)

---

## Troubleshooting Guide

### Common Issues During Onboarding

| Issue | Symptom | Fix |
|-------|---------|-----|
| API key invalid | "Authentication failed" | Verify key format, check billing |
| Rate limit hit | "429 Too Many Requests" | Wait 60s, or switch to different model |
| mgrep not responding | No search results | `magic-box restart mgrep` |
| SSH connection drops | Timeout | Check customer's network, use mosh |
| Model hallucinating | Incorrect output | Add constraints to CLAUDE.md |

### Escalation Path

1. **On-call engineer:** Slack #magic-box-support
2. **VM infrastructure:** Check Hetzner console
3. **API issues:** Check status pages (status.anthropic.com, etc.)

---

## Post-Session Checklist

### Immediately After

- [ ] Send thank you email with session recording (if recorded)
- [ ] Share CLAUDE.md they created (in case they lose it)
- [ ] Add customer to support channel
- [ ] Log session notes in CRM
- [ ] Schedule Day 7 follow-up call

### Day 3

- [ ] Send async check-in: "How's it going? Any blockers?"
- [ ] Share one relevant resource based on their use case

### Day 7

- [ ] 30-min call to address questions
- [ ] Gather feedback for improvement
- [ ] Identify upsell opportunities (enterprise, advanced training)

### Day 30

- [ ] Check-in email with usage stats (if available)
- [ ] Case study opportunity (if successful)
- [ ] Referral request (if happy)

---

## Session Materials

### Required

1. Onboarding script (this document)
2. CLAUDE.md template (industry-appropriate)
3. Pattern library access
4. Demo projects (backup if customer doesn't have a task)

### Optional

- Recording consent form
- Feedback survey link
- Case study permission form

---

## Metrics to Track

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to first output | < 15 min | Timestamp in session |
| Customer satisfaction | > 8/10 | Post-session survey |
| Solo success by Day 7 | > 80% | Follow-up call |
| 30-day retention | > 90% | Subscription status |

---

## Appendix: Demo Tasks by Industry

### For Agencies

- "Build a client proposal template with dynamic sections"
- "Create a social media content calendar for next month"
- "Audit this client's website for SEO issues"

### For Consultancies

- "Generate a market analysis report structure"
- "Create a stakeholder interview questionnaire"
- "Draft an executive summary template"

### For Legal/Compliance

- "Review this contract for standard clause deviations"
- "Create a compliance checklist for GDPR"
- "Draft a privacy policy template"

### For Coaching/Training

- "Create a workshop curriculum outline"
- "Generate assessment questions for a topic"
- "Build a client onboarding questionnaire"

---

*Last reviewed: December 2025*
*Next review: February 2026*
