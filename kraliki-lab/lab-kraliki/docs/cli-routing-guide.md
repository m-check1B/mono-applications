# Multi-AI CLI Routing Guide

> **For Lab by Kraliki Pro Customers**
> Route tasks to the right AI model for maximum productivity

## Quick Reference

| Task Type | Use This CLI | Why |
|-----------|--------------|-----|
| **Planning & Strategy** | `claude` | Best at orchestration |
| **Frontend/UI Work** | `gemini` | Multimodal, UI intuition |
| **Backend/Architecture** | `codex` | System design expert |
| **Documentation** | `claude` | Clearest writing |
| **Code Review** | `codex` → `claude` | Codex finds issues, Claude integrates |

## The 3 AI CLIs in Your Lab by Kraliki

### Claude Code (Primary Orchestrator)

**Best for:** Planning, coordination, documentation, general coding

```bash
# Interactive mode
claude

# One-shot task
claude -p "Create a plan to migrate our database"

# With specific model
claude -p "Review this architecture" --model opus  # Strongest reasoning
claude -p "Implement this feature" --model sonnet  # Faster, cheaper
```

### Gemini CLI (Frontend Specialist)

**Best for:** UI work, visual debugging, multimodal tasks

```bash
# Interactive mode
gemini

# One-shot task
gemini "Create a responsive navbar component"

# Analyze a screenshot (multimodal!)
gemini -f screenshot.png "What's wrong with this UI?"

# Frontend debugging
gemini -f error_screenshot.png "Fix this CSS issue"
```

### Codex CLI (Architecture Expert)

**Best for:** System design, database, algorithms, performance

```bash
# Architecture task
codex exec "Design the database schema for user authentication"

# With context file
codex exec "Review this API design" --context ./API_DESIGN.md

# Performance optimization
codex exec "Optimize this database query" --context ./slow_query.sql
```

## Routing Patterns for Your Workflow

### Pattern 1: Simple Routing (Daily Work)

Route tasks based on category:

```
Frontend work   → gemini
Backend/API     → claude
Database design → codex
General tasks   → claude
```

### Pattern 2: Build-Review-Integrate (Quality Work)

For important features:

```
1. Claude plans the feature
2. Gemini implements UI / Codex implements backend
3. The OTHER model reviews (cross-review)
4. Claude integrates and finalizes
```

**Example:**
```bash
# 1. Plan (Claude)
claude -p "Plan the user settings page"

# 2. Build UI (Gemini)
gemini "Implement the settings page based on this plan: [paste plan]"

# 3. Review (Codex)
codex exec "Review this settings page implementation for security issues"

# 4. Integrate (Claude)
claude -p "Integrate this feedback and finalize the settings page"
```

### Pattern 3: Council Decision (Big Decisions)

Get multiple perspectives on major choices:

```bash
# Ask all 3 models
claude -p "Should we use PostgreSQL or MongoDB for this project?"
gemini "Should we use PostgreSQL or MongoDB for this project?"
codex exec "Should we use PostgreSQL or MongoDB for this project?"

# Then synthesize with Claude
claude -p "Synthesize these 3 perspectives and recommend: [paste responses]"
```

## Your CLAUDE.md Integration

Add model hints to your tasks:

```markdown
## Current Sprint

- [ ] Build landing page → **gemini**
- [ ] Design API schema → **codex**
- [ ] Write user documentation → **claude**
- [ ] Review all code → **codex + claude**
```

## Cost-Effective Routing

| Model | Cost | Use For |
|-------|------|---------|
| Gemini Flash | $ | Quick tasks, frontend |
| Claude Sonnet | $$ | Daily implementation |
| Codex | $$ | Architecture decisions |
| Claude Opus | $$$ | Complex planning, final review |

**Tip:** Start with cheaper models (Gemini Flash, Sonnet) and escalate to expensive ones (Opus) only for complex decisions.

## Common Workflows

### New Feature Development

```
1. claude -p "Plan feature X"           # Planning
2. gemini "Build the UI for X"          # Frontend
3. codex exec "Build the API for X"     # Backend
4. codex exec "Review the full stack"   # Architecture review
5. claude -p "Finalize and document"    # Integration
```

### Bug Investigation

```
1. gemini -f screenshot.png "What's this error?"  # Visual debugging
2. codex exec "Analyze this stack trace"           # Deep analysis
3. claude -p "Suggest fix based on analysis"       # Solution
```

### Performance Optimization

```
1. codex exec "Profile this code for bottlenecks"
2. codex exec "Suggest optimizations"
3. claude -p "Implement the safest optimization"
```

## Tips for Success

1. **Match task to model** - Don't force Claude to do UI work or Gemini to design databases
2. **Use cross-review** - Have one model review another's work
3. **Start cheap** - Use Flash/Sonnet first, escalate to Opus when needed
4. **Context matters** - Always provide relevant files with `--context` or `-f`
5. **Synthesize with Claude** - When getting multiple opinions, let Claude integrate them

## Troubleshooting

### "The model didn't understand my task"

- Add more context (files, examples)
- Try a different model better suited to the task
- Break the task into smaller pieces

### "The output quality is inconsistent"

- Use the review pattern (build → review → integrate)
- Specify output format in your prompt
- Use a more capable model for complex tasks

### "It's too expensive"

- Route more tasks to Gemini Flash
- Use Sonnet instead of Opus for implementation
- Reserve Opus for planning and final review only

---

*Part of Lab by Kraliki Pro • Multi-AI Orchestration Platform*
