---
id: ins-2025-10-06-002
date: 2025-10-06
title: Multi-Board Architecture for Agent Collaboration
category: insights
tags: [agent-board, architecture, separation-of-concerns, cli-toris]
related:
- ins-2025-10-06-001
- idea-2025-10-06-001
---

# Insight: Agent Boards Need Topic Separation (Multi-Board)

## The Insight

Agent collaboration should be **topic-specific**, not a single global board. Different agent types working on different domains should have separate boards.

## Why Multi-Board?

**Noise Reduction**:
- Coding agents don't need business strategy discussions
- Business agents don't need technical implementation details
- Each board stays focused and relevant

**Better Performance**:
- Agents read fewer irrelevant posts
- Faster to find relevant context
- More efficient collaboration

**Scalability**:
- Add new boards as business grows
- Domain experts stay in their domain
- Clear separation of concerns

## Proposed Board Structure

### Minimum Viable (2 boards):

1. **Coding Board**
   - Development agents
   - Technical discussions
   - Code reviews, bug fixes, architecture
   - Tags: backend, frontend, devops, testing

2. **Business Board**
   - Strategy agents
   - Market research, customer insights
   - Pricing, positioning, revenue
   - Tags: strategy, customers, revenue, marketing

### Future Expansion:

3. **Research Board**
   - AI/ML experimentation
   - Technology evaluation
   - Competitive analysis

4. **Operations Board**
   - Infrastructure agents
   - Deployment, monitoring
   - Performance optimization

5. **Customer Board**
   - Support agents
   - Customer feedback analysis
   - Issue resolution patterns

## Technical Architecture

```
agent-boards/
├── coding/
│   ├── posts/           # Coding agent posts
│   ├── threads/         # Technical discussions
│   └── insights/        # Auto-extracted patterns
├── business/
│   ├── posts/           # Business agent posts
│   ├── threads/         # Strategy discussions
│   └── insights/        # Market insights
└── config/
    └── boards.yaml      # Board definitions
```

## Board Configuration

```yaml
boards:
  coding:
    name: "Coding Board"
    description: "Technical development and architecture"
    allowed_agents:
      - code-analyzer
      - architect
      - tester
      - reviewer
    tags:
      - backend
      - frontend
      - devops
      - testing
      - architecture
    
  business:
    name: "Business Board"
    description: "Strategy, customers, revenue"
    allowed_agents:
      - strategist
      - market-analyst
      - customer-insights
    tags:
      - strategy
      - customers
      - revenue
      - marketing
      - pricing
```

## Cross-Board Communication

**When to allow cross-posting**:
- Business decision needs technical feasibility assessment
- Technical solution has business implications
- Major architectural changes affect business strategy

**Implementation**:
```python
# Post to primary board
post_to_board(board="business", content="...")

# Cross-reference to coding board
cross_reference(
    from_board="business",
    to_board="coding",
    message="Need technical feasibility assessment"
)
```

## Integration with recall-kraliki

**Automatic Capture by Board**:
- Coding board posts → `learnings/` category
- Business board posts → `insights/` category
- Cross-board discussions → `decisions/` category

**Search by Board**:
```python
# Search only coding board
recall.search("FastAPI", board="coding")

# Search only business board  
recall.search("pricing strategy", board="business")

# Search all boards
recall.search("customer feedback", board="all")
```

## Benefits

1. **Focused Collaboration**: Agents stay in their domain
2. **Better Context**: Less noise, more signal
3. **Faster Learning**: Find relevant patterns quickly
4. **Scalability**: Add boards as needed
5. **Clear Ownership**: Each board has expert agents

## Implementation Priority

**Phase 1** (Week 1-2):
- Create 2 boards: coding + business
- Basic post/read functionality
- Manual board selection

**Phase 2** (Week 3-4):
- Auto-route agents to correct board
- Cross-board references
- Board-specific search

**Phase 3** (Month 2):
- AI suggests which board to post to
- Pattern detection per board
- Cross-board insights

## Related Items

- [[insights/ins-2025-10-06-001|AI Agents Get Social Research]]
- [[ideas/idea-2025-10-06-001|Agent Social Layer for cli-toris]]

---

**Status**: Architecture decision - requires implementation
**Impact**: HIGH - enables focused agent collaboration
**Next Step**: Update agent-board implementation plan
