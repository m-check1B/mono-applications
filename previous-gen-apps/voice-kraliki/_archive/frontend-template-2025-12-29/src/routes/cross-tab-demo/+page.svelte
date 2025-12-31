<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { crossTabSync } from '$lib/services/crossTabSync';

	let messages = $state<string[]>([]);
	let testMessage = $state('');

	// Subscribe to all message types
	$effect(() => {
		const unsubscribers = [
			crossTabSync.subscribe('auth_updated', (msg) => {
				messages = [
					...messages,
					`[${new Date(msg.timestamp).toLocaleTimeString()}] Auth updated from tab ${msg.tabId.slice(0, 15)}...`
				];
			}),
			crossTabSync.subscribe('auth_logout', (msg) => {
				messages = [
					...messages,
					`[${new Date(msg.timestamp).toLocaleTimeString()}] Logout detected from tab ${msg.tabId.slice(0, 15)}...`
				];
			}),
			crossTabSync.subscribe('session_updated', (msg) => {
				messages = [
					...messages,
					`[${new Date(msg.timestamp).toLocaleTimeString()}] Session updated: ${JSON.stringify(msg.payload).slice(0, 50)}...`
				];
			}),
			crossTabSync.subscribe('session_ended', (msg) => {
				messages = [
					...messages,
					`[${new Date(msg.timestamp).toLocaleTimeString()}] Session ended from tab ${msg.tabId.slice(0, 15)}...`
				];
			})
		];

		return () => unsubscribers.forEach((unsub) => unsub());
	});

	function sendTestMessage() {
		if (!testMessage.trim()) return;
		crossTabSync.broadcast('session_updated', { test: testMessage });
		testMessage = '';
	}

	function clearMessages() {
		messages = [];
	}
</script>

