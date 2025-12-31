# Lab by Kraliki Pro - Demo Environment

Ready-to-use demo environment for B2B client demonstrations.

## Quick Start

```bash
# 1. Start the demo environment
./scripts/demo-start.sh

# 2. Run a live demo scenario
./scripts/run-scenario.sh agency-website

# 3. Reset for next demo
./scripts/demo-reset.sh
```

## Directory Structure

```
demo/
├── README.md               # This file
├── sample-projects/        # Pre-configured demo projects
│   ├── agency-client/      # Sample agency project
│   ├── consulting-deck/    # Sample consulting project
│   └── content-campaign/   # Sample content project
├── scripts/                # Demo automation scripts
│   ├── demo-start.sh       # Initialize demo environment
│   ├── demo-reset.sh       # Reset between demos
│   └── run-scenario.sh     # Execute specific demo scenarios
├── scenarios/              # Scripted demo flows
│   ├── agency-website.md   # Agency website build demo
│   ├── content-audit.md    # Content audit demo
│   └── parallel-tasks.md   # Parallel execution demo
└── outputs/                # Sample outputs for showcase
    ├── before-after/       # Before/after comparisons
    └── case-studies/       # Demo case study outputs
```

## Demo Scenarios

| Scenario | Duration | Best For | Key Feature |
|----------|----------|----------|-------------|
| Agency Website | 15 min | Digital agencies | Build-Audit-Fix pattern |
| Content Audit | 10 min | SEO/Content teams | Multi-model analysis |
| Parallel Tasks | 12 min | Any | Concurrent execution |
| Hard Problem | 8 min | Technical buyers | Multi-AI voting |

## Pre-Demo Checklist

- [ ] All CLI tools responding (`magic-box status`)
- [ ] mgrep indexed and returning results
- [ ] Sample projects loaded
- [ ] API keys configured (or demo keys available)
- [ ] Screen sharing ready
- [ ] Backup video available (if live demo fails)

## Demo Credentials

For internal demos only:
- Demo account: `demo@magic-box.pro`
- SSH access: via designated demo VM

## Sample Data Included

### Agency Client Project
- Brand assets (Acme Corp)
- Project brief
- Wireframe sketches
- Content outline

### Consulting Deck Project
- Market research brief
- Competitor data
- Stakeholder list
- Deliverable template

### Content Campaign Project
- Campaign brief
- Topic list
- Brand voice guide
- Distribution channels

## Tips for Effective Demos

1. **Start with the problem** - Show the pain of copy-pasting between AI tabs
2. **Let them see the orchestration** - Show Claude delegating to workers
3. **Highlight the memory** - Query mgrep to show context retention
4. **End with ROI** - Compare time/output to traditional approach

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CLI not responding | `magic-box restart` |
| mgrep empty results | `magic-box index` |
| API rate limit | Switch to backup API key |
| Slow response | Use smaller demo task |

---

*Last updated: December 2025*
