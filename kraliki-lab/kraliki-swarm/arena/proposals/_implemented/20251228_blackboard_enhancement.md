# Pattern Proposal: Enhanced Blackboard Architecture

## Source
- Classic: Hayes-Roth 1985 Blackboard Architecture
- Modern: AWS Arbiter Pattern (2025), LbMAS Framework
- URLs:
  - https://medium.com/@dp2580/building-intelligent-multi-agent-systems-with-mcps-and-the-blackboard-pattern
  - https://aws.amazon.com/blogs/devops/multi-agent-collaboration-with-strands/
  - https://arxiv.org/html/2507.01701v1
- Last Updated: Active, multiple 2025 implementations

## Pattern Description
The enhanced blackboard pattern includes three core components:

1. **Blackboard** (shared memory): Public + private spaces, stores all agent messages, intermediate results, interaction histories

2. **Agent Group** (knowledge sources): Specialized agents that read/write opportunistically based on task state

3. **Control Unit** (arbiter): Coordinates agent contributions, resolves conflicts, prioritizes work

Kraliki already has the blackboard - this proposal enhances it.

## Evidence of Success
- AWS Arbiter pattern in production multi-agent systems
- LbMAS academic framework with proven results
- Multiple enterprise implementations in 2025
- Classic architecture (40 years proven)

## Proposed Integration

### 1. Add Semantic Search to Blackboard

```python
# In blackboard.py, add semantic search via mgrep

def search_semantic(query: str, limit: int = 5) -> List[Message]:
    """Search blackboard messages semantically."""
    # Use recall-kraliki or mgrep for semantic matching
    results = mgrep_search(query, store="blackboard")
    return results[:limit]

# Usage in genomes:
# Before starting task, search for relevant context
python3 arena/blackboard.py search "similar task patterns"
```

### 2. Add Priority Queues

```python
# Priority levels for messages
PRIORITY = {
    "critical": 0,  # Blockers, errors, urgent
    "high": 1,      # Active work, claims
    "normal": 2,    # Updates, completions
    "low": 3,       # Ideas, suggestions
}

# Post with priority
python3 arena/blackboard.py post "[agent]" "[message]" -t ideas -p high
```

### 3. Add Control Unit (Arbiter)

Create `arena/arbiter.py`:

```python
class Arbiter:
    """Control unit for blackboard coordination."""

    def resolve_conflicts(self):
        """Detect and resolve conflicting claims."""
        claims = self.blackboard.get_claims()
        conflicts = self.find_overlapping_claims(claims)
        for conflict in conflicts:
            winner = self.arbitrate(conflict)
            self.blackboard.post(
                "ARBITER",
                f"CONFLICT_RESOLVED: {conflict.task} → {winner}"
            )

    def prioritize_tasks(self):
        """Reorder pending work by urgency/impact."""
        pending = self.blackboard.get_pending_tasks()
        prioritized = self.score_and_sort(pending)
        return prioritized

    def suggest_next_task(self, agent_type: str):
        """Recommend best task for agent type."""
        available = self.get_unclaimed_tasks()
        suitable = self.filter_by_genome(available, agent_type)
        return suitable[0] if suitable else None
```

### 4. Add Private Spaces

```python
# Agent-specific private scratchpads
python3 arena/blackboard.py write-private "[agent]" "[key]" "[value]"
python3 arena/blackboard.py read-private "[agent]" "[key]"

# Useful for:
# - Work-in-progress notes
# - Internal reasoning
# - Draft outputs before publishing
```

### 5. Add Channels/Topics

Already partially implemented with tags. Formalize:

```
#general - Default, all agents
#ideas - Discoveries, proposals, suggestions
#review - Work needing reviewer attention
#blockers - Escalations, human-needed items
#system - Dispatcher, arbiter messages
#promotions - Beta/prod promotion updates
```

## Affected Files
- `arena/blackboard.py` - Add semantic search, priority, private spaces
- `arena/arbiter.py` - New file for control unit
- `genomes/*.md` - Update to use enhanced blackboard features

## Risk Assessment
- Risk Level: **Medium**
- Rollback plan: Keep existing blackboard.py, new features are additive
- Arbiter is optional enhancement, not required for basic function

## Success Metrics
1. Reduction in conflicting claims (arbiter resolution)
2. Faster task discovery (semantic search)
3. Better prioritization (critical items handled first)
4. Cleaner blackboard (private spaces reduce noise)

## Implementation Effort
- Semantic search: Medium (~2-3 hours, integrate with mgrep)
- Priority queues: Low (~1 hour, simple flag addition)
- Arbiter: High (~4-6 hours, new subsystem)
- Private spaces: Low (~1 hour, simple key-value store)
- Channels: Already done (tags)

## Priority
**HIGH for semantic search + priority**
**MEDIUM for arbiter + private spaces**

## Phase Recommendation
1. **Now**: Add priority queues (quick win)
2. **Soon**: Add semantic search (high value)
3. **Later**: Add arbiter (requires careful design)
4. **Optional**: Private spaces (nice-to-have)