<div class="cross-tab-demo">
	<h1>Cross-Tab Synchronization Demo</h1>

	<div class="status">
		<div class="status-item">
			<strong>BroadcastChannel:</strong>
			<span class={crossTabSync.isAvailable() ? 'supported' : 'not-supported'}>
				{crossTabSync.isAvailable() ? '✓ Supported' : '✗ Not Supported'}
			</span>
		</div>
		<div class="status-item">
			<strong>Auth Status:</strong>
			<span class="auth-status status-{$authStore.status}">
				{$authStore.status}
			</span>
		</div>
		<div class="status-item">
			<strong>User:</strong>
			<span>{$authStore.user?.email || 'Not logged in'}</span>
		</div>
	</div>

	<div class="instructions">
		<h2>Instructions:</h2>
		<ol>
			<li>Open this page in multiple browser tabs (Ctrl+Click or Cmd+Click on the tab)</li>
			<li>Login or logout in one tab using the auth pages</li>
			<li>Observe automatic synchronization in other tabs</li>
			<li>You can also send test messages between tabs using the form below</li>
		</ol>
	</div>

	<div class="test-section">
		<h2>Test Messages</h2>
		<div class="input-group">
			<input
				bind:value={testMessage}
				placeholder="Enter test message"
				onkeypress={(e) => e.key === 'Enter' && sendTestMessage()}
			/>
			<button onclick={sendTestMessage} disabled={!testMessage.trim()}>
				Send to Other Tabs
			</button>
		</div>
	</div>

	<div class="messages">
		<div class="messages-header">
			<h3>Messages from Other Tabs:</h3>
			<button class="clear-btn" onclick={clearMessages} disabled={messages.length === 0}>
				Clear
			</button>
		</div>
		<div class="messages-list">
			{#if messages.length === 0}
				<p class="no-messages">No messages yet. Try logging in/out in another tab or send a test message.</p>
			{:else}
				{#each messages as message}
					<div class="message">{message}</div>
				{/each}
			{/if}
		</div>
	</div>

	<div class="info-box">
		<h3>How It Works</h3>
		<p>
			This feature uses the <code>BroadcastChannel API</code> to synchronize authentication state
			and sessions across multiple browser tabs. When you login, logout, or update your session in
			one tab, all other tabs are automatically notified and updated.
		</p>
		<p>
			<strong>Benefits:</strong>
		</p>
		<ul>
			<li>Consistent authentication state across all tabs</li>
			<li>Automatic logout in all tabs when you logout in one</li>
			<li>Real-time session updates</li>
			<li>No server polling required</li>
		</ul>
	</div>
</div>

<style>
	.cross-tab-demo {
		max-width: 900px;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	h1 {
		color: #333;
		margin-bottom: 1.5rem;
	}

	h2 {
		color: #555;
		font-size: 1.3rem;
		margin-bottom: 1rem;
	}

	h3 {
		color: #666;
		font-size: 1.1rem;
		margin-bottom: 0.5rem;
	}

	.status {
		background: hsl(var(--card));
		color: white;
		padding: 1.5rem;
		border-radius: 12px;
		margin-bottom: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.status-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.status-item:last-child {
		margin-bottom: 0;
	}

	.status-item strong {
		min-width: 150px;
	}

	.supported {
		color: #4ade80;
		font-weight: 600;
	}

	.not-supported {
		color: #fca5a5;
		font-weight: 600;
	}

	.auth-status {
		padding: 0.25rem 0.75rem;
		border-radius: 6px;
		font-size: 0.875rem;
		font-weight: 600;
		text-transform: uppercase;
	}

	.status-authenticated {
		background: rgba(74, 222, 128, 0.2);
		color: #4ade80;
	}

	.status-unauthenticated {
		background: rgba(252, 165, 165, 0.2);
		color: #fca5a5;
	}

	.status-authenticating,
	.status-refreshing {
		background: rgba(251, 191, 36, 0.2);
		color: #fbbf24;
	}

	.instructions {
		background: #f8fafc;
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		margin-bottom: 2rem;
	}

	.instructions ol {
		margin: 0;
		padding-left: 1.5rem;
	}

	.instructions li {
		margin-bottom: 0.5rem;
		color: #475569;
	}

	.test-section {
		background: white;
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		margin-bottom: 2rem;
	}

	.input-group {
		display: flex;
		gap: 0.75rem;
	}

	input {
		flex: 1;
		padding: 0.75rem 1rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 1rem;
	}

	input:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	button {
		padding: 0.75rem 1.5rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 6px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	button:hover:not(:disabled) {
		background: #5568d3;
		transform: translateY(-1px);
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.messages {
		background: white;
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		margin-bottom: 2rem;
	}

	.messages-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.clear-btn {
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
		background: #ef4444;
	}

	.clear-btn:hover:not(:disabled) {
		background: #dc2626;
	}

	.messages-list {
		max-height: 400px;
		overflow-y: auto;
		background: #f8fafc;
		border-radius: 6px;
		padding: 1rem;
	}

	.message {
		padding: 0.75rem;
		margin-bottom: 0.5rem;
		background: white;
		border-left: 3px solid #667eea;
		border-radius: 4px;
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 0.875rem;
		color: #334155;
	}

	.message:last-child {
		margin-bottom: 0;
	}

	.no-messages {
		text-align: center;
		color: #94a3b8;
		font-style: italic;
		padding: 2rem;
	}

	.info-box {
		background: hsl(var(--card));
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid #fbbf24;
	}

	.info-box h3 {
		color: #92400e;
		margin-bottom: 0.75rem;
	}

	.info-box p {
		color: #78350f;
		margin-bottom: 0.75rem;
		line-height: 1.6;
	}

	.info-box code {
		background: rgba(251, 191, 36, 0.3);
		padding: 0.2rem 0.4rem;
		border-radius: 3px;
		font-size: 0.9em;
	}

	.info-box ul {
		margin: 0;
		padding-left: 1.5rem;
	}

	.info-box li {
		color: #78350f;
		margin-bottom: 0.25rem;
	}
</style>
