# Mac Computer Use Cookbook: Trader8

**App:** trader8  
**Description:** Trading research + strategy evolution dashboard  
**Created:** 2025-12-22  
**Linear:** VD-168

---

## Purpose

Provide step-by-step visual and manual checks for Trader8 on macOS using Computer Use. Focus on verifying the local dashboard UI and core workflow screens (dashboard, strategies, backtests).

---

## Access

### Local Dev (Recommended)

| Component | URL | Notes |
|----------|-----|------|
| Web dashboard | http://127.0.0.1:8900 | Trader8 UI |

### Repo Location

- `/home/adminmatej/github/applications/prototypes/trader8`

---

## Credentials

- No test accounts found in `/home/adminmatej/github/secrets/test-accounts/`.
- If login is required, request a test account from the owner.

---

## Visual Checks

### 1. Dashboard Loads

1. Open http://127.0.0.1:8900
2. Verify the dashboard renders without a blank screen.

Checklist:
- [ ] Page loads in under 5 seconds
- [ ] Header or app title references Trader8/Trader9
- [ ] No obvious layout breaks

### 2. Strategy List

1. Navigate to the Strategies view (if available).
2. Verify strategy cards or a table is visible.

Checklist:
- [ ] Strategy list/table renders
- [ ] Strategy name or ID is visible
- [ ] Selecting a strategy shows details

### 3. Backtest Interface

1. Open the Backtest view.
2. Verify the backtest controls and results area exist.

Checklist:
- [ ] Backtest form controls visible
- [ ] Results panel or chart placeholder appears
- [ ] No blocking errors in the UI

---

## API Checks (Quick Manual)

If a health endpoint is available, validate it in the browser or terminal. If not, skip this section.

---

## Payment Flow

- Not applicable. Trader8 has no payment flow in local dev.

---

## OAuth/Identity Setup

- No OAuth flow documented for local testing.
- If login is required, capture the error state and request credentials.

---

## Expected States (Screenshots)

Capture screenshots of:

1. Dashboard landing view.
2. Strategies list/table view.
3. Backtest interface view.

---

## Troubleshooting

### Dashboard not loading

- Ensure the web server is running:
  - `cd /home/adminmatej/github/applications/prototypes/trader8`
  - `uv run python -m src.web.app`
- Confirm port 8900 is listening on 127.0.0.1.

---

## Quick Start (For Tester)

```bash
cd /home/adminmatej/github/applications/prototypes/trader8
uv sync
source .venv/bin/activate
uv run python -m src.web.app
```

---

*Cookbook Version: 1.0*
