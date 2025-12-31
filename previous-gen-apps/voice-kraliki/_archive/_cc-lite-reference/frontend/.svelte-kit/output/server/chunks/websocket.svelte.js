import { a as ssr_context } from "./context.js";
import "clsx";
function onDestroy(fn) {
  /** @type {SSRContext} */
  ssr_context.r.on_destroy(fn);
}
class WebSocketStore {
  socket = null;
  connected = false;
  reconnecting = false;
  handlers = /* @__PURE__ */ new Set();
  reconnectAttempts = 0;
  maxReconnectAttempts = 5;
  reconnectDelay = 1e3;
  connect(token) {
    return;
  }
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      return;
    }
    this.reconnecting = true;
    this.reconnectAttempts++;
    setTimeout(
      () => {
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
        this.connect();
      },
      this.reconnectDelay * this.reconnectAttempts
    );
  }
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.connected = false;
    }
  }
  onMessage(handler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }
  send(message) {
    if (this.socket && this.connected) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket not connected, cannot send message");
    }
  }
}
const ws = new WebSocketStore();
export {
  onDestroy as o,
  ws as w
};
