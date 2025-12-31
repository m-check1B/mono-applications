<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/api/client';
  import { authStore, getUserFromToken } from '$lib/stores/auth';
  import { t } from '$lib/i18n';

  let firstName = $state('');
  let lastName = $state('');
  let email = $state('');
  let password = $state('');
  let companyName = $state('');
  let error = $state<string | null>(null);
  let loading = $state(false);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    error = null;
    loading = true;

    try {
      // Register the user
      await auth.register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        company_name: companyName,
      });

      // Auto-login after successful registration
      const result = await auth.login(email, password);
      authStore.setTokens(result.access_token, result.refresh_token);

      // Get user from /me and enrich with token data (company_name)
      const user = await auth.me(result.access_token);
      const tokenUser = getUserFromToken(result.access_token);
      authStore.setUser({
        ...user,
        company_name: tokenUser?.company_name,
      });

      goto('/dashboard');
    } catch (e: any) {
      error = e.message || $t('common.error');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('auth.register')} - Speak by Kraliki</title>
</svelte:head>

<div class="min-h-[calc(100vh-60px)] flex items-center justify-center p-4">
  <div class="brutal-card max-w-md w-full p-8">
    <div class="text-center mb-8">
      <h1 class="text-2xl mb-2">{$t('auth.register').toUpperCase()}</h1>
      <p class="text-sm text-muted-foreground">{$t('auth.registerDescription')}</p>
    </div>

    {#if error}
      <div class="mb-6 p-4 border-2 border-system-red text-system-red text-sm">
        {error}
      </div>
    {/if}

    <form onsubmit={handleSubmit}>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label for="firstName" class="block text-sm mb-2">{$t('auth.firstName').toUpperCase()}</label>
          <input
            id="firstName"
            type="text"
            bind:value={firstName}
            class="brutal-input w-full"
            required
            disabled={loading}
          />
        </div>
        <div>
          <label for="lastName" class="block text-sm mb-2">{$t('auth.lastName').toUpperCase()}</label>
          <input
            id="lastName"
            type="text"
            bind:value={lastName}
            class="brutal-input w-full"
            required
            disabled={loading}
          />
        </div>
      </div>

      <div class="mb-4">
        <label for="companyName" class="block text-sm mb-2">{$t('auth.companyName').toUpperCase()}</label>
        <input
          id="companyName"
          type="text"
          bind:value={companyName}
          class="brutal-input w-full"
          required
          disabled={loading}
        />
      </div>

      <div class="mb-4">
        <label for="email" class="block text-sm mb-2">{$t('auth.email').toUpperCase()}</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          class="brutal-input w-full"
          required
          disabled={loading}
        />
      </div>

      <div class="mb-6">
        <label for="password" class="block text-sm mb-2">{$t('auth.password').toUpperCase()}</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          class="brutal-input w-full"
          minlength="8"
          required
          disabled={loading}
        />
        <p class="text-xs text-muted-foreground mt-1">{$t('auth.minPassword')}</p>
      </div>

      <button
        type="submit"
        class="brutal-btn brutal-btn-primary w-full mb-4"
        disabled={loading}
      >
        {loading ? $t('auth.creatingAccount').toUpperCase() : $t('common.create').toUpperCase()}
      </button>
    </form>

    <div class="text-center text-sm">
      <span class="text-muted-foreground">{$t('auth.hasAccount')} </span>
      <a href="/login" class="text-terminal-green hover:underline">
        {$t('auth.login').toUpperCase()}
      </a>
    </div>
  </div>
</div>

<style>
</style>
