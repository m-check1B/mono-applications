# Voice AI Call-Center Architecture – Direction for Coding Architect  
*(Prepared for Matej – Nov 2025)*

---

## 1. Executive Summary

We **will not build on Vapi as a core dependency**.

Instead we will:

- Use **Twilio** directly for telephony (PSTN / SIP).
- Use **Google Gemini Live API** with **Gemini 2.5 Flash** (and optionally Pro) for real-time voice + tools.
- Build our **own orchestration layer** (our “mini-Vapi”) that:
  - Manages calls, tools, multi-tenant config, and analytics.
  - Can later support other providers (OpenAI Realtime, Anthropic, local models) behind a clean abstraction.

**Vapi will be used only as “know-how inspiration”:** we may prototype or study ideas, but **clients never log into Vapi** and the production product does not depend on it.

---

## 2. Key Decisions

### 2.1 Vendor strategy

- **Primary stack (production)**  
  - Telephony: **Twilio** (numbers, inbound, outbound, SIP).
  - Realtime model: **Gemini Live + Gemini 2.5 Flash** (for price + latency + IQ balance).
  - Orchestration: **Our own backend** (Hetzner / chosen infra).

- **Secondary / future stack (optional)**  
  - Add **OpenAI Realtime** / other models via the same abstraction later.
  - Optionally support **local models** for offline / special customers.

### 2.2 Role of Vapi

- **Not** a platform we put clients on.
- **Not** a core dependency for routing or call control.
- At most:
  - Internal sandbox for quick experiments.
  - Reference for:
    - How they structure “assistants”.
    - How they do live call control & monitoring.
    - What a commercial featureset looks like (for us to match or surpass).

**Rule:**  
> Clients interact only with *our* app and *our* dashboards.  
> Any external provider is purely an internal implementation detail.

---

## 3. Target High-Level Architecture

### 3.1 Core components

1. **Telephony Layer (Twilio)**
   - Phone numbers, SIP trunks, caller ID, recording (if needed).
   - Webhook into our backend for:
     - Inbound call initiation.
     - Media / WebRTC events (depending on integration mode).

2. **Call Orchestrator Service**
   - One “session actor” per call (e.g. WebSocket handler / worker).
   - Responsibilities:
     - Open/close **Gemini Live sessions**.
     - Stream audio between Twilio and Gemini Live.
     - Maintain per-call state (context, tools, tenant config, routing).
     - Trigger tools / webhooks (CRM, n8n, internal APIs).
     - Handle timeouts, retries, termination, and handoff to humans.

3. **LLM Layer**
   - Primary: **Gemini 2.5 Flash** via Live API.
   - Optional: switch to **Gemini Pro** or other models for:
     - Difficult reasoning segments.
     - Final summaries and QA.
   - Encapsulated in an internal interface so we can swap providers.

4. **Multi-Tenant Config & Storage**
   - **Postgres** (or equivalent) with clear separation by `tenant_id`.
   - Stores:
     - Tenant metadata (name, domain, billing).
     - Keys / credentials (encrypted): Gemini, Twilio, others (BYOK per tenant possible).
     - Assistant definitions (per tenant).
     - Routing rules (IVR trees, queues, escalation logic).
     - User accounts, roles, permissions (Owner, Supervisor, Agent, etc.).

5. **Logging & Analytics**
   - Call events: start, end, duration, dropped, transfer, etc.
   - Transcripts (per turn, with timestamps + speaker labels).
   - Tool calls (which tools used, parameters, latency).
   - Stored in DB or analytical store (Postgres / ClickHouse).
   - Periodic batch jobs using offline LLM calls (Gemini Pro) to generate:
     - QA summaries.
     - Intent classification.
     - Lead scores.
     - Outcome tags (sale, callback, wrong number, etc.).

6. **Frontend / Admin UI**
   - Multi-tenant SaaS UI:
     - Tenant onboarding.
     - Phone number and routing management.
     - Assistant & prompt configuration.
     - Real-time call monitoring (optional).
     - Reports and dashboards (AHT, call volume, conversion, etc.).
   - This is the **only** interface clients ever see.

---

## 4. Abstractions & Interfaces

### 4.1 Voice Provider abstraction

Internally define an abstraction like:

```ts
interface VoiceProvider {
  startCall(params: StartCallParams): Promise<CallHandle>;
  endCall(callId: string): Promise<void>;
  sendEvent(callId: string, event: VoiceControlEvent): Promise<void>;
}
```

Initial implementations:

- `TwilioVoiceProvider` (direct integration).
- Optional future: `VapiVoiceProvider` (for internal experiments only, not exposed to clients).

This keeps us provider-agnostic and allows us to swap or mix sources later.

### 4.2 Model / Realtime abstraction

Abstract the model side:

```ts
interface RealtimeModel {
  startSession(config: SessionConfig): Promise<SessionHandle>;
  sendAudio(sessionId: string, chunk: Buffer): Promise<void>;
  sendText(sessionId: string, text: string): Promise<void>;
  onEvent(sessionId: string, handler: (event: ModelEvent) => void): void;
  stopSession(sessionId: string): Promise<void>;
}
```

