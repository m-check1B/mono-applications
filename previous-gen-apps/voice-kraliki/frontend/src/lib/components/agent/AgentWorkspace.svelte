<script lang="ts">
	/**
	 * Agent Workspace Component
	 *
	 * Main agent interface that integrates all AI-powered features:
	 * - Call control panel
	 * - Real-time transcription
	 * - AI assistance suggestions
	 * - Sentiment analysis
	 * - Provider switching
	 *
	 * This is the central hub for agent operations.
	 */

	import { onMount, onDestroy } from 'svelte';
	import { get } from 'svelte/store';
	import CallControlPanel from './CallControlPanel.svelte';
	import SentimentIndicator from './SentimentIndicator.svelte';
	import AIAssistancePanel from './AIAssistancePanel.svelte';
	import TranscriptionPanel from '../TranscriptionPanel.svelte';
	import ProviderSwitcher from '../ProviderSwitcher.svelte';
	import EnhancedConnectionStatus from '../EnhancedConnectionStatus.svelte';
	import ScreenShare from '../ScreenShare.svelte';
	import { createEnhancedWebSocket, type EnhancedWebSocketCallbacks } from '$lib/services/enhancedWebSocket';
import { createSessionStateManager } from '$lib/services/sessionStateManager';

import type { SessionState, SessionStatus } from '$lib/services/providerSession';
	import type {
		TranscriptionSegment,
		SentimentAnalysis,
		SentimentTrend,
		AssistanceSuggestion
	} from '$lib/api/aiServices';
	import {
		startTranscription,
		startSentimentAnalysis,
		startAssistance,
		getSentimentTrend
	} from '$lib/api/aiServices';

interface Props {
	session: SessionState | null;
	onEndCall?: () => void;
	onMute?: (muted: boolean) => void;
	onHold?: (held: boolean) => void;
	onTransfer?: () => void;
	onRetryConnection?: () => Promise<void> | void;
}

let {
	session = $bindable(null),
	onEndCall,
	onMute,
	onHold,
	onTransfer,
	onRetryConnection: onRetryConnectionCb
}: Props = $props();

