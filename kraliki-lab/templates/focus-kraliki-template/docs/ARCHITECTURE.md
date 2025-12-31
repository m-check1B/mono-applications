# Template Architecture

## Overview

These templates are UI layers rendered inside Kraliki Swarm containers. They do
not host their own backend services. All orchestration, auth, and data access
remain within Swarm.

## Flow

1. Swarm container boots with selected templates.
2. Template UI modules read state from Swarm APIs/MCP.
3. User actions emit Swarm events or invoke MCP tools.
4. Metrics and audit logs are recorded by Swarm.

## Tenancy

- One container per customer (native tenancy).
- Multi-user, role-based access inside container.
- No shared API keys or external credentials in the template layer.

## Data Boundaries

- Template UIs may read and write only via Swarm APIs.
- No direct provider keys in template code.
- Template state is derived from Swarm memory and workflow events.

