import { ws } from './websocket.svelte';

type Call = {
  id: string;
  fromNumber: string;
  toNumber: string;
  status: string;
  direction: 'INBOUND' | 'OUTBOUND';
  startTime: string;
  agentId?: string;
};

class CallsStore {
  activeCalls = $state<Call[]>([]);
  queuedCalls = $state<Call[]>([]);

  constructor() {
    // Subscribe to WebSocket messages
    ws.onMessage((message) => {
      if (message.type === 'call:created') {
        this.addCall(message.call);
      } else if (message.type === 'call:updated') {
        this.updateCall(message.call);
      } else if (message.type === 'call:ended') {
        this.removeCall(message.callId);
      }
    });
  }

  private addCall(call: Call) {
    if (call.status === 'QUEUED') {
      this.queuedCalls = [...this.queuedCalls, call];
    } else if (call.status === 'IN_PROGRESS' || call.status === 'RINGING') {
      this.activeCalls = [...this.activeCalls, call];
    }
  }

  private updateCall(call: Call) {
    // Remove from both lists
    this.activeCalls = this.activeCalls.filter(c => c.id !== call.id);
    this.queuedCalls = this.queuedCalls.filter(c => c.id !== call.id);

    // Add to appropriate list
    this.addCall(call);
  }

  private removeCall(callId: string) {
    this.activeCalls = this.activeCalls.filter(c => c.id !== callId);
    this.queuedCalls = this.queuedCalls.filter(c => c.id !== callId);
  }

  setActiveCalls(calls: Call[]) {
    this.activeCalls = calls.filter(c => c.status === 'IN_PROGRESS' || c.status === 'RINGING');
  }

  setQueuedCalls(calls: Call[]) {
    this.queuedCalls = calls.filter(c => c.status === 'QUEUED');
  }
}

export const calls = new CallsStore();
