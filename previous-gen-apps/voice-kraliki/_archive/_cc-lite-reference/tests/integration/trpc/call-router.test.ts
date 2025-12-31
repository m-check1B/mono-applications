import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createTRPCMsw } from 'msw-trpc';
import { setupServer } from 'msw/node';
import { callRouter } from '../../../server/trpc/routers/call';
import { createTRPCClient, httpBatchLink } from '@trpc/client';
import { testDb, createTestUser, createTestCall, createTestCampaign } from '../../setup';
import { CallStatus, CallDirection, TelephonyProvider, UserRole } from '@prisma/client';

// Mock dependencies
vi.mock('../../../server/lib/call-manager-prisma', () => ({
  CallManagerPrisma: vi.fn().mockImplementation(() => ({
    prisma: testDb,
    getActiveCalls: vi.fn().mockResolvedValue([]),
    getCallHistory: vi.fn().mockResolvedValue({ calls: [], total: 0 }),
    getCallById: vi.fn(),
    createCall: vi.fn(),
    updateCall: vi.fn(),
    endCall: vi.fn(),
  })),
}));

vi.mock('../../../server/services/call.service', () => ({
  CallService: vi.fn().mockImplementation(() => ({
    listCalls: vi.fn(),
    getCall: vi.fn(),
    createCall: vi.fn(),
    updateCall: vi.fn(),
    getCallStats: vi.fn(),
    initiateOutboundCall: vi.fn(),
    endCall: vi.fn(),
    transferCall: vi.fn(),
    addTranscript: vi.fn(),
    getActiveCalls: vi.fn(),
    getAgentCalls: vi.fn(),
  })),
}));

