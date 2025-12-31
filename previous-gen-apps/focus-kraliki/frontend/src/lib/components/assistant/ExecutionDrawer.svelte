<script lang="ts">
	import { assistantStore, activeExecution } from "$lib/stores/assistant";
	import { logger } from "$lib/utils/logger";
	import {
		CheckCircle2Icon as CheckCircle2,
		ClockIcon as Clock,
		AlertCircleIcon as AlertCircle,
		SparklesIcon as Sparkles,
		XIcon as X,
		Edit2Icon as Edit2,
		SaveIcon as Save,
		XCircleIcon as XCircle,
		Loader2Icon as Loader2,
	} from "lucide-svelte";
	import type { ExecutionEntry } from "$lib/stores/assistant";

	interface Props {
		open?: boolean;
		executionId?: string | null;
		onclose?: () => void;
		onsave?: (event: {
			detail: {
				entryId: string;
				updates: { title: string; content: string; status: string };
			};
		}) => void;
		ontoggleStatus?: (event: {
			detail: { entryId: string; status: string };
		}) => void;
		onsendToAssistant?: (event: {
			detail: { prompt: string; entryId: string; type: string };
		}) => void;
		ondelete?: (event: { detail: { entryId: string } }) => void;
	}

	let {
		open = $bindable(false),
		executionId = null,
		onclose,
		onsave,
		ontoggleStatus,
		onsendToAssistant,
		ondelete,
	}: Props = $props();

	let isEditing = $state(false);
	let editForm = $state({
		title: "",
		content: "",
		status: "",
	});
	let isLoading = $state(false);

	let entry = $derived(
		executionId
			? $assistantStore.executionFeed.find((e) => e.id === executionId)
			: $activeExecution,
	);

	$effect(() => {
		if (entry && !isEditing) {
			editForm = {
				title: entry.title || "",
				content: entry.content || "",
				status: entry.status || "",
			};
		}
	});

	function close() {
		assistantStore.closeExecutionDrawer();
		isEditing = false;
		onclose?.();
	}

	function handleOverlayClick(event: MouseEvent) {
		if (event.target === event.currentTarget) {
			close();
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === "Escape") {
			event.preventDefault();
			if (isEditing) {
				cancelEdit();
			} else {
				close();
			}
		}
	}

	function getStatusIcon(status: string) {
		const lower = status.toLowerCase();
		if (lower.includes("complete") || lower.includes("done"))
			return CheckCircle2;
		if (lower.includes("error") || lower.includes("fail"))
			return AlertCircle;
		if (lower.includes("progress") || lower.includes("running"))
			return Loader2;
		return Clock;
	}

	function getStatusStyles(status: string) {
		const lower = status.toLowerCase();
		if (lower.includes("complete") || lower.includes("done")) {
			return "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20 border-green-600 dark:border-green-400";
		}
		if (lower.includes("error") || lower.includes("fail")) {
			return "text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20 border-red-600 dark:border-red-400";
		}
		if (lower.includes("progress") || lower.includes("running")) {
			return "text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/20 border-blue-600 dark:border-blue-400";
		}
		return "text-muted-foreground bg-white dark:bg-black border-black dark:border-white";
	}

	function getTypeStyles(type: string) {
		switch (type) {
			case "task":
				return "bg-blue-400 text-black border-black";
			case "knowledge":
				return "bg-purple-400 text-black border-black";
			case "event":
				return "bg-green-400 text-black border-black";
			case "automation":
				return "bg-orange-400 text-black border-black";
			default:
				return "bg-white text-black border-black";
		}
	}

	function startEdit() {
		if (!entry) return;
		isEditing = true;
		editForm = {
			title: entry.title || "",
			content: entry.content || "",
			status: entry.status || "",
		};
	}

	function cancelEdit() {
		isEditing = false;
		if (entry) {
			editForm = {
				title: entry.title || "",
				content: entry.content || "",
				status: entry.status || "",
			};
		}
	}

	async function saveEdit() {
		if (!entry) return;
		if (!editForm.title.trim()) return;

		isLoading = true;
		try {
			// Update in store
			assistantStore.updateExecutionEntry(entry.id, {
				title: editForm.title.trim(),
				content: editForm.content.trim(),
				status: editForm.status,
			});

			// Call callback for external handling (e.g., API call)
			onsave?.({
				detail: {
					entryId: entry.id,
					updates: {
						title: editForm.title.trim(),
						content: editForm.content.trim(),
						status: editForm.status,
					},
				},
			});

			isEditing = false;
		} catch (error) {
			logger.error("Failed to save execution entry", error);
		} finally {
			isLoading = false;
		}
	}

	function toggleStatus() {
		if (!entry) return;

		const currentLower = entry.status.toLowerCase();
		let nextStatus = "completed";

		if (
			currentLower.includes("complete") ||
			currentLower.includes("done")
		) {
			nextStatus = "pending";
		}

		assistantStore.updateExecutionEntry(entry.id, { status: nextStatus });

		ontoggleStatus?.({
			detail: {
				entryId: entry.id,
				status: nextStatus,
			},
		});
	}

	function sendToAssistant() {
		if (!entry) return;

		const prompt = `
Review ${entry.typeLabel || entry.type}: "${entry.title}"

Status: ${entry.status}
${entry.meta ? `Meta: ${entry.meta}` : ""}
${entry.content ? `\n\nContent:\n${entry.content}` : ""}

Provide analysis and next steps.
		`.trim();

		onsendToAssistant?.({
			detail: {
				prompt,
				entryId: entry.id,
				type: entry.type,
			},
		});
		close();
	}

	function deleteEntry() {
		if (!entry) return;
		if (!confirm(`Delete this ${entry.type}?`)) return;

		assistantStore.deleteExecutionEntry(entry.id);
		ondelete?.({ detail: { entryId: entry.id } });
		close();
	}
