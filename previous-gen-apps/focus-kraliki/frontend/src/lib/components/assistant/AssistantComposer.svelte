<script lang="ts">
	import {
		SendIcon as Send,
		MicIcon as Mic,
		MicOffIcon as MicOff,
		UploadCloudIcon as UploadCloud,
	} from "lucide-svelte";

	interface Props {
		inputMessage?: string;
		isLoading?: boolean;
		isRecording?: boolean;
		isProcessingAudio?: boolean;
		supportsRecording?: boolean;
		quickPrompts?: string[];
		voiceProvider?: string;
		voiceStatus?: { providers: Record<string, boolean> } | null;
		recordingError?: string | null;
		uploadError?: string | null;
		onsend?: () => void;
		onrecord?: () => void;
		onstop?: () => void;
		onupload?: (event: Event) => void;
		onprovider?: (value: string) => void;
		onprompt?: (prompt: string) => void;
	}

	let {
		inputMessage = $bindable(""),
		isLoading = false,
		isRecording = false,
		isProcessingAudio = false,
		supportsRecording = false,
		quickPrompts = [],
		voiceProvider = $bindable("gemini-native"),
		voiceStatus = null,
		recordingError = null,
		uploadError = null,
		onsend,
		onrecord,
		onstop,
		onupload,
		onprovider,
		onprompt,
	}: Props = $props();

	let fileInput: HTMLInputElement | null = $state(null);

	function triggerAudioUpload() {
		fileInput?.click();
	}

	function handleProviderChange(event: Event) {
		const target = event.currentTarget as HTMLSelectElement | null;
		if (target && onprovider) {
			onprovider(target.value);
		}
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		onsend?.();
	}
</script>

<div
	class="p-4 border-t-2 border-border space-y-4 bg-background"
>
	<form onsubmit={handleSubmit} class="flex flex-col gap-3">
		<div class="flex flex-col gap-3 md:flex-row">
			<input
				type="text"
				bind:value={inputMessage}
				placeholder="SPEAK YOUR INTENT..."
				class="brutal-input"
				disabled={isLoading}
			/>
			<div class="flex gap-2">
				<button
					type="button"
					class="brutal-btn flex-1 md:flex-none flex items-center justify-center gap-2 whitespace-nowrap bg-white text-black dark:bg-card dark:text-foreground"
					onclick={() => (isRecording ? onstop?.() : onrecord?.())}
					disabled={isProcessingAudio || !supportsRecording}
				>
					{#if isRecording}
						<MicOff class="w-4 h-4 text-system-red" />
						STOP
					{:else}
						<Mic class="w-4 h-4" />
						RECORD
					{/if}
				</button>
				<button
					type="submit"
					class="brutal-btn px-8 bg-primary text-primary-foreground flex items-center justify-center gap-2"
					disabled={isLoading || !inputMessage.trim()}
				>
					<Send class="w-4 h-4" />
					SEND
				</button>
			</div>
		</div>

		<div class="flex flex-wrap gap-2">
			{#each quickPrompts as prompt}
				<button
					type="button"
					onclick={() => onprompt?.(prompt)}
					class="text-[10px] font-black uppercase px-2 py-1 border-2 border-border bg-card hover:bg-terminal-green hover:text-void transition-colors"
				>
					{prompt}
				</button>
			{/each}
		</div>

		<div
			class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-[10px] font-black uppercase tracking-widest border-t border-border/30 pt-3"
		>
			<div class="flex items-center gap-4">
				<div class="flex items-center gap-2">
					<input
						bind:this={fileInput}
						id="audio-upload"
						type="file"
						accept="audio/*"
						class="hidden"
						onchange={(event) => onupload?.(event)}
					/>
					<button
						type="button"
						class="flex items-center gap-1 hover:text-terminal-green transition-colors"
						onclick={triggerAudioUpload}
					>
						<UploadCloud class="w-3.5 h-3.5" />
						UPLOAD_AUDIO
					</button>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-muted-foreground">PROVIDER:</span>
					<select
						bind:value={voiceProvider}
						class="bg-card border-2 border-border px-2 py-0.5 focus:outline-none focus:border-terminal-green transition-colors cursor-pointer"
						onchange={handleProviderChange}
					>
						<option value="gemini-native">GEMINI_NATIVE</option>
						<option value="openai-realtime">OPENAI_REALTIME</option>
					</select>
				</div>
			</div>
			
			<div class="flex items-center gap-3">
				{#if voiceStatus}
					<span class="text-muted-foreground opacity-50">
						ACTIVE: {Object.keys(voiceStatus.providers || {}).join(
							" | ",
						)}
					</span>
				{/if}
				{#if recordingError}
					<span class="text-system-red animate-pulse">ERROR: {recordingError}</span
					>
				{:else if uploadError}
					<span class="text-system-red animate-pulse">ERROR: {uploadError}</span>
				{/if}
			</div>
		</div>
	</form>
</div>
