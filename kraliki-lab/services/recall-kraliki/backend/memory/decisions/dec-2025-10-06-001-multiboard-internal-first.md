---
id: dec-2025-10-06-001
date: 2025-10-06
title: Multi-Board Agent Collaboration - Internal First, Public Later
category: decisions
tags: [agent-board, product-strategy, internal-tools, saas]
related:
- ins-2025-10-06-001
- ins-2025-10-06-002
- idea-2025-10-06-001
---

# Decision: Build Multi-Board Agent System - Internal First, Public Later

## Context

Research shows AI agents perform 12-38% faster with social collaboration (Botboard.biz). We need an agent collaboration platform but recognized agents need topic-specific boards (coding, business, etc.) not a single global board.

## Decision

**Build multi-board agent collaboration system in 2 phases:**

### Phase 1: Internal Use (Q4 2025 - Q1 2026)
- Deploy for Ocelot's internal agents
- 2 initial boards: Coding + Business
- Integration with recall-kraliki
- Dogfood and validate performance gains
- Measure actual impact (12-38% faster?)

### Phase 2: Public SaaS Product (Q2 2026+)
- Package as standalone product
- Multi-tenant architecture
- Custom boards per customer
- Pricing model: per agent/per board
- Brand: Part of Ocelot Platform suite

## Rationale

**Why Internal First:**
1. **Validation**: Prove 12-38% performance gain with our agents
2. **Iteration**: Fix issues before customers see them
3. **Product-Market Fit**: Learn what boards/features matter most
4. **Case Study**: "We use this ourselves and got X% faster"
5. **Competitive Advantage**: Our agents outperform competitors NOW

**Why Multi-Board:**
1. **Focus**: Coding agents don't need business discussions
2. **Performance**: Less noise = faster relevant context
3. **Scalability**: Add boards as needed (research, operations, support)
4. **Flexibility**: Different customers need different board combinations

## Implementation Plan

### Internal Phase (3 months)

**Month 1 - Core System**:
- [ ] Multi-board architecture
- [ ] 2 boards: coding + business
- [ ] Basic post/read/reply
- [ ] recall-kraliki integration
- [ ] Deploy for cli-toris agents

**Month 2 - AI Features**:
- [ ] Auto-route agents to correct board
- [ ] Cross-board references
- [ ] Pattern detection per board
- [ ] GLM 4.6 semantic search in posts

**Month 3 - Measurement**:
- [ ] Performance benchmarks
- [ ] A/B testing (with/without board)
- [ ] Document case studies
- [ ] Identify missing features

### Public Phase (6+ months)

**Q2 2026 - MVP**:
- [ ] Multi-tenant architecture
- [ ] Custom boards per customer
- [ ] Admin dashboard
- [ ] API for agent integration
- [ ] Pricing tiers

**Q3 2026 - Growth**:
- [ ] Marketing site
- [ ] Documentation
- [ ] Customer onboarding
- [ ] Support system

## Success Criteria

**Internal Phase**:
- ✅ 10%+ performance improvement (conservative vs 12-38%)
- ✅ Agents actively use boards (5+ posts/day)
- ✅ Measurable code quality improvement
- ✅ Zero downtime for 30 days

**Public Phase**:
- ✅ 10 paying customers in first quarter
- ✅ $5K+ MRR within 6 months
- ✅ 90%+ customer satisfaction
- ✅ Case studies from 3+ customers

## Revenue Potential

**Internal Value**:
- 15% faster development = 6 hours/week saved
- Better code quality = fewer bugs
- Knowledge persistence = less rework
- Competitive advantage in AI consulting

**Public Product**:
- **Pricing**: $50/agent/month
- **Target**: 100 agents across 10 customers = $5K MRR
- **Year 1**: 500 agents = $25K MRR
- **Year 2**: 2000 agents = $100K MRR

**Market**:
- Companies using AI agents for development
- AI consulting firms (like us)
- Enterprise dev teams experimenting with agents
- Research labs

## Risks & Mitigations

**Risk 1**: Performance gains don't materialize
- **Mitigation**: Measure continuously, iterate features
- **Fallback**: Use internally anyway for knowledge capture

**Risk 2**: Too complex for customers
- **Mitigation**: Start with simple 1-2 board setup
- **Fallback**: Managed service offering

**Risk 3**: Competitors copy quickly
- **Mitigation**: Move fast, build network effects
- **Advantage**: Our integration with recall-kraliki is unique

## Alternative Considered

**Option A**: Build public product first
- ❌ Risk: Build wrong features
- ❌ No proof of value
- ❌ Waste time on wrong market

**Option B**: Only build for internal use
- ❌ Leave revenue on table
- ❌ Product validated but not monetized

**Option C**: Use existing tools (Slack, Discord)
- ❌ Not designed for AI agents
- ❌ No recall-kraliki integration
- ❌ No multi-board specialization

## Next Steps

1. **This Week**:
   - [ ] Update agent-board PRD with multi-board architecture
   - [ ] Design database schema for boards
   - [ ] Sketch UI for board navigation

2. **Week 2**:
   - [ ] Implement core multi-board backend
   - [ ] Create coding board
   - [ ] Create business board
   - [ ] Deploy for first agent test

3. **Month 1**:
   - [ ] All cli-toris agents using boards
   - [ ] Measure baseline performance
   - [ ] Iterate based on usage patterns

## Related Items

- [[insights/ins-2025-10-06-001|AI Agents Get Social - 12-38% Faster]]
- [[insights/ins-2025-10-06-002|Multi-Board Architecture]]
- [[ideas/idea-2025-10-06-001|Agent Social Layer for cli-toris]]

---

**Decision Date**: 2025-10-06
**Status**: Approved - Ready for implementation
**Owner**: Matej (with Claude Code)
**Timeline**: Q4 2025 (internal) → Q2 2026 (public)
**Impact**: HIGH - Competitive advantage + new revenue stream
