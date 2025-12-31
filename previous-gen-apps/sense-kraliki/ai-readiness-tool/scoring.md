# AI Readiness Scoring Methodology

## Scoring Overview

The assessment produces a composite **AI Readiness Score (0-100)** based on weighted category scores.

## Category Weights

| Category | Weight | Max Raw | Max Weighted |
|----------|--------|---------|--------------|
| Data Infrastructure | 25% | 25 | 25 |
| Team AI Literacy | 20% | 25 | 20 |
| Process Automation | 20% | 25 | 20 |
| Budget & Investment | 15% | 25 | 15 |
| Strategic Alignment | 20% | 25 | 20 |
| **TOTAL** | **100%** | 125 | **100** |

## Calculation Formula

```python
def calculate_readiness_score(answers):
    # Calculate raw category scores (sum of 1-5 answers)
    data_raw = sum(answers['data'])           # Max 25
    literacy_raw = sum(answers['literacy'])   # Max 25
    process_raw = sum(answers['process'])     # Max 25
    budget_raw = sum(answers['budget'])       # Max 25
    strategy_raw = sum(answers['strategy'])   # Max 25

    # Normalize each category to 0-100 scale
    data_norm = (data_raw / 25) * 100
    literacy_norm = (literacy_raw / 25) * 100
    process_norm = (process_raw / 25) * 100
    budget_norm = (budget_raw / 25) * 100
    strategy_norm = (strategy_raw / 25) * 100

    # Apply weights
    weighted_score = (
        data_norm * 0.25 +
        literacy_norm * 0.20 +
        process_norm * 0.20 +
        budget_norm * 0.15 +
        strategy_norm * 0.20
    )

    return {
        'total_score': round(weighted_score),
        'maturity_level': get_maturity_level(weighted_score),
        'category_scores': {
            'data': round(data_norm),
            'literacy': round(literacy_norm),
            'process': round(process_norm),
            'budget': round(budget_norm),
            'strategy': round(strategy_norm)
        }
    }

def get_maturity_level(score):
    if score <= 20:
        return 'L1'  # AI Curious
    elif score <= 40:
        return 'L2'  # AI Aware
    elif score <= 60:
        return 'L3'  # AI Ready
    elif score <= 80:
        return 'L4'  # AI Active
    else:
        return 'L5'  # AI Leader
```

## Maturity Levels Defined

### L1: AI Curious (0-20)
**Characteristics:**
- Limited digital infrastructure
- Low awareness of AI capabilities
- Manual processes predominate
- No dedicated AI budget
- No clear AI strategy

**Typical Profile:**
- Small business, < 20 employees
- Paper-based or basic spreadsheet operations
- IT = email and basic tools
- "We've heard about AI but don't know where to start"

### L2: AI Aware (21-40)
**Characteristics:**
- Some digital systems in place
- General AI awareness from media
- Interested but cautious
- Could find budget if justified
- Exploring possibilities

**Typical Profile:**
- Growing SME, 20-100 employees
- Using cloud tools (Google Workspace, etc.)
- Some employees experimenting with ChatGPT
- "We want to use AI but need guidance"

### L3: AI Ready (41-60)
**Characteristics:**
- Solid data foundation
- Team has AI literacy
- Processes documented
- Budget available for pilots
- Use cases identified

**Typical Profile:**
- Established SME, 50-200 employees
- CRM, ERP, or other business systems
- Data-driven decision making emerging
- "We're ready to pilot AI projects"

### L4: AI Active (61-80)
**Characteristics:**
- Strong data infrastructure
- AI skills in-house or contracted
- Some AI tools in production
- Dedicated AI investment
- Clear AI roadmap

**Typical Profile:**
- Mid-market company, 100-500 employees
- Running AI-powered tools (chatbots, analytics)
- Facing scaling challenges
- "We need help optimizing our AI efforts"

### L5: AI Leader (81-100)
**Characteristics:**
- Mature data platform
- Strong AI/ML team
- AI embedded in operations
- Significant AI investment
- AI driving competitive advantage

**Typical Profile:**
- Enterprise or tech-forward company
- Multiple AI systems in production
- Measuring AI ROI
- "We want strategic partnership for innovation"

## Category Interpretation

### Data Infrastructure (25%)

| Score | Interpretation |
|-------|----------------|
| 0-40 | Major data gaps. Focus on basics first. |
| 41-60 | Foundation present but fragmented. Integration needed. |
| 61-80 | Solid foundation. Ready for AI data requirements. |
| 81-100 | Excellent. Data is an asset ready for AI. |

### Team AI Literacy (20%)

