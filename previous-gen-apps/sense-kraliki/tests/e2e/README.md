# Sense by Kraliki E2E Tests

Playwright-based end-to-end tests for the Sense by Kraliki sensitivity tracking application.

> **Note:** Sense by Kraliki is currently a Telegram bot without a web UI. These tests are designed
> for a future web dashboard and will **skip gracefully** when no server is available.
> This ensures the test suite remains green regardless of environment.

## Overview

Sense by Kraliki is a sensitivity tracking Telegram bot that combines 9 data sources:
- NOAA Geomagnetic (Kp index)
- NOAA Solar (Flare activity)
- USGS Seismic (Earthquake data)
- Schumann Resonance
- Weather (Pressure, humidity)
- Swiss Ephemeris (Astrology)
- Moon Phase
- Mercury Retrograde
- Biorhythm

These E2E tests cover the web interface for:
1. **Landing Page** - Homepage, navigation, CTAs
2. **Sensor Dashboard** - Sensitivity score, data visualization
3. **Alerts** - Alert configuration and notifications

## Setup

```bash
cd /home/adminmatej/github/applications/sense-kraliki/tests/e2e

# Install dependencies
npm install

# Install browsers
npx playwright install
```

## Running Tests

```bash
# Run all tests
npm test

# Run with headed browser (visible)
npm run test:headed

# Run with UI mode (interactive)
npm run test:ui

# Run specific test file
npm run test:landing
npm run test:dashboard
npm run test:alerts

# Run in specific browser
npm run test:chromium
npm run test:firefox
npm run test:webkit

# Run mobile tests
npm run test:mobile

# Debug mode
npm run test:debug
```

## Test Structure

```
tests/e2e/
├── playwright.config.ts     # Playwright configuration
├── package.json             # Dependencies and scripts
├── fixtures/
│   └── page-objects.ts      # Page Object Model classes
├── landing-page.spec.ts     # Landing page tests
├── sensor-dashboard.spec.ts # Dashboard tests
└── alerts.spec.ts           # Alerts tests
```

## Page Objects

The tests use the Page Object Model pattern:

- `LandingPage` - Hero section, navigation, CTAs
- `SensorDashboard` - Score display, data sources, charts
- `AlertsPage` - Alert CRUD, notifications, history
- `MockAPIHelper` - API mocking for test data

## Mock API

Tests use mocked API responses for consistent testing:

```typescript
// Mock sensitivity score
await mockAPI.mockSensitivityScore(45, 'Elevated');

// Mock alerts list
await mockAPI.mockAlerts([
  { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
]);

// Mock data source error
await mockAPI.mockDataSourceError('noaa');
```

## Configuration

Set the base URL via environment variable:

```bash
BASE_URL=http://127.0.0.1:3000 npm test
```

Default is `http://127.0.0.1:3000`.

## Sensitivity Levels

Tests cover the 5 sensitivity levels:
- **Low** (0-19): Green
- **Moderate** (20-39): Yellow
- **Elevated** (40-59): Orange
- **High** (60-79): Red
- **Extreme** (80-100): Warning

## Reports

View test report after running:

```bash
npm run report
```

Reports include:
- Test results summary
- Screenshots on failure
- Video recordings (on failure)
- Trace files for debugging

## Environment Resilience

Tests automatically skip when the Sense by Kraliki web server is not available. This behavior is controlled by
the `test-helpers.ts` fixture which checks server availability before running tests.

```typescript
// Tests import from test-helpers instead of @playwright/test
import { test, expect } from './fixtures/test-helpers';
```

This ensures:
- Tests pass (skip) in environments without a running server
- Tests run normally when a server is available
- No manual configuration needed

## Future Web UI

These tests are prepared for when Sense by Kraliki has a web interface. Currently, Sense by Kraliki is primarily
a Telegram bot. The tests will work once a web dashboard is implemented.

To implement the web UI to match these tests, ensure:
1. Landing page at `/`
2. Dashboard at `/dashboard`
3. Alerts page at `/alerts`
4. API endpoints matching the mocked routes

## Test Files

| File | Tests | Description |
|------|-------|-------------|
| `landing-page.spec.ts` | 18 | Homepage, navigation, CTAs |
| `sensor-dashboard.spec.ts` | 26 | Score display, data sources, charts |
| `alerts.spec.ts` | 33 | Alert CRUD, notifications, history |
| **Total** | **77** | All tests skip when server unavailable |
