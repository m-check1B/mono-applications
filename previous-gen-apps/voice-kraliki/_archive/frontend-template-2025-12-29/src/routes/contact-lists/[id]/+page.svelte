<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface ContactList {
		id: number;
		campaign_id: number;
		name: string;
		description: string;
		total_contacts: number;
		processed_contacts: number;
		successful_contacts: number;
		failed_contacts: number;
		import_status: string;
		created_at: string;
	}

	interface Contact {
		id: number;
		phone_number: string;
		first_name: string;
		last_name: string;
		email: string;
		company: string;
		status: string;
		attempts: number;
		last_attempt_at: string | null;
		disposition: string | null;
		created_at: string;
	}

	$: listId = parseInt($page.params.id ?? "0");

	let contactList: ContactList | null = null;
	let contacts: Contact[] = [];
	let loading = true;
	let error = '';
	let currentPage = 0;
	let pageSize = 50;
	let statusFilter = 'all';

	const statusColors: Record<string, string> = {
		pending: 'bg-gray-200 text-gray-800',
		calling: 'bg-blue-200 text-blue-800',
		completed: 'bg-green-200 text-green-800',
		failed: 'bg-red-200 text-red-800',
		skipped: 'bg-yellow-200 text-yellow-800'
	};

	onMount(async () => {
		await loadContactList();
		await loadContacts();
	});

	async function loadContactList() {
		try {
			const token = localStorage.getItem('token');
			const response = await fetch(`/api/campaign-management/contact-lists/${listId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (response.ok) {
				contactList = await response.json();
			} else {
				error = 'Contact list not found';
			}
		} catch (err) {
			error = `Error loading contact list: ${err}`;
		}
	}

	async function loadContacts() {
		try {
			loading = true;
			const token = localStorage.getItem('token');
			const statusParam = statusFilter !== 'all' ? `&status=${statusFilter}` : '';
			const response = await fetch(
				`/api/campaign-management/contact-lists/${listId}/contacts?skip=${currentPage * pageSize}&limit=${pageSize}${statusParam}`,
				{
					headers: { Authorization: `Bearer ${token}` }
				}
			);

			if (response.ok) {
				contacts = await response.json();
			}
		} catch (err) {
			console.error('Error loading contacts:', err);
		} finally {
			loading = false;
		}
	}

	async function handleStatusFilter(status: string) {
		statusFilter = status;
		currentPage = 0;
		await loadContacts();
	}

	function formatDate(dateString: string | null) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleString();
	}

	function getProgress() {
		if (!contactList) return 0;
		return contactList.total_contacts > 0
			? (contactList.processed_contacts / contactList.total_contacts) * 100
			: 0;
	}
</script>

<div class="container mx-auto p-6">
	{#if error}
		<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
			{error}
		</div>
	{:else if contactList}
		<!-- Header -->
		<div class="mb-6">
			<button
				onclick={() => goto(`/campaigns/${contactList.campaign_id}`)}
				class="text-gray-600 hover:text-gray-900 mb-2"
			>
				← Back to Campaign
			</button>
			<h1 class="text-3xl font-bold">{contactList.name}</h1>
			<p class="text-gray-600 mt-1">
				{contactList.description || 'No description provided'}
			</p>
		</div>

		<!-- Statistics Cards -->
		<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Total Contacts</div>
				<div class="text-3xl font-bold">{contactList.total_contacts}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Processed</div>
				<div class="text-3xl font-bold">{contactList.processed_contacts}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Successful</div>
				<div class="text-3xl font-bold text-green-600">{contactList.successful_contacts}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-1">Failed</div>
				<div class="text-3xl font-bold text-red-600">{contactList.failed_contacts}</div>
			</div>
		</div>

		<!-- Progress Bar -->
		<div class="bg-white p-4 rounded-lg shadow mb-6">
			<div class="flex justify-between text-sm text-gray-600 mb-2">
				<span>Progress</span>
				<span>{getProgress().toFixed(1)}%</span>
			</div>
			<div class="w-full bg-gray-200 rounded-full h-2">
				<div
					class="bg-blue-600 h-2 rounded-full transition-all duration-300"
					style="width: {getProgress()}%"
				></div>
			</div>
		</div>

		<!-- Filters -->
		<div class="mb-4 flex gap-2">
			<button
				onclick={() => handleStatusFilter('all')}
				class="px-4 py-2 rounded {statusFilter === 'all'
					? 'bg-blue-600 text-white'
					: 'bg-gray-200 text-gray-700'}"
			>
				All
			</button>
			{#each ['pending', 'calling', 'completed', 'failed', 'skipped'] as status}
				<button
					onclick={() => handleStatusFilter(status)}
					class="px-4 py-2 rounded capitalize {statusFilter === status
						? 'bg-blue-600 text-white'
						: 'bg-gray-200 text-gray-700'}"
				>
					{status}
				</button>
			{/each}
		</div>

		<!-- Contacts Table -->
		{#if loading}
			<div class="text-center py-12">
				<div
					class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
				></div>
				<p class="mt-4 text-gray-600">Loading contacts...</p>
			</div>
		{:else if contacts.length === 0}
			<div class="text-center py-12 bg-gray-50 rounded-lg">
				<p class="text-gray-600">No contacts found</p>
			</div>
		{:else}
			<div class="bg-white rounded-lg shadow overflow-hidden">
				<table class="min-w-full divide-y divide-gray-200">
					<thead class="bg-gray-50">
						<tr>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Name
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Phone
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Email
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Company
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Status
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Attempts
							</th>
							<th
								class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
							>
								Last Attempt
							</th>
						</tr>
					</thead>
					<tbody class="bg-white divide-y divide-gray-200">
						{#each contacts as contact}
							<tr class="hover:bg-gray-50">
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm font-medium text-gray-900">
										{contact.first_name} {contact.last_name}
									</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{contact.phone_number}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{contact.email || '-'}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{contact.company || '-'}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="px-2 text-xs font-semibold rounded-full {statusColors[contact.status]}">
										{contact.status}
									</span>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{contact.attempts}</div>
								</td>
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900">{formatDate(contact.last_attempt_at)}</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Pagination -->
			<div class="mt-4 flex justify-between items-center">
				<button
					onclick={() => {
						currentPage = Math.max(0, currentPage - 1);
						loadContacts();
					}}
					disabled={currentPage === 0}
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Previous
				</button>
				<span class="text-gray-600">
					Page {currentPage + 1}
				</span>
				<button
					onclick={() => {
						currentPage += 1;
						loadContacts();
					}}
					disabled={contacts.length < pageSize}
					class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Next
				</button>
			</div>
		{/if}
	{/if}
</div>
