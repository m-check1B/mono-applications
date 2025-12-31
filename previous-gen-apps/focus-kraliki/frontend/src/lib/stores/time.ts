/**
 * Time Store
 * Svelte writable store for time entry management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import {
	OFFLINE_STORES,
	clearOfflineStore,
	isOnline,
	offlineTimeEntries,
	queueOperation
} from '$lib/utils/offlineStorage';
import { logger } from '$lib/utils/logger';

export interface TimeEntry {
    id: string;
    userId: string;
    taskId?: string;
    projectId?: string;
    description?: string;
    startTime: string;
    endTime?: string;
    durationSeconds?: number;
    billable: boolean;
    hourlyRate?: number;
}

export interface TimeState {
    entries: TimeEntry[];
    activeEntry: TimeEntry | null;
    stats: any | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: TimeState = {
    entries: [],
    activeEntry: null,
    stats: null,
    isLoading: false,
    error: null
};

function createTimeStore() {
    const { subscribe, set, update } = writable<TimeState>(initialState);

    return {
        subscribe,

        async loadEntries(limit: number = 50) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                if (!isOnline()) {
                    const entries = await offlineTimeEntries.getAll();

                    update((state) => ({
                        ...state,
                        entries,
                        isLoading: false
                    }));

                    return { success: true, entries };
                }

                const response: any = await api.timeEntries.list({ limit });
                const entries = response.entries || [];

                await clearOfflineStore(OFFLINE_STORES.TIME_ENTRIES);
                for (const entry of entries) {
                    await offlineTimeEntries.save(entry);
                }

                update((state) => ({
                    ...state,
                    entries,
                    isLoading: false
                }));

                return { success: true, entries };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load time entries';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async loadActiveEntry() {
            try {
                if (!isOnline()) {
                    const entries = await offlineTimeEntries.getAll();
                    const entry = entries.find((item: TimeEntry) => !item.endTime) || null;
                    update((state) => ({
                        ...state,
                        activeEntry: entry
                    }));
                    return { success: true, entry };
                }

                const entry: any = await api.timeEntries.active();
                update((state) => ({
                    ...state,
                    activeEntry: entry
                }));
                return { success: true, entry };
            } catch (error: any) {
                // 404 means no active entry, which is fine
                if (error.status !== 404) {
                    logger.error('Failed to load active entry', error);
                }
                update((state) => ({ ...state, activeEntry: null }));
                return { success: false, error: error.detail };
            }
        },

        async startTimer(data: { description?: string; projectId?: string; taskId?: string; billable?: boolean }) {
            try {
                if (!isOnline()) {
                    const now = new Date().toISOString();
                    const offlineEntry: TimeEntry = {
                        id: crypto.randomUUID?.() || `offline-${Date.now()}`,
                        userId: 'offline',
                        taskId: data.taskId,
                        projectId: data.projectId,
                        description: data.description,
                        startTime: now,
                        billable: data.billable ?? false
                    };

                    await offlineTimeEntries.save(offlineEntry);
                    await queueOperation({
                        type: 'create',
                        entity: 'timeEntry',
                        data,
                        endpoint: '/time-entries'
                    });

                    update((state) => ({
                        ...state,
                        activeEntry: offlineEntry,
                        entries: [offlineEntry, ...state.entries]
                    }));
                    return { success: true, entry: offlineEntry };
                }

                const newEntry: any = await api.timeEntries.create(data);
                await offlineTimeEntries.save(newEntry);
                update((state) => ({
                    ...state,
                    activeEntry: newEntry,
                    entries: [newEntry, ...state.entries]
                }));
                return { success: true, entry: newEntry };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to start timer' };
            }
        },

        async stopTimer(entryId: string) {
            try {
                if (!isOnline()) {
                    const now = new Date().toISOString();
                    let updatedEntry: TimeEntry | null = null;

                    update((state) => {
                        const entries = state.entries.map((entry) => {
                            if (entry.id !== entryId) return entry;
                            updatedEntry = {
                                ...entry,
                                endTime: now,
                                durationSeconds: entry.startTime
                                    ? Math.max(0, Math.floor((Date.parse(now) - Date.parse(entry.startTime)) / 1000))
                                    : entry.durationSeconds
                            };
                            return updatedEntry;
                        });

                        return {
                            ...state,
                            activeEntry: null,
                            entries
                        };
                    });

                    if (updatedEntry) {
                        await offlineTimeEntries.save(updatedEntry);
                    }

                    await queueOperation({
                        type: 'create',
                        entity: 'timeEntry',
                        data: {},
                        endpoint: `/time-entries/${entryId}/stop`
                    });

                    return { success: true, entry: updatedEntry };
                }

                const updatedEntry: any = await api.timeEntries.stop(entryId);
                await offlineTimeEntries.save(updatedEntry);
                update((state) => ({
                    ...state,
                    activeEntry: null,
                    entries: state.entries.map(e => e.id === entryId ? updatedEntry : e)
                }));
                return { success: true, entry: updatedEntry };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to stop timer' };
            }
        },

        async deleteEntry(entryId: string) {
            try {
                if (!isOnline()) {
                    await offlineTimeEntries.delete(entryId);
                    await queueOperation({
                        type: 'delete',
                        entity: 'timeEntry',
                        data: {},
                        endpoint: `/time-entries/${entryId}`
                    });

                    update((state) => ({
                        ...state,
                        entries: state.entries.filter(e => e.id !== entryId),
                        activeEntry: state.activeEntry?.id === entryId ? null : state.activeEntry
                    }));
                    return { success: true };
                }

                await api.timeEntries.delete(entryId);
                update((state) => ({
                    ...state,
                    entries: state.entries.filter(e => e.id !== entryId),
                    activeEntry: state.activeEntry?.id === entryId ? null : state.activeEntry
                }));
                return { success: true };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to delete entry' };
            }
        }
    };
}

export const timeStore = createTimeStore();
