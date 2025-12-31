type SyncMessage = {
	type: 'auth_updated' | 'auth_logout' | 'session_updated' | 'session_ended';
	payload: any;
	timestamp: number;
	tabId: string;
};

type SyncListener = (message: SyncMessage) => void;

class CrossTabSyncService {
	private channel: BroadcastChannel | null = null;
	private listeners: Map<string, Set<SyncListener>> = new Map();
	private tabId: string;
	private isSupported: boolean;

	constructor() {
		this.tabId = this.generateTabId();
		this.isSupported = typeof BroadcastChannel !== 'undefined';

		if (this.isSupported) {
			this.channel = new BroadcastChannel('operator-demo-sync');
			this.setupMessageHandler();
		}
	}

	private generateTabId(): string {
		return `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}

	private setupMessageHandler(): void {
		if (!this.channel) return;

		this.channel.onmessage = (event: MessageEvent<SyncMessage>) => {
			const message = event.data;

			// Ignore messages from same tab
			if (message.tabId === this.tabId) return;

			// Notify listeners
			const listeners = this.listeners.get(message.type);
			if (listeners) {
				listeners.forEach((listener) => listener(message));
			}
		};
	}

	broadcast(type: SyncMessage['type'], payload: any): void {
		if (!this.channel) {
			console.warn('BroadcastChannel not supported');
			return;
		}

		const message: SyncMessage = {
			type,
			payload,
			timestamp: Date.now(),
			tabId: this.tabId
		};

		this.channel.postMessage(message);
	}

	subscribe(type: SyncMessage['type'], listener: SyncListener): () => void {
		if (!this.listeners.has(type)) {
			this.listeners.set(type, new Set());
		}

		this.listeners.get(type)!.add(listener);

		// Return unsubscribe function
		return () => {
			this.listeners.get(type)?.delete(listener);
		};
	}

	close(): void {
		if (this.channel) {
			this.channel.close();
			this.channel = null;
		}
		this.listeners.clear();
	}

	isAvailable(): boolean {
		return this.isSupported && this.channel !== null;
	}
}

export const crossTabSync = new CrossTabSyncService();

// Cleanup on page unload
if (typeof window !== 'undefined') {
	window.addEventListener('beforeunload', () => {
		crossTabSync.close();
	});
}
