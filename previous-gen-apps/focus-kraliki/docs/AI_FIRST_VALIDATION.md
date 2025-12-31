# AI-First Validation Checklist (Chat + Voice + Panels)

Use this quick list to validate the AI-first orchestration after changes. Prefer running these via chat; repeat with voice where possible.

1) Tasks (chat)
- Prompt: "Create a task 'Write summary' due tomorrow."
- Expect: AI calls task tool, Tasks panel opens, item appears in Tasks view without reload.

2) Knowledge Types (chat)
- Prompt: "Create an Idea called 'New onboarding flow'."
- Expect: AI asks/uses the correct typeId (Idea), item appears in Knowledge view.

3) Calendar (chat)
- Prompt: "Schedule a meeting with Alex tomorrow at 3pm."
- Expect: Event tool call, Calendar panel opens, event visible in range.

4) Time Tracking (chat)
- Prompt: "Start a focus timer for deep work."
- Expect: Timer tool call, Time panel opens, active timer visible; then "Stop my timer" stops it.

5) Workflow (chat)
- Prompt: "Run the weekly review workflow."
- Expect: Workflow execute tool call, Workflow panel opens, tasks created.

6) Analytics (chat)
- Prompt: "Show me my productivity analytics."
- Expect: Analytics tool call, Analytics panel opens with refreshed data.

7) Workspace (chat)
- Prompt: "Switch to workspace Alpha."
- Expect: Workspace switch tool call, projects/tasks reflect new workspace.

8) Theme (chat)
- Prompt: "Set theme to dark."
- Expect: Settings tool call, theme switches immediately.

9) Infra (chat)
- Prompt: "Check system status."
- Expect: Infra status tool call, Infra panel opens with status/logs.

10) Voice parity
- Repeat #1 and #3 via voice: record a command, see transcript+intent, panels open, items created.
