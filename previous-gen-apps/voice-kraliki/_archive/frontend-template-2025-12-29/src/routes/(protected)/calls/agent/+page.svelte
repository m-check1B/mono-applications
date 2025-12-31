<script lang="ts">
	/**
	 * Agent Operations Page
	 *
	 * Showcases the complete AI-powered Agent Workspace with:
	 * - Real-time transcription
	 * - Sentiment analysis
	 * - AI assistance suggestions
	 * - Call controls
	 * - Provider switching
	 *
	 * This is a demo page for the AI-first call center features.
	 */

	import { onMount, onDestroy } from 'svelte';
	import AgentWorkspace from '$lib/components/agent/AgentWorkspace.svelte';
	import { createProviderSession, type ProviderType } from '$lib/services/providerSession';
	import { createAudioManager } from '$lib/services/audioManager';
	import { Activity, PhoneCall, PhoneOff, Mic, MicOff } from 'lucide-svelte';

	// Provider session for demo
	const providerSession = createProviderSession({
		provider: 'gemini',
		path: '/agent-operations'
	});

	let session = $state(providerSession.getState());
	const unsubscribeSession = providerSession.subscribe((value) => {
		session = value;
	});

	// Audio manager for local testing
	const audioManager = createAudioManager();
	let audioState = $state(audioManager.getState());
	const unsubscribeAudio = audioManager.subscribe((value) => {
		audioState = value;
	});

	// State
let isCallActive = $state(false);
let isMuted = $state(false);
let lastError = $state<string | null>(null);
let startMessageSent = $state(false);

	// Setup audio streaming when session is connected
	audioManager.sendCapturedFrame((buffer) => {
		if (session.status === 'connected') {
			try {
				const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer.buffer)));
				providerSession.send(
					JSON.stringify({
						type: 'audio-data',
						audioData: base64
					})
				);
			} catch (error) {
				console.error('Failed to send captured audio frame', error);
			}
		}
	});

	// Handle session events
	$effect(() => {
	if (isCallActive && session.status === 'connected' && !startMessageSent) {
		providerSession.send(JSON.stringify({
			type: 'start-session',
			voice: 'Puck',
			model: 'gemini-2.0-flash-exp',
			language: 'en',
			aiInstructions:
				'You are a helpful AI assistant for a call center. Provide professional and courteous support to callers.',
			company: { name: 'Demo Company', phone: '+1234567890' }
		}));
		startMessageSent = true;
	}

	if (!session.lastEventAt) return;

		const payload = session.lastEvent;
		if (payload && typeof payload === 'object' && 'type' in payload) {
			const event = payload as {
				type?: string;
				audio?: string;
				mimeType?: string | null;
			};

			if (event.type === 'audio' && event.audio) {
				void audioManager.playBase64Audio(event.audio, event.mimeType).catch((error) => {
					console.error('Failed to play realtime audio chunk', error);
				});
			}
		}
	});

	/**
	 * Start a demo call session
	 */
	async function startCall() {
		lastError = null;

		// Start microphone
		if (audioState.status !== 'recording') {
			const result = await audioManager.startMicrophone();
			if (!result.success) {
				lastError = result.error ?? 'Unable to start microphone.';
				return;
			}
		}

	// Connect session
	providerSession.connect();
	isCallActive = true;
	startMessageSent = false;
	}

	/**
	 * End the call session
	 */
	function endCall() {
	providerSession.disconnect();
	audioManager.stop();
	isCallActive = false;
	startMessageSent = false;
}

	/**
	 * Toggle mute
	 */
	function handleMute(muted: boolean) {
		isMuted = muted;
		// In production, would actually mute audio stream
		console.log(muted ? 'Muted' : 'Unmuted');
	}

	/**
	 * Handle hold
	 */
	function handleHold(held: boolean) {
		console.log(held ? 'On hold' : 'Resumed');
		// In production, would pause audio processing
	}

	/**
	 * Handle transfer
	 */
function handleTransfer() {
	console.log('Transfer requested');
	// In production, would initiate call transfer
}

async function retryConnection() {
	providerSession.connect();
	if (isCallActive) {
		startMessageSent = false;
	}
}

	onDestroy(() => {
		providerSession.disconnect();
		void audioManager.cleanup();
		unsubscribeSession();
		unsubscribeAudio();
	});
</script>

