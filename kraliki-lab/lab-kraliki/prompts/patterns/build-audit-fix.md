# Pattern: Build → Audit → Fix

## Overview

This pattern builds deliverables, audits them for quality, then fixes issues. It's a quality-first approach suitable for production code, client work, and anything where mistakes are costly.

## When to Use

✅ **Use this pattern when:**
- Quality is critical (production deployments, client work)
- Deliverables will be used by many people
- Security or performance matters
- Code/content will be maintained long-term
- Reputations are at stake

❌ **Don't use this pattern when:**
- Speed is more important than quality (prototypes, experiments)
- Tasks are simple/trivial (overkill for one-line fixes)
- Working on throw-away code (temporary, one-off scripts)

## The Process

### Step 1: Build (Gemini or Codex)
**Goal**: Create initial deliverable

**Worker Selection**:
- Frontend/UI → Gemini
- Backend/API → Codex
- Content → Gemini
- Mixed → Orchestrator decides based on primary output

**Guidelines**:
- Follow requirements exactly
- Use appropriate tech stack
- Deliver in expected format
- Note assumptions made

**Output**: Draft deliverable ready for audit

### Step 2: Quality Audit (Codex)
**Goal**: Identify all issues - code quality, security, performance, accessibility

**Worker**: Codex (specialized in auditing)

**Audit Checklist**:
```markdown
## Code Quality
- [ ] Follows language/framework best practices
- [ ] No hardcoded values (use env vars)
- [ ] Proper error handling
- [ ] Type hints/annotations
- [ ] No security vulnerabilities
- [ ] Performance optimized

## Security
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No secrets in code
- [ ] Input validation on all inputs
- [ ] Authentication on protected endpoints
- [ ] Rate limiting where applicable

## Accessibility
- [ ] Alt text on images
- [ ] Keyboard navigation works
- [ ] Color contrast meets WCAG 2.1 AA
- [ ] ARIA labels where needed
- [ ] Focus indicators visible

## Performance
- [ ] Images optimized (WebP, compressed)
- [ ] No large JavaScript bundles
- [ ] Lazy loading below fold
- [ ] Efficient database queries
- [ ] Caching used appropriately
```

**Output**: Audit report with issues categorized by severity

### Step 3: Fix Issues (Same Worker or Alternative)
**Goal**: Resolve all audit findings

**Worker Selection**:
- Original worker fixes non-critical issues
- If original worker struggles with fixes, switch to alternative worker
- Critical issues may need specialist attention

**Fix Priority**:
1. **Critical** 🔴 - Security vulnerabilities, data loss risks, broken functionality
2. **High** 🟠 - Performance issues, accessibility failures, poor user experience
3. **Medium** 🟡 - Code quality, maintainability concerns
4. **Low** 🟢 - Style inconsistencies, minor optimizations

**Guidelines**:
- Fix one issue at a time
- Test each fix to verify it works
- Don't introduce new issues while fixing
- Re-audit after fixes if critical issues were found

**Output**: Fixed deliverable ready for final review

### Step 4: Final Review (Orchestrator)
**Goal**: Verify all issues resolved and quality standards met

**Check**:
- [ ] All critical issues resolved
- [ ] All high issues resolved
- [ ] No new issues introduced
- [ ] Meets original success criteria
- [ ] Ready for production/client delivery

**Decision**:
- **Pass** → Deliver to user
- **Fail** → Return to Step 3 with specific feedback

## Example Execution

### Task: Build User Authentication API

**Step 1: Build (Codex)**
```python
# auth.py - Initial implementation
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.query(User).filter(User.email == data['email']).first()
    if user and check_password(user.password, data['password']):
        return jsonify({'token': generate_token(user.id)})
    return jsonify({'error': 'Invalid credentials'}), 401
```

**Step 2: Audit (Codex)**
```markdown
## Audit Report

### Critical Issues 🔴
1. Line 4 - SQL injection risk
   - **Impact**: Database can be compromised
   - **Fix**: Use parameterized queries or ORM methods

2. Line 5 - No rate limiting
   - **Impact**: Brute force attacks possible
   - **Fix**: Add rate limiting middleware

### High Issues 🟠
1. No password hashing in check_password()
   - **Impact**: Compromised passwords reveal all users
   - **Fix**: Use bcrypt or Argon2

### Medium Issues 🟡
1. No input validation on email
   - **Impact**: Invalid data causes errors
   - **Fix**: Add email format validation

2. Missing error logging
   - **Impact**: Can't debug authentication failures
   - **Fix**: Add logging for failed attempts
```

**Step 3: Fix (Codex)**
```python
# auth.py - Fixed implementation
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    data = request.get_json()

    # Validate email format
    if not is_valid_email(data['email']):
        return jsonify({'error': 'Invalid email'}), 400

    # Parameterized query (ORM method)
    user = db.session.scalar(select(User).where(User.email == data['email']))

    if user and bcrypt.checkpw(data['password'].encode(), user.password_hash):
        logger.info(f"User {user.email} logged in")
        return jsonify({'token': generate_token(user.id)})

    logger.warning(f"Failed login attempt for {data['email']}")
    return jsonify({'error': 'Invalid credentials'}), 401
```

**Step 4: Final Review (Orchestrator)**
```markdown
## Final Review Results

✅ All critical issues resolved:
- SQL injection prevented (using ORM)
- Rate limiting implemented (5 attempts/15 min)
- Password hashing added (bcrypt)

✅ All high issues resolved:
- Password verification uses bcrypt.checkpw()

✅ Medium issues resolved:
- Email validation added
- Error logging implemented

✅ No new issues introduced

✅ Ready for production deployment
```

## Time Estimates

| Step | Worker | Time Estimate |
|-------|---------|---------------|
| Build | Gemini/Codex | 30-60 min |
| Audit | Codex | 15-30 min |
| Fix | Gemini/Codex | 30-60 min |
| Final Review | Orchestrator | 5-10 min |
| **Total** | | **80-160 min** |

## Success Metrics

Track these to measure pattern effectiveness:

- **First-Pass Quality**: % of issues found in audit
- **Fix Success Rate**: % of issues resolved in first fix attempt
- **Time to Delivery**: Total time from task assignment to completion
- **Re-Audit Needed**: % of tasks requiring second audit cycle
- **User Satisfaction**: Post-delivery feedback scores

## Variations

### Light Audit (Speed Trade-off)
Skip low-priority issues, focus on critical/high only.
- Use when: Time-constrained, quality threshold is "good enough"
- Risk: Minor issues may slip through

### Multiple Auditors (Quality Trade-off)
Have two workers audit independently, compare findings.
- Use when: Highest quality needed (production launch, security-critical)
- Benefit: Catches more issues
- Cost: Takes more time

### Audit-First (Process Reordering)
Audit requirements/plan before building.
- Use when: Unclear requirements, complex technical challenges
- Benefit: Reduces rework, catches issues early
- Risk: Slower initial progress

## Common Failure Modes

### Failure: Over-Auditing
**Symptom**: Finding issues in non-critical areas
**Fix**: Focus audit on what matters most (security, performance, accessibility)
**Learning**: Not everything needs to be perfect

### Failure: Fix Introduces New Issues
**Symptom**: Step 3 fixes create different problems
**Fix**: Test changes thoroughly, consider re-audit if critical changes
**Learning**: Changes have ripple effects, be careful

### Failure: Endless Re-Audit Cycles
**Symptom**: Each fix reveals more issues
**Fix**: Define "good enough" criteria, stop when met
**Learning**: Perfect is the enemy of done
