<script lang="ts">
	import { onMount } from 'svelte';
	import { Book, Upload, Search, FileText, Link as LinkIcon, Tag, Plus, Loader2, Settings, MoreVertical, Trash2 } from 'lucide-svelte';
	import { knowledgeStore } from '$lib/stores/knowledge';
	import { contextPanelStore } from '$lib/stores/contextPanel';
	import ItemTypeManager from './ItemTypeManager.svelte';
	import KnowledgeItemModal from './KnowledgeItemModal.svelte';
	import TypePicker from '../TypePicker.svelte';

	let searchQuery = $state('');
	let showTypeManager = $state(false);
	let showItemModal = $state(false);
	let selectedItem: any = $state(null);
	let searchTimeout: any = $state(undefined);

	let items = $derived($knowledgeStore.items);
	let itemTypes = $derived($knowledgeStore.itemTypes);
	let isLoading = $derived($knowledgeStore.isLoading);
	let selectedTypeId = $derived($knowledgeStore.selectedTypeId);

	onMount(() => {
		knowledgeStore.loadItemTypes();
		knowledgeStore.loadKnowledgeItems();
	});

	function handleSearch() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			if (searchQuery.trim()) {
				knowledgeStore.searchKnowledgeItems(searchQuery, selectedTypeId || undefined);
			} else {
				knowledgeStore.loadKnowledgeItems({ typeId: selectedTypeId || undefined });
			}
		}, 300);
	}

	function handleTypeSelect(typeId: string | null) {
		knowledgeStore.setSelectedTypeId(typeId);
		knowledgeStore.loadKnowledgeItems({ typeId: typeId || undefined });
	}

	function handleEdit(item: any) {
		selectedItem = item;
		showItemModal = true;
	}

	async function handleDelete(itemId: string, e: Event) {
		e.stopPropagation();
		if (confirm('Are you sure you want to delete this item?')) {
			await knowledgeStore.deleteKnowledgeItem(itemId);
		}
	}

	function getItemType(typeId: string) {
		return itemTypes.find(t => t.id === typeId);
	}
</script>

<div class="h-full flex flex-col relative overflow-hidden">
	<!-- Header -->
	<div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10">
		<div class="flex items-center gap-3">
			<div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">
				<Book class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">Knowledge Base</h2>
				<p class="text-sm font-bold text-muted-foreground">Create via AI · Manage via gestures</p>
			</div>
		</div>
		<button
			class="brutal-btn bg-white text-black flex items-center gap-2"
			onclick={() => showTypeManager = true}
		>
			<Settings class="w-4 h-4" />
			Types
		</button>
	</div>

	<!-- Search & Filter -->
	<div class="p-6 pb-0 space-y-4">
		<div class="relative">
			<Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground z-10" />
			<input 
				type="text" 
				bind:value={searchQuery}
				oninput={handleSearch}
				placeholder="Search knowledge..." 
				class="brutal-input pl-12 py-4 text-base"
			/>
		</div>
		
	<!-- Type Filters -->
	<div class="flex flex-wrap gap-2">
		<button 
			class="px-4 py-1.5 text-xs font-black uppercase border-2 transition-all {selectedTypeId === null ? 'bg-primary text-primary-foreground border-border shadow-brutal-sm' : 'bg-card border-border hover:bg-secondary'}"
			onclick={() => handleTypeSelect(null)}
			>
				All
			</button>
			{#each itemTypes as type}
				<button 
					class="px-4 py-1.5 text-xs font-black uppercase border-2 transition-all flex items-center gap-2 {selectedTypeId === type.id ? 'bg-primary text-primary-foreground border-border shadow-brutal-sm' : 'bg-card border-border hover:bg-secondary'}"
					onclick={() => handleTypeSelect(type.id)}
				>
					<div class="w-2.5 h-2.5" style="background-color: {type.color}; border: 1px solid currentColor;"></div>
					{type.name}
				</button>
			{/each}
	</div>

	<div class="mt-4">
		<TypePicker
			label="Share these type IDs with the assistant when creating items"
			selectedId={selectedTypeId}
			onSelect={(id) => handleTypeSelect(id)}
		/>
	</div>
</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto p-6 bg-grid-pattern">
		{#if isLoading && items.length === 0}
			<div class="h-full flex items-center justify-center">
				<div class="flex flex-col items-center gap-4">
					<Loader2 class="w-12 h-12 animate-spin text-primary" />
					<p class="font-black uppercase tracking-widest text-sm">Accessing Archive...</p>
				</div>
			</div>
		{:else if items.length === 0}
			<div class="h-full flex flex-col items-center justify-center text-center p-8">
				<div class="brutal-card p-12 max-w-md bg-background flex flex-col items-center gap-6">
					<div class="p-4 bg-secondary border-2 border-border">
						<Book class="w-16 h-16 text-muted-foreground" />
					</div>
					<div class="space-y-2">
						<h3 class="text-3xl font-black uppercase tracking-tighter">Library Empty</h3>
						<p class="text-sm font-bold uppercase text-muted-foreground tracking-wide">Ask the AI to document knowledge, ideas, or notes.</p>
					</div>
					<button 
						class="brutal-btn bg-terminal-green text-black"
						onclick={() => contextPanelStore.close()}
					>
						Start Conversation
					</button>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each items as item}
					<div
						class="brutal-card p-5 flex flex-col gap-4 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle active:translate-x-[4px] active:translate-y-[4px] active:shadow-none transition-all cursor-pointer group text-left relative"
						role="button"
						tabindex="0"
						onclick={() => handleEdit(item)}
						onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && handleEdit(item)}
					>
						<div class="flex items-start justify-between gap-4">
							<div class="p-2.5 border-2 border-border bg-secondary text-secondary-foreground flex-shrink-0">
								{#if item.item_metadata?.type === 'link'}
									<LinkIcon class="w-6 h-6" />
								{:else}
									<FileText class="w-6 h-6" />
								{/if}
							</div>
							
							<button
								class="p-2 brutal-btn bg-white dark:bg-black hover:bg-destructive hover:text-white !shadow-none hover:!shadow-brutal-sm scale-90 opacity-0 group-hover:opacity-100 transition-all"
								onclick={(e: MouseEvent) => handleDelete(item.id, e)}
							>
								<Trash2 class="w-4 h-4" />
							</button>
						</div>

						<div class="flex-1 min-w-0 space-y-2">
							<h3 class="text-xl font-black uppercase tracking-tight leading-tight group-hover:text-primary transition-colors">{item.title}</h3>
							
							<div class="flex flex-wrap items-center gap-2 mt-auto">
								{#if getItemType(item.typeId)}
									<span class="text-[10px] font-black uppercase px-2 py-0.5 border-2 border-border bg-accent text-accent-foreground shadow-brutal-sm">
										{getItemType(item.typeId)?.name}
									</span>
								{/if}
								<span class="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">
									<Tag class="w-3 h-3" />
									{new Date(item.updatedAt || Date.now()).toLocaleDateString()}
								</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<ItemTypeManager
		isOpen={showTypeManager}
		onclose={() => showTypeManager = false}
	/>

	<KnowledgeItemModal
		isOpen={showItemModal}
		item={selectedItem}
		onclose={() => showItemModal = false}
		onsaved={() => {
			knowledgeStore.loadKnowledgeItems({ typeId: selectedTypeId || undefined });
		}}
	/>
</div>
