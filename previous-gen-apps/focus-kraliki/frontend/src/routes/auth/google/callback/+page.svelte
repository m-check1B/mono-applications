<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		// Extract code and state from URL
		const urlParams = new URLSearchParams(window.location.search);
		const code = urlParams.get('code');
		const state = urlParams.get('state');
		const error = urlParams.get('error');

		if (error) {
			// Notify parent window of error
			window.opener?.postMessage(
				{
					type: 'GOOGLE_AUTH_ERROR',
					error: error
				},
				window.location.origin
			);
			window.close();
			return;
		}

		if (code) {
			// Notify parent window of success
			window.opener?.postMessage(
				{
					type: 'GOOGLE_AUTH_SUCCESS',
					code: code,
					state: state,
					redirectUri: window.location.origin + window.location.pathname
				},
				window.location.origin
			);
			window.close();
		} else {
			window.opener?.postMessage(
				{
					type: 'GOOGLE_AUTH_ERROR',
					error: 'No authorization code received'
				},
				window.location.origin
			);
			window.close();
		}
	});
</script>

<div class="flex items-center justify-center min-h-screen bg-background">
	<div class="text-center">
		<p class="text-muted-foreground">Completing Google Sign In...</p>
	</div>
</div>
