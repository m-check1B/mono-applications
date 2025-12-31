/**
 * Analytics Store
 * Svelte writable store for analytics data
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

export interface AnalyticsOverview {
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    in_progress_tasks: number;
    overdue_tasks: number;
    completion_rate: number;
    avg_completion_time: number; // in hours
    velocity: number; // tasks per week
    tasks_by_priority: {
        low: number;
        medium: number;
        high: number;
    };
    tasks_by_type: Record<string, number>;
}

export interface Bottleneck {
    id: string;
    type: 'stalled_task' | 'overloaded_day' | 'long_running';
    severity: 'low' | 'medium' | 'high';
    description: string;
    affected_items: string[];
    suggestion?: string;
}

export interface AnalyticsState {
    overview: AnalyticsOverview | null;
    bottlenecks: Bottleneck[];
    isLoading: boolean;
    error: string | null;
}

const initialState: AnalyticsState = {
    overview: null,
    bottlenecks: [],
    isLoading: false,
    error: null
};

function createAnalyticsStore() {
    const { subscribe, set, update } = writable<AnalyticsState>(initialState);

    return {
        subscribe,

        async loadOverview(workspaceId?: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                const response: any = await api.analytics.overview({ workspaceId });

                update((state) => ({
                    ...state,
                    overview: response,
                    isLoading: false
                }));

                return { success: true, overview: response };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load analytics overview';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async loadBottlenecks(workspaceId?: string) {
            // Don't set global loading here to avoid flickering if loading separately
            try {
                const response: any = await api.analytics.bottlenecks({ workspaceId });
                const bottlenecks = response.bottlenecks || [];

                update((state) => ({
                    ...state,
                    bottlenecks
                }));

                return { success: true, bottlenecks };
            } catch (error: any) {
                logger.error('Failed to load bottlenecks', error);
                return { success: false, error: error.detail };
            }
        },

        async loadAll(workspaceId?: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                const [overviewRes, bottlenecksRes] = await Promise.all([
                    api.analytics.overview({ workspaceId }),
                    api.analytics.bottlenecks({ workspaceId })
                ]);

                update((state) => ({
                    ...state,
                    overview: overviewRes as any,
                    bottlenecks: (bottlenecksRes as any).bottlenecks || [],
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load analytics data';
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

export const analyticsStore = createAnalyticsStore();
