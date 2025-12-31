import { browser } from '$app/environment';
import { writable, get } from 'svelte/store';
import { STORAGE_KEYS } from '$lib/config/env';

export type ThemeMode = 'dark' | 'light';

const DEFAULT_THEME: ThemeMode = 'dark';

function applyThemeToDocument(theme: ThemeMode) {
	if (!browser) return;
	const root = document.documentElement;
	root.classList.remove('light', 'dark');
	if (theme === 'light') {
		root.classList.add('light');
	} else {
		root.classList.add('dark');
	}
}

function readInitialTheme(): ThemeMode {
	if (!browser) return DEFAULT_THEME;

	const stored = localStorage.getItem(STORAGE_KEYS.theme);
	if (stored === 'dark' || stored === 'light') {
		return stored;
	}

	const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	return prefersDark ? 'dark' : 'light';
}

function persistTheme(theme: ThemeMode) {
	if (!browser) return;
	localStorage.setItem(STORAGE_KEYS.theme, theme);
}

function createThemeStore() {
	const initialTheme = readInitialTheme();
	const store = writable<ThemeMode>(initialTheme);

	if (browser) {
		applyThemeToDocument(initialTheme);
	}

	return {
		subscribe: store.subscribe,
		init: () => {
			const current = get(store);
			applyThemeToDocument(current);
		},
		set(theme: ThemeMode) {
			persistTheme(theme);
			applyThemeToDocument(theme);
			store.set(theme);
		},
		toggle() {
			store.update((prev) => {
				const next = prev === 'dark' ? 'light' : 'dark';
				persistTheme(next);
				applyThemeToDocument(next);
				return next;
			});
		}
	};
}

export const themeStore = createThemeStore();
