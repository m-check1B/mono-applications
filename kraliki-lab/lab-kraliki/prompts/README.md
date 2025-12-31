# Lab by Kraliki Prompt Library

**Version:** 1.0  
**Last Updated:** 2025-12-25

## Overview

This prompt library enables consistent, high-quality multi-AI orchestration across the Lab by Kraliki platform. All prompts are tested and optimized for use with Claude Opus (Orchestrator), Gemini CLI (Worker), and Codex CLI (Worker).

## Quick Start

### For Orchestrators (Claude Opus)
1. Read `orchestrator/` directory for role definitions
2. Use `orchestrator/task-decomposition.md` to break down requests
3. Apply `orchestrator/quality-control.md` to review all deliverables
4. Use `orchestrator/strategic-planning.md` to choose optimal approaches
5. Maintain context with `orchestrator/context-management.md`

### For Gemini Workers
1. Read `worker-gemini/README.md` for role definition
2. Use `worker-gemini/frontend-development.md` for UI tasks
3. Follow research/content guidelines in worker README

### For Codex Workers
1. Read `worker-codex/README.md` for role definition
2. Apply security checklists before submitting backend code
3. Use code review templates for auditing work

### For Workflow Patterns
1. Read `patterns/README.md` for available patterns
2. Select pattern based on task type (Build-Audit-Fix, Parallel Execution, etc.)
3. Follow step-by-step instructions for chosen pattern

## Directory Structure

```
prompts/
├── orchestrator/
│   ├── README.md                 # Orchestrator role and responsibilities
│   ├── task-decomposition.md      # How to break down complex tasks
│   ├── quality-control.md         # Quality standards and review process
│   ├── strategic-planning.md     # Decision-making frameworks
│   └── context-management.md      # Memory and continuity best practices
├── worker-gemini/
│   ├── README.md                 # Gemini worker role and when to use
│   ├── frontend-development.md    # Frontend/UI development guidelines
│   └── [More specialized prompts...]
├── worker-codex/
│   └── README.md                 # Codex worker role and when to use
│   └── [More specialized prompts...]
└── patterns/
    ├── README.md                 # Pattern catalog and usage guide
    ├── build-audit-fix.md         # Build → Audit → Fix workflow
    └── parallel-execution.md     # Parallel workstream execution
```

## Core Concepts

### The 16× Multiplier

Lab by Kraliki delivers 16× productivity by:
- **4×** speed (parallel execution)
- **4×** output (multi-AI specialization)
= **16×** overall productivity gain

### Multi-AI Orchestration

| Role | AI Model | Primary Strength | Best For |
|-------|-----------|------------------|-----------|
| Orchestrator | Claude Opus | Strategic thinking, context management | Task decomposition, synthesis |
| Worker 1 | Gemini CLI | Research, frontend, content | Fast iteration, UI, synthesis |
| Worker 2 | Codex CLI | Backend, security, audits | Thorough reviews, complex logic |

### Key Workflows

1. **Parallel Execution**: Multiple independent workstreams running simultaneously
2. **Build → Audit → Fix**: Quality-first development with verification
3. **MVP → Iteration**: Fast prototyping with iterative refinement
4. **Research → Synthesis**: Gather information, combine into insights
5. **Template Adaptation**: Leverage existing templates for new work

## When to Use Each Worker

### Gemini Worker Best For
- Frontend development (HTML, CSS, React, Vue, Svelte)
- Research tasks (market research, competitive analysis, fact-finding)
- Content creation (copywriting, documentation, emails)
- Rapid prototyping and exploration
- Tasks requiring natural language strength

### Codex Worker Best For
- Backend development (Python, Node.js, Go, database work)
- Security auditing and vulnerability scanning
- Code reviews and quality checks
- Complex business logic implementation
- Performance optimization

### Orchestrator Best For
- Task decomposition and assignment
- Quality control and review
- Strategic decision-making
- Context management across sessions
- Result synthesis from multiple workers

## Quality Standards

### Code Quality
- Type hints and annotations
- Proper error handling
- Input validation
- No hardcoded secrets
- Clear, readable code

### Security
- No SQL injection vulnerabilities
- No XSS vulnerabilities  
- Proper authentication/authorization
- Rate limiting where applicable
- OWASP Top 10 compliance

### Accessibility
- WCAG 2.1 AA compliant
- Semantic HTML
- Keyboard navigation
- Color contrast standards
- ARIA labels where needed

### Performance
- Fast load times (< 3 seconds)
- Optimized images (WebP, compressed)
- Efficient database queries
- Minimal JavaScript bundles
- Caching used appropriately

## Usage Examples

