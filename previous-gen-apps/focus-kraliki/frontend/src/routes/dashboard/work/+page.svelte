<script lang="ts">
	import { onMount } from 'svelte';
	import { knowledgeStore } from '$lib/stores/knowledge';
	import { tasksStore } from '$lib/stores/tasks';
	import ManageTypesDialog from '$lib/components/knowledge/ManageTypesDialog.svelte';
	import KnowledgeItemDialog from '$lib/components/knowledge/KnowledgeItemDialog.svelte';
	import type { KnowledgeItem, ItemType } from '$lib/stores/knowledge';
	import { Plus, Settings, Sparkles, Clipboard, Calendar, CheckSquare, BookOpen, Trash2 } from 'lucide-svelte';
	import { enqueueAssistantCommand } from '$lib/utils/assistantQueue';

	type WorkView = 'knowledge' | 'tasks' | 'calendar';

	let currentView = $state<WorkView>('knowledge');
	let showManageTypesDialog = $state(false);
	let showItemDialog = $state(false);
	let editingItem = $state<KnowledgeItem | null>(null);
	let selectedTypeId = $state<string | null>(null);
	let defaultTypeId = $state<string | null>(null);
	let statusMessage = $state<string | null>(null);
	let statusTimeout = $state<ReturnType<typeof setTimeout> | null>(null);

	let storeState = $derived($knowledgeStore);
	let itemTypes = $derived(storeState.itemTypes);
	let items = $derived(storeState.items);

	let displayedTypes = $derived(selectedTypeId
		? itemTypes.filter((type) => type.id === selectedTypeId)
		: itemTypes);

	let groupedStacks = $derived(displayedTypes.map((type) => ({
		type,
		items: items.filter((item) => item.typeId === type.id).slice(0, 10)
	})));

	// Task-related state
	let tasks = $derived($tasksStore.tasks);
	let isLoadingTasks = $derived($tasksStore.isLoading);

	onMount(async () => {
		await knowledgeStore.loadItemTypes();
		await knowledgeStore.loadKnowledgeItems();
		await tasksStore.loadTasks();
	});

	function selectType(typeId: string | null) {
		selectedTypeId = typeId;
		knowledgeStore.setSelectedTypeId(typeId);
		knowledgeStore.loadKnowledgeItems(typeId ? { typeId } : undefined);
	}

	function handleCreate(typeId?: string) {
		editingItem = null;
		defaultTypeId = typeId || null;
		showItemDialog = true;
	}

	function handleEdit(item: KnowledgeItem) {
		editingItem = item;
		defaultTypeId = null;
		showItemDialog = true;
	}

	function closeItemDialog() {
		showItemDialog = false;
		editingItem = null;
		defaultTypeId = null;
	}

	function getTypeMeta(typeId: string) {
		return itemTypes.find((type) => type.id === typeId);
	}

async function copyToClipboard(item: KnowledgeItem) {
	const meta = getTypeMeta(item.typeId);
	const payload = `${meta?.name || 'Item'}: ${item.title}\n\n${item.content}`;
	try {
		await navigator.clipboard.writeText(payload);
		showStatus('Copied context to clipboard');
	} catch (error) {
		showStatus('Unable to copy. Please copy manually.');
	}
}

function sendToAssistant(item: KnowledgeItem) {
	const meta = getTypeMeta(item.typeId);
	const prompt = `You have a ${meta?.name || 'knowledge item'} titled "${item.title}". Content:\n${item.content}\n\nProvide the best next action or improvement.`;
	enqueueAssistantCommand({
		prompt,
		context: { typeId: item.typeId, itemId: item.id }
	});
	showStatus('Sent to assistant. Switch to Assistant tab to continue.');
}

function showStatus(message: string) {
	statusMessage = message;
	if (statusTimeout) clearTimeout(statusTimeout);
	statusTimeout = setTimeout(() => {
		statusMessage = null;
	}, 2000);
}
</script>

