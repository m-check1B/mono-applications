# Template Guidelines

## Design Language

Match Kraliki Swarm visual system:
- Bold section headers (uppercase)
- Clear status badges
- High-contrast UI with disciplined color accents
- Dense, ops-friendly layouts

## Required UI Modules

Each template should include:
- **Overview**: current state and quick actions
- **Workflow**: steps, progress, and blockers
- **Context**: knowledge/notes and decision trail
- **Audit**: timeline of actions and approvals

## Roles

Minimum roles:
- Admin
- Operator
- Viewer

## Metrics

Track per-template:
- Active workflows
- Time-to-decision
- Human handoffs
- Error/retry rate

## Events

Templates should emit:
- `template.action.triggered`
- `template.decision.logged`
- `template.handoff.requested`
- `template.audit.updated`

