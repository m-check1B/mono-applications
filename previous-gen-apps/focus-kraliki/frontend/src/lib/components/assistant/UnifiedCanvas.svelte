<script lang="ts">
	/**
	 * UnifiedCanvas - AI-First Command Center Canvas
	 * Streams voice, text, and II-Agent events into unified conversation
	 */
	import { onMount, onDestroy } from "svelte";
	import {
		assistantStore,
		latestWorkflow,
		isProcessing,
	} from "$lib/stores/assistant";
	import { contextPanelStore } from "$lib/stores/contextPanel";
	import { IIAgentClient } from "$lib/agent/iiAgentClient";
	import { EventType } from "$lib/agent/types";
	import type { RealtimeEvent, AgentConfig } from "$lib/agent/types";
	import { api } from "$lib/api/client";
	import { tasksStore } from "$lib/stores/tasks";
	import { knowledgeStore } from "$lib/stores/knowledge";
	import { projectsStore } from "$lib/stores/projects";
	import { settingsStore } from "$lib/stores/settings";
	import { calendarStore } from "$lib/stores/calendar";
	import { timeStore } from "$lib/stores/time";
	import { analyticsStore } from "$lib/stores/analytics";
	import { workflowStore } from "$lib/stores/workflow";
	import { workspacesStore } from "$lib/stores/workspaces";
	import { setMode } from "mode-watcher";
	import { logger } from "$lib/utils/logger";
	import type { AssistantMessage } from "$lib/stores/assistant";
	import MarkdownRenderer from "$lib/components/MarkdownRenderer.svelte";
	import AssistantComposer from "./AssistantComposer.svelte";
	import WorkflowDrawer from "./WorkflowDrawer.svelte";
	import ExecutionDrawer from "./ExecutionDrawer.svelte";
	import { toast } from "$lib/stores/toast";
	import {
		BotIcon as Bot,
		UserIcon as User,
		Loader2Icon as Loader2,
		SparklesIcon as Sparkles,
		BrainIcon as Brain,
		WrenchIcon as Wrench,
		HistoryIcon as History,
		AlertTriangleIcon as AlertTriangle,
	} from "lucide-svelte";

	// Props interface
	interface Props {
		title?: string;
		subtitle?: string;
		inputMessage?: string;
		quickPrompts?: string[];
		isRecording?: boolean;
		isProcessingAudio?: boolean;
		supportsRecording?: boolean;
		voiceProvider?: string;
		voiceStatus?: { providers: Record<string, boolean> } | null;
		recordingError?: string | null;
		uploadError?: string | null;
		models?: Array<{ label: string; value: string }>;
		onsend?: (event: { detail: { message: string } }) => void;
		onrecord?: () => void;
		onstop?: () => void;
		onupload?: (event: any) => void;
		onprovider?: (event: any) => void;
		onrequestIIAgentSession?: () => void;
		onworkflowApprove?: (event: any) => void;
		onworkflowRevise?: (event: any) => void;
		onexecutionSave?: (event: any) => void;
	}

	let {
		title = "Command Center",
		subtitle = "Unified AI assistant with voice, text, and workflow orchestration",
		inputMessage = $bindable(""),
		quickPrompts = [],
		isRecording = false,
		isProcessingAudio = false,
		supportsRecording = false,
		voiceProvider = "gemini-native",
		voiceStatus = null,
		recordingError = null,
		uploadError = null,
		models = [],
		onsend,
		onrecord,
		onstop,
		onupload,
		onprovider,
		onrequestIIAgentSession,
		onworkflowApprove,
		onworkflowRevise,
		onexecutionSave,
	}: Props = $props();

	// Local state
	let container: HTMLDivElement | undefined = $state();
	let iiAgentClient: IIAgentClient | null = $state(null);
	let unsubscribeEvent: (() => void) | null = $state(null);
	let unsubscribeError: (() => void) | null = $state(null);
	let unsubscribeClose: (() => void) | null = $state(null);
	let streamingMessageId: string | null = $state(null);
	const focusSystemHint = `You are the Focus by Kraliki AI. Drive everything through tools and keep chat central.
Tools you may see: knowledge (any user-defined type: Task, Idea, Plan, Note, Goal, custom), tasks (Task type only), projects, events/calendar, time tracking (start/stop/list timers), workflows (list/execute templates), analytics, workspaces (list/switch), settings (preferences like theme), infra (status/logs), file search.
Rules:
- Tasks are just one predefined type; users can add/rename types. If you create/update an item, ensure you have the correct typeId or ask for it. Use task tool only for Task type; otherwise use knowledge item with the right typeId.
- When you use a tool, briefly tell the user which panel to open (e.g., "Opening Tasks panel to review" / "Showing Calendar panel") so the UI can react.
- Prefer tool calls over speculation; one tool at a time; if missing data, ask concise clarifications.`;

	// Reactive state from store
	let messages = $derived($assistantStore.messages);
	let composerMode = $derived($assistantStore.composerState.mode);
	let selectedModel = $derived(
		$assistantStore.composerState.model || "google/gemini-3-flash-preview",
	);
	let iiAgentConnected = $derived(
		$assistantStore.iiAgentState.isConnected &&
			$assistantStore.iiAgentState.isInitialized,
	);
	let iiAgentError = $derived($assistantStore.iiAgentState.error);
	let workflowDrawerOpen = $derived(
		$assistantStore.drawerState.workflowDrawerOpen,
	);
	let executionDrawerOpen = $derived(
		$assistantStore.drawerState.executionDrawerOpen,
	);

	export function scrollToBottom() {
		if (container) container.scrollTop = container.scrollHeight;
	}

	onMount(() => {
		// Initialize II-Agent client
		iiAgentClient = new IIAgentClient();

		// Set up event listeners
		if (iiAgentClient) {
			unsubscribeEvent = iiAgentClient.onEvent(handleIIAgentEvent);
			unsubscribeError = iiAgentClient.onError(handleIIAgentError);
			unsubscribeClose = iiAgentClient.onClose(handleIIAgentClose);
		}

		// Auto-scroll on message updates
		scrollToBottom();
	});

	onDestroy(() => {
		// Clean up event listeners
		if (unsubscribeEvent) unsubscribeEvent();
		if (unsubscribeError) unsubscribeError();
		if (unsubscribeClose) unsubscribeClose();

		// Disconnect II-Agent
		if (iiAgentClient) {
			iiAgentClient.disconnect();
		}
	});

	// ========== II-Agent Event Handlers ==========

	function handleIIAgentEvent(event: RealtimeEvent) {
		// Log event to store
		assistantStore.addIIAgentEvent(event);

		switch (event.type) {
			case EventType.CONNECTION_ESTABLISHED:
				assistantStore.setIIAgentConnection(true);
				break;

			case EventType.AGENT_INITIALIZED:
				assistantStore.setIIAgentInitialized(
					true,
					event.content.model_name,
				);
				break;

			case EventType.PROCESSING:
				assistantStore.setIIAgentProcessing(true);
				break;

			case EventType.AGENT_THINKING:
				handleThinkingEvent(event);
				break;

			case EventType.AGENT_RESPONSE:
				handleResponseEvent(event);
				break;

			case EventType.TOOL_CALL:
				handleToolCallEvent(event);
				break;

			case EventType.TOOL_RESULT:
				handleToolResultEvent(event);
				break;

			case EventType.STREAM_COMPLETE:
				handleStreamComplete(event);
				break;

			case EventType.ERROR:
				handleErrorEvent(event);
				break;

			case EventType.WORKSPACE_INFO:
				logger.info("[UnifiedCanvas] Workspace info:", { content: event.content });
				break;

			default:
				logger.info(
					"[UnifiedCanvas] Unhandled event:",
					{ type: event.type, content: event.content },
				);
		}

		scrollToBottom();
	}

	function handleThinkingEvent(event: RealtimeEvent) {
		const thinking =
			event.content.thinking || event.content.text || "Thinking...";

		// Create or update thinking message
		if (streamingMessageId) {
			assistantStore.updateMessage(streamingMessageId, {
				metadata: { thinking },
			});
		} else {
			const msg = assistantStore.addMessage({
				role: "assistant",
				content: "",
				source: "ii-agent",
				metadata: { thinking },
			});
			streamingMessageId = msg.id;
		}
	}

	function handleResponseEvent(event: RealtimeEvent) {
		const text = event.content.text || event.content.content || "";

		if (streamingMessageId) {
			// Append to existing message
			const currentMsg = messages.find(
				(m) => m.id === streamingMessageId,
			);
			const currentContent = currentMsg?.content || "";
			assistantStore.updateMessage(streamingMessageId, {
				content: currentContent + text,
				metadata: { ...currentMsg?.metadata, thinking: undefined },
			});
		} else {
			// Create new message
			const msg = assistantStore.addMessage({
				role: "assistant",
				content: text,
				source: "ii-agent",
			});
			streamingMessageId = msg.id;
		}
	}

	function handleToolCallEvent(event: RealtimeEvent) {
		const toolName =
			event.content.tool_name || event.content.name || "unknown";
		const toolArgs = event.content.arguments || event.content.args || {};

		// Orchestrate UI based on tool calls
		const name = toolName.toLowerCase();
		if (name.includes("infra") || name.includes("log")) {
			contextPanelStore.open("infra");
		} else if (
			name.includes("task") ||
			name.includes("knowledge") ||
			name.includes("item")
		) {
			// Unified: tasks are now knowledge items, all open knowledge panel
			contextPanelStore.open("knowledge");
		} else if (name.includes("project")) {
			contextPanelStore.open("projects");
		} else if (name.includes("setting") || name.includes("preference")) {
			contextPanelStore.open("settings");
		} else if (name.includes("event") || name.includes("calendar")) {
			contextPanelStore.open("calendar");
		} else if (name.includes("time") || name.includes("timer")) {
			contextPanelStore.open("time");
		} else if (name.includes("workflow")) {
			contextPanelStore.open("workflow");
		} else if (name.includes("analytic")) {
			contextPanelStore.open("analytics");
		} else if (name.includes("workspace")) {
			contextPanelStore.open("projects"); // show projects/workspaces context
		} else if (
			name.includes("file_search") ||
			name.includes("file-search")
		) {
			contextPanelStore.open("knowledge");
		} else if (name.includes("memory")) {
			contextPanelStore.open("knowledge");
		}

		if (streamingMessageId) {
			const currentMsg = messages.find(
				(m) => m.id === streamingMessageId,
			);
			const toolCalls = currentMsg?.metadata?.toolCalls || [];

			assistantStore.updateMessage(streamingMessageId, {
				metadata: {
					...currentMsg?.metadata,
					toolCalls: [
						...toolCalls,
						{
							id: crypto.randomUUID?.() || String(Date.now()),
							name: toolName,
							arguments: toolArgs,
							status: "running" as const,
							timestamp: new Date(),
						},
					],
				},
			});
		}
	}

	function handleToolResultEvent(event: RealtimeEvent) {
		const toolName = event.content.tool_name || event.content.name;
		const result = event.content.result || event.content.output;

		if (streamingMessageId) {
			const currentMsg = messages.find(
				(m) => m.id === streamingMessageId,
			);
			const toolCalls = currentMsg?.metadata?.toolCalls || [];

			// Update the matching tool call with result
			const updatedToolCalls = toolCalls.map((tc) =>
				tc.name === toolName && tc.status === "running"
					? { ...tc, result, status: "completed" as const }
					: tc,
			);

			assistantStore.updateMessage(streamingMessageId, {
				metadata: {
					...currentMsg?.metadata,
					toolCalls: updatedToolCalls,
				},
			});
		}

		// Refresh relevant stores so UI reflects tool-side effects
		if (toolName) {
			const name = toolName.toLowerCase();
			if (
				name.includes("task") ||
				name.includes("knowledge") ||
				name.includes("item")
			) {
				// Unified: refresh knowledgeStore for all item types (including tasks)
				knowledgeStore.loadKnowledgeItems();
				// Also refresh tasks store for backward compatibility
				tasksStore.loadTasks();
			}
			if (name.includes("project")) {
				projectsStore.loadProjects();
			}
			if (name.includes("event") || name.includes("calendar")) {
				const now = new Date();
				const end = new Date();
				end.setDate(end.getDate() + 7);
				calendarStore.loadEvents(now.toISOString(), end.toISOString());
			}
			if (name.includes("time") || name.includes("timer")) {
				timeStore.loadEntries();
			}
			if (name.includes("workflow")) {
				workflowStore.loadTemplates();
			}
			if (name.includes("analytic")) {
				analyticsStore.loadAll();
			}
			if (name.includes("workspace")) {
				workspacesStore.loadWorkspaces();
			}
			if (name.includes("setting") || name.includes("preference")) {
				settingsStore.loadSettings();
				// Apply theme preference immediately if returned
				try {
					if (result?.preferences?.theme) {
						const theme = String(
							result.preferences.theme,
						).toLowerCase();
						if (["light", "dark", "system"].includes(theme)) {
							setMode(theme as "light" | "dark" | "system");
						}
					}
				} catch (e) {
					logger.warn("Theme sync failed", { error: e });
				}
			}
			if (name.includes("infra") || name.includes("log")) {
				contextPanelStore.open("infra");
			}
			if (result) {
				try {
					const snippet =
						typeof result === "string"
							? result.slice(0, 160)
							: JSON.stringify(result).slice(0, 160);
					toast.info?.(
						`Tool ${toolName} completed${snippet ? `: ${snippet}` : ""}`,
					);
				} catch (e) {
					logger.error("Toast failure", e);
				}
			}
		}
	}

	function handleStreamComplete(event: RealtimeEvent) {
		assistantStore.setIIAgentProcessing(false);
		streamingMessageId = null;
	}

	function handleErrorEvent(event: RealtimeEvent) {
		const error =
			event.content.error || event.content.message || "Unknown error";
		assistantStore.setIIAgentError(error);
		assistantStore.setIIAgentProcessing(false);

		assistantStore.addMessage({
			role: "system",
			content: `Error: ${error}`,
			source: "ii-agent",
		});

		try {
			toast?.error?.(error);
		} catch (e) {
			logger.error("Toast error", e);
		}

		streamingMessageId = null;
	}

	function handleIIAgentError(error: Error) {
		logger.error("[UnifiedCanvas] II-Agent error:", error);
		assistantStore.setIIAgentError(error.message);
	}

	function handleIIAgentClose() {
		assistantStore.setIIAgentConnection(false);
		assistantStore.setIIAgentInitialized(false);
		logger.info("[UnifiedCanvas] II-Agent connection closed");
	}

	// ========== Message Handlers ==========

	async function handleSend() {
		if (!inputMessage.trim() || $isProcessing) return;

		const content = inputMessage.trim();
		inputMessage = "";

		// Add user message
		assistantStore.addMessage({
			role: "user",
			content,
			source: "text",
		});

		// Send based on mode
		if (composerMode === "ii-agent" && iiAgentConnected && iiAgentClient) {
			// Send via II-Agent
			try {
				assistantStore.setIIAgentProcessing(true);
				iiAgentClient.sendQuery(
					`${focusSystemHint}\n\nUser request: ${content}`,
				);
			} catch (error: any) {
				logger.error("Failed to send II-Agent query:", error);
				assistantStore.setIIAgentError(error.message);
			}
		} else {
			// Fall back to regular API
			onsend?.({ detail: { message: content } });
		}

		scrollToBottom();
	}

	function handleVoiceRecord() {
		onrecord?.();
	}

	function handleVoiceStop() {
		onstop?.();
	}

	function handleVoiceUpload(event: any) {
		onupload?.(event);
	}

	function handleProviderChange(event: any) {
		onprovider?.(event);
	}

	function handlePromptSelect(prompt: string) {
		inputMessage = prompt;
	}

	function handleModeChange(modeValue: string) {
		const mode = modeValue as "deterministic" | "orchestrated" | "ii-agent";
		assistantStore.setMode(mode);

		// Connect II-Agent if switching to II-Agent mode
		if (mode === "ii-agent" && !iiAgentConnected && iiAgentClient) {
			initializeIIAgent();
		}
	}

	function handleModelChange(event: CustomEvent) {
		const model = event.detail;
		assistantStore.setComposerState({ model });

		// Reinitialize II-Agent with new model if connected
		if (composerMode === "ii-agent" && iiAgentConnected && iiAgentClient) {
			initializeIIAgent(model);
		}
	}

	// ========== II-Agent Connection ==========

	async function initializeIIAgent(modelName?: string) {
		if (!iiAgentClient) return;

		try {
			// Get session credentials from API (real token, no mocks)
			const session: any = await api.agent.createSession();
			const sessionUuid =
				session.sessionUuid ||
				session.sessionId ||
				crypto.randomUUID?.() ||
				String(Date.now());
			const agentToken = session.agentToken;

			// Connect
			await iiAgentClient.connect(sessionUuid, agentToken);
			assistantStore.setIIAgentConnection(true, sessionUuid, agentToken);

			// Initialize agent
			const config: AgentConfig = {
				model_name: modelName || selectedModel,
				enable_focus_tools: true,
				enable_reviewer: false,
				thinking_tokens: 0,
			};

			iiAgentClient.initAgent(config);
		} catch (error: any) {
			logger.error("Failed to initialize II-Agent:", error);
			assistantStore.setIIAgentError(error.message);
		}
	}

	function disconnectIIAgent() {
		if (iiAgentClient) {
			iiAgentClient.disconnect();
		}
		assistantStore.setIIAgentConnection(false);
		assistantStore.setIIAgentInitialized(false);
	}

	// ========== Drawer Handlers ==========

	function openWorkflow(workflowId: string) {
		assistantStore.openWorkflowDrawer(workflowId);
	}

	function handleWorkflowApprove(event: any) {
		onworkflowApprove?.(event);
	}

	function handleWorkflowRevise(event: any) {
		onworkflowRevise?.(event);
	}

	function handleWorkflowReject(event: any) {
		// No callback prop for this yet
	}

	function handleInspectArtifact(event: any) {
		// No callback prop for this yet
	}

	function handleSendWorkflowToAssistant(event: CustomEvent) {
		inputMessage = event.detail.prompt;
		handleSend();
	}

	// ========== Message Rendering ==========

	function formatTime(date: Date) {
		return new Intl.DateTimeFormat("en-US", {
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		}).format(date);
	}

	function getSourceIcon(source: string) {
		switch (source) {
			case "voice":
				return "🎤";
			case "ii-agent":
				return "🤖";
			default:
				return "";
		}
	}
