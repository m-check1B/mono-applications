import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark';

function createThemeStore() {
  const initialTheme = (browser && localStorage.getItem('theme') as Theme) || 'dark';
  const { subscribe, set, update } = writable<Theme>(initialTheme);

  if (browser) {
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  return {
    subscribe,
    toggle: () => update(theme => {
      const next = theme === 'light' ? 'dark' : 'light';
      if (browser) {
        localStorage.setItem('theme', next);
        if (next === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
      return next;
    }),
    set: (theme: Theme) => {
      if (browser) {
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
      set(theme);
    }
  };
}

export const themeStore = createThemeStore();