| Score | Interpretation |
|-------|----------------|
| 0-40 | Training needed before AI adoption. |
| 41-60 | Basic awareness. More exposure helpful. |
| 61-80 | Good foundation. Can support AI projects. |
| 81-100 | Strong expertise. Can lead AI initiatives. |

### Process Automation (20%)

| Score | Interpretation |
|-------|----------------|
| 0-40 | Many manual processes. High automation potential. |
| 41-60 | Some automation. Good AI use cases likely. |
| 61-80 | Good automation. AI can add intelligence. |
| 81-100 | Highly automated. AI for optimization/prediction. |

### Budget & Investment (15%)

| Score | Interpretation |
|-------|----------------|
| 0-40 | Limited resources. Start with low-cost/no-code AI. |
| 41-60 | Some flexibility. Pilot projects feasible. |
| 61-80 | Good investment capacity. Multiple projects possible. |
| 81-100 | Strong commitment. Strategic AI program possible. |

### Strategic Alignment (20%)

| Score | Interpretation |
|-------|----------------|
| 0-40 | No clear direction. Strategy workshop recommended. |
| 41-60 | Some clarity. Needs prioritization and buy-in. |
| 61-80 | Good alignment. Ready for implementation. |
| 81-100 | Excellent alignment. AI is strategic priority. |

## Lead Scoring (Internal)

Beyond AI readiness, we score lead quality for sales prioritization:

```python
def calculate_lead_score(answers, meta):
    score = 0

    # Company size (bigger = higher value)
    size_scores = {'1-10': 5, '11-50': 15, '51-200': 25, '201-500': 35, '500+': 50}
    score += size_scores.get(meta['company_size'], 0)

    # Role (senior = higher value)
    role_scores = {
        'C-Level / Executive': 30,
        'Director / VP': 25,
        'Manager': 15,
        'Team Lead': 10,
        'Individual Contributor': 5,
        'Consultant / Advisor': 20
    }
    score += role_scores.get(meta['role'], 0)

    # Budget capacity (from Q4.1)
    budget_question = answers['budget'][0]
    score += budget_question * 5  # 5-25 points

    # Urgency signal (short expected ROI timeline)
    roi_timeline = answers['budget'][3]
    if roi_timeline <= 2:  # Wants results in 6 months
        score += 15

    # Consultation request
    if meta.get('requested_consultation'):
        score += 25

    return {
        'lead_score': score,
        'priority': 'Hot' if score >= 100 else 'Warm' if score >= 60 else 'Nurture'
    }
```

## Benchmark Data (Illustrative)

*To be updated with real data once assessment is live*

| Industry | Avg Score | Common Gaps |
|----------|-----------|-------------|
| Technology | 62 | Strategy alignment |
| Financial Services | 58 | Data governance |
| Healthcare | 45 | Budget, compliance |
| Manufacturing | 41 | AI literacy |
| Retail | 48 | Data infrastructure |
| Professional Services | 55 | Process documentation |

## Special Scoring Rules

### Minimum Viability Check
If any category scores below 20, the overall assessment includes a warning:
> "Your [category] score is a critical blocker. Address this before pursuing AI initiatives."

### Quick Win Identification
Scores of 80+ in Process Automation + 60+ in Data indicate high automation ROI potential:
> "You have significant quick-win opportunities in process automation."

### Training Priority
Literacy score below 40 with other scores above 60:
> "Your team's AI literacy is your biggest gap. Consider AI Academy training."

## Output Format

```json
{
  "assessment_id": "uuid",
  "completed_at": "2025-01-15T10:30:00Z",
  "respondent": {
    "name": "Jane Smith",
    "email": "jane@company.com",
    "role": "Director",
    "company": "Acme Corp",
    "company_size": "51-200",
    "industry": "Professional Services"
  },
  "scores": {
    "total": 52,
    "maturity_level": "L3",
    "maturity_name": "AI Ready",
    "categories": {
      "data_infrastructure": 64,
      "team_ai_literacy": 44,
      "process_automation": 56,
      "budget_investment": 40,
      "strategic_alignment": 52
    }
  },
  "insights": {
    "top_strength": "Data Infrastructure",
    "biggest_gap": "Budget & Investment",
    "quick_wins": ["document_processing", "report_automation"],
    "blockers": []
  },
  "lead": {
    "score": 85,
    "priority": "Warm",
    "recommended_cta": "ai_strategy_workshop"
  }
}
```

## Visualization

### Radar Chart
Display 5-category scores as pentagon radar chart for intuitive understanding.

### Score Gauge
Show overall score as speedometer-style gauge with color zones.

### Industry Comparison
Bar chart comparing respondent to industry average.

---

*Scoring methodology v1.0 - January 2025*
