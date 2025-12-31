<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { logger } from '$lib/utils/logger';
	import { Send, Bot, User, Sparkles } from 'lucide-svelte';
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';

	interface Message {
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
	}

let messages: Message[] = [];
let inputMessage = '';
let isLoading = false;
let chatContainer: HTMLDivElement;
let useOrchestrator = false;
let lastPlan: any = null;

	onMount(() => {
		// Load chat history from localStorage
		const savedMessages = localStorage.getItem('chat_history');
		if (savedMessages) {
			try {
				const parsed = JSON.parse(savedMessages);
				messages = parsed.map((m: any) => ({
					...m,
					timestamp: new Date(m.timestamp)
				}));
			} catch (e) {
				logger.error('Failed to parse chat history', e);
			}
		}

		// Add welcome message if empty
		if (messages.length === 0) {
			messages = [
				{
					role: 'assistant',
					content:
						"Hi! I'm your AI assistant powered by Claude and GPT-4. I can help you with task management, natural language processing, and productivity insights. How can I assist you today?",
					timestamp: new Date()
				}
			];
		}
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

		// Scroll to bottom
		setTimeout(() => scrollToBottom(), 100);

		try {
			// Prepare conversation history (last 10 messages)
			const history = messages.slice(-10).map((m) => ({
				role: m.role,
				content: m.content
			}));

			let assistantText = '';
			if (useOrchestrator) {
				const plan: any = await api.ai.orchestrateTask({ input: userMessage.content });
				lastPlan = plan;
				const steps =
					plan.workflow
						?.map((step: any) => `- Step ${step.step}: ${step.action} (${step.estimatedMinutes} min)`)
						.join('\\n') || 'No steps provided.';
				assistantText = `**Main Task:** ${plan.mainTask?.title || 'Untitled'}\\n\\n${steps}\\n\\nConfidence: ${
					plan.confidence ?? 'n/a'
				}`;
			} else {
				const response: any = await api.ai.chat({
					message: userMessage.content,
					conversation_history: history.slice(0, -1) // Exclude current message
				});
				assistantText =
					response.response || response.message || 'I apologize, but I could not generate a response.';
				lastPlan = null;
			}

			const assistantMessage: Message = {
				role: 'assistant',
				content: assistantText,
				timestamp: new Date()
			};

			messages = [...messages, assistantMessage];

			// Save to localStorage
			localStorage.setItem('chat_history', JSON.stringify(messages));

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

	function clearChat() {
		if (confirm('Are you sure you want to clear the chat history?')) {
			messages = [
				{
					role: 'assistant',
					content: "Chat cleared. How can I help you?",
					timestamp: new Date()
				}
			];
			localStorage.removeItem('chat_history');
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

<div class="flex flex-col h-[calc(100vh-8rem)]">
	<!-- Header -->
	<div class="flex items-center justify-between pb-4 border-b border-border">
		<div>
			<h1 class="text-3xl font-bold flex items-center gap-2">
				<Sparkles class="w-8 h-8 text-primary" />
				AI Chat
			</h1>
			<p class="text-muted-foreground mt-1">Powered by Claude & GPT-4</p>
		</div>
		<div class="flex items-center gap-4">
			<label class="inline-flex items-center gap-2 text-sm">
				<input type="checkbox" bind:checked={useOrchestrator} class="rounded border-border" />
				Use Orchestrator
			</label>
			<button
				onclick={clearChat}
				class="px-4 py-2 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors"
			>
				Clear Chat
			</button>
		</div>
	</div>

	<!-- Messages -->
	<div bind:this={chatContainer} class="flex-1 overflow-y-auto py-6 space-y-4">
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
				<div class="flex-1 max-w-3xl">
					<div
						class="p-4 rounded-lg {message.role === 'user'
							? 'bg-primary text-primary-foreground ml-auto'
							: 'bg-card border border-border'}"
					>
						{#if message.role === 'user'}
							<p class="whitespace-pre-wrap break-words">{message.content}</p>
						{:else}
							<MarkdownRenderer content={message.content} />
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
				<div class="flex-1 max-w-3xl">
					<div class="p-4 rounded-lg bg-card border border-border">
						<div class="flex gap-2">
							<div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 0ms"></div>
							<div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 150ms"></div>
							<div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 300ms"></div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	{#if lastPlan}
		<div class="bg-card border border-border rounded-lg p-4 mb-4">
			<h2 class="text-lg font-semibold mb-2">Orchestrated Workflow</h2>
			<p class="text-sm text-muted-foreground mb-2">Main Task: {lastPlan.mainTask?.title || 'Untitled'}</p>
			<ul class="list-disc pl-5 space-y-1">
				{#each lastPlan.workflow || [] as step}
					<li>Step {step.step}: {step.action} ({step.estimatedMinutes} min)</li>
				{/each}
			</ul>
		</div>
	{/if}

	<!-- Input -->
	<div class="pt-4 border-t border-border">
		<form onsubmit={(e) => { e.preventDefault(); handleSendMessage(); }} class="flex gap-3">
			<input
				type="text"
				bind:value={inputMessage}
				placeholder="Type your message... (e.g., 'Create a task for tomorrow')"
				disabled={isLoading}
				class="flex-1 px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
			/>
			<button
				type="submit"
				disabled={isLoading || !inputMessage.trim()}
				class="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
			>
				<Send class="w-4 h-4" />
				<span class="hidden sm:inline">Send</span>
			</button>
		</form>
		<p class="text-xs text-muted-foreground mt-2">
			Try: "Create a high priority task for tomorrow" or "Analyze my productivity patterns"
		</p>
	</div>
</div>
