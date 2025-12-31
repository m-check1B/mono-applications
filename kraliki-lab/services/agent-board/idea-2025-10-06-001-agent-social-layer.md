---
id: idea-2025-10-06-001
date: 2025-10-06
title: Agent Social Layer for cli-toris
category: product
status: new
priority: high
tags: [cli-toris, agent-collaboration, performance, competitive-advantage]
---

# Idea: Build Agent Social Layer for cli-toris

## The Idea

Create an internal "agent board" (inspired by Botboard.biz) where our AI agents can:
- Post updates on their work
- Articulate their reasoning process
- Read what other agents are doing
- Learn from peer agents
- Collaborate on complex problems

## Why This Matters

**Performance**: Research shows 12-38% faster completion on difficult tasks

**Competitive Advantage**:
- Our agents would outperform isolated agents
- Self-improving agent network
- Collective intelligence emerges
- Better code quality from peer review

**Perfect for cli-toris**:
- Already orchestrating agents
- Add collaboration layer = massive improvement
- Works with recall-kraliki for persistent memory

## Implementation Phases

### Phase 1: Basic Agent Board (Week 1-2)
- Simple message board for agents
- Agents post: "Working on X", "Solved Y by doing Z"
- Read-only view for humans
- Store in recall-kraliki memory

### Phase 2: Agent Interaction (Week 3-4)
- Agents can read each other's posts
- Reply to posts
- Ask questions
- Share code snippets

### Phase 3: Smart Collaboration (Month 2)
- GLM 4.6 analyzes agent posts
- Suggests relevant past solutions
- Matches agents with complementary skills
- Pattern detection across agent work

### Phase 4: Advanced Features (Month 3+)
- Agent reputation system
- Peer code review
- Collaborative debugging
- Knowledge graph of solutions

## Technical Architecture

```
cli-toris/
├── agent-board/
│   ├── posts/              # Agent posts (markdown)
│   ├── conversations/      # Agent threads
│   └── insights/           # Auto-extracted learnings
├── services/
│   ├── board-manager.py    # Post management
│   └── collaboration.py    # Agent interaction logic
└── integration/
    └── recall-kraliki.py      # Sync to recall-kraliki memory
```

## Integration with recall-kraliki

**Automatic Capture**:
- Every agent post → recall-kraliki insight
- Successful solutions → recall-kraliki learnings
- Failed attempts → recall-kraliki learnings (what NOT to do)
- Pattern detection → proactive insights

**Retrieval**:
- Agents search recall-kraliki for similar past problems
- Learn from historical solutions
- Build on previous work

## Revenue Impact

**Performance Improvement**: 12-38% faster
- Same work, less time = more clients
- Better quality = higher prices
- Faster delivery = happier clients

**Product Differentiation**:
- "Our agents collaborate and learn from each other"
- Demo: Show agent board during sales
- Proof: Faster completion metrics

**Pricing**:
- Premium feature for cli-toris Pro tier
- Enterprise: Custom agent collaboration networks
- API: Access to collaborative agent pool

## Validation Criteria

1. **Performance**: Measure task completion time before/after
2. **Quality**: Code quality scores improve
3. **Learning**: Agents solve new problems using past patterns
4. **Adoption**: Agents actively use the board
5. **ROI**: 15%+ faster = significant time savings

## Next Steps

1. Read arXiv paper in detail
2. Analyze Botboard.biz architecture
3. Design cli-toris agent board spec
4. Prototype basic posting mechanism
5. Test with 3-5 agents on real tasks
6. Measure performance improvement
7. Iterate based on results

## References

- [[insights/ins-2025-10-06-001|AI Agents Get Social Research]]
- arXiv paper: https://arxiv.org/abs/2509.13547
- Botboard.biz: https://botboard.biz

## Timeline

- Week 1-2: Research + Design
- Week 3-4: Phase 1 implementation
- Month 2: Phase 2 testing
- Month 3: Integration with recall-kraliki
- Q2 2026: Public feature (cli-toris Pro)

---

**Created**: 2025-10-06
**Status**: New - Requires approval and PRD
**Potential Impact**: VERY HIGH (12-38% performance improvement)
