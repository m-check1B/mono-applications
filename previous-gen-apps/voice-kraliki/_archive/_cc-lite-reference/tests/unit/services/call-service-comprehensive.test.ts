import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CallService } from '@server/services/call.service';
import { PrismaClient, CallStatus, CallDirection, TelephonyProvider, UserRole } from '@prisma/client';
import { FastifyInstance } from 'fastify';

// Mock telephony service
vi.mock('@server/services/telephony-service', () => ({
  getTelephonyService: vi.fn().mockReturnValue({
    makeCall: vi.fn().mockResolvedValue({ sid: 'call-sid-123' }),
    endCall: vi.fn().mockResolvedValue(true),
    transferCall: vi.fn().mockResolvedValue(true),
    getCallStatus: vi.fn().mockResolvedValue({ status: 'in-progress' })
  })
}));

// Mock sentiment analysis service
vi.mock('@server/services/sentiment-analysis-service', () => {
  return {
    SentimentAnalysisService: vi.fn().mockImplementation(() => ({
      analyzeSentiment: vi.fn().mockResolvedValue({
        sentiment: 'neutral',
        confidence: 0.8,
        emotions: []
      })
    }))
  };
});

describe('CallService', () => {
  let callService: CallService;
  let mockPrisma: any;
  let mockFastify: any;
  let mockCall: any;
  let mockUser: any;
  let mockOrganization: any;

  beforeEach(() => {
    mockOrganization = {
      id: 'test-org-id',
      name: 'Test Organization',
      domain: 'test.local'
    };

    mockUser = {
      id: 'test-user-id',
      email: 'agent@example.com',
      role: UserRole.AGENT,
      firstName: 'Test',
      lastName: 'Agent',
      organizationId: 'test-org-id'
    };

    mockCall = {
      id: 'test-call-id',
      fromNumber: '+1234567890',
      toNumber: '+9876543210',
      direction: CallDirection.INBOUND,
      provider: TelephonyProvider.TWILIO,
      status: CallStatus.QUEUED,
      organizationId: 'test-org-id',
      agentId: 'test-user-id',
      providerCallId: 'provider-call-id',
      startTime: new Date(),
      endTime: null,
      duration: null,
      metadata: {},
      agent: mockUser,
      organization: mockOrganization
    };

    mockPrisma = {
      call: {
        create: vi.fn(),
        findUnique: vi.fn(),
        findFirst: vi.fn(),
        findMany: vi.fn(),
        update: vi.fn(),
        delete: vi.fn(),
        count: vi.fn(),
        aggregate: vi.fn()
      },
      user: {
        findUnique: vi.fn(),
        findMany: vi.fn()
      },
      organization: {
        findUnique: vi.fn()
      },
      campaign: {
        findUnique: vi.fn()
      },
      callTranscript: {
        create: vi.fn(),
        findMany: vi.fn()
      }
    };

    mockFastify = {
      log: {
        info: vi.fn(),
        error: vi.fn(),
        warn: vi.fn(),
        debug: vi.fn()
      }
    } as any;

    mockPrisma.call.findFirst.mockResolvedValue(mockCall);

    callService = new CallService(mockFastify, mockPrisma);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('createCall', () => {
    beforeEach(() => {
      mockPrisma.organization.findUnique.mockResolvedValue(mockOrganization);
      mockPrisma.user.findUnique.mockResolvedValue(mockUser);
      mockPrisma.call.create.mockResolvedValue(mockCall);
    });

    it('should create a new call with valid data', async () => {
      const callData = {
        fromNumber: '+1234567890',
        toNumber: '+9876543210',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'test-org-id',
        agentId: 'test-user-id'
      };

      const result = await callService.createCall(callData);

      expect(mockPrisma.organization.findUnique).toHaveBeenCalledWith({
        where: { id: 'test-org-id' }
      });
      expect(mockPrisma.user.findUnique).toHaveBeenCalledWith({
        where: { id: 'test-user-id' }
      });
      expect(mockPrisma.call.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          fromNumber: '+1234567890',
          toNumber: '+9876543210',
          direction: CallDirection.INBOUND,
          provider: TelephonyProvider.TWILIO,
          status: CallStatus.QUEUED,
          startTime: expect.any(Date)
        }),
        include: expect.any(Object)
      });
      expect(result).toEqual(mockCall);
    });

    it('should throw error for non-existent organization', async () => {
      mockPrisma.organization.findUnique.mockResolvedValue(null);

      const callData = {
        fromNumber: '+1234567890',
        toNumber: '+9876543210',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'nonexistent-org'
      };

      await expect(callService.createCall(callData))
        .rejects.toThrow('Organization not found');
    });

    it('should throw error for non-existent agent', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);

      const callData = {
        fromNumber: '+1234567890',
        toNumber: '+9876543210',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'test-org-id',
        agentId: 'nonexistent-agent'
      };

      await expect(callService.createCall(callData))
        .rejects.toThrow('Agent not found');
    });

    it('should create call without agent assignment', async () => {
      const callData = {
        fromNumber: '+1234567890',
        toNumber: '+9876543210',
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TELNYX,
        organizationId: 'test-org-id'
      };

      await callService.createCall(callData);

      expect(mockPrisma.user.findUnique).not.toHaveBeenCalled();
      expect(mockPrisma.call.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          agentId: undefined
        }),
        include: expect.any(Object)
      });
    });
  });

  describe('updateCall', () => {
    beforeEach(() => {
      mockPrisma.call.findFirst.mockResolvedValue(mockCall);
      mockPrisma.call.update.mockResolvedValue({
        ...mockCall,
        status: CallStatus.COMPLETED,
        endTime: new Date(),
        duration: 300
      });
    });

    it('should update call with valid data', async () => {
      const updateData = {
        status: CallStatus.COMPLETED,
        endTime: new Date(),
        duration: 300,
        disposition: 'RESOLVED'
      };

      const result = await callService.updateCall('test-call-id', updateData);

      expect(mockPrisma.call.update).toHaveBeenCalledWith({
        where: { id: 'test-call-id' },
        data: updateData,
        include: expect.any(Object)
      });
      expect(result.status).toBe(CallStatus.COMPLETED);
    });

    it('should throw error for non-existent call', async () => {
      mockPrisma.call.findFirst.mockResolvedValue(null);

      await expect(callService.updateCall('nonexistent-call', { status: CallStatus.COMPLETED }))
        .rejects.toThrow('Call not found');
    });

    it('should calculate duration automatically when ending call', async () => {
      const startTime = new Date(Date.now() - 300000); // 5 minutes ago
      const endTime = new Date();

      mockPrisma.call.findFirst.mockResolvedValue({
        ...mockCall,
        startTime
      });

      await callService.updateCall('test-call-id', {
        status: CallStatus.COMPLETED,
        endTime
      });

      expect(mockPrisma.call.update).toHaveBeenCalledWith({
        where: { id: 'test-call-id' },
        data: expect.objectContaining({
          duration: expect.any(Number)
        }),
        include: expect.any(Object)
      });
    });
  });

  describe('getCall', () => {
    beforeEach(() => {
      mockPrisma.call.findFirst.mockResolvedValue(mockCall);
    });

    it('should retrieve call by ID', async () => {
      const result = await callService.getCall('test-call-id');

      expect(mockPrisma.call.findFirst).toHaveBeenCalledWith({
        where: { id: 'test-call-id' },
        include: expect.any(Object)
      });
      expect(result).toEqual(mockCall);
    });

    it('should return null for non-existent call', async () => {
      mockPrisma.call.findFirst.mockResolvedValue(null);

      const result = await callService.getCall('nonexistent-call');

      expect(result).toBeNull();
    });
  });

  describe('getCalls', () => {
    const mockCalls = [mockCall, { ...mockCall, id: 'call-2' }];

    beforeEach(() => {
      mockPrisma.call.findMany.mockResolvedValue(mockCalls);
    });

    it('should retrieve calls with filters', async () => {
      const filters = {
        status: CallStatus.IN_PROGRESS,
        organizationId: 'test-org-id',
        agentId: 'test-user-id'
      };

      const result = await callService.getCalls(filters);

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({
          status: CallStatus.IN_PROGRESS,
          organizationId: 'test-org-id',
          agentId: 'test-user-id'
        }),
        orderBy: { startTime: 'desc' }
      }));
      expect(result).toEqual(mockCalls);
    });

    it('should handle date range filters', async () => {
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-12-31');
      const filters = { startDate, endDate };

      await callService.getCalls(filters);

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({
          startTime: {
            gte: startDate,
            lte: endDate
          }
        }),
        orderBy: { startTime: 'desc' }
      }));
    });

    it('should handle pagination', async () => {
      const options = { skip: 10, take: 20 };

      await callService.getCalls({}, options);

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: {},
        orderBy: { startTime: 'desc' },
        skip: 10,
        take: 20
      }));
    });
  });

  describe('getCallStats', () => {
    beforeEach(() => {
      mockPrisma.call.aggregate.mockResolvedValue({
        _avg: { duration: 180 },
        _count: { id: 100 }
      });

      // Mock different status counts
      mockPrisma.call.count
        .mockResolvedValueOnce(100) // total
        .mockResolvedValueOnce(5)   // active
        .mockResolvedValueOnce(80)  // completed
        .mockResolvedValueOnce(10)  // busy
        .mockResolvedValueOnce(10); // no answer
    });

    it('should calculate call statistics', async () => {
      const filters = { organizationId: 'test-org-id' };

      const result = await callService.getCallStats(filters);

      expect(result).toEqual({
        totalCalls: 100,
        activeCalls: 5,
        completedCalls: 80,
        averageDuration: 180,
        successRate: 80,
        busyRate: 10,
        noAnswerRate: 10
      });
    });

    it('should handle division by zero for rates', async () => {
      mockPrisma.call.count.mockReset();
      mockPrisma.call.count.mockResolvedValue(0);
      mockPrisma.call.aggregate.mockResolvedValue({
        _avg: { duration: null },
        _count: { id: 0 }
      });

      const result = await callService.getCallStats({ organizationId: 'test-org-id' });

      expect(result).toEqual({
        totalCalls: 0,
        activeCalls: 0,
        completedCalls: 0,
        averageDuration: 0,
        successRate: 0,
        busyRate: 0,
        noAnswerRate: 0
      });
    });
  });

  describe('assignAgent', () => {
    beforeEach(() => {
      mockPrisma.call.findFirst.mockResolvedValue(mockCall);
      mockPrisma.user.findUnique.mockResolvedValue(mockUser);
      mockPrisma.call.update.mockResolvedValue({
        ...mockCall,
        agentId: 'new-agent-id',
        status: CallStatus.IN_PROGRESS
      });
    });

    it('should assign agent to call', async () => {
      const result = await callService.assignAgent('test-call-id', 'new-agent-id');

      expect(mockPrisma.user.findUnique).toHaveBeenCalledWith({
        where: { id: 'new-agent-id' }
      });
      expect(mockPrisma.call.update).toHaveBeenCalledWith(expect.objectContaining({
        where: { id: 'test-call-id' },
        data: expect.objectContaining({
          agentId: 'new-agent-id',
          status: CallStatus.IN_PROGRESS
        })
      }));
      expect(result.agentId).toBe('new-agent-id');
    });

    it('should throw error for non-existent agent', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);

      await expect(callService.assignAgent('test-call-id', 'nonexistent-agent'))
        .rejects.toThrow('Agent not found');
    });
  });

  describe('transferCall', () => {
    beforeEach(() => {
      mockCall.status = CallStatus.IN_PROGRESS;
      mockPrisma.call.findFirst.mockResolvedValue(mockCall);
      mockPrisma.user.findUnique.mockResolvedValue(mockUser);
      mockPrisma.call.update.mockResolvedValue({
        ...mockCall,
        agentId: 'new-agent-id'
      });
    });

    it('should transfer call to another agent', async () => {
      const result = await callService.transferCall('test-call-id', 'new-agent-id');

      expect(mockPrisma.call.update).toHaveBeenCalledWith(expect.objectContaining({
        where: { id: 'test-call-id' },
        data: expect.objectContaining({ agentId: 'new-agent-id' })
      }));
      expect(result.agentId).toBe('new-agent-id');
    });

    it('should call telephony service for transfer', async () => {
      const { getTelephonyService } = await import('@server/services/telephony-service');
      const telephonyService = getTelephonyService();

      await callService.transferCall('test-call-id', 'new-agent-id');

      expect(telephonyService.transferCall).toHaveBeenCalledWith(
        mockCall.providerCallId,
        'new-agent-id'
      );
    });
  });

  describe('endCall', () => {
    beforeEach(() => {
      mockPrisma.call.findFirst.mockResolvedValue({
        ...mockCall,
        status: CallStatus.IN_PROGRESS,
        startTime: new Date(Date.now() - 300000) // 5 minutes ago
      });
      mockPrisma.call.update.mockResolvedValue({
        ...mockCall,
        status: CallStatus.COMPLETED,
        endTime: new Date(),
        duration: 300
      });
    });

    it('should end active call', async () => {
      const disposition = 'RESOLVED';
      const notes = 'Call completed successfully';

      const result = await callService.endCall('test-call-id', disposition, notes);

      expect(mockPrisma.call.update).toHaveBeenCalledWith({
        where: { id: 'test-call-id' },
        data: expect.objectContaining({
          status: CallStatus.COMPLETED,
          disposition,
          notes,
          endTime: expect.any(Date),
          duration: expect.any(Number)
        }),
        include: expect.any(Object)
      });
      expect(result.status).toBe(CallStatus.COMPLETED);
    });

    it('should call telephony service to end call', async () => {
      const { getTelephonyService } = await import('@server/services/telephony-service');
      const telephonyService = getTelephonyService();

      await callService.endCall('test-call-id');

      expect(telephonyService.endCall).toHaveBeenCalledWith(
        mockCall.providerCallId
      );
    });

    it('should throw error for already ended call', async () => {
      mockPrisma.call.findFirst.mockResolvedValue({
        ...mockCall,
        status: CallStatus.COMPLETED
      });

      await expect(callService.endCall('test-call-id'))
        .rejects.toThrow('Call is not active');
    });
  });

  describe('addTranscript', () => {
    beforeEach(() => {
      mockCall.status = CallStatus.IN_PROGRESS;
      mockPrisma.call.findFirst.mockResolvedValue(mockCall);
      mockPrisma.callTranscript.create.mockResolvedValue({
        id: 'transcript-id',
        callId: 'test-call-id',
        role: 'USER',
        content: 'Hello, I need help',
        timestamp: new Date(),
        confidence: 0.95,
        metadata: { speaker: 'customer' }
      });
    });

    it('should add transcript to call', async () => {
      const transcriptData = {
        speaker: 'customer' as const,
        text: 'Hello, I need help',
        confidence: 0.95
      };

      const result = await callService.addTranscript('test-call-id', transcriptData);

      expect(mockPrisma.callTranscript.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          callId: 'test-call-id',
          role: 'USER',
          content: 'Hello, I need help',
          confidence: 0.95,
          metadata: expect.objectContaining({ speaker: 'customer' }),
          timestamp: expect.any(Date)
        })
      });
      expect(result.role).toBe('USER');
      expect(result.content).toBe('Hello, I need help');
    });

    it('should throw error for non-existent call', async () => {
      mockPrisma.call.findFirst.mockResolvedValue(null);

      const transcriptData = {
        speaker: 'agent' as const,
        text: 'How can I help you?',
        confidence: 0.98
      };

      await expect(callService.addTranscript('nonexistent-call', transcriptData))
        .rejects.toThrow('Call not found');
    });
  });

  describe('Error Handling', () => {
    it('should handle database connection errors', async () => {
      mockPrisma.call.findFirst.mockRejectedValue(new Error('Database connection failed'));

      await expect(callService.getCall('test-call-id'))
        .rejects.toThrow('Database connection failed');
    });

    it('should handle telephony service errors gracefully', async () => {
      const { getTelephonyService } = await import('@server/services/telephony-service');
      const telephonyService = getTelephonyService();
      telephonyService.endCall.mockRejectedValue(new Error('Telephony service error'));

      mockPrisma.call.findFirst.mockResolvedValue({
        ...mockCall,
        status: CallStatus.IN_PROGRESS
      });
      mockPrisma.call.update.mockResolvedValue({
        ...mockCall,
        status: CallStatus.COMPLETED
      });

      // Should still update database even if telephony service fails
      const result = await callService.endCall('test-call-id');
      expect(result.status).toBe(CallStatus.COMPLETED);
    });
  });

  describe('Performance and Memory', () => {
    it('should handle large number of calls efficiently', async () => {
      const largeCalls = Array.from({ length: 1000 }, (_, i) => ({
        ...mockCall,
        id: `call-${i}`
      }));

      mockPrisma.call.findMany.mockResolvedValue(largeCalls);

      const result = await callService.getCalls({}, { take: 1000 });

      expect(result).toHaveLength(1000);
      expect(mockPrisma.call.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: {},
        orderBy: { startTime: 'desc' },
        take: 1000
      }));
    });
  });
});
