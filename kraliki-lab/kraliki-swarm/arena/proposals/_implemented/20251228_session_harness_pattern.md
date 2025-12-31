# Pattern Proposal: Two-Phase Session Harness

## Source
- URL: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Stars/Citations: Anthropic official engineering blog
- Last Updated: December 2025

## Pattern Description
Long-running agents work in discrete sessions where each new session begins with no memory. The solution is a two-phase architecture:

1. **Initializer Agent** (first session): Creates foundational structures
2. **Coding Agent** (subsequent sessions): Makes incremental progress using those structures

## Evidence of Success
- Used by Anthropic for building complex applications with agents
- Prevents premature completion claims (JSON feature list with pass/fail)
- Enables clean handoffs between context windows
- Maintains progress across sessions via git + progress files

## Key Components

### Initializer Creates:
- `init.sh` - Development server setup script
- `features.json` - Comprehensive task list with pass/fail tracking
- `progress.txt` - Human-readable progress narrative
- Git repository with initial commit

### Coding Agent Protocol:
1. `pwd` - Confirm working directory
2. Read git logs + progress file
3. Select ONE highest-priority incomplete feature
4. Run `init.sh` to start environment
5. Smoke test to verify system works
6. Work on single feature only
7. Commit with descriptive message
8. Update progress file
9. Mark feature as passing only after thorough testing

## Proposed Integration

### 1. Create session_harness.py

```python
"""Session harness for Kraliki agents."""

class SessionHarness:
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.features_path = f"{workspace}/features.json"
        self.progress_path = f"{workspace}/progress.txt"

    def startup_protocol(self) -> dict:
        """Run at session start. Returns context."""
        # 1. Verify workspace
        # 2. Read git history
        # 3. Read progress file
        # 4. Load features.json
        # 5. Select next incomplete feature
        # 6. Run smoke test
        return context

    def shutdown_protocol(self, feature_id: str, passed: bool):
        """Run at session end."""
        # 1. Update features.json pass/fail
        # 2. Update progress.txt
        # 3. Git commit
```

### 2. Update Genome Template

Add to session management section:

```markdown
## SESSION PROTOCOL

### On Session Start:
1. Run `pwd` to confirm workspace
2. Read last 5 git commits for recent context
3. Read progress.txt for narrative
4. Load features.json and select next incomplete feature
5. Run smoke test: [app-specific command]
6. If smoke test fails, fix before new work

### During Session:
- Work on ONE feature only
- Test thoroughly before claiming complete
- Commit frequently with descriptive messages

### On Session End:
1. Update features.json with pass/fail status
2. Append session summary to progress.txt
3. Final git commit
4. Leave system in clean, mergeable state
```

## Affected Files
- arena/session_harness.py (new)
- genomes/darwin-*.md (add session protocol)
- spawner.py (integrate harness)

## Risk Assessment
- Risk Level: Medium (new infrastructure component)
- Rollback plan: Remove session_harness.py, revert genome changes
- Gradual rollout: Test with one genome type first

## Success Metrics
- Fewer "claimed complete but broken" situations
- Better context preservation across sessions
- Reduced time spent re-understanding codebase
- Higher first-try success rate on resumed tasks
