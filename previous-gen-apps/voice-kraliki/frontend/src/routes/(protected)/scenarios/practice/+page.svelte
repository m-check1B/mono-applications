<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { ArrowLeftIcon, RefreshCwIcon, CheckCircleIcon, XCircleIcon, SkipForwardIcon } from 'lucide-svelte';

	interface ScenarioNode {
		id: number;
		scenario_id: number;
		node_type: string;
		name: string;
		text_content: string | null;
		next_node_id: number | null;
		options: ScenarioOption[];
		condition_expression: string | null;
		variable_name: string | null;
		variable_value: string | null;
	}

	interface ScenarioOption {
		id: number;
		label: string;
		next_node_id: number | null;
	}

	interface Scenario {
		id: number;
		name: string;
		description: string;
		category: string;
		difficulty: string;
		is_active: boolean;
		entry_node_id: number | null;
	}

	let scenarioId = $state<number | null>(null);
	let scenario = $state<Scenario | null>(null);
	let nodes = $state<ScenarioNode[]>([]);
	let currentNode = $state<ScenarioNode | null>(null);
	let variables = $state<Record<string, string>>({});
	let history = $state<{ node: ScenarioNode; choice?: string }[]>([]);
	let loading = $state(true);
	let sessionComplete = $state(false);
	let finalScore = $state<string | null>(null);

	const nodeMap = $derived(new Map(nodes.map((n) => [n.id, n])));

	onMount(async () => {
		const id = $page.url.searchParams.get('id');
		if (!id) {
			goto('/scenarios');
			return;
		}
		scenarioId = parseInt(id);
		await loadScenario();
	});

	async function loadScenario() {
		if (!scenarioId) return;
		loading = true;
		try {
			const [scenarioRes, nodesRes] = await Promise.all([
				fetch(`/api/scenarios/${scenarioId}`),
				fetch(`/api/scenarios/${scenarioId}/nodes`)
			]);

			if (!scenarioRes.ok) throw new Error('Failed to load scenario');
			scenario = await scenarioRes.json();

			if (nodesRes.ok) {
				nodes = await nodesRes.json();
			}

			// Start at entry node
			if (scenario?.entry_node_id && nodeMap.has(scenario.entry_node_id)) {
				currentNode = nodeMap.get(scenario.entry_node_id)!;
				processCurrentNode();
			} else if (nodes.length > 0) {
				// Fallback to first node
				currentNode = nodes[0];
				processCurrentNode();
			}
		} catch (err) {
			console.error(err);
		} finally {
			loading = false;
		}
	}

	function processCurrentNode() {
		if (!currentNode) return;

		// Handle automatic node types
		if (currentNode.node_type === 'setVariable') {
			// Set the variable
			if (currentNode.variable_name && currentNode.variable_value) {
				variables[currentNode.variable_name] = currentNode.variable_value;
			}
			// Auto-advance
			advanceToNode(currentNode.next_node_id);
		} else if (currentNode.node_type === 'conditional') {
			// Evaluate condition (simple equality check)
			const expr = currentNode.condition_expression || '';
			const match = expr.match(/(\w+)\s*==\s*['"]?(\w+)['"]?/);
			let result = false;
			if (match) {
				const [, varName, value] = match;
				result = variables[varName] === value;
			}

			// Advance based on condition
			if (result) {
				advanceToNode(currentNode.next_node_id);
			} else {
				// Use first option for false branch
				const falseNode = currentNode.options[0]?.next_node_id;
				advanceToNode(falseNode);
			}
		} else if (currentNode.node_type === 'goTo') {
			advanceToNode(currentNode.next_node_id);
		} else if (currentNode.node_type === 'end') {
			sessionComplete = true;
			// Extract score from text content
			const scoreMatch = currentNode.text_content?.match(/Score:\s*(\d+\/\d+)/i);
			if (scoreMatch) {
				finalScore = scoreMatch[1];
			}
		}
	}

	function selectOption(option: ScenarioOption) {
		if (!currentNode) return;

		// Record choice in history
		history = [...history, { node: currentNode, choice: option.label }];

		// Advance to next node
		advanceToNode(option.next_node_id);
	}

	function advanceStatement() {
		if (!currentNode) return;

		// Record in history
		history = [...history, { node: currentNode }];

		// Advance to next node
		advanceToNode(currentNode.next_node_id);
	}

	function advanceToNode(nodeId: number | null | undefined) {
		if (nodeId === null || nodeId === undefined) {
			sessionComplete = true;
			return;
		}

		const nextNode = nodeMap.get(nodeId);
		if (!nextNode) {
			sessionComplete = true;
			return;
		}

		currentNode = nextNode;
		// Process the new node (handles automatic types)
		setTimeout(() => processCurrentNode(), 100);
	}

	function resetSession() {
		variables = {};
		history = [];
		sessionComplete = false;
		finalScore = null;

		if (scenario?.entry_node_id && nodeMap.has(scenario.entry_node_id)) {
			currentNode = nodeMap.get(scenario.entry_node_id)!;
			processCurrentNode();
		} else if (nodes.length > 0) {
			currentNode = nodes[0];
			processCurrentNode();
		}
	}

	function getNodeTypeIcon(type: string): string {
		switch (type) {
			case 'statement':
				return '💬';
			case 'question':
				return '❓';
			case 'end':
				return '🏁';
			default:
				return '📍';
		}
	}

	function getDifficultyColor(diff: string): string {
		switch (diff?.toLowerCase()) {
			case 'easy':
				return 'text-terminal-green';
			case 'medium':
				return 'text-accent';
			case 'hard':
				return 'text-system-red';
			case 'expert':
				return 'text-cyan-data';
			default:
				return 'text-muted-foreground';
		}
	}
</script>

<div class="min-h-screen bg-grid-pattern">
	<div class="max-w-4xl mx-auto p-6">
		<!-- Header -->
		<header class="mb-8 flex items-center justify-between border-b-4 border-foreground pb-6">
			<div class="flex items-center gap-4">
				<a
					href="/scenarios"
					class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all bg-card"
				>
					<ArrowLeftIcon class="w-5 h-5" />
				</a>
				<div>
					<h1 class="text-3xl font-display uppercase tracking-tighter">
						Practice <span class="text-terminal-green">Mode</span>
					</h1>
					{#if scenario}
						<p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1">
							{scenario.name} // {scenario.category} // <span class={getDifficultyColor(scenario.difficulty)}>{scenario.difficulty}</span>
						</p>
					{/if}
				</div>
			</div>
			<button
				onclick={resetSession}
				class="brutal-btn py-2 px-4 text-sm bg-muted hover:bg-accent transition-colors"
				title="Restart Scenario"
			>
				<RefreshCwIcon class="w-4 h-4 inline mr-1" />
				Restart
			</button>
		</header>

		{#if loading}
			<div class="brutal-card p-12 text-center bg-void text-terminal-green">
				<div class="inline-block animate-spin h-10 w-10 border-4 border-terminal-green/30 border-t-terminal-green"></div>
				<p class="mt-4 font-bold uppercase tracking-widest animate-pulse">Loading Simulation...</p>
			</div>
		{:else if sessionComplete}
			<!-- Session Complete -->
			<div class="brutal-card p-8 border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,1)]">
				<div class="text-center mb-8">
					<CheckCircleIcon class="w-16 h-16 mx-auto text-terminal-green mb-4" />
					<h2 class="text-4xl font-display uppercase tracking-tight mb-2">Session Complete</h2>
					{#if finalScore}
						<div class="text-6xl font-display text-terminal-green mt-4">{finalScore}</div>
					{/if}
				</div>

				{#if currentNode?.text_content}
					<div class="p-6 bg-muted/10 border-2 border-muted mb-8">
						<pre class="whitespace-pre-wrap font-mono text-sm leading-relaxed">{currentNode.text_content}</pre>
					</div>
				{/if}

				<div class="flex justify-center gap-4">
					<button
						onclick={resetSession}
						class="brutal-btn bg-terminal-green text-void"
					>
						<RefreshCwIcon class="w-4 h-4 inline mr-2" />
						Try Again
					</button>
					<a
						href="/scenarios"
						class="brutal-btn bg-muted"
					>
						Back to Scenarios
					</a>
				</div>

				<!-- History Review -->
				{#if history.length > 0}
					<div class="mt-8 pt-8 border-t-2 border-muted">
						<h3 class="text-lg font-display uppercase tracking-tight mb-4">Your Journey</h3>
						<div class="space-y-3 max-h-64 overflow-y-auto">
							{#each history as step, idx}
								<div class="flex items-start gap-3 text-sm">
									<span class="text-muted-foreground font-mono text-xs">{idx + 1}.</span>
									<span class="text-lg">{getNodeTypeIcon(step.node.node_type)}</span>
									<div class="flex-1">
										<span class="font-bold">{step.node.name}</span>
										{#if step.choice}
											<span class="text-terminal-green ml-2">→ {step.choice}</span>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{:else if currentNode}
			<!-- Current Node Display -->
			<div class="space-y-6">
				<!-- Progress Indicator -->
				<div class="flex items-center gap-2 text-[10px] font-bold uppercase text-muted-foreground">
					<span class="px-2 py-0.5 bg-terminal-green text-void">
						Step {history.length + 1}
					</span>
					<span>{currentNode.name}</span>
				</div>

				<!-- Node Content Card -->
				<div class="brutal-card p-8 relative overflow-hidden">
					<div class="scanline opacity-5"></div>

					<!-- Node Type Badge -->
					<div class="flex items-center gap-2 mb-6">
						<span class="text-2xl">{getNodeTypeIcon(currentNode.node_type)}</span>
						<span class="px-2 py-0.5 border-2 border-foreground text-[10px] font-bold uppercase">
							{currentNode.node_type}
						</span>
					</div>

					<!-- Text Content -->
					{#if currentNode.text_content}
						<div class="p-6 bg-muted/10 border-2 border-muted mb-6">
							<pre class="whitespace-pre-wrap font-mono text-lg leading-relaxed">{currentNode.text_content}</pre>
						</div>
					{/if}

					<!-- Actions based on node type -->
					{#if currentNode.node_type === 'statement'}
						<button
							onclick={advanceStatement}
							class="brutal-btn w-full bg-terminal-green text-void text-lg py-4 group"
						>
							Continue
							<SkipForwardIcon class="w-5 h-5 inline ml-2 group-hover:translate-x-1 transition-transform" />
						</button>
					{:else if currentNode.node_type === 'question'}
						<div class="space-y-3">
							<p class="text-xs font-bold uppercase text-muted-foreground tracking-widest mb-4">Choose your response:</p>
							{#each currentNode.options as option, idx}
								<button
									onclick={() => selectOption(option)}
									class="brutal-card w-full p-4 text-left hover:border-terminal-green hover:shadow-[4px_4px_0px_0px_rgba(51,255,0,1)] transition-all group"
								>
									<div class="flex items-start gap-4">
										<span class="flex-shrink-0 w-8 h-8 border-2 border-foreground flex items-center justify-center font-bold group-hover:bg-terminal-green group-hover:text-void transition-colors">
											{String.fromCharCode(65 + idx)}
										</span>
										<span class="flex-1 font-mono text-sm leading-relaxed">
											{option.label}
										</span>
									</div>
								</button>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Quick History -->
				{#if history.length > 0}
					<div class="text-[10px] text-muted-foreground">
						<span class="uppercase font-bold tracking-wider">Previous:</span>
						{history.slice(-3).map((h) => h.node.name).join(' → ')}
					</div>
				{/if}
			</div>
		{:else}
			<!-- No nodes -->
			<div class="brutal-card p-12 text-center">
				<XCircleIcon class="w-16 h-16 mx-auto text-system-red mb-4" />
				<h2 class="text-2xl font-display uppercase">No Scenario Data</h2>
				<p class="text-muted-foreground mt-2">This scenario has no nodes defined.</p>
				<a
					href="/scenarios/builder?id={scenarioId}"
					class="mt-4 inline-block text-terminal-green font-bold uppercase text-sm hover:underline"
				>
					Open in Builder
				</a>
			</div>
		{/if}
	</div>
</div>
