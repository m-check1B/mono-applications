/**
 * i18n Configuration and Setup
 *
 * Internationalization system supporting multiple languages
 * with dynamic loading and browser language detection.
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Supported languages
export const SUPPORTED_LOCALES = ['en', 'es', 'cs'] as const;
export type Locale = typeof SUPPORTED_LOCALES[number];

export const LOCALE_NAMES: Record<Locale, string> = {
	en: 'English',
	es: 'Español',
	cs: 'Čeština'
};

// Current locale store
const STORAGE_KEY = 'cc-lite-locale';

function getInitialLocale(): Locale {
	if (!browser) return 'en';

	// Check localStorage
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored && SUPPORTED_LOCALES.includes(stored as Locale)) {
		return stored as Locale;
	}

	// Check browser language
	const browserLang = navigator.language.split('-')[0];
	if (SUPPORTED_LOCALES.includes(browserLang as Locale)) {
		return browserLang as Locale;
	}

	return 'en';
}

export const locale = writable<Locale>(getInitialLocale());

// Save locale changes to localStorage
if (browser) {
	locale.subscribe((value) => {
		localStorage.setItem(STORAGE_KEY, value);
	});
}

// Translation store
const translations = writable<Record<string, any>>({});

// Load translations for a locale
export async function loadTranslations(newLocale: Locale) {
	try {
		const common = await import(`./locales/${newLocale}/common.json`);
		const navigation = await import(`./locales/${newLocale}/navigation.json`);
		const analytics = await import(`./locales/${newLocale}/analytics.json`);
		const operations = await import(`./locales/${newLocale}/operations.json`);
		const campaigns = await import(`./locales/${newLocale}/campaigns.json`);

		translations.set({
			common: common.default,
			navigation: navigation.default,
			analytics: analytics.default,
			operations: operations.default,
			campaigns: campaigns.default
		});

		locale.set(newLocale);
	} catch (error) {
		console.error(`Failed to load translations for ${newLocale}:`, error);
	}
}

// Derived store for current translations
export const t = derived(
	[translations, locale],
	([$translations, $locale]) => {
		return (key: string, params?: Record<string, string | number>): string => {
			const keys = key.split('.');
			let value: any = $translations;

			for (const k of keys) {
				if (value && typeof value === 'object' && k in value) {
					value = value[k];
				} else {
					console.warn(`Translation key not found: ${key}`);
					return key;
				}
			}

			if (typeof value !== 'string') {
				console.warn(`Translation key is not a string: ${key}`);
				return key;
			}

			// Replace parameters
			if (params) {
				return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
					return params[paramKey]?.toString() || match;
				});
			}

			return value;
		};
	}
);

// Helper function to change locale
export function setLocale(newLocale: Locale) {
	if (SUPPORTED_LOCALES.includes(newLocale)) {
		loadTranslations(newLocale);
	}
}

// Initialize translations
if (browser) {
	loadTranslations(getInitialLocale());
}
