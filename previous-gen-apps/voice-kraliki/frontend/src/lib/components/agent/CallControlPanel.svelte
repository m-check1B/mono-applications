<script lang="ts">
	/**
	 * Call Control Panel
	 *
	 * Provides telephony controls for active calls:
	 * - Mute/unmute microphone
	 * - Hold/resume call
	 * - Transfer call
	 * - End call
	 * - Call timer display
	 * - Connection status
	 */

import { onDestroy } from 'svelte';
import type { SessionState } from '$lib/services/providerSession';

interface Props {
	session: SessionState | null;
	onEndCall?: () => void;
	onMute?: (muted: boolean) => void;
	onHold?: (held: boolean) => void;
	onTransfer?: () => void;
}

let {
	session = $bindable(null),
	onEndCall,
	onMute,
	onHold,
	onTransfer
}: Props = $props();

	// State
	let isMuted = $state(false);
	let isOnHold = $state(false);
	let callDuration = $state(0);
	let connectionStatus = $state<'connecting' | 'connected' | 'disconnected'>('disconnected');

	// Timer
	let timerInterval: ReturnType<typeof setInterval> | null = null;

	// Format duration as MM:SS
	const formatDuration = (seconds: number): string => {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	};

	// Start call timer
	const startTimer = () => {
		if (timerInterval) return;
		timerInterval = setInterval(() => {
			callDuration++;
		}, 1000);
	};

	// Stop call timer
	const stopTimer = () => {
		if (timerInterval) {
			clearInterval(timerInterval);
			timerInterval = null;
		}
	};

	// Toggle mute
	const toggleMute = () => {
		isMuted = !isMuted;
		onMute?.(isMuted);
	};

	// Toggle hold
	const toggleHold = () => {
		isOnHold = !isOnHold;
		onHold?.(isOnHold);
	};

	// End call
	const endCall = () => {
		stopTimer();
		callDuration = 0;
		connectionStatus = 'disconnected';
		onEndCall?.();
	};

	// Transfer call
	const transferCall = () => {
		onTransfer?.();
	};

	// Watch session status
	$effect(() => {
		if (session?.status === 'connected') {
			connectionStatus = 'connected';
			startTimer();
		} else if (session?.status === 'connecting') {
			connectionStatus = 'connecting';
		} else {
			connectionStatus = 'disconnected';
			stopTimer();
		}
	});

	onDestroy(() => {
		stopTimer();
	});
</script>

