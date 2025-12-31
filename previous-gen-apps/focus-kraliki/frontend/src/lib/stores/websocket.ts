/**
 * WebSocket Store
 * Manages real-time updates from the backend
 */

import { writable, get } from 'svelte/store';
import { authStore } from './auth';
import { tasksStore } from './tasks';
import { notificationsStore } from './notifications';
import { logger } from '$lib/utils/logger';
import { browser } from '$app/environment';

export interface WebSocketState {
    isConnected: boolean;
    isConnecting: boolean;
    error: string | null;
    lastMessage: any | null;
}

const initialState: WebSocketState = {
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null
};

function createWebSocketStore() {
    const { subscribe, set, update } = writable<WebSocketState>(initialState);
    let socket: WebSocket | null = null;
    let reconnectTimeout: any = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;

    function connect() {
        if (!browser) return;
        
        const auth = get(authStore);
        if (!auth.isAuthenticated || !auth.user || !auth.token) {
            logger.debug('[WS] Not authenticated, skipping connection');
            return;
        }

        const userId = auth.user.id;
        const token = auth.token;

        // Don't connect if already connected or connecting
        const state = get({ subscribe });
        if (state.isConnected || state.isConnecting) return;

        update(s => ({ ...s, isConnecting: true, error: null }));

        // Build WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In development, the API might be on port 8000 while frontend is on 5173
        // We need to use the PUBLIC_API_URL or similar logic
        // For now, assume API is on the same host or use a configurable URL
        const apiUrl = import.meta.env.PUBLIC_API_URL || '';
        let wsHost = window.location.host;
        
        if (apiUrl) {
            try {
                const url = new URL(apiUrl);
                wsHost = url.host;
            } catch (e) {
                logger.error('[WS] Invalid PUBLIC_API_URL', e);
            }
        }

        const wsUrl = `${protocol}//${wsHost}/ws/${userId}?token=${token}`;
        
        logger.info(`[WS] Connecting to ${protocol}//${wsHost}/ws/${userId}`);

        try {
            socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                logger.info('[WS] Connected');
                update(s => ({ ...s, isConnected: true, isConnecting: false, error: null }));
                reconnectAttempts = 0;
            };

            socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    update(s => ({ ...s, lastMessage: message }));
                    handleMessage(message);
                } catch (e) {
                    logger.error('[WS] Failed to parse message', e);
                }
            };

            socket.onclose = (event) => {
                logger.warn(`[WS] Disconnected: ${event.code} ${event.reason}`);
                update(s => ({ ...s, isConnected: false, isConnecting: false }));
                socket = null;

                // Attempt reconnect if not a clean close
                if (event.code !== 1000 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    logger.info(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1})`);
                    reconnectTimeout = setTimeout(() => {
                        reconnectAttempts++;
                        connect();
                    }, delay);
                }
            };

            socket.onerror = (error) => {
                logger.error('[WS] Error', error);
                update(s => ({ ...s, error: 'WebSocket connection error' }));
            };

        } catch (e: any) {
            logger.error('[WS] Exception during connection', e);
            update(s => ({ ...s, isConnecting: false, error: e.message }));
        }
    }

    function disconnect() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
        }

        if (socket) {
            socket.close(1000, 'User logged out');
            socket = null;
        }

        update(s => ({ ...s, isConnected: false, isConnecting: false }));
    }

    function handleMessage(message: any) {
        logger.debug('[WS] Message received:', message);

        switch (message.type) {
            case 'task_update':
            case 'task_created':
            case 'task_updated':
            case 'task_completed':
                // Refresh tasks if we receive a task-related event
                tasksStore.loadTasks();
                break;
            case 'notification':
                // Could be used to trigger a toast
                break;
            case 'item_created':
            case 'item_updated':
            case 'item_deleted':
                // Refresh knowledge items if needed
                break;
            case 'chat_message':
                // Could be used for real-time chat updates
                break;
            case 'pong':
                // Keep-alive response
                break;
        }
    }

    function sendMessage(type: string, data: any) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type,
                data,
                timestamp: new Date().toISOString()
            }));
            return true;
        }
        return false;
    }

    return {
        subscribe,
        connect,
        disconnect,
        sendMessage,
        ping: () => sendMessage('ping', {})
    };
}

export const websocketStore = createWebSocketStore();