if (!onRetryConnectionCb) {
	onRetryConnectionCb = async () => {};
}

	// State
	const sessionStateManager = createSessionStateManager();

	let transcriptionSegments = $state<TranscriptionSegment[]>([]);
	let currentSentiment = $state<SentimentAnalysis | null>(null);
	let sentimentTrend = $state<SentimentTrend | null>(null);
	let assistanceSuggestions = $state<AssistanceSuggestion[]>([]);
	let wsClient: ReturnType<typeof createEnhancedWebSocket> | null = null;
	let isAIServicesActive = $state(false);
	let callStatus = $state<'idle' | 'connecting' | 'active' | 'ended' | 'error'>('idle');

	// Convert TranscriptionSegment to TranscriptMessage format
	interface TranscriptMessage {
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
	}

	const transcriptMessages = $derived(() => {
		return transcriptionSegments.map(segment => ({
			role: (segment.speaker === 'customer' ? 'user' : 'assistant') as 'user' | 'assistant',
			content: segment.text,
			timestamp: new Date(segment.timestamp)
		}));
	});

	function mapSessionStatus(status: SessionStatus): typeof callStatus {
		switch (status) {
			case 'connecting':
				return 'connecting';
			case 'connected':
				return 'active';
			case 'error':
				return 'error';
			case 'disconnected':
				return 'ended';
			default:
				return 'idle';
		}
	}

	onMount(() => {
		sessionStateManager.restoreState();
		const restoredState = get(sessionStateManager);
		callStatus = restoredState.call?.status ?? 'idle';

		return () => {
			sessionStateManager.saveState();
		};
	});

	$effect(() => {
		const currentSession = session;

		if (!currentSession) {
			callStatus = 'idle';
			sessionStateManager.updateCallState({ status: 'idle' });
			sessionStateManager.saveState();
			return;
		}

		const nextStatus = mapSessionStatus(currentSession.status);
		const persistedState = get(sessionStateManager);
		const currentCallId = currentSession.sessionId ?? persistedState.call?.id ?? '';

		callStatus = nextStatus;

		sessionStateManager.updateProvider(currentSession.provider);
		sessionStateManager.updateCallState({
			id: currentCallId,
			status: nextStatus,
			provider: currentSession.provider,
			metadata: {
				lastEvent: currentSession.lastEvent,
				lastEventAt: currentSession.lastEventAt
			}
		});

		if (currentSession.error) {
			sessionStateManager.addError({
				code: 'provider_session_error',
				message: currentSession.error,
				recoverable: true
			});
		}

		sessionStateManager.saveState();
	});

	// Initialize AI services when session becomes active
	$effect(() => {
		const sessionSnapshot = session;
		if (sessionSnapshot && sessionSnapshot.status === 'connected' && sessionSnapshot.sessionId && !isAIServicesActive) {
			initializeAIServices(sessionSnapshot.sessionId);
			isAIServicesActive = true;
		} else if ((!sessionSnapshot || sessionSnapshot.status !== 'connected') && isAIServicesActive) {
			shutdownAIServices();
			isAIServicesActive = false;
		}
	});

	/**
	 * Initialize all AI services for the session
	 */
	async function initializeAIServices(sessionId: string) {
		console.log('🤖 Initializing AI services for session:', sessionId);

		try {
			// Start transcription service
			await startTranscription(sessionId, {
				language: 'en',
				enable_interim_results: true,
				enable_speaker_detection: true,
				enable_punctuation: true
			});

			// Start sentiment analysis
			await startSentimentAnalysis(sessionId, {
				enable_real_time: true,
				enable_emotions: true,
				alert_on_negative: true,
				negative_threshold: -0.5,
				track_trends: true
			});

			// Start agent assistance
			await startAssistance(sessionId, {
				enable_suggestions: true,
				enable_knowledge_base: true,
				enable_compliance: true,
				enable_coaching: true,
				suggestion_threshold: 0.6,
				max_suggestions: 3
			});

			// Connect enhanced WebSocket for real-time updates
			const callbacks: EnhancedWebSocketCallbacks = {
				onMessage: (message) => {
					if (message.type === 'transcription') {
						handleTranscription(message.data);
					} else if (message.type === 'sentiment') {
						handleSentiment(message.data);
					} else if (message.type === 'assistance') {
						handleAssistance(message.data);
					}
				},
				onConnecting: () => console.log('🔄 Connecting to enhanced AI WebSocket...'),
				onConnected: (status) => console.log('✅ Enhanced AI WebSocket connected with quality:', status.metrics.connectionQuality),
				onDisconnecting: () => console.log('🔄 Disconnecting enhanced AI WebSocket...'),
				onDisconnected: (status) => console.log('🔌 Enhanced AI WebSocket disconnected'),
				onReconnecting: (attempt, maxAttempts) => console.log(`🔄 Enhanced AI WebSocket reconnecting ${attempt}/${maxAttempts}`),
				onError: (error: Error) => console.error('❌ Enhanced AI WebSocket error:', error),
				onHeartbeat: (latency) => console.log(`💓 Enhanced AI WebSocket heartbeat: ${latency}ms`),
				onConnectionQualityChange: (quality) => console.log('📊 Enhanced AI WebSocket quality changed to:', quality),
				onUnhealthyConnection: (status) => console.warn('⚠️ Enhanced AI WebSocket connection unhealthy:', status)
			};
			
			wsClient = createEnhancedWebSocket(sessionId, callbacks, {
				heartbeatInterval: 15000, // 15 seconds
				maxReconnectAttempts: 5,
				initialReconnectDelay: 1000,
				maxReconnectDelay: 10000
			});

			sessionStateManager.updateCallState({
				status: 'active',
				metadata: { aiServices: 'initialized' }
			});
			sessionStateManager.saveState();
			callStatus = 'active';

			console.log('✅ AI services initialized successfully');
		} catch (error) {
			console.error('❌ Failed to initialize AI services:', error);
			sessionStateManager.addError({
				code: 'ai_initialization_failed',
				message: error instanceof Error ? error.message : 'Failed to initialize AI services',
				recoverable: true
			});
			sessionStateManager.saveState();
			callStatus = 'error';
		}
	}

	/**
	 * Shutdown AI services
	 */
	function shutdownAIServices() {
		console.log('🛑 Shutting down AI services');

		if (wsClient) {
			wsClient.disconnect();
			wsClient = null;
		}

		// Reset state
		transcriptionSegments = [];
		currentSentiment = null;
		sentimentTrend = null;
		assistanceSuggestions = [];

		sessionStateManager.updateCallState({
			status: 'ended',
			metadata: { aiServices: 'stopped' }
		});
		sessionStateManager.saveState();
		callStatus = 'ended';
	}

	/**
	 * Handle incoming transcription
	 */
	function handleTranscription(data: TranscriptionSegment) {
		console.log('📝 Transcription received:', data.text);

		// Add to history or update existing
		const existingIndex = transcriptionSegments.findIndex(s => s.id === data.id);
		if (existingIndex >= 0) {
			transcriptionSegments[existingIndex] = data;
		} else {
			transcriptionSegments = [...transcriptionSegments, data];
		}

		// Request sentiment analysis for final transcriptions
		if (data.is_final && wsClient) {
			wsClient.analyzeSentiment(data.text, data.speaker);
		}

		// Keep last 100 segments to avoid memory issues
		if (transcriptionSegments.length > 100) {
			transcriptionSegments = transcriptionSegments.slice(-100);
		}
	}

	/**
	 * Handle incoming sentiment analysis
	 */
	async function handleSentiment(data: SentimentAnalysis) {
		console.log('😊 Sentiment received:', data.sentiment, data.polarity_score);
		currentSentiment = data;

	// Fetch updated trend
	if (session?.sessionId) {
		try {
			sentimentTrend = await getSentimentTrend(session.sessionId);
		} catch (error) {
			console.error('Failed to fetch sentiment trend:', error);
		}
	}

		// Request assistance update if sentiment is negative
		if (data.polarity_score < -0.3 && wsClient && transcriptionSegments.length > 0) {
			const transcript = transcriptionSegments
				.filter(s => s.is_final)
				.map(s => `${s.speaker.toUpperCase()}: ${s.text}`)
				.join('\n');

			wsClient.requestAssistance(transcript, {
				customer_sentiment: data.sentiment,
				polarity: data.polarity_score
			});
		}
	}

	/**
	 * Handle incoming assistance suggestions
	 */
	function handleAssistance(data: AssistanceSuggestion[]) {
		console.log('💡 Assistance received:', data.length, 'suggestions');
		assistanceSuggestions = data;
	}

	/**
	 * Handle using an assistance suggestion
	 */
	function handleUseSuggestion(suggestion: AssistanceSuggestion) {
		console.log('✓ Using suggestion:', suggestion.title);
		// In a real implementation, this would insert the suggestion into a text input
		// or trigger other actions based on the suggestion type

		// For now, just log it and remove from list
		assistanceSuggestions = assistanceSuggestions.filter(s => s.id !== suggestion.id);
	}

	/**
	 * Handle dismissing a suggestion
	 */
	function handleDismissSuggestion(suggestionId: string) {
		console.log('✕ Dismissing suggestion:', suggestionId);
		assistanceSuggestions = assistanceSuggestions.filter(s => s.id !== suggestionId);
	}

