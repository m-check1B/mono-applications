/**
 * Push Notifications Store
 * Manages Web Push subscription state and notification preferences
 */

import { writable, get } from 'svelte/store';
import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

export interface NotificationState {
    isSupported: boolean;
    permission: NotificationPermission;
    isSubscribed: boolean;
    isLoading: boolean;
    error: string | null;
    preferences: NotificationPreferences;
}

export interface NotificationPreferences {
    taskReminders: boolean;
    dailyDigest: boolean;
    pomodoroAlerts: boolean;
    projectUpdates: boolean;
}

const defaultPreferences: NotificationPreferences = {
    taskReminders: true,
    dailyDigest: true,
    pomodoroAlerts: true,
    projectUpdates: false
};

const initialState: NotificationState = {
    isSupported: false,
    permission: 'default',
    isSubscribed: false,
    isLoading: false,
    error: null,
    preferences: defaultPreferences
};

function createNotificationsStore() {
    const store = writable<NotificationState>(initialState);
    const { subscribe, set, update } = store;

    // Check if push notifications are supported
    function checkSupport(): boolean {
        if (typeof window === 'undefined') return false;
        return 'serviceWorker' in navigator &&
               'PushManager' in window &&
               'Notification' in window;
    }

    // Convert URL-safe base64 to Uint8Array for VAPID key
    function urlBase64ToUint8Array(base64String: string): Uint8Array {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async function loadPreferences() {
        try {
            const prefs: any = await api.notifications.getPreferences();
            update(s => ({
                ...s,
                preferences: { ...defaultPreferences, ...prefs }
            }));
            return { success: true };
        } catch (error: any) {
            logger.error('Failed to load notification preferences', error);
            return { success: false, error: error.message };
        }
    }

    async function requestPermission(): Promise<boolean> {
        update(state => ({ ...state, isLoading: true, error: null }));

        try {
            const permission = await Notification.requestPermission();

            update(state => ({
                ...state,
                permission,
                isLoading: false
            }));

            return permission === 'granted';
        } catch (error: any) {
            update(state => ({
                ...state,
                isLoading: false,
                error: 'Failed to request permission'
            }));
            return false;
        }
    }

    return {
        subscribe,

        async initialize() {
            const isSupported = checkSupport();
            const permission = isSupported ? Notification.permission : 'denied';

            update(state => ({
                ...state,
                isSupported,
                permission
            }));

            if (!isSupported) {
                return { success: false, error: 'Push notifications not supported' };
            }

            // Check if already subscribed
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.getSubscription();

                update(state => ({
                    ...state,
                    isSubscribed: !!subscription
                }));

                // Load preferences from server if subscribed
                if (subscription) {
                    await loadPreferences();
                }

                return { success: true };
            } catch (error: any) {
                logger.error('Failed to check subscription', error);
                return { success: false, error: error.message };
            }
        },

        requestPermission,

        async enablePush() {
            const state = get(store);

            if (!state.isSupported) {
                return { success: false, error: 'Push notifications not supported' };
            }

            if (state.permission !== 'granted') {
                const granted = await requestPermission();
                if (!granted) {
                    return { success: false, error: 'Permission denied' };
                }
            }

            update(s => ({ ...s, isLoading: true, error: null }));

            try {
                // Get VAPID public key from server
                const vapidResponse: any = await api.notifications.getVapidKey();
                const vapidPublicKey = vapidResponse.publicKey;

                if (!vapidPublicKey) {
                    throw new Error('VAPID key not configured on server');
                }

                // Subscribe to push manager
                const registration = await navigator.serviceWorker.ready;
                const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
                const pushSubscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: applicationServerKey.buffer as ArrayBuffer
                });

                // Send subscription to server
                const p256dhKey = pushSubscription.getKey('p256dh');
                const authKey = pushSubscription.getKey('auth');

                if (!p256dhKey || !authKey) {
                    throw new Error('Failed to get subscription keys');
                }

                await api.notifications.subscribe({
                    endpoint: pushSubscription.endpoint,
                    keys: {
                        p256dh: btoa(String.fromCharCode(...new Uint8Array(p256dhKey))),
                        auth: btoa(String.fromCharCode(...new Uint8Array(authKey)))
                    }
                });

                update(s => ({
                    ...s,
                    isSubscribed: true,
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                logger.error('Subscription failed', error);
                update(s => ({
                    ...s,
                    isLoading: false,
                    error: error.message || 'Subscription failed'
                }));
                return { success: false, error: error.message };
            }
        },

        async disablePush() {
            update(s => ({ ...s, isLoading: true, error: null }));

            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.getSubscription();

                if (subscription) {
                    await subscription.unsubscribe();
                    await api.notifications.unsubscribe();
                }

                update(s => ({
                    ...s,
                    isSubscribed: false,
                    isLoading: false
                }));

                return { success: true };
            } catch (error: any) {
                update(s => ({
                    ...s,
                    isLoading: false,
                    error: error.message || 'Unsubscribe failed'
                }));
                return { success: false, error: error.message };
            }
        },

        loadPreferences,

        async updatePreferences(prefs: Partial<NotificationPreferences>) {
            update(s => ({ ...s, isLoading: true, error: null }));

            try {
                await api.notifications.updatePreferences(prefs);
                update(s => ({
                    ...s,
                    preferences: { ...s.preferences, ...prefs },
                    isLoading: false
                }));
                return { success: true };
            } catch (error: any) {
                update(s => ({
                    ...s,
                    isLoading: false,
                    error: error.message || 'Failed to update preferences'
                }));
                return { success: false, error: error.message };
            }
        },

        async testNotification() {
            try {
                await api.notifications.test();
                return { success: true };
            } catch (error: any) {
                return { success: false, error: error.message };
            }
        }
    };
}

export const notificationsStore = createNotificationsStore();
