<script lang="ts">
	/**
	 * Screen Share Component
	 *
	 * Provides screen sharing functionality using WebRTC getDisplayMedia API:
	 * - Start/stop screen sharing
	 * - Live preview of shared screen
	 * - Automatic cleanup on component destruction
	 * - Browser compatibility handling
	 * - Full accessibility support
	 */

	import { onMount, onDestroy } from 'svelte';
	import { createWebRTCManager } from '$lib/services/webrtcManager';

	// Create WebRTC manager instance
	const webrtcManager = createWebRTCManager();

	// State
	let isSharing = $state(false);
	let screenStream = $state<MediaStream | null>(null);
	let videoElement: HTMLVideoElement;
	let error = $state<string | null>(null);

	/**
	 * Start screen sharing
	 */
	async function startSharing() {
		try {
			error = null;
			screenStream = await webrtcManager.startScreenShare();
			isSharing = true;

			// Attach stream to video element
			if (videoElement && screenStream) {
				videoElement.srcObject = screenStream;
			}
		} catch (err) {
			console.error('Failed to start screen sharing:', err);
			error = err instanceof Error ? err.message : 'Screen sharing not available or denied';
			isSharing = false;
			screenStream = null;
		}
	}

	/**
	 * Stop screen sharing
	 */
	function stopSharing() {
		webrtcManager.stopScreenShare();
		isSharing = false;
		screenStream = null;
		error = null;

		if (videoElement) {
			videoElement.srcObject = null;
		}
	}

	// Cleanup on component destruction
	onDestroy(() => {
		if (isSharing) {
			stopSharing();
		}
	});
</script>

<div class="screen-share-container" role="region" aria-label="Screen sharing controls">
	<div class="header">
		<h3 class="title">Screen Share</h3>
		{#if isSharing}
			<span class="status-badge active" aria-label="Screen sharing active">
				<span class="status-dot"></span>
				Active
			</span>
		{/if}
	</div>

	{#if error}
		<div class="error-message" role="alert">
			<span class="error-icon" aria-hidden="true">⚠️</span>
			<span>{error}</span>
		</div>
	{/if}

	{#if !isSharing}
		<div class="start-view">
			<p class="description">Share your screen to collaborate with others in real-time.</p>
			<button
				onclick={startSharing}
				class="share-button"
				aria-label="Start screen sharing"
			>
				<span class="button-icon" aria-hidden="true">🖥️</span>
				Start Screen Share
			</button>
			<p class="note">
				<strong>Note:</strong> Requires HTTPS and a modern browser (Chrome, Firefox, Edge, Safari).
			</p>
		</div>
	{:else}
		<div class="sharing-active">
			<div class="video-container">
				<video
					bind:this={videoElement}
					autoplay
					muted
					class="screen-preview"
					aria-label="Screen share preview"
				/>
			</div>
			<button
				onclick={stopSharing}
				class="stop-button"
				aria-label="Stop screen sharing"
			>
				<span class="button-icon" aria-hidden="true">⏹️</span>
				Stop Sharing
			</button>
		</div>
	{/if}
</div>

<style>
	.screen-share-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1.25rem;
		background: hsl(var(--card));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal);
		color: hsl(var(--foreground));
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.title {
		font-size: 1rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.status-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.35rem 0.55rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		box-shadow: var(--shadow-brutal-subtle);
		color: hsl(var(--foreground));
	}

	.status-badge.active {
		background: var(--color-terminal-green);
		color: #000;
	}

	.status-dot {
		width: 10px;
		height: 10px;
		border: 2px solid hsl(var(--border));
		background: currentColor;
		animation: pulse 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	.error-message {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		background: hsl(var(--destructive) / 0.1);
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		color: hsl(var(--foreground));
		font-size: 0.9rem;
	}

	.error-icon { font-size: 1.1rem; }

	.start-view { display: flex; flex-direction: column; gap: 1rem; }

	.description { color: hsl(var(--muted-foreground)); font-size: 0.95rem; margin: 0; }

	.note { color: hsl(var(--muted-foreground)); font-size: 0.8rem; margin: 0; line-height: 1.4; }

	.share-button, .stop-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.85rem 1.3rem;
		border: 2px solid hsl(var(--border));
		cursor: pointer;
		font-size: 0.95rem;
		font-weight: 900;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		box-shadow: var(--shadow-brutal);
		transition: transform 60ms linear, box-shadow 60ms linear, background-color 60ms linear, color 60ms linear;
	}

	.share-button { background: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
	.share-button:hover { background: var(--color-terminal-green); color: #000; transform: translate(2px, 2px); box-shadow: var(--shadow-brutal-subtle); }

	.stop-button { background: var(--color-system-red); color: #000; }
	.stop-button:hover { background: var(--color-terminal-green); color: #000; transform: translate(2px, 2px); box-shadow: var(--shadow-brutal-subtle); }

	.button-icon { font-size: 1.1rem; }

	.sharing-active { display: flex; flex-direction: column; gap: 1rem; }

	.video-container {
		position: relative;
		width: 100%;
		border: 2px solid hsl(var(--border));
		background: #000;
		box-shadow: var(--shadow-brutal);
	}

	.screen-preview {
		width: 100%;
		max-height: 400px;
		display: block;
		object-fit: contain;
	}

	@media (max-width: 768px) {
		.screen-share-container { padding: 1rem; }
		.screen-preview { max-height: 250px; }
		.share-button, .stop-button { padding: 0.75rem 1.1rem; font-size: 0.9rem; }
	}

	.share-buttonfocus-visible,
	.stop-buttonfocus-visible {
		outline: 2px solid var(--color-terminal-green);
		outline-offset: 0;
		box-shadow: var(--shadow-brutal);
	}
</style>

