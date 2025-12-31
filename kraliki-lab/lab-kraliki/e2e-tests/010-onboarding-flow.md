# E2E Test: 010 - Customer Onboarding Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 60 minutes (simulating 4-hour session) |
| Prerequisites | Provisioned VM, customer credentials |
| Location | Customer VM via SSH |

## Objective

Verify the complete customer onboarding flow as documented in the onboarding runbook, ensuring a customer can go from zero to productive in 4 hours.

## Pre-conditions

1. VM already provisioned (test 008 passed)
2. CLI tools installed (test 009 passed)
3. Customer has API keys ready
4. SSH credentials available

## Reference

Onboarding runbook: `/docs/onboarding-runbook.md`

## Test Steps

### Hour 1: Environment Setup (simulated 15 min)

#### Step 1.1: SSH Connection

| Action | Customer connects to VM |
|--------|------------------------|
| Command | `ssh customer@[VM_IP]` |
| Expected | SSH connection successful |
| Verification | Shell prompt appears |

#### Step 1.2: Environment Status Check

| Action | Verify environment ready |
|--------|-------------------------|
| Command | `magic-box status` |
| Expected | All components green |
| | - CLIProxyAPI running |
| | - Claude Code ready |
| | - Gemini CLI ready |
| | - Codex CLI ready |
| | - mgrep active |
| Verification | Health check passes |

#### Step 1.3: Component Tour

| Action | Test each component |
|--------|---------------------|
| Commands | `magic-box api test` |
| | `claude "hello"` |
| | `gemini "hello"` (if available) |
| | `codex "hello"` (if available) |
| | `mgrep "test query"` |
| Expected | Each responds appropriately |
| Verification | All components respond |

#### Step 1.4: API Key Configuration

| Action | Configure customer's API keys |
|--------|------------------------------|
| Command | `magic-box config` |
| Expected | - Anthropic key accepted |
| | - OpenAI key accepted (optional) |
| | - Google key accepted (optional) |
| Verification | Config saved, services restart |

### Hour 2: CLAUDE.md Customization (simulated 15 min)

#### Step 2.1: CLAUDE.md Concept

| Action | Explain and show CLAUDE.md |
|--------|---------------------------|
| Command | `cat ~/.magic-box/CLAUDE.md` or create new |
| Expected | Template or empty file |
| Verification | File accessible |

#### Step 2.2: Create Custom CLAUDE.md

| Action | Build customer's CLAUDE.md |
|--------|---------------------------|
| Template | ```markdown
# [Company Name] - Project Memory

## Business Context
[One paragraph about what they do]

## Our Terminology
[Industry-specific terms and definitions]

## Quality Standards
[Their specific requirements]

## Common Tasks
[Frequent workflows]

## Forbidden Actions
[Things the AI should never do]
``` |
| Expected | Customer-specific CLAUDE.md created |
| Verification | File saved and readable |

#### Step 2.3: Test CLAUDE.md Loading

| Action | Verify CLAUDE.md is used |
|--------|-------------------------|
| Command | `claude "What company are we working with?"` |
| Expected | Claude references the custom context |
| Verification | Context is applied |

### Hour 3: First Workflow (simulated 20 min)

#### Step 3.1: Pattern Introduction

| Action | Explain Build-Audit-Fix pattern |
|--------|--------------------------------|
| Concept | User Input > Opus (plan) > Gemini (build) > Codex (audit) > Opus (fix) > Output |
| Expected | Customer understands the flow |
| Verification | Customer can explain it back |

#### Step 3.2: Define Customer Task

| Action | Select real customer task |
|--------|--------------------------|
| Questions | - What are we building? |
| | - What's the expected output? |
| | - What would success look like? |
| Expected | Clear task definition |
| Verification | Written task description |

#### Step 3.3: Execute Workflow

| Action | Run Build-Audit-Fix on customer task |
|--------|-------------------------------------|
| Command | `claude "Build [customer task]. Use the Build-Audit-Fix pattern."` |
| Expected | Pattern executes with all phases |
| Verification | Output produced |

#### Step 3.4: Review Output

| Action | Assess workflow output |
|--------|----------------------|
| Questions | - Did it meet expectations? |
| | - What would they change? |
| | - Time comparison to traditional? |
| Expected | Positive assessment |
| Verification | Customer satisfied with output |

### Hour 4: Advanced Patterns (simulated 10 min)

#### Step 4.1: Parallel Execution Demo

| Action | Demonstrate parallel execution |
|--------|-------------------------------|
| Command | Run parallel streams pattern |
| Expected | Multiple tasks execute concurrently |
| Verification | Faster than sequential |

#### Step 4.2: Customer Solo Practice

| Action | Customer runs workflow independently |
|--------|-------------------------------------|
| Steps | - Choose new task |
| | - Configure approach |
| | - Execute |
| | - Iterate |
| Expected | Customer completes without help |
| Verification | Independent success |

#### Step 4.3: Wrap-Up

| Action | Finalize onboarding |
|--------|---------------------|
| Deliverables | - SSH credentials confirmed |
| | - Support channel access |
| | - Pattern library location |
| | - Contact info for questions |
| Expected | Customer has everything needed |
| Verification | Checklist complete |

## Pass Criteria

- SSH access works
- All components respond
- API keys configured
- Custom CLAUDE.md created
- First workflow completed
- Customer runs solo workflow successfully
- All deliverables handed off

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to first output | < 15 min |
| Workflow completion | 100% |
| Customer can work solo | Yes |
| Confidence level | High |

## Common Issues

| Issue | Resolution |
|-------|------------|
| API key format wrong | Show correct format |
| CLAUDE.md not loading | Check file path, permissions |
| Workflow incomplete | Check token limits |
| Model hallucinating | Add constraints to CLAUDE.md |
| SSH drops | Use mosh or check network |

## Post-Onboarding Checklist

- [ ] Send thank you email with session summary
- [ ] Share CLAUDE.md backup
- [ ] Add customer to support channel
- [ ] Log session notes in CRM
- [ ] Schedule Day 7 follow-up

## Customer Commitments to Verify

- [ ] First solo project within 48 hours
- [ ] Document one friction point
- [ ] Check-in call scheduled for Day 7

## Related Tests

- 008-vm-provisioning.md
- 009-cli-setup.md
- 004-demo-quick-audit.md
- 005-demo-agency-website.md
