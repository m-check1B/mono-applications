# Magic Box Prompt Library

**Industry-tested prompts for multi-AI orchestration.**

This library provides ready-to-use prompts for the Magic Box multi-AI orchestration platform. Each prompt has been tested and refined for optimal results.

## Quick Start

```bash
# Copy a prompt template
cp prompts/orchestrator/task-decomposition.md my-project/

# Use with Claude Code
claude --prompt "$(cat prompts/orchestrator/task-decomposition.md)" "Build a user authentication system"
```

## Directory Structure

```
prompts/
├── README.md                    # This file
│
├── orchestrator/                # Claude Opus orchestration prompts
│   ├── task-decomposition.md    # Break complex tasks into subtasks
│   ├── quality-control.md       # Review and validate work
│   ├── context-management.md    # Maintain project context
│   ├── strategic-planning.md    # High-level project planning
│   └── multi-step-reasoning.md  # Complex logical reasoning
│
├── workers/                     # Worker-specific prompts
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
├── content/                     # Content generation prompts
│   ├── blog-writer.md           # SEO-optimized blog posts
│   ├── social-media.md          # Platform-specific social content
│   └── marketing-copy.md        # Conversion-focused copy
│
├── data/                        # Data analysis prompts
│   ├── data-analyzer.md         # Data insights and visualization
│   └── summarizer.md            # Document summarization
│
└── patterns/                    # Multi-AI workflow patterns
    ├── build-audit-fix.md       # Builder -> Auditor -> Fixer cycle
    ├── parallel-execution.md    # Independent parallel tasks
    ├── hard-problem-voting.md   # Multi-model consensus
    └── research-implement.md    # Research first, then build
```

## Prompt Categories

### 1. Orchestrator Prompts (Claude Opus)

Use Claude Opus for high-level orchestration:
- **Task decomposition**: Breaking complex problems into manageable pieces
- **Quality control**: Reviewing and validating work from workers
- **Context management**: Maintaining project state across sessions
- **Strategic planning**: Choosing approaches and architectures
- **Multi-step reasoning**: Complex logical analysis with verification

### 2. Worker Prompts

#### Gemini CLI (Fast, Creative)
Best for:
- Frontend code generation (React, Svelte, Vue)
- Research and information gathering
- Documentation and technical writing
- Quick prototyping

#### Codex CLI (Precise, Technical)
Best for:
- Backend code generation (Python, Node.js, Go)
- Code auditing and review
- Security analysis
- Test generation

#### Claude (Nuanced, Thoughtful)
Best for:
- Translation and localization
- Code debugging and root cause analysis
- Complex reasoning tasks
- Nuanced content requiring judgment

### 3. Content Prompts

Professional content generation:

| Prompt | Use Case | Output |
|--------|----------|--------|
| Blog Writer | SEO articles, thought leadership | Full blog posts with meta |
| Social Media | LinkedIn, Twitter, Instagram | Platform-optimized posts |
| Marketing Copy | Landing pages, emails, ads | Conversion-focused copy |

### 4. Data Prompts

Data analysis and summarization:

| Prompt | Use Case | Output |
|--------|----------|--------|
| Data Analyzer | Business insights, trends | Structured analysis reports |
| Summarizer | Long documents, meetings | Multi-level summaries |

### 5. Pattern Prompts

Orchestration patterns for common workflows:

| Pattern | Use Case | Flow |
|---------|----------|------|
| Build-Audit-Fix | Quality code | Build -> Audit -> Fix issues |
| Parallel Execution | Independent tasks | Multiple workers simultaneously |
| Hard Problem Voting | Critical decisions | Multiple models vote |
| Research-Implement | Unknown domains | Research -> Plan -> Build |

## Usage Examples

### Example 1: Build-Audit-Fix Pattern