</script>

<section
	class="flex-1 bg-card brutal-border brutal-shadow flex flex-col overflow-hidden h-full"
>
	<!-- Header -->
	<div
		class="flex flex-col gap-2 px-5 py-4 border-b-2 border-black dark:border-white bg-secondary"
	>
		<div class="flex items-center justify-between">
			<div
				class="flex items-center gap-2 text-sm uppercase tracking-wide font-bold"
			>
				<Sparkles class="w-4 h-4 text-black dark:text-white" />
				{composerMode === "ii-agent"
					? "II-Agent Mode"
					: composerMode === "orchestrated"
						? "Orchestrator Mode"
						: "Deterministic Mode"}
			</div>

			<!-- Connection Status -->
			{#if composerMode === "ii-agent"}
				<div
					class="flex items-center gap-2 text-xs font-bold uppercase"
				>
					{#if iiAgentConnected}
						<div
							class="flex items-center gap-1.5 px-2 py-1 border-2 border-black dark:border-white bg-green-400 text-black"
						>
							<div class="w-2 h-2 bg-black animate-pulse"></div>
							Connected
						</div>
						<button
							class="px-2 py-1 border-2 border-black dark:border-white bg-white dark:bg-black hover:bg-gray-100 dark:hover:bg-gray-900"
							onclick={() => initializeIIAgent()}
						>
							Reconnect
						</button>
					{:else}
						<button
							class="flex items-center gap-1.5 px-2 py-1 border-2 border-black dark:border-white bg-white text-black hover:bg-gray-200 transition-colors"
							onclick={() => initializeIIAgent()}
						>
							Connect II-Agent
						</button>
					{/if}
					{#if iiAgentError}
						<span class="text-[10px] text-destructive font-bold"
							>Error: {iiAgentError}</span
						>
					{/if}
				</div>
			{/if}
		</div>

		<div
			class="flex flex-col md:flex-row md:items-center md:justify-between gap-2"
		>
			<div>
				<h1
					class="text-3xl font-black uppercase tracking-tighter text-foreground"
				>
					{title}
				</h1>
				<p class="text-muted-foreground font-bold text-sm">
					{subtitle}
				</p>
			</div>

			<!-- Mode & Model Selector -->
			<div class="flex flex-wrap items-center gap-3 text-sm font-bold">
				<select
					value={composerMode}
					class="px-3 py-1.5 border-2 border-black dark:border-white bg-white dark:bg-black text-foreground uppercase focus:outline-none focus:ring-0 focus:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[2px_2px_0px_0px_rgba(255,255,255,1)] transition-all"
					onchange={(e) => handleModeChange(e.currentTarget.value)}
				>
					<option value="ii-agent">II-Agent</option>
					<option value="orchestrated">Orchestrated</option>
					<option value="deterministic">Deterministic</option>
				</select>

				<select
					value={selectedModel}
					class="px-3 py-1.5 border-2 border-black dark:border-white bg-white dark:bg-black text-foreground uppercase focus:outline-none focus:ring-0 focus:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[2px_2px_0px_0px_rgba(255,255,255,1)] transition-all"
					onchange={(e) =>
						handleModelChange(
							new CustomEvent("change", {
								detail: e.currentTarget.value,
							}),
						)}
				>
					{#each models as model}
						<option value={model.value}>{model.label}</option>
					{/each}
				</select>
			</div>
		</div>
	</div>

	<!-- Messages -->
	<div
		bind:this={container}
		class="flex-1 overflow-y-auto p-6 space-y-8 bg-background bg-grid-pattern"
	>
		{#each messages as message (message.id)}
			<div
				class="flex items-start gap-4 {message.role === 'user'
					? 'flex-row-reverse'
					: ''} animate-fade-in"
			>
				<div
					class="w-10 h-10 border-2 border-border flex items-center justify-center flex-shrink-0 font-bold shadow-brutal-sm
					{message.role === 'user'
						? 'bg-primary text-primary-foreground'
						: message.role === 'system'
							? 'bg-system-red text-white'
							: 'bg-secondary text-secondary-foreground'}"
				>
					{#if message.role === "user"}
						<User class="w-5 h-5" />
					{:else if message.role === "system"}
						<AlertTriangle class="w-5 h-5" />
					{:else}
						<Bot class="w-5 h-5" />
					{/if}
				</div>

				<div class="flex-1 space-y-3 min-w-0 max-w-3xl">
					{#if message.metadata?.thinking}
						<div
							class="p-3 border-2 border-border bg-card text-foreground flex items-center gap-3 font-mono font-bold text-[10px] uppercase tracking-widest shadow-brutal-sm border-l-4 border-l-cyan-data"
						>
							<Brain class="w-4 h-4 animate-pulse text-cyan-data" />
							<span>{message.metadata.thinking}</span>
						</div>
					{/if}

					{#if message.metadata?.toolCalls && message.metadata.toolCalls.length > 0}
						<div class="space-y-2">
							{#each message.metadata.toolCalls as toolCall}
								<div
									class="p-3 border-2 border-border bg-void text-terminal-green font-mono shadow-brutal-sm"
								>
									<div class="flex items-center gap-2">
										<Wrench
											class="w-3.5 h-3.5 {toolCall.status ===
											'running'
												? 'animate-spin'
												: ''}"
										/>
										<span class="text-[11px] font-black uppercase tracking-tight">
											EXEC: {toolCall.name}
										</span>
										<span
											class="text-[9px] px-1.5 py-0.5 border border-terminal-green bg-terminal-green/10 uppercase font-black"
										>
											{toolCall.status}
										</span>
									</div>
									{#if toolCall.result}
										<div
											class="text-[10px] mt-2 border-t border-terminal-green/30 pt-2 opacity-80 overflow-hidden"
										>
											<span class="opacity-50">OUTPUT_BUFFER >></span> {typeof toolCall.result ===
											"string"
												? toolCall.result
												: JSON.stringify(
														toolCall.result,
													).substring(0, 150)}...
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{/if}

					{#if message.content}
						<div
							class="p-4 border-2 border-border shadow-card text-sm leading-relaxed
							{message.role === 'user'
								? 'bg-primary text-primary-foreground'
								: message.role === 'system'
									? 'bg-system-red text-white'
									: 'bg-card text-card-foreground'}"
						>
							{#if message.role === "assistant"}
								<MarkdownRenderer content={message.content} />
							{:else}
								<p
									class="whitespace-pre-wrap break-words font-medium"
								>
									{message.content}
								</p>
							{/if}
						</div>
					{/if}

					<div
						class="flex items-center gap-3 text-[9px] font-black uppercase tracking-widest text-muted-foreground {message.role ===
						'user'
							? 'flex-row-reverse'
							: ''}"
					>
						<span>{formatTime(message.timestamp)}</span>
						{#if message.source !== "text"}
							<span class="flex items-center gap-1">
								<span class="w-1 h-1 bg-muted-foreground rounded-full"></span>
								{getSourceIcon(message.source)} {message.source}
							</span>
						{/if}
					</div>
				</div>
			</div>
		{/each}

		{#if $isProcessing}
			<div class="flex items-start gap-4 animate-pulse">
				<div
					class="w-10 h-10 border-2 border-border bg-secondary flex items-center justify-center shadow-brutal-sm"
				>
					<Bot class="w-5 h-5" />
				</div>
				<div
					class="p-4 border-2 border-border bg-card flex gap-3 items-center shadow-card border-l-4 border-l-terminal-green"
				>
					<div class="w-2 h-2 bg-terminal-green animate-ping"></div>
					<span class="text-[11px] font-black uppercase tracking-widest"
						>SYSTEM_THINKING...</span
					>
				</div>
			</div>
		{/if}

		<!-- Latest Workflow Preview -->
		{#if $latestWorkflow}
			<div
				class="p-4 border-2 border-border bg-accent text-accent-foreground shadow-card relative overflow-hidden"
			>
				<div class="absolute top-0 right-0 w-16 h-16 bg-void/5 -rotate-45 translate-x-8 -translate-y-8"></div>
				<div class="flex items-center justify-between mb-2 relative z-10">
					<div class="flex items-center gap-2">
						<History class="w-4 h-4" />
						<span class="text-sm font-black uppercase tracking-tighter"
							>Draft Workflow</span
						>
					</div>
					<button
						class="brutal-btn py-1 px-3 text-[10px] bg-white text-black shadow-brutal-sm"
						onclick={() => openWorkflow($latestWorkflow.id)}
					>
						INSPECT_DATA
					</button>
				</div>
				<p class="text-sm font-black uppercase tracking-tight relative z-10">
					{$latestWorkflow.mainTask?.title || "Untitled"}
				</p>
				{#if $latestWorkflow.confidence !== undefined}
					<div class="mt-2 flex items-center gap-2 relative z-10">
						<div class="flex-1 h-1 bg-void/10">
							<div class="h-full bg-void" style="width: {$latestWorkflow.confidence * 100}%"></div>
						</div>
						<span class="text-[9px] font-mono font-bold">
							CONF: {($latestWorkflow.confidence * 100).toFixed(0)}%
						</span>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Status Bar -->
	<div
		class="px-6 py-2 text-xs font-bold uppercase tracking-wider border-t-2 border-black dark:border-white bg-secondary flex items-center justify-between"
	>
		<div>
			{#if isRecording}
				<div class="text-destructive animate-pulse">Recording...</div>
			{:else if isProcessingAudio}
				<div>Processing audio...</div>
			{:else if $isProcessing}
				<div>Processing...</div>
			{:else}
				<div class="text-muted-foreground">Ready</div>
			{/if}
		</div>

		{#if $assistantStore.iiAgentState.error}
			<div class="text-destructive flex items-center gap-1">
				<AlertTriangle class="w-3 h-3" />
				{$assistantStore.iiAgentState.error}
			</div>
		{/if}
	</div>

	<!-- Composer -->
	<AssistantComposer
		bind:inputMessage
		isLoading={$isProcessing}
		{quickPrompts}
		{isRecording}
		{isProcessingAudio}
		{supportsRecording}
		{voiceProvider}
		{voiceStatus}
		{recordingError}
		{uploadError}
		onsend={handleSend}
		onrecord={handleVoiceRecord}
		onstop={handleVoiceStop}
		onupload={handleVoiceUpload}
		onprovider={handleProviderChange}
		onprompt={handlePromptSelect}
	/>
</section>

<!-- Drawers -->
<WorkflowDrawer
	bind:open={workflowDrawerOpen}
	onapprove={handleWorkflowApprove}
	onrevise={handleWorkflowRevise}
	onreject={handleWorkflowReject}
	oninspectArtifact={handleInspectArtifact}
	onsendToAssistant={handleSendWorkflowToAssistant}
/>

<ExecutionDrawer
	bind:open={executionDrawerOpen}
	onsave={(e) => onexecutionSave?.(e)}
	ontoggleStatus={() => {}}
	ondelete={() => {}}
	onsendToAssistant={(e) => {
		inputMessage = e.detail?.prompt || "";
		handleSend();
	}}
/>
