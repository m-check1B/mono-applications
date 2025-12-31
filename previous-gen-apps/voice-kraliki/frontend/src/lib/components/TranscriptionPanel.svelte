<script lang="ts">
import { MessageCircle, User, Bot } from 'lucide-svelte';

interface TranscriptMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

interface Props {
	messages?: TranscriptMessage[];
	segments?: TranscriptMessage[];
	isLive?: boolean;
}

let { messages = [], segments = [], isLive = false }: Props = $props();

// Use segments if provided, otherwise use messages
const displayMessages = segments.length > 0 ? segments : messages;

function formatTime(date: Date): string {
	return date.toLocaleTimeString('en-US', {
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit'
	});
}

function getRoleLabel(role: string): string {
	return role === 'user' ? 'Customer' : 'AI Agent';
}

function getRoleIcon(role: string) {
	return role === 'user' ? User : Bot;
}

function getRoleColor(role: string): string {
	return role === 'user' ? 'text-cyan-data' : 'text-terminal-green';
}

function getBgColor(role: string): string {
	return role === 'user' ? 'bg-cyan-data/5' : 'bg-terminal-green/5';
}
</script>

<article class="brutal-card h-full flex flex-col" role="region" aria-label="Live transcription">
	<div class="flex items-center justify-between mb-6 border-b-2 border-foreground pb-4">
		<div class="flex items-center gap-3">
			<MessageCircle class="size-5 text-foreground" aria-hidden="true" />
			<h2 class="text-xl font-display uppercase tracking-tight">Transcription</h2>
			{#if isLive}
				<span class="inline-flex items-center gap-1.5 border-2 border-terminal-green bg-void px-2 py-0.5 text-[10px] font-bold uppercase text-terminal-green" role="status" aria-live="polite">
					<span class="size-1.5 animate-pulse bg-terminal-green" aria-hidden="true"></span>
					Live_Feed
					<span class="sr-only">Transcription is live</span>
				</span>
			{/if}
		</div>
		<span class="text-[10px] font-mono font-bold uppercase tracking-widest text-muted-foreground" role="status" aria-live="polite" aria-atomic="true">
			[{displayMessages.length}] Segments
		</span>
	</div>

	<div class="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversation transcript">
		{#if displayMessages.length === 0}
			<div class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-muted/20" role="status">
				<div class="relative mb-6">
					<MessageCircle class="size-16 text-muted/10" aria-hidden="true" />
					<div class="absolute inset-0 flex items-center justify-center">
						<span class="text-terminal-green animate-pulse font-mono text-xs">AWAITING_SIGNAL...</span>
					</div>
				</div>
				<p class="text-[11px] font-bold uppercase tracking-[0.2em] text-muted-foreground max-w-xs">
					No active stream detected. Start a call to initiate real-time logging.
				</p>
			</div>
		{:else}
			{#each displayMessages as message (message.timestamp)}
				<div class="border-2 border-foreground p-4 relative group hover:shadow-[4px_4px_0px_0px_rgba(51,255,0,0.5)] transition-all {getBgColor(message.role)}" role="article" aria-label="{getRoleLabel(message.role)} message">
					<div class="flex items-start gap-4">
						<div class={`border-2 border-foreground p-2 bg-void ${getRoleColor(message.role)}`} aria-hidden="true">
							<svelte:component this={getRoleIcon(message.role)} class="size-4" />
						</div>
						<div class="flex-1 space-y-2">
							<div class="flex items-center justify-between border-b border-foreground/10 pb-1">
								<span class={`text-[10px] font-black uppercase tracking-widest ${getRoleColor(message.role)}`}>
									// {getRoleLabel(message.role)}
								</span>
								<time class="text-[9px] font-mono font-bold text-muted-foreground" datetime={message.timestamp.toISOString()}>
									{formatTime(message.timestamp)}
								</time>
							</div>
							<p class="text-sm font-mono leading-relaxed text-foreground">
								{message.content}
							</p>
						</div>
					</div>
					{#if message.role === 'assistant'}
						<div class="absolute top-0 right-0 p-1">
							<div class="w-1 h-1 bg-terminal-green animate-pulse"></div>
						</div>
					{/if}
				</div>
			{/each}
		{/if}
	</div>
</article>

<style>
	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: hsl(var(--border));
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: var(--terminal-green);
	}
</style>
