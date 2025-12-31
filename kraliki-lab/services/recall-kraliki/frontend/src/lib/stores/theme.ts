import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Initialize theme from localStorage or system preference
function getInitialTheme(): 'light' | 'dark' {
	if (!browser) return 'light';

	const stored = localStorage.getItem('theme');
	if (stored === 'dark' || stored === 'light') {
		return stored;
	}

	// Check system preference
	if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
		return 'dark';
	}

	return 'light';
}

export const theme = writable<'light' | 'dark'>(getInitialTheme());

// Subscribe to theme changes and update localStorage + document class
if (browser) {
	theme.subscribe((value) => {
		localStorage.setItem('theme', value);

		if (value === 'dark') {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	});

	// Apply initial theme
	const initial = getInitialTheme();
	if (initial === 'dark') {
		document.documentElement.classList.add('dark');
	}
}

export function toggleTheme() {
	theme.update((current) => (current === 'light' ? 'dark' : 'light'));
}
