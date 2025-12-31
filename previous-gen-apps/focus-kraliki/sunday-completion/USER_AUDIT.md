# User Perspective Audit

**Research alignment:** Findings map to the personas/workflows documented in `docs/user-research/README.md`, especially the Solo Developer, Freelancer, Knowledge Worker, and Team Lead use cases.

## Conversation & Clarification
- ✅ `/dashboard` delivers the “single canvas” the user research calls for (chat + workflow + execution feed). This satisfies **Solo Dev** and **Knowledge Worker** needs for context continuity.
- ⚠️ **Clarification missing:** Top requests like “Plan my day” or “Break down [goal]” expect the assistant to ask follow-up questions. Currently the orchestrator prints a plan and stops, so Freelancers/Team Leads still do manual clarification.
- ⚠️ **No automated follow-through:** Approvals don’t trigger deterministic actions (calendar events, task creation). This violates the “Simply Out” principle for overwhelmed users (“Help reorganize”, “Show priority tasks”).

## Voice Capture
- ✅ `/dashboard/voice` supports voice memos (“Voice: create task for Monday morning”, “Capture idea”). This matches the research emphasis on voice input.
- ⚠️ **Siloed experience:** Voice transcripts don’t stream into the main assistant thread; users can’t say “Summarize what I just dictated” without context switching.
- ⚠️ **No live clarifications:** Overwhelmed users shout commands; they expect the assistant to interrupt if details are missing. Our voice flow is one-shot audio upload, not conversational.

## Deterministic Surfaces (Calendar/Time/Tasks/Projects/Team/Analytics)
- ✅ Each area now has assistant CTAs, supporting the “Simply In” need to push context without retyping.
- ⚠️ **Lack of follow-up instructions:** When a Freelancer clicks “Review portfolio,” the assistant only enqueues a prompt and replies later. There is no inline summary or highlight on the projects boards.
- ⚠️ **Execution Drawer is manual:** Users still have to click “Mark complete” or “Edit details”; the assistant never performs actions like “Create prep task for tomorrow’s meeting” automatically.

## Orchestration Transparency
- ✅ Workflow card now displays decision status/timestamp for approvals, acknowledging research needs for trust.
- ⚠️ **No execution log**: After approval the user sees no progress indicator or action feed. Team Leads (needing visibility) can’t tell if anything happened.
- ⚠️ **History resets**: There is no backlog of prior workflows, so users can’t reference “What did I approve last week?” (a high-frequency question per research).

## Onboarding & Guidance
- ⚠️ New users see no persona-specific walkthrough (“Solo Dev morning routine,” “Freelancer weekly review”). Given the research emphasis on first-run objections, we need scenario templates.
- ⚠️ API dependency instructions (voice/orchestrator) live only in docs; the UI doesn’t surface “connect calendar,” “bring your own key,” or privacy assurances.

## Key Gaps vs. Research Requests
1. **Plan/clarify** — assistant must ask follow-ups for “Plan my day,” “Help me choose idea,” “I’m overwhelmed.”
2. **Act automatically** — approvals should create tasks/events/files; right now they only change text.
3. **Voice parity** — voice inputs should feed the same loop as text with live clarifications.
4. **Trust & onboarding** — show status (“listening…”, “executing step 2/5”), provide persona-based starter workflows, highlight privacy/BYOK settings in-app.
