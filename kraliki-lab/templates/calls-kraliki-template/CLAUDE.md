# Calls Template - Project Memory

Lightweight calling UI template for Kraliki Swarm. UI-only.

## Guardrails

- Keep UI thin; Swarm handles orchestration and auth.
- Follow Kraliki Swarm design line (Style 2026).
- Assume multi-user, tenant-per-container deployments.
- No provider keys or direct model calls in the template layer.

## Structure

- `template.json`: template manifest
- `README.md`: scope and flows
