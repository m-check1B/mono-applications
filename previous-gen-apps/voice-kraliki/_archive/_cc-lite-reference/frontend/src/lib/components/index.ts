/**
 * Exportable UI Components for Platform Integration
 *
 * These components can be reused across the Ocelot Platform
 */

// Note: Actual component exports will be added as components are created
// For now, we're defining the export structure

// Re-export types
export type { Call, Campaign, Agent, Analytics } from '../types';

// Mobile-first PWA components
export {
  BottomNavigation,
  FloatingActionButton,
  MobileCard,
  CallQueueMobile
} from './mobile';

// Component exports (to be implemented)
// export { default as CallQueue } from './CallQueue.svelte';
// export { default as CampaignCard } from './CampaignCard.svelte';
// export { default as AnalyticsDashboard } from './AnalyticsDashboard.svelte';
// export { default as AgentStatus } from './AgentStatus.svelte';
// export { default as LiveTranscription } from './LiveTranscription.svelte';

// Placeholder exports for now
export const components = {
  // Will be populated with actual component exports
  version: '2.0.0',
  available: [
    'CallQueue',
    'CampaignCard',
    'AnalyticsDashboard',
    'AgentStatus',
    'LiveTranscription',
    'SentimentIndicator',
    'IVRBuilder'
  ]
};

// Export component metadata
export const componentMetadata = {
  CallQueue: {
    description: 'Real-time call queue display',
    props: ['calls', 'onCallSelect', 'filters']
  },
  CampaignCard: {
    description: 'Campaign overview card',
    props: ['campaign', 'onEdit', 'onDelete', 'onStart']
  },
  AnalyticsDashboard: {
    description: 'Call analytics and metrics dashboard',
    props: ['timeRange', 'teamId', 'agentId']
  },
  AgentStatus: {
    description: 'Agent status indicator and controls',
    props: ['agent', 'onStatusChange']
  },
  LiveTranscription: {
    description: 'Real-time call transcription display',
    props: ['callId', 'transcript', 'sentiment']
  }
};

export default components;
