/**
 * II-Agent WebSocket Client
 * Handles WebSocket connection to II-Agent server (override via PUBLIC_II_AGENT_WS_URL).
 */

import { logger } from '$lib/utils/logger';
import type {
	RealtimeEvent,
	InitAgentMessage,
	QueryMessage,
	CancelMessage,
	EnhancePromptMessage,
	AgentConfig,
	EventType
} from './types';

const DEFAULT_II_AGENT_WS_URL =
	import.meta.env.PUBLIC_II_AGENT_WS_URL || 'ws://127.0.0.1:8765/ws';

type EventCallback = (event: RealtimeEvent) => void;
type ErrorCallback = (error: Error) => void;
type CloseCallback = () => void;

export class IIAgentClient {
	private ws: WebSocket | null = null;
	private wsUrl: string;
	private sessionUuid: string | null = null;
	private agentToken: string | null = null;
	private isConnected = false;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;

	// Event handlers
	private eventCallbacks: EventCallback[] = [];
	private errorCallbacks: ErrorCallback[] = [];
	private closeCallbacks: CloseCallback[] = [];

	// Heartbeat
	private heartbeatInterval: number | null = null;
	private heartbeatIntervalMs = 30000; // 30 seconds

	constructor(wsUrl?: string) {
		this.wsUrl = wsUrl || DEFAULT_II_AGENT_WS_URL;
	}

	/**
	 * Connect to II-Agent WebSocket server
	 */
	connect(sessionUuid: string, agentToken: string): Promise<void> {
		return new Promise((resolve, reject) => {
			this.sessionUuid = sessionUuid;
			this.agentToken = agentToken;

			const url = `${this.wsUrl}?session_uuid=${encodeURIComponent(sessionUuid)}`;

			try {
				this.ws = new WebSocket(url);

				this.ws.onopen = () => {
					logger.info('[IIAgentClient] WebSocket connected');
					this.isConnected = true;
					this.reconnectAttempts = 0;
					this.startHeartbeat();
					resolve();
				};

				this.ws.onmessage = (event) => {
					try {
						const data = JSON.parse(event.data);
						this.handleMessage(data);
					} catch (error) {
						logger.error('[IIAgentClient] Failed to parse message', error);
						this.notifyError(new Error('Failed to parse WebSocket message'));
					}
				};

				this.ws.onerror = (error) => {
					logger.error('[IIAgentClient] WebSocket error', error);
					this.notifyError(new Error('WebSocket connection error'));
				};

				this.ws.onclose = () => {
					logger.info('[IIAgentClient] WebSocket closed');
					this.isConnected = false;
					this.stopHeartbeat();
					this.notifyClose();

					// Attempt reconnection
					if (this.reconnectAttempts < this.maxReconnectAttempts) {
						this.reconnectAttempts++;
						logger.info(
							`[IIAgentClient] Reconnecting attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`
						);
						setTimeout(() => {
							if (this.sessionUuid && this.agentToken) {
								this.connect(this.sessionUuid, this.agentToken);
							}
						}, this.reconnectDelay * this.reconnectAttempts);
					}
				};
			} catch (error) {
				reject(error);
			}
		});
	}

	/**
	 * Disconnect from WebSocket server
	 */
	disconnect() {
		this.stopHeartbeat();
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.isConnected = false;
		this.sessionUuid = null;
		this.agentToken = null;
		this.reconnectAttempts = 0;
	}

	/**
	 * Initialize agent with model and configuration
	 */
	initAgent(config: AgentConfig): void {
		if (!this.isConnected || !this.ws) {
			throw new Error('WebSocket not connected');
		}

		const tool_args: Record<string, any> = {};

		// Add agent token for Focus Tools authentication
		if (this.agentToken) {
			tool_args.agent_token = this.agentToken;
		}

		// Add focus tools flag
		if (config.enable_focus_tools) {
			tool_args.enable_focus_tools = true;
		}

		// Add reviewer flag
		if (config.enable_reviewer) {
			tool_args.enable_reviewer = true;
		}

		const message: InitAgentMessage = {
			type: 'init_agent',
			content: {
				model_name: config.model_name,
				tool_args,
				thinking_tokens: config.thinking_tokens || 0
			}
		};

		this.send(message);
	}

