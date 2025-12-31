# Focus by Kraliki Template Pack - Project Memory

Template UI surfaces for Kraliki Swarm. This repository is a template pack, not
an app with its own backend.

## Guardrails

- Do not copy the full Focus by Kraliki codebase.
- Keep templates thin: UI + config only.
- Use Kraliki Swarm design language (bold, uppercase sectioning, high-contrast).
- Assume Swarm handles auth, orchestration, and MCP calls.
- Multi-user by default; tenant per container.

## Structure

- `templates/`: per-template manifests and scope notes
- `docs/`: shared guidelines, contracts, and UX rules

## Template Contract (High Level)

Each template should document:
- Purpose and target workflow
- UI modules and states
- Required MCP endpoints
- Roles and permissions
- Metrics and audit logging

## Integration Notes

- Templates are rendered inside Swarm containers (no standalone hosting).
- Backend calls go to Swarm APIs or MCP (no direct provider keys).
