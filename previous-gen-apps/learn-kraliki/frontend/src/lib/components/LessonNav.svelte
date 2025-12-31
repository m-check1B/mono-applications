<script lang="ts">
  interface Props {
    hasPrevious: boolean;
    hasNext: boolean;
    onPrevious: () => void;
    onNext: () => void;
    onComplete: () => void;
  }

  let { hasPrevious, hasNext, onPrevious, onNext, onComplete }: Props = $props();
</script>

<div class="flex justify-between items-center mt-12 pt-8 border-t-4 border-black">
  <button
    onclick={onPrevious}
    disabled={!hasPrevious}
    class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
  >
    &larr; PREVIOUS
  </button>

  {#if hasNext}
    <button onclick={onNext} class="btn-primary">
      NEXT &rarr;
    </button>
  {:else}
    <button onclick={onComplete} class="btn-primary bg-green-600 border-green-600">
      COMPLETE COURSE
    </button>
  {/if}
</div>