async function onRetryConnection(): Promise<void> {
	try {
		sessionStateManager.clearErrors();
		sessionStateManager.updateCallState({ status: 'connecting' });
		sessionStateManager.saveState();
		callStatus = 'connecting';
		await onRetryConnectionCb?.();
	} catch (error) {
		sessionStateManager.addError({
			code: 'retry_failed',
			message: error instanceof Error ? error.message : 'Failed to retry connection',
			recoverable: true
			});
			sessionStateManager.saveState();
			callStatus = 'error';
		}
	}

	// Cleanup on unmount
	onDestroy(() => {
		shutdownAIServices();
		sessionStateManager.saveState();
	});

	$effect(() => {
		const sessionValue = session;

		if (!sessionValue) {
			callStatus = 'idle';
			sessionStateManager.updateCallState({ status: 'idle' });
			sessionStateManager.saveState();
			return;
		}

		const nextStatus = mapSessionStatus(sessionValue.status);
		const persistedState = get(sessionStateManager);
		const currentCallId = sessionValue.sessionId ?? persistedState.call?.id ?? '';

		callStatus = nextStatus;

		sessionStateManager.updateProvider(sessionValue.provider);
		sessionStateManager.updateCallState({
			id: currentCallId,
			status: nextStatus,
			provider: sessionValue.provider,
			metadata: {
				lastEvent: sessionValue.lastEvent,
				lastEventAt: sessionValue.lastEventAt
			}
		});

		if (sessionValue.error) {
			sessionStateManager.addError({
				code: 'provider_session_error',
				message: sessionValue.error,
				recoverable: true
			});
		}

		sessionStateManager.saveState();
	});
