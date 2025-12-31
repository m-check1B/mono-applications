import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const STORAGE_KEY = 'kraliki-terminals';

function getInitialTerminals() {
	if (!browser) return [1];
	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored) {
		try {
			return JSON.parse(stored);
		} catch (e) {
			return [1];
		}
	}
	return [1];
}

function createTerminalStore() {
	const initial = getInitialTerminals();
	const { subscribe, set, update } = writable<number[]>(initial);

	return {
		subscribe,
		add: (id: number) => update(n => {
			const next = [...n, id];
			if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
			return next;
		}),
		remove: (id: number) => update(n => {
			const next = n.filter(t => t !== id);
			if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
			return next;
		}),
		set: (val: number[]) => {
			if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(val));
			set(val);
		}
	};
}

export const activeTerminals = createTerminalStore();
