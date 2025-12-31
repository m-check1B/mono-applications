<script lang="ts">
	import { tick } from 'svelte';
	import { knowledgeStore, type KnowledgeItem, type ItemType } from '$lib/stores/knowledge';
	import { Plus, Pencil, Trash2, CheckCircle2, Circle } from 'lucide-svelte';

	interface Props {
		selectedTypeId?: string | null;
		highlightedItemId?: string | null;
		onCreateItem?: () => void;
		editingItem?: KnowledgeItem | null;
	}

	let {
		selectedTypeId = null,
		highlightedItemId = null,
		onCreateItem = () => {},
		editingItem = $bindable(null)
	}: Props = $props();

	let items = $derived($knowledgeStore.items);
	let itemTypes = $derived($knowledgeStore.itemTypes);
	let isLoading = $derived($knowledgeStore.isLoading);

	// Scroll to highlighted item when highlightedItemId changes
	$effect(() => {
		if (highlightedItemId) {
			scrollToHighlightedItem(highlightedItemId);
		}
	});

	async function scrollToHighlightedItem(itemId: string) {
		await tick(); // Wait for DOM to update
		const element = document.getElementById(`knowledge-item-${itemId}`);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'center' });
			// Add a temporary highlight animation
			element.classList.add('highlight-pulse');
			setTimeout(() => {
				element.classList.remove('highlight-pulse');
			}, 2000);
		}
	}

	async function handleDelete(itemId: string) {
		if (confirm('Are you sure you want to delete this item?')) {
			await knowledgeStore.deleteKnowledgeItem(itemId);
		}
	}

	async function handleToggleComplete(item: KnowledgeItem) {
		await knowledgeStore.toggleKnowledgeItem(item.id);
	}

	function getItemTypeName(typeId: string): string {
		return itemTypes.find((t) => t.id === typeId)?.name || 'Unknown';
	}

	function formatDate(dateStr: string | undefined): string {
		if (!dateStr) return '';
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h2 class="text-3xl font-bold">
				{selectedTypeId ? getItemTypeName(selectedTypeId) : 'All Items'}
			</h2>
			<p class="text-muted-foreground mt-1">
				{items.length}
				{items.length === 1 ? 'item' : 'items'} in your knowledge base
			</p>
		</div>
		<button
			onclick={onCreateItem}
			class="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
		>
			<Plus class="w-5 h-5" />
			New Item
		</button>
	</div>

	{#if isLoading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full"></div>
		</div>
	{:else if items.length === 0}
		<div class="text-center py-16 bg-card border border-border rounded-lg">
			<div class="max-w-md mx-auto space-y-6">
				<div class="w-20 h-20 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center">
					<Plus class="w-10 h-10 text-primary" />
				</div>
				<div class="space-y-2">
					<h3 class="text-2xl font-bold">No items yet</h3>
					<p class="text-muted-foreground">
						Create your first item or use the AI chat to generate knowledge items automatically.
					</p>
				</div>
				<button
					onclick={onCreateItem}
					class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Create Your First Item
				</button>
			</div>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each items as item (item.id)}
				<div
					id="knowledge-item-{item.id}"
					class="bg-card border rounded-lg p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg group {highlightedItemId === item.id ? 'border-primary' : 'border-border'}"
				>
					<div class="flex items-start justify-between gap-2 mb-4">
						<span
							class="text-xs px-2 py-1 rounded-full bg-accent text-accent-foreground border border-border"
						>
							{getItemTypeName(item.typeId)}
						</span>
						<div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
							{#if getItemTypeName(item.typeId) === 'Tasks'}
								<button
									onclick={() => handleToggleComplete(item)}
									class="p-2 hover:bg-accent rounded-md transition-colors"
								>
									{#if item.completed}
										<CheckCircle2 class="w-4 h-4 text-green-500" />
									{:else}
										<Circle class="w-4 h-4" />
									{/if}
								</button>
							{/if}
							<button
								onclick={() => (editingItem = item)}
								class="p-2 hover:bg-accent rounded-md transition-colors"
							>
								<Pencil class="w-4 h-4" />
							</button>
							<button
								onclick={() => handleDelete(item.id)}
								class="p-2 hover:bg-destructive/10 hover:text-destructive rounded-md transition-colors"
							>
								<Trash2 class="w-4 h-4" />
							</button>
						</div>
					</div>

					<div class="space-y-3">
						<h3 class="font-bold text-lg leading-tight line-clamp-2">{item.title}</h3>
						<p class="text-sm text-muted-foreground leading-relaxed line-clamp-3">
							{item.content}
						</p>
					</div>

					<div
						class="flex items-center justify-between text-xs text-muted-foreground pt-3 mt-3 border-t border-border"
					>
						<span>{formatDate(item.createdAt)}</span>
						{#if item.completed}
							<span class="px-2 py-1 rounded-full bg-green-500/10 text-green-600 border border-green-500/30">
								Done
							</span>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* Highlight pulse animation for cited knowledge items */
	:global(.highlight-pulse) {
		animation: highlightPulse 2s ease-in-out;
	}

	@keyframes highlightPulse {
		0%,
		100% {
			box-shadow: 0 0 0 0 hsl(var(--primary) / 0);
		}
		50% {
			box-shadow: 0 0 0 8px hsl(var(--primary) / 0.2);
		}
	}
</style>
