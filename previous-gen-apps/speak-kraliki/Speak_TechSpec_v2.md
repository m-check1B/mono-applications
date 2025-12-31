# Speak by Kraliki — Technical Specification v2.0

**AI Voice Employee Intelligence Platform**

Version 2.0 — November 2025 (Updated based on expert review)

> Integration with: Call Centrum + Plánovač

========================================
TEMPLATE-FIRST DELIVERY (2025-12-29)
Speak is delivered via Kraliki Swarm templates by default.
This spec remains a backend/reference blueprint; UI is in Swarm.
========================================

---

## Changelog v2.0

- ⚠️ Participation risk upgraded to HIGH (was MEDIUM)
- ✅ Added "Trust Layer" as core product feature
- ✅ Added "Action Loop" feature (moved from V2 to MVP)
- ✅ Added audio latency fallback ("filler" sounds)
- ✅ Added "continue in text" fallback for voice failures
- ✅ Shortened default session to 5-7 min (was 10-15)
- ✅ Added pilot focus on blue-collar/manufacturing
- ✅ Added works council / union considerations
- ✅ Added "What this is NOT" positioning

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Integration with Existing Products](#2-integration-with-existing-products)
3. [Database Schema](#3-database-schema)
4. [API Specification](#4-api-specification)
5. [Voice Pipeline](#5-voice-pipeline)
6. [AI Conversation Engine](#6-ai-conversation-engine)
7. [Trust Layer (NEW)](#7-trust-layer)
8. [Dashboard & Analytics](#8-dashboard--analytics)
9. [Security & Privacy](#9-security--privacy)
10. [Build Phases](#10-build-phases)
11. [What to Build NOW vs LATER](#11-what-to-build-now-vs-later)
12. [Risk Matrix (Updated)](#12-risk-matrix)

---

## 1. Architecture Overview

### 1.1 High-Level System Design

Speak by Kraliki se integruje do tvé existující platformy jako nový modul vedle Call Centra a Plánovače.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED PLATFORM CORE                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │    Auth     │ │   Users     │ │  Companies  │              │
│  │   (OAuth)   │ │  Employees  │ │   Billing   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │              
         ▼                    ▼                    ▼              
┌─────────────┐      ┌─────────────┐      ┌─────────────┐        
│   CALL      │      │  PLÁNOVAČ   │      │   VOICE     │        
│   CENTRUM   │      │   (Tasks)   │      │ OF PEOPLE   │        
│             │      │             │      │             │        
│  - Calls    │      │  - Tasks    │      │  - Surveys  │        
│  - Queue    │      │  - Projects │      │  - Voice AI │        
│  - Agents   │      │  - Calendar │      │  - Insights │        
└─────────────┘      └─────────────┘      └─────────────┘        
```

### 1.2 Speak by Kraliki Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEAK BY KRALIKI                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  INVITATION  │───▶│    VOICE     │───▶│   ANALYSIS   │     │
│  │   SERVICE    │    │   PIPELINE   │    │    ENGINE    │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│           │                  │                  │              │
│           ▼                  ▼                  ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │    TRUST     │    │   ACTION     │    │  DASHBOARD   │     │
│  │    LAYER     │    │    LOOP      │    │              │     │
│  │  (NEW v2.0)  │    │  (NEW v2.0)  │    │              │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Integration with Existing Products

### 2.1 Shared Components (Already Built)

| Component | Reuse in Speak by Kraliki |
|-----------|-------------------------|
| Auth System | Login pro adminy/HR. Employee auth = magic link (jednorázový). |
| User Management | Employees tabulka — rozšíříš o department, manager_id. |
| Company/Tenant | Multi-tenant struktura — každá firma vidí jen svá data. |
| Billing | Stripe/Fakturoid integrace — přidáš nový produkt. |
| Notifications | SMS/Email gateway — použiješ pro pozvánky. |
| Dashboard Shell | SvelteKit layout — přidáš novou sekci. |

### 2.2 New Components (Build for VoP)

| Component | Description |
|-----------|-------------|
| Voice Pipeline | WebSocket server pro real-time audio streaming. |
| AI Conversation | Gemini integration pro STT + konverzaci + TTS. |
| Survey Engine | Otázky, flow, scheduling, reminders. |
| Analysis Engine | Sentiment analysis, topic extraction, alerts. |
| **Trust Layer** | First-screen UX explaining anonymity, transcript review. |
| **Action Loop** | CEO marks issues as "Heard" / "In Progress", broadcast back. |
| VoP Dashboard | Specifické views pro HR/CEO. |

### 2.3 Cross-Product Synergies

**Call Center + VoP Package:**
- For call-center clients: combine Speak by Kraliki + Call Centre analytics
- "Culture + Performance Intelligence" bundle
- Premium pricing for combined insights

**Task/Planning Integration:**
- VoP alerts → auto-create action items in Plánovač
- "3 people mentioned workload issues" → Task: "Review team capacity"

---

## 3. Database Schema

### 3.1 Core Tables (Extend Existing)

#### employees (rozšíření)

```sql
ALTER TABLE employees ADD COLUMN IF NOT EXISTS
  department_id UUID REFERENCES departments(id),
  manager_id UUID REFERENCES employees(id),
  hire_date DATE,
  vop_opted_out BOOLEAN DEFAULT FALSE,
  vop_last_survey TIMESTAMP,
  vop_participation_rate DECIMAL(3,2);
```

#### departments (nová)

```sql
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  name VARCHAR(100) NOT NULL,
  parent_id UUID REFERENCES departments(id),
  manager_id UUID REFERENCES employees(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Speak by Kraliki Tables

#### vop_surveys

```sql
CREATE TABLE vop_surveys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  name VARCHAR(100) NOT NULL,
  status VARCHAR(20) DEFAULT 'draft',
  frequency VARCHAR(20) DEFAULT 'monthly',
  questions JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  starts_at TIMESTAMP,
  ends_at TIMESTAMP
);
```

#### vop_conversations

```sql
CREATE TABLE vop_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  survey_id UUID REFERENCES vop_surveys(id),
  employee_id UUID REFERENCES employees(id),
  status VARCHAR(20) DEFAULT 'pending',
  invited_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_seconds INTEGER,
  transcript JSONB,
  transcript_reviewed_by_employee BOOLEAN DEFAULT FALSE,  -- NEW v2.0
  audio_url VARCHAR(500),
  sentiment_score DECIMAL(3,2),
  topics JSONB,
  flags JSONB,
  anonymous_id VARCHAR(50),
  fallback_to_text BOOLEAN DEFAULT FALSE  -- NEW v2.0
);
```

#### vop_actions (NEW v2.0 - Action Loop)

```sql
CREATE TABLE vop_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  topic VARCHAR(200) NOT NULL,
  status VARCHAR(20) DEFAULT 'new',  -- new, heard, in_progress, resolved
  created_from_alert_id UUID REFERENCES vop_alerts(id),
  assigned_to UUID REFERENCES users(id),
  notes TEXT,
  visible_to_employees BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### vop_alerts

```sql
CREATE TABLE vop_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  conversation_id UUID REFERENCES vop_conversations(id),
  type VARCHAR(50),
  severity VARCHAR(20),
  department_id UUID REFERENCES departments(id),
  description TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  action_id UUID REFERENCES vop_actions(id),  -- NEW v2.0
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Specification

### 4.1 Survey Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vop/surveys` | List all surveys for company |
| POST | `/api/vop/surveys` | Create new survey |
| GET | `/api/vop/surveys/:id` | Get survey detail |
| PATCH | `/api/vop/surveys/:id` | Update survey |
| POST | `/api/vop/surveys/:id/launch` | Launch survey (send invites) |
| POST | `/api/vop/surveys/:id/pause` | Pause active survey |

### 4.2 Employee Voice Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v/:token` | Voice interface (magic link entry) |
| WS | `/ws/voice/:token` | WebSocket for voice streaming |
| POST | `/api/vop/voice/start` | Initialize conversation |
| POST | `/api/vop/voice/end` | End conversation, trigger analysis |
| POST | `/api/vop/voice/fallback-text` | Switch to text mode (NEW v2.0) |

### 4.3 Trust Layer (NEW v2.0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vop/employee/transcript/:id` | Employee views own transcript |
| POST | `/api/vop/employee/transcript/:id/redact` | Employee redacts parts |
| POST | `/api/vop/employee/consent` | Record explicit consent |
| DELETE | `/api/vop/employee/data` | Employee requests data deletion |

### 4.4 Action Loop (NEW v2.0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vop/actions` | List all actions |
| POST | `/api/vop/actions` | Create action from alert |
| PATCH | `/api/vop/actions/:id` | Update action status |
| GET | `/api/vop/actions/public` | Actions visible to employees |

### 4.5 Dashboard / Insights

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vop/insights/overview` | Company-wide metrics |
| GET | `/api/vop/insights/trends` | Sentiment over time |
| GET | `/api/vop/insights/departments` | Per-department breakdown |
| GET | `/api/vop/alerts` | Active alerts |
| GET | `/api/vop/quotes` | Anonymous quotes for display |

---

## 5. Voice Pipeline

### 5.1 Flow Diagram

```
EMPLOYEE BROWSER                    SERVER                         GEMINI
      │                               │                               │
      │  1. Click magic link          │                               │
      │─────────────────────────────▶│                               │
      │                               │                               │
      │  2. TRUST SCREEN (consent)    │                               │
      │◀─────────────────────────────│                               │
      │  [User accepts]               │                               │
      │                               │                               │
      │  3. Open WebSocket            │                               │
      │◀═══════════════════════════▶│                               │
      │                               │                               │
      │  4. AI greeting (TTS)         │                               │
      │◀─────────────────────────────│                               │
      │                               │                               │
      │  5. User speaks               │                               │
      │══════════════════════════════▶│  6. STT (Gemini)             │
      │                               │─────────────────────────────▶│
      │                               │                               │
      │                               │  [IF >1.5s delay]            │
      │  7. FILLER SOUND              │  "Hmm, rozumím..."           │
      │◀─────────────────────────────│                               │
      │                               │                               │
      │                               │◀─────────────────────────────│
      │  8. AI response (TTS)         │                               │
      │◀─────────────────────────────│                               │
      │                               │                               │
      │  [IF audio fails]             │                               │
      │  9. FALLBACK TO TEXT          │                               │
      │◀─────────────────────────────│                               │
      │                               │                               │
      │  [Repeat for each turn]       │                               │
      │                               │                               │
      │  10. End conversation         │                               │
      │─────────────────────────────▶│                               │
      │                               │                               │
      │  11. TRANSCRIPT REVIEW        │                               │
      │◀─────────────────────────────│                               │
      │  [Optional: redact parts]     │                               │
      │                               │                               │
      │  12. Thank you + Action Feed  │                               │
      │◀─────────────────────────────│                               │
```

### 5.2 Latency Fallback (NEW v2.0)

If Gemini response takes >1.5 seconds:

```javascript
const FILLER_SOUNDS = [
  "Hmm, rozumím...",
  "Momentík...",
  "Díky, přemýšlím...",
  "Jasně..."
];

// Play random filler while waiting for real response
if (responseTime > 1500) {
  playFiller(randomChoice(FILLER_SOUNDS));
}
```

### 5.3 Text Fallback (NEW v2.0)

If audio fails (mic permission denied, network issues, browser incompatibility):

```
┌─────────────────────────────────────┐
│  Zdá se, že máme problém se zvukem. │
│                                     │
│  Můžeme pokračovat textově?         │
│                                     │
│  [Pokračovat textem]  [Zkusit znovu]│
└─────────────────────────────────────┘
```

Text mode uses same AI conversation engine, just without voice.

### 5.4 Audio Configuration

| Parameter | Value |
|-----------|-------|
| Sample rate | 16000 Hz |
| Channels | Mono |
| Format | WebM/Opus → FLAC |
| Chunk size | 250ms |
| Silence detection | 1.5s pause = end of utterance |
| **Max conversation** | **7 minutes** (was 15, reduced v2.0) |
| Filler threshold | 1.5s delay triggers filler |

---

## 6. AI Conversation Engine

### 6.1 Gemini Configuration

```
Model: gemini-2.5-flash-preview (→ GA when available)
Temperature: 0.7
Max tokens: 300 per response (shorter = faster)
Language: Czech (cs)
```

### 6.2 System Prompt

```
SYSTEM PROMPT:

Jsi přátelský AI asistent pro měsíční check-in se zaměstnancem.
Cíl: zjistit jak se mu daří, co ho těší, co ho trápí.

PRAVIDLA:
- Mluv česky, přirozeně, přátelsky
- Odpovědi KRÁTKÉ (1-2 věty max) — rychlý dialog
- Ptej se follow-up jen na důležité věci
- Neopakuj otázky
- Nikdy neslibuj změny — jsi jen posluchač
- Celý rozhovor MAX 5-7 minut

STRUKTURA:
1. Krátký pozdrav (10 sec)
2. 4-5 core otázek (5 min)
3. Prostor pro cokoliv (1 min)
4. Poděkování (10 sec)

KONTEXT:
- Zaměstnanec: {employee_first_name}
- Firma: {company_name}
- Oddělení: {department_name}
```

### 6.3 Core Questions (Shortened v2.0)

| # | Question | Max follow-ups |
|---|----------|----------------|
| 1 | Jak se ti daří v práci tento měsíc? | 1 |
| 2 | Co tě nejvíc těší nebo motivuje? | 0-1 |
| 3 | Je něco, co tě frustruje? | 1-2 |
| 4 | Jak hodnotíš spolupráci s týmem? | 0-1 |
| 5 | Je ještě něco, co chceš říct? | 0 |

**Target duration: 5-7 minutes** (not 10-15)

---

## 7. Trust Layer (NEW v2.0)

### 7.1 First Screen (Before Conversation)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    🎙️ Speak by Kraliki                          │
│                                                                 │
│  Ahoj! Toto je tvůj měsíční prostor pro zpětnou vazbu.         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ✓  Rozhovor je 100% ANONYMNÍ                           │   │
│  │  ✓  Tvůj nadřízený NEUVIDÍ co jsi řekl/a               │   │
│  │  ✓  Vedení vidí pouze agregované trendy                 │   │
│  │  ✓  Po rozhovoru si můžeš přečíst a upravit přepis     │   │
│  │  ✓  Můžeš kdykoliv požádat o smazání svých dat         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Rozhovor trvá cca 5 minut.                                    │
│                                                                 │
│           [Rozumím, pojďme na to]                               │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  Nechci odpovídat: [Přeskočit tento měsíc]                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Post-Conversation Review

After conversation ends, employee can:
1. **Read transcript** — see exactly what was recorded
2. **Redact parts** — remove sensitive sections before analysis
3. **Delete all** — request full deletion (GDPR right)

```
┌─────────────────────────────────────────────────────────────────┐
│  Přepis tvého rozhovoru                                        │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  AI: Jak se ti daří v práci tento měsíc?                       │
│  Ty: Celkem dobře, ale mám trochu moc práce.                   │
│                                                                 │
│  AI: Co tě nejvíc těší?                                        │
│  Ty: Líbí se mi nový projekt s Janou.                          │
│      [Odstranit tuto část]                                     │
│                                                                 │
│  AI: Je něco, co tě frustruje?                                 │
│  Ty: Porady jsou moc dlouhé.                                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  [Potvrdit a odeslat]     [Smazat vše]                         │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 What This Is NOT (Sales Deck Slide)

```
❌ Toto NENÍ sledovací nástroj
❌ Toto NENÍ hodnocení výkonu
❌ Toto NENÍ HR surveillance
❌ Váš manažer NEUVIDÍ kdo co řekl

✅ Toto JE anonymní zpětná vazba
✅ Toto JE radar firemní kultury
✅ Toto JE hlas zaměstnanců k vedení
✅ Manažeři dostávají AGREGOVANÉ trendy
```

---

## 8. Dashboard & Analytics

### 8.1 Action Loop Widget (NEW v2.0)

On dashboard, show employees that leadership is listening:

```
┌─────────────────────────────────────────────────────────────────┐
│  📢 Co děláme s vaší zpětnou vazbou                            │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ✅ VYŘEŠENO: Zkrátili jsme porady na 30 min                   │
│  🔄 ŘEŠÍME: Přetížení v logistice                              │
│  👂 SLYŠÍME: Témata kolem komunikace                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why this matters:**
- Biggest churn reason for engagement tools = "Survey fatigue"
- Employees stop answering when they don't see action
- This closes the loop and BOOSTS participation

### 8.2 CEO/HR Dashboard Views

Same as v1.0:
- Overview (sentiment gauge, participation rate)
- Trends (line charts over time)
- Topics (word cloud)
- Alerts (flight_risk, burnout, etc.)
- Anonymous Quotes

**NEW: Actions tab**
- Create action from any alert
- Track status: New → Heard → In Progress → Resolved
- Toggle visibility to employees

### 8.3 Alert Triggers

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| flight_risk | "odejít", "hledám práci" | HIGH |
| burnout | "vyhoření", "nestíhám" | HIGH |
| toxic_manager | Negative + manager mention | HIGH |
| team_conflict | Multiple people, same issue | MEDIUM |
| low_engagement | Low sentiment 3+ months | MEDIUM |
| sentiment_drop | Dept drops >20% MoM | MEDIUM |

---

## 9. Security & Privacy

### 9.1 GDPR Compliance

- DPA template ready
- Explicit consent before first conversation
- Right to delete: Employee can request deletion
- **Right to review: Employee sees transcript before submission (NEW)**
- Data minimization

### 9.2 Works Council / Union Considerations (NEW v2.0)

For companies with works councils (especially PL/DE-owned):

**Prepare:**
- DPIA (Data Protection Impact Assessment) template
- "No individual monitoring" statement
- Voice ≠ biometric identification (we only transcribe, not identify)
- Option for text-only mode (no voice at all)
- Configurable data retention (12 vs 24 months)

**Positioning for legal/compliance:**
- "This is employee feedback tool, not monitoring"
- "Same as anonymous suggestion box, just digital"
- "No manager sees individual responses"

### 9.3 Access Control

| Role | Access |
|------|--------|
| CEO/Owner | Full access |
| HR Director | Full access |
| Manager | Department only (aggregated) |
| Employee | Own data only + Action Feed |

---

## 10. Build Phases

### 10.1 Phase 0: NOW (Before Gemini GA) — 3 weeks

| Task | Days |
|------|------|
| Database schema + migrations | 2 |
| API skeleton | 2 |
| Trust Layer UI | 2 |
| Dashboard shell | 3 |
| Action Loop backend | 2 |
| Conversation prompts (test in playground) | 2 |
| Legal docs (DPA, DPIA, Terms) | 2 |
| Marketing content | 2 |
| **Manual pilot prep (Figma + scripted demos)** | 3 |

**NEW: Pre-sell with manual demos**
- Create clickable Figma prototype
- Run "interviews" manually with GPT/Whisper behind scenes
- Get 3-5 CEOs to sign letter of intent

### 10.2 Phase 1: MVP (After Gemini GA) — 4 weeks

| Task | Days |
|------|------|
| Gemini STT + conversation | 3 |
| TTS integration | 2 |
| Filler sounds + latency handling | 1 |
| Text fallback mode | 2 |
| WebSocket pipeline | 3 |
| Voice UI | 2 |
| Transcript review (employee side) | 2 |
| Sentiment analysis | 2 |
| Testing | 3 |

### 10.3 Phase 2: Alpha Pilots — 4 weeks

**Pilot selection (NEW v2.0):**
- 3-5 companies, 20-100 employees each
- **At least 1 blue-collar/manufacturing** (they prefer voice)
- At least 1 tech/services (typical target)
- Mix of Czech + Slovak

| Task | Time |
|------|------|
| Onboard pilots | 1 week |
| Gather feedback | ongoing |
| Iterate UX | 2 weeks |
| Add alert system | 3 days |
| Add topic extraction | 2 days |

### 10.4 Phase 3: Beta — Paying Customers

- Billing integration
- Self-serve onboarding
- Case studies
- Sales outreach

---

## 11. What to Build NOW vs LATER

### 11.1 BUILD NOW (Before Gemini GA)

| Component | Priority |
|-----------|----------|
| Database schema | ⭐⭐⭐ |
| Trust Layer UI | ⭐⭐⭐ |
| Action Loop backend | ⭐⭐⭐ |
| API skeleton | ⭐⭐⭐ |
| Dashboard shell | ⭐⭐ |
| Legal docs | ⭐⭐ |
| **Figma prototype for pre-sales** | ⭐⭐⭐ |
| Conversation prompts | ⭐⭐ |

### 11.2 BUILD AFTER GEMINI GA

| Component | Priority |
|-----------|----------|
| Gemini STT | ⭐⭐⭐ |
| TTS + filler sounds | ⭐⭐⭐ |
| Text fallback | ⭐⭐⭐ |
| WebSocket pipeline | ⭐⭐⭐ |
| Voice UI | ⭐⭐⭐ |
| Sentiment analysis | ⭐⭐ |

### 11.3 BUILD LATER (V2+)

| Feature | When |
|---------|------|
| Trend predictions | After 3+ months data |
| Flight risk ML | After correlation data |
| HRIS integration | When demanded |
| Multi-language (EN, PL) | After CZ proven |
| Plánovač integration (auto-tasks) | After 20 customers |

---

## 12. Risk Matrix (Updated v2.0)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Employees don't participate** | **HIGH** | HIGH | Trust Layer, short sessions, Action Loop visibility |
| Gemini Czech quality poor | LOW | HIGH | Fallback: Whisper + GPT-4 |
| Middle managers block adoption | MEDIUM | MEDIUM | Position as "culture radar", aggregate only |
| GDPR/works council issues | MEDIUM | MEDIUM | Legal pack ready, text-only option |
| Voice UX fragile (mobile) | MEDIUM | MEDIUM | Text fallback, extensive testing |
| Companies don't buy | MEDIUM | HIGH | Free pilots, strong ROI story |
| Competition copies | LOW | LOW | First mover, data moat, Czech focus |

---

## Immediate Action Items

### This Week
1. Create DB schema (run migrations)
2. Build Trust Layer first screen (critical for adoption)
3. Write conversation prompts, test in Gemini playground

### Next Week
1. API endpoints skeleton
2. Action Loop backend
3. Figma clickable prototype for pre-sales

### Ongoing
- Monitor Gemini 2.5 Flash status
- **Pre-sell: Get 3-5 LOIs from pilot companies**
- Identify 1 blue-collar company for pilot
- Prepare DPA + DPIA templates

---

*— End of Tech Spec v2.0 —*
