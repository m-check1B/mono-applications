<script lang="ts">
	import { onMount } from 'svelte';

	interface VM {
		id: string;
		hostname: string;
		ip_address: string;
		customer_id: string;
		tier: string;
		status: string;
		cpu_cores: number;
		memory_gb: number;
		disk_gb: number;
		version: string;
		last_heartbeat?: string;
	}

	interface Customer {
		id: string;
		name: string;
		email: string;
		company?: string;
		tier: string;
		billing_status: string;
		monthly_fee: number;
	}

	interface Alert {
		id: string;
		vm_id?: string;
		customer_id?: string;
		type: string;
		severity: string;
		message: string;
		created_at: string;
		resolved: boolean;
	}

	interface FleetMetrics {
		total_vms: number;
		total_customers: number;
		online_vms: number;
		offline_vms: number;
		monthly_revenue: number;
		monthly_cost: number;
		avg_cpu: number;
		avg_memory: number;
		alerts_count: number;
	}

	const API_BASE = window.location.port === '5173'
		? 'http://localhost:8686'
		: '/api';

	let vms: VM[] = [];
	let customers: Customer[] = [];
	let alerts: Alert[] = [];
	let metrics: FleetMetrics | null = null;
	let selectedView = 'overview';
	let selectedVM: VM | null = null;
	let selectedCustomer: Customer | null = null;
	let loading = true;
	let error: string | null = null;

	onMount(() => {
		loadData();
		setInterval(loadData, 30000);
	});

	async function loadData() {
		try {
			loading = true;
			error = null;

			const [vmsData, customersData, alertsData, metricsData] = await Promise.all([
				fetch(`${API_BASE}/vms`).then((r) => r.json()),
				fetch(`${API_BASE}/customers`).then((r) => r.json()),
				fetch(`${API_BASE}/alerts?resolved=false`).then((r) => r.json()),
				fetch(`${API_BASE}/metrics/fleet`).then((r) => r.json())
			]);

			vms = vmsData;
			customers = customersData;
			alerts = alertsData;
			metrics = metricsData;
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function resolveAlert(alertId: string) {
		try {
			await fetch(`${API_BASE}/alerts/${alertId}/resolve`, { method: 'PUT' });
			alerts = alerts.filter((a) => a.id !== alertId);
			loadData();
		} catch (e: any) {
			alert('Failed to resolve alert: ' + e.message);
		}
	}

	async function restartVM(vmId: string) {
		if (!confirm('Are you sure you want to restart this VM?')) return;

		try {
			await fetch(`${API_BASE}/vms/${vmId}/restart`, { method: 'POST' });
			alert('Restart command sent');
		} catch (e: any) {
			alert('Failed to restart VM: ' + e.message);
		}
	}

	async function rebuildVM(vmId: string) {
		if (!confirm('Are you sure you want to rebuild this VM? This will reinstall all software.')) return;

		try {
			await fetch(`${API_BASE}/vms/${vmId}/rebuild`, { method: 'POST' });
			alert('Rebuild command sent');
		} catch (e: any) {
			alert('Failed to rebuild VM: ' + e.message);
		}
	}

	function getCustomerName(customerId: string): string {
		const customer = customers.find((c) => c.id === customerId);
		return customer ? customer.name : 'Unknown';
	}

	function getVMForAlert(alert: Alert): VM | null {
		if (!alert.vm_id) return null;
		return vms.find((v) => v.id === alert.vm_id) || null;
	}

	function getStatusBadgeClass(status: string): string {
		switch (status.toLowerCase()) {
			case 'online':
				return 'bg-green-100 text-green-800';
			case 'offline':
				return 'bg-red-100 text-red-800';
			case 'maintenance':
				return 'bg-yellow-100 text-yellow-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}

	function getSeverityBadgeClass(severity: string): string {
		switch (severity.toLowerCase()) {
			case 'high':
				return 'bg-red-100 text-red-800';
			case 'warning':
				return 'bg-yellow-100 text-yellow-800';
			case 'info':
				return 'bg-blue-100 text-blue-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 py-8">
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900">📦 Lab by Kraliki Fleet Management</h1>
			<p class="text-gray-600 mt-2">Monitor and manage your Lab by Kraliki VM fleet</p>
		</div>

		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<p class="text-red-800">{error}</p>
			</div>
		{/if}

		{#if loading && !metrics}
			<div class="text-center py-12">
				<p class="text-gray-600">Loading...</p>
			</div>
		{/if}

		{#if metrics}
			<div class="mb-8">
				<div class="flex space-x-4 mb-6">
					<button
						class="px-4 py-2 rounded-lg {selectedView === 'overview'
							? 'bg-indigo-600 text-white'
							: 'bg-white text-gray-700 hover:bg-gray-50'}"
						on:click={() => (selectedView = 'overview')}
					>
						Overview
					</button>
					<button
						class="px-4 py-2 rounded-lg {selectedView === 'vms'
							? 'bg-indigo-600 text-white'
							: 'bg-white text-gray-700 hover:bg-gray-50'}"
						on:click={() => (selectedView = 'vms')}
					>
						VMs
					</button>
					<button
						class="px-4 py-2 rounded-lg {selectedView === 'customers'
							? 'bg-indigo-600 text-white'
							: 'bg-white text-gray-700 hover:bg-gray-50'}"
						on:click={() => (selectedView = 'customers')}
					>
						Customers
					</button>
					<button
						class="px-4 py-2 rounded-lg {selectedView === 'alerts'
							? 'bg-indigo-600 text-white'
							: 'bg-white text-gray-700 hover:bg-gray-50'}"
						on:click={() => (selectedView = 'alerts')}
					>
						Alerts {alerts.length > 0 && `(${alerts.length})`}
					</button>
					<button class="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300" on:click={loadData}>
						Refresh
					</button>
				</div>

				{#if selectedView === 'overview'}
					<div>
						<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-sm font-medium text-gray-500 mb-2">Total VMs</h3>
								<p class="text-3xl font-bold text-gray-900">{metrics.total_vms}</p>
								<p class="text-sm text-gray-600 mt-1">
									{metrics.online_vms} online, {metrics.offline_vms} offline
								</p>
							</div>
							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-sm font-medium text-gray-500 mb-2">Total Customers</h3>
								<p class="text-3xl font-bold text-gray-900">{metrics.total_customers}</p>
							</div>
							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-sm font-medium text-gray-500 mb-2">Monthly Revenue</h3>
								<p class="text-3xl font-bold text-green-600">€{metrics.monthly_revenue.toFixed(2)}</p>
								<p class="text-sm text-gray-600 mt-1">Cost: €{metrics.monthly_cost.toFixed(2)}</p>
							</div>
							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-sm font-medium text-gray-500 mb-2">Active Alerts</h3>
								<p class="text-3xl font-bold {metrics.alerts_count > 0
									? 'text-red-600'
									: 'text-green-600'}">{metrics.alerts_count}
								</p>
							</div>
						</div>

						<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-lg font-semibold text-gray-900 mb-4">Resource Usage</h3>
								<div class="space-y-4">
									<div>
										<div class="flex justify-between mb-1">
											<span class="text-sm text-gray-600">Average CPU</span>
											<span class="text-sm font-medium">{metrics.avg_cpu.toFixed(1)}%</span>
										</div>
										<div class="w-full bg-gray-200 rounded-full h-2">
											<div
												class="bg-blue-600 h-2 rounded-full"
												style="width: {metrics.avg_cpu}%"
											></div>
										</div>
									</div>
									<div>
										<div class="flex justify-between mb-1">
											<span class="text-sm text-gray-600">Average Memory</span>
											<span class="text-sm font-medium">{metrics.avg_memory.toFixed(1)}%</span>
										</div>
										<div class="w-full bg-gray-200 rounded-full h-2">
											<div
												class="bg-green-600 h-2 rounded-full"
												style="width: {metrics.avg_memory}%"
											></div>
										</div>
									</div>
								</div>
							</div>

							<div class="bg-white rounded-lg shadow p-6">
								<h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h3>
								{#if alerts.length === 0}
									<p class="text-gray-600">No active alerts</p>
								{:else}
									<div class="space-y-2">
										{#each alerts.slice(0, 5) as alert}
											<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
												<div class="flex items-center space-x-3">
													<span class="px-2 py-1 text-xs font-medium rounded {getSeverityBadgeClass(
														alert.severity)}">{alert.severity}</span>
													<p class="text-sm text-gray-900">{alert.message}</p>
												</div>
												<button
													class="text-blue-600 hover:text-blue-800 text-sm"
													on:click={() => resolveAlert(alert.id)}>Resolve</button>
												</div>
										{/each}
									</div>
								{/if}
							</div>
						</div>
					</div>
				{/if}

				{#if selectedView === 'vms'}
					<div class="bg-white rounded-lg shadow overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
									>Hostname</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tier</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Specs</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								{#each vms as vm}
									<tr class="hover:bg-gray-50">
										<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{vm.hostname}</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{vm.ip_address}</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
											{getCustomerName(vm.customer_id)}
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
											<span class="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">{vm.tier}</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap">
											<span class="px-2 py-1 text-xs font-medium rounded {getStatusBadgeClass(
												vm.status)}">{vm.status}</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
											{vm.cpu_cores}C / {vm.memory_gb}GB / {vm.disk_gb}GB
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
											<button
												class="text-blue-600 hover:text-blue-800"
												on:click={() => (selectedVM = vm)}>Details</button>
											<button
												class="text-yellow-600 hover:text-yellow-800"
												on:click={() => restartVM(vm.id)}>Restart</button>
											<button
												class="text-red-600 hover:text-red-800"
												on:click={() => rebuildVM(vm.id)}>Rebuild</button>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}

				{#if selectedView === 'customers'}
					<div class="bg-white rounded-lg shadow overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tier</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Billing</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Monthly Fee</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								{#each customers as customer}
									<tr class="hover:bg-gray-50">
										<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
											{customer.name}
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.email}</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{customer.company ||
											'-'}</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
											<span class="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">{customer.tier}</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap">
											<span class="px-2 py-1 text-xs font-medium rounded {customer.billing_status === 'active'
												? 'bg-green-100 text-green-800'
												: 'bg-red-100 text-red-800'}">{customer.billing_status}</span>
										</td>
										<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
											€{customer.monthly_fee.toFixed(2)}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}

				{#if selectedView === 'alerts'}
					<div class="bg-white rounded-lg shadow overflow-hidden">
						<table class="min-w-full divide-y divide-gray-200">
							<thead class="bg-gray-50">
								<tr>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">VM</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
									<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
								</tr>
							</thead>
							<tbody class="bg-white divide-y divide-gray-200">
								{#if alerts.length === 0}
									<tr>
										<td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">
											No active alerts
										</td>
									</tr>
								{:else}
									{#each alerts as alert}
										<tr class="hover:bg-gray-50">
											<td class="px-6 py-4 whitespace-nowrap">
												<span class="px-2 py-1 text-xs font-medium rounded {getSeverityBadgeClass(
													alert.severity)}">{alert.severity}</span>
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{alert.type}</td>
											<td class="px-6 py-4 text-sm text-gray-900">{alert.message}</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
												{#if alert.vm_id}
													{getVMForAlert(alert)?.hostname || alert.vm_id}
												{:else}
													-
												{/if}
											</td>
											<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(
												alert.created_at).toLocaleString()}</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<button
													class="text-blue-600 hover:text-blue-800 text-sm"
													on:click={() => resolveAlert(alert.id)}>Resolve</button>
											</td>
										</tr>
									{/each}
								{/if}
							</tbody>
						</table>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	/* Add any custom styles here if needed */
</style>
