/**
 * REST API Client for Voice by Kraliki Python Backend
 * Replaces tRPC client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:3010';

interface RequestOptions extends RequestInit {
  auth?: boolean;
}

class APIClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    // Load token from localStorage if available
    this.accessToken = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.accessToken = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.accessToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { auth = true, ...fetchOptions } = options;

    const headers = new Headers(fetchOptions.headers as HeadersInit | undefined);
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    if (auth && this.accessToken) {
      headers.set('Authorization', `Bearer ${this.accessToken}`);
    }

    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      });

      // Handle 401 Unauthorized - token expired
      if (response.status === 401 && auth) {
        // Try to refresh token
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry request with new token
          return this.request<T>(endpoint, options);
        } else {
          // Refresh failed, clear token and redirect to login
          this.clearToken();
          window.location.href = '/login';
          throw new Error('Authentication failed');
        }
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return null as T;
      }

      return response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      this.setToken(data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // Authentication
  auth = {
    register: (data: {
      email: string;
      password: string;
      first_name: string;
      last_name: string;
      role?: string;
    }) =>
      this.request<any>('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
        auth: false,
      }),

    login: (email: string, password: string) =>
      this.request<{
        user: any;
        access_token: string;
        refresh_token: string;
        token_type: string;
      }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        auth: false,
      }).then((response) => {
        // Save tokens
        this.setToken(response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        return response;
      }),

    logout: () =>
      this.request('/api/auth/logout', {
        method: 'POST',
      }).then(() => {
        this.clearToken();
      }),

    me: () => this.request<any>('/api/auth/me'),
  };

  // Calls
  calls = {
    list: (params?: { page?: number; page_size?: number; status?: string }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/calls/?${query}`);
    },

    get: (id: string) => this.request<any>(`/api/calls/${id}`),

    create: (data: {
      from_number: string;
      to_number: string;
      direction: string;
      campaign_id?: string;
    }) =>
      this.request<any>('/api/calls/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: any) =>
      this.request<any>(`/api/calls/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (id: string) =>
      this.request<void>(`/api/calls/${id}`, {
        method: 'DELETE',
      }),
  };

  // Campaigns
  campaigns = {
    list: (params?: { skip?: number; limit?: number; active?: boolean }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any[]>(`/api/campaigns/?${query}`);
    },

    get: (id: string) => this.request<any>(`/api/campaigns/${id}`),

    create: (data: any) =>
      this.request<any>('/api/campaigns/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: any) =>
      this.request<any>(`/api/campaigns/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (id: string) =>
      this.request<void>(`/api/campaigns/${id}`, {
        method: 'DELETE',
      }),
  };

  // Agents
  agents = {
    list: (params?: { status?: string; skip?: number; limit?: number }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any[]>(`/api/agents/?${query}`);
    },

    get: (id: string) => this.request<any>(`/api/agents/${id}`),

    create: (data: any) =>
      this.request<any>('/api/agents/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: any) =>
      this.request<any>(`/api/agents/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    updateStatus: (id: string, status: string) =>
      this.request<any>(`/api/agents/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),

    availableCount: () =>
      this.request<{ available_agents: number }>('/api/agents/available/count'),
  };

  // Teams
  teams = {
    list: (params?: { skip?: number; limit?: number }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/teams/?${query}`);
    },

    get: (id: string) => this.request<any>(`/api/teams/${id}`),

    create: (data: any) =>
      this.request<any>('/api/teams/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: any) =>
      this.request<any>(`/api/teams/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (id: string) =>
      this.request<void>(`/api/teams/${id}`, {
        method: 'DELETE',
      }),

    addMember: (teamId: string, data: { user_id: string; role?: string }) =>
      this.request<any>(`/api/teams/${teamId}/members`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    removeMember: (teamId: string, userId: string) =>
      this.request<void>(`/api/teams/${teamId}/members/${userId}`, {
        method: 'DELETE',
      }),

    listMembers: (teamId: string) =>
      this.request<any[]>(`/api/teams/${teamId}/members`),
  };

  // Webhooks (for testing)
  webhooks = {
    health: () => this.request<any>('/api/webhooks/health'),
  };

  // Analytics
  analytics = {
    dashboard: () => this.request<any>('/api/analytics/dashboard'),

    calls: (params?: { start_date?: string; end_date?: string; group_by?: string }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/analytics/calls?${query}`);
    },

    agents: (params?: { start_date?: string; end_date?: string }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any[]>(`/api/analytics/agents?${query}`);
    },

    campaigns: () => this.request<any[]>('/api/analytics/campaigns'),
  };

  // Supervisor
  supervisor = {
    activeCalls: () => this.request<any>('/api/supervisor/active-calls'),

    callSummary: (callId: string) =>
      this.request<any>(`/api/supervisor/calls/${callId}/summary`),

    monitorCall: (callId: string) =>
      this.request<any>(`/api/supervisor/calls/${callId}/monitor`, {
        method: 'POST',
      }),

    whisper: (callId: string, message: string) =>
      this.request<any>(`/api/supervisor/calls/${callId}/whisper`, {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),

    bargeIn: (callId: string) =>
      this.request<any>(`/api/supervisor/calls/${callId}/barge-in`, {
        method: 'POST',
      }),

    endCall: (callId: string) =>
      this.request<any>(`/api/supervisor/calls/${callId}/end`, {
        method: 'POST',
      }),
  };

  // Contacts
  contacts = {
    list: (params?: { campaign_id?: string; status?: string; skip?: number; limit?: number }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/contacts/?${query}`);
    },

    get: (id: string) => this.request<any>(`/api/contacts/${id}`),

    create: (data: any) =>
      this.request<any>('/api/contacts/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: string, data: any) =>
      this.request<any>(`/api/contacts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    delete: (id: string) =>
      this.request<void>(`/api/contacts/${id}`, {
        method: 'DELETE',
      }),

    bulkImport: (campaignId: string, file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return fetch(`${this.baseUrl}/api/contacts/bulk-import?campaign_id=${campaignId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
        },
        body: formData,
      }).then(r => r.json());
    },
  };

  // Sentiment Analysis
  sentiment = {
    analyze: (data: {
      text: string;
      call_id: string;
      session_id?: string;
      transcript_id?: string;
      context?: any;
    }) =>
      this.request<any>('/api/sentiment/analyze', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    batchAnalyze: (analyses: any[]) =>
      this.request<any>('/api/sentiment/analyze/batch', {
        method: 'POST',
        body: JSON.stringify({ analyses }),
      }),

    getHistory: (callId: string, params?: { limit?: number; offset?: number }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/sentiment/history/${callId}?${query}`);
    },

    getRealTime: (sessionId: string, includeHistory = true) =>
      this.request<any>(
        `/api/sentiment/realtime/${sessionId}?include_history=${includeHistory}`
      ),

    getAnalytics: (params?: {
      start_date?: string;
      end_date?: string;
      call_ids?: string[];
      agent_id?: string;
      sentiment_type?: string;
      emotion_type?: string;
    }) => {
      const query = new URLSearchParams();
      if (params?.start_date) query.set('start_date', params.start_date);
      if (params?.end_date) query.set('end_date', params.end_date);
      if (params?.agent_id) query.set('agent_id', params.agent_id);
      if (params?.sentiment_type) query.set('sentiment_type', params.sentiment_type);
      if (params?.emotion_type) query.set('emotion_type', params.emotion_type);
      return this.request<any>(`/api/sentiment/analytics?${query.toString()}`);
    },

    generateCallSummary: (callId: string) =>
      this.request<any>(`/api/sentiment/calls/${callId}/summary`, {
        method: 'POST',
      }),

    getAlerts: (params?: { severity?: string; alert_type?: string; limit?: number }) => {
      const query = new URLSearchParams(params as any).toString();
      return this.request<any>(`/api/sentiment/alerts?${query}`);
    },

    getHealth: () => this.request<any>('/api/sentiment/health'),

    cleanup: (maxAgeHours = 24) =>
      this.request<any>(`/api/sentiment/cleanup?max_age_hours=${maxAgeHours}`, {
        method: 'POST',
      }),
  };
}

// Export singleton instance
export const api = new APIClient(API_BASE_URL);

// Export types
export type { APIClient };
