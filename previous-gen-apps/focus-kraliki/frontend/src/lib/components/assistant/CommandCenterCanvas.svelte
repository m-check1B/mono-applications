<script lang="ts">
	/**
	 * CommandCenterCanvas - Simplified AI Command Center
	 */
	import { onMount } from "svelte";
	import { assistantStore, isProcessing } from "$lib/stores/assistant";
	import MarkdownRenderer from "$lib/components/MarkdownRenderer.svelte";
	import AssistantComposer from "./AssistantComposer.svelte";
	import {
		BotIcon as Bot,
		UserIcon as User,
		AlertTriangleIcon as AlertTriangle,
		WrenchIcon as Wrench,
	} from "lucide-svelte";

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
		onsend?: (event: { detail: { message: string } }) => void;
		onrecord?: () => void;
		onstop?: () => void;
		onupload?: (event: Event) => void;
		onprovider?: (value: string) => void;
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
		onsend,
		onrecord,
		onstop,
		onupload,
		onprovider,
	}: Props = $props();

	let container: HTMLDivElement | undefined = $state();
	let messages = $derived($assistantStore.messages);

	export function scrollToBottom() {
		if (container) container.scrollTop = container.scrollHeight;
	}

	onMount(() => {
		scrollToBottom();
	});

	async function handleSend() {
		if (!inputMessage.trim() || $isProcessing) return;

		const content = inputMessage.trim();
		inputMessage = "";

		assistantStore.addMessage({
			role: "user",
			content,
			source: "text",
		});

		onsend?.({ detail: { message: content } });
		scrollToBottom();
	}

	function handleVoiceRecord() {
		onrecord?.();
	}

	function handleVoiceStop() {
		onstop?.();
	}

	function handleVoiceUpload(event: Event) {
		onupload?.(event);
	}

	function handleProviderChange(value: string) {
		onprovider?.(value);
	}

	function handlePromptSelect(prompt: string) {
		inputMessage = prompt;
	}

	function formatTime(date: Date) {
		return new Intl.DateTimeFormat("en-US", {
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		}).format(date);
	}

	function getSourceIcon(source: string) {
		return source === "voice" ? "🎤" : "";
	}
</script>

<section class="flex-1 bg-card brutal-border brutal-shadow flex flex-col overflow-hidden h-full">
	<div class="flex flex-col gap-2 px-5 py-4 border-b-2 border-black dark:border-white bg-secondary">
		<div>
			<h1 class="text-3xl font-black uppercase tracking-tighter text-foreground">
				{title}
			</h1>
			<p class="text-muted-foreground font-bold text-sm">
				{subtitle}
			</p>
		</div>
	</div>

	<div bind:this={container} class="flex-1 overflow-y-auto p-6 space-y-8 bg-background bg-grid-pattern">
		{#each messages as message (message.id)}
			<div class="flex items-start gap-4 {message.role === 'user' ? 'flex-row-reverse' : ''} animate-fade-in">
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
					{#if message.metadata?.toolCalls && message.metadata.toolCalls.length > 0}
						<div class="space-y-2">
							{#each message.metadata.toolCalls as toolCall}
								<div class="p-3 border-2 border-border bg-void text-terminal-green font-mono shadow-brutal-sm">
									<div class="flex items-center gap-2">
										<Wrench class="w-3.5 h-3.5 {toolCall.status === 'running' ? 'animate-spin' : ''}" />
										<span class="text-[11px] font-black uppercase tracking-tight">
											EXEC: {toolCall.name}
										</span>
										<span class="text-[9px] px-1.5 py-0.5 border border-terminal-green bg-terminal-green/10 uppercase font-black">
											{toolCall.status}
										</span>
									</div>
									{#if toolCall.result}
										<div class="text-[10px] mt-2 border-t border-terminal-green/30 pt-2 opacity-80 overflow-hidden">
											<span class="opacity-50">OUTPUT_BUFFER >></span> {typeof toolCall.result === "string"
												? toolCall.result
												: JSON.stringify(toolCall.result)}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{/if}

					<div class="text-[10px] uppercase font-black tracking-widest text-muted-foreground">
						{formatTime(message.timestamp)} {getSourceIcon(message.source)}
					</div>

					<div class="p-4 border-2 border-border bg-card shadow-card">
						<MarkdownRenderer content={message.content} />
					</div>
				</div>
			</div>
		{/each}

		{#if $isProcessing}
			<div class="flex items-center gap-3 opacity-70">
				<div class="w-8 h-8 border-2 border-border animate-spin"></div>
				<div class="flex items-center gap-2 text-terminal-green font-mono text-xs">
					<div class="w-2 h-2 bg-terminal-green animate-ping"></div>
					<span class="text-[11px] font-black uppercase tracking-widest">SYSTEM_THINKING...</span>
				</div>
			</div>
		{/if}
	</div>

	<div class="px-6 py-2 text-xs font-bold uppercase tracking-wider border-t-2 border-black dark:border-white bg-secondary flex items-center justify-between">
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
	</div>

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
