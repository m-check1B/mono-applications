/**
 * Enhanced WebSocket Client with Heartbeat, Retry/Backoff, and Connection Status
 * 
 * Features:
 * - Automatic heartbeat/ping-pong for connection health
 * - Exponential backoff reconnection with jitter
 * - Connection status events and metrics
 * - Graceful degradation and error handling
 * - Connection quality monitoring
 */

import { logger } from '$lib/utils/logger';

export interface ConnectionMetrics {
	connectedAt: number | null;
	lastPingAt: number | null;
	lastPongAt: number | null;
	reconnectAttempts: number;
	totalDisconnections: number;
	averageLatency: number;
	connectionQuality: 'excellent' | 'good' | 'fair' | 'poor' | 'disconnected';
}

export interface ConnectionStatus {
	state: 'connecting' | 'connected' | 'disconnecting' | 'disconnected' | 'reconnecting' | 'error';
	metrics: ConnectionMetrics;
	isHealthy: boolean;
}

export interface EnhancedWebSocketCallbacks {
	// Connection lifecycle
	onConnecting?: () => void;
	onConnected?: (status: ConnectionStatus) => void;
	onDisconnecting?: () => void;
	onDisconnected?: (status: ConnectionStatus) => void;
	onReconnecting?: (attempt: number, maxAttempts: number) => void;
	onError?: (error: Error, status: ConnectionStatus) => void;
	
	// Connection health
	onHeartbeat?: (latency: number) => void;
	onConnectionQualityChange?: (quality: ConnectionMetrics['connectionQuality']) => void;
	onUnhealthyConnection?: (status: ConnectionStatus) => void;
	
	// Message handling (inherited from AIWebSocketCallbacks)
	onMessage?: (message: any) => void;
	onBinaryMessage?: (data: ArrayBuffer) => void;
}

export interface EnhancedWebSocketOptions {
	// Connection settings
	url?: string;
	protocols?: string[];
	
	// Heartbeat settings
	heartbeatInterval?: number; // ms
	heartbeatTimeout?: number; // ms
	maxMissedHeartbeats?: number;
	
	// Reconnection settings
	maxReconnectAttempts?: number;
	initialReconnectDelay?: number; // ms
	maxReconnectDelay?: number; // ms
	reconnectBackoffFactor?: number;
	jitterFactor?: number; // 0-1, adds randomness to prevent thundering herd
	
	// Quality monitoring
	latencyThresholds?: {
		excellent: number;
		good: number;
		fair: number;
		poor: number;
	};
	
	// Health monitoring
	unhealthyThreshold?: number; // consecutive failures before marking unhealthy
	healthCheckInterval?: number; // ms
}

export class EnhancedWebSocketClient {
	private ws: WebSocket | null = null;
	private sessionId: string;
	private callbacks: EnhancedWebSocketCallbacks;
	private options: Required<EnhancedWebSocketOptions>;
	
	// Connection state
	private status: ConnectionStatus;
	private isIntentionallyClosed = false;
	private reconnectTimer: number | null = null;
	private heartbeatTimer: number | null = null;
	private healthCheckTimer: number | null = null;
	
	// Heartbeat state
	private pingStartTime = 0;
	private missedHeartbeats = 0;
	private latencyHistory: number[] = [];
	private maxLatencyHistory = 10;
	
	// Health monitoring
	private consecutiveFailures = 0;
	
