<script lang="ts">
  import { auth } from '$lib/stores/auth.svelte';

  let email = $state('');
  let password = $state('');
  let error = $state('');

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';

    const result = await auth.login(email, password);
    if (!result.success) {
      error = result.error || 'Login failed';
    }
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Voice by Kraliki</h1>
    <p class="text-gray-600 dark:text-gray-400 mt-2">Sign in to your account</p>
  </div>

  <form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded">
        {error}
      </div>
    {/if}

    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Email
      </label>
      <input
        id="email"
        type="email"
        bind:value={email}
        required
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        placeholder="agent@example.com"
      />
    </div>

    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Password
      </label>
      <input
        id="password"
        type="password"
        bind:value={password}
        required
        class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        placeholder="••••••••"
      />
    </div>

    <button
      type="submit"
      disabled={auth.loading}
      class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {auth.loading ? 'Signing in...' : 'Sign in'}
    </button>
  </form>

  <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
    <p class="mb-2">Demo accounts:</p>
    <div class="space-y-1 text-xs">
      <p><strong>Admin:</strong> admin@cc-light.local</p>
      <p><strong>Supervisor:</strong> supervisor@cc-light.local</p>
      <p><strong>Agent:</strong> agent1@cc-light.local</p>
    </div>
  </div>
</div>