Implementations:

- `GeminiLive2_5FlashModel`
- Optional later:
  - `GeminiLiveProModel`
  - `OpenAIRealtimeModel`
  - `LocalRealtimeModel`

### 4.3 Assistant definition structure

Per tenant, assistants stored in DB, e.g.:

```json
{
  "tenant_id": "tenant_123",
  "assistant_id": "inbound_support_cz",
  "name": "CZ Support Line",
  "system_prompt": "You are a polite Czech-speaking phone agent for ...",
  "language": "cs-CZ",
  "model_config": {
    "realtime_model": "gemini-2.5-flash-live",
    "latency_profile": "fast",
    "temperature": 0.4
  },
  "voice_config": {
    "voice_id": "cs-CZ-Standard-A",
    "barge_in": true
  },
  "tools": [
    { "type": "http", "name": "crm_lookup", "endpoint": "https://..." },
    { "type": "http", "name": "create_ticket", "endpoint": "https://..." }
  ],
  "routing_rules": {
    "on_opening_question": "...",
    "escalation_keywords": ["stížnost", "právník", "inspekce"],
    "transfer_to_queue": "human_support_cz"
  }
}
```

This fills the same role as “Vapi assistants” but under our full control.

---

## 5. Multi-Tenant Design Notes

- **Tenant isolation**
  - Every call, assistant, user, and log row must carry `tenant_id`.
  - Access control in API layer ensures tenants never see each others’ data.
- **Per-tenant keys**
  - Support both:
    - Our **shared master keys** (for small clients).
    - Optional BYOK (**Bring Your Own Key**) per tenant.
  - Keys stored encrypted (KMS / Vault / equivalent).
- **Per-tenant routing**
  - Each tenant can:
    - Attach one or more Twilio numbers.
    - Map numbers → routing profiles → assistants / queues.
    - Define business hours vs. off-hours behaviour.

---

## 6. Why Not Vapi (Explicit Rationale)

1. **Client ownership**
   - If clients log into Vapi, they can bypass us and become Vapi’s direct customers.
   - Our product value shrinks to “setup + consulting”.

2. **Cost structure**
   - Vapi adds its own per-minute margin on top of:
     - Telephony
     - STT/TTS
     - LLM tokens  
   - We want direct control of **TCO per minute**.

3. **Latency & control**
   - Removing Vapi reduces network hops and opaque processing.
   - We want fine-grained control over buffering, barge-in, and session logic.

4. **Compliance & data control**
   - We want control over:
     - Data residency (e.g., EU).
     - Retention periods.
     - Redaction / anonymization.
   - Vapi adds another data processor we don’t fully control.

5. **Product differentiation**
   - We aim to build a **call-center platform**, not just a wrapper on a voice middleware.
   - Owning routing, analytics, and UI is strategic.

---

## 7. Where Vapi Still Has Limited Use (Internal Only)

If we choose to touch Vapi at all, we define a **strict scope**:

1. **Prototype Lab**
   - For quick experiments when we want to test concept X in hours.
   - Used only by internal team.
   - Any working flows are later **rewritten** on our own stack.

2. **Reference / Inspiration**
   - Study:
     - Their assistant concept.
     - Their live call control API.
     - Their logging/analytics UX.
   - Use as “competitive benchmark” for features.

3. **Plug-in Provider (behind abstraction)**
   - If needed, implement `VapiVoiceProvider` as an internal adapter.
   - Still invisible to clients; used only for special cases or experiments.

---

## 8. Immediate TODOs for Coding Architect

1. **Define minimal service boundaries**
   - `call-orchestrator-service`
   - `realtime-model-adapter`
   - `telephony-adapter` (Twilio)
   - `config-service` (tenants, assistants, routes)
   - `logging-service` (or shared module)

2. **Draft data model**
   - Tables (or collections) for:
     - `tenants`
     - `users`
     - `phone_numbers`
     - `assistants`
     - `call_sessions`
     - `call_events`
     - `transcripts`
     - `tools` / `tool_logs`
     - `api_keys` (encrypted)

3. **Define the internal APIs**
   - gRPC/REST/WebSocket contracts between:
     - Telephony adapter ↔ Call orchestrator.
     - Call orchestrator ↔ Realtime model layer.
     - Call orchestrator ↔ Tools / CRM / n8n.
   - Auth & tenant scoping.

4. **PoC Milestones**
   - v0: One hard-coded tenant, single number, Gemini Live 2.5 Flash, single assistant.
   - v1: Multi-tenant, DB-backed assistants and routing, basic dashboard.
   - v2: Analytics, QA summaries, human handoff, and queueing.

---

## 9. One-Sentence Summary for Architect

We will treat **Vapi only as a reference**, and instead build our own **Twilio + Gemini Live–based, multi-tenant voice call-center platform**, with all value (routing, assistants, analytics, UI, and client relationships) owned entirely by **our** stack.