describe('tRPC Call Router Integration', () => {
  let testOrganizationId: string;
  let testAgentId: string;
  let testSupervisorId: string;
  let testCampaignId: string;
  let mockCallService: any;

  beforeEach(async () => {
    testOrganizationId = 'test-org';

    // Create test users
    const agent = await createTestUser({
      email: 'agent@test.com',
      role: UserRole.AGENT,
      organizationId: testOrganizationId,
    });
    testAgentId = agent.id;

    const supervisor = await createTestUser({
      email: 'supervisor@test.com',
      role: UserRole.SUPERVISOR,
      organizationId: testOrganizationId,
    });
    testSupervisorId = supervisor.id;

    // Create test campaign
    const campaign = await createTestCampaign({
      organizationId: testOrganizationId,
    });
    testCampaignId = campaign.id;

    // Get mocked CallService instance
    const { CallService } = await import('../../../server/services/call.service');
    mockCallService = new (CallService as any)();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('list', () => {
    it('should list calls with pagination and filters', async () => {
      const mockCalls = [
        {
          id: 'call-1',
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: CallDirection.INBOUND,
          provider: TelephonyProvider.TWILIO,
          status: CallStatus.COMPLETED,
          organizationId: testOrganizationId,
          agentId: testAgentId,
          startTime: new Date(),
          duration: 120,
        },
        {
          id: 'call-2',
          fromNumber: '+1234567891',
          toNumber: '+1987654322',
          direction: CallDirection.OUTBOUND,
          provider: TelephonyProvider.TWILIO,
          status: CallStatus.IN_PROGRESS,
          organizationId: testOrganizationId,
          agentId: testAgentId,
          startTime: new Date(),
          duration: null,
        },
      ];

      mockCallService.listCalls.mockResolvedValue({
        calls: mockCalls,
        total: 2,
        hasMore: false,
      });

      // Create TRPC client for testing
      const trpc = createTRPCClient({
        links: [
          httpBatchLink({
            url: 'http://localhost/trpc',
          }),
        ],
      });

      // Mock the router response
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      // Test the procedure directly
      const caller = callRouter.createCaller(mockContext);
      const result = await caller.list({
        limit: 10,
        offset: 0,
        status: CallStatus.COMPLETED,
        direction: CallDirection.INBOUND,
      });

      expect(result.calls).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.hasMore).toBe(false);
      expect(mockCallService.listCalls).toHaveBeenCalledWith(
        expect.objectContaining({
          status: CallStatus.COMPLETED,
          direction: CallDirection.INBOUND,
          organizationId: testOrganizationId,
        }),
        10,
        0
      );
    });

    it('should filter calls by agent for agent role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      mockCallService.listCalls.mockResolvedValue({
        calls: [],
        total: 0,
        hasMore: false,
      });

      const caller = callRouter.createCaller(mockContext);
      await caller.list({ limit: 10, offset: 0 });

      expect(mockCallService.listCalls).toHaveBeenCalledWith(
        expect.objectContaining({
          agentId: testAgentId,
          organizationId: testOrganizationId,
        }),
        10,
        0
      );
    });
  });

  describe('getById', () => {
    it('should get call by ID', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
      });

      mockCallService.getCall.mockResolvedValue(testCall);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.getById({ id: testCall.id });

      expect(result).toEqual(testCall);
      expect(mockCallService.getCall).toHaveBeenCalledWith(testCall.id, testOrganizationId);
    });

    it('should throw error for non-existent call', async () => {
      mockCallService.getCall.mockResolvedValue(null);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.getById({ id: 'non-existent' })).rejects.toThrow('Call not found');
    });
  });

  describe('create', () => {
    it('should create a new call', async () => {
      const newCall = {
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        agentId: testAgentId,
        campaignId: testCampaignId,
        metadata: { source: 'web' },
      };

      const createdCall = {
        id: 'new-call-id',
        ...newCall,
        organizationId: testOrganizationId,
        status: CallStatus.QUEUED,
        startTime: new Date(),
      };

      mockCallService.createCall.mockResolvedValue(createdCall);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.create(newCall);

      expect(result).toEqual(createdCall);
      expect(mockCallService.createCall).toHaveBeenCalledWith({
        ...newCall,
        organizationId: testOrganizationId,
      });
    });

    it('should require supervisor or admin role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.create({
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
      })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('update', () => {
    it('should update call status and details', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
        status: CallStatus.IN_PROGRESS,
      });

      const updateData = {
        status: CallStatus.COMPLETED,
        disposition: 'resolved',
        notes: 'Customer issue resolved',
      };

      const updatedCall = {
        ...testCall,
        ...updateData,
        endTime: new Date(),
        duration: 300,
      };

      mockCallService.updateCall.mockResolvedValue(updatedCall);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.update({
        id: testCall.id,
        ...updateData,
      });

      expect(result).toEqual(updatedCall);
      expect(mockCallService.updateCall).toHaveBeenCalledWith(
        testCall.id,
        updateData,
        testOrganizationId
      );
    });

    it('should allow agents to update only their own calls', async () => {
      const otherAgentCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: 'other-agent-id',
      });

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      mockCallService.getCall.mockResolvedValue(otherAgentCall);

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.update({
        id: otherAgentCall.id,
        status: CallStatus.COMPLETED,
      })).rejects.toThrow('Not authorized to update this call');
    });
  });

  describe('end', () => {
    it('should end an active call', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
        status: CallStatus.IN_PROGRESS,
      });

      const endedCall = {
        ...testCall,
        status: CallStatus.COMPLETED,
        endTime: new Date(),
        duration: 300,
        disposition: 'completed',
      };

      mockCallService.endCall.mockResolvedValue(endedCall);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.end({
        id: testCall.id,
        disposition: 'completed',
        notes: 'Call ended successfully',
      });

      expect(result).toEqual(endedCall);
      expect(mockCallService.endCall).toHaveBeenCalledWith(
        testCall.id,
        'completed',
        'Call ended successfully',
        testOrganizationId
      );
    });
  });

  describe('transfer', () => {
    it('should transfer call to another agent', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
        status: CallStatus.IN_PROGRESS,
      });

      const targetAgent = await createTestUser({
        email: 'target@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      const transferredCall = {
        ...testCall,
        agentId: targetAgent.id,
        metadata: {
          transferredFrom: testAgentId,
          transferredAt: new Date().toISOString(),
        },
      };

      mockCallService.transferCall.mockResolvedValue(transferredCall);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.transfer({
        id: testCall.id,
        targetAgentId: targetAgent.id,
      });

      expect(result).toEqual(transferredCall);
      expect(mockCallService.transferCall).toHaveBeenCalledWith(
        testCall.id,
        targetAgent.id,
        testOrganizationId
      );
    });
  });

  describe('addTranscript', () => {
    it('should add transcript to call', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
      });

      mockCallService.addTranscript.mockResolvedValue(undefined);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      await caller.addTranscript({
        callId: testCall.id,
        role: 'USER',
        content: 'Hello, I need help',
        confidence: 0.95,
        speakerId: 'customer',
        metadata: { language: 'en' },
      });

      expect(mockCallService.addTranscript).toHaveBeenCalledWith(
        testCall.id,
        'USER',
        'Hello, I need help',
        0.95,
        'customer',
        { language: 'en' }
      );
    });
  });

  describe('getStats', () => {
    it('should return call statistics', async () => {
      const mockStats = {
        totalCalls: 100,
        activeCalls: 5,
        completedCalls: 90,
        averageDuration: 180,
        successRate: 85.5,
        busyRate: 10.2,
        noAnswerRate: 4.3,
      };

      mockCallService.getCallStats.mockResolvedValue(mockStats);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.getStats({
        startDate: new Date('2023-01-01'),
        endDate: new Date('2023-12-31'),
        agentId: testAgentId,
      });

      expect(result).toEqual(mockStats);
      expect(mockCallService.getCallStats).toHaveBeenCalledWith(
        testOrganizationId,
        expect.objectContaining({
          startDate: expect.any(Date),
          endDate: expect.any(Date),
          agentId: testAgentId,
        })
      );
    });

    it('should require supervisor role for stats', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.getStats({})).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('getActive', () => {
    it('should return active calls', async () => {
      const mockActiveCalls = [
        {
          id: 'call-1',
          status: CallStatus.IN_PROGRESS,
          agentId: testAgentId,
          startTime: new Date(),
        },
        {
          id: 'call-2',
          status: CallStatus.RINGING,
          agentId: null,
          startTime: new Date(),
        },
      ];

      mockCallService.getActiveCalls.mockResolvedValue(mockActiveCalls);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.getActive();

      expect(result).toEqual(mockActiveCalls);
      expect(mockCallService.getActiveCalls).toHaveBeenCalledWith(testOrganizationId);
    });
  });

  describe('initiateOutbound', () => {
    it('should initiate outbound call', async () => {
      const outboundCall = {
        id: 'outbound-call-id',
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        status: CallStatus.RINGING,
        organizationId: testOrganizationId,
        agentId: testAgentId,
        campaignId: testCampaignId,
        providerCallId: 'twilio-sid-123',
        startTime: new Date(),
      };

      mockCallService.initiateOutboundCall.mockResolvedValue(outboundCall);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.initiateOutbound({
        toNumber: '+1987654321',
        fromNumber: '+1234567890',
        agentId: testAgentId,
        campaignId: testCampaignId,
        metadata: { source: 'manual' },
      });

      expect(result).toEqual(outboundCall);
      expect(mockCallService.initiateOutboundCall).toHaveBeenCalledWith(
        '+1987654321',
        '+1234567890',
        testOrganizationId,
        testAgentId,
        testCampaignId,
        { source: 'manual' }
      );
    });

    it('should require agent, supervisor, or admin role', async () => {
      const mockContext = {
        user: { id: 'user-id', organizationId: testOrganizationId, role: 'VIEWER' as any },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.initiateOutbound({
        toNumber: '+1987654321',
        fromNumber: '+1234567890',
      })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('getAgentCalls', () => {
    it('should return calls for specific agent', async () => {
      const mockAgentCalls = {
        calls: [
          {
            id: 'call-1',
            agentId: testAgentId,
            status: CallStatus.COMPLETED,
          },
          {
            id: 'call-2',
            agentId: testAgentId,
            status: CallStatus.IN_PROGRESS,
          },
        ],
        total: 2,
      };

      mockCallService.getAgentCalls.mockResolvedValue(mockAgentCalls);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);
      const result = await caller.getAgentCalls({
        agentId: testAgentId,
        limit: 10,
        offset: 0,
      });

      expect(result).toEqual(mockAgentCalls);
      expect(mockCallService.getAgentCalls).toHaveBeenCalledWith(
        testAgentId,
        testOrganizationId,
        10,
        0
      );
    });

    it('should allow agents to get their own calls', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      mockCallService.getAgentCalls.mockResolvedValue({ calls: [], total: 0 });

      const caller = callRouter.createCaller(mockContext);
      await caller.getAgentCalls({
        agentId: testAgentId,
        limit: 10,
        offset: 0,
      });

      expect(mockCallService.getAgentCalls).toHaveBeenCalledWith(
        testAgentId,
        testOrganizationId,
        10,
        0
      );
    });

    it('should prevent agents from accessing other agents calls', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        callService: mockCallService,
      };

      const caller = callRouter.createCaller(mockContext);

      await expect(caller.getAgentCalls({
        agentId: 'other-agent-id',
        limit: 10,
        offset: 0,
      })).rejects.toThrow('Can only access your own calls');
    });
  });
});