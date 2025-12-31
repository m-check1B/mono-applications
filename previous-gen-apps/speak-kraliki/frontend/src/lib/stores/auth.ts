/**
 * Speak by Kraliki - Auth Store
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  company_id?: string;
  company_name?: string;  // From JWT payload
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: browser ? localStorage.getItem('access_token') : null,
  refreshToken: browser ? localStorage.getItem('refresh_token') : null,
  loading: true,
};

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(initialState);

  return {
    subscribe,

    setTokens: (accessToken: string, refreshToken: string) => {
      if (browser) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
      }
      update((state) => ({
        ...state,
        accessToken,
        refreshToken,
      }));
    },

    setUser: (user: User | null) => {
      update((state) => ({
        ...state,
        user,
        loading: false,
      }));
    },

    logout: () => {
      if (browser) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        loading: false,
      });
    },

    setLoading: (loading: boolean) => {
      update((state) => ({ ...state, loading }));
    },
  };
}

export const authStore = createAuthStore();

/**
 * Decode JWT payload (no verification - server validates)
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

/**
 * Extract user from JWT token payload
 */
export function getUserFromToken(token: string): User | null {
  const payload = decodeJwtPayload(token);
  if (!payload) return null;

  return {
    id: payload.sub as string,
    email: payload.email as string,
    first_name: payload.first_name as string,
    last_name: payload.last_name as string,
    role: payload.role as string,
    company_id: payload.company_id as string,
    company_name: payload.company_name as string | undefined,
  };
}

// Derived stores
export const isAuthenticated = derived(
  authStore,
  ($auth) => !!$auth.accessToken && !!$auth.user
);

export const currentUser = derived(authStore, ($auth) => $auth.user);

export const accessToken = derived(authStore, ($auth) => $auth.accessToken);
