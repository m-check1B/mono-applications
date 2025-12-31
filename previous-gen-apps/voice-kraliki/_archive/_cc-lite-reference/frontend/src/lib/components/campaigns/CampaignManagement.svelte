<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Button from '../shared/Button.svelte';
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import { trpc } from '$lib/trpc/client';

  let campaigns = $state<any[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  let showCreateModal = $state(false);
  let showEditModal = $state(false);
  let showDeleteModal = $state(false);
  let showDetailsModal = $state(false);
  let selectedCampaign = $state<any>(null);

  let formData = $state({
    name: '',
    description: '',
    script: '',
    priority: 'medium' as 'low' | 'medium' | 'high',
    targetCallsPerDay: 100,
    startDate: '',
    endDate: ''
  });

  // Load campaigns from API
  const loadCampaigns = async () => {
    try {
      loading = true;
      error = null;
      const result = await trpc.campaign.list.query({ limit: 50, offset: 0 });
      campaigns = result.campaigns;
    } catch (err: any) {
      console.error('Failed to load campaigns:', err);
      error = err.message || 'Failed to load campaigns';
      // Fallback to mock data on error
      campaigns = [
        {
          id: '1',
          name: 'Q4 Sales Campaign',
          description: 'End of year sales outreach',
          active: true,
          createdAt: new Date().toISOString(),
          _count: { sessions: 245, metrics: 189 }
        },
        {
          id: '2',
          name: 'Customer Feedback Survey',
          description: 'Quarterly satisfaction survey',
          active: false,
          createdAt: new Date(Date.now() - 7 * 86400000).toISOString(),
          _count: { sessions: 156, metrics: 142 }
        }
      ];
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    loadCampaigns();
  });

  const resetForm = () => {
    formData = {
      name: '',
      description: '',
      script: '',
      priority: 'medium',
      targetCallsPerDay: 100,
      startDate: '',
      endDate: ''
    };
  };

  const handleCreate = async () => {
    try {
      const newCampaign = await trpc.campaign.create.mutate({
        name: formData.name,
        description: formData.description,
        script: formData.script,
        priority: formData.priority,
        targetCallsPerDay: formData.targetCallsPerDay,
        startDate: formData.startDate ? new Date(formData.startDate).toISOString() : undefined,
        endDate: formData.endDate ? new Date(formData.endDate).toISOString() : undefined
      });

      // Add to local state
      campaigns = [...campaigns, { ...newCampaign, _count: { sessions: 0, metrics: 0 } }];
      showCreateModal = false;
      resetForm();
    } catch (err: any) {
      console.error('Failed to create campaign:', err);
      alert(`Failed to create campaign: ${err.message}`);
    }
  };

  const handleEdit = (campaign: any) => {
    selectedCampaign = campaign;
    formData = {
      name: campaign.name,
      description: campaign.description || '',
      script: '',
      priority: 'medium',
      targetCallsPerDay: 100,
      startDate: '',
      endDate: ''
    };
    showEditModal = true;
  };

  const handleUpdate = async () => {
    if (!selectedCampaign) return;

    try {
      const updated = await trpc.campaign.update.mutate({
        id: selectedCampaign.id,
        name: formData.name,
        description: formData.description,
        script: formData.script,
        priority: formData.priority,
        targetCallsPerDay: formData.targetCallsPerDay
      });

      campaigns = campaigns.map(c =>
        c.id === selectedCampaign.id
          ? { ...c, name: formData.name, description: formData.description }
          : c
      );

      showEditModal = false;
      resetForm();
      selectedCampaign = null;
    } catch (err: any) {
      console.error('Failed to update campaign:', err);
      alert(`Failed to update campaign: ${err.message}`);
    }
  };

  const handleToggleCampaign = async (campaign: any) => {
    try {
      if (campaign.active) {
        await trpc.campaign.pause.mutate({ id: campaign.id });
      } else {
        await trpc.campaign.start.mutate({ id: campaign.id });
      }

      campaigns = campaigns.map(c =>
        c.id === campaign.id ? { ...c, active: !c.active } : c
      );
    } catch (err: any) {
      console.error('Failed to toggle campaign:', err);
      alert(`Failed to ${campaign.active ? 'pause' : 'start'} campaign: ${err.message}`);
    }
  };

  const handleDelete = async () => {
    if (!selectedCampaign) return;

    try {
      await trpc.campaign.delete.mutate({ id: selectedCampaign.id });

      campaigns = campaigns.filter(c => c.id !== selectedCampaign.id);
      showDeleteModal = false;
      selectedCampaign = null;
    } catch (err: any) {
      console.error('Failed to delete campaign:', err);
      alert(`Failed to delete campaign: ${err.message}`);
    }
  };

  const getStatusColor = (active: boolean) => {
    return active ? 'success' : 'gray';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'danger';
      case 'medium': return 'warning';
      case 'low': return 'primary';
      default: return 'gray';
    }
  };
</script>

