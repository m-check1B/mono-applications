/**
 * AI Services WebSocket Client
 *
 * Provides real-time communication with backend AI services:
 * - Transcription streaming
 * - Sentiment analysis updates
 * - Agent assistance suggestions
 */

import { logger } from '$lib/utils/logger';

export interface TranscriptionMessage {
	type: 'transcription';
	data: {
		id: string;
		session_id: string;
		text: string;
		speaker: 'agent' | 'customer' | 'system';
		confidence: number;
		is_final: boolean;
		timestamp: string;
	};
}

export interface SentimentMessage {
	type: 'sentiment';
	data: {
		id: string;
		session_id: string;
		sentiment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';
		emotions: string[];
		confidence: number;
		polarity_score: number;
		intensity: number;
		timestamp: string;
		text_analyzed: string;
		speaker: string;
	};
}

export interface AssistanceMessage {
	type: 'assistance';
	data: Array<{
		id: string;
		session_id: string;
		type: 'suggested_response' | 'knowledge_article' | 'compliance_warning' | 'performance_tip' | 'escalation_guide';
		priority: 'low' | 'medium' | 'high' | 'urgent';
		title: string;
		content: string;
		confidence: number;
		timestamp: string;
		context: Record<string, unknown>;
	}>;
}

export type AIMessage = TranscriptionMessage | SentimentMessage | AssistanceMessage;

export interface AIWebSocketCallbacks {
	onTranscription?: (data: TranscriptionMessage['data']) => void;
	onSentiment?: (data: SentimentMessage['data']) => void;
	onAssistance?: (data: AssistanceMessage['data']) => void;
	onError?: (error: Event) => void;
	onClose?: (event: CloseEvent) => void;
	onOpen?: (event: Event) => void;
}

export class AIWebSocketClient {
	private ws: WebSocket | null = null;
	private sessionId: string;
	private callbacks: AIWebSocketCallbacks;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private isIntentionallyClosed = false;

	constructor(sessionId: string, callbacks: AIWebSocketCallbacks) {
		this.sessionId = sessionId;
		this.callbacks = callbacks;
	}

	/**
	 * Connect to the AI services WebSocket
	 */
	connect(): void {
		const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsHost = window.location.hostname;
		const wsPort = import.meta.env.VITE_BACKEND_PORT || '8000';
		const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ai/ws/${this.sessionId}`;

		logger.info('Connecting to AI WebSocket', { wsUrl });
		this.isIntentionallyClosed = false;

		try {
			this.ws = new WebSocket(wsUrl);

			this.ws.onopen = (event) => {
				logger.info('AI WebSocket connected');
				this.reconnectAttempts = 0;
				this.callbacks.onOpen?.(event);
			};

			this.ws.onmessage = (event) => {
				try {
					const message: AIMessage = JSON.parse(event.data);
					this.handleMessage(message);
				} catch (error) {
					logger.error('Failed to parse AI WebSocket message', error as Error);
				}
			};

			this.ws.onerror = (event) => {
				logger.error('AI WebSocket error', event as unknown);
				this.callbacks.onError?.(event);
			};

			this.ws.onclose = (event) => {
				logger.info('AI WebSocket closed', { code: event.code, reason: event.reason });
				this.callbacks.onClose?.(event);

				// Attempt reconnection if not intentionally closed
				if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
					this.reconnectAttempts++;
					const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
					logger.info('Reconnecting AI WebSocket', {
						delay,
						attempt: this.reconnectAttempts,
						maxAttempts: this.maxReconnectAttempts
					});
					setTimeout(() => this.connect(), delay);
				}
			};
		} catch (error) {
			logger.error('Failed to create AI WebSocket', error as Error);
		}
	}

	/**
	 * Handle incoming WebSocket messages
	 */
	private handleMessage(message: AIMessage): void {
		switch (message.type) {
			case 'transcription':
				this.callbacks.onTranscription?.(message.data);
				break;
			case 'sentiment':
				this.callbacks.onSentiment?.(message.data);
				break;
			case 'assistance':
				this.callbacks.onAssistance?.(message.data);
				break;
			default:
				logger.warn('Unknown AI message type', { message });
		}
	}

	/**
	 * Send transcription data to backend
	 */
	sendTranscription(text: string, speaker: 'agent' | 'customer' | 'system', confidence = 1.0, isFinal = true): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify({
				type: 'transcription',
				text,
				speaker,
				confidence,
				is_final: isFinal
			}));
		}
	}

	/**
	 * Request sentiment analysis
	 */
	analyzeSentiment(text: string, speaker: string): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify({
				type: 'sentiment',
				text,
				speaker
			}));
		}
	}

	/**
	 * Request agent assistance
	 */
	requestAssistance(transcript: string, context: Record<string, unknown> = {}): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify({
				type: 'assistance',
				transcript,
				context
			}));
		}
	}

	/**
	 * Check if WebSocket is connected
	 */
	isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN;
	}

	/**
	 * Close the WebSocket connection
	 */
	disconnect(): void {
		this.isIntentionallyClosed = true;
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
	}
}

/**
 * Create and manage AI WebSocket connection
 */
export function createAIWebSocket(sessionId: string, callbacks: AIWebSocketCallbacks): AIWebSocketClient {
	const client = new AIWebSocketClient(sessionId, callbacks);
	client.connect();
	return client;
}
