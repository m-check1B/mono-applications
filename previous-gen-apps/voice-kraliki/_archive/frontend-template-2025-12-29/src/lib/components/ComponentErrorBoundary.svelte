<script lang="ts">
  import { errorStore } from '$lib/stores/errorStore';
  import type { Snippet } from 'svelte';

  let {
    children,
    componentName = 'Component',
    showDetails = false
  } = $props<{
    children: Snippet;
    componentName?: string;
    showDetails?: boolean;
  }>();

  let hasError = $state(false);
  let errorMessage = $state('');
  let errorStack = $state('');

  function catchError(fn: () => any) {
    try {
      return fn();
    } catch (err: any) {
      hasError = true;
      errorMessage = err?.message || 'Unknown error';
      errorStack = err?.stack || '';

      errorStore.addError({
        message: errorMessage,
        stack: errorStack,
        component: componentName,
        severity: 'error',
        recovered: false
      });

      return null;
    }
  }

  function reset() {
    hasError = false;
    errorMessage = '';
    errorStack = '';
  }
</script>

{#if hasError}
  <div class="component-error" role="alert">
    <div class="error-header">
      <span class="error-icon" aria-hidden="true">⚠️</span>
      <span class="error-title">{componentName} Error</span>
    </div>
    <p class="error-message">{errorMessage}</p>
    {#if showDetails && errorStack}
      <details class="error-stack">
        <summary>Error Details</summary>
        <pre>{errorStack}</pre>
      </details>
    {/if}
    <button onclick={reset} class="reset-button" aria-label="Retry loading {componentName}">
      Retry
    </button>
  </div>
{:else}
  {@render children?.()}
{/if}

<style>
  .component-error {
    padding: 1rem;
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    margin: 0.5rem 0;
  }

  .error-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .error-title {
    font-weight: 600;
    color: #856404;
  }

  .error-message {
    color: #856404;
    margin: 0.5rem 0;
  }

  .error-stack {
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .error-stack summary {
    cursor: pointer;
    color: #856404;
    font-weight: 500;
  }

  .error-stack summary:hover {
    text-decoration: underline;
  }

  .error-stack pre {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
    max-height: 200px;
    color: #212529;
    font-size: 0.75rem;
    margin-top: 0.5rem;
  }

  .reset-button {
    margin-top: 0.5rem;
    padding: 0.375rem 0.75rem;
    background: #ffc107;
    color: #000;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .reset-button:hover {
    background: #ffca2c;
  }

  .reset-buttonfocus {
    outline: 2px solid #ffc107;
    outline-offset: 2px;
  }
</style>