import { derived, writable } from 'svelte/store';

export const locale = writable('en');

export const locales = {
  en: 'English',
  cs: 'Čeština'
};

export const translations = {
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.calls': 'Calls',
    'nav.campaigns': 'Campaigns',
    'nav.analytics': 'Analytics',
    'call.status.active': 'Active',
    'call.status.completed': 'Completed',
    'call.status.missed': 'Missed',
    'campaign.create': 'Create Campaign',
    'campaign.status': 'Campaign Status'
  },
  cs: {
    'nav.dashboard': 'Přehled',
    'nav.calls': 'Hovory',
    'nav.campaigns': 'Kampaně',
    'nav.analytics': 'Analytika',
    'call.status.active': 'Aktivní',
    'call.status.completed': 'Dokončeno',
    'call.status.missed': 'Zmeškaný',
    'campaign.create': 'Vytvořit kampaň',
    'campaign.status': 'Stav kampaně'
  }
};

export const t = derived(locale, ($locale) => (key: string) => {
  return translations[$locale]?.[key] || key;
});
