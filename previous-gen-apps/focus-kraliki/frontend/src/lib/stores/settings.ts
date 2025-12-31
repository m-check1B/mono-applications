/**
 * Settings Store
 * Svelte writable store for application settings and configuration
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';

export interface UsageStats {
    total_requests: number;
    total_tokens: number;
    cost_estimate: number;
    last_request: string | null;
}

export interface SettingsState {
    openRouterKey: string | null;
    usageStats: UsageStats | null;
    isKeyValid: boolean;
    isLoading: boolean;
    error: string | null;
}

const initialState: SettingsState = {
    openRouterKey: null,
    usageStats: null,
    isKeyValid: false,
    isLoading: false,
    error: null
};

function createSettingsStore() {
    const { subscribe, set, update } = writable<SettingsState>(initialState);

    return {
        subscribe,

        async loadSettings() {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                const stats = await api.settings.getUsageStats() as unknown as UsageStats;

                // If we can fetch stats, we assume the key is valid/configured
                update((state) => ({
                    ...state,
                    usageStats: stats,
                    isKeyValid: true,
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                // If fetching stats fails, it might be because no key is configured or invalid key
                // We don't treat this as a global error to avoid showing an alert immediately on load
                update((state) => ({
                    ...state,
                    isLoading: false,
                    isKeyValid: false,
                    usageStats: null
                }));
                return { success: false, error: error.detail || 'Failed to load settings' };
            }
        },

        async saveOpenRouterKey(key: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                await api.settings.saveOpenRouterKey({ apiKey: key });

                update((state) => ({
                    ...state,
                    isKeyValid: true,
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to save API key';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage,
                    isKeyValid: false
                }));
                return { success: false, error: errorMessage };
            }
        },

        async deleteOpenRouterKey() {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                await api.settings.deleteOpenRouterKey();

                update((state) => ({
                    ...state,
                    isKeyValid: false,
                    isLoading: false,
                    openRouterKey: null
                }));

                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to delete API key';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        }
    };
}

export const settingsStore = createSettingsStore();
