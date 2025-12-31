<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { knowledgeStore } from '$lib/stores/knowledge';
	import { Send, Bot, User, Sparkles } from 'lucide-svelte';
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';
	import ModelPicker from '$lib/components/ModelPicker.svelte';

	interface Message {
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
		model?: string;
	}

	let messages: Message[] = [];
	let inputMessage = '';
	let isLoading = false;
	let chatContainer: HTMLDivElement;
	let selectedModel = 'google/gemini-3-flash-preview';

	function handleModelChange(modelId: string) {
		selectedModel = modelId;
	}

	onMount(() => {
		// Add welcome message
		messages = [
			{
				role: 'assistant',
				content:
					"Hi! I'm your AI Knowledge Assistant. I can help you create and manage your knowledge items. Try saying 'Create a note about my project ideas' or 'Add a task to review documentation'.",
				timestamp: new Date()
			}
		];
	});

	async function handleSendMessage() {
		if (!inputMessage.trim() || isLoading) return;

		const userMessage: Message = {
			role: 'user',
			content: inputMessage.trim(),
			timestamp: new Date()
		};

		messages = [...messages, userMessage];
		inputMessage = '';
		isLoading = true;

		setTimeout(() => scrollToBottom(), 100);

		try {
			// Prepare conversation history
			const history = messages.slice(-10).map((m) => ({
				role: m.role,
				content: m.content
			}));

			// Call AI chat endpoint with selected model
			const response: any = await api.ai.chat({
				message: userMessage.content,
				conversation_history: history.slice(0, -1),
				model: selectedModel
			});

			const assistantMessage: Message = {
				role: 'assistant',
				content:
					response.response || response.message || 'I apologize, but I could not generate a response.',
				timestamp: new Date(),
				model: response.model || selectedModel
			};

			messages = [...messages, assistantMessage];

			// Refresh knowledge items to show any AI-created items
			await knowledgeStore.loadKnowledgeItems();

			setTimeout(() => scrollToBottom(), 100);
		} catch (error: any) {
			const errorMessage: Message = {
				role: 'assistant',
				content: `Sorry, I encountered an error: ${error.detail || 'Unknown error'}`,
				timestamp: new Date()
			};
			messages = [...messages, errorMessage];
		} finally {
			isLoading = false;
		}
	}

	function scrollToBottom() {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	function formatTime(date: Date): string {
		return new Intl.DateTimeFormat('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true
		}).format(date);
	}
</script>

<div class="flex flex-col h-[500px] bg-card border border-border rounded-lg">
	<!-- Header -->
	<div class="p-4 border-b border-border space-y-3">
		<div class="flex items-center gap-2">
			<Sparkles class="w-5 h-5 text-primary" />
			<h3 class="font-semibold">AI Knowledge Assistant</h3>
		</div>
		<!-- Model Picker -->
		<ModelPicker {selectedModel} onModelChange={handleModelChange} compact={true} />
	</div>

	<!-- Messages -->
	<div bind:this={chatContainer} class="flex-1 overflow-y-auto p-4 space-y-4">
		{#each messages as message (message.timestamp.getTime())}
			<div class="flex items-start gap-3 {message.role === 'user' ? 'flex-row-reverse' : ''}">
				<!-- Avatar -->
				<div
					class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 {message.role ===
					'user'
						? 'bg-primary text-primary-foreground'
						: 'bg-accent text-accent-foreground'}"
				>
					{#if message.role === 'user'}
						<User class="w-4 h-4" />
					{:else}
						<Bot class="w-4 h-4" />
					{/if}
				</div>

				<!-- Message Bubble -->
				<div class="flex-1 max-w-[85%]">
					<div
						class="p-3 rounded-lg {message.role === 'user'
							? 'bg-primary text-primary-foreground ml-auto'
							: 'bg-accent'}"
					>
						{#if message.role === 'user'}
							<p class="text-sm whitespace-pre-wrap break-words">{message.content}</p>
						{:else}
							<div class="text-sm">
								<MarkdownRenderer content={message.content} />
							</div>
						{/if}
					</div>
					<p class="text-xs text-muted-foreground mt-1 {message.role === 'user' ? 'text-right' : ''}">
						{formatTime(message.timestamp)}
					</p>
				</div>
			</div>
		{/each}

		{#if isLoading}
			<div class="flex items-start gap-3">
				<div class="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
					<Bot class="w-4 h-4" />
				</div>
				<div class="flex-1 max-w-[85%]">
					<div class="p-3 rounded-lg bg-accent">
						<div class="flex gap-2">
							<div
								class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
								style="animation-delay: 0ms"
							></div>
							<div
								class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
								style="animation-delay: 150ms"
							></div>
							<div
								class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
								style="animation-delay: 300ms"
							></div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Input -->
	<div class="p-4 border-t border-border">
		<form onsubmit={(e) => { e.preventDefault(); handleSendMessage(); }} class="flex gap-2">
			<input
				type="text"
				bind:value={inputMessage}
				placeholder="Ask AI to create knowledge items..."
				disabled={isLoading}
				class="flex-1 px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 text-sm"
			/>
			<button
				type="submit"
				disabled={isLoading || !inputMessage.trim()}
				class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				<Send class="w-4 h-4" />
			</button>
		</form>
		<p class="text-xs text-muted-foreground mt-2">
			Try: "Create a note about meeting highlights" or "Add a task to review code"
		</p>
	</div>
</div>
