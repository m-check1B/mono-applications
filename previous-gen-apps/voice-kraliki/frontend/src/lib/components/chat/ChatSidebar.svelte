<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { chatStore, activeSession } from '$lib/stores/chat';
	import { apiGet, apiPost } from '$lib/utils/api';
	import { Plus, Phone, Users, Settings, Search } from 'lucide-svelte';

	interface Session {
		id: string;
		customerName: string;
		lastMessage: string;
		timestamp: Date;
		status: 'active' | 'ended';
		unreadCount: number;
		provider: string;
		context?: {
			voiceSessionId?: string;
			campaign?: string;
		};
	}

	interface ChatSessionApi {
		id: string;
		status: string;
		created_at?: string;
		last_activity?: string;
		last_message?: string;
		unread_count?: number;
		provider?: string;
		context?: Record<string, unknown>;
		customer_info?: {
			name?: string;
		};
	}

	interface ChatSessionListResponse {
		sessions: ChatSessionApi[];
	}

	let showNewSessionDialog = $state(false);
	let searchQuery = $state('');
	let filterStatus = $state<'all' | 'active' | 'ended'>('all');

	let sessions = $state<Session[]>([]);

	onMount(() => {
		// Load sessions from API
		loadSessions();
	});

	async function loadSessions() {
		try {
			const response = await apiGet<ChatSessionListResponse>('/api/chat/sessions');
			sessions = response.sessions.map((session) => {
				const context = (session.context ?? {}) as Record<string, unknown>;
				const timestampSource = session.last_activity ?? session.created_at;
				const timestamp = timestampSource ? new Date(timestampSource) : new Date();
				const customerName =
					session.customer_info?.name ||
					(context.customer_name as string | undefined) ||
					(context.customerName as string | undefined) ||
					'Unknown Customer';

				return {
					id: session.id,
					customerName,
					lastMessage: session.last_message ?? '',
					timestamp,
					status: session.status === 'active' ? 'active' : 'ended',
					unreadCount: session.unread_count ?? 0,
					provider: session.provider ?? '',
					context: {
						voiceSessionId:
							(context.voiceSessionId as string | undefined) ||
							(context.voice_session_id as string | undefined),
						campaign: context.campaign as string | undefined
					}
				};
			});
		} catch (error) {
			console.error('Failed to load sessions', error);
		}
	}

	function createNewSession() {
		const sessionId = `session_${Date.now()}`;
		const userId = 'user_123'; // Get from auth
		const companyId = 'company_456'; // Get from user context

		chatStore.initializeSession({ sessionId, userId, companyId });
		chatStore.setActiveSession(sessionId);

		// Add to sessions list
		sessions = [
			{
				id: sessionId,
				customerName: 'New Customer',
				lastMessage: 'Session started',
				timestamp: new Date(),
				status: 'active',
				unreadCount: 0,
				provider: 'gemini',
				context: {}
			},
			...sessions
		];

		showNewSessionDialog = false;
	}

	async function selectSession(sessionId: string) {
		chatStore.setActiveSession(sessionId);
		// Clear unread count for this session
		const session = sessions.find(s => s.id === sessionId);
		if (session) {
			session.unreadCount = 0;
		}
		try {
			await apiPost(`/api/chat/sessions/${sessionId}/read`, {});
		} catch (error) {
			console.error('Failed to mark session as read', error);
		}
	}

	function navigateToVoiceSession(voiceSessionId?: string) {
		if (!voiceSessionId) return;
		const params = new URLSearchParams({ voice_session_id: voiceSessionId });
		goto(`/calls/agent?${params.toString()}`);
	}

	function formatTime(date: Date) {
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const minutes = Math.floor(diff / (1000 * 60));
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (minutes < 1) return 'Just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days < 7) return `${days}d ago`;
		return date.toLocaleDateString();
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'active':
				return 'bg-green-100 text-green-800';
			case 'ended':
				return 'bg-gray-100 text-gray-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	const filteredSessions = $derived(sessions.filter(session => {
		const matchesSearch = session.customerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
			session.lastMessage.toLowerCase().includes(searchQuery.toLowerCase());
		const matchesFilter = filterStatus === 'all' || session.status === filterStatus;
		return matchesSearch && matchesFilter;
	}));
</script>

