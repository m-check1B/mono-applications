<script lang="ts">
	import { onMount } from 'svelte';
	import { BarChart3, TrendingUp, Clock, Calendar, ArrowUpRight, ArrowDownRight, AlertTriangle, CheckCircle2, AlertOctagon, Loader2 } from 'lucide-svelte';
	import { analyticsStore } from '$lib/stores/analytics';

	let overview = $derived($analyticsStore.overview);
	let bottlenecks = $derived($analyticsStore.bottlenecks);
	let isLoading = $derived($analyticsStore.isLoading);

	onMount(() => {
		analyticsStore.loadAll();
	});

	function getSeverityColor(severity: string) {
		switch (severity) {
			case 'high': return 'text-red-600 dark:text-red-400';
			case 'medium': return 'text-orange-600 dark:text-orange-400';
			case 'low': return 'text-yellow-600 dark:text-yellow-400';
			default: return 'text-muted-foreground';
		}
	}

	function getSeverityBg(severity: string) {
		switch (severity) {
			case 'high': return 'bg-red-100 dark:bg-red-900/20';
			case 'medium': return 'bg-orange-100 dark:bg-orange-900/20';
			case 'low': return 'bg-yellow-100 dark:bg-yellow-900/20';
			default: return 'bg-secondary';
		}
	}
</script>

