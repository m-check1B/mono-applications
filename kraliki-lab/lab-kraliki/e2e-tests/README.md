# Lab by Kraliki E2E Test Suite

Manual end-to-end test plans for the Lab by Kraliki orchestration platform.

## Overview

Lab by Kraliki is a B2B SaaS product that provides orchestration capabilities, delivering multi-AI workflow acceleration.

## Test Environment

| Environment | URL | Notes |
|-------------|-----|-------|
| Production | https://lab.kraliki.com | Primary domain |
| Beta/Dev | https://lab.verduona.dev | Development testing |
| Local | http://127.0.0.1:3000 | Local dev server |

## Test Categories

### Landing Page Tests
| ID | Test | Priority |
|----|------|----------|
| 001 | Landing Page - Core Elements | HIGH |
| 002 | Landing Page - Pricing Section | HIGH |
| 003 | Landing Page - Responsive Design | MEDIUM |

### Demo Flow Tests
| ID | Test | Priority |
|----|------|----------|
| 004 | Quick Audit Demo | HIGH |
| 005 | Agency Website Demo | HIGH |
| 006 | Content Audit Demo | MEDIUM |
| 007 | Parallel Tasks Demo | MEDIUM |

### Provisioning Tests
| ID | Test | Priority |
|----|------|----------|
| 008 | VM Provisioning Flow | HIGH |
| 009 | CLI Setup Scripts | HIGH |

### Onboarding Tests
| ID | Test | Priority |
|----|------|----------|
| 010 | Customer Onboarding Flow | HIGH |

## How to Run Tests

### Manual Testing
1. Navigate to the test file (e.g., `001-landing-page-core.md`)
2. Follow the step-by-step instructions
3. Record results in the `results/` folder using the template

### Recording Results
```bash
# Create result file with timestamp
cp results/TEMPLATE.md results/001-landing-page-core_$(date +%Y%m%d_%H%M).md
# Edit and fill in results
```

## Test Result Template

Each test result should include:
- Test ID and Name
- Execution date
- Tester
- Environment tested
- Pass/Fail status per step
- Screenshots (if applicable)
- Issues found
- Overall verdict

## File Structure

```
e2e-tests/
|-- README.md                    # This file
|-- 001-landing-page-core.md     # Core landing page elements
|-- 002-landing-page-pricing.md  # Pricing section tests
|-- 003-responsive-design.md     # Mobile/tablet responsiveness
|-- 004-demo-quick-audit.md      # Quick audit demo flow
|-- 005-demo-agency-website.md   # Agency website demo
|-- 006-demo-content-audit.md    # Content audit demo
|-- 007-demo-parallel-tasks.md   # Parallel execution demo
|-- 008-vm-provisioning.md       # VM provisioning tests
|-- 009-cli-setup.md             # CLI setup scripts tests
|-- 010-onboarding-flow.md       # Customer onboarding
|-- results/                     # Test execution results
    |-- TEMPLATE.md              # Result template
```

## Priority Levels

- **HIGH**: Must pass before any release
- **MEDIUM**: Should pass for production quality
- **LOW**: Nice to have, can be deferred

## Notes

- These tests complement the automated Playwright tests in `/tests/e2e/`
- Focus on user journey and business-critical flows
- Update tests when features change
