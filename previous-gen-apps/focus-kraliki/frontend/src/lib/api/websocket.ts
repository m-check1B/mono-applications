/**
 * WebSocket Client for Real-Time Updates
 * Part of Gap #6: WebSocket real-time updates
 */

import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { toast } from '$lib/stores/toast';
import { contextPanelStore, type PanelType } from '$lib/stores/contextPanel';
import { logger } from '$lib/utils/logger';

interface WebSocketMessage {
	type: string;
	entity?: string;
	data?: any;
	timestamp?: string;
}

export class WebSocketClient {
	private ws: WebSocket | null = null;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private heartbeatInterval: number | null = null;
	private isIntentionallyClosed = false;

	/**
	 * Connect to WebSocket server
	 */
	connect() {
		// Guard against SSR
		if (typeof window === 'undefined') {
			logger.warn('[WebSocket] Skipping connection (SSR)');
			return;
		}

		const auth = get(authStore);

		if (!auth.token || !auth.user?.id) {
			logger.warn('[WebSocket] No auth token, skipping connection');
			return;
		}

		const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const apiUrl = import.meta.env.PUBLIC_API_URL;
		if (!apiUrl) {
			logger.error('[WebSocket] PUBLIC_API_URL is required');
			toast.error('Real-time updates unavailable (PUBLIC_API_URL missing)', 5000);
			return;
		}
		if (!/^https?:\/\//.test(apiUrl)) {
			logger.error('[WebSocket] PUBLIC_API_URL must include http(s) scheme');
			toast.error('Real-time updates unavailable (PUBLIC_API_URL invalid)', 5000);
			return;
		}
		const wsHost = apiUrl.replace(/^https?:\/\//, '');
		// WebSocket endpoint includes user_id in path as expected by backend
		const wsUrl = `${wsProtocol}//${wsHost}/ws/${auth.user.id}?token=${auth.token}`;

		logger.info('[WebSocket] Connecting to:', { url: wsUrl.replace(/token=.*/, 'token=***') });
		this.ws = new WebSocket(wsUrl);

		this.ws.onopen = () => this.handleOpen();
		this.ws.onmessage = (event) => this.handleMessage(event);
		this.ws.onerror = (error) => this.handleError(error);
		this.ws.onclose = () => this.handleClose();
	}

	/**
	 * Disconnect from WebSocket server
	 */
	disconnect() {
		this.isIntentionallyClosed = true;
		this.reconnectAttempts = 0;

		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}

		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}

		logger.info('[WebSocket] Disconnected');
	}

	/**
	 * Send message to server
	 */
	send(message: any) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(message));
		} else {
			logger.warn('[WebSocket] Cannot send, not connected');
		}
	}

	/**
	 * Check if connected
	 */
	isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN;
	}

	// ========== Private Handlers ==========

	private handleOpen() {
		logger.info('[WebSocket] Connected');
		this.reconnectAttempts = 0;
		this.isIntentionallyClosed = false;

		// Start heartbeat
		this.heartbeatInterval = setInterval(() => {
			this.send({ type: 'ping' });
		}, 30000) as unknown as number;

		toast.success('Real-time updates connected', 2000);
	}

	private handleMessage(event: MessageEvent) {
		try {
			const message: WebSocketMessage = JSON.parse(event.data);
			logger.debug('[WebSocket] Received:', { message });

			switch (message.type) {
				case 'item_created':
					this.handleItemCreated(message);
					break;
				case 'task_update':
					this.handleTaskUpdate(message);
					break;
				case 'notification':
					this.handleNotification(message);
					break;
				case 'pong':
					// Heartbeat response
					break;
				default:
					logger.info('[WebSocket] Unknown message type:', { type: message.type });
			}
		} catch (error) {
			logger.error('[WebSocket] Failed to parse message:', error);
		}
	}

	private handleError(error: Event) {
		logger.error('[WebSocket] Error:', error);
		toast.error('Real-time connection error', 3000);
	}

	private handleClose() {
		logger.info('[WebSocket] Connection closed');

		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}

		// Attempt reconnect (unless intentionally closed or max attempts reached)
		if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
			this.reconnectAttempts++;
			const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
			
			logger.info(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
			
			setTimeout(() => this.connect(), delay);
		} else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			logger.warn('[WebSocket] Max reconnect attempts reached');
			toast.warning('Real-time updates disconnected', 5000);
		}
	}

	// ========== Message Handlers ==========

	private handleItemCreated(message: WebSocketMessage) {
		const { entity, data } = message;
		
		if (!entity || !data) return;

		// Show toast notification
		const entityLabel = this.getEntityLabel(entity);
		toast.success(`${entityLabel} created: ${data.title}`, 3000);

		// Refresh relevant panel
		const panelType = this.getPanelType(entity);
		if (panelType) {
			contextPanelStore.refresh(panelType as PanelType);
		}
	}

	private handleTaskUpdate(message: WebSocketMessage) {
		const { data } = message;
		
		if (!data) return;

		toast.info(`Task updated: ${data.title}`, 2000);
		contextPanelStore.refresh('tasks');
	}

	private handleNotification(message: WebSocketMessage) {
		const { data } = message;
		
		if (!data) return;

		const type = data.type || 'info';
		const content = data.message || 'Notification received';
		
		toast[type as 'info' | 'success' | 'warning' | 'error'](content, 4000);
	}

	// ========== Utility Methods ==========

	private getEntityLabel(entity: string): string {
		const labels: Record<string, string> = {
			task: 'Task',
			knowledge: 'Knowledge Item',
			event: 'Calendar Event',
			project: 'Project'
		};
		return labels[entity] || entity;
	}

	private getPanelType(entity: string): string | null {
		const panelMap: Record<string, string> = {
			task: 'tasks',
			knowledge: 'knowledge',
			event: 'calendar',
			project: 'projects'
		};
		return panelMap[entity] || null;
	}
}

// Export singleton instance
let wsClient: WebSocketClient | null = null;

export function getWebSocketClient(): WebSocketClient {
	if (!wsClient) {
		wsClient = new WebSocketClient();
	}
	return wsClient;
}

export function connectWebSocket() {
	const client = getWebSocketClient();
	client.connect();
}

export function disconnectWebSocket() {
	if (wsClient) {
		wsClient.disconnect();
		wsClient = null;
	}
}
