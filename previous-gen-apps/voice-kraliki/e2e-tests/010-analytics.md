# E2E Test 010: Analytics Page

**Priority:** Medium
**Route:** `/analytics`
**URL:** https://voice.verduona.dev/analytics

## Objective

Verify the analytics page loads and displays call center metrics and reports.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: Analytics Page Load

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/analytics
3. Verify page loads with:
   - Analytics dashboard header
   - Metric charts/graphs
   - Date range selector (if present)
   - Report generation options
4. Take a screenshot
```

### Test B: Dashboard Metrics

```
1. On analytics page
2. Look for key metrics:
   - Call volume statistics
   - Average handle time
   - Success/failure rates
   - Agent performance metrics
3. Check if data loads correctly
4. Take a screenshot of metrics display
```

### Test C: Date Range Selection

```
1. On analytics page
2. Find date range selector (if available)
3. Try selecting different time periods:
   - Today
   - Last 7 days
   - Last 30 days
   - Custom range
4. Verify data updates accordingly
5. Take a screenshot
```

### Test D: Export/Reports

```
1. On analytics page
2. Look for export functionality:
   - Export button
   - Report generation
   - PDF/CSV options
3. Note available export formats
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] Analytics page loads successfully
- [ ] Charts/graphs render correctly
- [ ] No data loading errors

### Test B
- [ ] Key metrics displayed
- [ ] Values are numeric (not NaN/undefined)
- [ ] Metrics update in real-time if applicable

### Test C
- [ ] Date selector functional
- [ ] Data refreshes on selection
- [ ] No errors on date change

### Test D
- [ ] Export options available
- [ ] Report generation works
- [ ] Formats clearly indicated

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/analytics
Take a screenshot
Report:
- What metrics are displayed?
- Are there charts or graphs?
- Is there a date range selector?
- What export options are available?
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**
