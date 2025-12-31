<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { Brain, Lock, Unlock, Eye, Calendar } from 'lucide-svelte';
	import { logger } from '$lib/utils/logger';

	interface ShadowInsight {
		id: string;
		type: string;
		content: string;
		day_unlocked: number;
		acknowledged: boolean;
		created_at: string;
	}

	let insights: ShadowInsight[] = [];
	let unlockStatus: any = null;
	let isLoading = true;
	let isAnalyzing = false;

	onMount(async () => {
		await loadShadowData();
	});

	async function loadShadowData() {
		isLoading = true;
		try {
			const [insightsData, statusData] = await Promise.all([
				api.shadow.getInsights(),
				api.shadow.getUnlockStatus()
			]);

			insights = (insightsData as any).insights || [];
			unlockStatus = statusData;
		} catch (error) {
			logger.error('Failed to load shadow data', error);
		} finally {
			isLoading = false;
		}
	}

	async function runAnalysis() {
		isAnalyzing = true;
		try {
			const result: any = await api.shadow.analyze({});

			// Reload insights after analysis
			await loadShadowData();

			alert(result.analysis || 'Analysis complete!');
		} catch (error: any) {
			alert('Analysis failed: ' + (error.detail || 'Unknown error'));
		} finally {
			isAnalyzing = false;
		}
	}

	async function acknowledgeInsight(insightId: string) {
		try {
			await api.shadow.acknowledgeInsight(insightId);

			// Update local state
			insights = insights.map(i =>
				i.id === insightId ? { ...i, acknowledged: true } : i
			);
		} catch (error) {
			logger.error('Failed to acknowledge insight', error);
		}
	}

	function getInsightTypeColor(type: string): string {
		switch (type.toLowerCase()) {
			case 'behavior':
				return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
			case 'pattern':
				return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
			case 'emotion':
				return 'bg-pink-500/10 text-pink-500 border-pink-500/20';
			case 'cognitive':
				return 'bg-green-500/10 text-green-500 border-green-500/20';
			default:
				return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
		}
	}

	function getDaysUntilUnlock(dayUnlocked: number): number {
		const currentDay = unlockStatus?.current_day || 1;
		return Math.max(0, dayUnlocked - currentDay);
	}

	function isUnlocked(dayUnlocked: number): boolean {
		const currentDay = unlockStatus?.current_day || 1;
		return currentDay >= dayUnlocked;
	}
</script>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold flex items-center gap-2">
				<Brain class="w-8 h-8 text-primary" />
				Shadow Work
			</h1>
			<p class="text-muted-foreground mt-1">
				Jungian psychology insights for productivity and self-awareness
			</p>
		</div>
		<button
			onclick={runAnalysis}
			disabled={isAnalyzing}
			class="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
		>
			<Brain class="w-4 h-4" />
			{isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
		</button>
	</div>

	{#if isLoading}
		<div class="flex items-center justify-center h-64">
			<p class="text-muted-foreground">Loading shadow insights...</p>
		</div>
	{:else}
		<!-- Unlock Status -->
		{#if unlockStatus}
			<div class="bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20 rounded-lg p-6">
				<div class="flex items-center gap-4">
					<div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
						<Calendar class="w-8 h-8 text-primary" />
					</div>
					<div class="flex-1">
						<h3 class="text-xl font-semibold">30-Day Progressive Unlock</h3>
						<p class="text-muted-foreground mt-1">
							Day {unlockStatus.current_day} of 30 •
							{unlockStatus.unlocked_insights_count} insights unlocked
						</p>
						<div class="mt-3 w-full bg-background rounded-full h-2">
							<div
								class="bg-primary h-2 rounded-full transition-all duration-500"
								style="width: {(unlockStatus.current_day / 30) * 100}%"
							></div>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Insights Grid -->
		{#if insights.length === 0}
			<div class="text-center py-16 bg-card border border-border rounded-lg">
				<Brain class="w-16 h-16 text-muted-foreground mx-auto mb-4" />
				<p class="text-muted-foreground mb-4">No shadow insights yet</p>
				<button
					onclick={runAnalysis}
					class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Run your first analysis
				</button>
			</div>
		{:else}
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
				{#each insights as insight (insight.id)}
					<div
						class="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-all {!isUnlocked(
							insight.day_unlocked
						)
							? 'opacity-60'
							: ''}"
					>
						<!-- Insight Header -->
						<div class="flex items-start justify-between mb-4">
							<div class="flex items-center gap-2">
								{#if isUnlocked(insight.day_unlocked)}
									<Unlock class="w-5 h-5 text-green-500" />
								{:else}
									<Lock class="w-5 h-5 text-muted-foreground" />
								{/if}
								<span class="text-xs px-2 py-1 rounded-full border {getInsightTypeColor(insight.type)}">
									{insight.type}
								</span>
							</div>
							<span class="text-xs text-muted-foreground">
								{#if isUnlocked(insight.day_unlocked)}
									Day {insight.day_unlocked}
								{:else}
									Unlocks in {getDaysUntilUnlock(insight.day_unlocked)} days
								{/if}
							</span>
						</div>

						<!-- Insight Content -->
						<div class="space-y-3">
							{#if isUnlocked(insight.day_unlocked)}
								<p class="text-sm leading-relaxed">{insight.content}</p>

								{#if !insight.acknowledged}
									<button
										onclick={() => acknowledgeInsight(insight.id)}
										class="flex items-center gap-2 text-sm text-primary hover:underline"
									>
										<Eye class="w-4 h-4" />
										Mark as acknowledged
									</button>
								{:else}
									<p class="text-xs text-green-500 flex items-center gap-1">
										<Eye class="w-3 h-3" />
										Acknowledged
									</p>
								{/if}
							{:else}
								<div class="space-y-2">
									<div class="h-4 bg-muted rounded animate-pulse"></div>
									<div class="h-4 bg-muted rounded animate-pulse w-5/6"></div>
									<div class="h-4 bg-muted rounded animate-pulse w-4/6"></div>
								</div>
								<p class="text-sm text-muted-foreground italic">
									This insight will unlock on day {insight.day_unlocked}
								</p>
							{/if}
						</div>

						<!-- Timestamp -->
						<p class="text-xs text-muted-foreground mt-4">
							{new Date(insight.created_at).toLocaleDateString()}
						</p>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Info Section -->
		<div class="bg-card border border-border rounded-lg p-6">
			<h3 class="text-lg font-semibold mb-3">About Shadow Work</h3>
			<div class="space-y-2 text-sm text-muted-foreground">
				<p>
					Shadow Work is based on Carl Jung's concept of the "shadow" - the unconscious aspects of our personality that we've rejected or denied.
				</p>
				<p>
					By analyzing your task patterns, procrastination behaviors, and emotional responses, we provide insights that help you:
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li>Understand unconscious productivity patterns</li>
					<li>Identify emotional triggers and avoidance behaviors</li>
					<li>Recognize cognitive biases affecting task completion</li>
					<li>Integrate denied aspects for holistic productivity</li>
				</ul>
				<p class="mt-4 text-primary">
					New insights unlock progressively over 30 days to allow time for reflection and integration.
				</p>
			</div>
		</div>
	{/if}
</div>
