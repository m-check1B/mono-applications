<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';

	interface Props {
		id: number;
		onDestroy?: () => void;
	}

	let { id, onDestroy: onDestroyCallback }: Props = $props();

	let container: HTMLDivElement;
	let terminal: any;
	let fitAddon: any;
	let handleResize: (() => void) | null = null;
	let socket: WebSocket | null = null;
	let connected = $state(false);
	let error = $state<string | null>(null);

	onMount(() => {
		if (!browser) return;

		(async () => {
			try {
				const { Terminal } = await import('xterm');
				const { FitAddon } = await import('@xterm/addon-fit');

				terminal = new Terminal({
					cursorBlink: true,
					fontSize: 14,
					fontFamily: 'JetBrains Mono, monospace',
					theme: {
						background: '#0a0a0a',
						foreground: '#33ff00',
						cursor: '#33ff00',
						black: '#000000',
						red: '#ff0000',
						green: '#33ff00',
						yellow: '#ffaa00',
						blue: '#0099ff',
						magenta: '#ff00ff',
						cyan: '#00ffff',
						white: '#ffffff'
					},
					scrollback: 10000,
					tabStopWidth: 4
				});

				fitAddon = new FitAddon();
				terminal.loadAddon(fitAddon);

				terminal.open(container);
				fitAddon.fit();

				connectWebSocket();

				terminal.onData((data: string) => {
					if (socket && socket.readyState === WebSocket.OPEN) {
						socket.send(JSON.stringify({ type: 'input', data, terminalId: id }));
					}
				});

				handleResize = () => {
					fitAddon.fit();
					if (socket && socket.readyState === WebSocket.OPEN) {
						const dims = { cols: terminal.cols, rows: terminal.rows };
						socket.send(JSON.stringify({ type: 'resize', ...dims, terminalId: id }));
					}
				};
				window.addEventListener('resize', handleResize);
				handleResize();
			} catch (err) {
				console.error(`[TERMINAL ${id}] Failed to initialize:`, err);
				error = 'Failed to initialize terminal';
			}
		})();
	});

	function connectWebSocket() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const sessionId = `terminal-${id}`;
		const wsUrl = `${protocol}//${window.location.host}/ws/terminal?sessionId=${sessionId}`;

		terminal.writeln(`\x1b[1;32m[Connecting to session ${sessionId}...]\x1b[0m`);

		socket = new WebSocket(wsUrl);

		socket.onopen = () => {
			connected = true;
			error = null;
			terminal.writeln('\x1b[1;32m[Connected]\x1b[0m\r\n');
			terminal.focus();
			
			// Trigger a resize on connect to ensure PTY matches terminal size
			handleResize?.();
		};

		socket.onmessage = (event) => {
			terminal.write(event.data);
		};

		socket.onerror = (err) => {
			console.error(`[TERMINAL ${id}] WebSocket error:`, err);
			error = 'Connection error';
			terminal.writeln('\r\n\x1b[1;31m[Connection error]\x1b[0m');
		};

		socket.onclose = () => {
			connected = false;
			terminal.writeln('\r\n\x1b[1;33m[Disconnected]\x1b[0m');

			setTimeout(() => {
				if (terminal && !socket) {
					terminal.writeln('\x1b[1;33m[Reconnecting...]\x1b[0m');
					connectWebSocket();
				}
			}, 3000);
		};
	}

	function reconnect() {
		if (socket) {
			socket.onclose = null; // Prevent auto-reconnect from this close
			socket.close();
			socket = null;
		}
		setTimeout(() => connectWebSocket(), 500);
	}

	function kill() {
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: 'kill' }));
		}
		if (onDestroyCallback) {
			onDestroyCallback();
		}
	}

	onDestroy(() => {
		// When navigating away, we keep the socket and terminal alive if possible?
		// Actually, Svelte component destruction means we lose the 'terminal' object anyway
		// because 'container' is gone. But the BACKEND session will persist.
		
		if (socket) {
			socket.onclose = null; // Prevent auto-reconnect
			socket.close();
		}
		if (terminal) {
			terminal.dispose();
		}
		if (handleResize) {
			window.removeEventListener('resize', handleResize);
		}
	});
</script>

<div class="terminal-wrapper">
	<div class="terminal-header">
		<div class="terminal-title">
			<span class="terminal-id">Terminal {id}</span>
			<div class="status">
				{#if connected}
					<span class="status-dot online"></span>
					<span>Connected</span>
				{:else}
					<span class="status-dot offline"></span>
					<span>Disconnected</span>
				{/if}
			</div>
		</div>
		<div class="actions">
			<button class="brutal-btn small" onclick={reconnect}>Reconnect</button>
			<button class="brutal-btn small danger" onclick={kill}>Kill</button>
		</div>
	</div>

	{#if error}
		<div class="error-banner">
			<span>⚠️ {error}</span>
		</div>
	{/if}

	<div class="terminal-container" bind:this={container}></div>
</div>

<style>
	.terminal-wrapper {
		display: flex;
		flex-direction: column;
		border: 4px solid var(--terminal-green);
		background: #0a0a0a;
		box-shadow: 8px 8px 0 0 var(--terminal-green);
		overflow: hidden;
		min-height: 0;
	}

	.terminal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px;
		background: #111;
		border-bottom: 2px solid var(--terminal-green);
	}

	.terminal-title {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.actions {
		display: flex;
		gap: 8px;
	}

	.brutal-btn.danger {
		border-color: var(--system-red);
		color: var(--system-red);
	}

	.brutal-btn.danger:hover {
		background: var(--system-red);
		color: var(--void);
	}

	.terminal-id {
		font-size: 14px;
		font-weight: 700;
		color: var(--terminal-green);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.status {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
	}

	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		border: 2px solid var(--border);
	}

	.status-dot.online {
		background: var(--terminal-green);
		box-shadow: 0 0 6px var(--terminal-green);
	}

	.status-dot.offline {
		background: var(--system-red);
	}

	.error-banner {
		padding: 8px 12px;
		background: var(--system-red);
		color: var(--void);
		font-size: 11px;
		font-weight: 700;
		text-align: center;
	}

	.terminal-container {
		flex: 1;
		padding: 8px;
		min-height: 0;
	}

	.terminal-container :global(.xterm) {
		height: 100%;
	}

	.terminal-container :global(.xterm-viewport) {
		overflow-y: auto;
	}
</style>
