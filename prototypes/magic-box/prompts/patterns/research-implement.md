# Research-Implement Pattern

**Purpose:** Research before building to ensure informed implementation decisions.

## Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   RESEARCH   │────▶│     PLAN     │────▶│  IMPLEMENT   │
│   (Gemini)   │     │   (Claude)   │     │   (Codex)    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## When to Use

- Unfamiliar technologies or domains
- Multiple valid implementation approaches
- Integration with external services/APIs
- Complex algorithms or patterns
- Security-sensitive features

## When NOT to Use

- Well-understood, routine tasks
- Tight deadlines (research takes time)
- Simple CRUD operations
- Following established patterns

## Phase 1: Research

**Worker:** Gemini (researcher)

**Objectives:**
- Understand the problem domain
- Survey available solutions
- Identify best practices
- Find relevant documentation
- Note potential pitfalls

**Input:**
```yaml
research_request:
  topic: "What needs to be researched"
  context: "Why we need this, what we're building"
  questions:
    - "Specific question 1"
    - "Specific question 2"
  constraints:
    - "Must work with X"
    - "Cannot use Y"
```

**Output:**
```yaml
research_findings:
  summary: "Executive summary"

  key_insights:
    - insight: "Important finding"
      source: "Where this came from"
      confidence: "high|medium|low"

  options:
    - name: "Option A"
      pros: []
      cons: []
      best_for: "When to use this"

  recommendations:
    primary: "Recommended approach"
    rationale: "Why"

  references:
    - name: "Resource name"
      url: "Link"
      relevance: "How it helps"

  pitfalls:
    - "Things to watch out for"
```

## Phase 2: Plan

**Worker:** Claude (orchestrator/strategic-planning)

**Objectives:**
- Synthesize research into actionable plan
- Make architectural decisions
- Define implementation sequence
- Set success criteria

**Input:**
```yaml
planning_request:
  goal: "What we're building"
  research: "Research findings from Phase 1"
  constraints:
    time: "Available time"
    resources: "Available resources"
```

**Output:**
```yaml
implementation_plan:
  approach: "High-level approach chosen"

  architecture:
    components:
      - name: "Component"
        purpose: "What it does"
        technology: "How it's built"

  phases:
    - phase: 1
      name: "Foundation"
      tasks:
        - "Task 1"
      duration: "Estimate"
      deliverable: "What's produced"

  decisions:
    - decision: "What was decided"
      rationale: "Why"
      alternatives_rejected: ["What else was considered"]

  success_criteria:
    - "How we know it's done"

  risks:
    - risk: "What could go wrong"
      mitigation: "How to handle it"
```

## Phase 3: Implement

**Worker:** Codex (appropriate builder)

**Objectives:**
- Execute the plan
- Build working code
- Include tests
- Follow best practices from research

**Input:**
```yaml
implementation_request:
  plan: "Implementation plan from Phase 2"
  research: "Key findings to remember"
  phase: "Which phase to implement"
```

**Output:**
```yaml
implementation:
  files:
    - path: "file path"
      content: "code"

  tests:
    - path: "test file path"
      content: "tests"

  documentation:
    - "API docs, README updates, etc."

  notes:
    - "Implementation decisions made"
    - "Deviations from plan (if any)"
```

## Example: Payment Integration

### Phase 1: Research

```yaml
research_request:
  topic: "Payment gateway integration"
  context: "Adding payment processing to SaaS app"
  questions:
    - "What payment providers work well for subscriptions?"
    - "How to handle webhooks securely?"
    - "What's the PCI compliance requirement?"
  constraints:
    - "Must support EUR and USD"
    - "Subscription model with monthly/annual"
    - "Self-hosted, not no-code"

research_findings:
  summary: |
    Stripe is the clear leader for subscription payments.
    Use Checkout for simplicity or Elements for customization.
    Webhook verification is critical for security.

  key_insights:
    - insight: "Stripe handles PCI compliance for card data"
      source: "Stripe documentation"
      confidence: "high"

    - insight: "Webhooks should verify signature before processing"
      source: "Stripe security best practices"
      confidence: "high"

    - insight: "Use idempotency keys for safe retries"
      source: "Stripe API docs"
      confidence: "high"

  options:
    - name: "Stripe Checkout (hosted)"
      pros:
        - "Pre-built UI, mobile optimized"
        - "Handles localization"
        - "Quick to implement"
      cons:
        - "Less customization"
        - "Redirect flow"
      best_for: "Fast MVP, standard checkout"

    - name: "Stripe Elements (embedded)"
      pros:
        - "Full UI control"
        - "In-page experience"
        - "Custom styling"
      cons:
        - "More implementation work"
        - "Handle more edge cases"
      best_for: "Custom branded experience"

  recommendations:
    primary: "Stripe Checkout"
    rationale: |
      Faster to implement, handles edge cases.
      Can migrate to Elements later if needed.

  references:
    - name: "Stripe Subscriptions Quickstart"
      url: "https://stripe.com/docs/billing/quickstart"
      relevance: "Step-by-step guide"

  pitfalls:
    - "Don't process payments without webhook verification"
    - "Handle failed payments with dunning emails"
    - "Store subscription status in your DB, not just Stripe"
```