<section class="agent-operations-page">
	<!-- Header -->
	<header class="page-header">
		<div>
			<h1 class="page-title">AI Agent Workspace</h1>
			<p class="page-description">
				Production-ready agent interface with real-time AI assistance, sentiment analysis, and live transcription.
			</p>
		</div>

		<div class="header-actions">
			{#if !isCallActive}
				<button class="btn btn-primary btn-lg" onclick={startCall}>
					<PhoneCall class="size-5" />
					Start Demo Call
				</button>
			{:else}
				<button class="btn btn-danger btn-lg" onclick={endCall}>
					<PhoneOff class="size-5" />
					End Call
				</button>
			{/if}
		</div>
	</header>

	<!-- Error Display -->
	{#if lastError}
		<div class="alert alert-error">
			{lastError}
		</div>
	{/if}

	<!-- Status Indicators -->
	<div class="status-bar">
		<div class="status-item">
			<Activity class="size-4" />
			<span>Session: <strong>{session.status}</strong></span>
		</div>
		<div class="status-item">
			{#if isMuted}
				<MicOff class="size-4 text-red-500" />
			{:else}
				<Mic class="size-4 text-green-500" />
			{/if}
			<span>Audio: <strong>{audioState.status}</strong></span>
		</div>
		<div class="status-item">
			<span class="status-dot" class:active={isCallActive}></span>
			<span>Call: <strong>{isCallActive ? 'Active' : 'Inactive'}</strong></span>
		</div>
	</div>

	<!-- Agent Workspace -->
	<div class="workspace-container">
		<AgentWorkspace
			bind:session
			onEndCall={endCall}
			onMute={handleMute}
			onHold={handleHold}
			onTransfer={handleTransfer}
			onRetryConnection={retryConnection}
		/>
	</div>

	<!-- Instructions -->
	{#if !isCallActive}
		<article class="instructions-card">
			<h3 class="instructions-title">Getting Started</h3>
			<div class="instructions-list">
				<div class="instruction-item">
					<span class="instruction-number">1</span>
					<div>
						<p class="instruction-text">Click "Start Demo Call" to begin a test session</p>
						<p class="instruction-hint">This will connect to the AI provider and start your microphone</p>
					</div>
				</div>
				<div class="instruction-item">
					<span class="instruction-number">2</span>
					<div>
						<p class="instruction-text">Speak naturally to interact with the AI</p>
						<p class="instruction-hint">Real-time transcription and sentiment analysis will appear automatically</p>
					</div>
				</div>
				<div class="instruction-item">
					<span class="instruction-number">3</span>
					<div>
						<p class="instruction-text">Watch for AI assistance suggestions</p>
						<p class="instruction-hint">Suggested responses, compliance warnings, and coaching tips will appear as you speak</p>
					</div>
				</div>
			</div>
		</article>
	{/if}
</section>

<style>
	.agent-operations-page {
		min-height: 100vh;
		background: hsl(var(--background));
		padding: 1.5rem;
		color: hsl(var(--foreground));
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 1.5rem;
		padding: 1.25rem;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal);
	}

	.page-title {
		font-size: 1.6rem;
		font-weight: 900;
		color: hsl(var(--foreground));
		margin: 0 0 0.4rem 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.page-description {
		font-size: 0.95rem;
		color: hsl(var(--muted-foreground));
		margin: 0;
	}

	.header-actions { display: flex; gap: 0.75rem; }

	.btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.7rem 1.25rem;
		border: 2px solid hsl(var(--border));
		font-weight: 900;
		font-size: 0.95rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		cursor: pointer;
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
		box-shadow: var(--shadow-brutal);
		background: hsl(var(--card));
		color: hsl(var(--foreground));
	}

	.btn-lg { padding: 0.9rem 1.6rem; font-size: 1rem; }

	.btn-primary { background: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
	.btn-primary:hover { background: var(--color-terminal-green); color: #000; transform: translate(2px, 2px); box-shadow: var(--shadow-brutal-subtle); }

	.btn-danger { background: var(--color-system-red); color: #000; }
	.btn-danger:hover { background: var(--color-terminal-green); color: #000; transform: translate(2px, 2px); box-shadow: var(--shadow-brutal-subtle); }

	.alert {
		padding: 1rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		margin-bottom: 1.5rem;
	}

	.alert-error {
		background: hsl(var(--destructive) / 0.12);
		color: hsl(var(--foreground));
	}

	.status-bar {
		display: flex;
		gap: 1.25rem;
		padding: 1rem 1.25rem;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		margin-bottom: 1.5rem;
	}

	.status-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem; color: hsl(var(--muted-foreground)); }
	.status-item strong { color: hsl(var(--foreground)); }

	.status-dot { width: 10px; height: 10px; border: 2px solid hsl(var(--border)); background: hsl(var(--muted-foreground)); }
	.status-dot.active { background: var(--color-terminal-green); animation: pulse 2s infinite; }

	.workspace-container { margin-bottom: 1.5rem; }

	.instructions-card {
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		padding: 1.25rem;
		box-shadow: var(--shadow-brutal-subtle);
	}

	.instructions-title {
		font-size: 1.2rem;
		font-weight: 900;
		color: hsl(var(--foreground));
		margin: 0 0 1rem 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.instructions-list { display: flex; flex-direction: column; gap: 1rem; }

	.instruction-item { display: flex; gap: 0.85rem; align-items: flex-start; }

	.instruction-number {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		color: hsl(var(--foreground));
		font-weight: 900;
		font-size: 0.9rem;
	}

	.instruction-text { font-size: 0.95rem; font-weight: 800; color: hsl(var(--foreground)); margin: 0 0 0.25rem 0; }
	.instruction-hint { font-size: 0.85rem; color: hsl(var(--muted-foreground)); margin: 0; }

	@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

	@media (max-width: 768px) {
		.page-header { flex-direction: column; gap: 1rem; }
		.status-bar { flex-direction: column; gap: 0.75rem; }
	}
</style>

