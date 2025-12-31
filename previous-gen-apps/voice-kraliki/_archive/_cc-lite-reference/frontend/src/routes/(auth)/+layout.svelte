<script lang="ts">
  let { children } = $props();
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 px-4">
  <div class="w-full max-w-md">
    {@render children?.()}
  </div>
</div>
