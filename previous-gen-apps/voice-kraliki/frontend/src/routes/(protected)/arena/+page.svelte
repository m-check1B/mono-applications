<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { MicIcon, MicOffIcon, PhoneIcon, PhoneOffIcon, PlayIcon, StopCircleIcon, Volume2Icon, UserIcon, ArrowLeftIcon, RefreshCwIcon } from 'lucide-svelte';

	interface Persona {
		id: string;
		name: string;
		description: string;
		emotional_state: string;
		response_style: string;
	}

	interface TranscriptEntry {
		role: 'trainee' | 'persona' | 'system';
		content: string;
		timestamp: string;
	}

	let personas = $state<Persona[]>([]);
	let selectedPersona = $state<Persona | null>(null);
	let sessionId = $state<string | null>(null);
	let sessionState = $state<'idle' | 'connecting' | 'active' | 'ended'>('idle');
	let transcript = $state<TranscriptEntry[]>([]);
	let userInput = $state('');
	let loading = $state(true);
	let isMuted = $state(false);
	let isRecording = $state(false);
	let ws: WebSocket | null = null;
	let duration = $state(0);
	let durationInterval: ReturnType<typeof setInterval> | null = null;

	onMount(async () => {
		await loadPersonas();
	});

	onDestroy(() => {
		if (ws) {
			ws.close();
		}
		if (durationInterval) {
			clearInterval(durationInterval);
		}
	});

	async function loadPersonas() {
		loading = true;
		try {
			const response = await fetch('/api/arena/personas');
			if (response.ok) {
				const data = await response.json();
				personas = data.personas || [];
			}
		} catch (err) {
			console.error('Failed to load personas:', err);
			addSystemMessage('Failed to load personas. Please refresh the page.');
		} finally {
			loading = false;
		}
	}

	async function createSession() {
		if (!selectedPersona) {
			addSystemMessage('Please select a persona first.');
			return;
		}

		sessionState = 'connecting';
		addSystemMessage(`Creating session with ${selectedPersona.name}...`);

		try {
			const response = await fetch('/api/arena/sessions', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					persona_type: selectedPersona.id
				})
			});

			if (!response.ok) {
				throw new Error('Failed to create session');
			}

			const data = await response.json();
			sessionId = data.session_id;

			// Connect WebSocket
			connectWebSocket();
		} catch (err) {
			console.error('Failed to create session:', err);
			addSystemMessage('Failed to create session. Please try again.');
			sessionState = 'idle';
		}
	}

	function connectWebSocket() {
		if (!sessionId) return;

		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsUrl = `${protocol}//${window.location.host}/api/arena/ws/${sessionId}`;

		ws = new WebSocket(wsUrl);

		ws.onopen = () => {
			addSystemMessage('Connected to arena. Starting session...');
			ws?.send(JSON.stringify({ type: 'start-arena' }));
		};

		ws.onmessage = (event) => {
			const data = JSON.parse(event.data);
			handleWebSocketMessage(data);
		};

		ws.onclose = () => {
			if (sessionState === 'active') {
				addSystemMessage('Connection lost. Session ended.');
				endSession();
			}
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
			addSystemMessage('Connection error occurred.');
		};
	}

	function handleWebSocketMessage(data: any) {
		switch (data.type) {
			case 'arena-started':
				sessionState = 'active';
				isRecording = true;
				startDurationTimer();
				addSystemMessage(`Session started with ${data.persona}. Begin speaking!`);
				break;

			case 'persona-response':
				transcript = [...transcript, {
					role: 'persona',
					content: data.response,
					timestamp: new Date().toISOString()
				}];
				break;

			case 'arena-ended':
				sessionState = 'ended';
				isRecording = false;
				stopDurationTimer();
				const durationStr = formatDuration(data.duration || duration);
				addSystemMessage(`Session ended. Duration: ${durationStr}`);
				break;

			case 'error':
				addSystemMessage(`Error: ${data.error}`);
				break;
		}
	}

	function sendUserInput() {
		if (!userInput.trim() || !ws || sessionState !== 'active') return;

		// Add to transcript
		transcript = [...transcript, {
			role: 'trainee',
			content: userInput,
			timestamp: new Date().toISOString()
		}];

		// Send to server
		ws.send(JSON.stringify({
			type: 'get-response',
			input: userInput
		}));

		userInput = '';
	}

	function endSession() {
		if (ws && sessionState === 'active') {
			ws.send(JSON.stringify({
				type: 'end-arena',
				scorecard: {
					empathy: 5,
					clarity: 4,
					resolution: 5
				}
			}));
		}
		sessionState = 'ended';
		stopDurationTimer();
	}

	function resetSession() {
		sessionId = null;
		sessionState = 'idle';
		transcript = [];
		duration = 0;
		selectedPersona = null;
		if (ws) {
			ws.close();
			ws = null;
		}
	}

	function addSystemMessage(content: string) {
		transcript = [...transcript, {
			role: 'system',
			content,
			timestamp: new Date().toISOString()
		}];
	}

	function startDurationTimer() {
		duration = 0;
		durationInterval = setInterval(() => {
			duration++;
		}, 1000);
	}

	function stopDurationTimer() {
		if (durationInterval) {
			clearInterval(durationInterval);
			durationInterval = null;
		}
	}

	function formatDuration(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function formatTimestamp(iso: string): string {
		return new Date(iso).toLocaleTimeString();
	}

	function getPersonaColor(id: string): string {
		const colors: Record<string, string> = {
			'angry_customer': 'bg-system-red',
			'curious_learner': 'bg-primary',
			'confused_user': 'bg-accent',
			'satisfied_client': 'bg-terminal-green',
			'persistent_issue_reporter': 'bg-cyan-data'
		};
		return colors[id] || 'bg-muted';
	}
</script>

<div class="p-6 max-w-7xl mx-auto min-h-screen space-y-6">
	<!-- Header -->
	<header class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-4 border-foreground pb-6">
		<div class="flex items-center gap-4">
			<a
				href="/scenarios"
				class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all bg-card"
			>
				<ArrowLeftIcon class="w-5 h-5" />
			</a>
			<div>
				<h1 class="text-4xl font-display text-foreground tracking-tighter uppercase">
					Voice <span class="text-terminal-green">Arena</span>
				</h1>
				<p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1">
					1:1 AI TRAINING // STATUS: {sessionState.toUpperCase()}
				</p>
			</div>
		</div>
		<div class="flex items-center gap-4">
			{#if sessionState === 'active'}
				<div class="flex items-center gap-2 px-3 py-1 bg-system-red/10 border-2 border-system-red text-system-red">
					<span class="w-2 h-2 bg-system-red rounded-full animate-pulse"></span>
					<span class="text-xs font-bold uppercase">{formatDuration(duration)}</span>
				</div>
			{/if}
		</div>
	</header>

	<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
		<!-- Left Panel: Persona Selection & Controls -->
		<div class="lg:col-span-4 space-y-6">
			<!-- Persona Selection -->
			<div class="brutal-card">
				<div class="flex items-center gap-2 mb-4 border-b-2 border-foreground pb-2">
					<div class="w-3 h-3 bg-terminal-green"></div>
					<h2 class="text-xl font-display uppercase tracking-tight">Select Persona</h2>
				</div>

				{#if loading}
					<div class="p-8 text-center">
						<div class="inline-block w-8 h-8 border-4 border-terminal-green/30 border-t-terminal-green animate-spin"></div>
						<p class="mt-2 text-xs font-bold uppercase text-muted-foreground">Loading personas...</p>
					</div>
				{:else}
					<div class="space-y-3">
						{#each personas as persona}
							<button
								onclick={() => selectedPersona = persona}
								disabled={sessionState !== 'idle'}
								class="w-full text-left p-4 border-2 transition-all {selectedPersona?.id === persona.id ? 'border-terminal-green bg-terminal-green/5 shadow-[4px_4px_0px_0px_rgba(51,255,0,1)]' : 'border-border hover:border-muted-foreground'} {sessionState !== 'idle' ? 'opacity-50 cursor-not-allowed' : ''}"
							>
								<div class="flex items-start gap-3">
									<div class="w-10 h-10 {getPersonaColor(persona.id)} flex items-center justify-center text-void">
										<UserIcon class="w-5 h-5" />
									</div>
									<div class="flex-1">
										<div class="font-display text-sm uppercase">{persona.name}</div>
										<div class="text-[10px] text-muted-foreground line-clamp-2 mt-1">{persona.description}</div>
									</div>
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Session Controls -->
			<div class="brutal-card">
				<div class="flex items-center gap-2 mb-4 border-b-2 border-foreground pb-2">
					<div class="w-3 h-3 bg-cyan-data"></div>
					<h2 class="text-xl font-display uppercase tracking-tight">Controls</h2>
				</div>

				<div class="space-y-4">
					{#if sessionState === 'idle'}
						<button
							onclick={createSession}
							disabled={!selectedPersona}
							class="w-full brutal-btn bg-terminal-green text-void {!selectedPersona ? 'opacity-50 cursor-not-allowed' : ''}"
						>
							<PlayIcon class="w-5 h-5 inline mr-2" />
							Start Session
						</button>
					{:else if sessionState === 'connecting'}
						<button disabled class="w-full brutal-btn bg-muted text-muted-foreground cursor-wait">
							<RefreshCwIcon class="w-5 h-5 inline mr-2 animate-spin" />
							Connecting...
						</button>
					{:else if sessionState === 'active'}
						<div class="flex gap-2">
							<button
								onclick={() => isMuted = !isMuted}
								class="flex-1 brutal-btn {isMuted ? 'bg-system-red text-white' : 'bg-muted text-foreground'}"
							>
								{#if isMuted}
									<MicOffIcon class="w-5 h-5 inline mr-2" />
									Muted
								{:else}
									<MicIcon class="w-5 h-5 inline mr-2" />
									Mic On
								{/if}
							</button>
							<button
								onclick={endSession}
								class="flex-1 brutal-btn bg-system-red text-white"
							>
								<PhoneOffIcon class="w-5 h-5 inline mr-2" />
								End
							</button>
						</div>
					{:else if sessionState === 'ended'}
						<button
							onclick={resetSession}
							class="w-full brutal-btn bg-primary text-primary-foreground"
						>
							<RefreshCwIcon class="w-5 h-5 inline mr-2" />
							New Session
						</button>
					{/if}

					{#if selectedPersona && sessionState === 'idle'}
						<div class="p-3 bg-muted/10 border border-muted text-xs">
							<div class="font-bold uppercase text-muted-foreground mb-1">Selected:</div>
							<div class="font-display">{selectedPersona.name}</div>
							<div class="text-muted-foreground mt-1">
								Mood: {selectedPersona.emotional_state}
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Right Panel: Transcript & Input -->
		<div class="lg:col-span-8">
			<div class="brutal-card h-full flex flex-col">
				<div class="flex items-center justify-between gap-2 mb-4 border-b-2 border-foreground pb-2">
					<div class="flex items-center gap-2">
						<div class="w-3 h-3 bg-primary"></div>
						<h2 class="text-xl font-display uppercase tracking-tight">Conversation</h2>
					</div>
					{#if isRecording}
						<div class="flex items-center gap-2 text-system-red">
							<span class="w-2 h-2 bg-system-red rounded-full animate-pulse"></span>
							<span class="text-[10px] font-bold uppercase">Recording</span>
						</div>
					{/if}
				</div>

				<!-- Transcript -->
				<div class="flex-1 min-h-[400px] max-h-[600px] overflow-y-auto space-y-3 mb-4 p-4 bg-muted/5 border border-muted">
					{#if transcript.length === 0}
						<div class="text-center py-12 text-muted-foreground">
							<PhoneIcon class="w-12 h-12 mx-auto mb-4 opacity-20" />
							<p class="text-xs font-bold uppercase">Select a persona and start the session</p>
						</div>
					{:else}
						{#each transcript as entry}
							<div class="flex {entry.role === 'trainee' ? 'justify-end' : 'justify-start'}">
								<div class="max-w-[80%] p-3 {
									entry.role === 'trainee'
										? 'bg-terminal-green/20 border-terminal-green text-foreground'
										: entry.role === 'persona'
											? 'bg-primary/20 border-primary text-foreground'
											: 'bg-muted/20 border-muted text-muted-foreground italic'
								} border-2">
									{#if entry.role !== 'system'}
										<div class="text-[9px] font-bold uppercase opacity-70 mb-1">
											{entry.role === 'trainee' ? 'You' : selectedPersona?.name || 'AI'}
										</div>
									{/if}
									<div class="text-sm">{entry.content}</div>
									<div class="text-[9px] opacity-50 mt-1">{formatTimestamp(entry.timestamp)}</div>
								</div>
							</div>
						{/each}
					{/if}
				</div>

				<!-- Input -->
				{#if sessionState === 'active'}
					<div class="flex gap-2">
						<input
							type="text"
							bind:value={userInput}
							onkeydown={(e) => e.key === 'Enter' && sendUserInput()}
							placeholder="Type your response..."
							class="flex-1 brutal-input"
						/>
						<button
							onclick={sendUserInput}
							disabled={!userInput.trim()}
							class="brutal-btn bg-terminal-green text-void {!userInput.trim() ? 'opacity-50' : ''}"
						>
							Send
						</button>
					</div>
					<p class="text-[10px] text-muted-foreground mt-2">
						Press Enter to send your message. The AI persona will respond based on the scenario.
					</p>
				{/if}
			</div>
		</div>
	</div>
</div>
