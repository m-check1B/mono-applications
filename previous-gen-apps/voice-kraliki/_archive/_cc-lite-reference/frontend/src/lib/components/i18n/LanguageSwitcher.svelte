<script lang="ts">
  import { locale, setLocale, type Locale } from '$lib/i18n';

  const languages: { code: Locale; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'cs', name: 'Čeština', flag: '🇨🇿' }
  ];

  function handleLanguageChange(newLocale: Locale) {
    setLocale(newLocale);
  }
</script>

<div class="language-switcher">
  <select
    value={$locale}
    onchange={(e) => handleLanguageChange(e.currentTarget.value as Locale)}
    class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
           rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2
           focus:ring-primary-500 dark:focus:ring-primary-400"
    aria-label="Select language"
  >
    {#each languages as lang}
      <option value={lang.code}>
        {lang.flag} {lang.name}
      </option>
    {/each}
  </select>
</div>

<style>
  .language-switcher select {
    cursor: pointer;
    transition: all 0.2s;
  }

  .language-switcher select:hover {
    border-color: #3b82f6;
  }
</style>
