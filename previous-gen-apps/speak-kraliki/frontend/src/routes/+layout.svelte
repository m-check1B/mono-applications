<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore, isAuthenticated, currentUser, getUserFromToken } from '$lib/stores/auth';
  import { themeStore } from '$lib/stores/theme';
  import { auth } from '$lib/api/client';
  import { locale, setLocale, initLocale, getLocaleName, SUPPORTED_LOCALES, t } from '$lib/i18n';
  import OnboardingModal from '$lib/components/onboarding/OnboardingModal.svelte';
  import { initAnalytics } from '$lib/analytics';

  let { children } = $props();

  // Check if we're on the voice interface (no nav needed)
  const isVoiceInterface = $derived($page.url.pathname.startsWith('/v/'));
  const isAuthPage = $derived(
    $page.url.pathname === '/login' ||
    $page.url.pathname === '/register' ||
    $page.url.pathname === '/'
  );
  const isDashboard = $derived($page.url.pathname.startsWith('/dashboard'));

  // Restore session on mount
  onMount(() => {
    // Initialize privacy-first analytics (Plausible)
    const cleanupAnalytics = initAnalytics();

    // Initialize locale from storage
    initLocale();

    const restoreSession = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Try to get user from /me endpoint
          const user = await auth.me(token);
          // Also decode token to get company_name
          const tokenUser = getUserFromToken(token);
          authStore.setUser({
            ...user,
            company_name: tokenUser?.company_name,
          });
        } catch {
          // Token invalid, clear it
          authStore.logout();
          if (!isAuthPage && !isVoiceInterface) {
            goto('/login');
          }
        }
      } else {
        authStore.setLoading(false);
      }
    };

    void restoreSession();

    return cleanupAnalytics;
  });

  function handleLogout() {
    authStore.logout();
    goto('/login');
  }

  function toggleLocale() {
    const nextLocale = $locale === 'cs' ? 'en' : 'cs';
    setLocale(nextLocale);
  }
</script>

<div class="min-h-screen bg-background bg-grid-pattern">
  <div class="scanline"></div>
  {#if !isVoiceInterface && !isAuthPage}
    <nav class="border-b-2 border-foreground bg-card">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <a href="/dashboard" class="flex items-center gap-2">
          <span class="text-terminal-green text-2xl">///</span>
          <span class="font-display text-lg">SPEAK BY KRALIKI</span>
          {#if $currentUser?.company_name}
            <span class="text-muted text-sm ml-2">| {$currentUser.company_name}</span>
          {/if}
        </a>

        <div class="flex items-center gap-4">
          <button 
            onclick={() => themeStore.toggle()} 
            class="brutal-btn text-xs py-1 px-2" 
            title="Toggle theme"
          >
            {$themeStore === 'dark' ? '☀️' : '🌙'}
          </button>
          {#if $isAuthenticated}
            <span class="text-sm text-muted hidden md:inline">
              {$currentUser?.first_name} {$currentUser?.last_name}
            </span>
            <button onclick={toggleLocale} class="brutal-btn text-xs py-1 px-2" title="Switch language">
              {$locale.toUpperCase()}
            </button>
            <button onclick={handleLogout} class="brutal-btn brutal-btn-secondary text-sm">
              {$t('nav.logout').toUpperCase()}
            </button>
          {:else}
            <a href="/login" class="brutal-btn text-sm">{$t('auth.login').toUpperCase()}</a>
          {/if}
        </div>
      </div>

      <!-- Dashboard Sub-Navigation -->
      {#if isDashboard}
        <div class="border-t border-foreground/30 bg-void">
          <div class="container mx-auto px-4 py-2 flex gap-4 overflow-x-auto">
            <a
              href="/dashboard"
              class="text-sm whitespace-nowrap {$page.url.pathname === '/dashboard' ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.dashboard').toUpperCase()}
            </a>
            <a
              href="/dashboard/surveys"
              class="text-sm whitespace-nowrap {$page.url.pathname.startsWith('/dashboard/surveys') ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.surveys').toUpperCase()}
            </a>
            <a
              href="/dashboard/alerts"
              class="text-sm whitespace-nowrap {$page.url.pathname.startsWith('/dashboard/alerts') ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.alerts').toUpperCase()}
            </a>
            <a
              href="/dashboard/actions"
              class="text-sm whitespace-nowrap {$page.url.pathname.startsWith('/dashboard/actions') ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.actions').toUpperCase()}
            </a>
            <a
              href="/dashboard/employees"
              class="text-sm whitespace-nowrap {$page.url.pathname.startsWith('/dashboard/employees') ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.employees').toUpperCase()}
            </a>
            <a
              href="/dashboard/settings"
              class="text-sm whitespace-nowrap {$page.url.pathname.startsWith('/dashboard/settings') ? 'text-terminal-green' : 'text-muted-foreground hover:text-foreground'}"
            >
              {$t('nav.settings').toUpperCase()}
            </a>
          </div>
        </div>
      {/if}
    </nav>
  {:else if !isVoiceInterface}
    <!-- Minimal nav for auth pages -->
    <nav class="border-b-2 border-foreground bg-card">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <a href="/" class="flex items-center gap-2">
          <span class="text-terminal-green text-2xl">///</span>
          <span class="font-display text-lg">SPEAK BY KRALIKI</span>
        </a>
        <button onclick={toggleLocale} class="brutal-btn text-xs py-1 px-2" title="Switch language">
          {$locale.toUpperCase()}
        </button>
      </div>
    </nav>
  {/if}

  <main>
    {@render children()}
  </main>

  {#if !isVoiceInterface}
    <footer class="border-t border-foreground/20 py-4 px-6 text-center text-sm text-muted-foreground">
      <div class="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4">
        <span>&copy; 2026 Verduona s.r.o.</span>
        <a href="/privacy" class="hover:text-foreground transition-colors">Privacy</a>
      </div>
    </footer>
  {/if}

  <!-- Onboarding for new users (only show on dashboard) -->
  {#if isDashboard && $isAuthenticated}
    <OnboardingModal />
  {/if}
</div>

<style>
</style>
