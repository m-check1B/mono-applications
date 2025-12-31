<script lang="ts">
	import { onMount } from 'svelte';
	import { X, Plus, Trash2, Tag, Loader2 } from 'lucide-svelte';
	import { knowledgeStore } from '$lib/stores/knowledge';

	interface Props {
		isOpen?: boolean;
		onclose?: () => void;
	}

	let {
		isOpen = false,
		onclose
	}: Props = $props();

	let newTypeName = $state('');
	let newTypeIcon = $state('file-text'); // Default icon
	let newTypeColor = $state('#000000'); // Default color
	let isSubmitting = $state(false);

	let itemTypes = $derived($knowledgeStore.itemTypes);
	let isLoading = $derived($knowledgeStore.isLoading);

	onMount(() => {
		knowledgeStore.loadItemTypes();
	});

	function close() {
		onclose?.();
		newTypeName = '';
	}

	async function handleCreate() {
		if (!newTypeName.trim()) return;
		
		isSubmitting = true;
		const result = await knowledgeStore.createItemType({
			name: newTypeName,
			icon: newTypeIcon,
			color: newTypeColor
		});
		isSubmitting = false;

		if (result.success) {
			newTypeName = '';
		}
	}

	async function handleDelete(typeId: string) {
		if (confirm('Are you sure you want to delete this item type? Items of this type may be affected.')) {
			await knowledgeStore.deleteItemType(typeId);
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
		<div class="w-full max-w-md bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] flex flex-col max-h-[80vh]">
			<!-- Header -->
			<div class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white bg-secondary">
				<div class="flex items-center gap-3">
					<Tag class="w-6 h-6" />
					<h2 class="text-xl font-black uppercase tracking-tighter">Manage Types</h2>
				</div>
				<button onclick={close} class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
					<X class="w-6 h-6" />
				</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-6 space-y-6">
				<!-- Create New -->
				<div class="space-y-4 p-4 border-2 border-black dark:border-white bg-secondary/10">
					<h3 class="text-sm font-black uppercase">Create New Type</h3>
					<div class="flex gap-2">
						<input
							type="text"
							bind:value={newTypeName}
							placeholder="Type Name (e.g. Article)"
							class="flex-1 border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold"
							onkeydown={(e) => e.key === 'Enter' && handleCreate()}
						/>
						<button 
							class="brutal-btn bg-primary text-primary-foreground p-2"
							disabled={!newTypeName.trim() || isSubmitting}
							onclick={handleCreate}
						>
							{#if isSubmitting}
								<Loader2 class="w-4 h-4 animate-spin" />
							{:else}
								<Plus class="w-4 h-4" />
							{/if}
						</button>
					</div>
				</div>

				<!-- List -->
				<div class="space-y-2">
					<h3 class="text-sm font-black uppercase text-muted-foreground">Existing Types</h3>
					{#if itemTypes.length === 0}
						<p class="text-sm italic text-muted-foreground">No types defined.</p>
					{:else}
						{#each itemTypes as type}
							<div class="flex items-center justify-between p-3 border-2 border-black dark:border-white bg-white dark:bg-zinc-900">
								<div class="flex items-center gap-3">
									<div class="w-3 h-3 border border-black dark:border-white" style="background-color: {type.color || '#000'}"></div>
									<span class="font-bold uppercase">{type.name}</span>
								</div>
								<button 
									class="p-1.5 hover:bg-red-500 hover:text-white border border-transparent hover:border-black dark:hover:border-white transition-all"
									onclick={() => handleDelete(type.id)}
								>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
