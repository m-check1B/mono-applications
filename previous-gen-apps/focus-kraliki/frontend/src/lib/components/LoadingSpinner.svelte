<!--
✨ LOADING SPINNER: Enhanced Feedback & Visibility (Gap #12)
Brutalist-styled loading indicator for AI operations
-->
<script lang="ts">
  interface Props {
    size?: 'sm' | 'md' | 'lg';
    label?: string;
  }

  let { size = 'md', label = '' }: Props = $props();
</script>

<div class="loading-spinner {size}" role="status" aria-live="polite">
  <div class="spinner brutal-border"></div>
  {#if label}
    <span class="label text-xs font-bold uppercase tracking-wide">{label}</span>
  {/if}
  <span class="sr-only">Loading...</span>
</div>

<style>
  .loading-spinner {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .spinner {
    border-width: 3px;
    border-style: solid;
    border-color: currentColor;
    border-top-color: transparent;
    border-radius: 0; /* Brutalist: no rounded corners */
    animation: spin 0.8s linear infinite;
  }

  .loading-spinner.sm .spinner {
    width: 16px;
    height: 16px;
    border-width: 2px;
  }

  .loading-spinner.md .spinner {
    width: 24px;
    height: 24px;
    border-width: 3px;
  }

  .loading-spinner.lg .spinner {
    width: 32px;
    height: 32px;
    border-width: 4px;
  }

  .label {
    color: inherit;
    opacity: 0.8;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
