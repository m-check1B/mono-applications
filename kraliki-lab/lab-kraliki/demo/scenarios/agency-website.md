# Demo Scenario: Agency Website Build

**Duration:** 15 minutes
**Pattern:** Build-Audit-Fix
**Target audience:** Digital agencies, development shops

---

## Pre-Demo Setup (1 min)

```bash
# Open the sample project
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/demo/sample-projects/agency-client

# Show the project brief
cat PROJECT.md
```

---

## Part 1: Set the Context (2 min)

### What to Say:

> "This is a real project brief from a fictional B2B SaaS client. They need a marketing landing page built to their specs.
>
> Normally, you'd have a designer create mockups, a developer build it, then QA review it. Three people, multiple handoffs, days of back-and-forth.
>
> With Lab by Kraliki, we do this in one session with AI collaboration."

### What to Show:

- The PROJECT.md file with requirements
- The content.md file with copy
- "These are the same inputs you'd give your team"

---

## Part 2: Execute Build-Audit-Fix (10 min)

### Step 1: Trigger the Pattern

```bash
claude "I need to build a landing page for Acme Corp.

Read the brief in PROJECT.md and content in content.md.

Execute the Build-Audit-Fix pattern:
1. GEMINI: Build the initial HTML/CSS landing page following the brand specs
2. CODEX: Audit the output for accessibility (WCAG 2.1 AA), SEO, and performance
3. OPUS: Fix all audit findings and deliver the final version

Start with Gemini building the page."
```

### What to Narrate:

- "Watch how Claude orchestrates the work..."
- "Gemini is generating the initial structure..."
- "Now Codex is auditing - looking for issues we might miss..."
- "Opus is incorporating the feedback and polishing..."

### Step 2: Show the Output

- Display the generated HTML
- Open in browser (if possible)
- Show the audit report with issues found and fixed

---

## Part 3: Highlight the Value (2 min)

### What to Say:

> "What just happened:
> - One person (me) steered the process
> - Three specialized AIs collaborated
> - We got a production-ready page with QA included
>
> Traditional timeline: 2-3 days
> Lab by Kraliki: 10 minutes
>
> That's the 16x productivity we documented on Day 1."

### Objection Handling:

**"It's not perfect"**
> "Neither is a first draft from a junior dev. The difference is iteration speed - I can run another cycle in minutes, not days."

**"We'd still need a designer"**
> "For high-touch creative work, absolutely. But for 80% of your production work? This handles it."

---

## Part 4: Memory Demo (1 min)

```bash
# Query mgrep to show context retention
curl -s -X POST http://localhost:8001/v1/stores/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Acme Corp brand colors", "store_identifiers": ["magic_box_demo"], "top_k": 3}'
```

### What to Say:

> "Everything we discussed is now in memory. Tomorrow, I can ask 'What were Acme's brand colors?' and it remembers.
>
> No more digging through old Slack threads or lost Notion pages."

---

## Closing

> "This is one pattern. We have parallel execution for research, multi-AI voting for hard decisions, and more.
>
> Want to see how this would work for your specific workflows?"

**Next step:** Book a 30-minute scoping call

---

## Backup Plan

If live demo fails:
1. Show pre-recorded video: `/demo/outputs/before-after/agency-website-video.mp4`
2. Walk through the static outputs in `/demo/outputs/`
3. Focus on the methodology and results, not the live execution

---

*Agency Website Demo Script v1.0*
