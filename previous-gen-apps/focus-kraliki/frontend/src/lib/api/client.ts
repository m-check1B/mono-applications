/**
 * Focus by Kraliki API Client
 * Type-safe REST client for FastAPI backend
 */

type VoiceProvider = 'gemini-native' | 'openai-realtime' | 'deepgram-transcription';
type WorkflowDecisionStatus = 'approved' | 'revise' | 'rejected';

export interface ApiError {
        detail: string;
        status: number;
}

export interface BrainResponse {
        success: boolean;
        message: string;
        data?: Record<string, unknown>;
}

export class ApiClient {
        private baseURL: string;
        private token: string | null = null;

        constructor(baseURL: string) {
                this.baseURL = baseURL;
        }

        setToken(token: string | null) {
                this.token = token;
        }

        getToken(): string | null {
                return this.token;
        }

	private getHeaders(): HeadersInit {
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

                if (this.token) {
                        headers['Authorization'] = `Bearer ${this.token}`;
                }

		return headers;
	}

	private async parseErrorDetail(response: Response, fallback: string): Promise<string> {
		const responseClone = response.clone();
		try {
			const errorData = await response.json();
			if (!errorData) {
				return fallback;
			}
			if (typeof errorData === 'string') {
				return errorData || fallback;
			}
			if (typeof errorData === 'object') {
				const record = errorData as Record<string, unknown>;
				const detail =
					record.detail ||
					record.message ||
					record.error;
				return typeof detail === 'string' ? detail || fallback : fallback;
			}
			return fallback;
		} catch {
			try {
				const text = await responseClone.text();
				return text || fallback;
			} catch {
				return fallback;
			}
		}
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<T> {
                const url = `${this.baseURL}${endpoint}`;

                const response = await fetch(url, {
                        ...options,
                        headers: {
                                ...this.getHeaders(),
                                ...options.headers
                        }
                });

		if (!response.ok) {
			const errorDetail = await this.parseErrorDetail(response, 'Request failed');
			const error: ApiError = {
				detail: errorDetail,
				status: response.status
			};
			throw error;
		}

                return response.json();
        }

        async get<T>(endpoint: string): Promise<T> {
                return this.request<T>(endpoint, { method: 'GET' });
        }

        async post<T>(endpoint: string, data?: any): Promise<T> {
                return this.request<T>(endpoint, {
                        method: 'POST',
                        body: data ? JSON.stringify(data) : undefined
                });
        }

        async patch<T>(endpoint: string, data: any): Promise<T> {
                return this.request<T>(endpoint, {
                        method: 'PATCH',
                        body: JSON.stringify(data)
                });
        }

        async put<T>(endpoint: string, data: any): Promise<T> {
                return this.request<T>(endpoint, {
                        method: 'PUT',
                        body: JSON.stringify(data)
                });
        }

        async delete<T>(endpoint: string): Promise<T> {
                return this.request<T>(endpoint, { method: 'DELETE' });
        }

        // Auth endpoints
        auth = {
                register: (data: { email: string; password: string; name: string }) =>
                        this.post('/auth/register', data),
                login: (data: { email: string; password: string }) =>
                        this.post('/auth/login', data),
                me: () => this.get('/auth/me'),
                logout: () => this.post('/auth/logout')
        };

        // Google OAuth endpoints (FastAPI mounts them at /auth/google/*)
        google = {
                getAuthUrl: (data: { redirect_uri: string; state: string }) =>
                        this.post('/auth/google/url', data),
                login: (data: { code: string; redirect_uri: string }) =>
                        this.post('/auth/google/login', data),
                link: (data: { code: string; redirect_uri: string }) =>
                        this.post('/auth/google/link', data),
                unlink: () => this.post('/auth/google/unlink')
        };

        // User endpoints
        users = {
                getProfile: () => this.get('/users/profile'),
                updateProfile: (data: any) => this.patch('/users/profile', data),
                getPreferences: () => this.get('/users/preferences'),
                updatePreferences: (data: any) => this.post('/users/preferences', data)
        };

        // Task endpoints
        tasks = {
                list: (params?: { status?: string; type?: string; priority?: string }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/tasks${query}`);
                },
                create: (data: any) => this.post('/tasks', data),
                get: (taskId: string) => this.get(`/tasks/${taskId}`),
                update: (taskId: string, data: any) => this.patch(`/tasks/${taskId}`, data),
                delete: (taskId: string) => this.delete(`/tasks/${taskId}`),
                toggle: (taskId: string) => this.post(`/tasks/${taskId}/toggle`),
                stats: () => this.get('/tasks/stats/summary'),
                search: (query: string) => this.get(`/tasks/search?q=${encodeURIComponent(query)}`)
        };

        // Project endpoints
        projects = {
                list: () => this.get('/projects'),
                create: (data: { name: string; description?: string; color?: string; icon?: string }) =>
                        this.post('/projects', data),
                get: (projectId: string) => this.get(`/projects/${projectId}`),
                update: (projectId: string, data: any) => this.patch(`/projects/${projectId}`, data),
                delete: (projectId: string) => this.delete(`/projects/${projectId}`),

                // Templates
                listTemplates: () => this.get('/projects/templates/list'),
                createFromTemplate: (templateId: string, customName?: string) => {
                        const query = customName ? `?custom_name=${encodeURIComponent(customName)}` : '';
                        return this.post(`/projects/templates/${templateId}/create${query}`);
                },

                // Progress
                getProgress: (projectId: string) => this.get(`/projects/${projectId}/progress`)
        };

        // Events endpoints
        events = {
                list: (params: { startDate: string; endDate: string }) => {
                        const query = new URLSearchParams({
                                start_date: params.startDate,
                                end_date: params.endDate
                        }).toString();
                        return this.get(`/events?${query}`);
                },
                create: (data: any) => this.post('/events', data),
                syncGoogle: () => this.post('/events/sync/google')
        };

        integration = {
                calendarStatus: () => this.get('/integration/calendar/status'),
                createCalendarEvent: (data: { title: string; duration_minutes?: number }) =>
                        this.post('/integration/calendar/events', data)
        };

        // Time entry endpoints
        timeEntries = {
                list: (params?: { limit?: number }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/time-entries${query}`);
                },
                stats: () => this.get('/time-entries/stats/summary'),
                active: () => this.get('/time-entries/active'),
                create: (data: any) => this.post('/time-entries', data),
                stop: (entryId: string, data?: any) => this.post(`/time-entries/${entryId}/stop`, data || {}),
                delete: (entryId: string) => this.delete(`/time-entries/${entryId}`)
        };

