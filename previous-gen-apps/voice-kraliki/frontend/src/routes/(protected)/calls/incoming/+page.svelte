<script lang="ts">
	import { onDestroy } from 'svelte';
	import { useAppConfig } from '$lib/hooks/useAppConfig';
	import { Radio, PhoneIncoming, ShieldCheck, RefreshCcw, PhoneOff, PhoneCall } from 'lucide-svelte';
	import { createIncomingSession } from '$lib/services/incomingSession';
import { createProviderHealthStore, type ProviderHealthResponse } from '$lib/services/providerHealth';
	import AIInsightsPanel from '$lib/components/AIInsightsPanel.svelte';

	const config = useAppConfig();
	const incomingSession = createIncomingSession('/test-inbound');
	let incoming = $state(incomingSession.getState());
	const unsubscribeSession = incomingSession.subscribe((value) => {
		incoming = value;
	});

	const healthStore = createProviderHealthStore();
let health = $state<ProviderHealthResponse | null>(null);
	const unsubscribeHealth = healthStore.subscribe((value) => {
		health = value;
	});

// AI Insights state
interface TranscriptMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

interface IntentAnalysis {
	intent: string;
	confidence: number;
	category: 'inquiry' | 'complaint' | 'purchase' | 'support' | 'general';
	keywords: string[];
}

interface SentimentAnalysis {
	sentiment: 'positive' | 'neutral' | 'negative';
	score: number;
	confidence: number;
	emotions: {
		joy?: number;
		anger?: number;
		fear?: number;
		sadness?: number;
	};
}

interface Suggestion {
	id: string;
	type: 'response' | 'action' | 'escalation';
	title: string;
	description: string;
	priority: 'high' | 'medium' | 'low';
	confidence: number;
	status: 'pending' | 'accepted' | 'rejected';
	timestamp: Date;
}

let transcriptMessages = $state<TranscriptMessage[]>([]);
let currentIntent = $state<IntentAnalysis | null>(null);
let currentSentiment = $state<SentimentAnalysis | null>(null);
let suggestions = $state<Suggestion[]>([]);

	let enabled = $state(false);
	let autoAccept = $state(true);

	function toggleListening() {
		enabled = !enabled;
		if (enabled) {
			incomingSession.connect();
		} else {
			incomingSession.disconnect();
		}
	}

	function resetState() {
		enabled = false;
		autoAccept = true;
		incomingSession.disconnect();
	}

	function acceptCall() {
		void incomingSession.accept();
	}

	function declineCall() {
		incomingSession.decline();
	}

	const hasActiveCall = $derived(Boolean(incoming.activeCall));
	let lastAcceptedFrom = $state<string | undefined>(undefined);

	$effect(() => {
		if (!enabled || !autoAccept) return;
		const caller = incoming.activeCall?.from;
		if (!caller) return;
		if (lastAcceptedFrom === caller && incoming.audioStatus === 'recording') return;
		lastAcceptedFrom = caller;
		void incomingSession.accept();
	});

	$effect(() => {
		if (!incoming.activeCall) {
			lastAcceptedFrom = undefined;
		}
	});

	// Process incoming session events for AI insights
	$effect(() => {
		if (incoming.lastEvent && typeof incoming.lastEvent === 'object') {
			const event = incoming.lastEvent as {
				type?: string;
				text?: string;
				role?: 'user' | 'assistant';
				data?: any;
			};
			
			// Capture transcription events
			if (event.type === 'transcription' && event.text && event.role) {
				transcriptMessages = [
					...transcriptMessages,
					{
						role: event.role,
						content: event.text,
						timestamp: new Date()
					}
				];
			}
			// Capture text output events
			if (event.type === 'text' && event.text) {
				transcriptMessages = [
					...transcriptMessages,
					{
						role: 'assistant',
						content: event.text,
						timestamp: new Date()
					}
				];
			}
			// Capture AI insights events
			if (event.type === 'intent-analysis') {
				currentIntent = event.data as IntentAnalysis;
			}
			if (event.type === 'sentiment-analysis') {
				currentSentiment = event.data as SentimentAnalysis;
			}
			if (event.type === 'suggestion') {
				const suggestion: Suggestion = {
					id: event.data.id || Math.random().toString(36).substr(2, 9),
					type: event.data.type || 'response',
					title: event.data.title || 'AI Suggestion',
					description: event.data.description || '',
					priority: event.data.priority || 'medium',
					confidence: event.data.confidence || 0.5,
					status: 'pending',
					timestamp: new Date()
				};
				suggestions = [...suggestions, suggestion];
			}
		}
	});

	function handleSuggestionAction(suggestionId: string, action: 'accept' | 'reject') {
		suggestions = suggestions.map(s => 
			s.id === suggestionId 
				? { ...s, status: action === 'accept' ? 'accepted' : 'rejected' }
				: s
		);
		
		// Send the action back to the backend for logging/execution
		if (action === 'accept') {
			const suggestion = suggestions.find(s => s.id === suggestionId);
			if (suggestion) {
				// Note: incomingSession would need to support sending messages back
				// For now, we'll just log it
				console.log('Accepted suggestion:', suggestion);
			}
		}
	}

	function formatStatus(status: string) {
		switch (status) {
			case 'connecting':
				return 'Connecting…';
			case 'connected':
				return 'Connected';
			case 'error':
				return 'Error';
			default:
				return 'Idle';
		}
	}

	healthStore.start();

	onDestroy(() => {
		incomingSession.disconnect();
		unsubscribeSession();
		healthStore.stop();
		unsubscribeHealth();
	});