	constructor(sessionId: string, callbacks: EnhancedWebSocketCallbacks, options: EnhancedWebSocketOptions = {}) {
		this.sessionId = sessionId;
		this.callbacks = callbacks;
		
		// Default options
		this.options = {
			url: this.getDefaultUrl(),
			protocols: [],
			heartbeatInterval: 30000, // 30 seconds
			heartbeatTimeout: 5000, // 5 seconds
			maxMissedHeartbeats: 3,
			maxReconnectAttempts: 10,
			initialReconnectDelay: 1000, // 1 second
			maxReconnectDelay: 30000, // 30 seconds
			reconnectBackoffFactor: 2,
			jitterFactor: 0.1,
			latencyThresholds: {
				excellent: 50,
				good: 150,
				fair: 300,
				poor: 1000
			},
			unhealthyThreshold: 3,
			healthCheckInterval: 10000, // 10 seconds
			...options
		};
		
		// Initialize status
		this.status = {
			state: 'disconnected',
			metrics: {
				connectedAt: null,
				lastPingAt: null,
				lastPongAt: null,
				reconnectAttempts: 0,
				totalDisconnections: 0,
				averageLatency: 0,
				connectionQuality: 'disconnected'
			},
			isHealthy: false
		};
	}
	
	/**
	 * Get default WebSocket URL based on current environment
	 */
	private getDefaultUrl(): string {
		const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsHost = window.location.hostname;
		const wsPort = import.meta.env.VITE_BACKEND_PORT || '8000';
		return `${wsProtocol}//${wsHost}:${wsPort}/ws/${this.sessionId}`;
	}
	
	/**
	 * Connect to WebSocket with enhanced features
	 */
	connect(): void {
		if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
			logger.warn('WebSocket already connected or connecting');
			return;
		}
		
		this.updateStatus('connecting');
		this.callbacks.onConnecting?.();
		
