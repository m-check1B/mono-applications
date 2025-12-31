<script lang="ts">
	import { onMount } from "svelte";
	import { flip } from "svelte/animate";
	import { dndzone } from "svelte-dnd-action";
	import type { DndEvent } from "svelte-dnd-action";
	// Note: svelte-gestures removed due to Svelte 5 type incompatibility
	// Mobile swipe interactions use long-press + action buttons instead
	import { knowledgeStore } from "$lib/stores/knowledge";
	import { workspacesStore } from "$lib/stores/workspaces";
	import { contextPanelStore } from "$lib/stores/contextPanel";
	import { toast } from "$lib/stores/toast";
	import { enqueueAssistantCommand } from "$lib/utils/assistantQueue";
	import {
		Plus,
		Search,
		Trash2,
		Check,
		Clock,
		Circle,
		Sparkles,
		ClipboardList,
		Filter,
		X,
		Calendar,
		User,
		Loader2,
		GripVertical,
	} from "lucide-svelte";
	import { logger } from "$lib/utils/logger";

	// State
	let searchQuery = $state("");
	let filterStatus: string = $state("ALL");
	let filterPriority: string = $state("ALL");
	let selectedWorkspaceId: string | null = $state(null);
	let tasksTypeId: string | null = $state(null);

	// DND State
	let displayedTasks: any[] = $state([]);
	let isDragging = $state(false);

	// Reactive
	let items = $derived($knowledgeStore.items);
	let itemTypes = $derived($knowledgeStore.itemTypes);
	let isLoading = $derived($knowledgeStore.isLoading);
	let workspaceState = $derived($workspacesStore);
	let workspaceMembers = $derived(workspaceState.members);

	// Filter tasks client-side
	let tasks = $derived(
		items.filter((item) => {
			// Only show items of 'Tasks' type (if we found the ID)
			if (tasksTypeId && item.typeId !== tasksTypeId) return false;

			const meta = item.item_metadata || {};

			// Filter by Workspace (stored in metadata)
			if (selectedWorkspaceId) {
				if (
					meta.workspaceId &&
					meta.workspaceId !== selectedWorkspaceId
				)
					return false;
			}

			// Filter by Status
			if (filterStatus !== "ALL") {
				if (filterStatus === "COMPLETED") {
					if (!item.completed) return false;
				} else {
					if (item.completed) return false;
					// Check metadata status for granularity (IN_PROGRESS vs PENDING)
					if (meta.status && meta.status !== filterStatus)
						return false;
				}
			}

			// Filter by Priority
			if (filterPriority !== "ALL") {
				if (meta.priority !== filterPriority) return false;
			}

			// Filter by Search
			if (searchQuery) {
				const q = searchQuery.toLowerCase();
				return (
					item.title.toLowerCase().includes(q) ||
					(item.content || "").toLowerCase().includes(q)
				);
			}

			return true;
		}),
	);

	// Sync displayedTasks with tasks, but respect DND
	$effect(() => {
		if (!isDragging) {
			displayedTasks = [...tasks];
		}
	});

	onMount(async () => {
		await workspacesStore.loadWorkspaces();
		if (workspaceState.activeWorkspaceId) {
			selectedWorkspaceId = workspaceState.activeWorkspaceId;
			await workspacesStore.loadMembers(selectedWorkspaceId);
		}

		// Load types to find "Tasks"
		await knowledgeStore.loadItemTypes();

		// Find 'Tasks' or 'Task' type
		const taskType = $knowledgeStore.itemTypes.find(
			(t) =>
				t.name.toLowerCase() === "tasks" ||
				t.name.toLowerCase() === "task",
		);

		if (taskType) {
			tasksTypeId = taskType.id;
			// Load items of this type
			await knowledgeStore.loadKnowledgeItems({ typeId: tasksTypeId });
		} else {
			logger.warn('[TasksView] "Tasks" item type not found.');
		}
	});

	// DND Handlers
	function handleDndConsider(e: CustomEvent<DndEvent<any>>) {
		displayedTasks = e.detail.items;
		isDragging = true;
	}

	function handleDndFinalize(e: CustomEvent<DndEvent<any>>) {
		displayedTasks = e.detail.items;
		isDragging = false;
		// Note: In a real app, we would persist the new order here
		// e.g. await knowledgeStore.updateTaskOrder(displayedTasks.map(t => t.id));
	}

	async function handleToggleTask(item: any) {
		const newCompleted = !item.completed;
		// Also update status in metadata
		const meta = {
			...item.item_metadata,
			status: newCompleted ? "COMPLETED" : "PENDING",
		};

		await knowledgeStore.updateKnowledgeItem(item.id, {
			completed: newCompleted,
			item_metadata: meta,
		});
	}

	// Delete with undo support
	async function handleDeleteTask(itemId: string) {
		// Store deleted item for undo
		const item = items.find((i) => i.id === itemId);
		if (!item) return;

		const deletedItem = { ...item };

		// Delete optimistically
		await knowledgeStore.deleteKnowledgeItem(itemId);

		// Show success with undo button
		toast.successWithUndo(
			`Deleted "${deletedItem.title}"`,
			async () => {
				// Undo: recreate the item
				await knowledgeStore.createKnowledgeItem({
					typeId: deletedItem.typeId,
					title: deletedItem.title,
					content: deletedItem.content,
					item_metadata: deletedItem.item_metadata,
				});
			},
			6000, // 6 seconds to undo
		);
	}

	// Keyboard Handler
	function handleKeydown(event: KeyboardEvent, task: any) {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			handleToggleTask(task);
		} else if (event.key === "Delete" || event.key === "Backspace") {
			event.preventDefault();
			handleDeleteTask(task.id);
		}
	}

	// Handler factory for keyboard events
	function getKeydownHandler(task: any) {
		return (e: KeyboardEvent) => handleKeydown(e, task);
	}

	function sendTaskToAssistant(item: any) {
		const prompt = `Review task "${item.title}" (completed: ${item.completed}).\nDescription: ${item.content || "None"}\n\nSuggest next steps.`;
		enqueueAssistantCommand({
			prompt,
			context: {
				itemId: item.id,
				type: "knowledge_item",
				subType: "task",
			},
		});
	}

	function getPriorityColor(priority: string) {
		switch (priority) {
			case "HIGH":
				return "bg-destructive text-destructive-foreground";
			case "MEDIUM":
				return "bg-accent text-accent-foreground";
			default:
				return "bg-muted text-muted-foreground";
		}
	}

	function formatDueDate(dateStr: string) {
		if (!dateStr) return "";
		return new Date(dateStr).toLocaleDateString();
	}