</script>

<section class="space-y-6">
	<header class="space-y-1">
		<h1 class="text-2xl font-semibold text-text-primary">Incoming Call Control</h1>
		<p class="text-sm text-text-muted">
			Connect WebSocket listeners, monitor provider health, and auto-route callers using Stack 2026 ergonomics.
		</p>
	</header>

	<div class="grid gap-4 lg:grid-cols-[2fr_3fr]">
		<article class="card">
			<div class="card-header">
				<h2 class="text-lg font-semibold text-text-primary">Provider Connection</h2>
				<button class="btn btn-ghost" onclick={resetState}>
					<RefreshCcw class="size-4" /> Reset
				</button>
			</div>
			<div class="space-y-4">
				<div class="rounded-2xl border border-divider bg-secondary p-4 text-sm text-text-secondary">
					<p class="font-medium text-text-primary">WebSocket Endpoint</p>
					<p class="mt-1 text-xs text-text-muted">{config.wsUrl}/test-inbound</p>
					<p class="mt-1 text-xs text-text-muted">Session: {formatStatus(incoming.session.status)}</p>
				</div>
				<div class="flex items-center justify-between rounded-2xl border border-divider bg-secondary/70 px-4 py-3">
					<div>
						<p class="text-sm font-medium text-text-primary">Auto-Accept Calls</p>
						<p class="text-xs text-text-muted">Automatically answer inbound callers using the active campaign script.</p>
					</div>
					<label class="relative inline-flex cursor-pointer items-center">
						<input type="checkbox" class="peer sr-only" bind:checked={autoAccept} />
						<span class="peer h-6 w-11 rounded-full bg-divider transition peer-checked:bg-primary-soft"></span>
						<span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-text-muted transition peer-checked:translate-x-5 peer-checked:bg-primary"></span>
					</label>
				</div>
				<div class="flex gap-2">
					<button class={`btn ${enabled ? 'btn-secondary' : 'btn-primary'}`} onclick={toggleListening}>
						{#if enabled}
							<ShieldCheck class="size-4" /> Listening...
						{:else}
							<PhoneIncoming class="size-4" /> Start Listening
						{/if}
					</button>
					{#if enabled}
						<button class="btn btn-ghost" onclick={() => incomingSession.disconnect()}>
							<PhoneOff class="size-4" /> Disconnect
						</button>
					{/if}
				</div>
				{#if hasActiveCall}
					<div class="rounded-xl border border-primary-soft bg-primary-soft/20 px-4 py-3 text-sm text-text-secondary">
						<p class="font-semibold text-text-primary">Incoming call from {incoming.activeCall?.from ?? 'Unknown'}</p>
						<div class="mt-2 flex gap-2">
							<button class="btn btn-primary" onclick={acceptCall}>
								<PhoneCall class="size-4" /> Accept
							</button>
							<button class="btn btn-ghost" onclick={declineCall}>
								<PhoneOff class="size-4" /> Decline
							</button>
						</div>
					</div>
				{/if}
				{#if incoming.error}
					<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">{incoming.error}</p>
				{/if}
			</div>
		</article>

		<AIInsightsPanel
			messages={transcriptMessages}
			isLive={enabled && incoming.session.status === 'connected'}
			intent={currentIntent}
			sentiment={currentSentiment}
			suggestions={suggestions}
			onSuggestionAction={handleSuggestionAction}
		/>

		<article class="card">
		<div class="card-header">
			<div class="flex items-center gap-2 text-text-primary">
				<Radio class="size-5" />
				<h2 class="text-lg font-semibold">Realtime Events</h2>
			</div>
			</div>
			<div class="space-y-3 text-sm text-text-secondary">
				<p class="rounded-2xl border border-divider bg-secondary px-4 py-3">
					{incoming.lastEvent ? JSON.stringify(incoming.lastEvent) : 'No inbound events yet.'}
				</p>
				<p class="text-xs text-text-muted">
					Audio status: {incoming.audioStatus}. When connected, microphone audio streams to Gemini and responses play through the browser.
				</p>
			</div>
		</article>
	</div>

	<article class="card">
		<div class="card-header">
			<h2 class="text-lg font-semibold text-text-primary">Provider Health</h2>
			<button class="btn btn-ghost btn-sm" onclick={() => healthStore.refresh()}>
				<RefreshCcw class="size-4" /> Refresh
			</button>
		</div>
		<div class="space-y-2 text-sm text-text-secondary">
			{#if health}
				<p>Status: {health.providerHealth?.gemini?.status ?? 'unknown'}</p>
				<p>Active connections: {health.activeConnections ?? 0}</p>
				<p class="text-xs text-text-muted">Last updated: {new Date(health.timestamp ?? Date.now()).toLocaleTimeString()}</p>
			{:else}
				<p class="text-xs text-text-muted">Health data not available yet.</p>
			{/if}
		</div>
	</article>
</section>
