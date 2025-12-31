/**
 * Voice by Kraliki Frontend Module Export
 * For integration into Ocelot Platform
 */

export const MODULE_CONFIG = {
  name: 'cc-lite',
  displayName: 'Communications',
  description: 'Multichannel communications and call center management',
  icon: 'phone',
  color: '#3b82f6',
  version: '2.0.0',
  routes: [
    { path: '/calls', name: 'Calls', icon: 'phone' },
    { path: '/campaigns', name: 'Campaigns', icon: 'megaphone' },
    { path: '/analytics', name: 'Analytics', icon: 'chart-bar' },
    { path: '/agents', name: 'Agents', icon: 'users' },
    { path: '/supervisor', name: 'Supervisor', icon: 'eye', role: 'SUPERVISOR' }
  ],
  apiPrefix: '/api/communications'
};

// Export module metadata
export const metadata = {
  version: '2.0.0',
  author: 'Ocelot Platform',
  description: 'Multichannel communications module with AI-powered call center',
  capabilities: [
    'voice_calls',
    'sms_messaging',
    'campaigns',
    'call_analytics',
    'sentiment_analysis',
    'real_time_transcription',
    'ai_agent_assist',
    'ivr_system',
    'call_recording',
    'team_management'
  ],
  dependencies: {
    platform: '^1.0.0',
    eventBus: '^1.0.0'
  }
};

// Module lifecycle hooks
export interface ModuleLifecycle {
  onMount?: () => Promise<void>;
  onUnmount?: () => Promise<void>;
  onEvent?: (event: PlatformEvent) => Promise<void>;
}

export interface PlatformEvent {
  type: string;
  data: any;
  source: string;
  timestamp: number;
}

// Export module class for platform integration
export class CommunicationsModule implements ModuleLifecycle {
  private eventBus?: any;
  private apiClient?: any;

  constructor(config?: {
    eventBus?: any;
    apiClient?: any;
  }) {
    this.eventBus = config?.eventBus;
    this.apiClient = config?.apiClient;
  }

  async onMount(): Promise<void> {
    console.log('[Voice by Kraliki] Communications module mounted');

    // Subscribe to relevant platform events
    if (this.eventBus) {
      await this.eventBus.subscribe('planning.*', this.onEvent.bind(this));
      await this.eventBus.subscribe('crm.*', this.onEvent.bind(this));
      await this.eventBus.subscribe('tasks.*', this.onEvent.bind(this));
    }
  }

  async onUnmount(): Promise<void> {
    console.log('[Voice by Kraliki] Communications module unmounted');

    // Cleanup subscriptions
    if (this.eventBus) {
      await this.eventBus.unsubscribe('planning.*');
      await this.eventBus.unsubscribe('crm.*');
      await this.eventBus.unsubscribe('tasks.*');
    }
  }

  async onEvent(event: PlatformEvent): Promise<void> {
    console.log('[Voice by Kraliki] Received platform event:', event.type);

    // Handle different event types
    switch (event.type) {
      case 'planning.task.completed':
        // Trigger follow-up campaign or notification
        console.log('[Voice by Kraliki] Task completed, checking for campaign triggers');
        break;

      case 'crm.contact.created':
        // Add contact to communications database
        console.log('[Voice by Kraliki] New contact created, syncing to communications');
        break;

      case 'tasks.milestone_reached':
        // Send notification to team
        console.log('[Voice by Kraliki] Milestone reached, sending notifications');
        break;

      default:
        console.log('[Voice by Kraliki] Unhandled event type:', event.type);
    }
  }

  // Module-specific methods
  async makeCall(params: {
    to: string;
    from?: string;
    campaignId?: string;
  }): Promise<any> {
    if (!this.apiClient) {
      throw new Error('API client not configured');
    }

    return await this.apiClient.post('/api/communications/calls', params);
  }

  async getCampaigns(filters?: any): Promise<any> {
    if (!this.apiClient) {
      throw new Error('API client not configured');
    }

    return await this.apiClient.get('/api/communications/campaigns', { params: filters });
  }
}

// Export for platform registration
export default {
  MODULE_CONFIG,
  metadata,
  CommunicationsModule
};
