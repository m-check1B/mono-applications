import { browser } from '$app/environment';

type WSMessage =
  | { type: 'call:created'; call: any }
  | { type: 'call:updated'; call: any }
  | { type: 'call:ended'; callId: string }
  | { type: 'agent:status'; agentId: string; status: string }
  | { type: 'transcript:chunk'; callId: string; text: string; speaker: string }
  | { type: 'sentiment:update'; callId: string; sentiment: any }
  | { type: 'queue:updated'; queue: any };

type MessageHandler = (message: WSMessage) => void;

class WebSocketStore {
  socket = $state<WebSocket | null>(null);
  connected = $state(false);
  reconnecting = $state(false);
  private handlers = new Set<MessageHandler>();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(token?: string) {
    if (!browser) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:3010/ws';
    const url = token ? `${wsUrl}?token=${token}` : wsUrl;

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.connected = true;
        this.reconnecting = false;
        this.reconnectAttempts = 0;
        console.log('WebSocket connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          this.handlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.socket.onclose = () => {
        this.connected = false;
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnecting = true;
    this.reconnectAttempts++;

    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.connected = false;
    }
  }

  onMessage(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  send(message: any) {
    if (this.socket && this.connected) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }
}

export const ws = new WebSocketStore();
