/**
 * Offline manager for handling unreliable connections
 * Provides message queuing, retry logic, and event buffering
 */

export interface QueuedMessage {
  id: string;
  type: 'message' | 'session_update' | 'context_update';
  timestamp: number;
  data: any;
  retryCount: number;
  maxRetries: number;
  nextRetryTime: number;
}

export interface ConnectionStatus {
  isOnline: boolean;
  lastConnected: number | null;
  reconnectAttempts: number;
  queuedMessages: number;
}

export class OfflineManager {
  private queue: QueuedMessage[] = [];
  private isOnline = navigator.onLine;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private reconnectTimer: number | null = null;
  private heartbeatTimer: number | null = null;
  private storageKey = 'chat_offline_queue';
  
  // Event callbacks
  private onConnectionChange?: (status: ConnectionStatus) => void;
  private onMessageQueued?: (message: QueuedMessage) => void;
  private onMessageSent?: (messageId: string) => void;
  private onMessageFailed?: (messageId: string, error: Error) => void;

  constructor() {
    this.loadQueueFromStorage();
    this.setupEventListeners();
    this.startHeartbeat();
  }

  /**
   * Set up event listeners for online/offline events
   */
  private setupEventListeners(): void {
    window.addEventListener('online', () => this.handleConnectionChange(true));
    window.addEventListener('offline', () => this.handleConnectionChange(false));
  }

  /**
   * Handle connection status changes
   */
  private handleConnectionChange(online: boolean): void {
    const wasOffline = !this.isOnline;
    this.isOnline = online;

    if (online && wasOffline) {
      // Came back online, try to send queued messages
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.processQueue();
    } else if (!online) {
      // Went offline, clear reconnect timer
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    }

    this.notifyConnectionChange();
  }

  /**
   * Start heartbeat to detect connection issues
   */
  private startHeartbeat(): void {
    const heartbeat = async () => {
      if (this.isOnline) {
        try {
          // Simple ping to server
          const response = await fetch('/api/health', {
            method: 'HEAD',
            cache: 'no-cache',
            signal: AbortSignal.timeout(5000)
          });
          
          if (!response.ok) {
            throw new Error('Health check failed');
          }
          
          // Connection is good, reset reconnect attempts
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
        } catch (error) {
          // Connection issue detected
          console.warn('Connection heartbeat failed:', error);
          if (this.isOnline) {
            this.handleConnectionIssue();
          }
        }
      }
      
      this.heartbeatTimer = requestAnimationFrame(() => {
        setTimeout(heartbeat, 30000); // Check every 30 seconds
      });
    };
    
    heartbeat();
  }