        // AI endpoints
        ai = {
                chat: (data: { message: string; conversation_history?: any[]; model?: string; useHighReasoning?: boolean }) =>
                        this.post('/ai/chat', data),
                parseTask: (data: { input: string }) =>
                        this.post('/ai/parse-task', data),
                enhanceInput: (data: { input: string; context?: string }) =>
                        this.post('/ai/enhance-input', data),
                analyzeTask: (data: { task_id: string }) =>
                        this.post('/ai/analyze-task', data),
                orchestrateTask: (data: { input: string; use_high_reasoning?: boolean; telemetryId?: string; context?: any }) =>
                        this.post('/ai/orchestrate-task', data),
                highReasoning: (data: { prompt: string; task_context?: any }) =>
                        this.post('/ai/high-reasoning', data),
                generateInsights: () => this.post('/ai/insights'),
                getTaskRecommendations: () => this.post('/ai/task-recommendations'),
                saveNote: (data: { content: string; task_id?: string }) =>
                        this.post('/ai/notes', data),
                getNotes: () => this.get('/ai/notes'),
                saveMemory: (data: { key: string; value: any; context?: string }) =>
                        this.post('/ai/memory/save', data),
                recallMemory: (data: { query: string }) =>
                        this.post('/ai/memory/recall', data),
                analyzeCognitiveState: () =>
                        this.post('/ai/cognitive-state'),
                markTelemetryRoute: (telemetryId: string, data: { route: 'deterministic' | 'orchestrated'; reason?: Record<string, unknown> }) =>
                        this.post(`/ai/telemetry/${telemetryId}/route`, data),
                recordWorkflowDecision: (telemetryId: string, data: { status: WorkflowDecisionStatus; notes?: Record<string, unknown> }) =>
                        this.post(`/ai/telemetry/${telemetryId}/decision`, data),
                telemetrySummary: () => this.get('/ai/telemetry/summary')
        };

