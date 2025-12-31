# Magic Box (Kraliki Box)

**Multi-AI Orchestration Platform for 16x Productivity**

This directory packages the one-click provisioning scripts for customer VMs.

## One-Click Install

```bash
# From a fresh Ubuntu 22.04+ VM (as root)
curl -fsSL https://raw.githubusercontent.com/YOUR_ORG/magic-box/main/scripts/setup-complete.sh | sudo bash
```

The script will:
- Detect your OS and architecture
- Install Docker, Docker Compose, and all dependencies
- Set up admin user with SSH key authentication
- Deploy AI services (Infinity, Qdrant, mgrep, Traefik)
- Install AI CLI tools (Claude, Gemini, OpenAI)
- Configure firewall and security hardening
- Prompt for API keys or use provided keys file
- Verify installation and show success message

**Full Setup Guide**: See `docs/SETUP.md` for detailed instructions, requirements, and troubleshooting.

## Quick Start (Local Development)

```bash
# Clone and run locally
git clone https://github.com/YOUR_ORG/magic-box.git
cd magic-box
sudo ./scripts/provision.sh
```

## What's Included

- Docker + Docker Compose
- Traefik reverse proxy
- CLIProxyAPI with API keys
- Claude Code, Gemini CLI, Codex CLI
- mgrep semantic search services
- Auto-start on boot + verification
- **Polished Prompt Library** (see below)

## Prompt Library

Industry-tested prompts for multi-AI orchestration. See `prompts/README.md` for full documentation.

**22 production-ready prompts across 5 categories.**

### Directory Structure

```
prompts/
├── orchestrator/                # Claude Opus orchestration (5 prompts)
│   ├── task-decomposition.md    # Break complex tasks into subtasks
│   ├── quality-control.md       # Review and validate work
│   ├── context-management.md    # Maintain project context
│   ├── strategic-planning.md    # High-level project planning
│   └── multi-step-reasoning.md  # Complex logical reasoning
│
├── workers/                     # Worker-specific prompts (8 prompts)
│   ├── gemini/                  # Gemini CLI prompts
│   │   ├── frontend-builder.md  # React/Svelte/Vue generation
│   │   ├── researcher.md        # Research and documentation
│   │   └── documentation.md     # Technical writing
│   │
│   ├── codex/                   # Codex/OpenAI prompts
│   │   ├── backend-builder.md   # API/server code generation
│   │   ├── code-auditor.md      # Security and quality audits
│   │   └── security-analyzer.md # Security-focused analysis
│   │
│   └── claude/                  # Claude-specific prompts
│       ├── translator.md        # Translation and localization
│       └── debugger.md          # Code debugging specialist
│
├── content/                     # Content generation (3 prompts)
│   ├── blog-writer.md           # SEO-optimized blog posts
│   ├── social-media.md          # Platform-specific social content
│   └── marketing-copy.md        # Conversion-focused copy
│
├── data/                        # Data analysis (2 prompts)
│   ├── data-analyzer.md         # Business insights and visualization
│   └── summarizer.md            # Document summarization
│
└── patterns/                    # Multi-AI workflow patterns (4 prompts)
    ├── build-audit-fix.md       # Builder -> Auditor -> Fixer cycle
    ├── parallel-execution.md    # Independent parallel tasks
    ├── hard-problem-voting.md   # Multi-model consensus
    └── research-implement.md    # Research first, then build
```

### Quick Usage

```bash
# Use orchestrator to decompose a task
claude --prompt "$(cat prompts/orchestrator/task-decomposition.md)" \
  "Build a user authentication system"

# Use build-audit-fix pattern
./prompts/patterns/build-audit-fix.py "Build user registration API"

# Run parallel workers
claude --prompt "prompts/workers/gemini/frontend-builder.md" "Build login UI" &
codex --prompt "prompts/workers/codex/backend-builder.md" "Build auth API" &
wait
```

## Landing Page

Production-ready landing page with Stripe checkout integration:

- `docs/landing-page.html` - Main landing page (ready to deploy)
- `docs/landing-page-copy.md` - Copy content (English + Czech)
- `docs/DEPLOYMENT.md` - Complete deployment guide
- `scripts/configure_stripe_links.sh` - Inject Stripe payment links

### Configuring Stripe Payment Links

1. Create payment links in Stripe Dashboard:
   - https://dashboard.stripe.com/products/payment-links

2. Add to `.env`:
   ```bash
   STRIPE_PAYMENT_LINK_STARTER=https://buy.stripe.com/...
   STRIPE_PAYMENT_LINK_PRO=https://buy.stripe.com/...
   STRIPE_PAYMENT_LINK_ENTERPRISE=https://buy.stripe.com/...
   ```

3. Run configuration script:
   ```bash
   ./scripts/configure_stripe_links.sh
   ```

The script will:
- Backup the current landing page
- Replace placeholder links with real Stripe URLs
- Show summary of configured links

See `docs/DEPLOYMENT.md` for deployment instructions.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      MAGIC BOX                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ORCHESTRATOR (Claude Opus)                             │
│  ├── Task decomposition                                 │
│  ├── Quality control                                    │
│  └── Strategic decisions                                │
│                                                         │
│  WORKERS                                                │
│  ├── Gemini CLI (Frontend, Research, Docs)              │
│  └── Codex CLI (Backend, Security, Auditing)            │
│                                                         │
│  PATTERNS                                               │
│  ├── Build-Audit-Fix (quality assurance)                │
│  ├── Parallel Execution (throughput)                    │
│  ├── Hard Problem Voting (consensus)                    │
│  └── Research-Implement (informed decisions)            │
│                                                         │
│  INFRASTRUCTURE                                         │
│  ├── mgrep (semantic search)                            │
│  ├── Qdrant (vector database)                           │
│  └── Traefik (reverse proxy)                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Notes

- `scripts/setup-complete.sh` is the full installer.
- `scripts/provision.sh` is a thin wrapper.
- Prompts are installed to `/opt/magic-box/prompts/` on customer VMs.
- If you update the installer in `applications/lab-kraliki/scripts/setup-complete.sh`, copy the changes here.
