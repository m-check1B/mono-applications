<script lang="ts">
	import { assistantStore, activeWorkflow } from "$lib/stores/assistant";
	import {
		HistoryIcon as History,
		CheckCircle2Icon as CheckCircle2,
		ClockIcon as Clock,
		AlertCircleIcon as AlertCircle,
		SparklesIcon as Sparkles,
		XIcon as X,
		Loader2Icon as Loader2,
	} from "lucide-svelte";
	import type {
		WorkflowPlan,
		WorkflowStep,
		WorkflowArtifact,
	} from "$lib/stores/assistant";

	interface Props {
		open?: boolean;
		workflowId?: string | null;
		onapprove?: (event: any) => void;
		onrevise?: (event: any) => void;
		onreject?: (event: any) => void;
		oninspectArtifact?: (event: any) => void;
		onsendToAssistant?: (event: any) => void;
		onclose?: () => void;
	}

	let {
		open = $bindable(false),
		workflowId = null,
		onapprove,
		onrevise,
		onreject,
		oninspectArtifact,
		onsendToAssistant,
		onclose,
	}: Props = $props();

	let workflow = $derived(
		workflowId && $assistantStore.workflows[workflowId]
			? $assistantStore.workflows[workflowId]
			: $activeWorkflow,
	);

	function close() {
		assistantStore.closeWorkflowDrawer();
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
			close();
		}
	}

	function getStepIcon(step: WorkflowStep) {
		switch (step.status) {
			case "completed":
				return CheckCircle2;
			case "running":
				return Loader2;
			case "error":
				return AlertCircle;
			default:
				return Clock;
		}
	}

	function getStepStyles(step: WorkflowStep) {
		switch (step.status) {
			case "completed":
				return "text-green-600 dark:text-green-400 border-green-600 dark:border-green-400 bg-green-100 dark:bg-green-900/20";
			case "running":
				return "text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400 bg-blue-100 dark:bg-blue-900/20";
			case "error":
				return "text-red-600 dark:text-red-400 border-red-600 dark:border-red-400 bg-red-100 dark:bg-red-900/20";
			default:
				return "text-muted-foreground border-black dark:border-white bg-white dark:bg-black";
		}
	}

	function getDecisionStyles(status: string) {
		switch (status) {
			case "approved":
				return "bg-green-400 text-black border-black";
			case "revise":
				return "bg-yellow-400 text-black border-black";
			case "rejected":
				return "bg-red-400 text-black border-black";
			default:
				return "bg-white text-black border-black";
		}
	}

	function approveWorkflow() {
		if (!workflow) return;
		assistantStore.updateWorkflowDecision(workflow.id, "approved");
		onapprove?.({ detail: { workflowId: workflow.id } });
	}

	function requestRevision() {
		if (!workflow) return;
		assistantStore.updateWorkflowDecision(workflow.id, "revise");
		onrevise?.({ detail: { workflowId: workflow.id } });
	}

	function rejectWorkflow() {
		if (!workflow) return;
		assistantStore.updateWorkflowDecision(workflow.id, "rejected");
		onreject?.({ detail: { workflowId: workflow.id } });
	}

	function inspectArtifact(artifact: WorkflowArtifact) {
		oninspectArtifact?.({ detail: { artifact, workflowId: workflow?.id } });
	}

	function sendToAssistant() {
		if (!workflow) return;
		const summary = `
Review workflow: ${workflow.mainTask?.title || "Untitled workflow"}

Steps:
${workflow.workflow?.map((s) => `${s.step}. ${s.action} (${s.estimatedMinutes || "?"} min)`).join("\n") || "No steps"}

Confidence: ${workflow.confidence !== undefined ? workflow.confidence.toFixed(2) : "N/A"}
		`.trim();

		onsendToAssistant?.({
			detail: {
				prompt: summary,
				workflowId: workflow.id,
			},
		});
		close();
	}
</script>

