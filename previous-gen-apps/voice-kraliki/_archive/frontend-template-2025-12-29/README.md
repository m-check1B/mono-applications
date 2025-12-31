# Operator Console – SvelteKit (Stack 2026)

This package is a fresh SvelteKit 5 implementation of the operator console, following the Stack 2026 “machine-cold” guidelines. It replaces the minimal demo with a project structure that mirrors the original Next.js frontend — ready to plug into the FastAPI backend.

## What’s in place today

- **Stack 2026 baseline**
  - Tailwind configured with the machine-cold palette, 4 px spacing system, touch-friendly tokens, and ergonomic button/card/input classes.
  - Global theme + auth stores (`$lib/stores`) with token refresh scaffolding, query client bootstrap, and runtime configuration sourced from environment variables.
  - Layout shell with desktop header, mobile bottom navigation, theme toggle, and TanStack Query provider.

- **Ported UI surfaces**
  - `/dashboard`: overview tiles, navigation CTAs, and migration checklist.
  - `/auth/login`, `/auth/register`: credential-based sign-in/sign-up backed by the new auth services with redirect guards protecting app routes.
  - `/calls/outbound`: full operator console structure—call configuration panel, campaign instructions, company list execution flow, realtime Gemini session card, local audio tester, and status monitor. Network calls use the new `services/calls` API layer, and status polling hooks are preserved.
  - `/calls/incoming`: realtime listener wiring via `incomingSession` (connect/accept/decline, auto-accept, browser playback) plus provider health polling.
  - `/campaigns`, `/companies`, `/settings`: library, lead list, and environment override placeholders that match the Next.js information hierarchy.

- **Service layer parity**
  - `services/calls.ts` replicates the legacy endpoints (`/available-voices`, `/make-call`, `/call-results/:sid`, etc.) so the Svelte UI can call into the same backend contract.
  - `services/realtime.ts`, `services/audioSession.ts`, `services/audioManager.ts`, and `services/incomingSession.ts` provide reusable WebSocket/token plumbing, browser audio lifecycle helpers, and inbound session orchestration shared by both consoles.
  - TanStack Query now hydrates call configuration (voices/models/voice config) with caching/resume semantics instead of bespoke `fetch` calls.

- **Developer experience**
  - `npm run dev` (Vite), `npm run check` (svelte-check), and `npm run build` all succeed.
  - README now documents the project instead of the CLI stub.

## Parity gaps & next tasks

These items are not yet implemented and are required for full parity with the archived Next.js app:

1. **Authentication polish**
   - Confirm FastAPI endpoint parity (`/auth/login`, `/auth/register`, `/auth/logout`, `/auth/refresh`) and align response schema with the new SvelteKit client.
   - Add password reset, token-from-query support, and surfaced error messaging consistent with the legacy UX.

2. **Realtime + audio**
   - Finish the worklet/pipeline parity: add silence gating, volume meters, and hook Gemini turn lifecycle into UI to match legacy tester behaviour.
   - Align inbound offer handling with backend events (`accept-call`, `decline-call`, session cleanup) and validate provider health endpoints (`/api/provider-health`, `/api/connection-metrics`).

3. **Data hydration**
   - Migrate the remaining placeholder fetches (campaign/company lists, provider metrics) onto TanStack Query and connect them to real backend endpoints.
   - Populate `campaigns`/`companies` routes from the API instead of static placeholders.

4. **Error handling & toasts**
   - Reintroduce toast/notification system used in Next.js (e.g., react-hot-toast) with a Svelte equivalent.

5. **UI fidelity**
   - Convert remaining plain inputs into reusable Svelte components (button, card, input) once slot patterns for Svelte 5 runes are stabilised.
   - Add responsive tweaks (sticky bottom sheet, mobile FAB) noted in Stack 2026 docs.

6. **Testing**
   - Add component/unit tests (Vitest) and high-level Playwright smoke tests to mirror the critical flows (launch call, poll summary, stop call, etc.).

## Local development

```bash
npm install
npm run dev            # start Vite dev server
npm run check          # svelte-check (type & lint)
npm run build          # production build
npm run preview        # preview the production output
```

Environment variables follow SvelteKit’s `$env/dynamic/public` convention. Populate `.env` or export:

```
PUBLIC_BACKEND_URL=https://gemini-api.example.com
PUBLIC_WS_URL=wss://gemini-api.example.com/ws
PUBLIC_TELNYX_FROM_NUMBER=+420228810376
PUBLIC_TELNYX_FROM_NUMBER_US=+18455954168
PUBLIC_TELNYX_FROM_NUMBER_CZ=+420228810376
PUBLIC_TELNYX_FROM_NUMBER_ES=+34123456789
PUBLIC_TWILIO_FROM_NUMBER=+420228810376
PUBLIC_TWILIO_FROM_NUMBER_US=+18455954168
PUBLIC_TWILIO_FROM_NUMBER_ES=+34123456789
```

## Repo structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── config/        # env + config utilities
│   │   ├── hooks/         # shared Svelte hooks (theme/auth)
│   │   ├── services/      # API clients (calls.ts, ...)
│   │   └── stores/        # global stores (auth, theme, TanStack query)
│   └── routes/
│       ├── (protected)/    # Authenticated app shell (dashboard, calls, campaigns, ...)
│       └── auth/           # Public auth flows (login/register)
├── tailwind.config.ts
├── tsconfig.json
└── README.md              # this file
```

## Next steps

Refer to the “Parity gaps” list above. Once authentication and realtime wiring are complete, the SvelteKit frontend will be feature-equal with the archived Next.js UI and ready for full integration testing against the FastAPI backend.

### Realtime verification (current state)

1. Ensure the FastAPI backend exposes the Gemini session WebSocket at `/test-outbound` (or adjust via `createGeminiSession`).
2. Sign in via `/auth/login`, navigate to `/calls/outbound`, and use the **Realtime Session** card to connect; the status should progress `idle → connecting → connected` and log the latest payload timestamp.
3. Disconnect from the card to confirm the state transitions to `disconnected` without errors.
4. Visit `/calls/incoming`, enable listening, and confirm call offers appear in the **Provider Connection** card (use mock inbound WebSocket events). Accepting auto-starts the microphone via the audio manager; declining clears the active call.
5. Provider health card currently consumes `/api/provider-health`; adjust the endpoint or data mapping once the FastAPI implementation lands.
6. Full audio capture/playback parity (silence gating, volume meters) and deeper provider metrics remain TODO as outlined in the parity gaps above.
