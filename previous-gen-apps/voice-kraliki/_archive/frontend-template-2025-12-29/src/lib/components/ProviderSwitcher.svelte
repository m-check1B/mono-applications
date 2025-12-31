<script lang="ts">
import { Zap, Check, Loader2 } from 'lucide-svelte';

interface Provider {
	id: string;
	name: string;
	status: 'active' | 'available' | 'unavailable';
	capabilities?: {
		realtime: boolean;
		multimodal: boolean;
		functionCalling: boolean;
	};
}

interface Props {
	providers?: Provider[];
	currentProvider?: string | null;
	isLive?: boolean;
	onSwitch?: (providerId: string) => void | Promise<void>;
}

let {
	providers = [],
	currentProvider = null,
	isLive = false,
	onSwitch
}: Props = $props();

let isSwitching = $state(false);

async function handleSwitch(providerId: string) {
	if (isSwitching || providerId === currentProvider) return;
	if (!onSwitch) return;

	isSwitching = true;
	try {
		await onSwitch(providerId);
	} catch (error) {
		console.error('Failed to switch provider:', error);
	} finally {
		isSwitching = false;
	}
}

function getStatusColor(status: Provider['status']): string {
	switch (status) {
		case 'active':
			return 'border-primary bg-primary/10';
		case 'available':
			return 'border-divider bg-secondary/50 hover:border-primary/50 hover:bg-primary/5';
		case 'unavailable':
			return 'border-divider bg-secondary/20 opacity-50 cursor-not-allowed';
		default:
			return 'border-divider bg-secondary/50';
	}
}

function getProviderIcon(providerId: string): string {
	// Return emoji or icon based on provider
	if (providerId.includes('gemini')) return '🤖';
	if (providerId.includes('openai')) return '🔷';
	if (providerId.includes('deepgram')) return '🎙️';
	return '⚡';
}
</script>

<article class="card">
	<div class="card-header">
		<div class="flex items-center gap-2">
			<Zap class="size-5 text-text-primary" />
			<h2 class="text-lg font-semibold text-text-primary">Voice Provider</h2>
		</div>
		<span class="text-xs text-text-muted">
			{#if isLive}
				<span class="inline-flex items-center gap-1.5 text-primary">
					<span class="size-1.5 animate-pulse rounded-full bg-primary"></span>
					Switch enabled
				</span>
			{:else}
				Not in call
			{/if}
		</span>
	</div>

	<div class="space-y-2">
		{#if providers.length === 0}
			<p class="text-sm text-text-muted">No providers configured</p>
		{:else}
			{#each providers as provider}
				<button
					type="button"
					class={`w-full rounded-xl border-2 p-4 text-left transition-all ${getStatusColor(provider.status)}`}
					disabled={provider.status === 'unavailable' || isSwitching}
					onclick={() => handleSwitch(provider.id)}
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-3">
							<span class="text-2xl" role="img" aria-label={provider.name}>
								{getProviderIcon(provider.id)}
							</span>
							<div>
								<p class="text-sm font-semibold text-text-primary">
									{provider.name}
								</p>
								{#if provider.capabilities}
									<div class="mt-1 flex gap-2 text-xs text-text-muted">
										{#if provider.capabilities.realtime}
											<span>Realtime</span>
										{/if}
										{#if provider.capabilities.multimodal}
											<span>• Multimodal</span>
										{/if}
										{#if provider.capabilities.functionCalling}
											<span>• Functions</span>
										{/if}
									</div>
								{/if}
							</div>
						</div>
						<div>
							{#if provider.status === 'active'}
								<Check class="size-5 text-primary" />
							{:else if isSwitching && provider.id !== currentProvider}
								<Loader2 class="size-5 animate-spin text-text-muted" />
							{/if}
						</div>
					</div>
				</button>
			{/each}
		{/if}

		{#if isLive && !isSwitching}
			<p class="mt-3 text-xs text-text-muted">
				💡 You can switch providers during an active call for seamless comparison
			</p>
		{/if}

		{#if isSwitching}
			<div class="flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">
				<Loader2 class="size-4 animate-spin" />
				Switching provider...
			</div>
		{/if}
	</div>
</article>
