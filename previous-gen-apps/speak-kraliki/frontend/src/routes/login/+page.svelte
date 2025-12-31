<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/api/client';
  import { authStore, getUserFromToken } from '$lib/stores/auth';
  import { t } from '$lib/i18n';

  let email = $state('');
  let password = $state('');
  let error = $state<string | null>(null);
  let loading = $state(false);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    error = null;
    loading = true;

    try {
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
      error = e.message || $t('auth.invalidCredentials');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>{$t('auth.login')} - Speak by Kraliki</title>
</svelte:head>

<div class="min-h-[calc(100vh-60px)] flex items-center justify-center p-4">
  <div class="brutal-card max-w-md w-full p-8">
    <div class="text-center mb-8">
      <h1 class="text-2xl mb-2">{$t('auth.login').toUpperCase()}</h1>
      <p class="text-sm text-muted-foreground">{$t('auth.loginDescription')}</p>
    </div>

    {#if error}
      <div class="mb-6 p-4 border-2 border-system-red text-system-red text-sm">
        {error}
      </div>
    {/if}

    <form onsubmit={handleSubmit}>
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
          required
          disabled={loading}
        />
      </div>

      <button
        type="submit"
        class="brutal-btn brutal-btn-primary w-full mb-4"
        disabled={loading}
      >
        {loading ? $t('auth.loggingIn').toUpperCase() : $t('auth.login').toUpperCase()}
      </button>
    </form>

    <div class="relative my-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t-2 border-foreground/20"></div>
      </div>
      <div class="relative flex justify-center text-xs">
        <span class="bg-background px-2 text-muted-foreground">OR CONTINUE WITH</span>
      </div>
    </div>

    <a
      href="/auth/sso"
      class="brutal-btn w-full mb-4 flex items-center justify-center gap-2 border-2 border-terminal-green bg-terminal-green/10 hover:bg-terminal-green hover:text-background"
    >
      <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 17l10 5 10-5"/>
        <path d="M2 12l10 5 10-5"/>
      </svg>
      SIGN IN WITH KRALIKI SSO
    </a>

    <div class="text-center text-sm">
      <span class="text-muted-foreground">{$t('auth.noAccount')} </span>
      <a href="/register" class="text-terminal-green hover:underline">
        {$t('auth.register').toUpperCase()}
      </a>
    </div>
  </div>
</div>

<style>
</style>
