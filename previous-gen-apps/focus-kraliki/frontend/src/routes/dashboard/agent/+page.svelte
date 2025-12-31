<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api/client';
	import { IIAgentClient } from '$lib/agent/iiAgentClient';
	import type {
		RealtimeEvent,
		EventLogEntry,
		AgentConfig,
		ConnectionState,
		AgentSessionResponse
	} from '$lib/agent/types';
	import { EventType } from '$lib/agent/types';
	import {
		Bot,
		Power,
		PowerOff,
		Send,
		X,
		Settings,
		Zap,
		AlertCircle,
		CheckCircle,
		Loader2,
		Terminal,
		Wrench,
		MessageSquare,
		Sparkles
	} from 'lucide-svelte';
	import { getPendingEscalation, clearPendingEscalation } from '$lib/utils/pendingEscalation';
	import { logger } from '$lib/utils/logger';

	// II-Agent Client
	let iiAgentClient: IIAgentClient;

	// Connection state
	let connectionState: ConnectionState = {
		isConnected: false,
		isConnecting: false,
		isAgentInitialized: false,
		error: null,
		sessionUuid: null,
		agentToken: null
	};

	// Agent configuration
	let agentConfig: AgentConfig = {
		model_name: 'z-ai/glm-4.7',
		enable_focus_tools: true,
		enable_reviewer: false,
		thinking_tokens: 0
	};

	// Event log
	let eventLog: EventLogEntry[] = [];
	let eventLogContainer: HTMLDivElement;

	// User input
	let userInput = '';
	let isProcessing = false;

	// Available models
	const availableModels = [
		{ value: 'google/gemini-3-flash-preview', label: 'Gemini 3 Flash' },
		{ value: 'z-ai/glm-4.7', label: 'GLM-4.7' },
		{ value: 'meta-llama/llama-4-scout', label: 'Llama 4 Scout (Groq)' },
		{ value: 'meta-llama/llama-3.3-70b-instruct', label: 'Llama 3.3 70B (Groq)' },
		{ value: 'deepseek/deepseek-v3.2', label: 'DeepSeek V3.2' }
	];
	const agentModelSelectId = 'agent-model-select';
	const thinkingTokensInputId = 'agent-thinking-tokens';

	onMount(() => {
		// Initialize II-Agent client
		iiAgentClient = new IIAgentClient(import.meta.env.PUBLIC_II_AGENT_WS_URL);

		// Register event handlers
		iiAgentClient.onEvent(handleAgentEvent);
		iiAgentClient.onError(handleAgentError);
		iiAgentClient.onClose(handleAgentClose);
	});

	onDestroy(() => {
		if (iiAgentClient) {
			iiAgentClient.disconnect();
		}
	});

	async function handleConnect() {
		if (connectionState.isConnecting || connectionState.isConnected) return;

		connectionState.isConnecting = true;
		connectionState.error = null;

		try {
			// Step 1: Get agent session token from Focus by Kraliki
			addSystemMessage('Requesting agent session from Focus by Kraliki...');
			const pendingEscalation = getPendingEscalation();
			const sessionResponse = (await api.agent.createSession(
				pendingEscalation || undefined
			)) as AgentSessionResponse;

			connectionState.sessionUuid = sessionResponse.sessionUuid;
			connectionState.agentToken = sessionResponse.agentToken;

			addSystemMessage(`Session created: ${sessionResponse.sessionUuid}`);
			if (pendingEscalation) {
				addSystemMessage('Escalation context attached to this ii-agent session.');
				clearPendingEscalation();
			}

			// Step 2: Connect to II-Agent WebSocket
			addSystemMessage('Connecting to II-Agent WebSocket...');
			await iiAgentClient.connect(sessionResponse.sessionUuid, sessionResponse.agentToken);

			connectionState.isConnected = true;
			connectionState.isConnecting = false;

			addSystemMessage('Connected to II-Agent! Ready to initialize agent.');
		} catch (error: any) {
			logger.error('Connection failed:', error);
			connectionState.error = error.detail || error.message || 'Connection failed';
			connectionState.isConnecting = false;
			connectionState.isConnected = false;
			addErrorMessage(`Connection failed: ${connectionState.error}`);
		}
	}

	function handleDisconnect() {
		if (iiAgentClient) {
			iiAgentClient.disconnect();
		}
		connectionState.isConnected = false;
		connectionState.isAgentInitialized = false;
		connectionState.sessionUuid = null;
		connectionState.agentToken = null;
		addSystemMessage('Disconnected from II-Agent');
	}

	function handleInitAgent() {
		if (!connectionState.isConnected) {
			addErrorMessage('Not connected to II-Agent');
			return;
		}

		try {
			addSystemMessage('Initializing agent...');
			iiAgentClient.initAgent(agentConfig);
			addSystemMessage(`Agent configuration sent:
- Model: ${agentConfig.model_name}
- Focus Tools: ${agentConfig.enable_focus_tools ? 'Enabled' : 'Disabled'}
- Reviewer: ${agentConfig.enable_reviewer ? 'Enabled' : 'Disabled'}`);
		} catch (error: any) {
			addErrorMessage(`Failed to initialize agent: ${error.message}`);
		}
	}

	async function handleSendQuery() {
		if (!userInput.trim() || isProcessing || !connectionState.isAgentInitialized) return;

		const query = userInput.trim();
		userInput = '';
		isProcessing = true;

		try {
			addUserMessage(query);
			iiAgentClient.sendQuery(query);
		} catch (error: any) {
			addErrorMessage(`Failed to send query: ${error.message}`);
			isProcessing = false;
		}
	}

	function handleCancel() {
		if (!connectionState.isConnected) return;

		try {
			iiAgentClient.cancel();
			addSystemMessage('Cancellation requested');
		} catch (error: any) {
			addErrorMessage(`Failed to cancel: ${error.message}`);
		}
	}

	// Event handlers

	function handleAgentEvent(event: RealtimeEvent) {
		logger.debug('[Agent Event]', { event });

		switch (event.type) {
			case EventType.CONNECTION_ESTABLISHED:
				addEventLog(event, 'Connection established');
				break;

			case EventType.AGENT_INITIALIZED:
				connectionState.isAgentInitialized = true;
				addEventLog(event, 'Agent initialized successfully');
				break;

			case EventType.WORKSPACE_INFO:
				addEventLog(
					event,
					`Workspace: ${event.content.workspace_dir || 'Unknown'}`
				);
				break;

			case EventType.PROCESSING:
				addEventLog(event, event.content.message || 'Processing...');
				break;

			case EventType.AGENT_THINKING:
				addEventLog(event, 'Agent is thinking...');
				break;

			case EventType.TOOL_CALL:
				const toolName = event.content.tool_name || 'Unknown Tool';
				const toolInput = event.content.tool_input
					? JSON.stringify(event.content.tool_input, null, 2)
					: '';
				addEventLog(event, `Tool Call: ${toolName}\n${toolInput}`);
				break;

			case EventType.TOOL_RESULT:
				const resultContent = event.content.result
					? typeof event.content.result === 'string'
						? event.content.result
						: JSON.stringify(event.content.result, null, 2)
					: 'No result';
				addEventLog(event, `Tool Result:\n${resultContent}`);
				break;

			case EventType.AGENT_RESPONSE:
				const response = event.content.response || event.content.text || '';
				addEventLog(event, `Agent Response:\n${response}`);
				isProcessing = false;
				break;

			case EventType.AGENT_RESPONSE_INTERRUPTED:
				addEventLog(event, 'Agent response interrupted');
				isProcessing = false;
				break;

			case EventType.STREAM_COMPLETE:
				addEventLog(event, 'Stream complete');
				isProcessing = false;
				break;

			case EventType.ERROR:
				const errorMsg = event.content.error || event.content.message || 'Unknown error';
				addEventLog(event, `Error: ${errorMsg}`);
				isProcessing = false;
				break;

			case EventType.SYSTEM:
				addEventLog(event, event.content.message || 'System message');
				break;

			case EventType.USER_MESSAGE:
				addEventLog(event, event.content.text || '');
				break;

			case EventType.PONG:
				// Ignore pong messages
				break;

			default:
				addEventLog(event, JSON.stringify(event.content, null, 2));
				break;
		}

		scrollToBottom();
	}

	function handleAgentError(error: Error) {
		logger.error('[Agent Error]', error);
		addErrorMessage(`WebSocket Error: ${error.message}`);
	}

	function handleAgentClose() {
		logger.info('[Agent Close]');
		if (connectionState.isConnected) {
			connectionState.isConnected = false;
			connectionState.isAgentInitialized = false;
			addSystemMessage('WebSocket connection closed');
		}
	}

	// Event log helpers

	function addEventLog(event: RealtimeEvent, formattedContent: string) {
		const entry: EventLogEntry = {
			id: `${Date.now()}-${Math.random()}`,
			timestamp: new Date(),
			type: event.type,
			content: event.content,
			formattedContent
		};
		eventLog = [...eventLog, entry];
	}

	function addSystemMessage(message: string) {
		const entry: EventLogEntry = {
			id: `${Date.now()}-${Math.random()}`,
			timestamp: new Date(),
			type: EventType.SYSTEM,
			content: { message },
			formattedContent: message
		};
		eventLog = [...eventLog, entry];
	}

	function addErrorMessage(message: string) {
		const entry: EventLogEntry = {
			id: `${Date.now()}-${Math.random()}`,
			timestamp: new Date(),
			type: EventType.ERROR,
			content: { error: message },
			formattedContent: message
		};
		eventLog = [...eventLog, entry];
	}

	function addUserMessage(message: string) {
		const entry: EventLogEntry = {
			id: `${Date.now()}-${Math.random()}`,
			timestamp: new Date(),
			type: EventType.USER_MESSAGE,
			content: { text: message },
			formattedContent: message
		};
		eventLog = [...eventLog, entry];
	}

	function scrollToBottom() {
		setTimeout(() => {
			if (eventLogContainer) {
				eventLogContainer.scrollTop = eventLogContainer.scrollHeight;
			}
		}, 100);
	}

	function clearEventLog() {
		if (confirm('Clear event log?')) {
			eventLog = [];
		}
	}

	function formatTime(date: Date): string {
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		}).format(date);
	}

	function getEventIcon(type: EventType) {
		switch (type) {
			case EventType.CONNECTION_ESTABLISHED:
				return CheckCircle;
			case EventType.AGENT_INITIALIZED:
				return CheckCircle;
			case EventType.PROCESSING:
				return Loader2;
			case EventType.AGENT_THINKING:
				return Sparkles;
			case EventType.TOOL_CALL:
				return Wrench;
			case EventType.TOOL_RESULT:
				return Terminal;
			case EventType.AGENT_RESPONSE:
				return Bot;
			case EventType.ERROR:
				return AlertCircle;
			case EventType.SYSTEM:
				return Settings;
			case EventType.USER_MESSAGE:
				return MessageSquare;
			default:
				return Terminal;
		}
	}

	function getEventColor(type: EventType): string {
		switch (type) {
			case EventType.CONNECTION_ESTABLISHED:
			case EventType.AGENT_INITIALIZED:
				return 'text-green-500';
			case EventType.PROCESSING:
			case EventType.AGENT_THINKING:
				return 'text-blue-500';
			case EventType.TOOL_CALL:
			case EventType.TOOL_RESULT:
				return 'text-purple-500';
			case EventType.AGENT_RESPONSE:
				return 'text-primary';
			case EventType.ERROR:
				return 'text-red-500';
			case EventType.SYSTEM:
				return 'text-muted-foreground';
			case EventType.USER_MESSAGE:
				return 'text-yellow-500';
			default:
				return 'text-muted-foreground';
		}
	}
