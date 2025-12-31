<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.svelte';

  onMount(async () => {
    await auth.init();

    if (auth.isAuthenticated) {
      // Redirect based on role
      if (auth.isAdmin) {
        goto('/admin');
      } else if (auth.isSupervisor) {
        goto('/supervisor');
      } else {
        goto('/operator');
      }
    } else {
      goto('/login');
    }
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
</div>
