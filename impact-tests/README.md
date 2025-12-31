# Impact Tests – AI Readiness Web App

Stack-2026 style **full app** that implements:

- **Business AI Readiness Test** (for companies)
- **Human AI Readiness Test** (for individuals/students)

Results are scored into readiness buckets and stored as CSV files under
`backend/data/` for later outreach and analysis.

## Structure (Stack-2026 Layout)

- `backend/` – Python + FastAPI API
  - `backend/app/main.py` – FastAPI application with:
    - HTML routes for quick manual use:
      - `GET /` – index
      - `GET/POST /business` – Business AI Readiness Test
      - `GET/POST /human` – Human AI Readiness Test
    - JSON API routes for the frontend:
      - `POST /api/business` – Business test (JSON)
      - `POST /api/human` – Human test (JSON)
  - `backend/templates/` – Minimal HTML templates for tests and result pages
  - `backend/data/` – CSV logs of submissions (`business_results.csv`, `human_results.csv`)
  - `backend/requirements.txt` – Python dependencies

- `frontend/` – SvelteKit 2 + Tailwind UI
  - `src/routes/+page.svelte` – Landing page with links to tests
  - `src/routes/business/+page.svelte` – Business test form + result view
  - `src/routes/human/+page.svelte` – Human test form + result view
  - `src/lib/api.ts` – API client calling `/api/business` and `/api/human`
  - Vite dev server proxies `/api` → FastAPI backend (see `vite.config.ts`)

## Alignment with Stack-2026 and Other Apps

- Uses the **primary Stack-2026 stack**: Python + FastAPI backend, SvelteKit 2 + Tailwind frontend.
- Follows the same layout and patterns as `recall-kraliki`, `focus-kraliki` and other 2026 apps:
  - `backend/` and `frontend/` directories
  - JSON API under `/api/*` consumed by the SvelteKit client
- This makes deployment, monitoring and scaling consistent with the rest of the Ocelot apps.

## Running locally

### Backend (FastAPI)

From the `impact-tests/backend` directory:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 3035
```

### Frontend (SvelteKit)

From the `impact-tests/frontend` directory:

```bash
pnpm install
pnpm dev
```

This starts SvelteKit on `http://127.0.0.1:5177` with `/api` requests proxied to the
backend on `http://127.0.0.1:3035`.

Open `http://127.0.0.1:5177` to use the full app.