<div class="space-y-6">
  <!-- Header -->
  <Card>
    <div class="p-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Campaign Management</h2>
          <p class="text-gray-600 dark:text-gray-400 mt-1">Create and manage outbound calling campaigns</p>
        </div>
        <Button
          variant="primary"
          onclick={() => showCreateModal = true}
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Campaign
        </Button>
      </div>
    </div>
  </Card>

  <!-- Campaigns List -->
  <Card>
    {#snippet header()}
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Active Campaigns</h3>
        <div class="flex gap-2">
          <Badge variant="gray" class="text-xs">
            Total: {campaigns.length}
          </Badge>
          <Badge variant="success" class="text-xs">
            Active: {campaigns.filter(c => c.active).length}
          </Badge>
        </div>
      </div>
    {/snippet}

    <div class="overflow-x-auto">
      {#if campaigns.length === 0}
        <div class="text-center py-8 text-gray-500">
          No campaigns found
        </div>
      {:else}
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Calls</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Metrics</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            {#each campaigns as campaign, i}
              <tr
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                in:fly={{ y: 20, duration: 300, delay: i * 50, easing: quintOut }}
              >
                <td class="px-4 py-3">
                  <div>
                    <p class="font-medium text-gray-900 dark:text-white">{campaign.name}</p>
                    {#if campaign.description}
                      <p class="text-sm text-gray-500 truncate max-w-xs">
                        {campaign.description}
                      </p>
                    {/if}
                  </div>
                </td>

                <td class="px-4 py-3">
                  <Badge
                    variant={getStatusColor(campaign.active)}
                    class="text-xs"
                  >
                    {campaign.active ? 'Active' : 'Paused'}
                  </Badge>
                </td>

                <td class="px-4 py-3">
                  <span class="text-gray-900 dark:text-white">{campaign._count.sessions}</span>
                </td>

                <td class="px-4 py-3">
                  <span class="text-gray-900 dark:text-white">{campaign._count.metrics}</span>
                </td>

                <td class="px-4 py-3">
                  <p class="text-sm text-gray-500">
                    {new Date(campaign.createdAt).toLocaleDateString()}
                  </p>
                </td>

                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <Button
                      size="sm"
                      variant={campaign.active ? 'warning' : 'success'}
                      onclick={() => handleToggleCampaign(campaign)}
                    >
                      {campaign.active ? 'Pause' : 'Start'}
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onclick={() => handleEdit(campaign)}
                    >
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onclick={() => { selectedCampaign = campaign; showDeleteModal = true; }}
                      disabled={campaign.active}
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  </Card>
</div>

<!-- Create Campaign Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Create New Campaign</h3>

      <div class="space-y-4">
        <div>
          <label for="create-campaign-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Campaign Name *</label>
          <input
            id="create-campaign-name"
            type="text"
            bind:value={formData.name}
            placeholder="Enter campaign name"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>

        <div>
          <label for="create-campaign-description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea
            id="create-campaign-description"
            bind:value={formData.description}
            placeholder="Describe the campaign objectives"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          ></textarea>
        </div>

        <div>
          <label for="create-campaign-script" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Call Script</label>
          <textarea
            id="create-campaign-script"
            bind:value={formData.script}
            placeholder="Enter the script for agents to follow"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="create-campaign-priority" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
            <select
              id="create-campaign-priority"
              bind:value={formData.priority}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label for="create-campaign-target" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Target Calls/Day</label>
            <input
              id="create-campaign-target"
              type="number"
              bind:value={formData.targetCallsPerDay}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="create-campaign-start" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label>
            <input
              id="create-campaign-start"
              type="date"
              bind:value={formData.startDate}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>

          <div>
            <label for="create-campaign-end" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label>
            <input
              id="create-campaign-end"
              type="date"
              bind:value={formData.endDate}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>
        </div>
      </div>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showCreateModal = false; resetForm(); }}>
          Cancel
        </Button>
        <Button variant="primary" onclick={handleCreate} disabled={!formData.name}>
          Create Campaign
        </Button>
      </div>
    </div>
  </div>
{/if}

<!-- Edit Campaign Modal -->
{#if showEditModal && selectedCampaign}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Edit Campaign</h3>

      <div class="space-y-4">
        <div>
          <label for="edit-campaign-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Campaign Name *</label>
          <input
            id="edit-campaign-name"
            type="text"
            bind:value={formData.name}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>

        <div>
          <label for="edit-campaign-description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea
            id="edit-campaign-description"
            bind:value={formData.description}
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          ></textarea>
        </div>
      </div>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showEditModal = false; resetForm(); selectedCampaign = null; }}>
          Cancel
        </Button>
        <Button variant="primary" onclick={handleUpdate} disabled={!formData.name}>
          Save Changes
        </Button>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && selectedCampaign}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-bold text-red-600 mb-4">Delete Campaign</h3>

      <p class="text-gray-700 dark:text-gray-300 mb-4">
        Are you sure you want to delete the campaign "{selectedCampaign.name}"?
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        This action cannot be undone. All associated data will be permanently removed.
      </p>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showDeleteModal = false; selectedCampaign = null; }}>
          Cancel
        </Button>
        <Button variant="danger" onclick={handleDelete}>
          Delete
        </Button>
      </div>
    </div>
  </div>
{/if}
