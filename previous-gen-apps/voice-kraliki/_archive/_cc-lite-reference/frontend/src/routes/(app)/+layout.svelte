<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import BottomNavigation from '$lib/components/mobile/BottomNavigation.svelte';
  import LanguageSwitcher from '$lib/components/i18n/LanguageSwitcher.svelte';

  let { children } = $props();

  onMount(async () => {
    await auth.init();
    if (!auth.isAuthenticated) {
      goto('/login');
    }
  });
</script>

{#if auth.loading}
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  </div>
{:else if auth.isAuthenticated}
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">Voice by Kraliki</h1>
            <nav class="ml-10 flex space-x-4">
              {#if auth.isAgent}
                <a href="/operator" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
              {:else if auth.isSupervisor}
                <a href="/supervisor" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
              {:else if auth.isAdmin}
                <a href="/admin" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  Dashboard
                </a>
                <a href="/admin/campaigns" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  Campaigns
                </a>
                <a href="/admin/users" class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium">
                  Users
                </a>
              {/if}
            </nav>
          </div>
          <div class="flex items-center space-x-4">
            <!-- Language Switcher -->
            <LanguageSwitcher />

            <span class="text-sm text-gray-700 dark:text-gray-300">
              {auth.user?.firstName} {auth.user?.lastName}
              <span class="text-xs text-gray-500 dark:text-gray-400">({auth.user?.role})</span>
            </span>
            <button
              onclick={() => auth.logout()}
              class="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-20 md:pb-8">
      {@render children?.()}
    </main>

    <!-- Mobile Bottom Navigation -->
    <BottomNavigation />
  </div>
{/if}
