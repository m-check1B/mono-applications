import { locale, type Locale } from '$lib/i18n';
import { browser } from '$app/environment';

export const load = async () => {
  if (browser) {
    const savedLocale = (localStorage.getItem('locale') as Locale) || 'en';
    locale.set(savedLocale);
  }
};
