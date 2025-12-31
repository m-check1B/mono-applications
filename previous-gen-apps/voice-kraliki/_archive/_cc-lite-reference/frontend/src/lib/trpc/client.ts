import { api } from '$lib/api/client';

type QueryHandler = (input?: any) => Promise<any>;
type MutationHandler = (input: any) => Promise<any>;

const query = (handler: QueryHandler) => ({
  query: (input?: any) => handler(input),
});

const mutation = (handler: MutationHandler) => ({
  mutate: (input: any) => handler(input),
});

const withDefaultCounts = (campaign: any) => ({
  ...campaign,
  _count: campaign._count ?? { sessions: 0, metrics: 0 },
});

export const trpc = {
  auth: {
    me: query(async () => {
      const user = await api.auth.me().catch(() => null);
      if (!user) throw new Error('Not authenticated');
      return { user };
    }),
    login: mutation(async ({ email, password }: { email: string; password: string }) =>
      api.auth.login(email, password)
    ),
    logout: mutation(async () => {
      await api.auth.logout().catch(() => undefined);
      return { success: true };
    }),
  },

  campaign: {
    list: query(async ({ limit = 20, offset = 0 } = {}) => {
      const data = await api.campaigns
        .list({ limit, skip: offset })
        .catch(() => []);
      return { campaigns: data.map(withDefaultCounts) };
    }),
    create: mutation(async (payload: any) => {
      const created = await api.campaigns.create({
        name: payload.name,
        description: payload.description,
        type: payload.type ?? 'OUTBOUND',
        language: payload.language ?? 'en',
        organization_id: payload.organizationId ?? 'demo-org',
        instructions: payload.instructions ?? { script: payload.script ?? '' },
        tools: payload.tools ?? {},
        voice: payload.voice ?? {},
        analytics: payload.analytics ?? {},
        metadata: payload.metadata ?? {},
      });
      return withDefaultCounts(created);
    }),
    update: mutation(async ({ id, ...data }: any) => {
      const updated = await api.campaigns.update(id, data);
      return withDefaultCounts(updated);
    }),
    pause: mutation(async ({ id }: { id: string }) => {
      await api.campaigns.update(id, { active: false });
      return { success: true };
    }),
    start: mutation(async ({ id }: { id: string }) => {
      await api.campaigns.update(id, { active: true });
      return { success: true };
    }),
    delete: mutation(async ({ id }: { id: string }) => {
      await api.campaigns.delete(id);
      return { success: true };
    }),
  },

  telephony: {
    getRecording: query(async () => {
      throw new Error('Recording lookup not yet implemented on FastAPI backend');
    }),
    getCallHistory: query(async () => {
      throw new Error('Call history not yet implemented on FastAPI backend');
    }),
    transferCall: mutation(async () => ({ success: true })),
    hangupCall: mutation(async () => ({ success: true })),
    createCall: mutation(async ({ to }: { to: string }) => ({
      callId: `mock-${Date.now()}`,
      to,
    })),
    getToken: query(async () => ({
      token: 'mock-token',
      identity: 'demo-agent',
    })),
    getAllActiveCalls: query(async () => []),
  },

  agentAssist: {
    suggestions: mutation(async () => ({
      suggestions: [
        {
          id: `suggestion-${Date.now()}`,
          type: 'advice',
          text: 'Acknowledge the issue and offer to escalate if the customer remains unsatisfied.',
          confidence: 0.65,
        },
      ],
      articles: [],
    })),
  },

  dashboard: {
    getOverview: query(async () => ({
      stats: {
        totalCalls: 24,
        avgDuration: 185,
        satisfaction: 94,
      },
    })),
  },

  agent: {
    list: query(async ({ limit = 100, offset = 0 } = {}) => {
      const agents = await api.agents.list({ limit, skip: offset }).catch(() => []);
      return { agents };
    }),
    updateStatus: mutation(async () => ({ success: true })),
  },

  supervisor: {
    getOverview: query(async () => ({
      stats: {
        activeCalls: 0,
        availableAgents: 0,
        avgWaitTime: 0,
        satisfaction: 0,
      },
    })),
  },
};

export type TrpcBridge = typeof trpc;
