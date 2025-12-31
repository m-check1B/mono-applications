---
name: prompts
description: OpenAI prompt templates library. Reusable prompts for communication, meetings, decisions, and productivity tasks.
source: OpenAI Academy
version: 1.0.0
location: /github/applications/kraliki-lab/kraliki-swarm/prompts/
---

# Prompt Templates Library

A collection of high-quality prompt templates from OpenAI Academy, organized by category for easy reuse across **all Kraliki agents** (Claude, OpenCode, Gemini, Codex).

## Multi-CLI Access

This library is in `/github/applications/kraliki-lab/kraliki-swarm/prompts/` - accessible by ALL CLIs:

```bash
# Any agent can read prompts directly
cat /github/applications/kraliki-lab/kraliki-swarm/prompts/communication/email-professional.md
```

## Categories

| Category | Count | Purpose |
|----------|-------|---------|
| [communication](./communication/) | 5 | Professional emails, clarity, audience adaptation |
| [meetings](./meetings/) | 5 | Agendas, notes, action items, follow-ups |
| [decisions](./decisions/) | 5 | Root cause analysis, options comparison, risk |
| [productivity](./productivity/) | 5 | Planning, prioritization, updates |

## Usage

Reference prompts in genome files or invoke directly:

```
/prompts/communication/email-professional
/prompts/meetings/agenda-create
/prompts/decisions/root-cause
/prompts/productivity/weekly-plan
```

## Available Prompts

### Communication
- `email-professional` - Write professional emails with subject line
- `rewrite-clarity` - Rewrite text for clarity and conciseness
- `audience-adapt` - Adapt message for different audiences
- `meeting-invite` - Draft calendar meeting invitations
- `email-summarize` - Summarize long email threads

### Meetings
- `agenda-create` - Create structured meeting agendas
- `notes-summarize` - Summarize meeting notes into recap
- `action-items` - Extract action items from notes
- `prep-questions` - Generate meeting prep questions
- `follow-up-email` - Write post-meeting follow-up emails

### Decisions
- `root-cause` - Identify root causes of issues
- `compare-options` - Compare solution alternatives
- `decision-criteria` - Define decision criteria with weights
- `risk-assessment` - Assess risks and mitigations
- `recommend-option` - Recommend best option with reasoning

### Productivity
- `priorities-daily` - Create prioritized daily to-do lists
- `weekly-plan` - Build balanced weekly work plans
- `document-summarize` - Summarize documents into key points
- `brainstorm-solutions` - Generate creative solutions
- `project-update` - Write stakeholder project updates

## Integration with Genomes

Add to genome configuration:

```yaml
prompts:
  - communication/email-professional
  - meetings/action-items
  - decisions/root-cause
```

Agents can then use these templates for structured outputs in blackboard posts and Linear issue comments.

## Source

[OpenAI Academy Prompt Packs](https://academy.openai.com/public/tags/prompt-packs-6849a0f98c613939acef841c)

300+ prompts organized by role. This library extracts the most universally applicable templates.
