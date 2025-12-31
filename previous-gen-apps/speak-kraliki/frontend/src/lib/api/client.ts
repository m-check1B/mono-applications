/**
 * Speak by Kraliki - API Client
 */

const API_BASE = '/api';

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: unknown;
  token?: string;
}

class ApiError extends Error {
  constructor(public status: number, message: string, public data?: unknown) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'include',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data.detail || 'Request failed', data);
  }

  return response.json();
}

// User type for auth.me
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  company_id?: string;
  company_name?: string;
}

// Auth
export const auth = {
  login: (email: string, password: string) =>
    request<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (data: { email: string; password: string; first_name: string; last_name: string; company_name: string }) =>
    request('/auth/register', { method: 'POST', body: data }),

  refresh: (refreshToken: string) =>
    request<{ access_token: string; refresh_token: string }>('/auth/refresh', {
      method: 'POST',
      body: { refresh_token: refreshToken },
    }),

  me: (token: string) =>
    request<User>('/auth/me', { token }),
};

// Surveys
export const surveys = {
  list: (token: string) =>
    request<Survey[]>('/vop/surveys', { token }),

  get: (id: string, token: string) =>
    request<Survey>(`/vop/surveys/${id}`, { token }),

  create: (data: Partial<Survey>, token: string) =>
    request<Survey>('/vop/surveys', { method: 'POST', body: data, token }),

  update: (id: string, data: Partial<Survey>, token: string) =>
    request<Survey>(`/vop/surveys/${id}`, { method: 'PATCH', body: data, token }),

  launch: (id: string, token: string) =>
    request(`/vop/surveys/${id}/launch`, { method: 'POST', token }),

  pause: (id: string, token: string) =>
    request(`/vop/surveys/${id}/pause`, { method: 'POST', token }),

  stats: (id: string, token: string) =>
    request(`/vop/surveys/${id}/stats`, { token }),
};

// Actions
export const actions = {
  list: (token: string, status?: string) =>
    request<Action[]>(`/vop/actions${status ? `?status_filter=${status}` : ''}`, { token }),

  create: (data: Partial<Action>, token: string) =>
    request<Action>('/vop/actions', { method: 'POST', body: data, token }),

  update: (id: string, data: Partial<Action>, token: string) =>
    request<Action>(`/vop/actions/${id}`, { method: 'PATCH', body: data, token }),

  public: (magicToken: string) =>
    request<ActionPublic[]>(`/vop/actions/public?token=${magicToken}`),
};

// Alerts
export const alerts = {
  list: (token: string, filters?: { severity?: string; type?: string; is_read?: boolean }) => {
    const params = new URLSearchParams();
    if (filters?.severity) params.set('severity', filters.severity);
    if (filters?.type) params.set('type_filter', filters.type);
    if (filters?.is_read !== undefined) params.set('is_read', String(filters.is_read));
    return request<Alert[]>(`/vop/alerts?${params}`, { token });
  },

  unreadCount: (token: string) =>
    request<{ unread_count: number }>('/vop/alerts/unread-count', { token }),

  update: (id: string, data: { is_read?: boolean; is_resolved?: boolean }, token: string) =>
    request<Alert>(`/vop/alerts/${id}`, { method: 'PATCH', body: data, token }),

  createAction: (id: string, token: string) =>
    request(`/vop/alerts/${id}/create-action`, { method: 'POST', token }),
};

// Insights
export const insights = {
  overview: (token: string, periodDays = 30) =>
    request(`/vop/insights/overview?period_days=${periodDays}`, { token }),

  departments: (token: string, periodDays = 30) =>
    request(`/vop/insights/departments?period_days=${periodDays}`, { token }),

  trends: (token: string, metric = 'sentiment', period = 'month') =>
    request(`/vop/insights/trends?metric=${metric}&period=${period}`, { token }),

  quotes: (token: string, limit = 10, sentiment?: string) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (sentiment) params.set('sentiment', sentiment);
    return request(`/vop/insights/quotes?${params}`, { token });
  },
};

