<script lang="ts">
	import { knowledgeStore } from '$lib/stores/knowledge';
	import { Plus, Trash2, X } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		onClose?: () => void;
	}

	let {
		open = false,
		onClose = () => {}
	}: Props = $props();

	let showForm = $state(false);
	let typeName = $state('');

	let itemTypes = $derived($knowledgeStore.itemTypes);

	const defaultTypes = ['Ideas', 'Notes', 'Tasks', 'Plans'];

	function handleClose() {
		showForm = false;
		typeName = '';
		onClose();
	}

	async function handleCreateType() {
		if (!typeName.trim()) return;

		const result = await knowledgeStore.createItemType({
			name: typeName.trim(),
			icon: 'FileText',
			color: 'text-blue-500'
		});

		if (result.success) {
			typeName = '';
			showForm = false;
		}
	}

	async function handleDeleteType(typeId: string) {
		if (confirm('Are you sure? This will delete all items of this type.')) {
			await knowledgeStore.deleteItemType(typeId);
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="bg-card border border-border rounded-lg max-w-2xl w-full p-6">
			<div class="flex items-center justify-between mb-6">
				<h2 class="text-2xl font-bold">Manage Knowledge Types</h2>
				<button onclick={handleClose} class="p-2 hover:bg-accent rounded-md transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<div class="space-y-4">
				<div class="space-y-2">
					{#each itemTypes as type (type.id)}
						<div class="bg-background border border-border rounded-lg p-4 flex items-center justify-between">
							<div class="flex items-center gap-3">
								<span class="px-3 py-1 rounded-full bg-accent text-accent-foreground border border-border">
									{type.name}
								</span>
							</div>
							{#if !defaultTypes.includes(type.name)}
								<button
									onclick={() => handleDeleteType(type.id)}
									class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors"
								>
									<Trash2 class="w-4 h-4" />
								</button>
							{/if}
						</div>
					{/each}
				</div>

				{#if !showForm}
					<button
						onclick={() => (showForm = true)}
						class="w-full flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-border rounded-lg hover:border-primary hover:bg-accent/50 transition-colors"
					>
						<Plus class="w-4 h-4" />
						Add Custom Type
					</button>
				{:else}
					<div class="p-4 rounded-lg bg-accent/50 border border-border space-y-4">
						<div class="space-y-2">
							<label for="typeName" class="text-sm font-medium">Type Name</label>
							<input
								id="typeName"
								type="text"
								bind:value={typeName}
								placeholder="e.g., Projects, Goals"
								class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
							/>
						</div>

						<div class="flex gap-2">
							<button
								onclick={() => {
									showForm = false;
									typeName = '';
								}}
								class="flex-1 px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors"
							>
								Cancel
							</button>
							<button
								onclick={handleCreateType}
								disabled={!typeName.trim()}
								class="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
							>
								Create Type
							</button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
