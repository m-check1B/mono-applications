<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { PlusIcon, SaveIcon, ArrowLeftIcon, Trash2Icon, Edit2Icon, PhoneIcon, MenuIcon } from 'lucide-svelte';

	interface ScenarioNode {
		id?: number;
		temp_id?: number;
		scenario_id?: number;
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
		id?: number;
		label: string;
		next_node_id: number | null;
	}

	interface Scenario {
		id?: number;
		name: string;
		description: string;
		category: string;
		difficulty: string;
		is_active: boolean;
		entry_node_id: number | null;
	}

	let scenarioId = $state<number | null>(null);
	let scenario = $state<Scenario>({
		name: '',
		description: '',
		category: 'Customer Service',
		difficulty: 'Medium',
		is_active: true,
		entry_node_id: null
	});

	let nodes = $state<ScenarioNode[]>([]);
	let selectedNode = $state<ScenarioNode | null>(null);
	let showNodeEditor = $state(false);
	let loading = $state(false);
	let saving = $state(false);
	let nextTempId = $state(-1);

	const nodeTypes = [
		{ value: 'statement', label: 'Statement', description: 'Agent or Customer makes a statement' },
		{ value: 'question', label: 'Question', description: 'Ask a question with multiple choices' },
		{ value: 'conditional', label: 'Conditional', description: 'Branch based on variable/state' },
		{ value: 'goTo', label: 'Go To', description: 'Jump to another node' },
		{ value: 'setVariable', label: 'Set Variable', description: 'Update scenario state' },
		{ value: 'end', label: 'End Scenario', description: 'Terminate the scenario' }
	];

	onMount(async () => {
		const id = $page.url.searchParams.get('id');
		if (id) {
			scenarioId = parseInt(id);
			await loadScenario();
		}
	});

	async function loadScenario() {
		if (!scenarioId) return;
		loading = true;
		try {
			const response = await fetch(`/api/scenarios/${scenarioId}`);
			if (!response.ok) throw new Error('Failed to load scenario');
			const data = await response.json();
			scenario = data;

			// Load nodes for this scenario
			const nodesResponse = await fetch(`/api/scenarios/${scenarioId}/nodes`);
			if (nodesResponse.ok) {
				nodes = await nodesResponse.json();
			}
		} catch (err) {
			console.error(err);
		} finally {
			loading = false;
		}
	}

	async function saveScenario() {
		if (!scenario.name.trim()) {
			alert('Please enter a scenario name');
			return;
		}

		saving = true;
		try {
			const method = scenarioId ? 'PUT' : 'POST';
			const url = scenarioId
				? `/api/scenarios/${scenarioId}`
				: '/api/scenarios';

			const response = await fetch(url, {
				method,
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(scenario)
			});

			if (!response.ok) throw new Error('Failed to save scenario');
			const savedScenario = await response.json();

			if (!scenarioId) {
				scenarioId = savedScenario.id;
				scenario.id = savedScenario.id;
			}

			// Save nodes in two passes to resolve client temp IDs.
			for (const node of nodes) {
				if (!node.id) {
					await saveNode(node, { next_node_id: null, options: [] });
				}
			}

			const tempIdMap = new Map<number, number>();
			for (const node of nodes) {
				if (node.temp_id && node.id) {
					tempIdMap.set(node.temp_id, node.id);
				}
			}

			for (const node of nodes) {
				const resolvedOptions = (node.options || []).map((option) => ({
					...option,
					next_node_id: resolveNodeId(option.next_node_id, tempIdMap)
				}));

				await saveNode(node, {
					next_node_id: resolveNodeId(node.next_node_id, tempIdMap),
					options: resolvedOptions
				});
			}

			alert('Scenario saved successfully!');
			goto('/scenarios');
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save scenario');
		} finally {
			saving = false;
		}
	}

	function resolveNodeId(value: number | null | undefined, tempIdMap: Map<number, number>): number | null {
		if (value === null || value === undefined) return null;
		if (value < 0) {
			return tempIdMap.get(value) ?? null;
		}
		return value;
	}

	function buildNodePayload(node: ScenarioNode, overrides: Partial<ScenarioNode> = {}) {
		const { temp_id, ...rest } = node;
		return { ...rest, ...overrides };
	}

	async function saveNode(node: ScenarioNode, overrides: Partial<ScenarioNode> = {}) {
		if (!scenarioId) return;

		const method = node.id ? 'PUT' : 'POST';
		const url = node.id
			? `/api/scenarios/nodes/${node.id}`
			: '/api/scenarios/nodes';

		const payload = buildNodePayload(node, overrides);
		const response = await fetch(url, {
			method,
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				...payload,
				scenario_id: scenarioId
			})
		});

		if (!response.ok) throw new Error('Failed to save node');
		const savedNode = await response.json();
		if (!node.id) {
			node.id = savedNode.id;
		}
	}

	function addNode() {
		const newNode: ScenarioNode = {
			temp_id: nextTempId--,
			scenario_id: scenarioId || undefined,
			node_type: 'statement',
			name: `Node ${nodes.length + 1}`,
			text_content: '',
			next_node_id: null,
			options: [],
			condition_expression: null,
			variable_name: null,
			variable_value: null
		};
		nodes = [...nodes, newNode];
		selectedNode = newNode;
		showNodeEditor = true;
	}

	function editNode(node: ScenarioNode) {
		selectedNode = node;
		showNodeEditor = true;
	}

	function deleteNode(index: number) {
		const nodeToDelete = nodes[index];
		if (confirm('Are you sure you want to delete this node?')) {
			nodes = nodes.filter((_, i) => i !== index);
			if (selectedNode === nodeToDelete) {
				selectedNode = null;
				showNodeEditor = false;
			}
		}
	}

	function addOption() {
		if (!selectedNode) return;
		if (!selectedNode.options) {
			selectedNode.options = [];
		}
		selectedNode.options = [
			...selectedNode.options,
			{
				label: '',
				next_node_id: null
			}
		];
	}

	function removeOption(index: number) {
		if (!selectedNode) return;
		selectedNode.options = selectedNode.options.filter((_, i) => i !== index);
	}

	function getNodeTypeLabel(type: string): string {
		return nodeTypes.find((t) => t.value === type)?.label || type;
	}

	function getNodeRef(node: ScenarioNode): number | null {
		return node.id ?? node.temp_id ?? null;
	}

	function getNodeColor(type: string): string {
		const colors: Record<string, string> = {
			statement: 'bg-terminal-green text-void',
			question: 'bg-primary text-primary-foreground',
			conditional: 'bg-accent text-accent-foreground',
			goTo: 'bg-cyan-data text-void',
			setVariable: 'bg-muted text-foreground',
			end: 'bg-system-red text-white'
		};
		return colors[type] || 'bg-secondary text-foreground';
	}
