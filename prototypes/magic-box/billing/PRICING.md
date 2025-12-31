# Magic Box Pricing Details

**Version**: 1.0.0
**Last Updated**: 2025-12-28

---

## Pricing Philosophy

Magic Box pricing follows these principles:

1. **Value-Based**: Price reflects productivity gains (16x claimed)
2. **Fair**: Heavy users pay more, light users pay less
3. **Transparent**: No hidden fees, clear cost breakdown
4. **Competitive**: Below enterprise AI platform pricing

---

## Tier Comparison

| Feature | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| **Monthly Price** | EUR 99 | EUR 199 | EUR 499 |
| **Annual Price** | EUR 990 | EUR 1,990 | EUR 4,990 |
| **VM Licenses** | 1 | 3 | Unlimited |
| **Compute Hours** | 100/month | 300/month | Unlimited |
| **API Credits** | EUR 50/month | EUR 150/month | EUR 500/month |
| **Prompt Library** | Basic (12) | Full (22+) | Full + Custom |
| **Support** | Community | Priority Email | Dedicated Slack |
| **SLA** | None | None | 99.9% |
| **Custom Patterns** | No | Yes | Yes + Development |
| **Central Dashboard** | No | Team Dashboard | Multi-VM Dashboard |

---

## Detailed Tier Breakdown

### Starter Tier - EUR 99/month

**Target Customer:**
- Solo developers
- Small startups (1-2 developers)
- Personal projects
- Evaluation/POC phase

**What's Included:**

| Resource | Included | Overage Rate |
|----------|----------|--------------|
| VM Licenses | 1 | N/A (upgrade to Pro) |
| Compute Hours | 100 hours | EUR 0.05/hour |
| API Credits | EUR 50 | Pass-through + 20% |

**Prompt Library Access:**
- Orchestrator prompts (5)
- Worker prompts - Gemini only (3)
- Basic patterns (2)
- Content prompts (2)

**Support:**
- Community Discord access
- Self-service documentation
- Response time: Best effort

**Typical Use Case:**
Developer using Magic Box 4 hours/day, 5 days/week = 80 hours/month.
With moderate API usage (~EUR 30/month), fits comfortably in Starter.

---

### Pro Tier - EUR 199/month

**Target Customer:**
- Growing teams (3-10 developers)
- Agencies
- Power users
- Production workloads

**What's Included:**

| Resource | Included | Overage Rate |
|----------|----------|--------------|
| VM Licenses | 3 | N/A (upgrade to Enterprise) |
| Compute Hours | 300 hours | EUR 0.04/hour |
| API Credits | EUR 150 | Pass-through + 15% |

**Prompt Library Access:**
- All Orchestrator prompts (5)
- All Worker prompts (8)
- All Patterns (4)
- All Content prompts (3)
- All Data prompts (2)
- Custom pattern creation tools

**Support:**
- Priority email support
- Response time: 24 hours
- Access to beta features

**Additional Features:**
- Team usage dashboard
- Usage alerts
- API key management
- Pattern analytics

**Typical Use Case:**
3-person team using Magic Box 6 hours/day = 90 hours/person/month.
Total: 270 hours/month. With EUR 120/month API usage, fits in Pro.

---

### Enterprise Tier - EUR 499/month

**Target Customer:**
- Large teams (10+ developers)
- Enterprise organizations
- Mission-critical workloads
- Multi-project deployments

**What's Included:**

| Resource | Included | Overage Rate |
|----------|----------|--------------|
| VM Licenses | Unlimited | N/A |
| Compute Hours | Unlimited | N/A |
| API Credits | EUR 500 | Pass-through + 10% |

**Prompt Library Access:**
- Everything in Pro
- Custom prompt development (included)
- Priority access to new prompts

**Support:**
- Dedicated Slack channel
- Named support contact
- Response time: 4 hours
- Monthly review calls
- Onboarding assistance

**SLA:**
- 99.9% uptime guarantee
- Credits for downtime
- Priority incident response

**Additional Features:**
- Central dashboard for all VMs
- Custom integrations
- SSO/SAML support
- Audit logging
- Compliance documentation

**Typical Use Case:**
20-person engineering team with multiple projects.
Heavy API usage (EUR 800/month). Enterprise provides best value.

---

## Overage Pricing Details

### Compute Hours

Compute hours are calculated from resource monitoring samples.
Each 5-minute sample = 0.0833 hours.

| Tier | Included | Overage Rate | Example Overage Cost |
|------|----------|--------------|---------------------|
| Starter | 100 hours | EUR 0.05/hour | 50 extra hours = EUR 2.50 |
| Pro | 300 hours | EUR 0.04/hour | 100 extra hours = EUR 4.00 |
| Enterprise | Unlimited | N/A | N/A |

### API Credits

API credits cover pass-through costs for Claude, OpenAI, and Gemini APIs.

**Pass-Through Pricing:**

