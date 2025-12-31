# Recall by Kraliki User Guide

Complete guide to using Recall by Kraliki for persistent knowledge management.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Capture Workflows](#capture-workflows)
3. [Search Strategies](#search-strategies)
4. [Knowledge Graph](#knowledge-graph)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)

---

## Core Concepts

### What is Recall by Kraliki?

recall-kraliki is a **persistent knowledge graph** that solves the "AI amnesia" problem. When you work with AI assistants like Claude, they forget everything between sessions. recall-kraliki remembers for you.

**How it works:**

1. **Capture** - Save decisions, insights, learnings as markdown files
2. **Search** - Find items using hybrid search (keyword + AI semantic)
3. **Connect** - Link related items with wikilinks
4. **Recall** - Instantly retrieve context from any past session

### Storage Format

**Markdown + YAML frontmatter:**

```markdown
---
date: '2025-10-07'
id: dec-2025-10-07-001
category: decisions
tags:
- architecture
- backend
- stack-2026
related:
- insights/ins-2025-10-06-001
wikilinks:
- '[[insights/ins-2025-10-06-001|Stack compliance research]]'
---

# Decision: Use FastAPI for recall-kraliki backend

We chose FastAPI because it's part of Stack 2026 and provides excellent developer experience.

## Context
...
```

**Benefits:**
- Human-readable
- Git-friendly
- Obsidian/Logseq compatible
- No vendor lock-in
- Plain text =永久 (永久 = permanent)

---

## Capture Workflows

### Workflow 1: Quick Capture

**Use case:** Fast note during meeting/call

1. Click "Capture"
2. Paste/type content
3. Let AI auto-categorize
4. Click "Capture to recall-kraliki"

**Example:**
```markdown
Customer wants multi-user support. High priority. Budget approved.
```

AI will:
- Categorize as "customers"
- Suggest tags: customer-feedback, feature-request, multi-user
- Find related items about multi-user features

### Workflow 2: Structured Decision

**Use case:** Document important strategic decision

**Template:**
```markdown
# Decision: [Clear title]

## Context
- What situation led to this decision?
- What were we trying to solve?
- Who was involved?

## Decision
What did we decide? Be specific.

## Alternatives Considered
- Option A: Why rejected
- Option B: Why rejected
- Option C: Chosen - why

## Rationale
Why is this the right decision?

## Impact
- Team: How does this affect the team?
- Timeline: Does this change our timeline?
- Costs: Financial impact?

## Success Criteria
How will we know this was the right decision?

## Related
- [[category/id|Description]]
```

### Workflow 3: Research Capture

**Use case:** Capture market research, competitive analysis

```markdown
# Research: Avatar Market Analysis Q4 2025

## Key Findings
- Market size: $9.72B (2024) → $117.71B (2034)
- CAGR: 28.3%
- Top use cases: Gaming (42%), Social (31%), Enterprise (18%)

## Sources
- Gartner Report Oct 2025
- TechCrunch interview with Meta AR lead
- Our customer surveys (n=147)

## Implications
1. Enterprise avatar market is underserved (18% vs potential 40%)
2. Opportunity for B2B avatar platform
3. Integration with Ocelot Platform possible

## Related Decisions
- [[decisions/dec-2025-10-03-005|Build avatar feature]]
- [[ideas/ide-2025-09-28-012|Avatar-based collaboration]]

Tags: market-research, avatars, enterprise, 2025
```

### Workflow 4: Learning Capture

**Use case:** Document technical learning, bug fix, solution

```markdown
# Learning: Fix Tailwind dark mode not working

## Problem
Added dark mode to SvelteKit app but styles weren't applying.

## Root Cause
Tailwind config missing `darkMode: 'class'`

## Solution
```javascript
// tailwind.config.js
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',  // <-- This line!
  theme: { extend: {} }
}
```

## Additional Steps
1. Create theme store with localStorage persistence
2. Add dark: prefix to all color classes
3. Toggle `dark` class on document root

## Files Changed
- tailwind.config.js:4
- src/lib/stores/theme.ts (new)
- src/routes/+layout.svelte:3,8

## Time Saved Next Time
~2 hours debugging

Tags: svelte, tailwind, dark-mode, bug-fix, frontend
```

### Workflow 5: Session Summary

**Use case:** End of day summary

```markdown
# Session: 2025-10-07 recall-kraliki Development

## Completed
- ✅ Added dark mode to all pages
- ✅ Fixed search API field name bug (filepath → file_path)
- ✅ End-to-end testing (all passed)
- ✅ Created user documentation

## Decisions Made
1. [[decisions/dec-2025-10-07-001|Build SvelteKit UI instead of Logseq-only]]
2. [[decisions/dec-2025-10-07-002|Use hybrid search as default]]

## Insights
- [[insights/ins-2025-10-07-001|Dark mode requires comprehensive color variants]]
- [[insights/ins-2025-10-07-002|sed works better than Edit tool for bulk changes]]

## Tomorrow
- Test GLM 4.6 AI features (auto-categorize, semantic search)
- Configure MCP server in Claude Code
- Capture first real business decisions

## Time Tracking
- Development: 4h
- Testing: 1h
- Documentation: 1h
- Total: 6h

Tags: session-summary, development, recall-kraliki, 2025-10-07
```

---

## Search Strategies

### Strategy 1: Exact Match (Keyword)

**When to use:**
- Finding specific file, ID, or term
- You know exact wording
- Fast lookup needed

**Examples:**
```
"dec-2025-10-07-001"  → Find decision by ID
"FastAPI"             → Find all FastAPI mentions
"Stack 2026"          → Find Stack 2026 references
```

### Strategy 2: Conceptual Search (Semantic)

**When to use:**
- Finding related concepts
- You don't remember exact wording
- Exploring connections

**Examples:**
```
"backend framework decision"  → Finds FastAPI, Django, Flask discussions
"dark UI implementation"      → Finds dark mode work
"cost reduction strategies"   → Finds pricing, efficiency work
```

### Strategy 3: Hybrid Search (Best of Both)

**When to use:**
- Most queries
- Balance speed + intelligence
- Not sure which search type to use

**How it works:**
1. Keyword search runs first (fast)
2. Semantic search fills gaps (intelligent)
3. Results merged (keyword first, then semantic)

**Examples:**
```
"API design decisions"     → Keyword: "API", Semantic: REST/GraphQL discussions
"performance optimization" → Keyword: exact matches, Semantic: speed improvements
"customer feedback"        → Keyword: "customer", Semantic: user requests/complaints
```

### Strategy 4: Category + Search

**When to use:**
- Narrow down results
- Focus on specific type

**Examples:**
```
Category: decisions
Query: "backend"
→ Only backend-related decisions

Category: learnings
Query: "Svelte"
→ Only Svelte technical learnings
```

### Strategy 5: Tag-Based Discovery

**When to use:**
- Explore a topic
- Find all items about X

**How:**
1. Search for topic: "dark mode"
2. Click on item
3. Note tags: `svelte`, `tailwind`, `frontend`
4. Search by tag to find more

---

## Knowledge Graph

### Understanding the Graph

**Nodes** = Your captured items (decisions, insights, etc.)

**Edges** = Connections between items:
- Wikilinks: `[[category/id|label]]`
- Related items: AI-detected connections
- Shared tags: Items with same tags

**Stats:**
- Total nodes: How many items captured
- Total edges: How many connections
- Categories: How many categories used
- Avg connections: How interconnected your knowledge is
- Most connected: Your "hub" item

### Using the Graph

**Filter by Category:**
```
Select "decisions" → See only decision nodes
Select "all" → See everything
```

**Identify Knowledge Hubs:**
```
Look for large nodes (more connections)
These are your key insights/decisions
Everything connects through them
```

**Find Gaps:**
```
Isolated nodes = orphaned knowledge
Add wikilinks to connect them
```

**Discover Patterns:**
```
Clusters = related topics
Multiple paths = redundant knowledge
Missing connections = opportunities to link
```

### Building a Strong Graph

**1. Use Wikilinks Liberally:**
```markdown
Related to:
- [[decisions/dec-2025-10-05-001|Previous framework decision]]
- [[insights/ins-2025-10-06-002|Performance research]]
- [[learnings/lea-2025-10-04-003|Deployment lesson]]
```

**2. Create Index Items:**
```markdown
# Index: Backend Architecture Decisions

All decisions related to backend architecture:

- [[decisions/dec-2025-09-15-001|Use FastAPI]]
- [[decisions/dec-2025-09-20-002|PostgreSQL vs MongoDB]]
- [[decisions/dec-2025-10-01-003|Authentication strategy]]
- [[decisions/dec-2025-10-07-004|API versioning approach]]

Tags: index, backend, architecture
```

**3. Weekly Review:**
```
Every Friday, check graph for:
- Orphaned nodes → Add connections
- New patterns → Create index items
- Hub nodes → Ensure they're up-to-date
```

---

## Advanced Features

### Auto-Categorization (AI)

**How it works:**
GLM 4.6 analyzes your content and suggests:
- Category (decisions/insights/ideas/etc.)
- Tags (3-5 relevant tags)
- Related items (connections to existing knowledge)

**When to use:**
- Quick captures
- Unsure of category
- Want AI suggestions

**When to override:**
- Very specific categorization needed
- Creating new category pattern
- AI suggestion is wrong

### Auto-Linking (AI)

**How it works:**
GLM 4.6 scans existing items and finds:
- Semantically similar content
- Related topics
- Potential connections

Generates wikilinks automatically.

**Example:**
```markdown
Input:
"We decided to use FastAPI for the backend API."

Auto-generated wikilinks:
- [[insights/ins-2025-10-05-001|FastAPI performance analysis]]
- [[decisions/dec-2025-09-28-002|Backend framework selection criteria]]
```

### Pattern Detection (AI)

**Access:** Graph → "Detect Patterns" button (coming soon)

**What it does:**
- Identifies recurring themes
- Finds clusters of related content
- Suggests new connections
- Detects knowledge gaps

**Example output:**
```
Recurring Themes:
• Backend architecture (15 items)
• Dark mode implementation (8 items)
• Performance optimization (12 items)

Content Clusters:
• Cluster 1: Stack 2026 compliance (22 items)
• Cluster 2: AI integration (18 items)

Suggested Connections:
• Link "FastAPI decision" to "API performance research"
• Link "Dark mode learning" to "UI/UX decisions"

Knowledge Gaps:
• No deployment decisions captured
• Missing customer feedback from Q3
```

---

## Best Practices

### 1. Capture Early, Organize Later

Don't overthink categories/tags during capture. Just capture the knowledge.

**Good workflow:**
1. Quick capture (30 seconds)
2. Let AI categorize
3. Review/adjust later

### 2. Use Consistent Naming

**Decisions:**
```markdown
# Decision: [Action verb] [What]
# Decision: Use FastAPI for backend
# Decision: Implement dark mode
# Decision: Deploy to AWS
```

**Insights:**
```markdown
# Insight: [Discovery]
# Insight: Hybrid search performs 24% better
# Insight: Customers prefer async-first delivery
```

**Ideas:**
```markdown
# Idea: [Concept]
# Idea: Voice notes feature
# Idea: Mobile app version
```

### 3. Include Outcomes

Capture not just decisions, but results:

```markdown
# Decision: Use FastAPI for backend

## Decision Date
2025-10-01

## Implementation Date
2025-10-05

## Outcome (2025-10-15)
✅ Success
- Development 40% faster than Django
- API docs auto-generated
- Type safety caught 12 bugs before production

## Lessons Learned
- Async patterns require learning curve
- Worth the investment
- Team now prefers FastAPI for all projects
```

### 4. Cross-Reference Ruthlessly

Every item should link to 2-3 related items minimum.

**Bad:**
```markdown
# Decision: Use dark mode

We added dark mode.
```

**Good:**
```markdown
# Decision: Implement dark mode across all pages

Related:
- [[insights/ins-2025-10-05-001|User research: 67% prefer dark mode]]
- [[learnings/lea-2025-10-07-001|Tailwind dark mode implementation]]
- [[ideas/ide-2025-09-15-003|Automatic dark mode based on time]]

Based on [[research/res-2025-09-28-002|UI/UX trends 2025]]
```

### 5. Review Regularly

**Daily (2 minutes):**
- Check "Recent" for yesterday's captures
- Verify nothing missing

**Weekly (15 minutes):**
- Review all week's captures
- Add missing wikilinks
- Check graph for orphaned nodes
- Create index items for clusters

**Monthly (1 hour):**
- Run pattern detection
- Create summary index items
- Archive old/irrelevant items
- Identify knowledge gaps

### 6. Use Tags Hierarchically

```markdown
# Broad → Specific
Tags: business, sales, enterprise, outbound, cold-email, 2025-q4

# Domain → Topic → Detail
Tags: frontend, react, performance, lazy-loading, code-splitting

# Time-Based
Tags: 2025, 2025-q4, 2025-october, urgent, follow-up-weekly
```

### 7. Template Everything

Create templates for common captures:

**File:** `.templates/decision-template.md`
```markdown
# Decision: [Title]

## Context
[What led to this decision?]

## Decision
[What did we decide?]

## Alternatives Considered
1. [Option A] - [Why rejected]
2. [Option B] - [Why rejected]

## Rationale
[Why is this the right decision?]

## Impact
- Team: [Impact on team]
- Timeline: [Impact on timeline]
- Cost: [Financial impact]

## Success Criteria
[How will we measure success?]

## Related
- [[category/id|description]]

Tags: decision, [domain], [priority], [year]
```

---

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for solutions to common issues.

---

## FAQ

**Q: How is this different from Notion/Obsidian?**

A: recall-kraliki is optimized for AI-assisted work:
- Hybrid search (keyword + semantic AI)
- Auto-categorization and linking (AI)
- MCP integration (Claude Code can search/capture directly)
- Knowledge graph visualization
- Plain markdown (no lock-in)

**Q: Can I use Logseq/Obsidian to view the files?**

A: Yes! Files are stored as markdown with wikilinks. Just open the `memory/` folder in Logseq or Obsidian.

**Q: Does it work offline?**

A: Frontend and storage work offline. AI features (auto-categorize, semantic search) require GLM 4.6 API connection.

**Q: Can I export my data?**

A: Your data is already exported - it's plain markdown files in `memory/`. Just copy the folder.

**Q: How do I backup?**

A: `memory/` folder is your data. Backup options:
- Git (recommended): `git add memory/ && git commit -m "Backup"`
- Cloud: Sync `memory/` folder to Dropbox/Google Drive
- Archive: `tar -czf recall-backup-$(date +%Y%m%d).tar.gz memory/`

---

**Next:** Read `GETTING-STARTED.md` to start using recall-kraliki today!
