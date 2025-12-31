<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';

	onMount(() => {
		// Redirect based on auth state
		const unsubscribe = authStore.subscribe(($auth) => {
			if ($auth.isAuthenticated) {
				goto('/dashboard');
			} else {
				goto('/login');
			}
		});

		return unsubscribe;
	});
</script>

<div class="flex items-center justify-center min-h-screen">
	<p class="text-muted-foreground">Loading...</p>
</div>
