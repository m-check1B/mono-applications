# Lab by Kraliki Pro - B2B Demo Guide

Complete guide for demonstrating Lab by Kraliki to potential B2B clients.

---

## Quick Reference

| Scenario | Duration | Best For | File |
|----------|----------|----------|------|
| Quick Audit | 5 min | Initial call, busy executives | `scenarios/quick-audit.md` |
| Agency Website | 15 min | Digital agencies, dev shops | `scenarios/agency-website.md` |
| Content Audit | 10 min | SEO agencies, content teams | `scenarios/content-audit.md` |
| Parallel Tasks | 12 min | Consultancies, research teams | `scenarios/parallel-tasks.md` |

---

## Before Any Demo

### Environment Check (2 min)

```bash
./scripts/demo-start.sh
```

This verifies:
- Claude Code responding
- mgrep semantic search running
- Sample projects loaded
- Demo workspace ready

### Mental Prep

1. Know your prospect's industry
2. Have relevant sample project ready
3. Know which pattern matters most to them
4. Prepare 2-3 industry-specific examples

---

## Demo Structure (Standard 30-min Call)

### 0:00-0:05 | Rapport & Context
- Brief intro
- Ask about their current workflow
- Identify their biggest productivity pain

### 0:05-0:10 | Problem Framing
- Validate their pain
- Introduce the campfire vs kitchen metaphor
- Set up the 16x claim with proof

### 0:10-0:20 | Live Demonstration
- Run appropriate scenario
- Narrate what's happening
- Highlight orchestration, not just AI

### 0:20-0:25 | Value Connection
- Map demo to their specific use case
- Calculate rough ROI together
- Address objections

### 0:25-0:30 | Next Steps
- Beta offer if appropriate
- Full onboarding proposal
- Book follow-up

---

## Key Messages by Audience

### For Agencies

**Lead with:** Speed and leverage
**Key metric:** "1 person + Lab by Kraliki = 3-person team output"
**Example:** The 4 websites in 7 hours story
**Objection:** "Our clients want human touch" → "Your humans do the creative direction. AI does the production."

### For Consultancies

**Lead with:** Research quality and synthesis
**Key metric:** "Day 1 of an engagement produces more than Week 1 traditionally"
**Example:** Parallel research streams that converge into strategic insight
**Objection:** "We bill by the hour" → "Bill the same, deliver more value, win more referrals"

### For Tech Teams

**Lead with:** Code quality and audit coverage
**Key metric:** "Every PR reviewed by multiple specialized AIs"
**Example:** Security + performance + maintainability audit in minutes
**Objection:** "We already use Copilot" → "Copilot helps write code. Lab by Kraliki orchestrates workflows."

### For Content/SEO

**Lead with:** Production scale without quality loss
**Key metric:** "10x content output with built-in optimization"
**Example:** Blog post + social repurposing + SEO audit in one pass
**Objection:** "AI content is detectable" → "We produce with AI, humans refine. The audit catches issues."

---

## Objection Handling Matrix

| Objection | Response |
|-----------|----------|
| "Too expensive" | "Compare to team cost, not tool cost. €499/mo vs €5,000/mo for a junior." |
| "Can't trust AI" | "Neither can we - that's why we have audit loops. Every output is verified." |
| "We'd have to learn it" | "4-hour onboarding. First output in 15 minutes. We hand-hold you." |
| "Security concerns" | "Your VM, your data, your API keys. We never see your work." |
| "Already have AI tools" | "Those are ingredients. Lab by Kraliki is the kitchen that makes them work together." |
| "Need to see ROI first" | "2-week pilot, no commitment. If you don't see value, walk away." |

---

## Demo Rescue Tactics

### If AI is Slow

> "Real-time AI can vary. The important thing is the output quality - let me show you a completed example while this runs."

Show pre-built outputs in `/demo/outputs/before-after/`

### If AI Makes a Mistake

> "This is exactly why we have audit loops. Watch what happens when we catch an issue..."

Use the mistake as a teaching moment about the Build-Audit-Fix pattern.

### If They're Skeptical

> "I understand. Let me show you the documented results from Day 1..."

Open `ORIGIN_STORY.md` and show the actual metrics.

### If They Want Customization

> "Absolutely. That's what onboarding is for. We configure your CLAUDE.md with your terminology, your standards, your workflows."

Show template library at `/templates/claude-md/`

---

## Sample Project Quick Access

```bash
# Agency demo
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/agency-client

# Consulting demo
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/consulting-deck

# Content demo
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/content-campaign
```

---

## Post-Demo Actions

### Immediately After

1. Send follow-up email within 2 hours
2. Include:
   - Summary of what they saw
   - Answer to any open questions
   - Next steps with clear timeline
   - Beta/pilot pricing if discussed

### Email Template

```
Subject: Lab by Kraliki Demo Follow-Up - [Their Use Case]

Hi [Name],

Thanks for the time today. As promised, here's a summary:

What we demonstrated:
- [Pattern shown]
- [Output produced]
- [Time saved estimate]

Your specific use case:
- [How Lab by Kraliki applies to their workflow]
- [Estimated ROI based on discussion]

Next steps:
- [Specific action with date]

Questions? Reply here or book time: [Calendly link]

Best,
[Your name]
```

---

## Tracking Demo Success

Log every demo in CRM with:
- Prospect name/company
- Scenario shown
- Key pain point identified
- Objections raised
- Next step committed
- Likelihood to close (1-5)

---

## Resources

- Sales deck: `/marketing-2026/demos/magic-box-pro/MB-002_magic-box-pro-sales-deck.md`
- Pricing: Check current tier structure in `/applications/lab-kraliki/README.md`
- Case studies: Coming Q1 2026 (use Day 1 results for now)
- Technical spec: `/applications/lab-kraliki/docs/mvp-technical-spec.md`

---

*B2B Demo Guide v1.0 - December 2025*
