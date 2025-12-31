import { locale } from '$lib/i18n';
import { browser } from '$app/environment';

export const load = async () => {
  if (browser) {
    const savedLocale = localStorage.getItem('locale') || 'en';
    locale.set(savedLocale);
  }
};
