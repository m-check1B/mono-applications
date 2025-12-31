<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { Plus, Save, ArrowLeft, Trash2, Edit2, Phone, Menu as MenuIcon } from 'lucide-svelte';

	interface IVRNode {
		id?: number;
		flow_id?: number;
		node_type: string;
		name: string;
		prompt_text: string | null;
		audio_url: string | null;
		timeout_seconds: number;
		max_retries: number;
		next_node_id: number | null;
		menu_options: MenuOption[];
		transfer_destination: string | null;
		variable_name: string | null;
		condition_expression: string | null;
		webhook_url: string | null;
	}

	interface MenuOption {
		id?: number;
		key: string;
		action: string;
		next_node_id: number | null;
		transfer_destination: string | null;
	}

	interface IVRFlow {
		id?: number;
		name: string;
		description: string;
		team_id: number;
		is_active: boolean;
		timeout_seconds: number;
		max_retries: number;
		entry_node_id: number | null;
	}

	let flowId: number | null = null;
	let flow: IVRFlow = {
		name: '',
		description: '',
		team_id: 1,
		is_active: true,
		timeout_seconds: 30,
		max_retries: 3,
		entry_node_id: null
	};

	let nodes: IVRNode[] = [];
	let selectedNode: IVRNode | null = null;
	let showNodeEditor = false;
	let loading = false;
	let saving = false;

	const nodeTypes = [
		{ value: 'menu', label: 'Menu', description: 'Present options to caller' },
		{ value: 'play', label: 'Play Message', description: 'Play audio message' },
		{ value: 'gather', label: 'Gather Input', description: 'Collect DTMF/speech input' },
		{ value: 'transfer', label: 'Transfer', description: 'Transfer to phone/agent' },
		{ value: 'voicemail', label: 'Voicemail', description: 'Send to voicemail' },
		{ value: 'webhook', label: 'Webhook', description: 'Call external API' },
		{ value: 'conditional', label: 'Conditional', description: 'Branch based on condition' },
		{ value: 'variable', label: 'Set Variable', description: 'Store value in variable' },
		{ value: 'end', label: 'End Call', description: 'Terminate the call' }
	];

	onMount(async () => {
		const urlParams = new URLSearchParams(window.location.search);
		const id = urlParams.get('id');
		if (id) {
			flowId = parseInt(id);
			await loadFlow();
		}
	});

	async function loadFlow() {
		if (!flowId) return;
		loading = true;
		try {
			const response = await fetch(`http://localhost:8000/api/ivr/flows/${flowId}`);
			if (!response.ok) throw new Error('Failed to load flow');
			const data = await response.json();
			flow = data;

			// Load nodes for this flow
			const nodesResponse = await fetch(`http://localhost:8000/api/ivr/flows/${flowId}/nodes`);
			if (nodesResponse.ok) {
				nodes = await nodesResponse.json();
			}
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to load flow');
		} finally {
			loading = false;
		}
	}

	async function saveFlow() {
		if (!flow.name.trim()) {
			alert('Please enter a flow name');
			return;
		}

		saving = true;
		try {
			const method = flowId ? 'PUT' : 'POST';
			const url = flowId
				? `http://localhost:8000/api/ivr/flows/${flowId}`
				: 'http://localhost:8000/api/ivr/flows';

			const response = await fetch(url, {
				method,
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(flow)
			});

			if (!response.ok) throw new Error('Failed to save flow');
			const savedFlow = await response.json();

			if (!flowId) {
				flowId = savedFlow.id;
				flow.id = savedFlow.id;
			}

			// Save all nodes
			for (const node of nodes) {
				await saveNode(node);
			}

			alert('Flow saved successfully!');
			goto('/operations/ivr');
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save flow');
		} finally {
			saving = false;
		}
	}

	async function saveNode(node: IVRNode) {
		if (!flowId) return;

		const method = node.id ? 'PUT' : 'POST';
		const url = node.id
			? `http://localhost:8000/api/ivr/nodes/${node.id}`
			: 'http://localhost:8000/api/ivr/nodes';

		const response = await fetch(url, {
			method,
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				...node,
				flow_id: flowId
			})
		});

		if (!response.ok) throw new Error('Failed to save node');
		const savedNode = await response.json();
		if (!node.id) {
			node.id = savedNode.id;
		}
	}

	function addNode() {
		const newNode: IVRNode = {
			flow_id: flowId || undefined,
			node_type: 'menu',
			name: `Node ${nodes.length + 1}`,
			prompt_text: '',
			audio_url: null,
			timeout_seconds: 30,
			max_retries: 3,
			next_node_id: null,
			menu_options: [],
			transfer_destination: null,
			variable_name: null,
			condition_expression: null,
			webhook_url: null
		};
		nodes = [...nodes, newNode];
		selectedNode = newNode;
		showNodeEditor = true;
	}

	function editNode(node: IVRNode) {
		selectedNode = node;
		showNodeEditor = true;
	}

	function deleteNode(index: number) {
		if (confirm('Are you sure you want to delete this node?')) {
			nodes = nodes.filter((_, i) => i !== index);
			if (selectedNode === nodes[index]) {
				selectedNode = null;
				showNodeEditor = false;
			}
		}
	}

	function addMenuOption() {
		if (!selectedNode) return;
		if (!selectedNode.menu_options) {
			selectedNode.menu_options = [];
		}
		selectedNode.menu_options = [
			...selectedNode.menu_options,
			{
				key: '',
				action: 'navigate',
				next_node_id: null,
				transfer_destination: null
			}
		];
	}

	function removeMenuOption(index: number) {
		if (!selectedNode) return;
		selectedNode.menu_options = selectedNode.menu_options.filter((_, i) => i !== index);
	}

	function getNodeTypeLabel(type: string): string {
		return nodeTypes.find((t) => t.value === type)?.label || type;
	}

	function getNodeColor(type: string): string {
		const colors: Record<string, string> = {
			menu: 'bg-blue-100 border-blue-300 text-blue-800',
			play: 'bg-green-100 border-green-300 text-green-800',
			gather: 'bg-purple-100 border-purple-300 text-purple-800',
			transfer: 'bg-orange-100 border-orange-300 text-orange-800',
			voicemail: 'bg-yellow-100 border-yellow-300 text-yellow-800',
			webhook: 'bg-pink-100 border-pink-300 text-pink-800',
			conditional: 'bg-indigo-100 border-indigo-300 text-indigo-800',
			variable: 'bg-teal-100 border-teal-300 text-teal-800',
			end: 'bg-red-100 border-red-300 text-red-800'
		};
		return colors[type] || 'bg-gray-100 border-gray-300 text-gray-800';
	}
