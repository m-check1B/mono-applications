# CODEX Audit 02 – User Perspective

**Based on:** Personas & workflows in `docs/user-research/README.md`.

## 1. Conversation & Clarification
- ✅ Single canvas aligns with Solo Dev / Knowledge Worker need for continuous context.
- ❌ Clarification loop missing – orchestrator output is static text; no follow-up questions for “Plan my day”, “Break down goal”, “I’m overwhelmed”.
- ❌ Approvals don’t auto-run actions (no tasks/calendar entries).

## 2. Voice Capture
- ✅ Voice page records/uploads audio as requested in research (“Voice: create task Monday morning”).
- ❌ Voice and chat are siloed; transcripts don’t appear in main conversation.
- ❌ No live transcript or conversational clarifications mid-recording.

## 3. Deterministic Screens & CTAs
- ✅ All major tabs (calendar/time/tasks/projects/team/analytics) provide “Send to assistant” buttons reflecting “Simply In” expectation.
- ❌ Buttons only enqueue prompts; they don’t display inline assistant replies or auto-actions (e.g., create prep tasks) which Freelancers/Team Leads expect.

## 4. Orchestration Transparency
- ✅ Workflow card shows decision status/timestamp.
- ❌ No execution log; approvals disappear after refresh with no history. Users can’t recall “What did I approve last week?” (top requests #3 / #10).

## 5. Onboarding & Trust
- ❌ No persona-driven onboarding (e.g., Solo Dev morning routine template, Freelancer weekly review). Initial objections (“Another app?” “My workflow is unique”) go unaddressed in-product.
- ❌ BYOK/privacy messaging only exists in docs; UI doesn’t guide API key setup or show active provider states.

### User Gaps Summary
1. Lack of auto-clarification and auto-action blocks AI from acting like a “personal human assistant”.
2. Voice + deterministic surfaces feed context but do not receive assistant responses inline.
3. No execution tracking/history reduces trust and fails “Show me what I worked on last week”.
4. Onboarding/trust cues absent despite being top objections.

➡️ Next: Developer Audit (03) to scope engineering work needed to close these gaps.