| Provider | Model | Input (per 1M) | Output (per 1M) |
|----------|-------|----------------|-----------------|
| Claude | claude-3-5-sonnet | $3.00 | $15.00 |
| Claude | claude-opus-4 | $15.00 | $75.00 |
| OpenAI | gpt-4 | $30.00 | $60.00 |
| OpenAI | gpt-4-turbo | $10.00 | $30.00 |
| Gemini | gemini-1.5-pro | $1.25 | $5.00 |
| Gemini | gemini-2-flash | $0.10 | $0.40 |

**Margin Applied:**

| Tier | Margin | Example |
|------|--------|---------|
| Starter | +20% | $10 pass-through = EUR 12 charged |
| Pro | +15% | $10 pass-through = EUR 11.50 charged |
| Enterprise | +10% | $10 pass-through = EUR 11 charged |

**Note**: USD to EUR conversion applied at billing time.

---

## Annual Pricing

Annual subscriptions receive 17% discount (2 months free).

| Tier | Monthly | Annual | Savings |
|------|---------|--------|---------|
| Starter | EUR 99 | EUR 990 | EUR 198 |
| Pro | EUR 199 | EUR 1,990 | EUR 398 |
| Enterprise | EUR 499 | EUR 4,990 | EUR 998 |

Annual subscriptions:
- Billed upfront
- Locked pricing for 12 months
- No mid-term downgrade (can upgrade)
- Early termination: No refund

---

## Add-Ons

### Additional VM Licenses (Pro tier only)

| Add-On | Price |
|--------|-------|
| +1 VM License | EUR 49/month |
| +2 VM Licenses | EUR 89/month |

### Support Upgrades

| Add-On | Price | Description |
|--------|-------|-------------|
| Priority Support | EUR 99/month | For Starter tier, get Pro-level support |
| Dedicated Support | EUR 199/month | For Pro tier, get Enterprise-level support |

### Custom Development

| Service | Price |
|---------|-------|
| Custom Prompt | EUR 299 one-time |
| Custom Pattern | EUR 499 one-time |
| Integration Development | EUR 149/hour |
| Training Session | EUR 299/2 hours |

---

## Comparison with Alternatives

### vs. Individual AI Subscriptions

| Service | Monthly Cost |
|---------|--------------|
| Claude Pro | $20/month |
| ChatGPT Plus | $20/month |
| GitHub Copilot | $19/month |
| Total | $59/month |

Magic Box Starter at EUR 99/month provides:
- All three AIs working together
- Orchestration capabilities
- 16x productivity multiplier
- Self-hosted privacy

**Value**: 5-10x more productive for 1.7x the cost.

### vs. Enterprise AI Platforms

| Platform | Monthly Cost |
|----------|--------------|
| Anthropic API (heavy usage) | $500-2000/month |
| Azure OpenAI Enterprise | $1000+/month |
| AI Development Team | $15,000+/month |

Magic Box Enterprise at EUR 499/month provides:
- Multi-AI orchestration
- Prompt engineering included
- Self-hosted privacy
- No per-seat licensing

**Value**: Enterprise AI capabilities at startup pricing.

---

## Pricing FAQ

**Q: Can I switch tiers mid-month?**
A: Yes. Upgrades are prorated immediately. Downgrades take effect next billing cycle.

**Q: What happens if I exceed API credits?**
A: You continue using the service. Overage is charged at tier rate on next invoice.

**Q: Can I cap my spending?**
A: Yes. Set spending alerts in the dashboard. Auto-pause available on request.

**Q: Is there a free trial?**
A: Yes. 14-day free trial with Starter tier limits. No credit card required.

**Q: Can I pay in USD?**
A: Yes. Stripe handles currency conversion. Displayed prices are in EUR.

**Q: Are there volume discounts?**
A: Enterprise tier includes volume discounts. Contact sales for custom pricing.

**Q: What's the refund policy?**
A: Monthly: Cancel anytime, no refund for current month.
Annual: No refund, but can be transferred to another organization.

---

## Revenue Projections

### Per-Customer Economics

| Tier | Monthly | Gross Margin | LTV (24 months) |
|------|---------|--------------|-----------------|
| Starter | EUR 99 | 85% | EUR 2,376 |
| Pro | EUR 199 | 80% | EUR 4,776 |
| Enterprise | EUR 499 | 75% | EUR 11,976 |

### Target Mix (Year 1)

| Tier | Target Customers | Monthly Revenue |
|------|------------------|-----------------|
| Starter | 20 | EUR 1,980 |
| Pro | 10 | EUR 1,990 |
| Enterprise | 2 | EUR 998 |
| **Total** | **32** | **EUR 4,968** |

Aligns with ME-90 goal of EUR 3-5K MRR by March 2026.

---

## Price Change Policy

- Existing customers: 90-day notice for price increases
- Grandfathered rates: Available for early adopters
- Annual customers: Locked pricing for contract term
- Enterprise: Custom agreements may have different terms