        // Shadow Work endpoints
        shadow = {
                analyze: (data: { task_patterns?: any; recent_activity?: any }) =>
                        this.post('/shadow/analyze', data),
                getInsights: () => this.get('/shadow/insights'),
                acknowledgeInsight: (insightId: string) =>
                        this.post(`/shadow/insights/${insightId}/acknowledge`),
                getUnlockStatus: () => this.get('/shadow/unlock-status')
        };

        // Voice/Assistant endpoints
        assistant = {
                // Voice transcription - upload audio file
				transcribeAudio: async (audioBlob: Blob, language: string = 'en', provider?: string) => {
					const formData = new FormData();
					formData.append('audio', audioBlob, 'recording.webm');
					formData.append('language', language);
					if (provider) formData.append('provider', provider);

					const response = await fetch(`${this.baseURL}/voice/transcribe`, {
						method: 'POST',
						headers: {
							Authorization: `Bearer ${this.getToken()}`
						},
						body: formData
					});
					if (!response.ok) {
						const errorDetail = await this.parseErrorDetail(
							response,
							'Voice transcription failed'
						);
						throw new Error(errorDetail);
					}
					return response.json();
				},
                // Voice processing - analyze transcript with AI
                processVoice: (data: { transcript: string; recordingId?: string }) =>
                        this.post('/voice/process', data),
                // Voice to task - convert voice input to task
                voiceToTask: (data: { transcript: string; recordingId?: string; forceCreate?: boolean }) =>
                        this.post('/voice/to-task', data),
                // Get available voice providers
                getProviders: () => this.get('/voice/providers'),
                // Get voice recordings
                getRecordings: (limit?: number, offset?: number) => {
                        const params = new URLSearchParams();
                        if (limit) params.append('limit', String(limit));
                        if (offset) params.append('offset', String(offset));
                        return this.get(`/voice/recordings?${params.toString()}`);
                },
                // Legacy methods (kept for compatibility)
                textToSpeech: (data: { text: string; provider?: VoiceProvider; voice?: string; language?: string; format?: string }) =>
                        this.post('/assistant/tts', data),
                chat: (data: { message: string; conversation_history?: any[] }) =>
                        this.post('/assistant/chat', data)
        };
        // Pricing endpoints
        pricing = {
                listModels: () => this.get('/pricing/models')
        };

        // Billing endpoints
        billing = {
                getPlans: () => this.get('/billing/plans'),
                createCheckoutSession: (data: { plan: 'monthly' | 'yearly'; success_url?: string; cancel_url?: string }) =>
                        this.post('/billing/checkout-session', data),
                createSubscription: (data: { paymentMethodId: string }) =>
                        this.post('/billing/create-subscription', data),
                cancelSubscription: () => this.post('/billing/cancel-subscription'),
                reactivateSubscription: () => this.post('/billing/reactivate-subscription'),
                portalSession: () => this.get('/billing/portal-session'),
                subscriptionStatus: () => this.get('/billing/subscription-status')
        };