// Department type
export interface Department {
  id: string;
  name: string;
}

// Employees
export const employees = {
  list: (token: string, departmentId?: string) => {
    const params = departmentId ? `?department_id=${departmentId}` : '';
    return request<Employee[]>(`/vop/employees${params}`, { token });
  },

  create: (data: Partial<Employee>, token: string) =>
    request<Employee>('/vop/employees', { method: 'POST', body: data, token }),

  update: (id: string, data: Partial<Employee>, token: string) =>
    request<Employee>(`/vop/employees/${id}`, { method: 'PATCH', body: data, token }),

  departments: (token: string) =>
    request<Department[]>('/vop/employees/departments/list', { token }),

  import: async (file: File, token: string) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/vop/employees/import`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'Import failed');
    }

    return response.json() as Promise<{ imported: number }>;
  },
};

// Voice (employee side)
export interface VoiceStartResponse {
  conversation_id: string;
  employee_name: string;
  websocket_url: string;
  reach?: boolean;
  reach_session_id?: string;
  mode: 'voice' | 'text';
}

export const voice = {
  start: (magicToken: string, mode = 'voice') =>
    request<VoiceStartResponse>(`/vop/voice/start?token=${magicToken}&mode=${mode}`, { method: 'POST' }),

  fallbackToText: (magicToken: string, reason = 'user_requested') =>
    request(`/vop/voice/fallback-text?token=${magicToken}&reason=${reason}`, { method: 'POST' }),

  complete: (magicToken: string, transcript: TranscriptTurn[], durationSeconds?: number) =>
    request<{ success: boolean; conversation_id: string }>(`/vop/voice/complete?token=${magicToken}`, {
      method: 'POST',
      body: {
        transcript,
        duration_seconds: durationSeconds,
      },
    }),
};

// Transcript turn type
export interface TranscriptTurn {
  role: 'ai' | 'user';
  content: string;
  timestamp?: string;
}

// Employee self-service
export const employee = {
  transcript: (magicToken: string) =>
    request<{ transcript: TranscriptTurn[]; conversation_id?: string }>(`/vop/employee/transcript/${magicToken}`),

  redact: (magicToken: string, turnIndices: number[]) =>
    request<{ success: boolean }>(`/vop/employee/transcript/${magicToken}/redact`, {
      method: 'POST',
      body: { turn_indices: turnIndices },
    }),

  consent: (magicToken: string) =>
    request<{ success: boolean }>(`/vop/employee/consent/${magicToken}`, { method: 'POST' }),

  deleteData: (magicToken: string) =>
    request<{ success: boolean }>(`/vop/employee/data/${magicToken}`, { method: 'DELETE' }),
};

// Types
export interface Survey {
  id: string;
  company_id: string;
  name: string;
  description?: string;
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed';
  frequency: 'once' | 'weekly' | 'monthly' | 'quarterly';
  questions: Array<{ id: number; question: string; follow_up_count: number }>;
  starts_at?: string;
  ends_at?: string;
  conversation_count?: number;
  completion_rate?: number;
}

export interface Action {
  id: string;
  topic: string;
  description?: string;
  status: 'new' | 'heard' | 'in_progress' | 'resolved';
  priority: 'low' | 'medium' | 'high';
  public_message?: string;
  visible_to_employees: boolean;
  created_at: string;
  resolved_at?: string;
}

export interface ActionPublic {
  id: string;
  topic: string;
  status: string;
  public_message?: string;
  created_at: string;
  resolved_at?: string;
}

export interface Alert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high';
  department_name?: string;
  description: string;
  is_read: boolean;
  is_resolved: boolean;
  created_at: string;
}

export interface Employee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  department_id?: string;
  job_title?: string;
  is_active: boolean;
  vop_opted_out: boolean;
}

export { ApiError };