{#if open && workflow}
	<div
		class="absolute inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
		role="button"
		tabindex="0"
		aria-label="Close workflow drawer"
		onclick={handleOverlayClick}
		onkeydown={handleKeydown}
	>
		<div
			class="brutal-card w-full sm:max-w-2xl flex flex-col max-h-[90vh] shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]"
			role="dialog"
			aria-modal="true"
			aria-labelledby="workflow-drawer-title"
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white"
			>
				<div class="flex items-center gap-3">
					<div
						class="p-2 border-2 border-black dark:border-white bg-primary text-primary-foreground"
					>
						<History class="w-5 h-5" />
					</div>
					<div>
						<p
							class="text-xs font-black uppercase tracking-wide text-muted-foreground"
						>
							Workflow Plan
						</p>
						<h3
							id="workflow-drawer-title"
							class="text-xl font-black uppercase tracking-tighter"
						>
							{workflow.mainTask?.title || "Untitled Workflow"}
						</h3>
					</div>
				</div>
				<button
					class="brutal-btn p-2 h-auto"
					onclick={close}
					aria-label="Close"
				>
					<X class="w-5 h-5" />
				</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-6 space-y-6">
				<!-- Metadata -->
				<div class="flex flex-wrap gap-3 text-sm font-bold uppercase">
					{#if workflow.confidence !== undefined}
						<div
							class="px-3 py-1.5 bg-white text-black border-2 border-black"
						>
							Confidence: {(workflow.confidence * 100).toFixed(
								0,
							)}%
						</div>
					{/if}
					{#if workflow.decisionStatus}
						<div
							class="px-3 py-1.5 border-2 {getDecisionStyles(
								workflow.decisionStatus,
							)}"
						>
							{workflow.decisionStatus}
						</div>
					{/if}
					<div
						class="px-3 py-1.5 bg-secondary text-secondary-foreground border-2 border-black dark:border-white"
					>
						{workflow.timestamp.toLocaleString()}
					</div>
				</div>

				<!-- Description -->
				{#if workflow.mainTask?.description}
					<div
						class="p-4 border-2 border-black dark:border-white bg-secondary/20"
					>
						<p class="text-sm leading-relaxed font-medium">
							{workflow.mainTask.description}
						</p>
					</div>
				{/if}

				<!-- Steps -->
				{#if workflow.workflow && workflow.workflow.length > 0}
					<div class="space-y-4">
						<h4
							class="text-sm font-black uppercase tracking-wide flex items-center gap-2 border-b-2 border-black dark:border-white pb-2"
						>
							<Clock class="w-4 h-4" />
							Execution Steps
						</h4>
						<div class="space-y-3">
							{#each workflow.workflow as step}
								{@const Icon = getStepIcon(step)}
								<div
									class="p-4 border-2 transition-all {getStepStyles(
										step,
									)} shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
								>
									<div class="flex items-start gap-3">
										<div class="flex-shrink-0 mt-0.5">
											<Icon
												class="w-5 h-5 {step.status ===
												'running'
													? 'animate-spin'
													: ''}"
											/>
										</div>
										<div class="flex-1 space-y-1">
											<div
												class="flex items-center justify-between gap-2"
											>
												<p class="font-bold uppercase">
													Step {step.step}
												</p>
												{#if step.estimatedMinutes}
													<span
														class="text-xs px-2 py-0.5 bg-white dark:bg-black border border-current font-mono"
													>
														{step.estimatedMinutes} min
													</span>
												{/if}
											</div>
											<p class="text-sm font-medium">
												{step.action}
											</p>
											{#if step.result}
												<div
													class="mt-2 p-2 border border-current bg-white/50 dark:bg-black/50 font-mono text-xs"
												>
													<p>
														Result: {typeof step.result ===
														"string"
															? step.result
															: JSON.stringify(
																	step.result,
																)}
													</p>
												</div>
											{/if}
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Artifacts -->
				{#if workflow.artifacts && workflow.artifacts.length > 0}
					<div class="space-y-4">
						<h4
							class="text-sm font-black uppercase tracking-wide flex items-center gap-2 border-b-2 border-black dark:border-white pb-2"
						>
							<Sparkles class="w-4 h-4" />
							Artifacts
						</h4>
						<div class="space-y-3">
							{#each workflow.artifacts as artifact}
								<div
									class="p-4 border-2 border-black dark:border-white bg-card transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
								>
									<div
										class="flex items-start justify-between gap-3"
									>
										<div class="flex-1">
											<p
												class="font-bold text-sm uppercase"
											>
												{artifact.label ||
													artifact.title ||
													artifact.name ||
													"Artifact"}
											</p>
											{#if artifact.summary || artifact.description}
												<p
													class="text-xs text-muted-foreground mt-1 font-medium"
												>
													{artifact.summary ||
														artifact.description}
												</p>
											{/if}
											{#if artifact.type}
												<span
													class="inline-block mt-2 px-2 py-0.5 border border-black dark:border-white bg-secondary text-xs font-bold uppercase"
												>
													{artifact.type}
												</span>
											{/if}
										</div>
										<div class="flex flex-col gap-2">
											{#if artifact.url}
												<a
													href={artifact.url}
													target="_blank"
													rel="noreferrer"
													class="brutal-btn text-xs text-center bg-white text-black"
												>
													Open
												</a>
											{/if}
											<button
												type="button"
												class="brutal-btn text-xs bg-primary text-primary-foreground"
												onclick={() =>
													inspectArtifact(artifact)}
											>
												Inspect
											</button>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>

			<!-- Footer Actions -->
			<div
				class="p-6 border-t-2 border-black dark:border-white bg-muted/30"
			>
				<div class="flex flex-wrap gap-3">
					{#if !workflow.decisionStatus || workflow.decisionStatus === "pending"}
						<button
							type="button"
							class="brutal-btn bg-green-500 text-black border-black"
							onclick={approveWorkflow}
						>
							Approve Plan
						</button>
						<button
							type="button"
							class="brutal-btn bg-yellow-400 text-black border-black"
							onclick={requestRevision}
						>
							Request Changes
						</button>
						<button
							type="button"
							class="brutal-btn bg-red-500 text-white border-black"
							onclick={rejectWorkflow}
						>
							Reject
						</button>
					{/if}
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
						class="brutal-btn bg-white text-black ml-auto"
						onclick={close}
					>
						Close
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