<div class="h-full flex flex-col">
	<!-- Header -->
	<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10">
		<div class="flex items-center gap-3">
			<div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">
				<BarChart3 class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">Insights</h2>
				<p class="text-sm font-bold text-muted-foreground">Productivity Analytics</p>
			</div>
		</div>
		<div class="flex items-center gap-2">
			<span class="text-xs font-bold uppercase px-2 py-1 border border-black dark:border-white bg-white dark:bg-black">
				{new Date().toLocaleDateString()}
			</span>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto p-6 space-y-8 bg-grid-pattern">
		{#if isLoading && !overview}
			<div class="h-full flex items-center justify-center">
				<div class="flex flex-col items-center gap-4">
					<Loader2 class="w-12 h-12 animate-spin text-primary" />
					<p class="font-black uppercase tracking-widest text-sm">Aggregating Data...</p>
				</div>
			</div>
		{:else}
			<!-- KPI Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all">
					<div class="flex items-center justify-between text-muted-foreground">
						<span class="text-xs font-black uppercase tracking-widest">Avg Completion</span>
						<Clock class="w-5 h-5" />
					</div>
					<div class="flex items-end gap-2">
						<span class="text-4xl font-black tracking-tighter tabular-nums">{overview?.avg_completion_time?.toFixed(1) || '0'}h</span>
						<span class="text-[10px] font-black uppercase text-muted-foreground mb-1.5">
							/ task
						</span>
					</div>
				</div>
				
				<div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all">
					<div class="flex items-center justify-between text-muted-foreground">
						<span class="text-xs font-black uppercase tracking-widest">Velocity</span>
						<TrendingUp class="w-5 h-5" />
					</div>
					<div class="flex items-end gap-2">
						<span class="text-4xl font-black tracking-tighter tabular-nums">{overview?.velocity || '0'}</span>
						<span class="text-[10px] font-black uppercase text-green-500 mb-1.5">
							tasks/wk
						</span>
					</div>
				</div>

				<div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all">
					<div class="flex items-center justify-between text-muted-foreground">
						<span class="text-xs font-black uppercase tracking-widest">Comp. Rate</span>
						<CheckCircle2 class="w-5 h-5" />
					</div>
					<div class="flex items-end gap-2">
						<span class="text-4xl font-black tracking-tighter tabular-nums">{Math.round((overview?.completion_rate || 0) * 100)}%</span>
					</div>
				</div>

				<div class="brutal-card p-6 space-y-3 bg-primary text-primary-foreground shadow-card">
					<div class="flex items-center justify-between opacity-80">
						<span class="text-xs font-black uppercase tracking-widest">Total Tasks</span>
						<BarChart3 class="w-5 h-5" />
					</div>
					<div class="flex items-end gap-2">
						<span class="text-4xl font-black tracking-tighter tabular-nums">{overview?.total_tasks || '0'}</span>
						<span class="text-[10px] font-black uppercase opacity-80 mb-1.5">Total</span>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<!-- Bottlenecks -->
				<div class="brutal-card p-0 overflow-hidden flex flex-col bg-card shadow-card">
					<div class="p-5 border-b-2 border-border bg-secondary flex items-center justify-between">
						<h3 class="text-xl font-black uppercase tracking-tighter flex items-center gap-2">
							<AlertOctagon class="w-6 h-6" />
							Critical Bottlenecks
						</h3>
						{#if bottlenecks.length > 0}
							<span class="bg-destructive text-destructive-foreground text-[10px] font-black uppercase px-2 py-0.5 border-2 border-border animate-pulse">
								{bottlenecks.length} Active
							</span>
						{/if}
					</div>
					<div class="divide-y-2 divide-border flex-1">
						{#if bottlenecks.length === 0}
							<div class="p-12 text-center text-muted-foreground bg-grid-pattern bg-[size:16px_16px]">
								<div class="inline-block p-4 border-2 border-border bg-secondary mb-4">
									<CheckCircle2 class="w-12 h-12 opacity-40" />
								</div>
								<p class="font-black uppercase tracking-widest mb-1">Zero Blockers</p>
								<p class="text-[10px] font-bold uppercase tracking-widest opacity-60">Optimized throughput detected.</p>
							</div>
						{:else}
							{#each bottlenecks as bottleneck}
								<div class="p-5 hover:bg-secondary transition-colors group">
									<div class="flex items-start justify-between mb-3">
										<span class="text-[10px] font-black uppercase px-2 py-1 border-2 border-border shadow-brutal-sm {getSeverityBg(bottleneck.severity)} {getSeverityColor(bottleneck.severity)}">
											{bottleneck.type.replace('_', ' ')}
										</span>
										<span class="text-[10px] font-black uppercase text-muted-foreground bg-card px-1.5 border border-border">
											{bottleneck.affected_items.length} ITEMS
										</span>
									</div>
									<p class="font-bold text-base mb-3 leading-tight uppercase tracking-tight">{bottleneck.description}</p>
									{#if bottleneck.suggestion}
										<div class="flex items-start gap-3 text-xs font-bold uppercase tracking-wide text-muted-foreground bg-background p-3 border-2 border-border border-dashed">
											<ArrowUpRight class="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
											<span>RECO: {bottleneck.suggestion}</span>
										</div>
									{/if}
								</div>
							{/each}
						{/if}
					</div>
				</div>

				<!-- Tasks by Priority Chart -->
				<div class="brutal-card p-6 space-y-8 bg-card shadow-card">
					<div class="flex items-center justify-between border-b-2 border-border pb-4">
						<h3 class="text-xl font-black uppercase tracking-tighter">Task Priority Dist.</h3>
						<div class="flex gap-1">
							<div class="w-2 h-2 bg-red-500"></div>
							<div class="w-2 h-2 bg-orange-500"></div>
							<div class="w-2 h-2 bg-blue-500"></div>
						</div>
					</div>
					
					{#if overview?.tasks_by_priority}
						<div class="space-y-6">
							{#each Object.entries(overview.tasks_by_priority) as [priority, count]}
								<div class="space-y-2">
									<div class="flex justify-between text-[10px] font-black uppercase tracking-widest">
										<span class="flex items-center gap-2">
											<div class="w-2 h-2 {priority === 'high' ? 'bg-red-500' : priority === 'medium' ? 'bg-orange-500' : 'bg-blue-500'}"></div>
											{priority}
										</span>
										<span class="tabular-nums">{count} UNITS</span>
									</div>
									<div class="h-10 w-full border-2 border-border bg-secondary p-1 relative">
										<div 
											class="h-full transition-all duration-1000 ease-out {priority === 'high' ? 'bg-red-500' : priority === 'medium' ? 'bg-orange-500' : 'bg-blue-500'}"
											style="width: {(count / (overview.total_tasks || 1)) * 100}%"
										></div>
										<!-- Grid overlay -->
										<div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.05)_1px,transparent_1px)] bg-[size:10%_100%] pointer-events-none"></div>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="h-40 flex items-center justify-center text-muted-foreground font-black uppercase tracking-widest border-2 border-dashed border-border">
							Data Unavailable
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
