# APM Monitoring Dashboard E2E Testing

## Overview

This document summarizes the comprehensive end-to-end (e2e) testing implementation for the APM (Application Performance Monitoring) dashboard in Voice by Kraliki.

## Files Created/Modified

### 1. `/tests/e2e/apm-monitoring.spec.ts` (NEW)
Comprehensive e2e test suite for the APM monitoring dashboard covering:

#### Test Categories:
- **Access and Authentication**: Verifies supervisor/admin access and blocks unauthorized users
- **Dashboard Components and UI**: Tests all main UI components, health cards, and charts
- **Real-time Updates**: Validates auto-refresh, time range changes, and WebSocket integration
- **Responsive Design**: Tests mobile, tablet, and desktop viewports
- **Performance Testing**: Load time validation and rapid interaction testing
- **Accessibility**: Keyboard navigation and user experience testing

#### Key Features Tested:
- ✅ Supervisor login flow for APM access
- ✅ Security verification (non-supervisors blocked)
- ✅ Real-time metrics display with proper data-testid attributes
- ✅ Health status indicators and system status cards
- ✅ Error tracking display and distribution charts
- ✅ Metric refresh functionality and auto-refresh toggle
- ✅ Responsive design across viewports (mobile, tablet, desktop)
- ✅ WebSocket real-time updates simulation
- ✅ Multi-browser compatibility testing
- ✅ Performance metric collection and load time validation

### 2. `/tests/e2e/critical-flows.spec.ts` (UPDATED)
Added new test section: **"APM Dashboard Access and Security"** with:
- Supervisor access verification to `/monitoring` route
- Agent access blocking and security verification
- Performance metric collection testing

### 3. `/src/components/monitoring/APMDashboard.tsx` (UPDATED)
Added essential `data-testid` attributes for reliable e2e testing:
- `data-testid="apm-dashboard"` - Main dashboard container
- `data-testid="time-range-controls"` - Time range button controls
- `data-testid="system-health-card"` - System health status card
- `data-testid="database-health-card"` - Database health status card
- `data-testid="memory-health-card"` - Memory usage health card
- `data-testid="response-time-card"` - Response time metrics card

## Test Coverage

### Authentication & Security
- ✅ Supervisor access to `/monitoring` route
- ✅ Admin access to APM dashboard
- ✅ Agent access blocking (redirect or error handling)
- ✅ Universal test account compatibility

### UI Components
- ✅ Header and navigation elements
- ✅ Time range controls (1h, 6h, 24h, 7d, 30d)
- ✅ Auto-refresh toggle functionality
- ✅ Health status cards with proper indicators
- ✅ Tab navigation (Overview, Errors, Performance)
- ✅ Charts and visualizations (request metrics, memory usage)
- ✅ Error distribution and recent errors display
- ✅ Performance percentiles (P50, P95, P99)

### Real-time Features
- ✅ Auto-refresh mechanism testing
- ✅ Manual refresh disable/enable
- ✅ Time range change updates
- ✅ WebSocket connection simulation
- ✅ Network interruption handling

### Responsive Design
- ✅ Mobile viewport (375x667) compatibility
- ✅ Tablet viewport (768x1024) compatibility
- ✅ Large desktop viewport (2560x1440) compatibility
- ✅ Chart scaling and layout adaptation

### Performance Testing
- ✅ Dashboard load time under 10 seconds
- ✅ Rapid tab switching performance
- ✅ Multiple chart update handling
- ✅ Concurrent user interaction testing

### Browser Compatibility
- ✅ Chrome user agent testing
- ✅ Multi-browser context support
- ✅ Cross-browser screenshot capture

## Test Execution

### Run APM-specific tests:
```bash
pnpm playwright test tests/e2e/apm-monitoring.spec.ts --headed --project=chromium
```

### Run critical flows (includes APM tests):
```bash
pnpm playwright test tests/e2e/critical-flows.spec.ts --headed --project=chromium
```

### Run all e2e tests:
```bash
pnpm playwright test tests/e2e/ --headed
```

## Screenshots Generated

The tests automatically capture screenshots for verification:
- `tests/screenshots/apm-dashboard-supervisor.png` - Supervisor access
- `tests/screenshots/apm-overview-tab.png` - Overview tab content
- `tests/screenshots/apm-errors-tab.png` - Errors tab content
- `tests/screenshots/apm-performance-tab.png` - Performance tab content
- `tests/screenshots/apm-mobile-view.png` - Mobile responsive view
- `tests/screenshots/apm-tablet-view.png` - Tablet responsive view
- `tests/screenshots/apm-large-desktop-view.png` - Large desktop view
- `tests/screenshots/apm-dashboard-access.png` - Access verification

## Test Data and Credentials

### Universal Test Account (Recommended)
```typescript
{
  email: 'test.assistant@stack2025.com',
  password: 'Stack2025!Test@Assistant#Secure$2024',
  userId: '550e8400-e29b-41d4-a716-446655440000',
  role: 'TESTER_UNIVERSAL',
  tier: 'CORPORATE'
}
```

### Environment-based Credentials
- Supervisor: Uses `getSupervisorCredentials()` helper
- Agent: Uses `getAgentCredentials()` helper
- Admin: Uses `getAdminCredentials()` helper

## Best Practices Implemented

### Page Object Patterns
- ✅ Consistent data-testid attribute usage
- ✅ Reliable element selection strategies
- ✅ Wait strategies for dynamic content

### Test Stability
- ✅ Proper loading state handling
- ✅ Network idle waiting for complex operations
- ✅ Timeout management for slow operations
- ✅ Error handling and graceful degradation testing

### User Experience Testing
- ✅ Real user workflow simulation
- ✅ Keyboard navigation testing
- ✅ Accessibility considerations
- ✅ Performance budget validation

### Security Testing
- ✅ Role-based access control verification
- ✅ Unauthorized access prevention
- ✅ Proper redirect handling

## Next Steps

1. **Integration with CI/CD**: Add APM tests to automated build pipeline
2. **Performance Monitoring**: Set up alerts for test performance regressions
3. **Visual Regression**: Consider adding visual comparison testing
4. **Load Testing**: Extend tests to handle high-frequency updates
5. **Accessibility Audits**: Add automated accessibility testing tools

## Technical Notes

- Tests use Playwright with TypeScript for type safety
- Compatible with Voice by Kraliki's existing test infrastructure
- Follows Stack 2025 testing standards
- Uses universal test accounts for cross-app compatibility
- Implements proper error handling and recovery mechanisms