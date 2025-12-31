<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Plus, Save, ArrowLeft, Trash2, X } from 'lucide-svelte';

	interface RoutingCondition {
		id?: number;
		field: string;
		operator: string;
		value: string;
		logic_operator: 'AND' | 'OR';
	}

	interface RoutingTarget {
		id?: number;
		target_type: string;
		target_id: number | null;
		weight: number;
		max_capacity: number | null;
	}

	interface RoutingRule {
		id?: number;
		name: string;
		description: string;
		team_id: number;
		priority: number;
		strategy: string;
		is_active: boolean;
		conditions: RoutingCondition[];
		targets: RoutingTarget[];
		fallback_action: string;
		business_hours_only: boolean;
	}

	let ruleId: number | null = null;
	let rule: RoutingRule = {
		name: '',
		description: '',
		team_id: 1,
		priority: 100,
		strategy: 'skill_based',
		is_active: true,
		conditions: [],
		targets: [],
		fallback_action: 'voicemail',
		business_hours_only: false
	};

	let loading = false;
	let saving = false;

	const strategies = [
		{ value: 'skill_based', label: 'Skill-Based', description: 'Route based on agent skills' },
		{ value: 'least_busy', label: 'Least Busy', description: 'Route to agent with fewest calls' },
		{
			value: 'longest_idle',
			label: 'Longest Idle',
			description: 'Route to agent idle longest'
		},
		{ value: 'round_robin', label: 'Round Robin', description: 'Distribute calls evenly' },
		{ value: 'priority', label: 'Priority', description: 'Route by priority level' },
		{ value: 'language', label: 'Language', description: 'Match caller language' },
		{ value: 'vip', label: 'VIP', description: 'Prioritize VIP callers' },
		{ value: 'custom', label: 'Custom', description: 'Custom routing logic' }
	];

	const conditionFields = [
		{ value: 'caller_phone', label: 'Caller Phone' },
		{ value: 'caller_country', label: 'Caller Country' },
		{ value: 'time_of_day', label: 'Time of Day' },
		{ value: 'day_of_week', label: 'Day of Week' },
		{ value: 'queue_wait_time', label: 'Queue Wait Time' },
		{ value: 'required_skills', label: 'Required Skills' },
		{ value: 'language', label: 'Language' },
		{ value: 'campaign_id', label: 'Campaign' },
		{ value: 'custom_field', label: 'Custom Field' }
	];

	const operators = [
		{ value: 'equals', label: 'Equals' },
		{ value: 'not_equals', label: 'Not Equals' },
		{ value: 'contains', label: 'Contains' },
		{ value: 'starts_with', label: 'Starts With' },
		{ value: 'greater_than', label: 'Greater Than' },
		{ value: 'less_than', label: 'Less Than' },
		{ value: 'in_list', label: 'In List' }
	];

	const targetTypes = [
		{ value: 'agent', label: 'Agent' },
		{ value: 'team', label: 'Team' },
		{ value: 'queue', label: 'Queue' },
		{ value: 'phone', label: 'Phone Number' },
		{ value: 'ivr', label: 'IVR Flow' }
	];

	const fallbackActions = [
		{ value: 'voicemail', label: 'Send to Voicemail' },
		{ value: 'queue', label: 'Add to Queue' },
		{ value: 'transfer', label: 'Transfer to Number' },
		{ value: 'hangup', label: 'Hangup' },
		{ value: 'callback', label: 'Offer Callback' }
	];

	onMount(async () => {
		const urlParams = new URLSearchParams(window.location.search);
		const id = urlParams.get('id');
		if (id) {
			ruleId = parseInt(id);
			await loadRule();
		}
	});

	async function loadRule() {
		if (!ruleId) return;
		loading = true;
		try {
			const response = await fetch(`http://localhost:8000/api/routing/rules/${ruleId}`);
			if (!response.ok) throw new Error('Failed to load rule');
			rule = await response.json();
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to load rule');
		} finally {
			loading = false;
		}
	}

	async function saveRule() {
		if (!rule.name.trim()) {
			alert('Please enter a rule name');
			return;
		}

		if (rule.targets.length === 0) {
			alert('Please add at least one routing target');
			return;
		}

		saving = true;
		try {
			const method = ruleId ? 'PUT' : 'POST';
			const url = ruleId
				? `http://localhost:8000/api/routing/rules/${ruleId}`
				: 'http://localhost:8000/api/routing/rules';

			const response = await fetch(url, {
				method,
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(rule)
			});

			if (!response.ok) throw new Error('Failed to save rule');

			alert('Rule saved successfully!');
			goto('/operations/routing');
		} catch (err) {
			alert(err instanceof Error ? err.message : 'Failed to save rule');
		} finally {
			saving = false;
		}
	}

	function addCondition() {
		rule.conditions = [
			...rule.conditions,
			{
				field: 'caller_phone',
				operator: 'equals',
				value: '',
				logic_operator: 'AND'
			}
		];
	}

	function removeCondition(index: number) {
		rule.conditions = rule.conditions.filter((_, i) => i !== index);
	}

	function addTarget() {
		rule.targets = [
			...rule.targets,
			{
				target_type: 'agent',
				target_id: null,
				weight: 100,
				max_capacity: null
			}
		];
	}

	function removeTarget(index: number) {
		rule.targets = rule.targets.filter((_, i) => i !== index);
	}
</script>

