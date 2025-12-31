# Focus by Kraliki Template Pack

Template UI surfaces that sit above Kraliki Swarm for B2B knowledge capture,
decision-making, and management use cases. This is a template pack, not a full
product app.

## Purpose

- Provide thin UI templates that run inside Swarm containers
- Keep core orchestration inside Kraliki Swarm
- Support multi-user, tenant-per-container deployments
- Reuse Focus ideas without copying the Focus app

## Templates (Phase 1)

- **Knowledge**: capture, structure, and retrieve decision context
- **Project Management**: decisions, tasks, and execution tracking

Other Phase 1 templates live in their own template repos:
- Vibecoder (creative coding workflow)
- Calls (simple calling UI)
- Call Center (full call center UI)

## Operating Model

- **Backend**: Kraliki Swarm only (API + MCP)
- **UI**: template pages/modules rendered in Swarm container
- **Tenancy**: one container per customer (native multi-user)
- **Auth**: Swarm auth and roles

## What This Repo Includes

- Template manifests and scope docs
- UI layout guidelines aligned with Kraliki Swarm design language (Style 2026)
- Integration touchpoints (MCP endpoints, metrics, events)

## What This Repo Does Not Include

- Full Focus app codebase
- Standalone backend services
- Shared secrets or API keys

## Next Steps

- Add template UI scaffolds inside Swarm
- Implement template registry schema in Swarm
- Connect template metrics to Swarm analytics
