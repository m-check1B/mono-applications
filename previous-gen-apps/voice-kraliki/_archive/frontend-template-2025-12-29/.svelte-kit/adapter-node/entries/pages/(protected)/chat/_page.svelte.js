import { g as sanitize_props, j as spread_props, s as slot, e as ensure_array_like, d as attr_class, f as stringify, c as attr, a as store_get, u as unsubscribe_stores, b as bind_props } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import { d as derived, w as writable } from "../../../../chunks/index.js";
import { c as crossTabSync } from "../../../../chunks/auth2.js";
import { B as Bot, U as User, M as Message_circle } from "../../../../chunks/user.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { X } from "../../../../chunks/x.js";
import { M as Mic } from "../../../../chunks/mic.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import "../../../../chunks/env.js";
import { P as Plus } from "../../../../chunks/plus.js";
import { S as Search } from "../../../../chunks/search.js";
import { U as Users } from "../../../../chunks/users.js";
import { P as Phone } from "../../../../chunks/phone.js";
import { W as Wifi_off } from "../../../../chunks/wifi-off.js";
import { R as Refresh_cw } from "../../../../chunks/refresh-cw.js";
function Info($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["path", { "d": "M12 16v-4" }],
    ["path", { "d": "M12 8h.01" }]
  ];
  Icon($$renderer, spread_props([
    { name: "info" },
    $$sanitized_props,
    {
      /**
       * @component @name Info
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8cGF0aCBkPSJNMTIgMTZ2LTQiIC8+CiAgPHBhdGggZD0iTTEyIDhoLjAxIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/info
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Paperclip($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M13.234 20.252 21 12.3" }],
    [
      "path",
      {
        "d": "m16 6-8.414 8.586a2 2 0 0 0 0 2.828 2 2 0 0 0 2.828 0l8.414-8.586a4 4 0 0 0 0-5.656 4 4 0 0 0-5.656 0l-8.415 8.585a6 6 0 1 0 8.486 8.486"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "paperclip" },
    $$sanitized_props,
    {
      /**
       * @component @name Paperclip
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTMuMjM0IDIwLjI1MiAyMSAxMi4zIiAvPgogIDxwYXRoIGQ9Im0xNiA2LTguNDE0IDguNTg2YTIgMiAwIDAgMCAwIDIuODI4IDIgMiAwIDAgMCAyLjgyOCAwbDguNDE0LTguNTg2YTQgNCAwIDAgMCAwLTUuNjU2IDQgNCAwIDAgMC01LjY1NiAwbC04LjQxNSA4LjU4NWE2IDYgMCAxIDAgOC40ODYgOC40ODYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/paperclip
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Send($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"
      }
    ],
    ["path", { "d": "m21.854 2.147-10.94 10.939" }]
  ];
  Icon($$renderer, spread_props([
    { name: "send" },
    $$sanitized_props,
    {
      /**
       * @component @name Send
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTQuNTM2IDIxLjY4NmEuNS41IDAgMCAwIC45MzctLjAyNGw2LjUtMTlhLjQ5Ni40OTYgMCAwIDAtLjYzNS0uNjM1bC0xOSA2LjVhLjUuNSAwIDAgMC0uMDI0LjkzN2w3LjkzIDMuMThhMiAyIDAgMCAxIDEuMTEyIDEuMTF6IiAvPgogIDxwYXRoIGQ9Im0yMS44NTQgMi4xNDctMTAuOTQgMTAuOTM5IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/send
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Settings($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
      }
    ],
    ["circle", { "cx": "12", "cy": "12", "r": "3" }]
  ];
  Icon($$renderer, spread_props([
    { name: "settings" },
    $$sanitized_props,
    {
      /**
       * @component @name Settings
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIuMjIgMmgtLjQ0YTIgMiAwIDAgMC0yIDJ2LjE4YTIgMiAwIDAgMS0xIDEuNzNsLS40My4yNWEyIDIgMCAwIDEtMiAwbC0uMTUtLjA4YTIgMiAwIDAgMC0yLjczLjczbC0uMjIuMzhhMiAyIDAgMCAwIC43MyAyLjczbC4xNS4xYTIgMiAwIDAgMSAxIDEuNzJ2LjUxYTIgMiAwIDAgMS0xIDEuNzRsLS4xNS4wOWEyIDIgMCAwIDAtLjczIDIuNzNsLjIyLjM4YTIgMiAwIDAgMCAyLjczLjczbC4xNS0uMDhhMiAyIDAgMCAxIDIgMGwuNDMuMjVhMiAyIDAgMCAxIDEgMS43M1YyMGEyIDIgMCAwIDAgMiAyaC40NGEyIDIgMCAwIDAgMi0ydi0uMThhMiAyIDAgMCAxIDEtMS43M2wuNDMtLjI1YTIgMiAwIDAgMSAyIDBsLjE1LjA4YTIgMiAwIDAgMCAyLjczLS43M2wuMjItLjM5YTIgMiAwIDAgMC0uNzMtMi43M2wtLjE1LS4wOGEyIDIgMCAwIDEtMS0xLjc0di0uNWEyIDIgMCAwIDEgMS0xLjc0bC4xNS0uMDlhMiAyIDAgMCAwIC43My0yLjczbC0uMjItLjM4YTIgMiAwIDAgMC0yLjczLS43M2wtLjE1LjA4YTIgMiAwIDAgMS0yIDBsLS40My0uMjVhMiAyIDAgMCAxLTEtMS43M1Y0YTIgMiAwIDAgMC0yLTJ6IiAvPgogIDxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/settings
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Wifi($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M12 20h.01" }],
    ["path", { "d": "M2 8.82a15 15 0 0 1 20 0" }],
    ["path", { "d": "M5 12.859a10 10 0 0 1 14 0" }],
    ["path", { "d": "M8.5 16.429a5 5 0 0 1 7 0" }]
  ];
  Icon($$renderer, spread_props([
    { name: "wifi" },
    $$sanitized_props,
    {
      /**
       * @component @name Wifi
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgMjBoLjAxIiAvPgogIDxwYXRoIGQ9Ik0yIDguODJhMTUgMTUgMCAwIDEgMjAgMCIgLz4KICA8cGF0aCBkPSJNNSAxMi44NTlhMTAgMTAgMCAwIDEgMTQgMCIgLz4KICA8cGF0aCBkPSJNOC41IDE2LjQyOWE1IDUgMCAwIDEgNyAwIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/wifi
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
class OfflineManager {
  queue = [];
  isOnline = navigator.onLine;
  reconnectAttempts = 0;
  maxReconnectAttempts = 10;
  reconnectDelay = 1e3;
  // Start with 1 second
  maxReconnectDelay = 3e4;
  // Max 30 seconds
  reconnectTimer = null;
  heartbeatTimer = null;
  storageKey = "chat_offline_queue";
  // Event callbacks
  onConnectionChange;
  onMessageQueued;
  onMessageSent;
  onMessageFailed;
  constructor() {
    this.loadQueueFromStorage();
    this.setupEventListeners();
    this.startHeartbeat();
  }
  /**
   * Set up event listeners for online/offline events
   */
  setupEventListeners() {
    window.addEventListener("online", () => this.handleConnectionChange(true));
    window.addEventListener("offline", () => this.handleConnectionChange(false));
  }
  /**
   * Handle connection status changes
   */
  handleConnectionChange(online) {
    const wasOffline = !this.isOnline;
    this.isOnline = online;
    if (online && wasOffline) {
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1e3;
      this.processQueue();
    } else if (!online) {
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
  startHeartbeat() {
    const heartbeat = async () => {
      if (this.isOnline) {
        try {
          const response = await fetch("/api/health", {
            method: "HEAD",
            cache: "no-cache",
            signal: AbortSignal.timeout(5e3)
          });
          if (!response.ok) {
            throw new Error("Health check failed");
          }
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1e3;
        } catch (error) {
          console.warn("Connection heartbeat failed:", error);
          if (this.isOnline) {
            this.handleConnectionIssue();
          }
        }
      }
      this.heartbeatTimer = requestAnimationFrame(() => {
        setTimeout(heartbeat, 3e4);
      });
    };
    heartbeat();
  }
  /**
   * Handle connection issues while supposedly online
   */
  handleConnectionIssue() {
    this.reconnectAttempts++;
    if (this.reconnectAttempts >= 3) {
      this.handleConnectionChange(false);
    }
  }
  /**
   * Queue a message for sending when connection is restored
   */
  queueMessage(type, data, maxRetries = 3) {
    const message = {
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
    if (this.isOnline) {
      this.processQueue();
    }
    return message.id;
  }
  /**
   * Process the message queue
   */
  async processQueue() {
    if (!this.isOnline || this.queue.length === 0) {
      return;
    }
    const now = Date.now();
    const readyMessages = this.queue.filter((msg) => msg.nextRetryTime <= now);
    if (readyMessages.length === 0) {
      return;
    }
    for (const message of readyMessages) {
      try {
        await this.sendMessage(message);
        this.removeMessage(message.id);
        this.onMessageSent?.(message.id);
      } catch (error) {
        console.error(`Failed to send message ${message.id}:`, error);
        this.handleMessageFailure(message, error);
      }
    }
    if (this.queue.length > 0) {
      setTimeout(() => this.processQueue(), 1e3);
    }
  }
  /**
   * Send a single message
   */
  async sendMessage(message) {
    const { type, data } = message;
    switch (type) {
      case "message":
        await this.sendChatMessage(data);
        break;
      case "session_update":
        await this.sendSessionUpdate(data);
        break;
      case "context_update":
        await this.sendContextUpdate(data);
        break;
      default:
        throw new Error(`Unknown message type: ${type}`);
    }
  }
  /**
   * Send chat message via API
   */
  async sendChatMessage(data) {
    const response = await fetch("/api/chat/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
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
  async sendSessionUpdate(data) {
    const { session_id, context } = data;
    const response = await fetch(`/api/chat/sessions/${session_id}/context`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
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
  async sendContextUpdate(data) {
    const { session_id, customer_info } = data;
    const response = await fetch(`/api/chat/sessions/${session_id}/context/customer-info`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
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
  handleMessageFailure(message, error) {
    message.retryCount++;
    if (message.retryCount >= message.maxRetries) {
      this.removeMessage(message.id);
      this.onMessageFailed?.(message.id, error);
      return;
    }
    const delay = Math.min(1e3 * Math.pow(2, message.retryCount), 3e4);
    message.nextRetryTime = Date.now() + delay;
    this.queue.sort((a, b) => a.nextRetryTime - b.nextRetryTime);
    this.saveQueueToStorage();
    setTimeout(() => this.processQueue(), delay);
  }
  /**
   * Remove a message from the queue
   */
  removeMessage(messageId) {
    const index = this.queue.findIndex((msg) => msg.id === messageId);
    if (index !== -1) {
      this.queue.splice(index, 1);
      this.saveQueueToStorage();
      this.notifyConnectionChange();
    }
  }
  /**
   * Save queue to localStorage
   */
  saveQueueToStorage() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.queue));
    } catch (error) {
      console.error("Failed to save queue to storage:", error);
    }
  }
  /**
   * Load queue from localStorage
   */
  loadQueueFromStorage() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.queue = JSON.parse(stored);
        const dayAgo = Date.now() - 24 * 60 * 60 * 1e3;
        this.queue = this.queue.filter((msg) => msg.timestamp > dayAgo);
        this.saveQueueToStorage();
      }
    } catch (error) {
      console.error("Failed to load queue from storage:", error);
      this.queue = [];
    }
  }
  /**
   * Notify connection status change
   */
  notifyConnectionChange() {
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
  getConnectionStatus() {
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
  getQueuedMessages() {
    return [...this.queue];
  }
  /**
   * Clear all queued messages
   */
  clearQueue() {
    this.queue = [];
    this.saveQueueToStorage();
    this.notifyConnectionChange();
  }
  on(event, callback) {
    switch (event) {
      case "connectionChange":
        this.onConnectionChange = callback;
        break;
      case "messageQueued":
        this.onMessageQueued = callback;
        break;
      case "messageSent":
        this.onMessageSent = callback;
        break;
      case "messageFailed":
        this.onMessageFailed = callback;
        break;
    }
  }
  /**
   * Cleanup resources
   */
  destroy() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.heartbeatTimer) {
      cancelAnimationFrame(this.heartbeatTimer);
    }
    window.removeEventListener("online", () => this.handleConnectionChange(true));
    window.removeEventListener("offline", () => this.handleConnectionChange(false));
  }
}
const offlineManager = new OfflineManager();
function broadcastSessionUpdate(sessionId, data) {
  if (crossTabSync.isAvailable()) {
    crossTabSync.broadcast("session_updated", {
      sessionId,
      data,
      timestamp: Date.now()
    });
  }
}
function broadcastSessionEnd(sessionId) {
  if (crossTabSync.isAvailable()) {
    crossTabSync.broadcast("session_ended", {
      sessionId,
      timestamp: Date.now()
    });
  }
}
function subscribeToSessionUpdates(callback) {
  if (!crossTabSync.isAvailable()) {
    return () => {
    };
  }
  return crossTabSync.subscribe("session_updated", (message) => {
    const { sessionId, data } = message.payload;
    callback(sessionId, data);
  });
}
function subscribeToSessionEnd(callback) {
  if (!crossTabSync.isAvailable()) {
    return () => {
    };
  }
  return crossTabSync.subscribe("session_ended", (message) => {
    const { sessionId } = message.payload;
    callback(sessionId);
  });
}
function getUnreadTotal(sessions) {
  return Object.values(sessions).reduce(
    (total, session) => total + (session.unreadCount ?? 0),
    0
  );
}
function normalizeSession(session) {
  return {
    ...session,
    messages: session.messages ?? [],
    context: session.context ?? {},
    createdAt: session.createdAt ?? /* @__PURE__ */ new Date(),
    lastActivity: session.lastActivity ?? /* @__PURE__ */ new Date(),
    unreadCount: session.unreadCount ?? 0
  };
}
function createChatStore() {
  const initialState = {
    sessions: {},
    activeSessionId: null,
    isConnected: false,
    isTyping: false,
    unreadCount: 0,
    connectionStatus: offlineManager.getConnectionStatus(),
    offlineMode: !navigator.onLine
  };
  const { subscribe, set, update } = writable(initialState);
  offlineManager.on("connectionChange", (status) => {
    update((state) => ({
      ...state,
      connectionStatus: status,
      isConnected: status.isOnline,
      offlineMode: !status.isOnline
    }));
  });
  subscribeToSessionUpdates((sessionId, data) => {
    update((state) => {
      const session = state.sessions[sessionId];
      if (!session) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [sessionId]: {
            ...session,
            ...data,
            lastActivity: /* @__PURE__ */ new Date()
          }
        }
      };
    });
  });
  subscribeToSessionEnd((sessionId) => {
    update((state) => ({
      ...state,
      sessions: {
        ...state.sessions,
        [sessionId]: {
          ...state.sessions[sessionId],
          status: "ended"
        }
      }
    }));
  });
  return {
    subscribe,
    // Session management
    setSessions: (sessions) => {
      update((state) => {
        const nextSessions = { ...state.sessions };
        for (const session of sessions) {
          const normalized = normalizeSession(session);
          const existing = nextSessions[normalized.id];
          nextSessions[normalized.id] = {
            ...normalized,
            messages: existing?.messages ?? normalized.messages,
            context: {
              ...existing?.context,
              ...normalized.context
            },
            unreadCount: normalized.unreadCount ?? existing?.unreadCount ?? 0
          };
        }
        return {
          ...state,
          sessions: nextSessions,
          unreadCount: getUnreadTotal(nextSessions)
        };
      });
    },
    initializeSession: (sessionData) => {
      update((state) => {
        const newSession = {
          id: sessionData.sessionId,
          userId: sessionData.userId,
          companyId: sessionData.companyId,
          status: "active",
          createdAt: /* @__PURE__ */ new Date(),
          lastActivity: /* @__PURE__ */ new Date(),
          messages: [],
          unreadCount: 0,
          context: {}
        };
        broadcastSessionUpdate(sessionData.sessionId, newSession);
        return {
          ...state,
          sessions: {
            ...state.sessions,
            [sessionData.sessionId]: newSession
          },
          activeSessionId: sessionData.sessionId
        };
      });
    },
    setActiveSession: (sessionId) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) {
          return {
            ...state,
            activeSessionId: sessionId
          };
        }
        const updatedSessions = {
          ...state.sessions,
          [sessionId]: {
            ...session,
            unreadCount: 0
          }
        };
        return {
          ...state,
          activeSessionId: sessionId,
          sessions: updatedSessions,
          unreadCount: getUnreadTotal(updatedSessions)
        };
      });
    },
    updateSession: (sessionId, updates) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) {
          return state;
        }
        const updatedSessions = {
          ...state.sessions,
          [sessionId]: {
            ...session,
            ...updates,
            context: {
              ...session.context,
              ...updates.context
            },
            messages: updates.messages ?? session.messages
          }
        };
        return {
          ...state,
          sessions: updatedSessions,
          unreadCount: getUnreadTotal(updatedSessions)
        };
      });
    },
    endSession: (sessionId) => {
      update((state) => ({
        ...state,
        sessions: {
          ...state.sessions,
          [sessionId]: {
            ...state.sessions[sessionId],
            status: "ended"
          }
        }
      }));
      broadcastSessionEnd(sessionId);
    },
    // Message management
    addMessage: (message, queueOffline = true) => {
      const newMessage = {
        ...message,
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: /* @__PURE__ */ new Date()
      };
      update((state) => {
        const session = state.sessions[message.sessionId] ?? normalizeSession({
          id: message.sessionId,
          userId: "",
          companyId: "",
          status: "active",
          createdAt: /* @__PURE__ */ new Date(),
          lastActivity: /* @__PURE__ */ new Date(),
          messages: [],
          context: {}
        });
        const isActiveSession = state.activeSessionId === message.sessionId;
        const nextUnreadCount = isActiveSession ? 0 : (session.unreadCount ?? 0) + 1;
        const updatedSession = {
          ...session,
          messages: [...session.messages, newMessage],
          lastActivity: /* @__PURE__ */ new Date(),
          lastMessage: newMessage.content,
          unreadCount: nextUnreadCount
        };
        const updatedSessions = {
          ...state.sessions,
          [message.sessionId]: updatedSession
        };
        return {
          ...state,
          sessions: updatedSessions,
          unreadCount: getUnreadTotal(updatedSessions)
        };
      });
      if (queueOffline && message.role === "user") {
        offlineManager.queueMessage("message", {
          session_id: message.sessionId,
          message: {
            role: message.role,
            content: message.content,
            metadata: message.metadata
          }
        });
      }
      return newMessage.id;
    },
    // Send message with offline support
    sendMessage: async (sessionId, content, metadata) => {
      const messageId = chatStore.addMessage({
        sessionId,
        role: "user",
        content,
        metadata
      }, false);
      try {
        if (offlineManager.getConnectionStatus().isOnline) {
          const response = await fetch("/api/chat/messages", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              session_id: sessionId,
              message: {
                role: "user",
                content,
                metadata
              }
            })
          });
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
        } else {
          offlineManager.queueMessage("message", {
            session_id: sessionId,
            message: {
              role: "user",
              content,
              metadata
            }
          });
        }
      } catch (error) {
        console.error("Failed to send message:", error);
        offlineManager.queueMessage("message", {
          session_id: sessionId,
          message: {
            role: "user",
            content,
            metadata
          }
        });
      }
      return messageId;
    },
    updateMessage: (sessionId, messageId, updates) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) return state;
        return {
          ...state,
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...session,
              messages: session.messages.map(
                (msg) => msg.id === messageId ? { ...msg, ...updates } : msg
              )
            }
          }
        };
      });
    },
    // Connection state
    setConnectionState: (isConnected2) => {
      update((state) => ({
        ...state,
        isConnected: isConnected2
      }));
    },
    setTypingState: (isTyping) => {
      update((state) => ({
        ...state,
        isTyping
      }));
    },
    // Context management
    updateSessionContext: (sessionId, context) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) return state;
        const updatedContext = {
          ...session.context,
          ...context
        };
        broadcastSessionUpdate(sessionId, { context: updatedContext });
        return {
          ...state,
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...session,
              context: updatedContext,
              lastActivity: /* @__PURE__ */ new Date()
            }
          }
        };
      });
      offlineManager.queueMessage("session_update", {
        session_id: sessionId,
        context
      });
    },
    updateCustomerInfo: (sessionId, customerInfo) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) return state;
        return {
          ...state,
          sessions: {
            ...state.sessions,
            [sessionId]: {
              ...session,
              context: {
                ...session.context,
                customerInfo: {
                  ...session.context.customerInfo,
                  ...customerInfo
                }
              },
              lastActivity: /* @__PURE__ */ new Date()
            }
          }
        };
      });
      offlineManager.queueMessage("context_update", {
        session_id: sessionId,
        customer_info: customerInfo
      });
    },
    // Utility
    clearUnreadCount: () => {
      update((state) => ({
        ...state,
        unreadCount: 0,
        sessions: Object.fromEntries(
          Object.entries(state.sessions).map(([sessionId, session]) => [
            sessionId,
            {
              ...session,
              unreadCount: 0
            }
          ])
        )
      }));
    },
    markSessionRead: (sessionId) => {
      update((state) => {
        const session = state.sessions[sessionId];
        if (!session) return state;
        const updatedSessions = {
          ...state.sessions,
          [sessionId]: {
            ...session,
            unreadCount: 0,
            lastActivity: /* @__PURE__ */ new Date()
          }
        };
        return {
          ...state,
          sessions: updatedSessions,
          unreadCount: getUnreadTotal(updatedSessions)
        };
      });
    },
    // Offline management
    getOfflineStatus: () => offlineManager.getConnectionStatus(),
    getQueuedMessages: () => offlineManager.getQueuedMessages(),
    clearOfflineQueue: () => offlineManager.clearQueue()
  };
}
const chatStore = createChatStore();
const activeSession = derived(
  chatStore,
  ($chatStore) => $chatStore.activeSessionId ? $chatStore.sessions[$chatStore.activeSessionId] : null
);
const activeMessages = derived(
  activeSession,
  ($activeSession) => $activeSession?.messages || []
);
derived(
  chatStore,
  ($chatStore) => $chatStore.isConnected
);
function ChatMessageList($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { messages, compact = false } = $$props;
    function formatTime(date) {
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    function getRoleIcon(role) {
      switch (role) {
        case "user":
          return User;
        case "assistant":
          return Bot;
        case "system":
          return Info;
        default:
          return User;
      }
    }
    function getRoleColor(role) {
      switch (role) {
        case "user":
          return "bg-primary text-white";
        case "assistant":
          return "bg-secondary text-text-primary";
        case "system":
          return "bg-tertiary text-text-muted";
        default:
          return "bg-secondary text-text-primary";
      }
    }
    function getAttachments(message) {
      const attachments = message.metadata?.attachments;
      if (!Array.isArray(attachments)) {
        return [];
      }
      return attachments;
    }
    function formatFileSize(size) {
      if (!size) return "";
      if (size < 1024) return `${size} B`;
      if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }
    $$renderer2.push(`<div class="flex h-full flex-col space-y-4 overflow-y-auto p-4 svelte-1soyxjk">`);
    const each_array = ensure_array_like(messages);
    if (each_array.length !== 0) {
      $$renderer2.push("<!--[-->");
      for (let $$index_1 = 0, $$length = each_array.length; $$index_1 < $$length; $$index_1++) {
        let message = each_array[$$index_1];
        const IconComponent = getRoleIcon(message.role);
        const attachments = getAttachments(message);
        $$renderer2.push(`<div${attr_class(`flex gap-3 ${stringify(message.role === "user" ? "flex-row-reverse" : "flex-row")}`, "svelte-1soyxjk", { "compact": compact })}><div class="flex-shrink-0"><div${attr_class(`flex size-8 items-center justify-center rounded-full ${stringify(getRoleColor(message.role))}`, "svelte-1soyxjk")}><!---->`);
        IconComponent($$renderer2, { class: "size-4" });
        $$renderer2.push(`<!----></div></div> <div${attr_class("flex max-w-[70%] flex-col gap-1", void 0, { "text-right": message.role === "user" })}><div${attr_class(
          `rounded-2xl px-4 py-2 ${stringify(message.role === "user" ? "bg-primary text-white" : "bg-secondary text-text-primary")}`,
          "svelte-1soyxjk"
        )}><p class="text-sm leading-relaxed svelte-1soyxjk">${escape_html(message.content)}</p></div> `);
        if (attachments.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="rounded-lg border border-divider-subtle bg-card px-3 py-2 text-xs text-text-secondary svelte-1soyxjk"><!--[-->`);
          const each_array_1 = ensure_array_like(attachments);
          for (let $$index = 0, $$length2 = each_array_1.length; $$index < $$length2; $$index++) {
            let attachment = each_array_1[$$index];
            $$renderer2.push(`<div class="flex items-center justify-between gap-2"><span class="max-w-[220px] truncate">${escape_html(attachment.name)}</span> <span class="text-text-muted">${escape_html(formatFileSize(attachment.size))}</span></div> `);
            if (attachment.text) {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<pre class="mt-1 max-h-40 overflow-auto whitespace-pre-wrap text-[11px] leading-relaxed text-text-muted">${escape_html(attachment.text)}</pre>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]-->`);
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> <div class="flex items-center gap-2 text-xs text-text-muted"><span>${escape_html(formatTime(message.timestamp))}</span> `);
        if (message.metadata?.provider) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="font-medium">${escape_html(message.metadata.provider)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.metadata?.confidence) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span>${escape_html(Math.round(message.metadata.confidence * 100))}% confidence</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.metadata?.intent) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="rounded bg-tertiary px-1 py-0.5">${escape_html(message.metadata.intent)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (message.metadata?.sentiment) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="rounded bg-tertiary px-1 py-0.5">${escape_html(message.metadata.sentiment)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div></div></div>`);
      }
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="flex flex-1 items-center justify-center text-text-muted"><div class="text-center">`);
      Bot($$renderer2, { class: "mx-auto mb-2 size-8 text-text-muted" });
      $$renderer2.push(`<!----> <p class="text-sm">No messages yet. Start a conversation!</p></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function ChatInput($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      disabled = false,
      placeholder = "Type your message..."
    } = $$props;
    let message = "";
    let attachments = [];
    let attachmentErrors = [];
    function formatFileSize(size) {
      if (size < 1024) return `${size} B`;
      if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }
    $$renderer2.push(`<div class="flex items-end gap-3"><button class="flex size-10 items-center justify-center rounded-lg text-text-secondary hover:bg-secondary-hover disabled:opacity-50"${attr("disabled", disabled, true)} title="Attach file">`);
    Paperclip($$renderer2, { class: "size-5" });
    $$renderer2.push(`<!----></button> <input type="file" class="hidden" multiple${attr("disabled", disabled, true)}/> <div class="flex-1"><textarea${attr("placeholder", placeholder)}${attr("disabled", disabled, true)} class="w-full resize-none border-2 border-divider bg-background px-4 py-3 text-sm placeholder-text-muted focus:outline-none disabled:opacity-50 shadow-card svelte-j7h4bp" rows="1" style="max-height: 120px; min-height: 44px;">`);
    const $$body = escape_html(message);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea> `);
    if (attachmentErrors.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="mt-2 text-xs text-red-500">${escape_html(attachmentErrors.join(" "))}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (attachments.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="mt-2 flex flex-wrap gap-2"><!--[-->`);
      const each_array = ensure_array_like(attachments);
      for (let index = 0, $$length = each_array.length; index < $$length; index++) {
        let attachment = each_array[index];
        $$renderer2.push(`<div class="flex items-center gap-2 rounded-lg border border-divider bg-card px-2 py-1 text-xs text-text-secondary"><span class="max-w-[180px] truncate">${escape_html(attachment.payload.name)}</span> <span class="text-text-muted">${escape_html(formatFileSize(attachment.payload.size))}</span> <button class="text-text-muted hover:text-text-primary" title="Remove attachment" type="button">`);
        X($$renderer2, { class: "size-3" });
        $$renderer2.push(`<!----></button></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <button class="inline-flex size-10 items-center justify-center border-2 border-divider bg-card text-text-secondary shadow-card disabled:opacity-50"${attr("disabled", disabled, true)}${attr("title", "Start recording")}>`);
    Mic($$renderer2, {
      class: `size-5 ${stringify("")}`
    });
    $$renderer2.push(`<!----></button> <button class="inline-flex size-10 items-center justify-center border-2 border-divider bg-primary text-primary-foreground shadow-card disabled:opacity-50"${attr("disabled", disabled || !message.trim() && attachments.length === 0, true)} title="Send message">`);
    Send($$renderer2, { class: "size-5" });
    $$renderer2.push(`<!----></button></div>`);
  });
}
function ChatSidebar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let searchQuery = "";
    let filterStatus = "all";
    let sessions = Object.values(store_get($$store_subs ??= {}, "$chatStore", chatStore).sessions);
    function formatTime(date) {
      const now = /* @__PURE__ */ new Date();
      const diff = now.getTime() - date.getTime();
      const minutes = Math.floor(diff / (1e3 * 60));
      const hours = Math.floor(diff / (1e3 * 60 * 60));
      const days = Math.floor(diff / (1e3 * 60 * 60 * 24));
      if (minutes < 1) return "Just now";
      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      if (days < 7) return `${days}d ago`;
      return date.toLocaleDateString();
    }
    function getStatusColor(status) {
      switch (status) {
        case "active":
          return "bg-green-100 text-green-800";
        case "ended":
          return "bg-gray-100 text-gray-800";
        default:
          return "bg-gray-100 text-gray-800";
      }
    }
    const filteredSessions = sessions.slice().sort((a, b) => b.lastActivity.getTime() - a.lastActivity.getTime()).filter((session) => {
      const customerName = session.customerName ?? "Unknown Customer";
      const lastMessage = session.lastMessage ?? "";
      const matchesSearch = customerName.toLowerCase().includes(searchQuery.toLowerCase()) || lastMessage.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterStatus === "all";
      return matchesSearch && matchesFilter;
    });
    $$renderer2.push(`<div class="flex h-full flex-col bg-background"><div class="border-b border-divider-subtle p-4"><div class="mb-4 flex items-center justify-between"><h3 class="text-lg font-semibold text-text-primary">Chat Sessions</h3> <button class="flex size-8 items-center justify-center rounded-lg bg-primary text-white hover:bg-primary/90" title="New session">`);
    Plus($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----></button></div> <div class="relative mb-3">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-muted"
    });
    $$renderer2.push(`<!----> <input${attr("value", searchQuery)} type="text" placeholder="Search sessions..." class="w-full rounded-lg border border-divider-subtle bg-background pl-10 pr-4 py-2 text-sm placeholder-text-muted focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"/></div> <div class="flex gap-2"><!--[-->`);
    const each_array = ensure_array_like(["all", "active", "ended"]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let status = each_array[$$index];
      const statusValue = status;
      $$renderer2.push(`<button${attr_class(`rounded-lg px-3 py-1 text-xs font-medium capitalize ${stringify(filterStatus === statusValue ? "bg-primary text-white" : "bg-secondary text-text-secondary hover:bg-secondary-hover")}`)}>${escape_html(status)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="flex-1 overflow-y-auto svelte-fhtucl">`);
    const each_array_1 = ensure_array_like(filteredSessions);
    if (each_array_1.length !== 0) {
      $$renderer2.push("<!--[-->");
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let session = each_array_1[$$index_1];
        $$renderer2.push(`<div${attr_class(`flex cursor-pointer gap-3 border-b border-divider-subtle p-4 hover:bg-secondary-hover ${stringify(store_get($$store_subs ??= {}, "$activeSession", activeSession)?.id === session.id ? "bg-secondary-hover" : "")}`)}><div class="flex size-10 flex-shrink-0 items-center justify-center rounded-full bg-primary text-white">`);
        Users($$renderer2, { class: "size-5" });
        $$renderer2.push(`<!----></div> <div class="flex-1 min-w-0"><div class="flex items-center justify-between gap-2"><h4 class="truncate text-sm font-medium text-text-primary">${escape_html(session.customerName ?? "Unknown Customer")}</h4> <span class="text-xs text-text-muted">${escape_html(formatTime(session.lastActivity))}</span></div> <div class="mt-1 flex items-center justify-between gap-2"><p class="truncate text-xs text-text-secondary">${escape_html(session.lastMessage ?? "")}</p> `);
        if ((session.unreadCount ?? 0) > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="flex size-5 items-center justify-center rounded-full bg-primary text-xs text-white">${escape_html(session.unreadCount)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div> <div class="mt-2 flex items-center gap-2"><span${attr_class(`rounded-full px-2 py-0.5 text-xs font-medium ${stringify(getStatusColor(session.status))}`, "svelte-fhtucl")}>${escape_html(session.status)}</span> `);
        if (session.provider) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="rounded bg-tertiary px-2 py-0.5 text-xs text-text-muted">${escape_html(session.provider)}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> `);
        if (session.context?.voiceSessionId) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<button class="rounded bg-tertiary px-2 py-0.5 text-xs text-text-muted hover:bg-secondary-hover" title="Go to voice session">`);
          Phone($$renderer2, { class: "inline size-3" });
          $$renderer2.push(`<!----></button>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div></div></div>`);
      }
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="flex flex-1 items-center justify-center p-8 text-center">`);
      Users($$renderer2, { class: "mx-auto mb-2 size-8 text-text-muted" });
      $$renderer2.push(`<!----> <p class="text-sm text-text-muted">${escape_html("No sessions yet")}</p></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="border-t border-divider-subtle p-4"><button class="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm text-text-secondary hover:bg-secondary-hover">`);
    Settings($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Chat Settings</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ConnectionStatus($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let status = offlineManager.getConnectionStatus();
    onDestroy(() => {
    });
    function getStatusColor() {
      if (!status.isOnline) return "bg-red-500";
      if (status.queuedMessages > 0) return "bg-yellow-500";
      return "bg-green-500";
    }
    function getStatusText() {
      if (!status.isOnline) return "Offline";
      if (status.queuedMessages > 0) return `${status.queuedMessages} queued`;
      return "Online";
    }
    $$renderer2.push(`<div class="fixed bottom-4 right-4 z-50 svelte-pz4xm9"><div${attr_class(`bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden transition-all duration-300 ${stringify("w-auto")}`, "svelte-pz4xm9")}><div class="flex items-center gap-2 p-3 cursor-pointer hover:bg-gray-50 transition-colors svelte-pz4xm9"><div class="relative svelte-pz4xm9">`);
    if (status.isOnline) {
      $$renderer2.push("<!--[-->");
      Wifi($$renderer2, { class: "w-5 h-5 text-green-600" });
    } else {
      $$renderer2.push("<!--[!-->");
      Wifi_off($$renderer2, { class: "w-5 h-5 text-red-600" });
    }
    $$renderer2.push(`<!--]--> <div${attr_class(`absolute -top-1 -right-1 w-3 h-3 rounded-full ${stringify(getStatusColor())}`, "svelte-pz4xm9", {
      "animate-pulse": !status.isOnline || status.queuedMessages > 0
    })}></div></div> <span class="font-medium text-sm svelte-pz4xm9">${escape_html(getStatusText())}</span> <div class="flex-1 svelte-pz4xm9"></div> `);
    if (status.queuedMessages > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full svelte-pz4xm9">${escape_html(status.queuedMessages)}</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    Refresh_cw($$renderer2, {
      class: `w-4 h-4 text-gray-400 transition-transform ${stringify("")}`
    });
    $$renderer2.push(`<!----></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
function ChatInterface($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="flex h-full gap-4">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="w-80 flex-shrink-0">`);
      ChatSidebar($$renderer2);
      $$renderer2.push(`<!----></div>`);
    }
    $$renderer2.push(`<!--]--> <div class="flex flex-1 flex-col"><div class="flex items-center justify-between border-b border-divider-subtle bg-background px-6 py-4"><div class="flex items-center gap-3"><button class="rounded-lg p-2 text-text-secondary hover:bg-secondary-hover md:hidden" title="Toggle sidebar">`);
    Users($$renderer2, { class: "size-5" });
    $$renderer2.push(`<!----></button> <div class="flex items-center gap-2">`);
    Message_circle($$renderer2, { class: "size-5 text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold text-text-primary">${escape_html(store_get($$store_subs ??= {}, "$activeSession", activeSession) ? `Chat Session ${store_get($$store_subs ??= {}, "$activeSession", activeSession).id.slice(-8)}` : "No Active Session")}</h2></div></div> <div class="flex items-center gap-3">`);
    ConnectionStatus($$renderer2);
    $$renderer2.push(`<!----> <button class="rounded-lg p-2 text-text-secondary hover:bg-secondary-hover" title="Chat settings">`);
    Settings($$renderer2, { class: "size-5" });
    $$renderer2.push(`<!----></button></div></div> <div class="flex-1 overflow-hidden svelte-10hnnxw">`);
    ChatMessageList($$renderer2, {
      messages: store_get($$store_subs ??= {}, "$activeMessages", activeMessages)
    });
    $$renderer2.push(`<!----></div> <div class="border-t border-divider-subtle bg-background p-4">`);
    ChatInput($$renderer2, {
      disabled: !store_get($$store_subs ??= {}, "$activeSession", activeSession),
      placeholder: store_get($$store_subs ??= {}, "$activeSession", activeSession) ? "Type your message..." : "No active session"
    });
    $$renderer2.push(`<!----></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let data = $$props["data"];
    $$renderer2.push(`<div class="flex h-full flex-col"><div class="mb-4"><h1 class="text-2xl font-bold text-text-primary">Web Chat</h1> <p class="text-text-secondary">AI-powered customer engagement</p></div> `);
    ChatInterface($$renderer2);
    $$renderer2.push(`<!----> `);
    ConnectionStatus($$renderer2);
    $$renderer2.push(`<!----></div>`);
    bind_props($$props, { data });
  });
}
export {
  _page as default
};
