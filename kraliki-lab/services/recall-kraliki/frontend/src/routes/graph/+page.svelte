<script lang="ts">
	import { onMount } from 'svelte';
	import { getGraph } from '$lib/api';

	let category = '';
	let loading = true;
	let error = '';
	let nodes: any[] = [];
	let edges: any[] = [];
	let stats: any = {};

	const categories = [
		'all',
		'decisions',
		'insights',
		'ideas',
		'learnings',
		'customers',
		'competitors',
		'research',
		'sessions'
	];

	async function loadGraph() {
		loading = true;
		error = '';

		try {
			const response = await getGraph(
				category === 'all' ? undefined : category,
				undefined,
				2,
				100
			);

			nodes = response.nodes;
			edges = response.edges;
			stats = response.stats;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load graph';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadGraph();
	});

	$: if (category !== undefined) {
		loadGraph();
	}
</script>

<svelte:head>
	<title>Graph • RECALL-KRALIKI</title>
</svelte:head>

<div class="max-w-6xl mx-auto">
	<div class="mb-10">
		<h1 class="text-4xl font-display mb-2">KNOWLEDGE_GRAPH</h1>
		<div class="flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider">
			<span class="text-terminal-green">&gt;&gt; STATUS:</span> MAPPING_NEURAL_CONNECTIONS
		</div>
	</div>

	<!-- Category Filter -->
	<div class="brutal-card p-4 mb-8 bg-card flex flex-col md:flex-row items-center gap-4">
		<div class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-60">Sub_Graph_Isolation:</div>
		<div class="flex-1 w-full">
			<select
				bind:value={category}
				class="brutal-input !py-2 appearance-none cursor-pointer"
			>
				{#each categories as cat}
					<option value={cat === 'all' ? '' : cat}>{cat.toUpperCase()}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if loading}
		<div class="brutal-card text-center py-20 bg-card">
			<div class="text-2xl font-display text-terminal-green animate-pulse">COMPUTING_TOPOLOGY...</div>
			<div class="mt-4 font-mono text-[10px] opacity-40 uppercase tracking-[0.3em]">Processing connections across nodes</div>
		</div>
	{:else if error}
		<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 font-mono text-sm">
			<span class="font-bold uppercase">[ GRAPH_ERROR ]</span> {error}
		</div>
	{:else}
		<!-- Stats -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
			<div class="brutal-card p-4 bg-card">
				<p class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-50 mb-1">Nodes</p>
				<p class="text-3xl font-display text-terminal-green">{stats.total_nodes || 0}</p>
			</div>

			<div class="brutal-card p-4 bg-card">
				<p class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-50 mb-1">Edges</p>
				<p class="text-3xl font-display text-cyan-data">{stats.total_edges || 0}</p>
			</div>

			<div class="brutal-card p-4 bg-card">
				<p class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-50 mb-1">Clusters</p>
				<p class="text-3xl font-display">{stats.categories || 0}</p>
			</div>

			<div class="brutal-card p-4 bg-card">
				<p class="text-[10px] font-mono font-bold uppercase tracking-widest opacity-50 mb-1">Density</p>
				<p class="text-3xl font-display text-primary">{stats.avg_connections?.toFixed(1) || 0}</p>
			</div>
		</div>

		<!-- Graph Visualization Placeholder -->
		<div class="brutal-card p-12 mb-8 bg-void relative overflow-hidden min-h-[400px] flex items-center justify-center">
			<div class="absolute inset-0 opacity-10 pointer-events-none">
				<div class="w-full h-full bg-grid-pattern"></div>
			</div>
			
			<div class="text-center relative z-10">
				<div class="text-6xl mb-4 opacity-50 animate-pulse">📊</div>
				<h2 class="text-2xl font-display text-terminal-green mb-4">GRAPH_VISUALIZATION_READY</h2>
				<p class="font-mono text-xs uppercase tracking-[0.2em] opacity-60 mb-8 max-w-md mx-auto">
					Interactive D3.js topology engine initialized. Awaiting vector rendering.
				</p>

				{#if stats.most_connected}
					<div class="brutal-card bg-void border-terminal-green/50 p-4 text-left inline-block">
						<p class="text-[9px] font-bold uppercase tracking-[0.2em] text-terminal-green mb-1">Highest Centrality:</p>
						<p class="font-mono text-xs text-concrete">{stats.most_connected}</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Node List -->
		{#if nodes.length > 0}
			<div class="brutal-card p-6 bg-card relative">
				<div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[40px] leading-none pointer-events-none select-none">NODES</div>
				<h3 class="font-display text-lg border-b-2 border-border pb-2 mb-6 uppercase">INDEXED_NODES ({nodes.length})</h3>

				<div class="space-y-2 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
					{#each nodes as node}
						<div class="flex flex-wrap items-center justify-between p-3 border-2 border-transparent hover:border-border bg-void/5 hover:bg-void/10 transition-all">
							<div class="flex items-center gap-3">
								<span class="text-[9px] font-bold px-1.5 py-0.5 bg-void text-terminal-green uppercase tracking-widest">
									{node.category}
								</span>
								<span class="text-sm font-bold uppercase tracking-tight">{node.label}</span>
							</div>

							<div class="flex items-center gap-6">
								{#if node.tags && node.tags.length > 0}
									<div class="hidden sm:flex flex-wrap gap-1">
										{#each node.tags.slice(0, 2) as tag}
											<span class="text-[8px] font-bold px-1.5 py-0.5 border border-border opacity-50 uppercase">
												{tag}
											</span>
										{/each}
									</div>
								{/if}

								<div class="flex items-center gap-2">
									<div class="h-2 w-24 bg-void border border-border hidden xs:block overflow-hidden">
										<div class="h-full bg-primary" style="width: {Math.min(100, node.size * 20)}%"></div>
									</div>
									<span class="text-[10px] font-mono font-bold w-12 text-right">
										{node.size} CX
									</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: rgba(0, 0, 0, 0.05);
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: hsl(var(--border));
	}
</style>
