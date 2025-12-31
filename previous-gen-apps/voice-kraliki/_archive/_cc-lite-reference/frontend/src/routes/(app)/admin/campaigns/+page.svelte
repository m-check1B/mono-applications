<script lang="ts">
  import CampaignManagement from '$lib/components/campaigns/CampaignManagement.svelte';
</script>

<div class="space-y-6">
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
      Campaign Management
    </h1>
    <p class="text-gray-600 dark:text-gray-400">
      Manage all outbound calling campaigns from this central dashboard.
    </p>
  </div>

  <CampaignManagement />
</div>