### Example 1: Building a Landing Page
```bash
# Orchestrator decomposes task
claude "Build a SaaS landing page with pricing"

# Orchestrator assigns streams in parallel
STREAM 1 (gemini): "Research competitor landing pages and best practices"
STREAM 2 (gemini): "Write hero section copy"
STREAM 3 (gemini): "Write features section copy"
STREAM 4 (gemini): "Build hero and features sections with Tailwind CSS"

# After streams complete, codex audits
codex "Audit landing page for security, accessibility, performance"

# Orchestrator synthesizes results
claude "Combine all sections into complete landing page"
```

### Example 2: Competitive Analysis
```bash
# Orchestrator launches parallel research streams
STREAM 1 (gemini): "Research top 5 market leaders"
STREAM 2 (gemini): "Research top 5 emerging competitors"
STREAM 3 (gemini): "Analyze feature sets across competitors"
STREAM 4 (gemini): "Compare pricing and positioning"

# Codex validates facts and synthesizes
codex "Fact-check all research and provide strategic recommendations"
```

### Example 3: Bug Fix with Quality Check
```bash
# Codex identifies and fixes issue
codex "Fix the authentication bug in /backend/api/auth.py"

# Codex runs security audit
codex "Audit auth.py for SQL injection, XSS, rate limiting"

# Orchestrator reviews and approves
claude "Review the fix and audit, approve for deployment"
```

## Getting Started with Lab by Kraliki

### New Users
1. Start with simple tasks to learn the system
2. Use existing patterns rather than creating from scratch
3. Ask for clarification if requirements are vague
4. Review the patterns directory before starting complex tasks

### Experienced Users
1. Store learnings in mgrep semantic memory
2. Adapt and refine patterns based on what works
3. Contribute new patterns back to this library
4. Track metrics to identify improvement areas

## Metrics to Track

### Effectiveness Metrics
- **Task Success Rate**: % of tasks completed without rework
- **Quality Score**: % passing quality checks
- **Time Estimates**: Accuracy of time predictions
- **User Satisfaction**: Post-delivery feedback scores

### Workflow Metrics
- **Parallel Speedup**: (Sequential time) / (Parallel time)
- **Audit Findings**: Average issues found per deliverable
- **Context Hits**: How often retrieved context helps
- **Pattern Usage**: Which patterns are used most

## Continuous Improvement

### Pattern Refinement
1. Document what works well
2. Identify patterns that need improvement
3. Update prompt library with learnings
4. Retire ineffective patterns

### Worker Training
1. Track which workers excel at which tasks
2. Refine worker-specific prompts based on success rates
3. Identify worker weaknesses to avoid
4. Adjust task assignment strategy

## Contributing to the Library

When you discover a successful workflow:

1. **Document the steps** taken
2. **Identify the use case** when it's applicable
3. **Note any variations** needed for different contexts
4. **Create a new prompt/pattern** in the appropriate directory
5. **Index in mgrep** for future retrieval
6. **Update this README** with the new addition

## Troubleshooting

### Common Issues

| Issue | Solution |
|--------|----------|
| Workers produce conflicting outputs | Orchestrator mediates, research to resolve |
| Task takes longer than estimated | Break into smaller subtasks or reduce scope |
| Quality checks keep failing | Simplify requirements or reduce scope |
| Context is lost between sessions | Query mgrep for past work, reconstruct state |
| Pattern doesn't apply to current task | Adapt the pattern or create a new variation |

## Support and Documentation

### For Help Using Prompts
- **Pattern Selection**: Not sure which pattern to use? Read `patterns/README.md`
- **Worker Assignment**: Confused about which worker for what task? Check worker READMEs
- **Quality Standards**: Need clarification on standards? See `orchestrator/quality-control.md`
- **Context Management**: Lost track of what was done? Review `orchestrator/context-management.md`

### Lab by Kraliki Documentation
- **Main README**: `/applications/lab-kraliki/README.md`
- **Product Roadmap**: See `applications/lab-kraliki/docs/`
- **Demo Scenarios**: `/applications/lab-kraliki/demo/scenarios/`

## Version History

### v1.0 (2025-12-25)
- Initial prompt library
- Orchestrator prompts (decomposition, quality control, strategy, context)
- Worker prompts (Gemini frontend, Codex backend/security)
- Workflow patterns (Build-Audit-Fix, Parallel Execution)
- Comprehensive examples and use cases

## License

This prompt library is part of Lab by Kraliki. Use it freely within your Lab by Kraliki deployment.

---

**Lab by Kraliki Prompt Library - Making Multi-AI Orchestration Simple and Powerful**
