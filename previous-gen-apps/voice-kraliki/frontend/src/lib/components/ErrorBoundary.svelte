<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { errorStore } from '$lib/stores/errorStore';

  let { children, fallback, onError } = $props<{
    children: any;
    fallback?: any;
    onError?: (error: Error) => void;
  }>();

  let hasError = $state(false);
  let error = $state<Error | null>(null);

  function handleError(event: ErrorEvent) {
    event.preventDefault();
    hasError = true;
    error = event.error;

    errorStore.addError({
      message: event.error?.message || 'Unknown error',
      stack: event.error?.stack,
      severity: 'error',
      recovered: false
    });

    if (onError) {
      onError(event.error);
    }
  }

  function reset() {
    hasError = false;
    error = null;
  }

  onMount(() => {
    if (browser) {
      window.addEventListener('error', handleError);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('error', handleError);
    }
  });
</script>

{#if hasError}
  {#if fallback}
    {@render fallback({ error, reset })}
  {:else}
    <div class="error-boundary" role="alert" aria-live="assertive">
      <div class="error-content">
        <h2>Something went wrong</h2>
        <p>An unexpected error occurred. Please try again.</p>
        <button onclick={reset} class="retry-button">
          Try Again
        </button>
      </div>
    </div>
  {/if}
{:else}
  {@render children()}
{/if}

<style>
  .error-boundary {
    padding: 2rem;
    background: var(--error-background, #fee);
    border: 2px solid var(--error-border, #f88);
    border-radius: 8px;
    margin: 1rem;
  }

  .error-content {
    text-align: center;
  }

  .error-content h2 {
    color: var(--error-text, #c00);
    margin-bottom: 0.5rem;
  }

  .retry-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .retry-button:hover {
    opacity: 0.9;
  }

  .retry-buttonfocus {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
  }
</style>
