<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { PlusIcon, SearchIcon, Trash2Icon, Edit2Icon, PlayIcon, FileTextIcon, MoreVerticalIcon, ZapIcon, SparklesIcon, MicIcon } from 'lucide-svelte';

	interface Scenario {
		id: number;
		name: string;
		description: string;
		category: string;
		difficulty: string;
		is_active: boolean;
		created_at?: string;
		updated_at?: string;
	}

	interface Template {
		id: string;
		name: string;
		description: string;
		category: string;
		difficulty: string;
	}

	let scenarios = $state<Scenario[]>([]);
	let templates = $state<Template[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let selectedCategory = $state('All');
	let showTemplateModal = $state(false);
	let creatingFromTemplate = $state(false);

	const categories = ['All', 'Customer Service', 'Sales', 'Technical Support', 'Compliance'];

	onMount(async () => {
		await Promise.all([loadScenarios(), loadTemplates()]);
	});

	async function loadTemplates() {
		try {
			const response = await fetch('/api/scenarios/templates/list');
			if (response.ok) {
				templates = await response.json();
			}
		} catch (err) {
			console.error('Failed to load templates', err);
		}
	}

	async function createFromTemplate(templateId: string) {
		creatingFromTemplate = true;
		try {
			const response = await fetch('/api/scenarios/templates/create', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ template_id: templateId })
			});
			if (!response.ok) throw new Error('Failed to create from template');
			const newScenario = await response.json();
			showTemplateModal = false;
			// Refresh scenarios list
			await loadScenarios();
			// Navigate to practice mode immediately
			goto(`/scenarios/practice?id=${newScenario.id}`);
		} catch (err) {
			alert('Error creating scenario from template');
		} finally {
			creatingFromTemplate = false;
		}
	}

	async function loadScenarios() {
		loading = true;
		error = null;
		try {
			const response = await fetch('/api/scenarios');
			if (!response.ok) throw new Error('Failed to load scenarios');
			scenarios = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	async function deleteScenario(id: number) {
		if (!confirm('Are you sure you want to delete this scenario? This action cannot be undone.')) return;
		
		try {
			const response = await fetch(`/api/scenarios/${id}`, {
				method: 'DELETE'
			});
			if (!response.ok) throw new Error('Failed to delete scenario');
			scenarios = scenarios.filter(s => s.id !== id);
		} catch (err) {
			alert('Error deleting scenario');
		}
	}

	function formatDate(dateStr?: string) {
		if (!dateStr) return 'N/A';
		return new Date(dateStr).toLocaleDateString('en-US', { 
			year: 'numeric', 
			month: 'short', 
			day: 'numeric' 
		});
	}

	let filteredScenarios = $derived(scenarios.filter(s => {
		const matchesSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
							  s.description.toLowerCase().includes(searchQuery.toLowerCase());
		const matchesCategory = selectedCategory === 'All' || s.category === selectedCategory;
		return matchesSearch && matchesCategory;
	}));

	function getDifficultyColor(diff: string) {
		switch (diff.toLowerCase()) {
			case 'easy': return 'text-terminal-green';
			case 'medium': return 'text-accent';
			case 'hard': return 'text-system-red';
			case 'expert': return 'text-cyan-data';
			default: return 'text-muted-foreground';
		}
	}
</script>

<div class="p-6 max-w-7xl mx-auto min-h-screen space-y-8">
	<!-- Header -->
	<header class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-4 border-foreground pb-6">
		<div class="space-y-2">
			<h1 class="text-5xl font-display text-foreground tracking-tighter uppercase">
				Scenario <span class="text-terminal-green">Matrix</span>
			</h1>
			<p class="text-[11px] font-bold uppercase tracking-[0.3em] text-muted-foreground">
				TRAINING_MODULES // TOTAL_COUNT: {scenarios.length} // STATUS: ONLINE
			</p>
		</div>
		<div class="flex gap-3">
			<button
				onclick={() => goto('/arena')}
				class="brutal-btn bg-primary text-primary-foreground hover:translate-x-[-2px] hover:translate-y-[-2px]"
			>
				<MicIcon class="w-5 h-5 inline mr-2" />
				Voice Arena
			</button>
			<button
				onclick={() => showTemplateModal = true}
				class="brutal-btn bg-accent text-accent-foreground hover:translate-x-[-2px] hover:translate-y-[-2px]"
			>
				<SparklesIcon class="w-5 h-5 inline mr-2" />
				Quick Start
			</button>
			<button
				onclick={() => goto('/scenarios/builder')}
				class="brutal-btn bg-terminal-green text-void hover:translate-x-[-2px] hover:translate-y-[-2px]"
			>
				<PlusIcon class="w-5 h-5 inline mr-2" />
				New Simulation
			</button>
		</div>
	</header>

	<!-- Filters -->
	<div class="flex flex-col md:flex-row gap-4 items-center justify-between">
		<div class="flex items-center gap-2 w-full md:w-auto">
			{#each categories as cat}
				<button
					onclick={() => selectedCategory = cat}
					class="px-3 py-1 text-[10px] font-bold uppercase border-2 transition-all
						{selectedCategory === cat 
							? 'bg-foreground text-background border-foreground' 
							: 'border-transparent text-muted-foreground hover:border-muted'}"
				>
					{cat}
				</button>
			{/each}
		</div>
		<div class="relative w-full md:w-64">
			<SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="SEARCH_INDEX..."
				class="w-full pl-9 pr-4 py-2 bg-card border-2 border-border font-mono text-sm focus:outline-none focus:border-terminal-green focus:shadow-[4px_4px_0px_0px_rgba(51,255,0,1)] transition-all placeholder:text-muted-foreground/50 uppercase"
			/>
		</div>
	</div>

	<!-- Content -->
	{#if loading}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each Array(6) as _}
				<div class="h-48 brutal-card animate-pulse bg-muted/10 border-muted"></div>
			{/each}
		</div>
	{:else if error}
		<div class="p-12 text-center border-2 border-system-red bg-system-red/5 text-system-red">
			<AlertTriangleIcon class="w-12 h-12 mx-auto mb-4" />
			<h3 class="font-display text-xl uppercase">System Error</h3>
			<p class="font-mono text-sm mt-2">{error}</p>
			<button onclick={loadScenarios} class="mt-4 underline uppercase font-bold text-xs">Retry Connection</button>
		</div>
	{:else if filteredScenarios.length === 0}
		<div class="p-20 text-center border-2 border-dashed border-muted">
			<div class="relative inline-block mb-6">
				<FileTextIcon class="w-16 h-16 text-muted/20" />
				<div class="absolute -right-2 -bottom-2 w-6 h-6 bg-terminal-green rounded-full flex items-center justify-center text-void font-bold text-xs">!</div>
			</div>
			<h3 class="font-display text-2xl text-muted-foreground uppercase">No Data Found</h3>
			<p class="font-mono text-xs text-muted-foreground mt-2 mb-6">Search parameters yielded zero results.</p>
			<button
				onclick={() => goto('/scenarios/builder')}
				class="text-terminal-green font-bold uppercase text-xs hover:underline"
			>
				Initiate New Protocol
			</button>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each filteredScenarios as scenario}
				<article class="group relative brutal-card hover:border-terminal-green hover:shadow-[8px_8px_0px_0px_rgba(51,255,0,1)] transition-all duration-200 flex flex-col h-full">
					<!-- Card Header -->
					<div class="p-5 pb-0 flex justify-between items-start">
						<span class="inline-block px-2 py-0.5 text-[9px] font-bold uppercase border border-foreground {getDifficultyColor(scenario.difficulty)}">
							{scenario.difficulty}
						</span>
						<div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
							<button
								onclick={() => goto(`/scenarios/builder?id=${scenario.id}`)}
								class="p-1.5 hover:bg-terminal-green hover:text-void border border-foreground transition-colors"
								title="Edit"
							>
								<Edit2Icon class="w-3.5 h-3.5" />
							</button>
							<button
								onclick={() => deleteScenario(scenario.id)}
								class="p-1.5 hover:bg-system-red hover:text-white border border-foreground transition-colors"
								title="Delete"
							>
								<Trash2Icon class="w-3.5 h-3.5" />
							</button>
						</div>
					</div>

					<!-- Card Body -->
					<div class="p-5 flex-1">
						<h3 class="font-display text-xl uppercase leading-tight mb-2 line-clamp-2" title={scenario.name}>
							{scenario.name}
						</h3>
						<p class="font-mono text-xs text-muted-foreground line-clamp-3 mb-4 h-12">
							{scenario.description || 'No description provided.'}
						</p>
						
						<div class="flex items-center gap-2 text-[10px] font-bold uppercase text-muted-foreground">
							<span class="w-2 h-2 rounded-full {scenario.is_active ? 'bg-terminal-green' : 'bg-muted'}"></span>
							{scenario.is_active ? 'Active Protocol' : 'Archived'}
						</div>
					</div>

					<!-- Card Footer -->
					<div class="p-4 border-t-2 border-border bg-muted/5 flex justify-between items-center mt-auto">
						<span class="font-mono text-[10px] text-muted-foreground">
							{scenario.category}
						</span>
						<div class="flex items-center gap-2">
							<button
								onclick={() => goto(`/scenarios/practice?id=${scenario.id}`)}
								class="text-[10px] font-bold uppercase flex items-center gap-1 text-terminal-green hover:underline"
								title="Practice this scenario"
							>
								<ZapIcon class="w-3 h-3" /> Practice
							</button>
							<span class="text-muted-foreground">|</span>
							<button
								onclick={() => goto(`/scenarios/builder?id=${scenario.id}`)}
								class="text-[10px] font-bold uppercase flex items-center gap-1 group-hover:text-terminal-green transition-colors"
							>
								Edit <PlayIcon class="w-3 h-3" />
							</button>
						</div>
					</div>

					<!-- Scanline Effect on Hover -->
					<div class="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-10 bg-terminal-green/5 mix-blend-overlay transition-opacity"></div>
				</article>
			{/each}
		</div>
	{/if}
</div>

<!-- Template Selection Modal -->
{#if showTemplateModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-void/80 backdrop-blur-sm">
		<div class="brutal-card max-w-2xl w-full mx-4 p-6 border-terminal-green shadow-[8px_8px_0px_0px_rgba(51,255,0,1)]">
			<div class="flex items-center justify-between mb-6 border-b-2 border-foreground pb-4">
				<div class="flex items-center gap-3">
					<SparklesIcon class="w-6 h-6 text-terminal-green" />
					<h2 class="text-2xl font-display uppercase tracking-tight">Quick Start Templates</h2>
				</div>
				<button
					onclick={() => showTemplateModal = false}
					class="p-2 border-2 border-foreground hover:bg-system-red hover:text-white transition-colors"
				>
					&times;
				</button>
			</div>

			<p class="text-sm text-muted-foreground mb-6">
				Select a pre-built scenario template to instantly start practicing. These are fully configured training simulations.
			</p>

			{#if templates.length === 0}
				<div class="p-8 text-center text-muted-foreground">
					<p>Loading templates...</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each templates as template}
						<button
							onclick={() => createFromTemplate(template.id)}
							disabled={creatingFromTemplate}
							class="w-full brutal-card p-4 text-left hover:border-terminal-green hover:shadow-[4px_4px_0px_0px_rgba(51,255,0,1)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<div class="flex items-start justify-between gap-4">
								<div class="flex-1">
									<div class="flex items-center gap-2 mb-2">
										<h3 class="font-display text-lg uppercase">{template.name}</h3>
										<span class="px-2 py-0.5 text-[9px] font-bold uppercase border border-foreground {getDifficultyColor(template.difficulty)}">
											{template.difficulty}
										</span>
									</div>
									<p class="text-sm text-muted-foreground line-clamp-2">{template.description}</p>
									<span class="inline-block mt-2 text-[10px] font-bold uppercase text-muted-foreground">{template.category}</span>
								</div>
								<div class="flex-shrink-0">
									<span class="text-terminal-green text-xs font-bold uppercase">
										{creatingFromTemplate ? 'Creating...' : 'Start →'}
									</span>
								</div>
							</div>
						</button>
					{/each}
				</div>
			{/if}

			<div class="mt-6 pt-4 border-t border-muted text-center">
				<button
					onclick={() => showTemplateModal = false}
					class="text-sm text-muted-foreground hover:text-foreground"
				>
					Cancel
				</button>
			</div>
		</div>
	</div>
{/if}
