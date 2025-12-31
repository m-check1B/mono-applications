# Pattern Proposal: Reflexion Self-Correction

## Source
- Paper: https://arxiv.org/abs/2303.11366
- LangChain Blog: https://blog.langchain.com/reflection-agents/
- Stars/Citations: 900+ citations, implemented in major frameworks
- Last Updated: Active in 2025, widely adopted

## Pattern Description
Reflexion adds a post-task reflection loop where agents:
1. Complete a task
2. Evaluate their own performance
3. Generate self-critique identifying failures/gaps
4. Store learnings in episodic memory
5. Retry with accumulated wisdom

Unlike fine-tuning, this uses text-based feedback as reinforcement. The model stays frozen - only the prompts evolve.

## Evidence of Success
- AlfWorld: 130/134 tasks completed (vs lower for ReAct alone)
- HotPotQA: Significant improvement on reasoning questions
- HumanEval: Better code generation through iterative refinement

## Proposed Integration

### 1. Add to All Genomes
Add post-task reflection section before DARWIN_RESULT:

```markdown
## POST-TASK REFLECTION (Before DARWIN_RESULT)

Before outputting DARWIN_RESULT, reflect on your execution:

1. **What worked well?** - Identify successful strategies
2. **What failed or was suboptimal?** - Note errors, inefficiencies
3. **What would I do differently?** - Specific improvements
4. **Key learnings** - Store via memory.py for future runs

Post reflection to blackboard:
python3 arena/blackboard.py post "[agent]" "REFLECTION: [key learning]" -t ideas
```

### 2. Store in Memory System
```bash
# Store reflection for cross-agent learning
DARWIN_AGENT="[agent]" python3 arena/memory.py remember "REFLECTION: [task] - [learning]"
```

### 3. Retrieve Before Similar Tasks
```bash
# Check for relevant past reflections
DARWIN_AGENT="[agent]" python3 arena/memory.py recall "REFLECTION task-type"
```

## Affected Files
- `genomes/*.md` - All genome files get reflection section
- `arena/memory.py` - Already exists, used for storage
- `arena/blackboard.py` - Already exists, used for visibility

## Risk Assessment
- Risk Level: **Low**
- Rollback plan: Remove reflection section from genomes
- No code changes to arena infrastructure needed

## Success Metrics
1. Increase in task completion rate (track via fitness.py)
2. Reduction in retry loops
3. Cross-agent learning visible in blackboard reflections
4. Quality score improvements in DARWIN_RESULT

## Implementation Effort
- Minimal: Add ~15 lines to each genome template
- No new infrastructure needed
- Use existing memory.py and blackboard.py

## Priority
**HIGH** - Low effort, high potential impact, uses existing infrastructure
