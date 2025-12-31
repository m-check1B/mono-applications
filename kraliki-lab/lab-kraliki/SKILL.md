---
name: lab-kraliki
description: Multi-AI orchestration stack and product playbook for Lab by Kraliki. Use when working on multi-agent workflows, AI orchestration patterns, VM provisioning, semantic memory (mgrep), product docs, onboarding flows, or billing/metering for the Lab by Kraliki product (Claude orchestrator + Gemini frontend + Codex audit).
---

# Lab by Kraliki

Use Lab by Kraliki as a pre-configured multi-AI orchestration stack that delivers 16x productivity gains by combining specialized AI agents, semantic memory, and proven workflow patterns.

## Architecture Overview

Review the architecture to understand agent roles, memory, and execution patterns.

```
┌─────────────────────────────────────────────┐
│  LAB BY KRALIKI                                  │
├─────────────────────────────────────────────┤
│  ORCHESTRATOR (Claude Opus)                 │
│  ├── Context & memory (mgrep semantic)      │
│  ├── Strategy & continuity                  │
│  └── Quality control                        │
│                                             │
│  WORKERS                                    │
│  ├── Gemini CLI (frontend, research)        │
│  └── Codex CLI (audit, backend)             │
│                                             │
│  PATTERNS                                   │
│  ├── Build → Audit → Fix                    │
│  ├── Parallel execution                     │
│  └── Hard problem voting                    │
│                                             │
│  MEMORY                                     │
│  ├── Semantic search (mgrep)                │
│  ├── Pattern library                        │
│  └── Decision docs                          │
└─────────────────────────────────────────────┘
```

## Product Components

Use this table to track what is ready versus still in progress.

| Component | Purpose | Status |
|-----------|---------|--------|
| Hetzner VM | Pre-configured infrastructure (EU/US) | Ready |
| CLIProxyAPI | Unified AI gateway (Claude/GPT/Gemini) | Ready |
| Claude Code | Orchestrator CLI | Ready |
| Gemini CLI | Frontend/Research worker | Ready |
| Codex CLI | Audit/Backend worker | Ready |
| mgrep | Semantic memory | Ready |
| Prompt Library | Polished workflows | In Progress |

## Business Model

Use this pricing table for positioning and sales conversations.

| Tier | Price | Target |
|------|-------|--------|
| Starter | €299/mo | Freelancers |
| Pro | €499/mo | Agencies |
| Enterprise | €10K+/yr | Large orgs |
| Setup + Training | €2,500 | One-time |

Margin: 80%+ (cost: €50-100/mo per VM)

## Key Patterns

Apply these patterns when implementing Lab by Kraliki workflows.

### Build → Audit → Fix

1. Gemini builds frontend/content
2. Codex audits for issues
3. Claude orchestrates fixes
4. Repeat until quality bar met

### Parallel Execution

- Multiple workers on independent tasks
- Orchestrator manages context
- Results merged at checkpoints

### Hard Problem Voting

- All agents propose solutions
- Best approach selected
- Execution with consensus

## Folder Structure

Use this structure to locate product documentation, demos, and operational scripts.

```
magic-box/
├── README.md           # Full product concept
├── CLAUDE.md           # Project memory
├── SKILL.md            # This file (agentskills.io format)
├── docs/               # User documentation
│   ├── mvp-technical-spec.md
│   ├── onboarding-runbook.md
│   ├── cli-routing-guide.md
│   ├── beta-customers.md
│   └── landing-page-copy.md
├── templates/          # Customer CLAUDE.md templates
│   └── claude-md/      # By industry (agency, consultancy, legal)
├── demo/               # B2B demo materials
│   ├── scenarios/      # Demo workflows
│   ├── scripts/        # Demo automation
│   └── sample-projects/
├── stack/              # Docker/infrastructure configs
├── prompts/            # Polished prompt library
├── patterns/           # Workflow patterns
└── scripts/            # Setup and management scripts
```

## Target Customers

Target these segments when building outreach and positioning.

### Primary: Agencies & Consultancies

- Digital agencies needing capacity
- Consulting firms wanting leverage
- Freelancers wanting to scale
- Dev shops with backlog overflow

**Value Prop:** One person + Lab by Kraliki = 4-person team output

### Secondary: Tech-Forward Companies

- Startups wanting speed
- Product teams with bottlenecks
- Innovation labs

## Competitive Moat

Reference these advantages when drafting sales or marketing material.

| Advantage | Why It Works |
|-----------|--------------|
| Memory (mgrep) | More use = harder to leave |
| Pattern Library | 500+ tested patterns |
| Smart Proxy | Auto-optimize prompts |
| Community | Contributors create value |
| First Mover | Nobody else sells this |

## Related Files

| File | Purpose |
|------|---------|
| `/business-automation/patterns/multi-ai-orchestration.md` | The proven pattern |
| `/matej-planning/long.md` | Strategy context |
| `/marketing-2026/demos/magic-box-pro/` | Sales materials |

## Development Commands

```bash
# Demo workflow
./demo/scripts/demo-start.sh

# Run specific scenario
./demo/scripts/run-scenario.sh agency-website

# Reset demo environment
./demo/scripts/demo-reset.sh
```

---

*Lab by Kraliki: The team multiplier. Born December 2, 2025.*
