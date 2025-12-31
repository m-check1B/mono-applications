import { ws } from './websocket.svelte';

type Agent = {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  status: 'AVAILABLE' | 'BUSY' | 'BREAK' | 'OFFLINE';
  currentCallId?: string;
};

class AgentsStore {
  agents = $state<Agent[]>([]);
  loading = $state(false);

  constructor() {
    // Subscribe to WebSocket messages
    ws.onMessage((message) => {
      if (message.type === 'agent:status') {
        this.updateAgentStatus(message.agentId, message.status as any);
      }
    });
  }

  setAgents(agents: Agent[]) {
    this.agents = agents;
  }

  private updateAgentStatus(agentId: string, status: Agent['status']) {
    const index = this.agents.findIndex(a => a.id === agentId);
    if (index !== -1) {
      this.agents[index] = { ...this.agents[index], status };
    }
  }

  get availableAgents() {
    return this.agents.filter(a => a.status === 'AVAILABLE');
  }

  get busyAgents() {
    return this.agents.filter(a => a.status === 'BUSY');
  }

  get onBreakAgents() {
    return this.agents.filter(a => a.status === 'BREAK');
  }

  get offlineAgents() {
    return this.agents.filter(a => a.status === 'OFFLINE');
  }
}

export const agents = new AgentsStore();
