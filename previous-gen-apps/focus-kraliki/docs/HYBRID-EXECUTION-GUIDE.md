# Hybrid Execution Guide

Date: 2025-11-14  
Audience: engineering + product

This document captures the **real hybrid execution model** already present in Focus by Kraliki and defines how we decide between fast, deterministic API flows and ii-agent orchestration.

## 1. Reality Check – What Already Ships

| User Job | Deterministic Components | Notes |
| --- | --- | --- |
| Day planning (“show me priority tasks for today, plan my day”) | `/ai/tasks/prioritize`, `/ai/schedule/suggest`, `AISchedulerService` heuristics | All logic lives in `backend/app/routers/ai_scheduler.py` and `backend/app/services/ai_scheduler.py`; latency <5 s. |
| Idea lookup & ranking (“look up my ideas, what is 3 best to follow”) | Knowledge Hub CRUD + `/knowledge-ai` function-calling interface | `backend/app/routers/knowledge_ai.py` already runs structured prompts and tool calls. |
| Messy NL input (“add this gdahjdjasgj task to Vestec”) | `/ai/parse-task`, `/ai/enhance-input`, voice pipeline, `/tasks` CRUD | Runs entirely inside our API; fuzzy input resolved before storage. |
| CRUD / list (“list my projects”, “update settings”) | `/projects`, `/tasks`, `/settings`, etc. | Simple Postgres queries; no AI required. |
| Goal → plan (“Here is my goal, plan for it”) | `/workflow` templates + `/ai/orchestrate-task` for optional breakdown | Deterministic template execution; AI only to generate structured steps. |

ii-agent is already wired in through `/agent` + `/agent-tools` and eight lightweight tools in `ii-agent/src/ii_agent/tools/focus_tools.py`. It should stay optional and focused on work our routers cannot perform (browser automation, long-form research, cross-repo edits, etc.).

## 2. Decision Flow (Deterministic vs Orchestrator)

1. **Classify the request.**
   - Use `/ai/enhance-input` to capture `intent`, `confidence`, `detectedType`, and metadata.
   - For multi-step asks, call `/ai/orchestrate-task` to inspect the returned workflow (`len(workflow)`, dependency graph, estimated minutes).
2. **Evaluate routing criteria.**
   - Deterministic path when: `confidence >= 0.7`, workflow length ≤ 5 steps, no external systems mentioned, and the detected type maps to an existing router.
   - Escalate to ii-agent when any of the following are true:
     - `confidence < 0.5` **and** user explicitly asks for “research”, “code”, or “website”.
     - Workflow has > 5 linked steps **or** dependencies cross multiple workspaces/accounts.
     - User references tooling we don’t expose via REST (e.g., “open a browser and gather quotes”).
     - Backend raises a capability flag (e.g., missing integration) and handoff is required.
3. **Execute & log.**
   - Deterministic path calls the relevant router/service directly.
   - Orchestrator path:
     1. Issue `/agent/sessions` to mint a token.
     2. From the frontend, initialize ii-agent with `tool_args.enable_focus_tools = true` so it can call `/agent-tools/*` along with its standard toolkit.
     3. Include `escalation_reason` so telemetry can be correlated.

### Pseudocode Sketch

```python
def route_request(nl_input: str, context: dict):
    enhanced = ai_enhance_input(nl_input, context)
    if enhanced.intent in ("create_task", "update_task") and enhanced.confidence >= 0.7:
        return execute_deterministic(enhanced)

    workflow = ai_orchestrate_task(nl_input, context)
    complexity = len(workflow.steps)

    if complexity <= 5 and workflow.confidence >= 0.6:
        return run_workflow(workflow)

    return escalate_to_agent(
        nl_input,
        reason={
            "intent": enhanced.intent,
            "confidence": enhanced.confidence,
            "workflow_steps": complexity
        }
    )
```

## 3. Telemetry & Guardrails

| Metric | Why | Implementation Sketch |
| --- | --- | --- |
| Routing decisions (`deterministic` vs `orchestrated`) | Validate the 90/10 target with real data. | Log a structured event (user id, intent, confidence, route). |
| Latency per router | Confirm deterministic UX stays <5 s for high-frequency jobs. | Add FastAPI middleware or instrumentation via `time.perf_counter()`. |
| Agent escalations reason codes | Detect misuse/drift (e.g., repeated escalations for CRUD tasks). | Include `escalation_reason` payload when creating agent sessions; persist in Redis/Postgres. |
| Cost envelope | Compare OpenRouter usage vs ii-agent LLM spend. | Record model + tokens per `/ai/*` call and per agent session. |

## 4. Action Plan (Incremental)

1. **Instrument classification + routing (Week 1).**
   - Persist outputs from `/ai/enhance-input` and `/ai/orchestrate-task` in a lightweight `request_classifications` table or log stream.
   - Emit structured logs when a deterministic workflow handles a request vs when we hand off to ii-agent.
2. **Expose escalation UX (Week 1-2).**
   - Show “Send to ii-agent” in the dashboard when the classifier flags low confidence or the user explicitly requests automation beyond our scope.
3. **Review telemetry (Weekly).**
   - Validate that ≥85% of traffic stays on deterministic routers.
   - Adjust heuristics when false positives/negatives appear.
4. **Expand ii-agent tools only when needed.**
   - If telemetry shows repeated escalations because a REST capability is missing (e.g., calendar automation), add that router/tool pair instead of inventing speculative workflows.

## 5. Communication Checklist

- Update top-level README to describe this hybrid model and point to this guide.
- Remove claims about “27 workflow classes in 6 weeks” unless backed by code.
- Share telemetry dashboards with product so cost/perf expectations stay grounded.

The goal is to keep Focus by Kraliki fast for everyday productivity while giving users an escape hatch (ii-agent) for the rare heavyweight tasks. This guide documents how to do that with the system we already have.

> **Update (Dashboard Hybrid Router - Pending UI)**
>
> The Hybrid Router/Telemetry cards described here are not yet shipped in the dashboard. Use this as the target UX; current builds do routing server-side without a dedicated UI card.