<div class="flex h-full flex-col bg-background">
	<!-- Header -->
	<div class="border-b border-divider-subtle p-4">
		<div class="mb-4 flex items-center justify-between">
			<h3 class="text-lg font-semibold text-text-primary">Chat Sessions</h3>
			<button
				onclick={() => showNewSessionDialog = true}
				class="flex size-8 items-center justify-center rounded-lg bg-primary text-white hover:bg-primary/90"
				title="New session"
			>
				<Plus class="size-4" />
			</button>
		</div>

		<!-- Search -->
		<div class="relative mb-3">
			<Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-muted" />
			<input
				bind:value={searchQuery}
				type="text"
				placeholder="Search sessions..."
				class="w-full rounded-lg border border-divider-subtle bg-background pl-10 pr-4 py-2 text-sm placeholder-text-muted focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
			/>
		</div>

		<!-- Filter -->
		<div class="flex gap-2">
			{#each ['all', 'active', 'ended'] as status}
				{@const statusValue = status as 'all' | 'active' | 'ended'}
				<button
					onclick={() => filterStatus = statusValue}
					class="rounded-lg px-3 py-1 text-xs font-medium capitalize {
						filterStatus === statusValue
							? 'bg-primary text-white'
							: 'bg-secondary text-text-secondary hover:bg-secondary-hover'
					}"
				>
					{status}
				</button>
			{/each}
		</div>
	</div>

	<!-- Sessions List -->
	<div class="flex-1 overflow-y-auto">
		{#each filteredSessions as session (session.id)}
			<div
				onclick={() => selectSession(session.id)}
				class="flex cursor-pointer gap-3 border-b border-divider-subtle p-4 hover:bg-secondary-hover {
					$activeSession?.id === session.id ? 'bg-secondary-hover' : ''
				}"
			>
				<!-- Avatar -->
				<div class="flex size-10 flex-shrink-0 items-center justify-center rounded-full bg-primary text-white">
					<Users class="size-5" />
				</div>

				<!-- Session Info -->
				<div class="flex-1 min-w-0">
					<div class="flex items-center justify-between gap-2">
						<h4 class="truncate text-sm font-medium text-text-primary">
							{session.customerName}
						</h4>
						<span class="text-xs text-text-muted">{formatTime(session.timestamp)}</span>
					</div>

					<div class="mt-1 flex items-center justify-between gap-2">
						<p class="truncate text-xs text-text-secondary">{session.lastMessage}</p>
						{#if session.unreadCount > 0}
							<span class="flex size-5 items-center justify-center rounded-full bg-primary text-xs text-white">
								{session.unreadCount}
							</span>
						{/if}
					</div>

					<div class="mt-2 flex items-center gap-2">
						<span class="rounded-full px-2 py-0.5 text-xs font-medium {getStatusColor(session.status)}">
							{session.status}
						</span>
						{#if session.provider}
							<span class="rounded bg-tertiary px-2 py-0.5 text-xs text-text-muted">
								{session.provider}
							</span>
						{/if}
						{#if session.context?.voiceSessionId}
							<button
								onclick={(e) => {
									e.stopPropagation();
									navigateToVoiceSession(session.context?.voiceSessionId);
								}}
								class="rounded bg-tertiary px-2 py-0.5 text-xs text-text-muted hover:bg-secondary-hover"
								title="Go to voice session"
							>
								<Phone class="inline size-3" />
							</button>
						{/if}
					</div>
				</div>
			</div>
		{:else}
			<div class="flex flex-1 items-center justify-center p-8 text-center">
				<Users class="mx-auto mb-2 size-8 text-text-muted" />
				<p class="text-sm text-text-muted">
					{searchQuery ? 'No sessions found' : 'No sessions yet'}
				</p>
			</div>
		{/each}
	</div>

	<!-- Footer -->
	<div class="border-t border-divider-subtle p-4">
		<button class="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm text-text-secondary hover:bg-secondary-hover">
			<Settings class="size-4" />
			Chat Settings
		</button>
	</div>
</div>

<!-- New Session Dialog -->
{#if showNewSessionDialog}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
		<div class="w-full max-w-md rounded-xl bg-background p-6 shadow-card">
			<h3 class="mb-4 text-lg font-semibold text-text-primary">Start New Chat Session</h3>
			<p class="mb-6 text-sm text-text-secondary">
				Create a new chat session to start assisting customers.
			</p>
			<div class="flex gap-3">
				<button
					onclick={createNewSession}
					class="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
				>
					Create Session
				</button>
				<button
					onclick={() => showNewSessionDialog = false}
					class="flex-1 rounded-lg border border-divider-subtle px-4 py-2 text-sm font-medium text-text-secondary hover:bg-secondary-hover"
				>
					Cancel
				</button>
			</div>
		</div>
	</div>
{/if}

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
</style>
