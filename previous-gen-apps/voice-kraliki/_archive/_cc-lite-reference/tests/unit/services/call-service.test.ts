import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CallService, CallCreateData, CallUpdateData, CallFilters } from '../../../server/services/call.service';
import { testDb, createTestUser, createTestCall, createTestCampaign } from '../../setup';
import { FastifyInstance } from 'fastify';
import { CallStatus, CallDirection, TelephonyProvider, UserRole } from '@prisma/client';

const skipDb = process.env.SKIP_DB_TEST_SETUP === 'true';

// Mock fastify instance
const mockFastify = {
  log: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
} as unknown as FastifyInstance;

// Mock telephony service
vi.mock('../../../server/services/telephony-service', () => ({
  getTelephonyService: vi.fn(() => ({
    createOutboundCall: vi.fn().mockResolvedValue('test-provider-call-id'),
    hangupCall: vi.fn().mockResolvedValue(true),
  })),
}));

const maybeDescribe = skipDb ? describe.skip : describe;

maybeDescribe('CallService', () => {
  let callService: CallService;
  let testOrganizationId: string;
  let testAgentId: string;
  let testSupervisorId: string;
  let testCampaignId: string;

  beforeEach(async () => {
    callService = new CallService(mockFastify, testDb);
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
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('createCall', () => {
    it('should create a new call with valid data', async () => {
      const callData: CallCreateData = {
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: testOrganizationId,
        agentId: testAgentId,
        campaignId: testCampaignId,
        metadata: { testData: 'example' },
      };

      const call = await callService.createCall(callData);

      expect(call).toBeDefined();
      expect(call.fromNumber).toBe(callData.fromNumber);
      expect(call.toNumber).toBe(callData.toNumber);
      expect(call.status).toBe(CallStatus.QUEUED);
      expect(call.organizationId).toBe(testOrganizationId);
      expect(call.agentId).toBe(testAgentId);
      expect(call.campaignId).toBe(testCampaignId);
      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Call created')
      );
    });

    it('should throw error for non-existent organization', async () => {
      const callData: CallCreateData = {
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'non-existent-org',
      };

      await expect(callService.createCall(callData)).rejects.toThrow(
        'Organization not found'
      );
    });

    it('should throw error for non-existent agent', async () => {
      const callData: CallCreateData = {
        fromNumber: '+1234567890',
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: testOrganizationId,
        agentId: 'non-existent-agent',
      };

      await expect(callService.createCall(callData)).rejects.toThrow(
        'Agent not found'
      );
    });
  });

  describe('getCall', () => {
    it('should retrieve call by ID', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
      });

      const retrievedCall = await callService.getCall(testCall.id, testOrganizationId);

      expect(retrievedCall).toBeDefined();
      expect(retrievedCall?.id).toBe(testCall.id);
      expect(retrievedCall?.agent).toBeDefined();
      expect(retrievedCall?.transcripts).toBeDefined();
    });

    it('should return null for non-existent call', async () => {
      const retrievedCall = await callService.getCall('non-existent-id', testOrganizationId);
      expect(retrievedCall).toBeNull();
    });

    it('should respect organization isolation', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
      });

      const retrievedCall = await callService.getCall(testCall.id, 'different-org');
      expect(retrievedCall).toBeNull();
    });
  });

  describe('updateCall', () => {
    it('should update call status and calculate duration', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
      });

      const updateData: CallUpdateData = {
        status: CallStatus.COMPLETED,
        disposition: 'success',
        notes: 'Call completed successfully',
      };

      const updatedCall = await callService.updateCall(
        testCall.id,
        updateData,
        testOrganizationId
      );

      expect(updatedCall.status).toBe(CallStatus.COMPLETED);
      expect(updatedCall.disposition).toBe('success');
      expect(updatedCall.notes).toBe('Call completed successfully');
      expect(updatedCall.duration).toBeGreaterThan(0);
      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Call updated')
      );
    });

    it('should update call by provider ID', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        providerCallId: 'test-provider-id',
      });

      const updatedCall = await callService.updateCallByProviderId(
        'test-provider-id',
        { status: CallStatus.COMPLETED },
        testOrganizationId
      );

      expect(updatedCall).toBeDefined();
      expect(updatedCall?.status).toBe(CallStatus.COMPLETED);
    });
  });

  describe('listCalls', () => {
    beforeEach(async () => {
      // Create test calls with different statuses
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
        agentId: testAgentId,
        campaignId: testCampaignId,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
        agentId: testAgentId,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.FAILED,
      });
    });

    it('should list calls with pagination', async () => {
      const filters: CallFilters = {
        organizationId: testOrganizationId,
      };

      const result = await callService.listCalls(filters, 2, 0);

      expect(result.calls).toHaveLength(2);
      expect(result.total).toBe(3);
      expect(result.hasMore).toBe(true);
    });

    it('should filter calls by status', async () => {
      const filters: CallFilters = {
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
      };

      const result = await callService.listCalls(filters);

      expect(result.calls).toHaveLength(1);
      expect(result.calls[0].status).toBe(CallStatus.COMPLETED);
    });

    it('should filter calls by agent', async () => {
      const filters: CallFilters = {
        organizationId: testOrganizationId,
        agentId: testAgentId,
      };

      const result = await callService.listCalls(filters);

      expect(result.calls).toHaveLength(2);
      result.calls.forEach(call => {
        expect(call.agentId).toBe(testAgentId);
      });
    });

    it('should filter calls by date range', async () => {
      const startDate = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago
      const endDate = new Date();

      const filters: CallFilters = {
        organizationId: testOrganizationId,
        startDate,
        endDate,
      };

      const result = await callService.listCalls(filters);

      expect(result.calls.length).toBeGreaterThan(0);
      result.calls.forEach(call => {
        expect(call.startTime).toBeInstanceOf(Date);
        expect(call.startTime.getTime()).toBeGreaterThanOrEqual(startDate.getTime());
        expect(call.startTime.getTime()).toBeLessThanOrEqual(endDate.getTime());
      });
    });
  });

  describe('getCallStats', () => {
    beforeEach(async () => {
      // Create calls with various statuses for stats calculation
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
        duration: 120,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
        duration: 180,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.BUSY,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.NO_ANSWER,
      });
    });

    it('should calculate correct call statistics', async () => {
      const stats = await callService.getCallStats(testOrganizationId);

      expect(stats.totalCalls).toBe(5);
      expect(stats.completedCalls).toBe(2);
      expect(stats.activeCalls).toBe(1);
      expect(stats.averageDuration).toBe(150); // (120 + 180) / 2
      expect(stats.successRate).toBe(40); // 2/5 * 100
      expect(stats.busyRate).toBe(20); // 1/5 * 100
      expect(stats.noAnswerRate).toBe(20); // 1/5 * 100
    });

    it('should handle empty result set', async () => {
      const stats = await callService.getCallStats('empty-org');

      expect(stats.totalCalls).toBe(0);
      expect(stats.completedCalls).toBe(0);
      expect(stats.activeCalls).toBe(0);
      expect(stats.averageDuration).toBe(0);
      expect(stats.successRate).toBe(0);
      expect(stats.busyRate).toBe(0);
      expect(stats.noAnswerRate).toBe(0);
    });
  });

  describe('initiateOutboundCall', () => {
    it('should create outbound call and update with provider ID', async () => {
      const call = await callService.initiateOutboundCall(
        '+1987654321',
        '+1234567890',
        testOrganizationId,
        testAgentId,
        testCampaignId,
        { testData: 'outbound' }
      );

      expect(call.direction).toBe(CallDirection.OUTBOUND);
      expect(call.status).toBe(CallStatus.RINGING);
      expect(call.providerCallId).toBe('test-provider-call-id');
      expect(call.agentId).toBe(testAgentId);
      expect(call.campaignId).toBe(testCampaignId);
    });

    it('should handle telephony service failure', async () => {
      const { getTelephonyService } = await import('../../../server/services/telephony-service');
      (getTelephonyService as any).mockReturnValue({
        createOutboundCall: vi.fn().mockRejectedValue(new Error('Provider error')),
      });

      await expect(callService.initiateOutboundCall(
        '+1987654321',
        '+1234567890',
        testOrganizationId
      )).rejects.toThrow('Provider error');

      // Verify call status was updated to failed
      const calls = await callService.listCalls({ organizationId: testOrganizationId });
      const failedCall = calls.calls.find(c => c.status === CallStatus.FAILED);
      expect(failedCall).toBeDefined();
      expect(failedCall?.disposition).toBe('provider_error');
    });
  });

  describe('endCall', () => {
    it('should end call and update status', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
        providerCallId: 'test-provider-id',
      });

      const endedCall = await callService.endCall(
        testCall.id,
        'completed',
        'Customer satisfied',
        testOrganizationId
      );

      expect(endedCall.status).toBe(CallStatus.COMPLETED);
      expect(endedCall.disposition).toBe('completed');
      expect(endedCall.notes).toBe('Customer satisfied');
      expect(endedCall.endTime).toBeInstanceOf(Date);
    });

    it('should throw error for non-existent call', async () => {
      await expect(callService.endCall(
        'non-existent-id',
        'completed',
        'notes',
        testOrganizationId
      )).rejects.toThrow('Call not found');
    });
  });

  describe('transferCall', () => {
    it('should transfer call to another agent', async () => {
      const targetAgent = await createTestUser({
        email: 'target@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
        agentId: testAgentId,
      });

      const transferredCall = await callService.transferCall(
        testCall.id,
        targetAgent.id,
        testOrganizationId
      );

      expect(transferredCall.agentId).toBe(targetAgent.id);
      expect(transferredCall.metadata).toHaveProperty('transferredFrom');
      expect(transferredCall.metadata).toHaveProperty('transferredAt');
    });

    it('should throw error for inactive call', async () => {
      const targetAgent = await createTestUser({
        email: 'target2@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
      });

      await expect(callService.transferCall(
        testCall.id,
        targetAgent.id,
        testOrganizationId
      )).rejects.toThrow('Call is not active and cannot be transferred');
    });

    it('should throw error for non-existent target agent', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
      });

      await expect(callService.transferCall(
        testCall.id,
        'non-existent-agent',
        testOrganizationId
      )).rejects.toThrow('Target agent not found');
    });
  });

  describe('addTranscript', () => {
    it('should add transcript to call', async () => {
      const testCall = await createTestCall({
        organizationId: testOrganizationId,
      });

      await callService.addTranscript(
        testCall.id,
        'USER',
        'Hello, I need help with my account',
        0.95,
        'speaker-1',
        { language: 'en' }
      );

      const call = await callService.getCall(testCall.id, testOrganizationId);
      expect(call?.transcripts).toHaveLength(1);
      expect(call?.transcripts[0].role).toBe('USER');
      expect(call?.transcripts[0].content).toBe('Hello, I need help with my account');
      expect(call?.transcripts[0].confidence).toBe(0.95);
    });
  });

  describe('getActiveCalls', () => {
    it('should return only active calls', async () => {
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.IN_PROGRESS,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.RINGING,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        status: CallStatus.COMPLETED,
      });

      const activeCalls = await callService.getActiveCalls(testOrganizationId);

      expect(activeCalls).toHaveLength(2);
      activeCalls.forEach(call => {
        expect([CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.QUEUED]).toContain(call.status);
      });
    });
  });

  describe('getAgentCalls', () => {
    it('should return calls for specific agent with pagination', async () => {
      // Create calls for the agent
      await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
      });
      await createTestCall({
        organizationId: testOrganizationId,
        agentId: testAgentId,
      });
      // Create call for different agent
      await createTestCall({
        organizationId: testOrganizationId,
        agentId: testSupervisorId,
      });

      const result = await callService.getAgentCalls(
        testAgentId,
        testOrganizationId,
        10,
        0
      );

      expect(result.calls).toHaveLength(2);
      expect(result.total).toBe(2);
      result.calls.forEach(call => {
        expect(call.agentId).toBe(testAgentId);
      });
    });
  });
});