<div class="space-y-6">
	<header class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-3xl font-bold flex items-center gap-2">
				<CheckSquare class="w-8 h-8 text-primary" />
				Work Canvas
			</h1>
			<p class="text-muted-foreground">
				Manage tasks, knowledge, and calendar—all routed back through the assistant.
			</p>
		</div>
	</header>

	<!-- Tab Navigation -->
	<div class="flex gap-2 border-b border-border pb-2">
		<button
			class={`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${
				currentView === 'knowledge'
					? 'bg-primary text-primary-foreground'
					: 'text-muted-foreground hover:bg-accent/40'
			}`}
			onclick={() => currentView = 'knowledge'}
		>
			<BookOpen class="w-4 h-4" />
			Knowledge
		</button>
		<button
			class={`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${
				currentView === 'tasks'
					? 'bg-primary text-primary-foreground'
					: 'text-muted-foreground hover:bg-accent/40'
			}`}
			onclick={() => currentView = 'tasks'}
		>
			<CheckSquare class="w-4 h-4" />
			Tasks
		</button>
		<button
			class={`flex items-center gap-2 px-4 py-2 text-sm rounded-t-lg transition-colors ${
				currentView === 'calendar'
					? 'bg-primary text-primary-foreground'
					: 'text-muted-foreground hover:bg-accent/40'
			}`}
			onclick={() => currentView = 'calendar'}
		>
			<Calendar class="w-4 h-4" />
			Calendar
		</button>
	</div>

	<!-- Knowledge View -->
	{#if currentView === 'knowledge'}
		<div class="flex flex-col gap-4">
			<div class="flex justify-end gap-2">
				<button
					class="flex items-center gap-2 px-3 py-2 text-sm rounded-full border border-border hover:bg-accent/40 transition-colors"
					onclick={() => (showManageTypesDialog = true)}
				>
					<Settings class="w-4 h-4" />
					Manage types
				</button>
				<button
					class="flex items-center gap-2 px-3 py-2 text-sm rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
					onclick={() => handleCreate(selectedTypeId || undefined)}
				>
					<Plus class="w-4 h-4" />
					Add item
				</button>
			</div>

			<div class="flex gap-2 overflow-x-auto pb-2">
				<button
					class={`px-3 py-1.5 rounded-full text-sm border ${selectedTypeId === null ? 'bg-primary text-primary-foreground border-transparent' : 'border-border text-muted-foreground hover:bg-accent/40'}`}
					onclick={() => selectType(null)}
				>
					All
				</button>
				{#each itemTypes as type (type.id)}
					<button
						class={`px-3 py-1.5 rounded-full text-sm border ${selectedTypeId === type.id ? 'bg-primary text-primary-foreground border-transparent' : 'border-border text-muted-foreground hover:bg-accent/40'}`}
						onclick={() => selectType(type.id)}
					>
						{type.name}
					</button>
				{/each}
			</div>

			{#if statusMessage}
				<div class="text-xs text-muted-foreground px-2">{statusMessage}</div>
			{/if}

	{#if groupedStacks.length === 0}
		<div class="border border-dashed border-border rounded-2xl p-8 text-center text-muted-foreground">
			<p class="font-medium">No knowledge types found.</p>
			<p class="text-sm">Create a type to start capturing ideas, notes, or plans.</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each groupedStacks as stack}
				<section class="bg-card/80 border border-border rounded-2xl p-5 shadow-sm backdrop-blur">
					<div class="flex items-center justify-between mb-4">
						<div>
							<p class="text-xs uppercase tracking-wide text-muted-foreground">{stack.type.name}</p>
							<p class="text-lg font-semibold">{stack.items.length} item{stack.items.length === 1 ? '' : 's'}</p>
						</div>
						<button
							class="text-xs px-3 py-1.5 rounded-full border border-border hover:bg-accent/40 transition-colors"
							onclick={() => handleCreate(stack.type.id)}
						>
							<Plus class="w-3 h-3" />
							New {stack.type.name}
						</button>
					</div>

					{#if stack.items.length === 0}
						<p class="text-sm text-muted-foreground">No entries yet. Start by creating a {stack.type.name.toLowerCase()}.</p>
					{:else}
						<ul class="space-y-3">
							{#each stack.items as item (item.id)}
								<li class="p-3 rounded-xl border border-border hover:border-primary/40 transition-all">
									<div class="flex items-start justify-between gap-3">
										<div class="space-y-1">
											<p class="font-medium text-sm">{item.title}</p>
											<p class="text-xs text-muted-foreground line-clamp-2">{item.content}</p>
										</div>
										<div class="flex gap-1">
											<div class="flex gap-1">
												<button
													class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40"
													onclick={() => sendToAssistant(item)}
													title="Send to assistant"
												>
													<Sparkles class="w-3.5 h-3.5" />
												</button>
												<button
													class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40"
													onclick={() => copyToClipboard(item)}
													title="Copy context"
												>
													<Clipboard class="w-3.5 h-3.5" />
												</button>
												<button
													class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40"
													onclick={() => handleEdit(item)}
													title="Edit item"
												>
													✎
												</button>
											</div>
										</div>
									</div>
								</li>
							{/each}
						</ul>
					{/if}
				</section>
			{/each}
		</div>
	{/if}
		</div>
	{/if}

	<!-- Tasks View -->
	{#if currentView === 'tasks'}
		<div class="space-y-4">
			{#if isLoadingTasks}
				<div class="flex items-center justify-center h-64">
					<p class="text-muted-foreground">Loading tasks...</p>
				</div>
			{:else if tasks.length === 0}
				<div class="text-center py-16 bg-card border border-border rounded-lg">
					<p class="text-muted-foreground mb-4">No tasks found</p>
					<p class="text-sm text-muted-foreground">Visit the Tasks page or use the Assistant to create tasks.</p>
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each tasks.slice(0, 12) as task (task.id)}
						<div class="bg-card/80 border border-border rounded-2xl p-4 shadow-sm backdrop-blur hover:border-primary/40 transition-all">
							<div class="flex items-start justify-between gap-2 mb-2">
								<h3 class="font-semibold text-sm line-clamp-2">{task.title}</h3>
								<button
									class="p-1.5 rounded-full text-xs border border-border hover:bg-accent/40 transition-colors"
									onclick={() => {
										const prompt = `Review task "${task.title}" (status: ${task.status}, priority: ${task.priority}). Suggest next actions.`;
										enqueueAssistantCommand({ prompt, context: { taskId: task.id } });
										showStatus('Sent to assistant. Switch to Assistant tab.');
									}}
									title="Send to assistant"
								>
									<Sparkles class="w-3.5 h-3.5" />
								</button>
							</div>
							{#if task.description}
								<p class="text-xs text-muted-foreground line-clamp-2 mb-2">{task.description}</p>
							{/if}
							<div class="flex flex-wrap gap-1.5 text-xs">
								<span class={`px-2 py-0.5 rounded-full ${
									task.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
									task.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-700' :
									'bg-gray-100 text-gray-700'
								}`}>
									{task.status}
								</span>
								<span class={`px-2 py-0.5 rounded-full ${
									task.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
									task.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
									'bg-gray-100 text-gray-700'
								}`}>
									{task.priority}
								</span>
								{#if task.due_date}
									<span class="px-2 py-0.5 rounded-full bg-accent text-accent-foreground">
										Due {new Date(task.due_date).toLocaleDateString()}
									</span>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}

	<!-- Calendar View -->
	{#if currentView === 'calendar'}
		<div class="bg-card border border-border rounded-2xl p-8 text-center">
			<Calendar class="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
			<h3 class="text-xl font-semibold mb-2">Calendar Integration</h3>
			<p class="text-muted-foreground mb-4">View your calendar events and schedule via the dedicated Calendar page.</p>
			<a
				href="/dashboard/calendar"
				class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
			>
				<Calendar class="w-4 h-4" />
				Open Calendar
			</a>
		</div>
	{/if}
</div>

<ManageTypesDialog
	open={showManageTypesDialog}
	onClose={() => (showManageTypesDialog = false)}
/>

<KnowledgeItemDialog
	open={showItemDialog}
	item={editingItem}
	defaultTypeId={defaultTypeId}
	onClose={closeItemDialog}
/>