```bash
# 1. Builder creates initial implementation
claude --prompt "$(cat prompts/workers/codex/backend-builder.md)" \
  "Create a REST API for user management with CRUD operations"

# 2. Auditor reviews the code
claude --prompt "$(cat prompts/workers/codex/code-auditor.md)" \
  "Review src/api/users.py for security and quality issues"

# 3. Builder fixes identified issues
claude --prompt "$(cat prompts/workers/codex/backend-builder.md)" \
  "Fix the issues identified: [paste auditor findings]"
```

### Example 2: Content Generation

```bash
# Generate a blog post
claude --prompt "$(cat prompts/content/blog-writer.md)" \
  "Write a blog post about remote team productivity for small business owners"

# Create social media content
claude --prompt "$(cat prompts/content/social-media.md)" \
  "Create a LinkedIn post announcing our new product launch"

# Write marketing copy
claude --prompt "$(cat prompts/content/marketing-copy.md)" \
  "Write landing page copy for an AI writing assistant"
```

### Example 3: Data Analysis

```bash
# Analyze sales data
claude --prompt "$(cat prompts/data/data-analyzer.md)" \
  "Analyze Q4 sales data to identify trends and opportunities"

# Summarize a long document
claude --prompt "$(cat prompts/data/summarizer.md)" \
  "Summarize this 50-page research report for executive presentation"
```

### Example 4: Translation

```bash
# Translate marketing content
claude --prompt "$(cat prompts/workers/claude/translator.md)" \
  "Translate our landing page from English to German with cultural adaptation"
```

### Example 5: Debugging

```bash
# Debug a complex issue
claude --prompt "$(cat prompts/workers/claude/debugger.md)" \
  "Help me debug this API crash when user ID doesn't exist"
```

### Example 6: Multi-Step Reasoning

```bash
# Analyze a complex decision
claude --prompt "$(cat prompts/orchestrator/multi-step-reasoning.md)" \
  "Should we invest in TV ads, digital ads, or a mix? Budget: $500K"
```

### Example 7: Parallel Execution

```bash
# Run frontend and backend builders simultaneously
claude --prompt "$(cat prompts/workers/gemini/frontend-builder.md)" \
  "Build the user dashboard component" &

codex --prompt "$(cat prompts/workers/codex/backend-builder.md)" \
  "Build the dashboard API endpoint" &

wait  # Wait for both to complete
```

## Model Recommendations

Each prompt includes model recommendations. General guidelines:

| Task Type | Best Model | Why |
|-----------|------------|-----|
| Complex reasoning | Claude Opus | Nuanced analysis |
| Code generation | Codex, Claude | Precision |
| Fast drafts | Gemini Flash | Speed + creativity |
| High volume | Claude Haiku, GPT-3.5 | Cost efficiency |
| Multi-language | GPT-4 | Broad support |
| Long context | Gemini Pro | 100K+ tokens |

## Customization

### Adding Your Own Prompts

1. Copy an existing template:
   ```bash
   cp prompts/workers/codex/backend-builder.md prompts/workers/codex/my-custom-prompt.md
   ```

2. Edit to fit your needs:
   - Modify the role description
   - Add domain-specific context
   - Include relevant examples
   - Adjust output format

3. Test with a sample task

### Best Practices

1. **Be specific**: Include concrete examples in prompts
2. **Set constraints**: Define what NOT to do
3. **Request format**: Specify expected output structure
4. **Chain context**: Pass relevant context between prompts
5. **Iterate**: Refine prompts based on results

## Integration with Magic Box

When running on Magic Box, prompts are available at:
```
/opt/magic-box/prompts/
```

The `magic-box` CLI can use prompts directly:
```bash
magic-box run --prompt orchestrator/task-decomposition.md "Your task here"
```

## Prompt Statistics

| Category | Count | Description |
|----------|-------|-------------|
| Orchestrator | 5 | High-level coordination |
| Workers | 8 | Task execution |
| Content | 3 | Content generation |
| Data | 2 | Analysis & summarization |
| Patterns | 4 | Workflow templates |
| **Total** | **22** | Production-ready prompts |

## License

Part of Magic Box by Kraliki. Commercial use permitted for Magic Box customers.
