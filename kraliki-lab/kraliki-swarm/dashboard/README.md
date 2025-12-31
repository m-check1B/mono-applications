# Kraliki Swarm Dashboard

Web UI for the Kraliki Swarm control plane and template delivery surface.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Swarm is the shell. Voice is the engine.
Templates + modules are the UI surface.
========================================

## What Lives Here

- Swarm control UI (agents, status, observability)
- Feature pages for templates (Focus, Speak, Learn)
- Entry points to standalone modules when needed

## Development

```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard
pnpm install
pnpm dev
```

## Notes

- This UI should stay **light**; heavy workflows live in templates.
- Standalone apps are optional; default delivery is via Swarm.
