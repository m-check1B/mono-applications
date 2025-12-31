/**
 * Calendar Store
 * Svelte writable store for event management and calendar sync
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

export interface CalendarEvent {
    id: string;
    title: string;
    description?: string;
    startTime: string;
    endTime: string;
    location?: string;
    isAllDay: boolean;
    source: 'local' | 'google';
    externalId?: string;
}

export interface CalendarState {
    events: CalendarEvent[];
    isLoading: boolean;
    error: string | null;
    syncStatus: {
        connected: boolean;
        lastSync?: string;
    } | null;
}

const initialState: CalendarState = {
    events: [],
    isLoading: false,
    error: null,
    syncStatus: null
};

function createCalendarStore() {
    const { subscribe, set, update } = writable<CalendarState>(initialState);

    return {
        subscribe,

        async loadEvents(startDate: string, endDate: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                const response: any = await api.events.list({ startDate, endDate });
                const events = response.events || [];

                update((state) => ({
                    ...state,
                    events,
                    isLoading: false
                }));

                return { success: true, events };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load events';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async checkSyncStatus() {
            try {
                const status: any = await api.integration.calendarStatus();
                update((state) => ({
                    ...state,
                    syncStatus: status
                }));
                return { success: true, status };
            } catch (error: any) {
                logger.error('Failed to check sync status', error);
                return { success: false, error: error.detail };
            }
        },

        async syncGoogleCalendar() {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                await api.events.syncGoogle();
                // Reload events after sync
                // Note: In a real app we'd need the current view range here
                update((state) => ({ ...state, isLoading: false }));
                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to sync calendar';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async createEvent(eventData: any) {
            try {
                const newEvent: any = await api.events.create(eventData);
                update((state) => ({
                    ...state,
                    events: [...state.events, newEvent]
                }));
                return { success: true, event: newEvent };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to create event' };
            }
        }
    };
}

export const calendarStore = createCalendarStore();
