# Error Boundary Implementation Guide

## Overview

This implementation provides comprehensive error handling for the Svelte frontend with three main components:
- **errorStore**: Centralized error tracking and management
- **ErrorBoundary**: Application-level error boundary
- **ComponentErrorBoundary**: Component-level granular error handling

## Files Created

1. `/frontend/src/lib/stores/errorStore.ts` - Error tracking store
2. `/frontend/src/lib/components/ErrorBoundary.svelte` - Generic error boundary
3. `/frontend/src/lib/components/ComponentErrorBoundary.svelte` - Component-specific boundary
4. `/frontend/src/routes/+layout.svelte` - Updated with ErrorBoundary integration

## Usage Examples

### 1. Application-Level Error Boundary (Already Integrated)

The main layout already wraps all routes with ErrorBoundary:

```svelte
<!-- /frontend/src/routes/+layout.svelte -->
<QueryClientProvider client={queryClient}>
  <ErrorBoundary>
    {@render children()}
  </ErrorBoundary>
</QueryClientProvider>
```

### 2. Component-Level Error Boundary

Wrap individual components for granular error handling:

```svelte
<!-- Example: Wrapping a data table component -->
<script lang="ts">
  import ComponentErrorBoundary from '$lib/components/ComponentErrorBoundary.svelte';
  import DataTable from './DataTable.svelte';
</script>

<ComponentErrorBoundary componentName="Data Table" showDetails={true}>
  <DataTable />
</ComponentErrorBoundary>
```

### 3. Custom Error Boundary with Fallback UI

```svelte
<script lang="ts">
  import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';

  function handleError(error: Error) {
    console.error('Custom error handler:', error);
    // Send to analytics, logging service, etc.
  }
</script>

<ErrorBoundary onError={handleError}>
  {#snippet fallback({ error, reset })}
    <div class="custom-error">
      <h3>Oops! Something went wrong in this section</h3>
      <p>{error?.message}</p>
      <button onclick={reset}>Reload Section</button>
    </div>
  {/snippet}

  <YourComponent />
</ErrorBoundary>
```

### 4. Using the Error Store

Track and display errors across the application:

```svelte
<script lang="ts">
  import { errorStore } from '$lib/stores/errorStore';

  // Subscribe to all errors
  const errors = $derived($errorStore);

  // Manually add an error
  function reportError() {
    errorStore.addError({
      message: 'Custom error occurred',
      component: 'UserProfile',
      severity: 'warning',
      recovered: false
    });
  }

  // Clear a specific error
  function dismissError(id: string) {
    errorStore.clearError(id);
  }

  // Clear all errors
  function clearAllErrors() {
    errorStore.clearAll();
  }
</script>

<!-- Display error notifications -->
{#if errors.length > 0}
  <div class="error-notifications">
    {#each errors as error (error.id)}
      <div class="error-notification" class:severity-{error.severity}>
        <strong>{error.component || 'App'}</strong>: {error.message}
        <button onclick={() => dismissError(error.id)}>Dismiss</button>
      </div>
    {/each}
  </div>
{/if}
```

### 5. API Error Handling Integration

Combine with API clients for comprehensive error handling:

```svelte
<script lang="ts">
  import { errorStore } from '$lib/stores/errorStore';
  import ComponentErrorBoundary from '$lib/components/ComponentErrorBoundary.svelte';

  async function fetchData() {
    try {
      const response = await fetch('/api/data');
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }
      return await response.json();
    } catch (err: any) {
      errorStore.addError({
        message: err.message,
        component: 'DataFetcher',
        severity: 'error',
        recovered: false
      });
      throw err; // Re-throw to trigger component boundary
    }
  }
</script>

<ComponentErrorBoundary componentName="Data Fetcher">
  {#await fetchData()}
    <p>Loading...</p>
  {:then data}
    <DataDisplay {data} />
  {/await}
</ComponentErrorBoundary>
```

## Features

### Error Store
- Centralized error tracking with unique IDs
- Timestamp tracking for all errors
- Severity levels: error, warning, info
- Component-level error attribution
- Stack trace preservation
- Recovery status tracking

### ErrorBoundary Component
- Application-level error catching
- Custom fallback UI support
- Error event listener integration
- Automatic error store integration
- Reset functionality for recovery
- Accessibility features (ARIA roles, live regions)

### ComponentErrorBoundary
- Granular component-level error handling
- Try/catch block integration
- Optional error detail display
- Component name tracking
- Individual component reset
- Warning-style UI for less critical errors

## Accessibility Features

All error boundaries include:
- `role="alert"` for screen readers
- `aria-live="assertive"` for immediate announcements
- `aria-label` attributes for action buttons
- Keyboard navigation support
- Focus management

## Best Practices

1. **Use ErrorBoundary at layout level** for application-wide error catching
2. **Use ComponentErrorBoundary** around:
   - Complex data display components
   - Third-party integrations
   - API data fetching components
   - User input forms

3. **Configure showDetails** based on environment:
   ```svelte
   <ComponentErrorBoundary
     componentName="MyComponent"
     showDetails={import.meta.env.DEV}
   />
   ```

4. **Integrate with monitoring services**:
   ```svelte
   <ErrorBoundary onError={(error) => {
     // Send to Sentry, LogRocket, etc.
     analyticsService.trackError(error);
   }}>
     <App />
   </ErrorBoundary>
   ```

5. **Display global error notifications**:
   Create a notification component that subscribes to errorStore and displays errors as toast notifications.

## Testing

### Manual Testing
1. Trigger a runtime error in a component
2. Verify error boundary catches it
3. Check error appears in errorStore
4. Test reset functionality
5. Verify accessibility with screen reader

### Unit Testing
```typescript
import { render, fireEvent } from '@testing-library/svelte';
import { errorStore } from '$lib/stores/errorStore';
import ComponentErrorBoundary from '$lib/components/ComponentErrorBoundary.svelte';

test('catches component errors', () => {
  const { getByText } = render(ComponentErrorBoundary, {
    props: {
      componentName: 'Test',
      children: () => { throw new Error('Test error'); }
    }
  });

  expect(getByText('Test Error')).toBeInTheDocument();
});
```

## Next Steps

1. Create global error notification component
2. Integrate with logging service (Sentry, LogRocket, etc.)
3. Add error recovery strategies for specific error types
4. Implement error analytics dashboard
5. Add production vs development error detail levels
