import { browser } from '$app/environment';
import { WS_URL } from '$lib/config/env';

type QueryValue = string | number | boolean | null | undefined;

export interface RealtimeClientOptions {
	path?: string;
	query?: Record<string, QueryValue>;
	protocols?: string | string[];
	reconnect?: boolean;
	reconnectDelayMs?: number;
	maxReconnectAttempts?: number;
	token?: string | (() => string | null | undefined);
}

type MessageHandler = (event: MessageEvent) => void;
type OpenHandler = (event: Event) => void;
type CloseHandler = (event: CloseEvent) => void;
type ErrorHandler = (event: Event) => void;

export class RealtimeClient {
	private socket: WebSocket | null = null;
	private reconnectAttempts = 0;
	private options: Required<Omit<RealtimeClientOptions, 'token'>> & { token?: string | (() => string | null | undefined) };
	private readonly messageHandlers = new Set<MessageHandler>();
	private readonly openHandlers = new Set<OpenHandler>();
	private readonly closeHandlers = new Set<CloseHandler>();
	private readonly errorHandlers = new Set<ErrorHandler>();
	private shouldReconnect: boolean;

	constructor(options: RealtimeClientOptions = {}) {
		this.options = {
			path: options.path ?? '',
			query: options.query ?? {},
			protocols: options.protocols ?? [],
			reconnect: options.reconnect ?? true,
			reconnectDelayMs: options.reconnectDelayMs ?? 2000,
			maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
			token: options.token
		};
		this.shouldReconnect = this.options.reconnect;
	}

	connect() {
		if (!browser) return;
		if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
			return;
		}

	const url = this.buildUrl();
	this.shouldReconnect = this.options.reconnect;
		this.socket = new WebSocket(url, this.options.protocols);

		this.socket.addEventListener('open', (event) => {
			this.reconnectAttempts = 0;
			for (const handler of this.openHandlers) {
				handler(event);
			}
		});

		this.socket.addEventListener('message', (event) => {
			for (const handler of this.messageHandlers) {
				handler(event);
			}
		});

		this.socket.addEventListener('close', (event) => {
			for (const handler of this.closeHandlers) {
				handler(event);
			}
			if (this.options.reconnect) {
				this.scheduleReconnect();
			}
		});

		this.socket.addEventListener('error', (event) => {
			for (const handler of this.errorHandlers) {
				handler(event);
			}
		});
	}

	disconnect() {
		this.shouldReconnect = false;
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
	}

	setToken(token: string | (() => string | null | undefined) | undefined) {
		this.options = { ...this.options, token };
	}

	setQuery(query: Record<string, QueryValue>) {
		this.options = { ...this.options, query: { ...query } };
	}

	updateQuery(query: Record<string, QueryValue>) {
		this.options = { ...this.options, query: { ...this.options.query, ...query } };
	}

	setPath(path: string) {
		this.options = { ...this.options, path };
	}

	send(data: string | ArrayBufferLike | Blob | ArrayBufferView) {
		if (this.socket?.readyState === WebSocket.OPEN) {
			this.socket.send(data);
		} else {
			console.warn('WebSocket not connected. Message not sent.');
		}
	}

	onMessage(handler: MessageHandler) {
		this.messageHandlers.add(handler);
		return () => this.messageHandlers.delete(handler);
	}

	onOpen(handler: OpenHandler) {
		this.openHandlers.add(handler);
		return () => this.openHandlers.delete(handler);
	}

	onClose(handler: CloseHandler) {
		this.closeHandlers.add(handler);
		return () => this.closeHandlers.delete(handler);
	}

	onError(handler: ErrorHandler) {
		this.errorHandlers.add(handler);
		return () => this.errorHandlers.delete(handler);
	}

	private scheduleReconnect() {
		if (!this.shouldReconnect || !this.options.reconnect) return;
		if (this.reconnectAttempts >= this.options.maxReconnectAttempts) return;

		this.reconnectAttempts += 1;
		setTimeout(() => this.connect(), this.options.reconnectDelayMs);
	}

	private buildUrl() {
		const { path, query, token } = this.options;
		const normalizedPath = path?.startsWith('/') ? path : `/${path ?? ''}`;
		const base = `${WS_URL}${normalizedPath}`;
		const params = new URLSearchParams();

		if (query) {
			for (const [key, value] of Object.entries(query)) {
				if (value === null || value === undefined) continue;
				params.set(key, String(value));
			}
		}

		const resolvedToken = typeof token === 'function' ? token() : token;
		if (resolvedToken) {
			params.set('token', resolvedToken);
		}

		const queryString = params.toString();
		return queryString.length > 0 ? `${base}?${queryString}` : base;
	}
}