</script>

<div class="p-6 max-w-7xl mx-auto bg-grid-pattern min-h-screen">
	<!-- Header -->
	<div class="mb-8 flex flex-col md:flex-row md:items-center justify-between border-b-4 border-foreground pb-6 gap-4">
		<div class="flex items-center gap-6">
			<a
				href="/scenarios"
				class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-card"
			>
				<ArrowLeftIcon class="w-6 h-6" />
			</a>
			<div>
				<h1 class="text-4xl font-display text-foreground tracking-tighter">
					{scenarioId ? 'Edit Scenario' : 'New Scenario'}
				</h1>
				<p class="text-muted-foreground uppercase font-bold tracking-[0.2em] text-[10px] mt-1">Design your training scenario // V1.0 // SYSTEM_READY</p>
			</div>
		</div>
		<div class="flex items-center gap-4">
			{#if saving}
				<span class="text-[10px] font-black uppercase text-terminal-green animate-pulse">Syncing to database...</span>
			{/if}
			<button
				onclick={saveScenario}
				disabled={saving}
				class="brutal-btn bg-primary text-primary-foreground"
			>
				<SaveIcon class="w-5 h-5 inline mr-2" />
				{saving ? 'Saving...' : 'Save Scenario'}
			</button>
		</div>
	</div>

	{#if loading}
		<div class="p-12 text-center brutal-card bg-void text-terminal-green">
			<div class="inline-block animate-spin h-10 w-10 border-4 border-terminal-green/30 border-t-terminal-green"></div>
			<p class="mt-4 font-bold uppercase tracking-widest animate-pulse">Initialising Scenario Data...</p>
			<p class="text-[10px] mt-2 font-mono opacity-50">GET /api/scenarios/{scenarioId} ... PENDING</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
			<!-- Scenario Configuration -->
			<div class="lg:col-span-8 space-y-8">
				<!-- Basic Info -->
				<div class="brutal-card">
					<div class="flex items-center gap-3 mb-6 border-b-2 border-foreground pb-2">
						<div class="w-3 h-3 bg-terminal-green"></div>
						<h2 class="text-2xl font-display uppercase tracking-tight">Global Settings</h2>
					</div>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div class="md:col-span-2">
							<label for="scenario-name" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">
								// Scenario Name
							</label>
							<input
								id="scenario-name"
								type="text"
								bind:value={scenario.name}
								placeholder="e.g., Dealing with Angry Customer"
								class="w-full brutal-input focus:border-terminal-green"
							/>
						</div>
						<div class="md:col-span-2">
							<label for="scenario-desc" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">
								// Description
							</label>
							<textarea
								id="scenario-desc"
								bind:value={scenario.description}
								placeholder="What should the agent learn from this scenario?"
								rows="3"
								class="w-full brutal-input focus:border-terminal-green"
							></textarea>
						</div>
						<div>
							<label for="scenario-cat" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">
								// Category
							</label>
							<select id="scenario-cat" bind:value={scenario.category} class="w-full brutal-input">
								<option>Customer Service</option>
								<option>Sales</option>
								<option>Technical Support</option>
								<option>Compliance</option>
							</select>
						</div>
						<div>
							<label for="scenario-diff" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">
								// Difficulty
							</label>
							<select id="scenario-diff" bind:value={scenario.difficulty} class="w-full brutal-input">
								<option>Easy</option>
								<option>Medium</option>
								<option>Hard</option>
								<option>Expert</option>
							</select>
						</div>
					</div>
				</div>

				<!-- Nodes List -->
				<div class="brutal-card relative overflow-hidden">
					<div class="scanline opacity-10"></div>
					<div class="flex items-center justify-between mb-6 border-b-2 border-foreground pb-2">
						<div class="flex items-center gap-3">
							<div class="w-3 h-3 bg-cyan-data"></div>
							<h2 class="text-2xl font-display uppercase tracking-tight">Scenario Flow</h2>
						</div>
						<button
							onclick={addNode}
							class="brutal-btn py-2 px-4 text-sm bg-terminal-green text-void"
						>
							<PlusIcon class="w-4 h-4 inline mr-1" />
							Add Node
						</button>
					</div>

					{#if nodes.length === 0}
						<div class="text-center py-20 border-2 border-dashed border-muted bg-muted/5">
							<MenuIcon class="w-16 h-16 text-muted/30 mx-auto mb-4" />
							<p class="text-muted-foreground font-bold uppercase tracking-widest text-xs">No nodes defined in buffer.</p>
							<button onclick={addNode} class="mt-4 text-terminal-green font-bold uppercase text-xs hover:underline cursor-pointer">Create your first node</button>
						</div>
					{:else}
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							{#each nodes as node, index}
								<div
									role="button"
									tabindex="0"
									onclick={() => editNode(node)}
									onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') editNode(node); }}
									class="text-left w-full brutal-card p-4 hover:border-terminal-green hover:shadow-[6px_6px_0px_0px_rgba(51,255,0,1)] transition-all group cursor-pointer {selectedNode === node ? 'border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,1)]' : ''}"
								>
									<div class="flex items-start justify-between gap-4">
										<div class="flex-1">
											<div class="flex items-center gap-2 mb-3">
												<span class="px-2 py-0.5 border-2 border-foreground text-[9px] font-bold uppercase {getNodeColor(node.node_type)}">
													{getNodeTypeLabel(node.node_type)}
												</span>
												<div class="font-display text-sm truncate max-w-[150px] uppercase tracking-tight">{node.name}</div>
											</div>
											<div class="text-[11px] text-muted-foreground font-mono line-clamp-2 bg-muted/20 p-2 border border-muted/30">
												{node.text_content || 'EMPTY_BUFFER'}
											</div>
										</div>
										<div class="flex flex-col gap-2">
											<div class="p-1 border-2 border-foreground group-hover:border-terminal-green transition-colors bg-card">
												<Edit2Icon class="w-3 h-3" />
											</div>
											<button
												onclick={(e) => { e.stopPropagation(); deleteNode(index); }}
												class="p-1 border-2 border-foreground hover:bg-system-red hover:text-white transition-colors bg-card"
											>
												<Trash2Icon class="w-3 h-3" />
											</button>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Node Editor Sidebar -->
			<div class="lg:col-span-4">
				{#if showNodeEditor && selectedNode}
					<div class="brutal-card sticky top-6 border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,1)]">
						<div class="flex items-center gap-3 mb-6 border-b-2 border-terminal-green pb-2">
							<div class="w-3 h-3 bg-terminal-green animate-pulse"></div>
							<h2 class="text-2xl font-display uppercase tracking-tight">Node Editor</h2>
						</div>

						<div class="space-y-6">
							<div>
								<label for="node-type" class="block text-xs font-bold uppercase mb-2 tracking-widest text-muted-foreground">
									// Node Type
								</label>
								<select
									id="node-type"
									bind:value={selectedNode.node_type}
									class="w-full brutal-input bg-void text-terminal-green border-terminal-green"
								>
									{#each nodeTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							<div>
								<label for="node-name" class="block text-xs font-bold uppercase mb-2 tracking-widest text-muted-foreground">
									// Identifier
								</label>
								<input
									id="node-name"
									type="text"
									bind:value={selectedNode.name}
									placeholder="e.g., Intro"
									class="w-full brutal-input"
								/>
							</div>

							<div>
								<label for="node-content" class="block text-xs font-bold uppercase mb-2 tracking-widest text-muted-foreground">
									// Script Payload
								</label>
								<textarea
									id="node-content"
									bind:value={selectedNode.text_content}
									placeholder="Enter the dialogue or instructions..."
									rows="8"
									class="w-full brutal-input font-mono text-sm bg-muted/5"
								></textarea>
							</div>

							{#if selectedNode.node_type === 'question'}
								<div class="border-t-2 border-muted pt-4">
									<div class="flex items-center justify-between mb-4">
										<span class="block text-xs font-bold uppercase tracking-widest text-muted-foreground">
											// Branch Options
										</span>
										<button
											onclick={addOption}
											class="text-[10px] font-bold uppercase bg-terminal-green text-void px-2 py-1 brutal-border shadow-brutal-sm active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-all"
										>
											+ Add Option
										</button>
									</div>
									<div class="space-y-3">
										{#each selectedNode.options || [] as option, idx}
											<div class="flex flex-col gap-2 p-3 border-2 border-muted bg-muted/5">
												<div class="flex gap-2">
													<input
														type="text"
														bind:value={option.label}
														placeholder="Choice text"
														class="flex-1 brutal-input py-1 text-xs"
														aria-label="Option Label"
													/>
													<button
														onclick={() => removeOption(idx)}
														class="p-1 border-2 border-foreground hover:bg-system-red hover:text-white bg-card"
														aria-label="Remove Option"
													>
														<Trash2Icon class="w-4 h-4" />
													</button>
												</div>
												<div class="flex items-center gap-2">
													<span class="text-[9px] font-bold uppercase text-muted-foreground tracking-tighter font-mono">NEXT_PTR:</span>
													<select
														bind:value={option.next_node_id}
														class="flex-1 brutal-input py-1 text-[10px]"
														aria-label="Next Node"
													>
														<option value={null}>[ TERMINATE ]</option>
														{#each nodes as n}
															{#if n !== selectedNode}
																<option value={getNodeRef(n)}>{n.name}</option>
															{/if}
														{/each}
													</select>
												</div>
											</div>
									{/each}
									</div>
								</div>
							{/if}

							{#if selectedNode.node_type === 'setVariable'}
								<div class="border-t-2 border-muted pt-4 space-y-4">
									<span class="block text-xs font-bold uppercase tracking-widest text-muted-foreground">
										// Variable Configuration
									</span>
									<div>
										<label for="var-name" class="block text-[10px] uppercase font-bold text-muted-foreground mb-1">Variable Name</label>
										<input
											id="var-name"
											type="text"
											bind:value={selectedNode.variable_name}
											placeholder="e.g. customer_mood"
											class="w-full brutal-input py-1 text-sm"
										/>
									</div>
									<div>
										<label for="var-value" class="block text-[10px] uppercase font-bold text-muted-foreground mb-1">Variable Value</label>
										<input
											id="var-value"
											type="text"
											bind:value={selectedNode.variable_value}
											placeholder="e.g. happy"
											class="w-full brutal-input py-1 text-sm"
										/>
									</div>
								</div>
							{/if}

							{#if selectedNode.node_type === 'conditional'}
								<div class="border-t-2 border-muted pt-4 space-y-4">
									<span class="block text-xs font-bold uppercase tracking-widest text-muted-foreground">
										// Logic Configuration
									</span>
									<div>
										<label for="cond-expr" class="block text-[10px] uppercase font-bold text-muted-foreground mb-1">Condition Expression</label>
										<input
											id="cond-expr"
											type="text"
											bind:value={selectedNode.condition_expression}
											placeholder="e.g. customer_mood == 'angry'"
											class="w-full brutal-input py-1 text-sm font-mono"
										/>
									</div>
									
									<div class="space-y-3">
										<div class="p-3 border-2 border-terminal-green bg-terminal-green/5">
											<label for="true-path" class="block text-[10px] uppercase font-bold text-terminal-green mb-1">IF TRUE (NEXT_NODE)</label>
											<select
												id="true-path"
												bind:value={selectedNode.next_node_id}
												class="w-full brutal-input py-1 text-xs"
											>
												<option value={null}>[ TERMINATE ]</option>
												{#each nodes as n}
													{#if n !== selectedNode}
														<option value={getNodeRef(n)}>{n.name}</option>
													{/if}
												{/each}
											</select>
										</div>

										<div class="p-3 border-2 border-system-red bg-system-red/5">
											<label for="false-path" class="block text-[10px] uppercase font-bold text-system-red mb-1">IF FALSE (DEFAULT)</label>
											<select
												id="false-path"
												value={selectedNode.options?.[0]?.next_node_id ?? null}
												onchange={(e) => {
													const val = e.currentTarget.value ? parseInt(e.currentTarget.value) : null;
													if (!selectedNode.options) selectedNode.options = [];
													if (selectedNode.options.length === 0) {
														selectedNode.options = [{ label: 'FALSE', next_node_id: val }];
													} else {
														selectedNode.options[0].next_node_id = val;
													}
												}}
												class="w-full brutal-input py-1 text-xs"
											>
												<option value={null}>[ TERMINATE ]</option>
												{#each nodes as n}
													{#if n !== selectedNode}
														<option value={getNodeRef(n)}>{n.name}</option>
													{/if}
												{/each}
											</select>
										</div>
									</div>
								</div>
							{/if}

							{#if selectedNode.node_type === 'goTo' || selectedNode.node_type === 'statement' || selectedNode.node_type === 'setVariable'}
								<div class="border-t-2 border-muted pt-4">
									<label for="next-node" class="block text-xs font-bold uppercase mb-2 tracking-widest text-muted-foreground">
										// Flow Progression
									</label>
									<select
										id="next-node"
										bind:value={selectedNode.next_node_id}
										class="w-full brutal-input"
									>
										<option value={null}>[ TERMINATE SCENARIO ]</option>
										{#each nodes as n}
											{#if n !== selectedNode}
												<option value={getNodeRef(n)}>{n.name}</option>
											{/if}
										{/each}
									</select>
								</div>
							{/if}
						</div>
					</div>
				{:else}
					<div class="brutal-card text-center py-32 bg-muted/5 border-dashed">
						<div class="relative inline-block">
							<PhoneIcon class="w-16 h-16 text-muted/20 mx-auto mb-4" />
							<div class="absolute inset-0 flex items-center justify-center">
								<div class="w-8 h-8 border-2 border-terminal-green/30 animate-ping"></div>
							</div>
						</div>
						<p class="text-muted-foreground font-bold uppercase tracking-widest text-[10px]">Awaiting Node Selection // BUFFER_IDLE</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