	/**
	 * Send a query to the agent
	 */
	sendQuery(text: string, files: string[] = []): void {
		if (!this.isConnected || !this.ws) {
			throw new Error('WebSocket not connected');
		}

		const message: QueryMessage = {
			type: 'query',
			content: {
				text,
				files,
				resume: false
			}
		};

		this.send(message);
	}

	/**
	 * Cancel the current agent operation
	 */
	cancel(): void {
		if (!this.isConnected || !this.ws) {
			throw new Error('WebSocket not connected');
		}

		const message: CancelMessage = {
			type: 'cancel',
			content: {}
		};

		this.send(message);
	}

	/**
	 * Enhance prompt using II-Agent
	 */
	enhancePrompt(modelName: string, text: string, files: string[] = []): void {
		if (!this.isConnected || !this.ws) {
			throw new Error('WebSocket not connected');
		}

		const message: EnhancePromptMessage = {
			type: 'enhance_prompt',
			content: {
				model_name: modelName,
				text,
				files
			}
		};

		this.send(message);
	}

	/**
	 * Send a ping message
	 */
	ping(): void {
		if (!this.isConnected || !this.ws) {
			return;
		}

		this.send({
			type: 'ping',
			content: {}
		});
	}

	/**
	 * Register event callback
	 */
	onEvent(callback: EventCallback): () => void {
		this.eventCallbacks.push(callback);
		// Return unsubscribe function
		return () => {
			const index = this.eventCallbacks.indexOf(callback);
			if (index > -1) {
				this.eventCallbacks.splice(index, 1);
			}
		};
	}

	/**
	 * Register error callback
	 */
	onError(callback: ErrorCallback): () => void {
		this.errorCallbacks.push(callback);
		return () => {
			const index = this.errorCallbacks.indexOf(callback);
			if (index > -1) {
				this.errorCallbacks.splice(index, 1);
			}
		};
	}

	/**
	 * Register close callback
	 */
	onClose(callback: CloseCallback): () => void {
		this.closeCallbacks.push(callback);
		return () => {
			const index = this.closeCallbacks.indexOf(callback);
			if (index > -1) {
				this.closeCallbacks.splice(index, 1);
			}
		};
	}

	/**
	 * Get connection status
	 */
	getConnectionStatus(): boolean {
		return this.isConnected;
	}

	// Private methods

	private send(message: any): void {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
			throw new Error('WebSocket is not open');
		}

		const jsonString = JSON.stringify(message);
		this.ws.send(jsonString);
	}

	private handleMessage(data: any): void {
		// Expect RealtimeEvent format
		if (data.type && data.content !== undefined) {
			const event: RealtimeEvent = {
				type: data.type as EventType,
				content: data.content
			};
			this.notifyEvent(event);
		} else {
			logger.warn('[IIAgentClient] Received unexpected message format', { data });
		}
	}

	private notifyEvent(event: RealtimeEvent): void {
		this.eventCallbacks.forEach((callback) => {
			try {
				callback(event);
			} catch (error) {
				logger.error('[IIAgentClient] Event callback error', error);
			}
		});
	}

	private notifyError(error: Error): void {
		this.errorCallbacks.forEach((callback) => {
			try {
				callback(error);
			} catch (err) {
				logger.error('[IIAgentClient] Error callback error', err);
			}
		});
	}

	private notifyClose(): void {
		this.closeCallbacks.forEach((callback) => {
			try {
				callback();
			} catch (error) {
				logger.error('[IIAgentClient] Close callback error', error);
			}
		});
	}

	private startHeartbeat(): void {
		this.stopHeartbeat();
		this.heartbeatInterval = window.setInterval(() => {
			this.ping();
		}, this.heartbeatIntervalMs);
	}

	private stopHeartbeat(): void {
		if (this.heartbeatInterval !== null) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}
	}
}
