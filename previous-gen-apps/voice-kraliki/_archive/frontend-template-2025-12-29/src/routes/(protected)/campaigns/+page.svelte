<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query';
	import { FileText, UploadCloud } from 'lucide-svelte';
	import { fetchCampaigns, type CampaignSummary } from '$lib/services/calls';
	import { queryClient } from '$lib/stores';

	const campaignsQuery = createQuery<CampaignSummary[]>({
		queryKey: ['campaigns'],
		queryFn: fetchCampaigns,
		staleTime: 60_000
	});

	let campaigns = $state<CampaignSummary[]>([]);
	let isLoading = $state(false);
	let errorMessage = $state<string | null>(null);

	const unsubscribe = campaignsQuery.subscribe((result) => {
		campaigns = result.data ?? [];
		isLoading = result.isPending;
		errorMessage = result.isError ? (result.error?.message ?? 'Failed to load campaigns.') : null;
	});

	$effect(() => () => {
		unsubscribe();
	});
</script>

<section class="space-y-6">
	<header class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
		<div class="space-y-1">
			<h1 class="text-2xl font-semibold text-text-primary">Campaign Library</h1>
			<p class="text-sm text-text-muted">
				Manage AI-driven calling campaigns, preview steps, and sync updates from the FastAPI backend.
			</p>
		</div>
		<button class="btn btn-primary">
			<UploadCloud class="size-4" /> Import Campaign
		</button>
	</header>

	{#if errorMessage}
		<div class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">
			{errorMessage}
			<button
				class="ml-2 text-primary underline"
				type="button"
				onclick={() => {
					void queryClient.invalidateQueries({ queryKey: ['campaigns'] });
				}}
			>
				Retry
			</button>
		</div>
	{/if}

	{#if isLoading && !campaigns.length}
		<p class="text-xs text-text-muted">Loading campaigns…</p>
	{:else if campaigns.length === 0}
		<p class="text-sm text-text-secondary">No campaigns found.</p>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			{#each campaigns as campaign}
				<article class="card bg-secondary/80">
					<div class="card-header">
						<div class="flex items-center gap-2 text-text-primary">
							<FileText class="size-4" />
							<h2 class="text-lg font-semibold">{campaign.name}</h2>
						</div>
					</div>
					<ul class="text-sm text-text-secondary">
						<li>Language: {campaign.language ?? '—'}</li>
						<li>
							Steps: {campaign.stepsCount ?? (Array.isArray(campaign.steps) ? campaign.steps.length : '—')}
						</li>
					</ul>
				</article>
			{/each}
		</div>
	{/if}
</section>
