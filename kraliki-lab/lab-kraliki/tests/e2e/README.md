# Lab by Kraliki E2E Tests

End-to-end tests for the Lab by Kraliki landing page and documentation using Playwright.

## Test Coverage

### Landing Page Tests (`landing-page.spec.ts`)
- Page loads successfully
- Hero section with headline displays
- Navigation with logo and links
- CTA buttons functionality
- Features section with feature cards
- Social proof section with stats
- Footer navigation links
- Heading hierarchy for accessibility
- Meta description for SEO
- Responsive design (mobile and tablet)

### Demo Request Tests (`demo-request.spec.ts`)
- Book Demo CTA button visibility
- CTA section visibility
- Trial signup CTAs
- *Future:* Demo request form validation and submission

### Documentation Navigation Tests (`documentation.spec.ts`)
- Documentation link in footer
- Navigation links to main sections
- Scroll to sections functionality
- API documentation link
- Footer resource links
- Sticky header navigation
- *Future:* Full documentation site tests

## Running Tests

```bash
# Install dependencies (first time only)
npm install
npx playwright install

# Run all tests
npm run test:e2e

# Run tests with UI
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test landing-page.spec.ts
```

## Test Configuration

The tests use a local HTTP server to serve the landing page from `demo/outputs/before-after/`. The server starts automatically when running tests.

### Environment Variables

- `MAGIC_BOX_URL` - Override the base URL for tests (default: `http://127.0.0.1:3000`)
- `CI` - Set to `true` in CI environments for retry and worker configuration

## Project Structure

```
tests/e2e/
  landing-page.spec.ts    # Landing page tests
  demo-request.spec.ts    # Demo request form tests
  documentation.spec.ts   # Documentation navigation tests
  reports/                # HTML test reports (gitignored)
  README.md               # This file
```

## Browser Support

Tests run on:
- Chromium (Chrome)
- Firefox
- WebKit (Safari)
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)
