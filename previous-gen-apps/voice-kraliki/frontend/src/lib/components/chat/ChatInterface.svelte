<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { chatStore, activeSession, activeMessages, isConnected } from '$lib/stores/chat';
	import ChatMessageList from './ChatMessageList.svelte';
	import ChatInput from './ChatInput.svelte';
	import ChatSidebar from './ChatSidebar.svelte';
	import ConnectionStatus from './ConnectionStatus.svelte';
	import { MessageCircle, Users, Settings } from 'lucide-svelte';

	let showSidebar = $state(true);
	let wsConnection: WebSocket | null = null;

	onMount(() => {
		// Initialize WebSocket connection for real-time chat
		connectWebSocket();
	});

	onDestroy(() => {
		if (wsConnection) {
			wsConnection.close();
		}
	});

	function connectWebSocket() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsUrl = `${protocol}//${window.location.host}/api/chat/ws`;
		
		wsConnection = new WebSocket(wsUrl);

		wsConnection.onopen = () => {
			chatStore.setConnectionState(true);
			console.log('Chat WebSocket connected');
		};

		wsConnection.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				handleWebSocketMessage(data);
			} catch (error) {
				console.error('Error parsing WebSocket message:', error);
			}
		};

		wsConnection.onclose = () => {
			chatStore.setConnectionState(false);
			console.log('Chat WebSocket disconnected');
			
			// Attempt to reconnect after 3 seconds
			setTimeout(connectWebSocket, 3000);
		};

		wsConnection.onerror = (error) => {
			console.error('Chat WebSocket error:', error);
			chatStore.setConnectionState(false);
		};
	}

	function handleWebSocketMessage(data: any) {
		switch (data.type) {
			case 'message':
				chatStore.addMessage({
					sessionId: data.sessionId,
					role: data.role,
					content: data.content,
					metadata: data.metadata
				});
				break;
			
			case 'typing':
				chatStore.setTypingState(data.isTyping);
				break;
			
			case 'session_update':
				chatStore.updateSessionContext(data.sessionId, data.context);
				break;
			
			default:
				console.log('Unknown WebSocket message type:', data.type);
		}
	}

	async function sendMessage(content: string, metadata?: Record<string, any>) {
		const sessionId = $activeSession?.id;
		if (!sessionId) {
			console.error('No active session');
			return;
		}

		// Use offline-aware message sending
		try {
			await chatStore.sendMessage(sessionId, content, metadata);
		} catch (error) {
			console.error('Failed to send message:', error);
			// Message is already queued by the store, so no need to handle here
		}

		// Also send via WebSocket if connected for real-time updates
		if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
			wsConnection.send(JSON.stringify({
				type: 'message',
				sessionId,
				content,
				metadata
			}));
		}
	}

	function toggleSidebar() {
		showSidebar = !showSidebar;
	}
</script>

<div class="flex h-full gap-4">
	<!-- Chat Sidebar -->
	{#if showSidebar}
		<div class="w-80 flex-shrink-0">
			<ChatSidebar />
		</div>
	{/if}

	<!-- Main Chat Area -->
	<div class="flex flex-1 flex-col">
		<!-- Chat Header -->
		<div class="flex items-center justify-between border-b border-divider-subtle bg-background px-6 py-4">
			<div class="flex items-center gap-3">
				<button
					onclick={toggleSidebar}
					class="rounded-lg p-2 text-text-secondary hover:bg-secondary-hover md:hidden"
					title="Toggle sidebar"
				>
					<Users class="size-5" />
				</button>
				
				<div class="flex items-center gap-2">
					<MessageCircle class="size-5 text-primary" />
					<h2 class="text-lg font-semibold text-text-primary">
						{$activeSession ? `Chat Session ${$activeSession.id.slice(-8)}` : 'No Active Session'}
					</h2>
				</div>
			</div>

			<div class="flex items-center gap-3">
				<ConnectionStatus />
				
				<button
					class="rounded-lg p-2 text-text-secondary hover:bg-secondary-hover"
					title="Chat settings"
				>
					<Settings class="size-5" />
				</button>
			</div>
		</div>

		<!-- Messages Area -->
		<div class="flex-1 overflow-hidden">
			<ChatMessageList messages={$activeMessages} />
		</div>

		<!-- Input Area -->
		<div class="border-t border-divider-subtle bg-background p-4">
			<ChatInput 
				onSendMessage={sendMessage}
				disabled={!$activeSession}
				placeholder={$activeSession ? "Type your message..." : "No active session"}
			/>
		</div>
	</div>
</div>

<style>
	/* Custom scrollbar for chat messages */
	.overflow-hidden {
		overflow: hidden;
	}
</style>