</script>

<div class="p-6 max-w-7xl mx-auto">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<a
				href="/operations/ivr"
				class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<ArrowLeft class="w-5 h-5" />
			</a>
			<div>
				<h1 class="text-3xl font-bold text-gray-900">
					{flowId ? 'Edit IVR Flow' : 'Create IVR Flow'}
				</h1>
				<p class="text-gray-600">Design your interactive voice response flow</p>
			</div>
		</div>
		<button
			onclick={saveFlow}
			disabled={saving}
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
		>
			<Save class="w-4 h-4" />
			{saving ? 'Saving...' : 'Save Flow'}
		</button>
	</div>

	{#if loading}
		<div class="p-8 text-center">
			<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
			<p class="mt-2 text-gray-600">Loading flow...</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Flow Configuration -->
			<div class="lg:col-span-2 space-y-6">
				<!-- Basic Info -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-xl font-semibold text-gray-900 mb-4">Flow Configuration</h2>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Flow Name *
							</label>
							<input
								type="text"
								bind:value={flow.name}
								placeholder="e.g., Main Menu"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Description
							</label>
							<textarea
								bind:value={flow.description}
								placeholder="Describe the purpose of this IVR flow..."
								rows="3"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Timeout (seconds)
							</label>
							<input
								type="number"
								bind:value={flow.timeout_seconds}
								min="5"
								max="300"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								Max Retries
							</label>
							<input
								type="number"
								bind:value={flow.max_retries}
								min="1"
								max="10"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							/>
						</div>
						<div class="flex items-center">
							<input
								type="checkbox"
								id="is_active"
								bind:checked={flow.is_active}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<label for="is_active" class="ml-2 text-sm text-gray-700">
								Active (enable this flow)
							</label>
						</div>
					</div>
				</div>

				<!-- Nodes List -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<div class="flex items-center justify-between mb-4">
						<h2 class="text-xl font-semibold text-gray-900">Flow Nodes</h2>
						<button
							onclick={addNode}
							class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
						>
							<Plus class="w-4 h-4" />
							Add Node
						</button>
					</div>

					{#if nodes.length === 0}
						<div class="text-center py-8">
							<MenuIcon class="w-12 h-12 text-gray-300 mx-auto mb-2" />
							<p class="text-gray-600">No nodes yet. Click "Add Node" to start building your flow.</p>
						</div>
					{:else}
						<div class="space-y-3">
							{#each nodes as node, index}
								<div class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
									<div class="flex items-center justify-between">
										<div class="flex items-center gap-3 flex-1">
											<span class="px-3 py-1 rounded-full border text-xs font-medium {getNodeColor(node.node_type)}">
												{getNodeTypeLabel(node.node_type)}
											</span>
											<div class="flex-1">
												<div class="font-medium text-gray-900">{node.name}</div>
												<div class="text-sm text-gray-500">
													{node.prompt_text ? node.prompt_text.substring(0, 60) + '...' : 'No prompt text'}
												</div>
											</div>
										</div>
										<div class="flex items-center gap-2">
											<button
												onclick={() => editNode(node)}
												class="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
												title="Edit"
											>
												<Edit2 class="w-4 h-4" />
											</button>
											<button
												onclick={() => deleteNode(index)}
												class="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
												title="Delete"
											>
												<Trash2 class="w-4 h-4" />
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
			<div class="lg:col-span-1">
				{#if showNodeEditor && selectedNode}
					<div class="bg-white rounded-lg border border-gray-200 p-6 sticky top-6">
						<h2 class="text-xl font-semibold text-gray-900 mb-4">Edit Node</h2>

						<div class="space-y-4">
							<div>
								<label class="block text-sm font-medium text-gray-700 mb-1">
									Node Type
								</label>
								<select
									bind:value={selectedNode.node_type}
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								>
									{#each nodeTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-700 mb-1">
									Node Name
								</label>
								<input
									type="text"
									bind:value={selectedNode.name}
									placeholder="e.g., Welcome Message"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								/>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-700 mb-1">
									Prompt Text
								</label>
								<textarea
									bind:value={selectedNode.prompt_text}
									placeholder="What to say to the caller..."
									rows="4"
									class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								/>
							</div>

							{#if selectedNode.node_type === 'menu'}
								<div>
									<div class="flex items-center justify-between mb-2">
										<label class="block text-sm font-medium text-gray-700">
											Menu Options
										</label>
										<button
											onclick={addMenuOption}
											class="text-sm text-blue-600 hover:text-blue-700"
										>
											+ Add Option
										</button>
									</div>
									<div class="space-y-2">
										{#each selectedNode.menu_options || [] as option, idx}
											<div class="flex gap-2 items-start">
												<input
													type="text"
													bind:value={option.key}
													placeholder="Key (0-9,*,#)"
													maxlength="1"
													class="w-20 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
												/>
												<select
													bind:value={option.action}
													class="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
												>
													<option value="navigate">Navigate</option>
													<option value="transfer">Transfer</option>
													<option value="voicemail">Voicemail</option>
													<option value="end">End Call</option>
												</select>
												<button
													onclick={() => removeMenuOption(idx)}
													class="p-1 text-red-600 hover:bg-red-50 rounded"
												>
													<Trash2 class="w-4 h-4" />
												</button>
											</div>
										{/each}
									</div>
								</div>
							{/if}

							{#if selectedNode.node_type === 'transfer'}
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-1">
										Transfer Destination
									</label>
									<input
										type="text"
										bind:value={selectedNode.transfer_destination}
										placeholder="+1234567890 or agent_id"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									/>
								</div>
							{/if}

							{#if selectedNode.node_type === 'webhook'}
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-1">
										Webhook URL
									</label>
									<input
										type="url"
										bind:value={selectedNode.webhook_url}
										placeholder="https://api.example.com/webhook"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									/>
								</div>
							{/if}

							<div class="grid grid-cols-2 gap-2">
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-1">
										Timeout (s)
									</label>
									<input
										type="number"
										bind:value={selectedNode.timeout_seconds}
										min="5"
										max="300"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									/>
								</div>
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-1">
										Max Retries
									</label>
									<input
										type="number"
										bind:value={selectedNode.max_retries}
										min="1"
										max="10"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
									/>
								</div>
							</div>
						</div>
					</div>
				{:else}
					<div class="bg-gray-50 rounded-lg border border-gray-200 p-6 text-center">
						<Phone class="w-12 h-12 text-gray-300 mx-auto mb-2" />
						<p class="text-gray-600">Select a node to edit its properties</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