<div class="p-6 max-w-5xl mx-auto">
	<!-- Header -->
	<div class="mb-6 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<a href="/operations/routing" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
				<ArrowLeft class="w-5 h-5" />
			</a>
			<div>
				<h1 class="text-3xl font-bold text-gray-900">
					{ruleId ? 'Edit Routing Rule' : 'Create Routing Rule'}
				</h1>
				<p class="text-gray-600">Configure intelligent call routing</p>
			</div>
		</div>
		<button
			onclick={saveRule}
			disabled={saving}
			class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
		>
			<Save class="w-4 h-4" />
			{saving ? 'Saving...' : 'Save Rule'}
		</button>
	</div>

	{#if loading}
		<div class="p-8 text-center">
			<div
				class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"
			></div>
			<p class="mt-2 text-gray-600">Loading rule...</p>
		</div>
	{:else}
		<div class="space-y-6">
			<!-- Basic Configuration -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<h2 class="text-xl font-semibold text-gray-900 mb-4">Basic Configuration</h2>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="md:col-span-2">
						<label class="block text-sm font-medium text-gray-700 mb-1"> Rule Name * </label>
						<input
							type="text"
							bind:value={rule.name}
							placeholder="e.g., VIP Customer Routing"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div class="md:col-span-2">
						<label class="block text-sm font-medium text-gray-700 mb-1"> Description </label>
						<textarea
							bind:value={rule.description}
							placeholder="Describe the purpose of this routing rule..."
							rows="3"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Routing Strategy *
						</label>
						<select
							bind:value={rule.strategy}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each strategies as strategy}
								<option value={strategy.value}>{strategy.label}</option>
							{/each}
						</select>
						<p class="mt-1 text-sm text-gray-500">
							{strategies.find((s) => s.value === rule.strategy)?.description || ''}
						</p>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Priority (Lower = Higher Priority)
						</label>
						<input
							type="number"
							bind:value={rule.priority}
							min="1"
							max="1000"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">
							Fallback Action
						</label>
						<select
							bind:value={rule.fallback_action}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each fallbackActions as action}
								<option value={action.value}>{action.label}</option>
							{/each}
						</select>
					</div>
					<div class="flex items-center gap-4">
						<div class="flex items-center">
							<input
								type="checkbox"
								id="is_active"
								bind:checked={rule.is_active}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<label for="is_active" class="ml-2 text-sm text-gray-700"> Active </label>
						</div>
						<div class="flex items-center">
							<input
								type="checkbox"
								id="business_hours"
								bind:checked={rule.business_hours_only}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<label for="business_hours" class="ml-2 text-sm text-gray-700">
								Business Hours Only
							</label>
						</div>
					</div>
				</div>
			</div>

			<!-- Conditions -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-xl font-semibold text-gray-900">Routing Conditions</h2>
					<button
						onclick={addCondition}
						class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
					>
						<Plus class="w-4 h-4" />
						Add Condition
					</button>
				</div>

				{#if rule.conditions.length === 0}
					<p class="text-gray-500 text-center py-4">
						No conditions added. Rule will apply to all calls.
					</p>
				{:else}
					<div class="space-y-3">
						{#each rule.conditions as condition, index}
							<div class="border border-gray-200 rounded-lg p-4">
								<div class="grid grid-cols-1 md:grid-cols-4 gap-3">
									{#if index > 0}
										<div class="md:col-span-4">
											<select
												bind:value={condition.logic_operator}
												class="px-3 py-1 border border-gray-300 rounded text-sm"
											>
												<option value="AND">AND</option>
												<option value="OR">OR</option>
											</select>
										</div>
									{/if}
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">Field</label>
										<select
											bind:value={condition.field}
											class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
										>
											{#each conditionFields as field}
												<option value={field.value}>{field.label}</option>
											{/each}
										</select>
									</div>
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">Operator</label>
										<select
											bind:value={condition.operator}
											class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
										>
											{#each operators as op}
												<option value={op.value}>{op.label}</option>
											{/each}
										</select>
									</div>
									<div class="md:col-span-2 flex gap-2">
										<div class="flex-1">
											<label class="block text-xs font-medium text-gray-600 mb-1">Value</label>
											<input
												type="text"
												bind:value={condition.value}
												placeholder="Enter value..."
												class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
											/>
										</div>
										<button
											onclick={() => removeCondition(index)}
											class="self-end p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
											title="Remove Condition"
										>
											<X class="w-4 h-4" />
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Targets -->
			<div class="bg-white rounded-lg border border-gray-200 p-6">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-xl font-semibold text-gray-900">Routing Targets *</h2>
					<button
						onclick={addTarget}
						class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
					>
						<Plus class="w-4 h-4" />
						Add Target
					</button>
				</div>

				{#if rule.targets.length === 0}
					<p class="text-gray-500 text-center py-4">
						No targets added. Please add at least one routing target.
					</p>
				{:else}
					<div class="space-y-3">
						{#each rule.targets as target, index}
							<div class="border border-gray-200 rounded-lg p-4">
								<div class="grid grid-cols-1 md:grid-cols-4 gap-3">
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">
											Target Type
										</label>
										<select
											bind:value={target.target_type}
											class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
										>
											{#each targetTypes as type}
												<option value={type.value}>{type.label}</option>
											{/each}
										</select>
									</div>
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">
											Target ID
										</label>
										<input
											type="number"
											bind:value={target.target_id}
											placeholder="ID or leave blank"
											class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
										/>
									</div>
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">
											Weight
										</label>
										<input
											type="number"
											bind:value={target.weight}
											min="1"
											max="1000"
											class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
										/>
									</div>
									<div class="flex gap-2">
										<div class="flex-1">
											<label class="block text-xs font-medium text-gray-600 mb-1">
												Max Capacity
											</label>
											<input
												type="number"
												bind:value={target.max_capacity}
												placeholder="Optional"
												min="1"
												class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
											/>
										</div>
										<button
											onclick={() => removeTarget(index)}
											class="self-end p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
											title="Remove Target"
										>
											<X class="w-4 h-4" />
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