</script>

<div class="agent-workspace">
	<!-- Top Bar: Call Controls & Provider Selector -->
	<div class="top-bar">
		<div class="call-controls-container">
			<CallControlPanel
				bind:session
				{onEndCall}
				{onMute}
				{onHold}
				{onTransfer}
			/>
		</div>
		<div class="provider-selector-container">
			<ProviderSwitcher />
		</div>
		<div class="connection-status-container">
			<EnhancedConnectionStatus
				isLive={callStatus === 'active'}
				currentProvider={session?.provider ?? 'unknown'}
				onRetry={onRetryConnection}
			/>
		</div>
	</div>

	<!-- Main Content Area -->
	<div class="main-content">
		<!-- Left Panel: Transcription + Customer Info -->
		<div class="left-panel">
			<div class="customer-info">
				<h3 class="section-title">Customer Information</h3>
				{#if session}
					<div class="info-grid">
						<div class="info-item">
							<span class="info-label">Session ID:</span>
							<span class="info-value">{session.sessionId}</span>
						</div>
						<div class="info-item">
							<span class="info-label">Status:</span>
							<span class="info-value status" class:active={callStatus === 'active'}>
								{callStatus}
							</span>
						</div>
						<div class="info-item">
							<span class="info-label">Provider:</span>
							<span class="info-value">{session.provider}</span>
						</div>
					</div>
				{:else}
					<p class="no-session">No active session</p>
				{/if}
			</div>

			<div class="transcription-container">
				<h3 class="section-title">Live Transcription</h3>
				<TranscriptionPanel segments={transcriptMessages()} />
			</div>
		</div>

		<!-- Right Panel: Sentiment + Screen Share + AI Assistance -->
		<div class="right-panel">
			<div class="sentiment-container">
				<SentimentIndicator sentiment={currentSentiment} trend={sentimentTrend} />
			</div>

			<div class="screen-share-wrapper">
				<ScreenShare />
			</div>

			<div class="assistance-container">
				<AIAssistancePanel
					suggestions={assistanceSuggestions}
					onUseSuggestion={handleUseSuggestion}
					onDismissSuggestion={handleDismissSuggestion}
				/>
			</div>
		</div>
	</div>
</div>

<style>
	.agent-workspace {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background: #f9fafb;
		overflow: hidden;
	}

	.top-bar {
		display: grid;
		grid-template-columns: 2fr 1fr auto;
		gap: 1rem;
		padding: 1rem;
		background: white;
		border-bottom: 2px solid #e5e7eb;
		align-items: center;
	}

	.main-content {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		padding: 1rem;
		flex: 1;
		overflow: hidden;
	}

	.left-panel,
	.right-panel {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		overflow: hidden;
	}

	.customer-info {
		background: white;
		border-radius: 12px;
		padding: 1.25rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
	}

	.section-title {
		font-size: 1rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0 0 1rem 0;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 0.75rem;
	}

	.info-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.info-label {
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
	}

	.info-value {
		font-size: 0.9rem;
		color: #1f2937;
		font-weight: 600;
	}

	.info-value.status {
		padding: 0.25rem 0.5rem;
		border-radius: 6px;
		background: #f3f4f6;
		color: #6b7280;
		display: inline-block;
		width: fit-content;
	}

	.info-value.status.active {
		background: #d1fae5;
		color: #065f46;
	}

	.no-session {
		color: #9ca3af;
		font-size: 0.9rem;
		text-align: center;
		padding: 1rem;
	}

	.transcription-container,
	.sentiment-container,
	.assistance-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.transcription-container {
		background: white;
		border-radius: 12px;
		padding: 1.25rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
	}

	.assistance-container {
		min-height: 300px;
	}

	/* TABLET PORTRAIT (768px - 1024px) */
	@media (min-width: 768px) and (max-width: 1024px) {
		.agent-workspace {
			height: 100vh;
			overflow: hidden;
		}

		.top-bar {
			grid-template-columns: 1fr;
			gap: 0.75rem;
			padding: 0.75rem;
		}

		.call-controls-container,
		.provider-selector-container,
		.connection-status-container {
			width: 100%;
		}

		.main-content {
			grid-template-columns: 1fr;
			grid-template-rows: auto auto;
			gap: 0.75rem;
			padding: 0.75rem;
			overflow-y: auto;
		}

		.left-panel,
		.right-panel {
			overflow: visible;
		}

		.customer-info {
			padding: 1rem;
		}

		.transcription-container {
			min-height: 300px;
			max-height: 400px;
			padding: 1rem;
		}

		.sentiment-container,
		.assistance-container {
			min-height: 250px;
			max-height: 350px;
		}

		.screen-share-wrapper {
			min-height: 200px;
		}
	}

	/* TABLET LANDSCAPE */
	@media (min-width: 768px) and (max-width: 1024px) and (orientation: landscape) {
		.agent-workspace {
			height: 100vh;
		}

		.top-bar {
			grid-template-columns: 2fr 1fr auto;
			padding: 0.75rem;
		}

		.main-content {
			grid-template-columns: 1fr 1fr;
			grid-template-rows: 1fr;
			gap: 0.75rem;
			padding: 0.75rem;
			overflow: hidden;
		}

		.left-panel {
			display: flex;
			flex-direction: column;
			gap: 0.75rem;
			overflow-y: auto;
		}

		.right-panel {
			display: flex;
			flex-direction: column;
			gap: 0.75rem;
			overflow-y: auto;
		}

		.transcription-container {
			flex: 1;
			min-height: 250px;
		}

		.sentiment-container {
			flex: 0 0 auto;
			min-height: 150px;
		}

		.screen-share-wrapper {
			flex: 0 0 auto;
			min-height: 150px;
		}

		.assistance-container {
			flex: 1;
			min-height: 200px;
		}
	}

	@media (max-width: 1200px) {
		.top-bar {
			grid-template-columns: 1fr;
		}

		.main-content {
			grid-template-columns: 1fr;
			overflow-y: auto;
		}

		.left-panel,
		.right-panel {
			overflow: visible;
		}

		.transcription-container,
		.assistance-container {
			min-height: 400px;
		}
	}

	@media (max-width: 768px) {
		.info-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