</script>

{#if open && entry}
	{@const StatusIcon = getStatusIcon(entry.status)}
	<div
		class="absolute inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
		role="button"
		tabindex="0"
		aria-label="Close execution drawer"
		onclick={handleOverlayClick}
		onkeydown={handleKeydown}
	>
		<div
			class="brutal-card w-full sm:max-w-2xl flex flex-col max-h-[90vh] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]"
			role="dialog"
			aria-modal="true"
			aria-labelledby="execution-drawer-title"
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white"
			>
				<div class="flex items-center gap-3 flex-1">
					<div class="p-2 border-2 {getStatusStyles(entry.status)}">
						<StatusIcon
							class="w-5 h-5 {entry.status
								.toLowerCase()
								.includes('progress')
								? 'animate-spin'
								: ''}"
						/>
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 flex-wrap">
							<p
								class="text-xs font-black uppercase tracking-wide text-muted-foreground"
							>
								{entry.typeLabel || entry.type}
							</p>
							<span
								class="px-2 py-0.5 border-2 text-xs font-bold uppercase {getTypeStyles(
									entry.type,
								)}"
							>
								{entry.type}
							</span>
						</div>
						{#if !isEditing}
							<h3
								id="execution-drawer-title"
								class="text-xl font-black uppercase tracking-tighter truncate"
							>
								{entry.title}
							</h3>
						{/if}
					</div>
				</div>
				<button
					class="brutal-btn p-2 h-auto flex-shrink-0"
					onclick={close}
					aria-label="Close"
				>
					<X class="w-5 h-5" />
				</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-6 space-y-6">
				{#if isEditing}
					<!-- Edit Form -->
					<form
						onsubmit={(e: Event) => {
							e.preventDefault();
							saveEdit();
						}}
						class="space-y-4"
					>
						<div class="space-y-2">
							<label
								for="edit-title"
								class="text-sm font-black uppercase"
							>
								Title
							</label>
							<input
								id="edit-title"
								type="text"
								class="w-full px-4 py-2 border-2 border-black dark:border-white bg-background text-foreground focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all"
								bind:value={editForm.title}
								required
								disabled={isLoading}
							/>
						</div>

						{#if entry.type === "knowledge" || entry.type === "task"}
							<div class="space-y-2">
								<label
									for="edit-content"
									class="text-sm font-black uppercase"
								>
									{entry.type === "task"
										? "Description"
										: "Content"}
								</label>
								<textarea
									id="edit-content"
									class="w-full px-4 py-2 border-2 border-black dark:border-white bg-background text-foreground focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all min-h-[120px]"
									bind:value={editForm.content}
									rows="6"
									disabled={isLoading}
								></textarea>
							</div>
						{/if}

						<div class="space-y-2">
							<label
								for="edit-status"
								class="text-sm font-black uppercase"
							>
								Status
							</label>
							<select
								id="edit-status"
								class="w-full px-4 py-2 border-2 border-black dark:border-white bg-background text-foreground focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all"
								bind:value={editForm.status}
								disabled={isLoading}
							>
								<option value="pending">Pending</option>
								<option value="in_progress">In Progress</option>
								<option value="completed">Completed</option>
								<option value="error">Error</option>
							</select>
						</div>

						<div class="flex gap-3 pt-2">
							<button
								type="submit"
								class="brutal-btn bg-primary text-primary-foreground flex items-center gap-2 disabled:opacity-50"
								disabled={isLoading}
							>
								<Save class="w-4 h-4" />
								{isLoading ? "Saving..." : "Save Changes"}
							</button>
							<button
								type="button"
								class="brutal-btn bg-white text-black"
								onclick={cancelEdit}
								disabled={isLoading}
							>
								Cancel
							</button>
						</div>
					</form>
				{:else}
					<!-- View Mode -->
					<div class="space-y-4">
						<!-- Metadata -->
						<div
							class="flex flex-wrap gap-3 text-sm font-bold uppercase"
						>
							<div
								class="px-3 py-1.5 border-2 {getStatusStyles(
									entry.status,
								)}"
							>
								{entry.status}
							</div>
							<div
								class="px-3 py-1.5 bg-secondary text-secondary-foreground border-2 border-black dark:border-white"
							>
								{entry.timestamp.toLocaleString()}
							</div>
							{#if entry.meta}
								<div
									class="px-3 py-1.5 bg-white text-black border-2 border-black"
								>
									{entry.meta}
								</div>
							{/if}
						</div>

						<!-- Content -->
						{#if entry.content}
							<div
								class="p-4 border-2 border-black dark:border-white bg-secondary/20"
							>
								<p
									class="text-sm leading-relaxed whitespace-pre-wrap font-medium"
								>
									{entry.content}
								</p>
							</div>
						{/if}

						<!-- Source References -->
						{#if entry.sourceMessageId || entry.sourceWorkflowId}
							<div class="space-y-2">
								<h4
									class="text-xs font-black uppercase tracking-wide text-muted-foreground border-b-2 border-black dark:border-white pb-1 inline-block"
								>
									Source
								</h4>
								<div
									class="flex flex-wrap gap-2 text-xs font-bold uppercase"
								>
									{#if entry.sourceMessageId}
										<span
											class="px-2 py-1 bg-primary/10 text-primary border-2 border-primary/30"
										>
											Message: {entry.sourceMessageId.substring(
												0,
												8,
											)}...
										</span>
									{/if}
									{#if entry.sourceWorkflowId}
										<span
											class="px-2 py-1 bg-primary/10 text-primary border-2 border-primary/30"
										>
											Workflow: {entry.sourceWorkflowId.substring(
												0,
												8,
											)}...
										</span>
									{/if}
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Footer Actions -->
			{#if !isEditing}
				<div
					class="p-6 border-t-2 border-black dark:border-white bg-muted/30"
				>
					<div class="flex flex-wrap gap-3">
						<button
							type="button"
							class="brutal-btn bg-white text-black flex items-center gap-2"
							onclick={toggleStatus}
						>
							<CheckCircle2 class="w-4 h-4" />
							{entry.status.toLowerCase().includes("complete")
								? "Reopen"
								: "Mark Complete"}
						</button>
						<button
							type="button"
							class="brutal-btn bg-white text-black flex items-center gap-2"
							onclick={startEdit}
						>
							<Edit2 class="w-4 h-4" />
							Edit
						</button>
						<button
							type="button"
							class="brutal-btn bg-primary text-primary-foreground flex items-center gap-2"
							onclick={sendToAssistant}
						>
							<Sparkles class="w-4 h-4" />
							Send to Assistant
						</button>
						<button
							type="button"
							class="brutal-btn bg-red-500 text-white border-black flex items-center gap-2"
							onclick={deleteEntry}
						>
							<XCircle class="w-4 h-4" />
							Delete
						</button>
						<button
							type="button"
							class="brutal-btn bg-white text-black ml-auto"
							onclick={close}
						>
							Close
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}
