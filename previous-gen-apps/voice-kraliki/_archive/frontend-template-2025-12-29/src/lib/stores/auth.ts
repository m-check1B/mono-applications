import { browser } from '$app/environment';
import { writable, get } from 'svelte/store';
import { BACKEND_URL, STORAGE_KEYS } from '$lib/config/env';
import { login as loginRequest, register as registerRequest, logout as logoutRequest, type Credentials, type RegisterPayload } from '$lib/services/auth';
import { crossTabSync } from '$lib/services/crossTabSync';

export type AuthStatus = 'unauthenticated' | 'authenticating' | 'authenticated' | 'refreshing';

export interface AuthTokens {
	accessToken: string;
	refreshToken: string;
	expiresAt?: number;
}

export interface AuthUser {
	id: string;
	email?: string;
	name?: string;
	role?: string;
}

export interface AuthState {
	status: AuthStatus;
	user: AuthUser | null;
	tokens: AuthTokens | null;
	error?: string | null;
}

const initialState: AuthState = {
	status: 'unauthenticated',
	user: null,
	tokens: null,
	error: null
};

function persistState(state: AuthState) {
	if (!browser) return;
	try {
		localStorage.setItem(
			STORAGE_KEYS.auth,
			JSON.stringify({
				tokens: state.tokens,
				user: state.user
			})
		);
	} catch (error) {
		console.error('Failed to persist auth state', error);
	}
}

function restoreState(): Pick<AuthState, 'tokens' | 'user'> {
	if (!browser) return { tokens: null, user: null };

	try {
		const raw = localStorage.getItem(STORAGE_KEYS.auth);
		if (!raw) return { tokens: null, user: null };

		const parsed = JSON.parse(raw) as Partial<AuthState>;
		return {
			tokens: parsed.tokens ?? null,
			user: parsed.user ?? null
		};
	} catch (error) {
		console.warn('Failed to restore auth state', error);
		return { tokens: null, user: null };
	}
}

async function requestTokenRefresh(refreshToken: string) {
	try {
		const response = await fetch(`${BACKEND_URL}/auth/refresh`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ refresh_token: refreshToken })
		});

		if (!response.ok) {
			throw new Error(`Failed to refresh token: ${response.statusText}`);
		}

		const payload = await response.json();
		return payload as { access_token: string; refresh_token?: string; expires_at?: number; user?: AuthUser };
	} catch (error) {
		console.error('Token refresh failed', error);
		throw error;
	}
}

// Cross-tab synchronization helper functions
function broadcastAuthUpdate(tokens: AuthTokens, user: AuthUser | null) {
	if (browser && crossTabSync.isAvailable()) {
		crossTabSync.broadcast('auth_updated', { tokens, user });
	}
}

function broadcastLogout() {
	if (browser && crossTabSync.isAvailable()) {
		crossTabSync.broadcast('auth_logout', {});
	}
}

function createAuthStore() {
	const restored = restoreState();
	const store = writable<AuthState>({
		...initialState,
		...restored,
		status: restored.tokens ? 'authenticated' : 'unauthenticated'
	});

	// Cross-tab synchronization
	if (browser && crossTabSync.isAvailable()) {
		// Listen for auth updates from other tabs
		crossTabSync.subscribe('auth_updated', (message) => {
			const { tokens, user } = message.payload;
			store.update(() => {
				const next: AuthState = {
					status: 'authenticated',
					tokens,
					user,
					error: null
				};
				persistState(next);
				return next;
			});
		});

		// Listen for logout from other tabs
		crossTabSync.subscribe('auth_logout', () => {
			store.set(initialState);
			if (browser) {
				localStorage.removeItem(STORAGE_KEYS.auth);
			}
		});
	}

	return {
		subscribe: store.subscribe,
		getSnapshot: () => get(store),
		setAuthenticating() {
			store.update((prev) => ({ ...prev, status: 'authenticating', error: null }));
		},
		setAuthenticated(data: { tokens: AuthTokens; user: AuthUser | null }) {
			store.update(() => {
				const next: AuthState = {
					status: 'authenticated',
					tokens: data.tokens,
					user: data.user,
					error: null
				};
				persistState(next);
				return next;
			});
		},
		setError(error: string) {
			store.update((prev) => ({ ...prev, error, status: 'unauthenticated' }));
		},
		clear() {
			store.set(initialState);
			if (browser) {
				localStorage.removeItem(STORAGE_KEYS.auth);
			}
		},
		async login(credentials: Credentials) {
			this.setAuthenticating();
			try {
				const response = await loginRequest(credentials);
				const tokens: AuthTokens = {
					accessToken: response.access_token,
					refreshToken: response.refresh_token,
					expiresAt: response.expires_at
				};
				const user = response.user ?? null;

				store.update(() => {
					const next: AuthState = {
						status: 'authenticated',
						tokens,
						user,
						error: null
					};
					persistState(next);
					return next;
				});

				// Broadcast to other tabs
				broadcastAuthUpdate(tokens, user);

				return { success: true } as const;
			} catch (error) {
				const message = error instanceof Error ? error.message : 'Failed to sign in';
				store.set({ ...initialState, error: message });
				return { success: false, error: message } as const;
			}
		},
		async register(payload: RegisterPayload) {
			this.setAuthenticating();
			try {
				const response = await registerRequest(payload);
				const tokens: AuthTokens = {
					accessToken: response.access_token,
					refreshToken: response.refresh_token,
					expiresAt: response.expires_at
				};
				const user = response.user ?? null;

				store.update(() => {
					const next: AuthState = {
						status: 'authenticated',
						tokens,
						user,
						error: null
					};
					persistState(next);
					return next;
				});

				// Broadcast to other tabs
				broadcastAuthUpdate(tokens, user);

				return { success: true } as const;
			} catch (error) {
				const message = error instanceof Error ? error.message : 'Failed to register';
				store.set({ ...initialState, error: message });
				return { success: false, error: message } as const;
			}
		},
		async logout() {
			try {
				await logoutRequest();
			} catch (error) {
				console.warn('Logout request failed', error);
			} finally {
				this.clear();
				// Broadcast to other tabs
				broadcastLogout();
			}
		},
		async refreshTokens(): Promise<boolean> {
			const current = get(store);
			const refreshToken = current.tokens?.refreshToken;
			if (!refreshToken) return false;

			store.update((prev) => ({ ...prev, status: 'refreshing' }));

			try {
				const response = await requestTokenRefresh(refreshToken);
				const nextTokens: AuthTokens = {
					accessToken: response.access_token,
					refreshToken: response.refresh_token ?? refreshToken,
					expiresAt: response.expires_at
				};
				const user = response.user ?? current.user;

				store.update((prev) => {
					const next: AuthState = {
						status: 'authenticated',
						tokens: nextTokens,
						user,
						error: null
					};
					persistState(next);
					return next;
				});

				// Broadcast to other tabs
				broadcastAuthUpdate(nextTokens, user);

				return true;
			} catch (error) {
				store.set({ ...initialState, error: 'Session expired' });
				return false;
			}
		}
	};
}

export const authStore = createAuthStore();