<div class="call-control-panel" role="region" aria-label="Call controls">
	<!-- Connection Status -->
	<div class="status-bar">
		<div class="status-indicator" role="status" aria-live="polite"
			class:connected={connectionStatus === 'connected'}
			class:connecting={connectionStatus === 'connecting'}
			class:disconnected={connectionStatus === 'disconnected'}>
			{#if connectionStatus === 'connected'}
				<span class="status-dot" aria-hidden="true"></span>
				<span class="status-text">Connected</span>
			{:else if connectionStatus === 'connecting'}
				<span class="status-dot" aria-hidden="true"></span>
				<span class="status-text">Connecting...</span>
			{:else}
				<span class="status-dot" aria-hidden="true"></span>
				<span class="status-text">No Active Call</span>
			{/if}
		</div>

		<div class="call-timer" role="timer" aria-label="Call duration">
			<span class="timer-icon" aria-hidden="true">⏱</span>
			<span class="timer-text">{formatDuration(callDuration)}</span>
		</div>
	</div>

	<!-- Call Controls -->
	<div class="controls" role="group" aria-label="Call control buttons">
		<button
			class="control-btn mute"
			class:active={isMuted}
			onclick={toggleMute}
			disabled={connectionStatus !== 'connected'}
			aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
			aria-pressed={isMuted}
			tabindex="0"
		>
			<span class="icon" aria-hidden="true">{isMuted ? '🔇' : '🎤'}</span>
			<span class="label">{isMuted ? 'Unmute' : 'Mute'}</span>
			<span class="sr-only">{isMuted ? 'Microphone is muted' : 'Microphone is active'}</span>
		</button>

		<button
			class="control-btn hold"
			class:active={isOnHold}
			onclick={toggleHold}
			disabled={connectionStatus !== 'connected'}
			aria-label={isOnHold ? 'Resume call' : 'Place call on hold'}
			aria-pressed={isOnHold}
			tabindex="0"
		>
			<span class="icon" aria-hidden="true">{isOnHold ? '▶' : '⏸'}</span>
			<span class="label">{isOnHold ? 'Resume' : 'Hold'}</span>
			<span class="sr-only">{isOnHold ? 'Call is on hold' : 'Call is active'}</span>
		</button>

		<button
			class="control-btn transfer"
			onclick={transferCall}
			disabled={connectionStatus !== 'connected'}
			aria-label="Transfer call to another agent"
			tabindex="0"
		>
			<span class="icon" aria-hidden="true">↗</span>
			<span class="label">Transfer</span>
		</button>

		<button
			class="control-btn end-call"
			onclick={endCall}
			disabled={connectionStatus === 'disconnected'}
			aria-label="End call"
			tabindex="0"
		>
			<span class="icon" aria-hidden="true">📞</span>
			<span class="label">End Call</span>
		</button>
	</div>
</div>

<style>
	.call-control-panel {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 12px;
		padding: 1.5rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		color: white;
	}

	.status-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.2);
	}

	.status-indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.status-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: #ff4444;
		animation: pulse 2s infinite;
	}

	.status-indicator.connected .status-dot {
		background: #44ff44;
	}

	.status-indicator.connecting .status-dot {
		background: #ffaa44;
	}

	.status-text {
		font-weight: 500;
		font-size: 0.9rem;
	}

	.call-timer {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.1rem;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
	}

	.timer-icon {
		font-size: 1.2rem;
	}

	.controls {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
	}

		.control-btn {
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			gap: 0.5rem;
			min-width: 44px;
			min-height: 44px;
			padding: 1rem 0.5rem;
			background: hsl(var(--card));
			border: 2px solid hsl(var(--border));
			color: hsl(var(--foreground));
			font-size: 0.85rem;
			font-weight: 800;
			text-transform: uppercase;
			letter-spacing: 0.04em;
			cursor: pointer;
			transition: transform 80ms linear, box-shadow 80ms linear, background-color 80ms linear, color 80ms linear;
			margin: 0.25rem;
			box-shadow: var(--shadow-brutal-subtle);
			touch-action: manipulation;
		}

		.control-btn:hover:not(:disabled) {
			background: var(--color-terminal-green);
			color: #000;
			transform: translate(2px, 2px);
			box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
		}

		.control-btn:disabled {
			opacity: 0.5;
			cursor: not-allowed;
		}

		.control-btn.active {
			background: var(--color-terminal-green);
			color: #000;
			box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
		}

		.control-btn .icon {
			font-size: 1.5rem;
		}

		.control-btn.end-call {
			background: var(--color-system-red);
			color: #000;
			border-color: hsl(var(--border));
		}

		.control-btn.end-call:hover:not(:disabled) {
			transform: translate(2px, 2px);
			box-shadow: 2px 2px 0px 0px hsl(var(--foreground));
		}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	/* Increase touch targets on smaller screens */
	@media (max-width: 1024px) {
		.control-btn {
			min-width: 48px;
			min-height: 48px;
			padding: 1rem;
			font-size: 1rem;
		}

		.controls {
			gap: 0.75rem;
		}
	}

	/* Extra spacing on mobile */
	@media (max-width: 767px) {
		.control-btn {
			min-width: 52px;
			min-height: 52px;
			padding: 1.25rem;
			margin: 0.5rem;
		}

		.controls {
			grid-template-columns: repeat(2, 1fr);
			gap: 1rem;
		}
	}
</style>