</script>

<div class="flex flex-col h-[calc(100vh-8rem)]">
	<!-- Header -->
	<div class="flex items-center justify-between pb-4 border-b border-border">
		<div>
			<h1 class="text-3xl font-bold flex items-center gap-2">
				<Bot class="w-8 h-8 text-primary" />
				Agent Workbench
			</h1>
			<p class="text-muted-foreground mt-1">II-Agent Integration</p>
		</div>

		<!-- Connection Controls -->
		<div class="flex items-center gap-2">
			{#if !connectionState.isConnected}
				<button
					onclick={handleConnect}
					disabled={connectionState.isConnecting}
					class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
				>
					{#if connectionState.isConnecting}
						<Loader2 class="w-4 h-4 animate-spin" />
						Connecting...
					{:else}
						<Power class="w-4 h-4" />
						Connect
					{/if}
				</button>
			{:else}
				<div class="flex items-center gap-2">
					<span class="text-sm text-green-500 flex items-center gap-1">
						<CheckCircle class="w-4 h-4" />
						Connected
					</span>
					{#if !connectionState.isAgentInitialized}
						<button
							onclick={handleInitAgent}
							class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2"
						>
							<Zap class="w-4 h-4" />
							Initialize Agent
						</button>
					{/if}
					<button
						onclick={handleDisconnect}
						class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"
					>
						<PowerOff class="w-4 h-4" />
						Disconnect
					</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- Configuration Panel -->
	{#if connectionState.isConnected && !connectionState.isAgentInitialized}
		<div class="mt-4 p-4 bg-card border border-border rounded-lg">
			<h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
				<Settings class="w-5 h-5" />
				Agent Configuration
			</h3>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Model Selector -->
				<div>
					<label class="block text-sm font-medium mb-2" for={agentModelSelectId}>Model</label>
					<select
						id={agentModelSelectId}
						bind:value={agentConfig.model_name}
						class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
					>
						{#each availableModels as model}
							<option value={model.value}>{model.label}</option>
						{/each}
					</select>
				</div>

				<!-- Focus Tools Toggle -->
				<div class="flex items-center gap-2">
					<input
						type="checkbox"
						id="focus-tools"
						bind:checked={agentConfig.enable_focus_tools}
						class="w-4 h-4 text-primary bg-background border-input rounded focus:ring-2 focus:ring-ring"
					/>
					<label for="focus-tools" class="text-sm font-medium">
						Enable Focus Tools (Tasks, Knowledge, Projects)
					</label>
				</div>

				<!-- Reviewer Toggle -->
				<div class="flex items-center gap-2">
					<input
						type="checkbox"
						id="reviewer"
						bind:checked={agentConfig.enable_reviewer}
						class="w-4 h-4 text-primary bg-background border-input rounded focus:ring-2 focus:ring-ring"
					/>
					<label for="reviewer" class="text-sm font-medium"> Enable Reviewer </label>
				</div>

				<!-- Thinking Tokens -->
				<div>
					<label class="block text-sm font-medium mb-2" for={thinkingTokensInputId}>Thinking Tokens (Extended Thinking)</label>
					<input
						id={thinkingTokensInputId}
						type="number"
						bind:value={agentConfig.thinking_tokens}
						min="0"
						max="10000"
						step="1000"
						class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
					/>
				</div>
			</div>
		</div>
	{/if}

	<!-- Event Log -->
	<div class="flex-1 mt-4 flex flex-col min-h-0">
		<div class="flex items-center justify-between mb-2">
			<h3 class="text-lg font-semibold">Event Stream</h3>
			<button
				onclick={clearEventLog}
				class="px-3 py-1 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors"
			>
				Clear Log
			</button>
		</div>

		<div
			bind:this={eventLogContainer}
			class="flex-1 overflow-y-auto bg-card border border-border rounded-lg p-4 space-y-2 font-mono text-sm"
		>
			{#if eventLog.length === 0}
				<p class="text-muted-foreground text-center py-8">
					No events yet. Connect to II-Agent to get started.
				</p>
			{:else}
				{#each eventLog as entry (entry.id)}
					<div class="flex items-start gap-2 p-2 rounded hover:bg-accent/50 transition-colors">
						<span class="text-xs text-muted-foreground whitespace-nowrap pt-1">
							{formatTime(entry.timestamp)}
						</span>
						<svelte:component
							this={getEventIcon(entry.type)}
							class="w-4 h-4 flex-shrink-0 mt-1 {getEventColor(entry.type)}"
						/>
						<div class="flex-1 min-w-0">
							<div class="text-xs text-muted-foreground uppercase">{entry.type}</div>
							<pre
								class="whitespace-pre-wrap break-words mt-1">{entry.formattedContent || ''}</pre>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Query Input -->
	{#if connectionState.isAgentInitialized}
		<div class="mt-4 border-t border-border pt-4">
			<form onsubmit={(e) => { e.preventDefault(); handleSendQuery(); }} class="flex gap-3">
				<input
					type="text"
					bind:value={userInput}
					placeholder="Enter your query... (e.g., 'Create a task for tomorrow')"
					disabled={isProcessing}
					class="flex-1 px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
				/>
				<button
					type="button"
					onclick={handleCancel}
					disabled={!isProcessing}
					class="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
				>
					<X class="w-4 h-4" />
				</button>
				<button
					type="submit"
					disabled={isProcessing || !userInput.trim()}
					class="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
				>
					{#if isProcessing}
						<Loader2 class="w-4 h-4 animate-spin" />
						Processing...
					{:else}
						<Send class="w-4 h-4" />
						Send
					{/if}
				</button>
			</form>
			<p class="text-xs text-muted-foreground mt-2">
				Try: "Create a knowledge item about WebSocket integration" or "List my current tasks"
			</p>
		</div>
	{/if}

	<!-- Connection Error -->
	{#if connectionState.error}
		<div class="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
			<div class="flex items-center gap-2 text-red-600 dark:text-red-400">
				<AlertCircle class="w-5 h-5" />
				<span class="font-semibold">Connection Error</span>
			</div>
			<p class="mt-2 text-sm text-red-700 dark:text-red-300">{connectionState.error}</p>
		</div>
	{/if}
</div>