  /**
   * Handle connection issues while supposedly online
   */
  private handleConnectionIssue(): void {
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts >= 3) {
      // Consider offline after 3 failed attempts
      this.handleConnectionChange(false);
    }
  }

  /**
   * Queue a message for sending when connection is restored
   */
  public queueMessage(
    type: QueuedMessage['type'],
    data: any,
    maxRetries: number = 3
  ): string {
    const message: QueuedMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      timestamp: Date.now(),
      data,
      retryCount: 0,
      maxRetries,
      nextRetryTime: Date.now()
    };

    this.queue.push(message);
    this.saveQueueToStorage();
    
    this.onMessageQueued?.(message);
    this.notifyConnectionChange();

    // Try to send immediately if online
    if (this.isOnline) {
      this.processQueue();
    }

    return message.id;
  }

  /**
   * Process the message queue
   */
  private async processQueue(): Promise<void> {
    if (!this.isOnline || this.queue.length === 0) {
      return;
    }

    const now = Date.now();
    const readyMessages = this.queue.filter(msg => msg.nextRetryTime <= now);
    
    if (readyMessages.length === 0) {
      return;
    }

    // Process messages in order
    for (const message of readyMessages) {
      try {
        await this.sendMessage(message);
        this.removeMessage(message.id);
        this.onMessageSent?.(message.id);
      } catch (error) {
        console.error(`Failed to send message ${message.id}:`, error);
        this.handleMessageFailure(message, error as Error);
      }
    }

    // Continue processing if there are more messages
    if (this.queue.length > 0) {
      setTimeout(() => this.processQueue(), 1000);
    }
  }

  /**
   * Send a single message
   */
  private async sendMessage(message: QueuedMessage): Promise<void> {
    const { type, data } = message;

    switch (type) {
      case 'message':
        await this.sendChatMessage(data);
        break;
      case 'session_update':
        await this.sendSessionUpdate(data);
        break;
      case 'context_update':
        await this.sendContextUpdate(data);
        break;
      default:
        throw new Error(`Unknown message type: ${type}`);
    }
  }

  /**
   * Send chat message via API
   */
  private async sendChatMessage(data: any): Promise<void> {
    const response = await fetch('/api/chat/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  /**
   * Send session update via API
   */
  private async sendSessionUpdate(data: any): Promise<void> {
    const { session_id, context } = data;
    const response = await fetch(`/api/chat/sessions/${session_id}/context`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ context })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  /**
   * Send context update via API
   */
  private async sendContextUpdate(data: any): Promise<void> {
    const { session_id, customer_info } = data;
    const response = await fetch(`/api/chat/sessions/${session_id}/context/customer-info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customer_info)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  /**
   * Handle message sending failure
   */
  private handleMessageFailure(message: QueuedMessage, error: Error): void {
    message.retryCount++;
    
    if (message.retryCount >= message.maxRetries) {
      // Max retries reached, remove message
      this.removeMessage(message.id);
      this.onMessageFailed?.(message.id, error);
      return;
    }

    // Calculate next retry time with exponential backoff
    const delay = Math.min(1000 * Math.pow(2, message.retryCount), 30000);
    message.nextRetryTime = Date.now() + delay;
    
    // Re-sort queue by next retry time
    this.queue.sort((a, b) => a.nextRetryTime - b.nextRetryTime);
    this.saveQueueToStorage();

    // Schedule retry
    setTimeout(() => this.processQueue(), delay);
  }

  /**
   * Remove a message from the queue
   */
  private removeMessage(messageId: string): void {
    const index = this.queue.findIndex(msg => msg.id === messageId);
    if (index !== -1) {
      this.queue.splice(index, 1);
      this.saveQueueToStorage();
      this.notifyConnectionChange();
    }
  }

  /**
   * Save queue to localStorage
   */
  private saveQueueToStorage(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save queue to storage:', error);
    }
  }

  /**
   * Load queue from localStorage
   */
  private loadQueueFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.queue = JSON.parse(stored);
        // Filter out old messages (older than 24 hours)
        const dayAgo = Date.now() - (24 * 60 * 60 * 1000);
        this.queue = this.queue.filter(msg => msg.timestamp > dayAgo);
        this.saveQueueToStorage();
      }
    } catch (error) {
      console.error('Failed to load queue from storage:', error);
      this.queue = [];
    }
  }

  /**
   * Notify connection status change
   */
  private notifyConnectionChange(): void {
    this.onConnectionChange?.({
      isOnline: this.isOnline,
      lastConnected: this.isOnline ? Date.now() : null,
      reconnectAttempts: this.reconnectAttempts,
      queuedMessages: this.queue.length
    });
  }

  /**
   * Get current connection status
   */
  public getConnectionStatus(): ConnectionStatus {
    return {
      isOnline: this.isOnline,
      lastConnected: this.isOnline ? Date.now() : null,
      reconnectAttempts: this.reconnectAttempts,
      queuedMessages: this.queue.length
    };
  }

  /**
   * Get queued messages
   */
  public getQueuedMessages(): QueuedMessage[] {
    return [...this.queue];
  }

  /**
   * Clear all queued messages
   */
  public clearQueue(): void {
    this.queue = [];
    this.saveQueueToStorage();
    this.notifyConnectionChange();
  }

  /**
   * Set event callbacks
   */
  public on(event: 'connectionChange', callback: (status: ConnectionStatus) => void): void;
  public on(event: 'messageQueued', callback: (message: QueuedMessage) => void): void;
  public on(event: 'messageSent', callback: (messageId: string) => void): void;
  public on(event: 'messageFailed', callback: (messageId: string, error: Error) => void): void;
  public on(event: string, callback: any): void {
    switch (event) {
      case 'connectionChange':
        this.onConnectionChange = callback;
        break;
      case 'messageQueued':
        this.onMessageQueued = callback;
        break;
      case 'messageSent':
        this.onMessageSent = callback;
        break;
      case 'messageFailed':
        this.onMessageFailed = callback;
        break;
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.heartbeatTimer) {
      cancelAnimationFrame(this.heartbeatTimer);
    }
    window.removeEventListener('online', () => this.handleConnectionChange(true));
    window.removeEventListener('offline', () => this.handleConnectionChange(false));
  }
}

// Singleton instance
export const offlineManager = new OfflineManager();