# Speak by Kraliki E2E Tests

Playwright end-to-end tests for Speak by Kraliki, a B2B/B2G employee feedback platform.

## Test Coverage

| Test File | Description | Tests |
|-----------|-------------|-------|
| `landing-page.spec.ts` | Homepage, login, register, responsive design | 20 |
| `survey-creation.spec.ts` | Dashboard routes, survey management, form validation | 18 |
| `employee-access.spec.ts` | Magic link flow, consent, voice recording, mobile | 22 |

**Total: 60 tests**

## Environment Resilience

Tests skip gracefully when the Speak by Kraliki web server is not available.
This makes the test suite resilient to different environments (CI, local dev, production).

## Running Tests

```bash
# Navigate to test directory
cd /home/adminmatej/github/applications/speak-kraliki/tests/e2e

# Run all tests
npx playwright test

# Run specific test file
npx playwright test landing-page.spec.ts

# Run with UI mode
npx playwright test --ui

# Run headed (see the browser)
npx playwright test --headed

# View test report
npx playwright show-report
```

## Starting the Dev Server

Tests require the Speak by Kraliki frontend to be running:

```bash
cd /home/adminmatej/github/applications/speak-kraliki/frontend
npm run dev -- --host 127.0.0.1
```

Server runs at: `http://127.0.0.1:5173`

## Test Structure

```
tests/e2e/
├── fixtures/
│   ├── test-helpers.ts     # Environment resilience, skip logic
│   └── page-objects.ts     # Page Object Models
├── landing-page.spec.ts    # Landing page tests
├── survey-creation.spec.ts # Survey/dashboard tests
├── employee-access.spec.ts # Employee magic link tests
├── playwright.config.ts    # Playwright configuration
└── README.md               # This file
```

## Page Objects

- `LandingPage` - Homepage with login/register buttons
- `LoginPage` - Authentication form
- `RegisterPage` - User registration
- `DashboardPage` - CEO/Manager dashboard
- `EmployeeVoicePage` - Employee feedback flow (magic links)
- `SurveyCreationModal` - Survey creation form

## Features Tested

### Landing Page
- Page load and title
- Hero section and heading
- Login/Register buttons
- Feature cards (01, 02, 03)
- Navigation to login/register
- Responsive design (mobile, tablet, desktop)
- Accessibility (heading hierarchy, keyboard nav)
- Performance (load time, console errors)

### Survey Creation Flow
- Dashboard route protection
- Survey routes (CRUD)
- Action routes
- Employee routes
- Alert routes
- Analytics routes
- Form validation

### Employee Access Flow
- Magic link routes (/v/[token])
- Consent screen
- Speak by Kraliki branding
- Anonymity guarantees
- Voice interface
- Microphone permissions
- Text mode fallback
- Invalid token handling
- Mobile experience
- Touch-friendly buttons
- Transcript review

## Locale Support

Speak by Kraliki supports Czech (cs) as the default locale.
Tests use regex patterns to match both Czech and English UI text:

- Login: `prihlasit|sign in|login`
- Register: `zalozit|create|register`
- Start: `pojdme|start|begin`
- Skip: `preskocit|skip`

## CI/CD Integration

Tests automatically skip when the server is unavailable, making them safe
to run in CI environments without server setup. For full test coverage,
ensure the dev server is running or use the webServer configuration.
