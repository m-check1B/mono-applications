<script lang="ts">
	import { useAppConfig } from '$lib/hooks/useAppConfig';
	import { Save } from 'lucide-svelte';

	const config = useAppConfig();

	let backendUrl = $state(config.backendUrl);
	let wsUrl = $state(config.wsUrl);
</script>

<section class="space-y-6">
	<header class="space-y-1">
		<h1 class="text-2xl font-semibold text-text-primary">Console Settings</h1>
		<p class="text-sm text-text-muted">Update runtime endpoints and experiment flags for the operator console.</p>
	</header>

	<article class="card">
		<div class="card-header">
			<h2 class="text-lg font-semibold text-text-primary">Environment Overrides</h2>
		</div>
		<div class="space-y-4">
			<label class="field" for="backend-url">
				<span class="field-label">Backend URL</span>
				<input id="backend-url" class="input-field" bind:value={backendUrl} />
			</label>
			<label class="field" for="ws-url">
				<span class="field-label">WebSocket URL</span>
				<input id="ws-url" class="input-field" bind:value={wsUrl} />
			</label>
			<button class="btn btn-primary">
				<Save class="size-4" /> Save Changes
			</button>
		</div>
	</article>
</section>
