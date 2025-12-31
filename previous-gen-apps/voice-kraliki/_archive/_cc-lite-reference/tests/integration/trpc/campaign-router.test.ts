import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { campaignRouter } from '../../../server/trpc/routers/campaign';
import { testDb, createTestUser, createTestCampaign } from '../../setup';
import { CampaignType, UserRole } from '@prisma/client';

// Mock dependencies
vi.mock('../../../server/services/campaign-service', () => ({
  CampaignService: vi.fn().mockImplementation(() => ({
    createCampaign: vi.fn(),
    startCampaign: vi.fn(),
    stopCampaign: vi.fn(),
    getCampaignStats: vi.fn(),
    getCampaignContacts: vi.fn(),
    importContacts: vi.fn(),
    scheduleCallback: vi.fn(),
  })),
}));

vi.mock('../../../server/services/contact.service', () => ({
  ContactService: vi.fn().mockImplementation(() => ({
    getCampaignContacts: vi.fn(),
    getContactStats: vi.fn(),
    importFromCSV: vi.fn(),
    createContact: vi.fn(),
    updateContact: vi.fn(),
    deleteContact: vi.fn(),
  })),
}));

describe('tRPC Campaign Router Integration', () => {
  let testOrganizationId: string;
  let testAdminId: string;
  let testSupervisorId: string;
  let testAgentId: string;
  let mockCampaignService: any;
  let mockContactService: any;

  beforeEach(async () => {
    testOrganizationId = 'test-org';

    // Create test users
    const admin = await createTestUser({
      email: 'admin@test.com',
      role: UserRole.ADMIN,
      organizationId: testOrganizationId,
    });
    testAdminId = admin.id;

    const supervisor = await createTestUser({
      email: 'supervisor@test.com',
      role: UserRole.SUPERVISOR,
      organizationId: testOrganizationId,
    });
    testSupervisorId = supervisor.id;

    const agent = await createTestUser({
      email: 'agent@test.com',
      role: UserRole.AGENT,
      organizationId: testOrganizationId,
    });
    testAgentId = agent.id;

    // Get mocked service instances
    const { CampaignService } = await import('../../../server/services/campaign-service');
    const { ContactService } = await import('../../../server/services/contact.service');
    mockCampaignService = new (CampaignService as any)();
    mockContactService = new (ContactService as any)();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('list', () => {
    it('should list campaigns for organization', async () => {
      const mockCampaigns = [
        {
          id: 'campaign-1',
          name: 'Test Campaign 1',
          type: CampaignType.OUTBOUND,
          active: true,
          organizationId: testOrganizationId,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: 'campaign-2',
          name: 'Test Campaign 2',
          type: CampaignType.INBOUND,
          active: false,
          organizationId: testOrganizationId,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      // Mock database query
      vi.spyOn(testDb.campaign, 'findMany').mockResolvedValue(mockCampaigns as any);
      vi.spyOn(testDb.campaign, 'count').mockResolvedValue(2);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.list({ limit: 10, offset: 0 });

      expect(result.campaigns).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.hasMore).toBe(false);
      expect(testDb.campaign.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { organizationId: testOrganizationId },
          take: 10,
          skip: 0,
        })
      );
    });

    it('should filter campaigns by type', async () => {
      vi.spyOn(testDb.campaign, 'findMany').mockResolvedValue([]);
      vi.spyOn(testDb.campaign, 'count').mockResolvedValue(0);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      await caller.list({
        limit: 10,
        offset: 0,
        type: CampaignType.OUTBOUND,
        active: true
      });

      expect(testDb.campaign.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            organizationId: testOrganizationId,
            type: CampaignType.OUTBOUND,
            active: true,
          },
        })
      );
    });
  });

  describe('getById', () => {
    it('should get campaign by ID', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
        name: 'Test Campaign',
        type: CampaignType.OUTBOUND,
      });

      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.getById({ id: testCampaign.id });

      expect(result).toEqual(testCampaign);
      expect(testDb.campaign.findUnique).toHaveBeenCalledWith({
        where: {
          id: testCampaign.id,
          organizationId: testOrganizationId,
        },
        include: expect.any(Object),
      });
    });

    it('should throw error for non-existent campaign', async () => {
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(null);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.getById({ id: 'non-existent' })).rejects.toThrow('Campaign not found');
    });
  });

  describe('create', () => {
    it('should create a new campaign', async () => {
      const campaignData = {
        name: 'New Test Campaign',
        description: 'A campaign for testing',
        type: CampaignType.OUTBOUND,
        settings: {
          maxConcurrentCalls: 5,
          maxAttemptsPerContact: 3,
          timeBetweenAttempts: 15,
          dialingHours: {
            start: '09:00',
            end: '17:00',
            timezone: 'UTC',
          },
          callbackEnabled: true,
          voicemailDetection: true,
          complianceSettings: {
            dncListEnabled: true,
            consentRequired: true,
            recordingConsent: true,
          },
        },
        script: 'Hello, this is a test campaign.',
      };

      const createdCampaign = {
        id: 'new-campaign-id',
        ...campaignData,
        organizationId: testOrganizationId,
        active: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      mockCampaignService.createCampaign.mockResolvedValue(createdCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.create(campaignData);

      expect(result).toEqual(createdCampaign);
      expect(mockCampaignService.createCampaign).toHaveBeenCalledWith({
        ...campaignData,
        organizationId: testOrganizationId,
      });
    });

    it('should require admin role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.create({
        name: 'Test Campaign',
        type: CampaignType.OUTBOUND,
        settings: {} as any,
      })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('update', () => {
    it('should update campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const updateData = {
        name: 'Updated Campaign Name',
        description: 'Updated description',
        active: true,
      };

      const updatedCampaign = {
        ...testCampaign,
        ...updateData,
        updatedAt: new Date(),
      };

      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);
      vi.spyOn(testDb.campaign, 'update').mockResolvedValue(updatedCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.update({
        id: testCampaign.id,
        ...updateData,
      });

      expect(result).toEqual(updatedCampaign);
      expect(testDb.campaign.update).toHaveBeenCalledWith({
        where: { id: testCampaign.id },
        data: updateData,
        include: expect.any(Object),
      });
    });

    it('should require admin role', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.update({
        id: 'campaign-id',
        name: 'Updated Name',
      })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('delete', () => {
    it('should delete campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: false,
      });

      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);
      vi.spyOn(testDb.campaign, 'delete').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.delete({ id: testCampaign.id });

      expect(result.success).toBe(true);
      expect(testDb.campaign.delete).toHaveBeenCalledWith({
        where: { id: testCampaign.id },
      });
    });

    it('should prevent deletion of active campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: true,
      });

      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.delete({ id: testCampaign.id })).rejects.toThrow(
        'Cannot delete active campaign'
      );
    });
  });

  describe('start', () => {
    it('should start campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: false,
      });

      mockCampaignService.startCampaign.mockResolvedValue(undefined);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.start({ id: testCampaign.id });

      expect(result.success).toBe(true);
      expect(mockCampaignService.startCampaign).toHaveBeenCalledWith(testCampaign.id);
    });

    it('should require admin role', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.start({ id: 'campaign-id' })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('stop', () => {
    it('should stop campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: true,
      });

      mockCampaignService.stopCampaign.mockResolvedValue(undefined);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.stop({ id: testCampaign.id });

      expect(result.success).toBe(true);
      expect(mockCampaignService.stopCampaign).toHaveBeenCalledWith(testCampaign.id);
    });
  });

  describe('getStats', () => {
    it('should return campaign statistics', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const mockStats = {
        totalContacts: 100,
        contactsDialed: 50,
        contactsConnected: 40,
        contactsCompleted: 35,
        avgCallDuration: 120,
        conversionRate: 0.7,
        callbacks: 5,
      };

      mockCampaignService.getCampaignStats.mockResolvedValue(mockStats);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.getStats({ id: testCampaign.id });

      expect(result).toEqual(mockStats);
      expect(mockCampaignService.getCampaignStats).toHaveBeenCalledWith(testCampaign.id);
    });
  });

  describe('getContacts', () => {
    it('should return campaign contacts', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const mockContacts = {
        contacts: [
          {
            id: 'contact-1',
            phoneNumber: '+1234567890',
            name: 'John Doe',
            status: 'PENDING',
            campaignId: testCampaign.id,
          },
          {
            id: 'contact-2',
            phoneNumber: '+1987654321',
            name: 'Jane Smith',
            status: 'COMPLETED',
            campaignId: testCampaign.id,
          },
        ],
        total: 2,
        hasMore: false,
      };

      mockContactService.getCampaignContacts.mockResolvedValue(mockContacts);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.getContacts({
        id: testCampaign.id,
        limit: 10,
        offset: 0,
        status: 'PENDING',
      });

      expect(result).toEqual(mockContacts);
      expect(mockContactService.getCampaignContacts).toHaveBeenCalledWith(
        testCampaign.id,
        10,
        0,
        { status: 'PENDING' }
      );
    });
  });

  describe('importContacts', () => {
    it('should import contacts from CSV', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const csvData = 'phone,name,email\n+1234567890,John Doe,john@example.com\n+1987654321,Jane Smith,jane@example.com';
      const importResult = {
        imported: 2,
        failed: 0,
        duplicates: 0,
      };

      mockContactService.importFromCSV.mockResolvedValue(importResult);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.importContacts({
        id: testCampaign.id,
        csvData,
        skipDuplicates: true,
      });

      expect(result).toEqual(importResult);
      expect(mockContactService.importFromCSV).toHaveBeenCalledWith(
        testCampaign.id,
        csvData,
        true
      );
    });

    it('should require admin role for import', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);

      await expect(caller.importContacts({
        id: 'campaign-id',
        csvData: 'phone,name\n+1234567890,John',
      })).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('scheduleCallback', () => {
    it('should schedule callback for contact', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const callbackTime = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours from now

      mockCampaignService.scheduleCallback.mockResolvedValue(undefined);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.scheduleCallback({
        campaignId: testCampaign.id,
        contactId: 'contact-1',
        scheduledTime: callbackTime,
        notes: 'Customer requested callback',
      });

      expect(result.success).toBe(true);
      expect(mockCampaignService.scheduleCallback).toHaveBeenCalledWith(
        testCampaign.id,
        'contact-1',
        callbackTime,
        'Customer requested callback'
      );
    });
  });

  describe('getContactStats', () => {
    it('should return contact statistics for campaign', async () => {
      const testCampaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const mockContactStats = {
        total: 100,
        pending: 60,
        completed: 30,
        failed: 10,
        averageAttempts: 2.5,
        successRate: 75,
      };

      mockContactService.getContactStats.mockResolvedValue(mockContactStats);
      vi.spyOn(testDb.campaign, 'findUnique').mockResolvedValue(testCampaign);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
        campaignService: mockCampaignService,
        contactService: mockContactService,
      };

      const caller = campaignRouter.createCaller(mockContext);
      const result = await caller.getContactStats({ id: testCampaign.id });

      expect(result).toEqual(mockContactStats);
      expect(mockContactService.getContactStats).toHaveBeenCalledWith(testCampaign.id);
    });
  });
});