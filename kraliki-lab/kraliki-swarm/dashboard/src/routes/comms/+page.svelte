<script lang="ts">
	import { onMount } from "svelte";

	interface BlackboardMessage {
		id: number;
		time: string;
		agent: string;
		topic: string;
		message: string;
	}

	interface BlackboardData {
		messages: BlackboardMessage[];
		stats: {
			total: number;
			by_topic: Record<string, number>;
			by_agent: Record<string, number>;
		};
	}

	let data = $state<BlackboardData | null>(null);
	let loading = $state(true);
	let sending = $state(false);
	let statusMessage = $state<{ text: string; type: 'success' | 'error' } | null>(null);
	let alertMessages = $state<BlackboardMessage[]>([]);
	let alertCount = $state(0);
	let criticalCount = $state(0);
	let earlyExitCount = $state(0);

	// Search state
	let searchQuery = $state('');
	let searching = $state(false);
	let searchResults = $state<BlackboardMessage[]>([]);
	let isSearchMode = $state(false);

	// Unified form
	let message = $state('');
	let title = $state('');
	let destination = $state<'linear' | 'blackboard' | 'both' | 'agent'>('linear');
	let priority = $state('3');
	let label = $state('ai-task');
	let streamLabel = $state('stream:cash-engine');
	let topic = $state('general');
	let targetAgent = $state('CC-orchestrator');

	// File state
	let files = $state<File[]>([]);
	let isDragging = $state(false);

	// STT state
	let isRecording = $state(false);
	let recognition: any = null;
	let sttSupported = $state(false);

	const agents = [
		{ id: 'CC-orchestrator', name: 'Claude Orchestrator' },
		{ id: 'OC-orchestrator', name: 'OpenCode Orchestrator' },
		{ id: 'GE-orchestrator', name: 'Gemini Orchestrator' },
		{ id: 'CX-orchestrator', name: 'Codex Orchestrator' },
		{ id: 'all-orchestrators', name: 'All Orchestrators' },
		{ id: 'all-builders', name: 'All Builders' },
	];

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files) {
			files = [...files, ...Array.from(input.files)];
		}
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		if (e.dataTransfer?.files) {
			files = [...files, ...Array.from(e.dataTransfer.files)];
		}
	}

	function removeFile(index: number) {
		files = files.filter((_, i) => i !== index);
	}

	$effect(() => {
		// Auto-extract title from first line if going to Linear
		if ((destination === 'linear' || destination === 'both') && message && !title) {
			const firstLine = message.split('\n')[0];
			if (firstLine.length <= 80) {
				title = firstLine;
			}
		}
	});

	async function send() {
		if (!message.trim() && files.length === 0) return;
		if ((destination === 'linear' || destination === 'both') && !title.trim()) return;

		sending = true;
		statusMessage = null;

		let finalMessage = message;
		if (files.length > 0) {
			finalMessage += '\n\nAttachments:\n' + files.map(f => `- ${f.name}`).join('\n');
		}

		const labelSet = new Set<string>();
		if (label.trim()) labelSet.add(label.trim());
		if (streamLabel.trim()) labelSet.add(streamLabel.trim());
		const labels = Array.from(labelSet);

		const results: string[] = [];
		let hasError = false;

		try {
			// Send to Linear
			if (destination === 'linear' || destination === 'both') {
				const res = await fetch('/api/jobs', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						action: 'create',
						title: title,
						description: finalMessage,
						priority: parseInt(priority),
						labels
					})
				});
				const result = await res.json();
				if (res.ok && result.success) {
					results.push(`Linear: ${result.issue?.identifier || 'Created'}`);
				} else {
					results.push(`Linear: ${result.error || 'Failed'}`);
					hasError = true;
				}
			}

			// Send to Blackboard
			if (destination === 'blackboard' || destination === 'both') {
				const res = await fetch('/api/comms', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						agent: 'human',
						topic: topic,
						message: destination === 'both' ? `[${title}] ${finalMessage}` : finalMessage
					})
				});
				if (res.ok) {
					results.push('Blackboard: Sent');
					await fetchData();
				} else {
					results.push('Blackboard: Failed');
					hasError = true;
				}
			}

			// Send to Agent (via blackboard with @mention)
			if (destination === 'agent') {
				const mentionMsg = `@${targetAgent}: ${finalMessage}`;
				const res = await fetch('/api/comms', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						agent: 'human',
						topic: 'direct',
						message: mentionMsg
					})
				});
				if (res.ok) {
					results.push(`Sent to ${targetAgent}`);
					await fetchData();
				} else {
					results.push('Agent message: Failed');
					hasError = true;
				}
			}

			statusMessage = {
				text: results.join(' | '),
				type: hasError ? 'error' : 'success'
			};

			if (!hasError) {
				message = '';
				title = '';
				files = [];
			}
		} catch (e) {
			statusMessage = { text: 'Connection failed', type: 'error' };
		} finally {
			sending = false;
			setTimeout(() => statusMessage = null, 5000);
		}
	}

	async function fetchData() {
		try {
			const res = await fetch('/api/comms?limit=50');
			const result = await res.json();
			const messages = (result.messages ?? []).map((msg: any) => ({
				...msg,
				time: msg.time || msg.timestamp || ''
			}));
			const byTopic: Record<string, number> = {};
			const byAgent: Record<string, number> = {};
			for (const msg of messages) {
				const msgTopic = msg.topic || 'general';
				const msgAgent = msg.agent || 'unknown';
				byTopic[msgTopic] = (byTopic[msgTopic] || 0) + 1;
				byAgent[msgAgent] = (byAgent[msgAgent] || 0) + 1;
			}
			data = {
				messages,
				stats: {
					total: messages.length,
					by_topic: byTopic,
					by_agent: byAgent
				}
			};
			alertMessages = messages.filter((msg) => msg.topic === 'alerts' || msg.topic === 'critical');
			alertCount = alertMessages.length;
			criticalCount = alertMessages.filter((msg) => msg.topic === 'critical').length;
			earlyExitCount = alertMessages.filter((msg) => msg.message.toLowerCase().includes('early exit')).length;
		} catch (e) {
			console.error('Failed to fetch:', e);
		} finally {
			loading = false;
		}
	}

	async function performSearch() {
		if (!searchQuery.trim()) {
			clearSearch();
			return;
		}

		searching = true;
		isSearchMode = true;
		try {
			const res = await fetch(`/api/comms?search=${encodeURIComponent(searchQuery)}&limit=50`);
			const result = await res.json();
			searchResults = result.messages.filter((m: any) => !m.raw).map((m: any) => ({
				time: m.timestamp,
				agent: m.agent,
				topic: m.topic,
				message: m.message
			}));
		} catch (e) {
			console.error('Search failed:', e);
			searchResults = [];
		} finally {
			searching = false;
		}
	}

	function clearSearch() {
		searchQuery = '';
		searchResults = [];
		isSearchMode = false;
	}

	function handleSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			performSearch();
		} else if (e.key === 'Escape') {
			clearSearch();
		}
	}

	function initSTT() {
		// Check for Web Speech API support
		const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
		if (!SpeechRecognition) {
			sttSupported = false;
			return;
		}

		sttSupported = true;
		recognition = new SpeechRecognition();
		recognition.continuous = true;
		recognition.interimResults = true;
		recognition.lang = 'en-US';

		let finalTranscript = '';

		recognition.onresult = (event: any) => {
			let interimTranscript = '';
			for (let i = event.resultIndex; i < event.results.length; i++) {
				const transcript = event.results[i][0].transcript;
				if (event.results[i].isFinal) {
					finalTranscript += transcript + ' ';
				} else {
					interimTranscript += transcript;
				}
			}
			message = finalTranscript + interimTranscript;
		};

		recognition.onerror = (event: any) => {
			console.error('STT error:', event.error);
			isRecording = false;
			if (event.error === 'not-allowed') {
				statusMessage = { text: 'Microphone access denied', type: 'error' };
				setTimeout(() => statusMessage = null, 3000);
			}
		};

		recognition.onend = () => {
			if (isRecording) {
				recognition.start();
			}
		};
	}

	function toggleRecording() {
		if (!recognition) return;

		if (isRecording) {
			recognition.stop();
			isRecording = false;
		} else {
			recognition.start();
			isRecording = true;
		}
	}

	onMount(() => {
		fetchData();
		initSTT();
		const interval = setInterval(fetchData, 15000);
		return () => clearInterval(interval);
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Comms</h2>
		<div class="header-right">
			<div class="search-box">
				<input
					type="text"
					class="search-input"
					bind:value={searchQuery}
					placeholder="Search messages..."
					onkeydown={handleSearchKeydown}
				/>
				{#if searchQuery}
					<button class="search-clear" onclick={clearSearch}>X</button>
				{/if}
				<button
					class="search-btn"
					onclick={performSearch}
					disabled={searching}
				>
					{searching ? '...' : 'SEARCH'}
				</button>
			</div>
			{#if data}
				<span class="updated">{data.stats.total} messages</span>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="loading">Loading...</div>
	{:else}
		<div class="layout">
			<!-- Unified Send Form -->
			<div class="card send-card">
				<div class="destination-tabs">
					<button
						class="dest-tab"
						class:active={destination === 'linear'}
						onclick={() => destination = 'linear'}
					>
						Linear
					</button>
					<button
						class="dest-tab"
						class:active={destination === 'blackboard'}
						onclick={() => destination = 'blackboard'}
					>
						Blackboard
					</button>
					<button
						class="dest-tab"
						class:active={destination === 'both'}
						onclick={() => destination = 'both'}
					>
						Both
					</button>
					<button
						class="dest-tab"
						class:active={destination === 'agent'}
						onclick={() => destination = 'agent'}
					>
						Agent
					</button>
				</div>

				{#if destination === 'agent'}
					<select bind:value={targetAgent} class="agent-select">
						{#each agents as agent}
							<option value={agent.id}>{agent.name}</option>
						{/each}
					</select>
				{/if}

				{#if destination === 'linear' || destination === 'both'}
					<input
						type="text"
						class="title-input"
						bind:value={title}
						placeholder="Title"
					/>
				{/if}

				<div class="input-container">
					<textarea
						class="message-input"
						bind:value={message}
						placeholder={destination === 'agent' ? `Message to ${targetAgent}...` : destination === 'blackboard' ? 'Message to agents...' : 'Description...'}
						rows="4"
					></textarea>
					<div class="side-controls">
						{#if sttSupported}
							<button
								class="mic-btn"
								class:recording={isRecording}
								onclick={toggleRecording}
								type="button"
								title={isRecording ? 'Stop recording' : 'Start voice input'}
							>
								{#if isRecording}
									<span class="mic-icon recording-pulse">⏹</span>
								{:else}
									<span class="mic-icon">🎤</span>
								{/if}
							</button>
						{/if}
						<div 
							class="drop-zone"
							class:dragging={isDragging}
							ondragover={(e: DragEvent) => { e.preventDefault(); isDragging = true; }}
							ondragleave={() => isDragging = false}
							ondrop={(e: DragEvent) => handleDrop(e)}
							role="button"
							tabindex="0"
							onclick={() => document.getElementById('file-upload')?.click()}
							onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && document.getElementById('file-upload')?.click()}
						>
							<input 
								type="file" 
								id="file-upload" 
								multiple 
								class="hidden-input" 
								onchange={handleFileSelect} 
							/>
							<span class="drop-icon">📎</span>
						</div>
					</div>
				</div>

				{#if files.length > 0}
					<div class="file-list">
						{#each files as file, i}
							<div class="file-item">
								<span class="file-name">{file.name}</span>
								<button class="remove-file" onclick={() => removeFile(i)}>×</button>
							</div>
						{/each}
					</div>
				{/if}

				<div class="options-row">
					{#if destination === 'linear' || destination === 'both'}
						<select bind:value={streamLabel} class="option-select">
							<option value="stream:cash-engine">stream:cash-engine</option>
							<option value="stream:asset-engine">stream:asset-engine</option>
							<option value="stream:apps">stream:apps</option>
						</select>
						<select bind:value={priority} class="option-select">
							<option value="1">Urgent</option>
							<option value="2">High</option>
							<option value="3">Medium</option>
							<option value="4">Low</option>
						</select>
						<select bind:value={label} class="option-select">
							<option value="ai-task">AI Task</option>
							<option value="human-task">Human Task</option>
							<option value="bug">Bug</option>
							<option value="feature">Feature</option>
							<option value="GIN-DEV">GIN-DEV</option>
							<option value="GIN-BIZ">GIN-BIZ</option>
						</select>
					{/if}
					{#if destination === 'blackboard' || destination === 'both'}
						<select bind:value={topic} class="option-select">
							<option value="general">General</option>
							<option value="ideas">Ideas</option>
							<option value="bugs">Bugs</option>
							<option value="help">Help</option>
						</select>
					{/if}
					<div class="spacer"></div>
					<button
						class="send-btn"
						onclick={send}
						disabled={sending || !message.trim() || ((destination === 'linear' || destination === 'both') && !title.trim())}
					>
						{sending ? 'Sending...' : 'Send'}
					</button>
				</div>

				{#if statusMessage}
					<div class="status" class:success={statusMessage.type === 'success'} class:error={statusMessage.type === 'error'}>
						{statusMessage.text}
					</div>
				{/if}
			</div>

			<!-- Search Results -->
			{#if isSearchMode}
				<div class="card feed-card search-results-card">
					<div class="search-header">
						<h3>Search Results for "{searchQuery}"</h3>
						<button class="clear-search-btn" onclick={clearSearch}>CLEAR</button>
					</div>
					{#if searchResults.length === 0}
						<p class="no-results">No messages found matching "{searchQuery}"</p>
					{:else}
						<div class="feed">
							{#each searchResults as msg}
								<div class="msg search-result">
									<div class="msg-header">
										<span class="msg-agent">{msg.agent}</span>
										<span class="msg-topic">#{msg.topic}</span>
										<span class="msg-time">{msg.time?.slice(11, 16) || ''}</span>
									</div>
									<div class="msg-content">{msg.message}</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}

			<!-- Feed -->
			{#if !isSearchMode}
				<div class="card alert-card" class:active={alertCount > 0}>
					<div class="alert-header">
						<h3>Alert Digest</h3>
						<span class="alert-count">{alertCount} in last 50</span>
					</div>
					<div class="alert-stats">
						<span class="stat-pill alert">Alerts: {alertCount}</span>
						<span class="stat-pill critical">Critical: {criticalCount}</span>
						<span class="stat-pill early">Early Exits: {earlyExitCount}</span>
					</div>
					{#if alertMessages.length === 0}
						<p class="no-alerts">No alerts in the recent feed.</p>
					{:else}
						<div class="alert-list">
							{#each alertMessages.slice(0, 6) as msg}
								<div class="alert-item" class:critical={msg.topic === 'critical'}>
									<div class="alert-meta">
										<span>{msg.agent}</span>
										<span>#{msg.topic}</span>
										<span>{msg.time.slice(11, 19)}</span>
									</div>
									<div class="alert-text">{msg.message}</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}

			{#if !isSearchMode && data && data.messages.length > 0}
				<div class="card feed-card">
					<h3>Recent Activity</h3>
					<div class="feed">
						{#each data.messages as msg}
							<div
								class="msg"
								class:alert={msg.topic === 'alerts'}
								class:critical={msg.topic === 'critical'}
								class:early-exit={msg.message.toLowerCase().includes('early exit')}
							>
								<div class="msg-header">
									<span class="msg-agent">{msg.agent}</span>
									<span class="msg-topic">#{msg.topic}</span>
									<span class="msg-time">{msg.time.slice(11, 19)}</span>
								</div>
								<div class="msg-content">{msg.message}</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
		flex-wrap: wrap;
		gap: 12px;
	}

	.header-right {
		display: flex;
		align-items: center;
		gap: 16px;
		flex-wrap: wrap;
	}

	.search-box {
		display: flex;
		align-items: center;
		gap: 0;
		border: 2px solid var(--border);
	}

	.search-input {
		padding: 8px 12px;
		border: none;
		background: var(--surface);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		width: 200px;
	}

	.search-input:focus {
		outline: none;
	}

	.search-input::placeholder {
		color: var(--text-muted);
	}

	.search-clear {
		padding: 8px 10px;
		background: transparent;
		border: none;
		border-left: 1px solid var(--border);
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		cursor: pointer;
	}

	.search-clear:hover {
		color: var(--system-red);
		background: rgba(255, 68, 68, 0.1);
	}

	.search-btn {
		padding: 8px 16px;
		background: var(--border);
		border: none;
		border-left: 2px solid var(--border);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.1s;
	}

	.search-btn:hover:not(:disabled) {
		background: var(--terminal-green);
		color: var(--void);
	}

	.search-btn:disabled {
		opacity: 0.6;
		cursor: wait;
	}

	.search-results-card {
		border-color: var(--cyan-data);
	}

	.search-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
	}

	.search-header h3 {
		margin: 0;
		color: var(--cyan-data);
	}

	.clear-search-btn {
		padding: 6px 12px;
		background: transparent;
		border: 1px solid var(--text-muted);
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 10px;
		font-weight: 700;
		cursor: pointer;
	}

	.clear-search-btn:hover {
		border-color: var(--system-red);
		color: var(--system-red);
	}

	.no-results {
		color: var(--text-muted);
		font-style: italic;
		font-size: 13px;
	}

	.search-result {
		border-left-color: var(--cyan-data);
	}

	.search-result:hover {
		border-left-color: var(--terminal-green);
	}

	.layout {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		box-shadow: 4px 4px 0 0 var(--border);
	}

	.send-card {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.destination-tabs {
		display: flex;
		gap: 0;
		border: 2px solid var(--border);
		width: fit-content;
	}

	.dest-tab {
		padding: 10px 20px;
		background: var(--surface);
		border: none;
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.1s;
		text-transform: uppercase;
	}

	.dest-tab:not(:last-child) {
		border-right: 2px solid var(--border);
	}

	.dest-tab:hover {
		background: rgba(51, 255, 0, 0.1);
		color: var(--text-main);
	}

	.dest-tab.active {
		background: var(--terminal-green);
		color: var(--void);
	}

	.agent-select {
		padding: 12px;
		border: 2px solid var(--terminal-green);
		background: var(--surface);
		color: var(--terminal-green);
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		font-weight: 700;
	}

	.agent-select:focus {
		outline: none;
		box-shadow: 0 0 0 2px rgba(51, 255, 0, 0.3);
	}

	.title-input {
		padding: 12px;
		border: 2px solid var(--border);
		background: var(--surface);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		font-weight: 700;
	}

	.title-input:focus {
		outline: none;
		border-color: var(--terminal-green);
	}

	.input-container {
		position: relative;
		display: flex;
		gap: 8px;
		align-items: stretch;
	}

	.side-controls {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.message-input {
		flex: 1;
		padding: 12px;
		border: 2px solid var(--border);
		background: var(--surface);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		resize: vertical;
		min-height: 100px;
	}

	.message-input:focus {
		outline: none;
		border-color: var(--terminal-green);
	}

	.mic-btn {
		padding: 12px 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-main);
		font-size: 20px;
		cursor: pointer;
		transition: all 0.1s;
		min-width: 56px;
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.mic-btn:hover {
		border-color: var(--terminal-green);
		transform: translate(-1px, -1px);
		box-shadow: 3px 3px 0 0 var(--border);
	}

	.mic-btn:active {
		transform: translate(1px, 1px);
		box-shadow: 1px 1px 0 0 var(--border);
	}

	.drop-zone {
		border: 2px dashed var(--border);
		background: var(--surface);
		color: var(--text-muted);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		min-width: 56px;
		flex: 1;
		transition: all 0.1s;
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.drop-zone:hover {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.05);
	}

	.drop-zone.dragging {
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.1);
		transform: scale(1.02);
	}

	.hidden-input {
		display: none;
	}

	.drop-icon {
		font-size: 20px;
	}

	.file-list {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-top: 8px;
	}

	.file-item {
		display: flex;
		align-items: center;
		gap: 8px;
		background: rgba(51, 255, 0, 0.1);
		border: 1px solid var(--terminal-green);
		padding: 4px 8px;
		border-radius: 4px;
		font-size: 12px;
		color: var(--terminal-green);
	}

	.file-name {
		max-width: 200px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.remove-file {
		background: transparent;
		border: none;
		color: var(--system-red);
		cursor: pointer;
		font-weight: bold;
		font-size: 14px;
		padding: 0 4px;
	}

	.remove-file:hover {
		color: #ff0000;
	}

	.options-row {
		display: flex;
		gap: 12px;
		align-items: center;
		flex-wrap: wrap;
	}


	.option-select {
		padding: 8px 12px;
		border: 2px solid var(--border);
		background: var(--surface);
		color: var(--text-main);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
	}

	.option-select:focus {
		outline: none;
		border-color: var(--terminal-green);
	}

	.spacer {
		flex: 1;
	}

	.send-btn {
		padding: 10px 24px;
		background: var(--terminal-green);
		color: var(--void);
		border: 2px solid var(--terminal-green);
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		font-weight: 700;
		cursor: pointer;
		text-transform: uppercase;
		box-shadow: 4px 4px 0 0 var(--border);
		transition: all 0.1s;
	}

	.send-btn:hover:not(:disabled) {
		transform: translate(-2px, -2px);
		box-shadow: 6px 6px 0 0 var(--border);
	}

	.send-btn:active:not(:disabled) {
		transform: translate(2px, 2px);
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.send-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.status {
		padding: 8px 12px;
		font-size: 12px;
		font-weight: 700;
		font-family: 'JetBrains Mono', monospace;
		border: 2px solid;
	}

	.status.success {
		color: var(--terminal-green);
		border-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.1);
	}

	.status.error {
		color: var(--system-red);
		border-color: var(--system-red);
		background: rgba(255, 0, 0, 0.1);
	}

	.feed-card h3 {
		font-size: 12px;
		font-weight: 700;
		margin: 0 0 16px 0;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.alert-card {
		border-color: var(--warning);
	}

	.alert-card.active {
		border-color: var(--system-red);
		box-shadow: 4px 4px 0 0 var(--system-red);
	}

	.alert-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.alert-header h3 {
		margin: 0;
		color: var(--warning);
		font-size: 12px;
		text-transform: uppercase;
	}

	.alert-count {
		font-size: 10px;
		color: var(--text-muted);
		text-transform: uppercase;
	}

	.alert-stats {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
		margin-bottom: 12px;
	}

	.stat-pill {
		padding: 4px 8px;
		border: 1px solid var(--border);
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
	}

	.stat-pill.alert {
		border-color: var(--warning);
		color: var(--warning);
	}

	.stat-pill.critical {
		border-color: var(--system-red);
		color: var(--system-red);
	}

	.stat-pill.early {
		border-color: var(--cyan-data);
		color: var(--cyan-data);
	}

	.alert-list {
		display: flex;
		flex-direction: column;
		gap: 10px;
		max-height: 220px;
		overflow-y: auto;
	}

	.alert-item {
		border-left: 3px solid var(--warning);
		padding: 6px 10px;
		background: rgba(255, 170, 0, 0.08);
	}

	.alert-item.critical {
		border-left-color: var(--system-red);
		background: rgba(255, 51, 51, 0.08);
	}

	.alert-meta {
		display: flex;
		gap: 10px;
		font-size: 10px;
		color: var(--text-muted);
		margin-bottom: 4px;
	}

	.alert-text {
		font-size: 12px;
		line-height: 1.4;
	}

	.no-alerts {
		color: var(--text-muted);
		font-style: italic;
		font-size: 12px;
	}

	.feed {
		display: flex;
		flex-direction: column;
		gap: 12px;
		max-height: 500px;
		overflow-y: auto;
	}

	.msg {
		border-left: 3px solid var(--border);
		padding: 8px 12px;
		transition: all 0.1s;
	}

	.msg:hover {
		border-left-color: var(--terminal-green);
		background: rgba(51, 255, 0, 0.03);
	}

	.msg.alert {
		border-left-color: var(--warning);
	}

	.msg.critical {
		border-left-color: var(--system-red);
		background: rgba(255, 51, 51, 0.06);
	}

	.msg.early-exit {
		background: rgba(0, 255, 255, 0.04);
	}

	.msg.alert .msg-topic {
		color: var(--warning);
	}

	.msg.critical .msg-topic {
		color: var(--system-red);
	}

	.msg.early-exit .msg-topic {
		color: var(--cyan-data);
	}

	.msg-header {
		display: flex;
		gap: 12px;
		align-items: center;
		margin-bottom: 4px;
		font-size: 11px;
	}

	.msg-agent {
		color: var(--terminal-green);
		font-weight: 700;
	}

	.msg-topic {
		color: var(--cyan-data);
	}

	.msg-time {
		color: var(--text-muted);
		margin-left: auto;
	}

	.msg-content {
		font-size: 13px;
		line-height: 1.5;
		white-space: pre-wrap;
		word-break: break-word;
	}

	.mic-btn {
		padding: 12px 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-main);
		font-size: 20px;
		cursor: pointer;
		transition: all 0.1s;
		min-width: 56px;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 2px 2px 0 0 var(--border);
	}

	.mic-btn:hover {
		border-color: var(--terminal-green);
		transform: translate(-1px, -1px);
		box-shadow: 3px 3px 0 0 var(--border);
	}

	.mic-btn:active {
		transform: translate(1px, 1px);
		box-shadow: 1px 1px 0 0 var(--border);
	}

	.mic-btn.recording {
		background: var(--system-red);
		border-color: var(--system-red);
		color: var(--void);
		animation: pulse 1.5s ease-in-out infinite;
	}

	.mic-btn.recording:hover {
		background: #cc0000;
		border-color: #cc0000;
	}

	.mic-icon {
		display: inline-block;
		line-height: 1;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}
</style>