### Phase 2: Plan

```yaml
implementation_plan:
  approach: "Stripe Checkout with subscription management"

  architecture:
    components:
      - name: "Pricing API"
        purpose: "Fetch plans, create checkout sessions"
        technology: "Python/FastAPI + stripe-python"

      - name: "Webhook Handler"
        purpose: "Process Stripe events"
        technology: "FastAPI endpoint with signature verification"

      - name: "Subscription Model"
        purpose: "Track subscription status in DB"
        technology: "SQLAlchemy model"

  phases:
    - phase: 1
      name: "Stripe Setup"
      tasks:
        - "Configure Stripe products and prices"
        - "Set up webhook endpoint"
        - "Create subscription database model"
      deliverable: "Stripe configured, basic model"

    - phase: 2
      name: "Checkout Flow"
      tasks:
        - "Build checkout session API"
        - "Handle checkout.session.completed webhook"
        - "Update user subscription status"
      deliverable: "Working checkout flow"

    - phase: 3
      name: "Subscription Management"
      tasks:
        - "Build customer portal redirect"
        - "Handle subscription.updated/deleted webhooks"
        - "Add billing page to frontend"
      deliverable: "Full subscription lifecycle"

  decisions:
    - decision: "Use Stripe Checkout over Elements"
      rationale: "Faster implementation, handles edge cases"
      alternatives_rejected: ["Stripe Elements", "PayPal", "Paddle"]

  success_criteria:
    - "User can subscribe via checkout"
    - "Subscription status updates on webhook"
    - "User can manage subscription in portal"
```

### Phase 3: Implement (Phase 1)

```yaml
implementation:
  files:
    - path: "src/models/subscription.py"
      content: |
        from sqlalchemy import Column, String, DateTime, Enum
        from datetime import datetime

        class Subscription(Base):
            __tablename__ = "subscriptions"

            id = Column(String, primary_key=True)
            user_id = Column(String, ForeignKey("users.id"))
            stripe_subscription_id = Column(String, unique=True)
            stripe_customer_id = Column(String)
            status = Column(String)  # active, canceled, past_due
            plan = Column(String)  # monthly, annual
            current_period_end = Column(DateTime)
            created_at = Column(DateTime, default=datetime.utcnow)

    - path: "src/api/webhooks.py"
      content: |
        import stripe
        from fastapi import APIRouter, Request, HTTPException

        router = APIRouter()

        @router.post("/webhooks/stripe")
        async def stripe_webhook(request: Request):
            payload = await request.body()
            sig = request.headers.get("stripe-signature")

            try:
                event = stripe.Webhook.construct_event(
                    payload, sig, STRIPE_WEBHOOK_SECRET
                )
            except stripe.error.SignatureVerificationError:
                raise HTTPException(400, "Invalid signature")

            # Handle events...

  tests:
    - path: "tests/test_webhooks.py"
      content: |
        def test_webhook_rejects_invalid_signature():
            response = client.post(
                "/webhooks/stripe",
                content=b"fake payload",
                headers={"stripe-signature": "invalid"}
            )
            assert response.status_code == 400
```

## Best Practices

1. **Research breadth first** - Understand the landscape before diving deep
2. **Document decisions** - Record why you chose one approach over others
3. **Validate assumptions** - Research should confirm or refute initial ideas
4. **Iterate if needed** - Plan may reveal research gaps
5. **Time-box research** - Don't over-research, decide and move forward
