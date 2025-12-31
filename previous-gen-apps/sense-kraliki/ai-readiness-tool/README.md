# AI Readiness Assessment Tool

**Lead generation tool for Verduona's AI consulting services.**

## Overview

The AI Readiness Assessment is a self-service questionnaire that helps SMEs (Small and Medium Enterprises) understand their current AI maturity level and readiness to adopt AI solutions. By completing a 5-10 minute assessment, businesses receive:

1. **Personalized AI Maturity Score** (L1-L5)
2. **Detailed breakdown** across 5 key dimensions
3. **Actionable recommendations** tailored to their level
4. **Clear next steps** with Verduona services

## Lead Generation Strategy

### Funnel Architecture

```
AWARENESS                    CONSIDERATION                 CONVERSION
    |                             |                            |
    v                             v                            v
[Blog/Social] --> [Assessment Landing] --> [Results + CTA] --> [Consultation Call]
                         |
                         v
                  [Email Capture]
                         |
                         v
                  [Nurture Sequence]
```

### Value Exchange

**What prospect gives:** Email, company info, 5-10 minutes answering questions

**What prospect gets:**
- Immediate AI maturity score
- Personalized 3-page PDF report
- Comparison to industry benchmarks
- 3 quick wins they can implement today
- Option for free 15-min consultation

### Lead Quality Signals

| Signal | Weight | Meaning |
|--------|--------|---------|
| Company size > 20 | High | Can afford consulting |
| Budget score > 3 | High | Has investment capacity |
| Urgency indicators | High | Ready to act |
| Completed all questions | Medium | Engaged prospect |
| Requested consultation | Highest | Sales-ready lead |

## Assessment Structure

**5 Categories, 25 Questions Total**

| Category | Questions | Weight | Focus |
|----------|-----------|--------|-------|
| Data Infrastructure | 5 | 25% | Data quality, accessibility, governance |
| Team AI Literacy | 5 | 20% | Skills, training, openness to AI |
| Process Automation | 5 | 20% | Current automation, pain points |
| Budget & Investment | 5 | 15% | Financial readiness |
| Strategic Alignment | 5 | 20% | Leadership buy-in, goals clarity |

**Completion Time:** 5-10 minutes

## Maturity Levels

| Level | Score | Name | Description |
|-------|-------|------|-------------|
| L1 | 0-20 | AI Curious | Just starting to explore AI possibilities |
| L2 | 21-40 | AI Aware | Understanding benefits, no implementation |
| L3 | 41-60 | AI Ready | Foundation in place, ready to pilot |
| L4 | 61-80 | AI Active | Running AI projects, scaling challenges |
| L5 | 81-100 | AI Leader | AI embedded in operations, driving value |

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This overview |
| `questionnaire.md` | Full 25-question assessment |
| `scoring.md` | Scoring methodology and calculations |
| `results-templates/` | Level-specific result pages |
| `email-sequences/` | Follow-up email templates |
| `landing-page.md` | Landing page copy |
| `integration.md` | Verduona service integration points |

## Implementation Options

### Phase 1: MVP (Typeform/Tally)
- Quick launch using existing form tools
- Manual scoring and email follow-up
- Validate demand before custom build

### Phase 2: Custom Web App
- Self-hosted assessment
- Automatic scoring and PDF generation
- CRM integration (EspoCRM)
- Email automation (Brevo/n8n)

### Phase 3: AI-Enhanced
- Dynamic questions based on answers
- GPT-generated personalized recommendations
- Industry-specific benchmarks
- Chatbot consultation scheduling

## Integration with Verduona Services

Based on assessment results, prospects are directed to:

| Maturity Level | Primary CTA | Verduona Service |
|----------------|-------------|------------------|
| L1 (AI Curious) | AI Academy Course | Learn by Kraliki |
| L2 (AI Aware) | AI Strategy Workshop | Consulting |
| L3 (AI Ready) | Pilot Project Proposal | Consulting + Apps |
| L4 (AI Active) | Optimization Audit | Consulting |
| L5 (AI Leader) | Partnership Discussion | Enterprise |

## GDPR Compliance

- Explicit consent checkbox before submission
- Clear privacy policy link
- Data minimization (only collect necessary fields)
- Right to erasure supported
- Data stored in EU (Hetzner Germany)
- No third-party tracking without consent
- Results can be delivered without account creation

## Metrics to Track

| Metric | Target | Purpose |
|--------|--------|---------|
| Landing page conversion | 15-25% | Traffic quality |
| Assessment completion rate | 70%+ | Question quality |
| Email opt-in rate | 80%+ | Value proposition |
| Consultation requests | 5-10% | Lead quality |
| Email open rate | 40%+ | Subject line quality |
| Consultation show rate | 80%+ | Follow-up quality |

## Quick Start

1. Review questionnaire.md for question content
2. Review scoring.md for calculation logic
3. Set up form (Typeform/Tally or custom)
4. Configure email sequences
5. Create landing page
6. Launch and measure

---

**Part of Verduona Lead Generation System**

Contact: matej@verduona.com
