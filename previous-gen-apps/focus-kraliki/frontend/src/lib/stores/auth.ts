/**
 * Authentication Store
 * Svelte writable store for auth state management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';

export interface User {
        id: string;
        email: string;
        full_name: string;
        google_id?: string;
        role: string;
        status: string;
        created_at: string;
        activeWorkspaceId?: string;
        isPremium?: boolean;
        usageCount?: number;
        academyStatus?: string;
        academyInterest?: string;
}

export interface AuthState {
        user: User | null;
        token: string | null;
        isAuthenticated: boolean;
        isLoading: boolean;
        error: string | null;
}

const initialState: AuthState = {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
};

const TOKEN_COOKIE = 'focus_token';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

const getGoogleRedirectUri = () => {
        if (import.meta.env.PUBLIC_GOOGLE_REDIRECT_URI) {
                return import.meta.env.PUBLIC_GOOGLE_REDIRECT_URI;
        }

        if (typeof window !== 'undefined') {
                return `${window.location.origin}/auth/google/callback`;
        }

        return '';
};

const setTokenCookie = (token: string | null) => {
        if (typeof document === 'undefined') {
                return;
        }

        if (token) {
                document.cookie = `${TOKEN_COOKIE}=${token}; Path=/; Max-Age=${COOKIE_MAX_AGE}; SameSite=Lax`;
        } else {
                document.cookie = `${TOKEN_COOKIE}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
        }
};

function createAuthStore() {
        const { subscribe, set, update } = writable<AuthState>(initialState);

        return {
                subscribe,

                async login(email: string, password: string) {
                        update((state) => ({ ...state, isLoading: true, error: null }));

                        try {
                                const response: any = await api.auth.login({ email, password });

                                const newState: AuthState = {
                                        user: response.user,
                                        token: response.token,
                                        isAuthenticated: true,
                                        isLoading: false,
                                        error: null
                                };

                                // Store token for API client and localStorage
                                api.setToken(response.token);
                                localStorage.setItem('token', response.token);
                                setTokenCookie(response.token);

                                set(newState);
                                return { success: true };
                        } catch (error: any) {
                                const errorMessage = error.detail || 'Login failed';
                                update((state) => ({
                                        ...state,
                                        isLoading: false,
                                        error: errorMessage
                                }));
                                return { success: false, error: errorMessage };
                        }
                },

                async register(email: string, password: string, full_name: string) {
                        update((state) => ({ ...state, isLoading: true, error: null }));

                        try {
                                const response: any = await api.auth.register({ email, password, name: full_name });

                                const newState: AuthState = {
                                        user: response.user,
                                        token: response.token,
                                        isAuthenticated: true,
                                        isLoading: false,
                                        error: null
                                };

                                // Store token
                                api.setToken(response.token);
                                localStorage.setItem('token', response.token);
                                setTokenCookie(response.token);

                                set(newState);
                                return { success: true };
                        } catch (error: any) {
                                const errorMessage = error.detail || 'Registration failed';
                                update((state) => ({
                                        ...state,
                                        isLoading: false,
                                        error: errorMessage
                                }));
                                return { success: false, error: errorMessage };
                        }
                },

                async getGoogleAuthUrl(state: string) {
                        try {
                                const response = await api.google.getAuthUrl({
                                        redirect_uri: getGoogleRedirectUri(),
                                        state
                                });
                                return response;
                        } catch (error: any) {
                                throw error;
                        }
                },

                async loginWithGoogle(code: string, redirectUri: string) {
                        update((state) => ({ ...state, isLoading: true, error: null }));

                        try {
                                const response: any = await api.google.login({ code, redirect_uri: redirectUri });

                                const newState: AuthState = {
                                        user: response.user,
                                        token: response.token,
                                        isAuthenticated: true,
                                        isLoading: false,
                                        error: null
                                };

                                api.setToken(response.token);
                                localStorage.setItem('token', response.token);
                                setTokenCookie(response.token);

                                set(newState);
                                return { success: true };
                        } catch (error: any) {
                                const errorMessage = error.detail || 'Google login failed';
                                update((state) => ({
                                        ...state,
                                        isLoading: false,
                                        error: errorMessage
                                }));
                                return { success: false, error: errorMessage };
                        }
                },

                async restoreSession(token: string) {
                        update((state) => ({ ...state, isLoading: true }));

                        try {
                                api.setToken(token);
                                const user: any = await api.auth.me();

                                set({
                                        user,
                                        token,
                                        isAuthenticated: true,
                                        isLoading: false,
                                        error: null
                                });
                                setTokenCookie(token);

                                return { success: true };
                        } catch (error) {
                                // Token invalid, clear everything
                                localStorage.removeItem('token');
                                api.setToken(null);
                                setTokenCookie(null);
                                set(initialState);
                                return { success: false };
                        }
                },

                async logout() {
                        try {
                                await api.auth.logout();
                        } catch (error) {
                                // Continue logout even if API call fails
                        }

                        localStorage.removeItem('token');
                        api.setToken(null);
                        setTokenCookie(null);
                        set(initialState);
                },

                clearError() {
                        update((state) => ({ ...state, error: null }));
                }
        };
}

export const authStore = createAuthStore();
