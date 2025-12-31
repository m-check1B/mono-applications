<script lang="ts">
	import { onMount } from 'svelte';
	import { Ghost, Lock, Unlock, Brain, Sparkles, ArrowRight, RefreshCw, Loader2 } from 'lucide-svelte';
	import { shadowStore } from '$lib/stores/shadow';
	import { fade, fly } from 'svelte/transition';

	let profile = $derived($shadowStore.profile);
	let insights = $derived($shadowStore.insights);
	let unlockStatus = $derived($shadowStore.unlockStatus);
	let isLoading = $derived($shadowStore.isLoading);

	onMount(() => {
		shadowStore.loadAll();
	});

	async function handleAnalyze() {
		await shadowStore.analyze();
	}

	async function handleAcknowledge(insightId: string) {
		await shadowStore.acknowledgeInsight(insightId);
	}
</script>

<div class="h-full flex flex-col">
	<!-- Header -->
	<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10">
		<div class="flex items-center gap-3">
			<div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">
				<Ghost class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">Shadow Work</h2>
				<p class="text-sm font-bold text-muted-foreground">Archetype Analysis & Integration</p>
			</div>
		</div>
		<button 
			class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"
			onclick={handleAnalyze}
			disabled={isLoading}
		>
			{#if isLoading}
				<Loader2 class="w-4 h-4 animate-spin" />
				Analyzing...
			{:else}
				<Sparkles class="w-4 h-4" />
				New Analysis
			{/if}
		</button>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto p-6 space-y-8">
		{#if isLoading && !profile}
			<div class="h-full flex items-center justify-center">
				<Loader2 class="w-8 h-8 animate-spin" />
			</div>
		{:else}
			<!-- Unlock Status (if locked) -->
			{#if unlockStatus && !unlockStatus.isUnlocked}
				<div class="brutal-card p-8 bg-zinc-900 text-white relative overflow-hidden">
					<div class="absolute top-0 right-0 p-8 opacity-10">
						<Lock class="w-32 h-32" />
					</div>
					<div class="relative z-10 max-w-2xl">
						<h3 class="text-2xl font-black uppercase tracking-tighter mb-4 flex items-center gap-3">
							<Lock class="w-6 h-6" />
							Shadow Mode Locked
						</h3>
						<p class="text-lg font-medium mb-6 opacity-90">
							Complete more tasks and maintain focus to unlock deep psychological insights.
						</p>
						
						<div class="space-y-4">
							<div class="flex justify-between text-sm font-bold uppercase">
								<span>Progress to Unlock</span>
								<span>{Math.round(unlockStatus.progress * 100)}%</span>
							</div>
							<div class="h-6 w-full border-2 border-white bg-black p-0.5">
								<div 
									class="h-full bg-white transition-all duration-500"
									style="width: {unlockStatus.progress * 100}%"
								></div>
							</div>
							<div class="flex flex-wrap gap-2 mt-4">
								{#each unlockStatus.requirements as req}
									<span class="text-xs font-bold uppercase px-2 py-1 border border-white/50 bg-white/10">
										{req}
									</span>
								{/each}
							</div>
						</div>
					</div>
				</div>
			{:else if profile}
				<!-- Profile & Archetypes -->
				<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
					<!-- Primary Archetype -->
					<div class="brutal-card p-6 bg-primary text-primary-foreground flex flex-col justify-between min-h-[200px]">
						<div>
							<span class="text-xs font-black uppercase opacity-70">Primary Archetype</span>
							<h3 class="text-3xl font-black uppercase tracking-tighter mt-1">{profile.archetypes.primary}</h3>
						</div>
						<div class="mt-4">
							<Brain class="w-12 h-12 opacity-80" />
						</div>
					</div>

					<!-- Shadow Archetype -->
					<div class="brutal-card p-6 bg-black text-white dark:bg-white dark:text-black flex flex-col justify-between min-h-[200px]">
						<div>
							<span class="text-xs font-black uppercase opacity-70">Shadow Archetype</span>
							<h3 class="text-3xl font-black uppercase tracking-tighter mt-1">{profile.archetypes.shadow}</h3>
						</div>
						<div class="mt-4">
							<Ghost class="w-12 h-12 opacity-80" />
						</div>
					</div>

					<!-- Integration Level -->
					<div class="brutal-card p-6 flex flex-col justify-between min-h-[200px]">
						<div>
							<span class="text-xs font-black uppercase text-muted-foreground">Integration Level</span>
							<div class="flex items-end gap-2 mt-1">
								<h3 class="text-5xl font-black tracking-tighter">{profile.integration_level}%</h3>
							</div>
						</div>
						<div class="w-full bg-secondary h-4 border-2 border-black dark:border-white mt-4">
							<div class="h-full bg-green-500" style="width: {profile.integration_level}%"></div>
						</div>
					</div>
				</div>

				<!-- Daily Insights -->
				<div class="space-y-4">
					<h3 class="text-xl font-black uppercase tracking-tight flex items-center gap-2">
						<Sparkles class="w-5 h-5" />
						Daily Insights
					</h3>
					
					{#if insights.length === 0}
						<div class="p-8 border-2 border-black dark:border-white border-dashed text-center opacity-60">
							<p class="font-bold uppercase">No insights generated yet.</p>
							<button class="text-sm underline mt-2" onclick={handleAnalyze}>Run analysis</button>
						</div>
					{:else}
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							{#each insights as insight (insight.id)}
								<div 
									class="brutal-card p-6 flex flex-col gap-4 {insight.acknowledged ? 'opacity-60 bg-secondary/20' : 'bg-background'}"
									transition:fly={{ y: 20, duration: 300 }}
								>
									<div class="flex items-start justify-between">
										<span class="text-xs font-black uppercase px-2 py-0.5 border border-black dark:border-white bg-secondary">
											{insight.type}
										</span>
										<span class="text-xs font-bold text-muted-foreground">
											{new Date(insight.created_at).toLocaleDateString()}
										</span>
									</div>
									
									<div>
										<h4 class="text-lg font-black uppercase tracking-tight mb-2">{insight.title}</h4>
										<p class="text-sm font-medium leading-relaxed text-muted-foreground">
											{insight.description}
										</p>
									</div>

									{#if !insight.acknowledged}
										<button 
											class="mt-auto self-start brutal-btn bg-white text-black text-xs py-2"
											onclick={() => handleAcknowledge(insight.id)}
										>
											Acknowledge
										</button>
									{:else}
										<div class="mt-auto flex items-center gap-2 text-xs font-bold text-green-600 uppercase">
											<RefreshCw class="w-3 h-3" />
											Integrated
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		{/if}
	</div>
</div>
