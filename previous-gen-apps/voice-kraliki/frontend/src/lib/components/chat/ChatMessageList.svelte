<script lang="ts">
	import { onMount } from 'svelte';
	import type { ChatMessage } from '$lib/stores/chat';
	import { User, Bot, Info } from 'lucide-svelte';

	interface Props {
		messages: ChatMessage[];
		compact?: boolean;
	}

	interface AttachmentMetadata {
		name: string;
		size?: number;
		type?: string;
		text?: string;
	}

	let { messages, compact = false }: Props = $props();

	let messagesContainer: HTMLElement;
	let autoScroll = $state(true);

	onMount(() => {
		// Scroll to bottom when new messages arrive
		const observer = new MutationObserver(() => {
			if (autoScroll) {
				scrollToBottom();
			}
		});

		observer.observe(messagesContainer, {
			childList: true,
			subtree: true
		});

		return () => observer.disconnect();
	});

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function handleScroll() {
		if (messagesContainer) {
			const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
			autoScroll = scrollTop + clientHeight >= scrollHeight - 50;
		}
	}

	function formatTime(date: Date) {
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	function getRoleIcon(role: ChatMessage['role']) {
		switch (role) {
			case 'user':
				return User;
			case 'assistant':
				return Bot;
			case 'system':
				return Info;
			default:
				return User;
		}
	}

	function getRoleColor(role: ChatMessage['role']) {
		switch (role) {
			case 'user':
				return 'bg-primary text-white';
			case 'assistant':
				return 'bg-secondary text-text-primary';
			case 'system':
				return 'bg-tertiary text-text-muted';
			default:
				return 'bg-secondary text-text-primary';
		}
	}

	function getAttachments(message: ChatMessage): AttachmentMetadata[] {
		const attachments = message.metadata?.attachments;
		if (!Array.isArray(attachments)) {
			return [];
		}
		return attachments as AttachmentMetadata[];
	}

	function formatFileSize(size?: number) {
		if (!size) return '';
		if (size < 1024) return `${size} B`;
		if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
		return `${(size / (1024 * 1024)).toFixed(1)} MB`;
	}
</script>

<div
	bind:this={messagesContainer}
	class="flex h-full flex-col space-y-4 overflow-y-auto p-4"
	onscroll={handleScroll}
>
	{#each messages as message (message.id)}
		{@const IconComponent = getRoleIcon(message.role)}
		{@const attachments = getAttachments(message)}
		<div
			class="flex gap-3 {message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}"
			class:compact
		>
			<!-- Avatar -->
			<div class="flex-shrink-0">
				<div
					class="flex size-8 items-center justify-center rounded-full {getRoleColor(message.role)}"
				>
					<IconComponent class="size-4" />
				</div>
			</div>

			<!-- Message Content -->
			<div
				class="flex max-w-[70%] flex-col gap-1"
				class:text-right={message.role === 'user'}
			>
				<!-- Message Bubble -->
				<div
					class="rounded-2xl px-4 py-2 {message.role === 'user'
						? 'bg-primary text-white'
						: 'bg-secondary text-text-primary'}"
				>
					<p class="text-sm leading-relaxed">{message.content}</p>
				</div>

				{#if attachments.length > 0}
					<div class="rounded-lg border border-divider-subtle bg-card px-3 py-2 text-xs text-text-secondary">
						{#each attachments as attachment}
							<div class="flex items-center justify-between gap-2">
								<span class="max-w-[220px] truncate">{attachment.name}</span>
								<span class="text-text-muted">{formatFileSize(attachment.size)}</span>
							</div>
							{#if attachment.text}
								<pre class="mt-1 max-h-40 overflow-auto whitespace-pre-wrap text-[11px] leading-relaxed text-text-muted">{attachment.text}</pre>
							{/if}
						{/each}
					</div>
				{/if}

				<!-- Metadata -->
				<div class="flex items-center gap-2 text-xs text-text-muted">
					<span>{formatTime(message.timestamp)}</span>
					
					{#if message.metadata?.provider}
						<span class="font-medium">{message.metadata.provider}</span>
					{/if}
					
					{#if message.metadata?.confidence}
						<span>{Math.round(message.metadata.confidence * 100)}% confidence</span>
					{/if}
					
					{#if message.metadata?.intent}
						<span class="rounded bg-tertiary px-1 py-0.5">{message.metadata.intent}</span>
					{/if}
					
					{#if message.metadata?.sentiment}
						<span class="rounded bg-tertiary px-1 py-0.5">{message.metadata.sentiment}</span>
					{/if}
				</div>
			</div>
		</div>
	{:else}
		<div class="flex flex-1 items-center justify-center text-text-muted">
			<div class="text-center">
				<Bot class="mx-auto mb-2 size-8 text-text-muted" />
				<p class="text-sm">No messages yet. Start a conversation!</p>
			</div>
		</div>
	{/each}
</div>

<style>
	/* Custom scrollbar */
	.overflow-y-auto::-webkit-scrollbar {
		width: 6px;
	}

	.overflow-y-auto::-webkit-scrollbar-track {
		background: transparent;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb {
		background-color: var(--color-border-subtle);
		border-radius: 3px;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb:hover {
		background-color: var(--color-border-default);
	}

	/* Compact mode */
	.compact {
		gap: 0.5rem;
	}

	.compact .size-8 {
		size: 1.5rem;
	}

	.compact .text-sm {
		font-size: 0.75rem;
	}

	.compact .px-4 {
		padding-left: 0.75rem;
		padding-right: 0.75rem;
	}

	.compact .py-2 {
		padding-top: 0.5rem;
		padding-bottom: 0.5rem;
	}
</style>
