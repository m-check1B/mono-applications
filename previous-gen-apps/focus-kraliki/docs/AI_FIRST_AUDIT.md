# AI-First Architecture Audit & Handoff Plan

## 🎯 Goal
Achieve a fully "AI-First" user experience where the intelligent chatbot (text/voice) serves as the primary interface for **all** application capabilities, including data management (Context), user settings, and infrastructure operations. The UI should dynamically orchestrate views ("Context Panels") based on user intent, minimizing the need for manual navigation while retaining essential manual controls.

## 🔍 Audit Findings

### ✅ What's Working
1.  **Context Panel Architecture**: The frontend now supports a `ContextPanel` system that slides in to provide relevant views (`TasksView`, `KnowledgeView`, `TimeTrackingView`) without navigating away from the chat.
2.  **Unified Item Model**: The frontend `TasksView` has been refactored to use the unified `KnowledgeItem` backend model (filtering by type="Task"), aligning with the "one system for all items" vision.
3.  **Manual Controls**: Essential manual controls (create, delete, toggle) exist within these views.
4.  **Agent Tools (Basic)**: The `ii-agent` has tools to Create/Update/List Knowledge Items, Tasks, and Projects, allowing the AI to manipulate this data.

### ❌ Critical Gaps (updates applied; keep validating UX)

#### 1. Agent Tools for Settings & Infrastructure
✅ Shipped: `backend/app/routers/agent_tools.py` now exposes `/agent-tools/settings/update`, `/agent-tools/infra/status`, and `/agent-tools/infra/logs` (references `backend/app/routers/infra.py`).  
🔍 Validation needed: Ensure ii-agent maps to these via `focus_tools.py` and that frontend reacts to tool results (theme switch, infra panel).

#### 2. Backend Endpoints
✅ Shipped: `backend/app/routers/infra.py` provides `/infra/status`, `/infra/logs/{service}`, and `/infra/restart/{service}` (guarded, uses prod scripts). Agent tools proxy these.  

#### 3. Frontend Reactivity Gaps
-   **Side Effects**: If the AI executes a tool like `update_user_preferences(theme='dark')`, the frontend `UnifiedCanvas` displays the tool call but does not automatically trigger a state update (e.g., switching the theme). The application relies on page reloads or manual store updates.
-   **Infra View**: There is no `InfraView` in the `ContextPanel` to show logs or status dashboards when the user asks "System status".

## 🛠️ Handoff Plan (Next Iteration)

The next development session should focus on closing these gaps to complete the "AI-First" vision.

### Phase 1: Backend Expansion (Agent Tools)

1.  **Create `InfraRouter` (`backend/app/routers/infra.py`)**:
    -   Endpoint `GET /infra/status`: Wraps `scripts/monitor.sh` or checks Docker status.
    -   Endpoint `POST /infra/restart/{service}`: Restarts a service (requires careful security handling, perhaps only in dev/admin mode).
    -   Endpoint `GET /infra/logs/{service}`: Returns tail of logs.
    -   *Security Note*: Ensure these are protected and only accessible by admin or the authenticated owner in single-user mode.

2.  **Expand `AgentToolsRouter` (`backend/app/routers/agent_tools.py`)**:
    -   Add `POST /agent-tools/settings/update`: To update user preferences (theme, etc.).
    -   Add `GET /agent-tools/infra/...`: Proxy to the new Infra endpoints.

3.  **Update `ii-agent` Tools (`ii-agent/src/ii_agent/tools/focus_tools.py`)**:
    -   Implement `UpdateSettingsTool`.
    -   Implement `CheckInfraStatusTool`, `RestartServiceTool`, `GetLogsTool`.

### Phase 2: Frontend Orchestration

1.  **Implement `InfraView.svelte`**:
    -   Create `frontend/src/lib/components/dashboard/InfraView.svelte`.
    -   Display health status, resource usage, and logs.
    -   Add manual controls (Restart buttons).
    -   Register in `ContextPanel.svelte` and `contextPanelStore`.

2.  **Enhance `UnifiedCanvas` for Reactivity**:
    -   Listen for specific `TOOL_RESULT` events from the agent.
    -   If `update_settings` tool succeeds, automatically refresh `settingsStore` or `userStore` to reflect changes (e.g., theme switch) immediately.
    -   If `check_infra_status` tool is called, automatically open the `InfraView` panel.

3.  **Orchestration Logic**:
    -   Ensure the AI (System Prompt) knows it can "Show" these panels.
    -   The `UnifiedCanvas` already handles some intent detection, but ensuring the *Agent* calls the right tool and the *Frontend* reacts to that tool call is key.

### Phase 3: Verification
-   **Test**: "Change my theme to dark" -> Agent calls tool -> Frontend updates theme instantly.
-   **Test**: "System status" -> Agent calls tool -> Frontend opens Infra Panel.
-   **Test**: "Restart backend" -> Agent calls tool -> Backend restarts (and frontend handles the disconnect gracefully).

---
**Technical Context**:
-   **Backend**: FastAPI (`app/routers/agent_tools.py` is the key integration point).
-   **Frontend**: SvelteKit (`UnifiedCanvas.svelte` receives agent events; `ContextPanel.svelte` manages views).
-   **Agent**: Python-based `ii-agent` (Tool definitions in `focus_tools.py`).