		try {
			logger.info('Connecting to enhanced WebSocket', { url: this.options.url });
			this.ws = new WebSocket(this.options.url, this.options.protocols);
			
			this.setupEventHandlers();
		} catch (error) {
			logger.error('Failed to create WebSocket', error as Error);
			this.handleError(error as Error);
		}
	}
	
	/**
	 * Setup WebSocket event handlers
	 */
	private setupEventHandlers(): void {
		if (!this.ws) return;
		
		this.ws.onopen = (event) => {
			logger.info('Enhanced WebSocket connected');
			this.status.metrics.connectedAt = Date.now();
			this.status.metrics.reconnectAttempts = 0;
			this.consecutiveFailures = 0;
			this.missedHeartbeats = 0;
			
			this.updateStatus('connected');
			this.startHeartbeat();
			this.startHealthCheck();
			this.callbacks.onConnected?.(this.getStatus());
		};
		
		this.ws.onmessage = (event) => {
			try {
				// Handle heartbeat responses
				if (this.handleHeartbeatResponse(event.data)) {
					return;
				}
				
				// Handle regular messages
				if (event.data instanceof ArrayBuffer) {
					this.callbacks.onBinaryMessage?.(event.data);
				} else {
					const message = JSON.parse(event.data);
					this.callbacks.onMessage?.(message);
				}
				
				// Reset failure counter on successful message
				this.consecutiveFailures = 0;
			} catch (error) {
				logger.error('Failed to parse WebSocket message', error as Error);
				this.consecutiveFailures++;
			}
		};
		
		this.ws.onerror = (event) => {
			logger.error('Enhanced WebSocket error', event as unknown);
			this.handleError(new Error('WebSocket connection error'));
		};
		
		this.ws.onclose = (event) => {
			logger.info('Enhanced WebSocket closed', { code: event.code, reason: event.reason });
			this.stopHeartbeat();
			this.stopHealthCheck();
			
			this.status.metrics.totalDisconnections++;
			this.updateStatus('disconnected');
			this.callbacks.onDisconnected?.(this.getStatus());
			
			// Attempt reconnection if not intentionally closed
			if (!this.isIntentionallyClosed) {
				this.attemptReconnection();
			}
		};
	}
	
	/**
	 * Handle heartbeat ping/pong responses
	 */
	private handleHeartbeatResponse(data: string | ArrayBuffer): boolean {
		if (typeof data !== 'string') return false;
		
		try {
			const message = JSON.parse(data);
			if (message.type === 'pong') {
				const latency = Date.now() - this.pingStartTime;
				this.recordLatency(latency);
				this.status.metrics.lastPongAt = Date.now();
				this.missedHeartbeats = 0;
				this.callbacks.onHeartbeat?.(latency);
				return true;
			}
		} catch {
			// Not a JSON message, continue with normal processing
		}
		
		return false;
	}
	
	/**
	 * Start heartbeat/ping-pong mechanism
	 */
	private startHeartbeat(): void {
		this.stopHeartbeat(); // Clear any existing timer
		
		this.heartbeatTimer = window.setInterval(() => {
			if (this.ws?.readyState === WebSocket.OPEN) {
				this.pingStartTime = Date.now();
				this.status.metrics.lastPingAt = this.pingStartTime;
				
				try {
					this.ws.send(JSON.stringify({ type: 'ping', timestamp: this.pingStartTime }));
					
					// Check for missed heartbeat
					setTimeout(() => {
						if (this.status.metrics.lastPongAt && this.status.metrics.lastPongAt < this.pingStartTime) {
							this.missedHeartbeats++;
							if (this.missedHeartbeats >= this.options.maxMissedHeartbeats) {
								logger.warn('Too many missed heartbeats, closing connection');
								this.ws?.close(1000, 'Missed heartbeats');
							}
						}
					}, this.options.heartbeatTimeout);
				} catch (error) {
					logger.error('Failed to send heartbeat', error as Error);
					this.consecutiveFailures++;
				}
			}
		}, this.options.heartbeatInterval);
	}
	
	/**
	 * Stop heartbeat mechanism
	 */
	private stopHeartbeat(): void {
		if (this.heartbeatTimer) {
			clearInterval(this.heartbeatTimer);
			this.heartbeatTimer = null;
		}
	}
	
	/**
	 * Start connection health monitoring
	 */
	private startHealthCheck(): void {
		this.stopHealthCheck(); // Clear any existing timer
		
		this.healthCheckTimer = window.setInterval(() => {
			this.updateConnectionQuality();
			
			if (!this.isHealthy()) {
				this.callbacks.onUnhealthyConnection?.(this.getStatus());
			}
		}, this.options.healthCheckInterval);
	}
	
	/**
	 * Stop health monitoring
	 */
	private stopHealthCheck(): void {
		if (this.healthCheckTimer) {
			clearInterval(this.healthCheckTimer);
			this.healthCheckTimer = null;
		}
	}
	
	/**
	 * Record latency and update metrics
	 */
	private recordLatency(latency: number): void {
		this.latencyHistory.push(latency);
		if (this.latencyHistory.length > this.maxLatencyHistory) {
			this.latencyHistory.shift();
		}
		
		// Calculate average latency
		this.status.metrics.averageLatency = this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length;
	}
	
	/**
	 * Update connection quality based on metrics
	 */
	private updateConnectionQuality(): void {
		const { averageLatency } = this.status.metrics;
		const { excellent, good, fair, poor } = this.options.latencyThresholds;
		
		let quality: ConnectionMetrics['connectionQuality'];
		if (averageLatency <= excellent) {
			quality = 'excellent';
		} else if (averageLatency <= good) {
			quality = 'good';
		} else if (averageLatency <= fair) {
			quality = 'fair';
		} else if (averageLatency <= poor) {
			quality = 'poor';
		} else {
			quality = 'disconnected';
		}
		
		if (quality !== this.status.metrics.connectionQuality) {
			this.status.metrics.connectionQuality = quality;
			this.callbacks.onConnectionQualityChange?.(quality);
		}
	}
	
	/**
	 * Attempt reconnection with exponential backoff
	 */
	private attemptReconnection(): void {
		if (this.status.metrics.reconnectAttempts >= this.options.maxReconnectAttempts) {
			logger.error('Max reconnection attempts reached');
			this.updateStatus('error');
			return;
		}
		
		this.status.metrics.reconnectAttempts++;
		this.updateStatus('reconnecting');
		
		const baseDelay = Math.min(
			this.options.initialReconnectDelay * Math.pow(this.options.reconnectBackoffFactor, this.status.metrics.reconnectAttempts - 1),
			this.options.maxReconnectDelay
		);
		
		// Add jitter to prevent thundering herd
		const jitter = baseDelay * this.options.jitterFactor * Math.random();
		const delay = baseDelay + jitter;
		
		logger.info('Reconnecting WebSocket', {
			delay: Math.round(delay),
			attempt: this.status.metrics.reconnectAttempts,
			maxAttempts: this.options.maxReconnectAttempts
		});
		this.callbacks.onReconnecting?.(this.status.metrics.reconnectAttempts, this.options.maxReconnectAttempts);
		
		this.reconnectTimer = window.setTimeout(() => {
			this.connect();
		}, delay);
	}
	
	/**
	 * Handle errors and update status
	 */
	private handleError(error: Error): void {
		this.consecutiveFailures++;
		this.updateStatus('error');
		this.callbacks.onError?.(error, this.getStatus());
	}
	
	/**
	 * Update connection status
	 */
	private updateStatus(state: ConnectionStatus['state']): void {
		this.status.state = state;
		this.status.isHealthy = this.isHealthy();
	}
	
	/**
	 * Check if connection is healthy
	 */
	private isHealthy(): boolean {
		return (
			this.status.state === 'connected' &&
			this.consecutiveFailures < this.options.unhealthyThreshold &&
			this.missedHeartbeats < this.options.maxMissedHeartbeats &&
			this.status.metrics.connectionQuality !== 'disconnected'
		);
	}
	
	/**
	 * Get current connection status
	 */
	getStatus(): ConnectionStatus {
		return { ...this.status };
	}
	
	/**
	 * Send message with connection check
	 */
	send(data: string | ArrayBuffer): boolean {
		if (this.ws?.readyState === WebSocket.OPEN) {
			try {
				this.ws.send(data);
				return true;
			} catch (error) {
				logger.error('Failed to send message', error as Error);
				this.consecutiveFailures++;
				return false;
			}
		}
		return false;
	}
	
	/**
	 * Send JSON message
	 */
	sendJSON(data: any): boolean {
		return this.send(JSON.stringify(data));
	}
	
	/**
	 * Request sentiment analysis (compatibility with AIWebSocketClient)
	 */
	analyzeSentiment(text: string, speaker: string): void {
		this.sendJSON({
			type: 'sentiment',
			text,
			speaker
		});
	}
	
	/**
	 * Request agent assistance (compatibility with AIWebSocketClient)
	 */
	requestAssistance(transcript: string, context: Record<string, unknown> = {}): void {
		this.sendJSON({
			type: 'assistance',
			transcript,
			context
		});
	}
	
	/**
	 * Send transcription data (compatibility with AIWebSocketClient)
	 */
	sendTranscription(text: string, speaker: 'agent' | 'customer' | 'system', confidence = 1.0, isFinal = true): void {
		this.sendJSON({
			type: 'transcription',
			text,
			speaker,
			confidence,
			is_final: isFinal
		});
	}
	
	/**
	 * Check if WebSocket is connected
	 */
	isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN && this.status.state === 'connected';
	}
	
	/**
	 * Close the WebSocket connection
	 */
	disconnect(): void {
		this.isIntentionallyClosed = true;
		this.updateStatus('disconnecting');
		this.callbacks.onDisconnecting?.();
		
		// Clear timers
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		this.stopHeartbeat();
		this.stopHealthCheck();
		
		// Close WebSocket
		if (this.ws) {
			this.ws.close(1000, 'Intentionally closed');
			this.ws = null;
		}
		
		this.updateStatus('disconnected');
	}
}

/**
 * Factory function to create enhanced WebSocket client
 */
export function createEnhancedWebSocket(
	sessionId: string, 
	callbacks: EnhancedWebSocketCallbacks, 
	options?: EnhancedWebSocketOptions
): EnhancedWebSocketClient {
	const client = new EnhancedWebSocketClient(sessionId, callbacks, options);
	client.connect();
	return client;
}
