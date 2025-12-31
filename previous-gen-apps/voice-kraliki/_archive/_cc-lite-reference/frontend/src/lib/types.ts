/**
 * TypeScript type definitions for Voice by Kraliki module
 */

export interface Call {
  id: string;
  from_number: string;
  to_number: string;
  status: 'queued' | 'ringing' | 'in-progress' | 'completed' | 'failed' | 'no-answer' | 'busy';
  direction: 'inbound' | 'outbound';
  campaign_id?: string;
  agent_id?: string;
  duration?: number;
  recording_url?: string;
  transcript?: string;
  sentiment_score?: number;
  created_at: string;
  started_at?: string;
  ended_at?: string;
}

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed';
  type: 'outbound' | 'inbound' | 'mixed';
  contact_list_id?: string;
  script?: string;
  start_date?: string;
  end_date?: string;
  total_contacts?: number;
  completed_contacts?: number;
  success_rate?: number;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  user_id: string;
  name: string;
  email: string;
  status: 'available' | 'busy' | 'on-call' | 'away' | 'offline';
  team_id?: string;
  skills: string[];
  current_call_id?: string;
  calls_today: number;
  avg_call_duration?: number;
  satisfaction_score?: number;
  created_at: string;
  last_seen_at?: string;
}

export interface Analytics {
  total_calls: number;
  active_calls: number;
  avg_call_duration: number;
  success_rate: number;
  sentiment_avg: number;
  calls_by_status: Record<string, number>;
  calls_by_hour: Array<{ hour: number; count: number }>;
  top_agents: Array<{
    agent_id: string;
    name: string;
    calls: number;
    avg_duration: number;
  }>;
}

export interface Contact {
  id: string;
  phone_number: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  tags?: string[];
  custom_fields?: Record<string, any>;
  campaign_id?: string;
  status?: 'pending' | 'contacted' | 'completed' | 'dnc';
  created_at: string;
}

export interface Transcript {
  id: string;
  call_id: string;
  content: string;
  speaker: 'agent' | 'customer' | 'system';
  timestamp: number;
  confidence?: number;
  sentiment?: number;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  manager_id?: string;
  agent_ids: string[];
  created_at: string;
}

export interface IVRFlow {
  id: string;
  name: string;
  description?: string;
  nodes: IVRNode[];
  edges: IVREdge[];
  status: 'draft' | 'active' | 'archived';
  created_at: string;
}

export interface IVRNode {
  id: string;
  type: 'greeting' | 'menu' | 'input' | 'transfer' | 'voicemail' | 'end';
  config: Record<string, any>;
}

export interface IVREdge {
  id: string;
  source: string;
  target: string;
  condition?: string;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  secret: string;
  status: 'active' | 'inactive';
  created_at: string;
}

// Event types for platform integration
export interface PlatformEvent {
  type: string;
  data: any;
  source: string;
  timestamp: number;
}

// Module configuration types
export interface ModuleConfig {
  name: string;
  displayName: string;
  description: string;
  icon: string;
  color: string;
  version: string;
  routes: ModuleRoute[];
  apiPrefix: string;
}

export interface ModuleRoute {
  path: string;
  name: string;
  icon?: string;
  role?: string;
}
