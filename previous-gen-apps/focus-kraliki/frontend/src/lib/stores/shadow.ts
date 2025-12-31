/**
 * Shadow Work Store
 * Svelte writable store for shadow work analysis and insights
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';

export interface ShadowInsight {
    id: string;
    type: 'pattern' | 'resistance' | 'projection' | 'integration';
    title: string;
    description: string;
    confidence: number;
    related_tasks?: string[];
    acknowledged: boolean;
    created_at: string;
}

export interface ShadowProfile {
    archetypes: {
        primary: string;
        secondary?: string;
        shadow: string;
    };
    traits: string[];
    integration_level: number;
    last_analysis: string;
}

export interface ShadowState {
    profile: ShadowProfile | null;
    insights: ShadowInsight[];
    unlockStatus: {
        isUnlocked: boolean;
        progress: number;
        requirements: string[];
    } | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: ShadowState = {
    profile: null,
    insights: [],
    unlockStatus: null,
    isLoading: false,
    error: null
};

function createShadowStore() {
    const { subscribe, set, update } = writable<ShadowState>(initialState);

    return {
        subscribe,

        async loadAll() {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                // In a real app, we might fetch profile and insights separately
                // For now, assuming endpoints exist or using placeholders if backend isn't fully ready
                const [insightsRes, unlockRes] = await Promise.all([
                    api.shadow.getInsights(),
                    api.shadow.getUnlockStatus()
                ]);

                // Mock profile for now if not available in API
                const profile: ShadowProfile = {
                    archetypes: {
                        primary: 'The Creator',
                        secondary: 'The Ruler',
                        shadow: 'The Perfectionist'
                    },
                    traits: ['High Standards', 'Control', 'Visionary'],
                    integration_level: 45,
                    last_analysis: new Date().toISOString()
                };

                update((state) => ({
                    ...state,
                    profile,
                    insights: (insightsRes as any).insights || [],
                    unlockStatus: (unlockRes as any) || { isUnlocked: false, progress: 0, requirements: [] },
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load shadow work data';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async analyze() {
            update((state) => ({ ...state, isLoading: true }));
            try {
                const result: any = await api.shadow.analyze({});

                update((state) => ({
                    ...state,
                    insights: [...(result.new_insights || []), ...state.insights],
                    isLoading: false
                }));

                return { success: true, result };
            } catch (error: any) {
                const errorMessage = error.detail || 'Analysis failed';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async acknowledgeInsight(insightId: string) {
            try {
                await api.shadow.acknowledgeInsight(insightId);

                update((state) => ({
                    ...state,
                    insights: state.insights.map(i =>
                        i.id === insightId ? { ...i, acknowledged: true } : i
                    )
                }));

                return { success: true };
            } catch (error: any) {
                return { success: false, error: error.detail };
            }
        }
    };
}

export const shadowStore = createShadowStore();
