<script lang="ts">
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';
	import { Bot, User, Loader2, Sparkles } from 'lucide-svelte';
	import AssistantComposer from './AssistantComposer.svelte';

	interface AssistantMessage {
		id: string;
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
		source: 'text' | 'voice';
	}

	interface Props {
		title?: string;
		subtitle?: string;
		useOrchestrator?: boolean;
		models?: Array<{ label: string; value: string }>;
		selectedModel?: string;
		messages?: AssistantMessage[];
		isLoading?: boolean;
		sendError?: string | null;
		quickPrompts?: string[];
		inputMessage?: string;
		isRecording?: boolean;
		isProcessingAudio?: boolean;
		supportsRecording?: boolean;
		voiceProvider?: string;
		voiceStatus?: { providers: Record<string, boolean> } | null;
		recordingError?: string | null;
		uploadError?: string | null;
		formatTime?: (date: Date) => string;
		onorchestrator?: (checked: boolean) => void;
		onmodel?: (value: string) => void;
		onsend?: () => void;
		onrecord?: () => void;
		onstop?: () => void;
		onupload?: (event: Event) => void;
		onprovider?: (value: string) => void;
		onprompt?: (prompt: string) => void;
	}

	let {
		title = 'Command Center',
		subtitle = 'Chat, orchestrate, and execute from one canvas.',
		useOrchestrator = true,
		models = [],
		selectedModel = '',
		messages = [],
		isLoading = false,
		sendError = null,
		quickPrompts = [],
		inputMessage = $bindable(''),
		isRecording = false,
		isProcessingAudio = false,
		supportsRecording = false,
		voiceProvider = 'gemini-native',
		voiceStatus = null,
		recordingError = null,
		uploadError = null,
		formatTime = () => '',
		onorchestrator,
		onmodel,
		onsend,
		onrecord,
		onstop,
		onupload,
		onprovider,
		onprompt
	}: Props = $props();

	let container: HTMLDivElement | undefined = $state();

	export function scrollToBottom() {
		if (container) container.scrollTop = container.scrollHeight;
	}

	function handleOrchestratorChange(event: Event) {
		const target = event.currentTarget as HTMLInputElement | null;
		if (target && onorchestrator) {
			onorchestrator(target.checked);
		}
	}

	function handleModelChange(event: Event) {
		const target = event.currentTarget as HTMLSelectElement | null;
		if (target && onmodel) {
			onmodel(target.value);
		}
	}
</script>

<section class="flex-1 bg-white/80 dark:bg-card/80 border border-white/40 dark:border-border rounded-[32px] flex flex-col overflow-hidden shadow-xl backdrop-blur">
	<div class="flex flex-col gap-2 px-5 py-4 border-b border-border/60">
		<div class="flex items-center gap-2 text-sm uppercase tracking-wide text-muted-foreground">
			<Sparkles class="w-4 h-4 text-primary" />
			Proactive Agent
		</div>
		<div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
			<div>
				<h1 class="text-3xl font-bold text-slate-900 dark:text-white">{title}</h1>
				<p class="text-muted-foreground">{subtitle}</p>
			</div>
			<div class="flex flex-wrap items-center gap-3 text-sm">
				<label class="inline-flex items-center gap-2">
					<input
						type="checkbox"
						checked={useOrchestrator}
						class="rounded border-border"
						onchange={handleOrchestratorChange}
					/>
					Use orchestrator
				</label>
				<div class="flex items-center gap-2">
					<span class="text-muted-foreground">Model</span>
					<select
						value={selectedModel}
						class="px-3 py-1.5 rounded-full bg-card border border-border text-sm"
						onchange={handleModelChange}
					>
						{#each models as model}
							<option value={model.value}>{model.label}</option>
						{/each}
					</select>
				</div>
			</div>
		</div>
	</div>

	<div bind:this={container} class="flex-1 overflow-y-auto p-6 space-y-4">
		{#each messages as message (message.id)}
			<div class="flex items-start gap-3 {message.role === 'user' ? 'flex-row-reverse' : ''}">
				<div
					class="w-9 h-9 rounded-full flex items-center justify-center {message.role === 'user'
						? 'bg-primary text-primary-foreground'
						: 'bg-accent text-accent-foreground'}"
				>
					{#if message.role === 'user'}
						<User class="w-4 h-4" />
					{:else}
						<Bot class="w-4 h-4" />
					{/if}
				</div>
				<div class="flex-1 space-y-2">
					<div
						class="p-4 rounded-2xl text-sm leading-relaxed shadow-sm {message.role === 'user'
							? 'bg-primary text-primary-foreground ml-auto'
							: 'bg-muted/30 border border-border'}"
					>
						{#if message.role === 'assistant'}
							<MarkdownRenderer content={message.content} />
						{:else}
							<p class="whitespace-pre-wrap break-words">{message.content}</p>
						{/if}
					</div>
					<p class="text-xs text-muted-foreground {message.role === 'user' ? 'text-right' : ''}">
						{formatTime(message.timestamp)} {message.source === 'voice' ? '• Voice' : ''}
					</p>
				</div>
			</div>
		{/each}

		{#if isLoading}
			<div class="flex items-start gap-3">
				<div class="w-9 h-9 rounded-full bg-accent flex items-center justify-center">
					<Bot class="w-4 h-4" />
				</div>
				<div class="p-4 rounded-2xl border border-border flex gap-2 items-center">
					<Loader2 class="w-4 h-4 animate-spin text-muted-foreground" />
					<span class="text-sm text-muted-foreground">Thinking...</span>
				</div>
			</div>
		{/if}
	</div>

	{#if sendError}
		<div class="px-4 py-2 text-sm text-destructive bg-destructive/10">{sendError}</div>
	{/if}

	<div class="px-6 pb-2 text-xs text-muted-foreground">
		{#if isRecording}
			<div class="text-destructive font-medium">Recording...</div>
		{:else if isProcessingAudio}
			<div>Processing audio...</div>
		{:else}
			<div>Ready</div>
		{/if}
	</div>

	<AssistantComposer
		bind:inputMessage
		{isLoading}
		{quickPrompts}
		{isRecording}
		{isProcessingAudio}
		{supportsRecording}
		{voiceProvider}
		{voiceStatus}
		{recordingError}
		{uploadError}
		onsend={() => onsend?.()}
		onrecord={() => onrecord?.()}
		onstop={() => onstop?.()}
		onupload={(event) => onupload?.(event)}
		onprovider={(value) => onprovider?.(value)}
		onprompt={(prompt) => onprompt?.(prompt)}
	/>
</section>
