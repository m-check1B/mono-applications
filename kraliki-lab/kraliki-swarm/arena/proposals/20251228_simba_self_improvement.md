# Pattern Proposal: SIMBA-Style Self-Improvement

## Source
- URL: https://dspy.ai/learn/optimization/optimizers/
- URL: https://github.com/stanfordnlp/dspy
- Stars/Citations: Stanford NLP, 30K+ GitHub stars
- Last Updated: December 2025

## Pattern Description
SIMBA (Stochastic Introspective Mini-Batch Ascent) uses stochastic mini-batch sampling to identify challenging examples with high output variability, then applies LLM introspection to analyze failures and generate self-reflective improvement rules.

Key insight: Instead of manual prompt engineering, use automated failure analysis to generate improvement rules that are applied to prompts/genomes.

## Evidence of Success
- Documented improvement from 24% to 51% on evaluation criterion task
- Stanford NLP production-tested framework
- Used by enterprise teams for automated prompt optimization
- GEPA optimizer shows up to 11% additional improvement

## Proposed Integration

### 1. Create simba_improver.py

```python
"""SIMBA-style self-improvement for Kraliki genomes."""

class SIMBAImprover:
    def __init__(self, genome_path: str):
        self.genome_path = genome_path
        self.failure_log = []
        self.improvement_rules = []

    def log_failure(self, task: dict, output: dict, expected: dict):
        """Log a failure case for analysis."""
        self.failure_log.append({
            'task': task,
            'output': output,
            'expected': expected,
            'timestamp': datetime.now().isoformat()
        })

    def analyze_failures_batch(self, batch_size: int = 5):
        """Introspectively analyze failure batch."""
        # Sample challenging failures (high variability)
        sample = self._sample_challenging_failures(batch_size)

        # Generate improvement rules via LLM introspection
        prompt = f"""Analyze these agent failures and identify patterns:

{json.dumps(sample, indent=2)}

For each pattern identified:
1. What went wrong?
2. Why did it happen?
3. What rule would prevent this?

Output format:
- RULE: [concise improvement rule]
- APPLY TO: [section of genome to modify]
"""
        rules = self._call_llm(prompt)
        self.improvement_rules.extend(rules)
        return rules

    def apply_improvements(self):
        """Apply accumulated rules to genome."""
        # Read current genome
        # For each rule, modify relevant section
        # Write updated genome
        pass
```

### 2. Integration with darwin-self-improver

Add to darwin-self-improver genome:

```markdown
## SIMBA IMPROVEMENT CYCLE

1. **Collect Failures**: After each genome run, log failures with:
   - Task description
   - Expected output
   - Actual output
   - Error details

2. **Batch Analysis** (every 10 failures):
   - Sample 5 most challenging failures (high variability)
   - Introspect: What patterns caused these failures?
   - Generate improvement rules

3. **Rule Application**:
   - For each rule, identify target genome section
   - Apply modification
   - Test on held-out failure cases
   - If improvement, commit rule permanently

4. **Continuous Evolution**:
   - Track which rules improved which metrics
   - Prune rules that don't help
   - Combine successful rules into genome templates
```

## Affected Files
- arena/simba_improver.py (new)
- genomes/darwin-self-improver.md (add SIMBA cycle)
- arena/fitness.py (log failures for SIMBA)

## Risk Assessment
- Risk Level: Medium (automated genome modification)
- Rollback plan: Git history preserves all genome versions
- Safety: Require human approval for rule application initially
- Gradual: Start with suggestions, move to auto-apply after validation

## Success Metrics
- Increasing fitness scores over generations
- Decreasing failure rates on recurring task types
- Accumulated improvement rules that persist
- Measurable via fitness.py trend analysis