        // Workflow endpoints
        workflow = {
                createTemplate: (data: any) => this.post('/workflow/templates', data),
                listTemplates: (params?: { category?: string; include_system?: boolean; include_public?: boolean }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/workflow/templates${query}`);
                },
                getTemplate: (templateId: string) => this.get(`/workflow/templates/${templateId}`),
                updateTemplate: (templateId: string, data: any) => this.put(`/workflow/templates/${templateId}`, data),
                deleteTemplate: (templateId: string) => this.delete(`/workflow/templates/${templateId}`),
                execute: (data: { templateId: string; startDate?: string; priority?: number; customTitle?: string; additionalTags?: string[] }) =>
                        this.post('/workflow/execute', data),
                generate: (data: { description: string; category?: string }) =>
                        this.post('/workflow/generate', data),
                getCategories: () => this.get('/workflow/categories')
        };

        // Exports endpoints
        exports = {
                generateInvoice: (data: {
                        start_date: string;
                        end_date: string;
                        project_id?: string;
                        client_name?: string;
                        invoice_number?: string;
                        hourly_rate?: number;
                        format?: 'csv' | 'json' | 'pdf';
                        include_non_billable?: boolean;
                }) => this.post('/exports/invoices/generate', data),
                getBillableSummary: (params: { start_date: string; end_date: string; project_id?: string }) => {
                        const query = new URLSearchParams(params as any).toString();
                        return this.get(`/exports/billable/summary?${query}`);
                },
                getWeeklyBillable: (weeks: number = 4) => this.get(`/exports/billable/weekly?weeks=${weeks}`)
        };

        // Swarm tools endpoints
        swarm = {
                createTaskFromNL: (data: { natural_language: string }) =>
                        this.post('/swarm-tools/tasks/create-from-nl', data),
                getTaskWithContext: (data: { task_id: string }) =>
                        this.post('/swarm-tools/tasks/get-with-context', data),
                createSubtasks: (data: { parent_task_id: string; num_subtasks?: number }) =>
                        this.post('/swarm-tools/tasks/create-subtasks', data),
                getRecommendations: (params?: { limit?: number }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/swarm-tools/tasks/recommendations${query}`);
                },
                updateCognitiveState: (data: { state_type: string; value: number; context?: string }) =>
                        this.post('/swarm-tools/cognitive/update-state', data),
                getLatestCognitive: () => this.get('/swarm-tools/cognitive/latest'),
                getCognitiveTrends: (params?: { days?: number }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/swarm-tools/cognitive/trends${query}`);
                }
        };

        // Knowledge endpoints
        knowledge = {
                // Item Types
                listItemTypes: (params?: { limit?: number }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/knowledge/item-types${query}`);
                },
                createItemType: (data: { name: string; icon?: string; color?: string }) =>
                        this.post('/knowledge/item-types', data),
                getItemType: (typeId: string) => this.get(`/knowledge/item-types/${typeId}`),
                updateItemType: (typeId: string, data: any) =>
                        this.patch(`/knowledge/item-types/${typeId}`, data),
                deleteItemType: (typeId: string) => this.delete(`/knowledge/item-types/${typeId}`),

                // Knowledge Items
                listKnowledgeItems: (params?: { typeId?: string; completed?: boolean; limit?: number }) => {
                        const query = params ? `?${new URLSearchParams(params as any).toString()}` : '';
                        return this.get(`/knowledge/items${query}`);
                },
                createKnowledgeItem: (data: { typeId: string; title: string; content: string; item_metadata?: any; completed?: boolean }) =>
                        this.post('/knowledge/items', data),
                getKnowledgeItem: (itemId: string) => this.get(`/knowledge/items/${itemId}`),
                updateKnowledgeItem: (itemId: string, data: any) =>
                        this.patch(`/knowledge/items/${itemId}`, data),
                deleteKnowledgeItem: (itemId: string) => this.delete(`/knowledge/items/${itemId}`),
                toggleKnowledgeItem: (itemId: string) => this.post(`/knowledge/items/${itemId}/toggle`),
                searchKnowledgeItems: (query: string, typeId?: string) => {
                        const params = new URLSearchParams({ query });
                        if (typeId) params.append('typeId', typeId);
                        return this.get(`/knowledge/search?${params.toString()}`);
                }
        };

        // Agent endpoints (II-Agent integration)
        agent = {
                createSession: (data?: { telemetryId?: string; reason?: Record<string, unknown> }) =>
                        this.post('/agent/sessions', data || {})
        };

        // Settings endpoints
        settings = {
                saveOpenRouterKey: (data: { apiKey: string }) =>
                        this.post('/settings/openrouter-key', data),
                deleteOpenRouterKey: () =>
                        this.delete('/settings/openrouter-key'),
                testOpenRouterKey: (data: { apiKey: string }) =>
                        this.post('/settings/test-openrouter-key', data),
                getUsageStats: () =>
                        this.get('/settings/usage-stats')
        };

        // Push Notifications endpoints
        notifications = {
                getVapidKey: () =>
                        this.get('/notifications/vapid-key'),
                subscribe: (data: { endpoint: string; keys: { p256dh: string; auth: string } }) =>
                        this.post('/notifications/subscribe', data),
                unsubscribe: () =>
                        this.delete('/notifications/subscribe'),
                getPreferences: () =>
                        this.get('/notifications/preferences'),
                updatePreferences: (data: {
                        taskReminders?: boolean;
                        dailyDigest?: boolean;
                        pomodoroAlerts?: boolean;
                        projectUpdates?: boolean;
                }) => this.patch('/notifications/preferences', data),
                test: () =>
                        this.post('/notifications/test', {})
        };

        // Analytics endpoints
        analytics = {
                overview: (params?: { workspaceId?: string }) => {
                        const query = params?.workspaceId ? `?workspaceId=${params.workspaceId}` : '';
                        return this.get(`/analytics/overview${query}`);
                },
                bottlenecks: (params?: { workspaceId?: string }) => {
                        const query = params?.workspaceId ? `?workspaceId=${params.workspaceId}` : '';
                        return this.get(`/analytics/bottlenecks${query}`);
                }
        };

        // Workspace endpoints
        workspaces = {
                list: () => this.get('/workspaces'),
                create: (data: { name: string; description?: string; color?: string }) =>
                        this.post('/workspaces', data),
                get: (workspaceId: string) => this.get(`/workspaces/${workspaceId}`),
                switch: (workspaceId: string) =>
                        this.post('/workspaces/switch', { workspaceId }),
                members: (workspaceId: string) => this.get(`/workspaces/${workspaceId}/members`),
                inviteMember: (workspaceId: string, data: { email: string; role?: string }) =>
                        this.post(`/workspaces/${workspaceId}/members`, data),
                updateMember: (workspaceId: string, memberId: string, data: any) =>
                        this.patch(`/workspaces/${workspaceId}/members/${memberId}`, data),
                removeMember: (workspaceId: string, memberId: string) =>
                        this.delete(`/workspaces/${workspaceId}/members/${memberId}`)
        };

        // Onboarding endpoints (Track 5)
        onboarding = {
                getStatus: () => this.get('/onboarding/status'),
                listPersonas: () => this.get('/onboarding/personas'),
                getPersona: (personaId: string) => this.get(`/onboarding/personas/${personaId}`),
                selectPersona: (data: { personaId: string }) =>
                        this.post('/onboarding/select-persona', data),
                updatePrivacyPreferences: (data: {
                        geminiFileSearchEnabled: boolean;
                        iiAgentEnabled: boolean;
                        dataPrivacyAcknowledged: boolean;
                }) => this.post('/onboarding/privacy-preferences', data),
                updateFeatureToggles: (data: {
                        geminiFileSearch: boolean;
                        iiAgent: boolean;
                        voiceTranscription: boolean;
                }) => this.post('/onboarding/feature-toggles', data),
                complete: (data: {}) => this.post('/onboarding/complete', data),
                skip: () => this.post('/onboarding/skip', {})
        };

        // Brain endpoints - AI Brain Organizer
        brain = {
                // AI-First Capture: Say anything, Brain organizes it
                capture: (data: { input: string; create?: boolean }) =>
                        this.post<BrainResponse>('/brain/capture', data),
                // Get summary of all captured items by type
                summary: () =>
                        this.get<BrainResponse>('/brain/summary'),
                // Parse natural language goal into project + tasks
                understandGoal: (data: { goal: string; create_project?: boolean }) =>
                        this.post<BrainResponse>('/brain/understand-goal', data),
                // Get daily plan: "Good morning! Here's your day..."
                dailyPlan: () =>
                        this.get<BrainResponse>('/brain/daily-plan'),
                // Ask the Brain anything about your work
                ask: (data: { question: string; context?: Record<string, unknown> }) =>
                        this.post<BrainResponse>('/brain/ask', data),
                // What should you do RIGHT NOW?
                nextAction: () =>
                        this.get<BrainResponse>('/brain/next-action'),
                // Check Brain health
                health: () =>
                        this.get<{ status: string; service: string }>('/brain/health')
        };
}

// Create singleton instance
// Use /api for proxy through SvelteKit server (works in both dev and production)
export const api = new ApiClient('/api');