</script>

<div class="h-full flex flex-col relative overflow-hidden bg-background">
	<!-- Header -->
	<div
		class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex flex-col gap-4 bg-background z-10"
	>
		<div class="flex items-center gap-3">
			<div
				class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground"
			>
				<ClipboardList class="w-6 h-6" />
			</div>
			<div>
				<h2 class="text-2xl font-black uppercase tracking-tighter">
					Tasks
				</h2>
				<p class="text-sm font-bold text-muted-foreground">
					Create via AI · Manage via gestures
				</p>
			</div>
		</div>

		<!-- Filters -->
		<div class="flex flex-wrap gap-3">
			<div class="flex-1 min-w-[200px] relative">
				<Search
					class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground z-10"
				/>
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search tasks..."
					class="brutal-input pl-10"
				/>
			</div>

			<select
				bind:value={filterStatus}
				class="brutal-input w-auto min-w-[140px] appearance-none cursor-pointer"
			>
				<option value="ALL">All Status</option>
				<option value="PENDING">Pending</option>
				<option value="IN_PROGRESS">In Progress</option>
				<option value="COMPLETED">Completed</option>
			</select>

			<select
				bind:value={filterPriority}
				class="brutal-input w-auto min-w-[140px] appearance-none cursor-pointer"
			>
				<option value="ALL">All Priority</option>
				<option value="HIGH">High</option>
				<option value="MEDIUM">Medium</option>
				<option value="LOW">Low</option>
			</select>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto p-6 bg-grid-pattern">
		{#if isLoading && tasks.length === 0}
			<div class="h-full flex items-center justify-center">
				<div class="flex flex-col items-center gap-4">
					<Loader2 class="w-12 h-12 animate-spin text-primary" />
					<p class="font-black uppercase tracking-widest text-sm">Synchronizing...</p>
				</div>
			</div>
		{:else if displayedTasks.length === 0}
			<div
				class="h-full flex flex-col items-center justify-center text-center p-8"
			>
				<div class="brutal-card p-12 max-w-md bg-background flex flex-col items-center gap-6">
					<div class="p-4 bg-secondary border-2 border-border">
						<ClipboardList class="w-16 h-16 text-muted-foreground" />
					</div>
					<div class="space-y-2">
						<h3 class="text-3xl font-black uppercase tracking-tighter">
							Void Detected
						</h3>
						<p class="text-sm font-bold uppercase text-muted-foreground tracking-wide">
							No tasks match your current configuration or the queue is empty.
						</p>
					</div>
					
					{#if !tasksTypeId}
						<div class="p-3 bg-red-100 dark:bg-red-900/30 border-2 border-red-500 text-red-500 text-xs font-bold uppercase">
							CRITICAL: "Tasks" item type not found in database.
						</div>
					{:else}
						<button 
							class="brutal-btn bg-terminal-green text-black"
							onclick={() => contextPanelStore.close()}
						>
							Ask AI to Create Task
						</button>
					{/if}
				</div>
			</div>
		{:else}
			<div
				class="space-y-4"
				use:dndzone={{
					items: displayedTasks,
					flipDurationMs: 200,
					dropTargetStyle: {},
				}}
				onconsider={handleDndConsider}
				onfinalize={handleDndFinalize}
			>
				{#each displayedTasks as task (task.id)}
					<div
						animate:flip={{ duration: 200 }}
						role="button"
						tabindex="0"
						onkeydown={getKeydownHandler(task)}
						class="brutal-card p-4 flex gap-4 group hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all outline-none focus:ring-2 focus:ring-terminal-green active:translate-x-[4px] active:translate-y-[4px] active:shadow-none"
					>
						<!-- Drag Handle (Desktop) -->
						<div
							class="hidden md:flex items-center justify-center cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground border-r-2 border-border/10 pr-2"
						>
							<GripVertical class="w-4 h-4" />
						</div>

						<!-- Status Checkbox -->
						<button
							onclick={(e: MouseEvent) => {
								e.stopPropagation();
								handleToggleTask(task);
							}}
							class="mt-1 w-7 h-7 flex-shrink-0 border-2 border-black dark:border-white flex items-center justify-center hover:bg-terminal-green transition-colors
							{task.completed ? 'bg-terminal-green text-black' : 'bg-card'}"
							tabindex="-1"
						>
							{#if task.completed}
								<Check class="w-5 h-5 stroke-[3]" />
							{:else if task.item_metadata?.status === "IN_PROGRESS"}
								<div class="w-3 h-3 bg-primary animate-pulse"></div>
							{/if}
						</button>

						<div class="flex-1 min-w-0 space-y-3 select-none">
							<div class="flex items-start justify-between gap-4">
								<h3
									class="text-xl font-black uppercase leading-tight tracking-tight {task.completed
										? 'line-through opacity-40'
										: ''}"
								>
									{task.title}
								</h3>

								<div
									class="flex items-center gap-1 opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity"
								>
									<button
										onclick={(e: MouseEvent) => {
											e.stopPropagation();
											sendTaskToAssistant(task);
										}}
										class="p-2 brutal-btn bg-white dark:bg-black !shadow-none hover:!shadow-brutal-sm scale-90"
										title="Ask Assistant"
										tabindex="-1"
									>
										<Sparkles class="w-4 h-4" />
									</button>
									<button
										onclick={(e: MouseEvent) => {
											e.stopPropagation();
											handleDeleteTask(task.id);
										}}
										class="p-2 brutal-btn bg-white dark:bg-black hover:bg-destructive hover:text-white !shadow-none hover:!shadow-brutal-sm scale-90"
										title="Delete"
										tabindex="-1"
									>
										<Trash2 class="w-4 h-4" />
									</button>
								</div>
							</div>

							{#if task.content}
								<p
									class="text-sm font-medium text-muted-foreground line-clamp-2 leading-relaxed"
								>
									{task.content}
								</p>
							{/if}

							<div
								class="flex flex-wrap items-center gap-3 text-[10px] font-black uppercase tracking-widest"
							>
								<span
									class="px-2 py-0.5 border-2 border-border {getPriorityColor(
										task.item_metadata?.priority,
									)}"
								>
									{task.item_metadata?.priority || "MEDIUM"}
								</span>
								{#if task.item_metadata?.dueDate}
									<span
										class="flex items-center gap-1.5 px-2 py-0.5 border-2 border-border bg-secondary"
									>
										<Calendar class="w-3.5 h-3.5" />
										{formatDueDate(
											task.item_metadata.dueDate,
										)}
									</span>
								{/if}
								{#if task.item_metadata?.assignedUserId}
									<span
										class="flex items-center gap-1.5 px-2 py-0.5 border-2 border-border bg-secondary"
									>
										<User class="w-3.5 h-3.5" />
										Assigned
									</span>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
