<script lang="ts">
  import { currentUser, isAuthenticated } from '$lib/stores/auth';
  import { locale, setLocale, getLocaleName, SUPPORTED_LOCALES, t } from '$lib/i18n';

  // User can change language here
  function handleLocaleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    setLocale(target.value as 'cs' | 'en');
  }
</script>

<svelte:head>
  <title>{$t('nav.settings')} | Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-2xl">
  <h1 class="font-display text-3xl mb-8">{$t('nav.settings').toUpperCase()}</h1>

  {#if $isAuthenticated && $currentUser}
    <!-- Profile Section -->
    <section class="brutal-card p-6 mb-6">
      <h2 class="font-display text-xl mb-4 text-terminal-green">{$t('settings.profile')}</h2>
      <div class="space-y-4">
        <div>
          <span class="block text-sm text-muted-foreground mb-1">{$t('auth.firstName')}</span>
          <div class="text-lg">{$currentUser.first_name}</div>
        </div>
        <div>
          <span class="block text-sm text-muted-foreground mb-1">{$t('auth.lastName')}</span>
          <div class="text-lg">{$currentUser.last_name}</div>
        </div>
        <div>
          <span class="block text-sm text-muted-foreground mb-1">{$t('auth.email')}</span>
          <div class="text-lg">{$currentUser.email}</div>
        </div>
      </div>
    </section>

    <!-- Company Section -->
    {#if $currentUser.company_name}
      <section class="brutal-card p-6 mb-6">
        <h2 class="font-display text-xl mb-4 text-terminal-green">{$t('settings.company')}</h2>
        <div>
          <span class="block text-sm text-muted-foreground mb-1">{$t('auth.companyName')}</span>
          <div class="text-lg">{$currentUser.company_name}</div>
        </div>
      </section>
    {/if}

    <!-- Preferences Section -->
    <section class="brutal-card p-6 mb-6">
      <h2 class="font-display text-xl mb-4 text-terminal-green">{$t('settings.preferences')}</h2>
      <div>
        <label for="language" class="block text-sm text-muted-foreground mb-2">{$t('settings.language')}</label>
        <select
          id="language"
          class="brutal-input w-full max-w-xs"
          value={$locale}
          onchange={handleLocaleChange}
        >
          {#each SUPPORTED_LOCALES as loc}
            <option value={loc}>{getLocaleName(loc)}</option>
          {/each}
        </select>
      </div>
    </section>
  {:else}
    <div class="brutal-card p-6 text-center text-muted-foreground">
      {$t('common.loading')}
    </div>
  {/if}
</div>
