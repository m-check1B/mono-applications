<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { enqueueAssistantCommand } from '$lib/utils/assistantQueue';
	import { BarChart3, Sparkles, Shield } from 'lucide-svelte';
	import { logger } from '$lib/utils/logger';

	let usageStats = $state<any>(null);
	let subscriptionStatus = $state<any>(null);
	let telemetrySummary = $state<any>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const [usage, subscription, telemetry] = await Promise.all([
				api.settings.getUsageStats(),
				api.billing.subscriptionStatus(),
				api.ai.telemetrySummary()
			]);
			usageStats = usage;
			subscriptionStatus = subscription;
			telemetrySummary = telemetry;
		} catch (error) {
			logger.error('Failed to load insights', error);
		} finally {
			isLoading = false;
		}
	});

	function sendPrompt(prompt: string) {
		enqueueAssistantCommand({ prompt });
	}

	let routeBreakdown = $derived(telemetrySummary?.routeBreakdown || telemetrySummary?.routes || []);
	let recentRuns = $derived(telemetrySummary?.recentRuns || telemetrySummary?.history || []);
	let usageHistory = $derived(telemetrySummary?.usageHistory || []);
</script>

<div class="space-y-6">
	<header class="flex flex-col gap-4">
		<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold flex items-center gap-2">
					<BarChart3 class="w-8 h-8 text-primary" />
					Insights
				</h1>
				<p class="text-muted-foreground">Usage, subscription, and orchestration telemetry at a glance.</p>
			</div>
			<button
				class="flex items-center gap-2 px-3 py-2 text-sm rounded-full border border-border hover:bg-accent/40 transition-colors"
				onclick={() => sendPrompt('Give me a health summary of my workspace.')}
			>
				<Sparkles class="w-4 h-4" />
				Ask assistant
			</button>
		</div>

		<!-- Quick Stats Summary -->
		<div class="bg-gradient-to-br from-primary/10 via-accent/10 to-secondary/10 border border-primary/20 rounded-2xl p-4">
			<div class="flex items-center justify-between flex-wrap gap-3">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
						<Shield class="w-5 h-5 text-primary" />
					</div>
					<div>
						<p class="text-xs text-muted-foreground">Account Status</p>
						<p class="font-semibold">{usageStats?.isPremium ? 'Premium' : 'Free Tier'}</p>
					</div>
				</div>
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
						<BarChart3 class="w-5 h-5 text-blue-600" />
					</div>
					<div>
						<p class="text-xs text-muted-foreground">BYOK Status</p>
						<p class="font-semibold">{usageStats?.hasCustomKey ? 'Enabled' : 'Disabled'}</p>
					</div>
				</div>
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
						<Sparkles class="w-5 h-5 text-green-600" />
					</div>
					<div>
						<p class="text-xs text-muted-foreground">Orchestrations</p>
						<p class="font-semibold">{telemetrySummary?.orchestratedCount ?? 0}</p>
					</div>
				</div>
			</div>
		</div>
	</header>

	{#if isLoading}
		<div class="flex items-center justify-center h-64">
			<div class="flex items-center gap-3">
				<div class="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
				<p class="text-sm text-muted-foreground">Loading insights…</p>
			</div>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold flex items-center gap-2">
						<Shield class="w-4 h-4 text-primary" />
						Usage
					</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('How is my usage trending versus limits?')}
					>
						Ask assistant
					</button>
				</div>
				<p class="text-2xl font-bold">{usageStats?.usageCount ?? 0}</p>
				<p class="text-xs text-muted-foreground">
					Remaining: {usageStats?.remainingUsage ?? '∞'} · BYOK: {usageStats?.hasCustomKey ? 'On' : 'Off'}
				</p>
			</section>

			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold flex items-center gap-2">
						<Shield class="w-4 h-4 text-primary" />
						Subscription
					</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('Do I need to adjust my subscription or billing?')}
					>
						Tell assistant
					</button>
				</div>
				<p class="text-2xl font-bold capitalize">{subscriptionStatus?.status || 'free'}</p>
				<p class="text-xs text-muted-foreground">
					Renews:{' '}
					{subscriptionStatus?.currentPeriodEnd
						? new Date(subscriptionStatus.currentPeriodEnd * 1000).toLocaleDateString()
						: 'n/a'}
				</p>
			</section>

			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold flex items-center gap-2">
						<BarChart3 class="w-4 h-4 text-primary" />
						Orchestration
					</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('Review my orchestrator telemetry and suggest improvements.')}
					>
						Review
					</button>
				</div>
				<p class="text-2xl font-bold">{telemetrySummary?.orchestratedCount ?? 0}</p>
				<p class="text-xs text-muted-foreground">
					Deterministic: {telemetrySummary?.deterministicCount ?? 0} · Avg Confidence:{' '}
					{telemetrySummary?.averageConfidence
						? telemetrySummary.averageConfidence.toFixed(2)
						: 'n/a'}
				</p>
			</section>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold">Route breakdown</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('Analyze orchestrated vs deterministic routes and recommend improvements.')}
					>
						Analyze
					</button>
				</div>
				{#if routeBreakdown.length === 0}
					<p class="text-xs text-muted-foreground">No telemetry breakdown available yet.</p>
				{:else}
					<ul class="text-sm space-y-2">
						{#each routeBreakdown as row}
							<li class="flex items-center justify-between">
								<span class="text-muted-foreground">{row.route || row.name}</span>
								<span class="font-semibold">{row.count ?? row.value}</span>
							</li>
						{/each}
					</ul>
				{/if}
			</section>

			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold">Recent runs</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('Summarize my last few orchestrations and outcomes.')}
					>
						Summarize
					</button>
				</div>
				{#if recentRuns.length === 0}
					<p class="text-xs text-muted-foreground">No runs recorded yet.</p>
				{:else}
					<ul class="space-y-2 text-sm">
                {#each recentRuns.slice(0, 5) as run}
                  <li class="flex flex-col gap-0.5 text-muted-foreground border-b border-border/60 pb-1 last:border-0 last:pb-0">
                    <div class="flex items-center justify-between">
                      <span>{run.label || run.route || 'Run'}</span>
                      <span>{run.confidence ? `${(run.confidence * 100).toFixed(0)}%` : run.result || ''}</span>
                    </div>
                    {#if run.decisionStatus}
                      <span class="text-[11px] uppercase tracking-wide">Decision: {run.decisionStatus}</span>
                    {/if}
                  </li>
                {/each}
					</ul>
				{/if}
			</section>
		</div>

		{#if usageHistory.length > 0}
			<section class="bg-card border border-border rounded-2xl p-5 space-y-3">
				<div class="flex items-center justify-between">
					<p class="text-sm font-semibold">Usage history</p>
					<button
						class="text-xs text-primary hover:text-primary/80"
						onclick={() => sendPrompt('Review my usage history and forecast when I will hit limits.')}
					>
						Forecast
					</button>
				</div>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
					{#each usageHistory.slice(0, 4) as point}
						<div class="rounded-xl border border-border p-3">
							<p class="text-xs text-muted-foreground">{point.label || point.period || 'Period'}</p>
							<p class="text-lg font-semibold">{point.value ?? point.count ?? 0}</p>
						</div>
					{/each}
				</div>
			</section>
		{/if}
	{/if}
</div>
