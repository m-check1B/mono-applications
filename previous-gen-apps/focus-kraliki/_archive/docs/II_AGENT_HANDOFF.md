# Focus Lite → II-Agent Integration Handoff

## Direction
- II-Agent (in `/ii-agent/`) is the orchestration core. Deterministic requests stay within Focus Lite; escalations mint `/agent/sessions` and delegate to II-Agent, which executes via `focus_tools` and streams status back.

## Tracks & Ownership
1. **Platform Hardening (Track 1)**  
   - Resolve backend dependency conflicts (uv/pip), stabilize pytest, and add CI jobs that spin up II-Agent so full Focus → II-Agent → Focus roundtrips are tested. _Must finish first._ See [Environment & Tooling Audit](../sunday-completion/GLM/01-environment-tooling-audit.md) and [Testing & Observability Audit](../sunday-completion/GLM/06-testing-observability-audit.md).

2. **Clarification & Execution Loop (Track 2)**  
   - Extend `/ai/enhance-input` + `/ai/orchestrate-task` to emit escalation payloads. Mint II-Agent sessions, pass structured goals/context, and subscribe to execution events. Persist tool calls in telemetry. Backed by findings in [Developer Audit](../sunday-completion/CODEX/03_developer_audit.md) and [Hybrid Execution Guide](./HYBRID-EXECUTION-GUIDE.md).

3. **Assistant/Voice Unification (Track 3)**  
   - Build the shared `assistantStore` per the [AI-First Command Center Plan](./AI_FIRST_UI_PLAN.md). Stream II-Agent updates (voice + text) into the same canvas; workflow/execution drawers show live progress as requested in the [User Audit](../sunday-completion/CODEX/02_user_audit.md).

4. **Command History & Telemetry (Track 4)**  
   - Add `/assistant/commands` + `/ai/telemetry/history` so deterministic and II-Agent routes share a single timeline answering “What did I work on last week?” (top request in [User Research README](./user-research/README.md)).

5. **Persona Onboarding & Trust (Track 5)**  
   - Embed persona templates plus BYOK/privacy messaging, and expose toggles for Gemini File Search + II-Agent usage to counter documented objections ([Common Objections](./user-research/objections/common-objections.md), [Gemini File Search Guide](./GEMINI_FILE_SEARCH.md)).

6. **Integrations & Mobile (Track 6)**  
   - Ship invoice/billable exports, two-way Google Calendar sync, and the PWA/offline capture; update `focus_tools` so II-Agent can use the new APIs. Reference [Feature Request Backlog](./user-research/requests/BACKLOG.md) and [Freelancer Persona](./user-research/personas/02-freelancer.md).

7. **Command Center Shell (Track 7)**  
   - Implement the Assistant/Work/Insights shell with workflow/execution drawers and the Insights tab showing hybrid telemetry + BYOK status per the [AI-First Command Center Plan](./AI_FIRST_UI_PLAN.md).

## Parallelization
- Track 1 is the prerequisite for everything else.  
- Tracks 2–4 run in parallel once escalation payloads/event schemas are defined (Track 2 emits, Tracks 3–4 consume).  
- Tracks 5–7 can start after the shared store/telemetry shapes are agreed.  
- Track 6 is largely independent but should register new endpoints with `focus_tools`.

## Key References
- Hybrid routing rules: [Hybrid Execution Guide](./HYBRID-EXECUTION-GUIDE.md)  
- Command Center UI plan: [AI-First Command Center Plan](./AI_FIRST_UI_PLAN.md)  
- Personas & research: [User Research README](./user-research/README.md), [Common Objections](./user-research/objections/common-objections.md), [Feature Request Backlog](./user-research/requests/BACKLOG.md)  
- Audits: [User Audit](../sunday-completion/CODEX/02_user_audit.md), [Developer Audit](../sunday-completion/CODEX/03_developer_audit.md), [Environment & Tooling](../sunday-completion/GLM/01-environment-tooling-audit.md), [Testing & Observability](../sunday-completion/GLM/06-testing-observability-audit.md)  
- II-Agent capabilities & tools: [ii-agent README](../ii-agent/README.md), [`focus_tools.py`](../ii-agent/src/ii_agent/tools/focus_tools.py)
