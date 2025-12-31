import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CampaignService } from '../../../server/services/campaign-service';
import { testDb, createTestUser, createTestCampaign, waitFor } from '../../setup';
import { FastifyInstance } from 'fastify';
import { CampaignType, UserRole, ContactStatus } from '@prisma/client';

const skipDb = process.env.SKIP_DB_TEST_SETUP === 'true';

// Mock dependencies
const mockFastify = {
  log: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
} as unknown as FastifyInstance;

// Mock TwilioService
vi.mock('../../../server/lib/twilio-service', () => ({
  TwilioService: vi.fn().mockImplementation(() => ({
    makeCall: vi.fn().mockResolvedValue('test-call-sid'),
    endCall: vi.fn().mockResolvedValue(true),
  })),
}));

// Mock AI services
vi.mock('../../../server/services/ai-assistant-service', () => ({
  AIAssistantService: vi.fn().mockImplementation(() => ({
    processCallInput: vi.fn().mockResolvedValue({
      text: 'AI response',
      confidence: 0.9,
    }),
  })),
}));

// Mock file system for CSV import
vi.mock('fs', async (importOriginal) => {
  const actual = await importOriginal<typeof import('node:fs')>();
  return {
    ...actual,
    readFile: vi.fn(),
    createReadStream: vi.fn(),
    default: {
      ...actual,
      readFile: vi.fn(),
      createReadStream: vi.fn()
    }
  };
});

const maybeDescribe = skipDb ? describe.skip : describe;

maybeDescribe('CampaignService', () => {
  let campaignService: CampaignService;
  let testOrganizationId: string;
  let testUserId: string;

  beforeEach(async () => {
    campaignService = new CampaignService(mockFastify, testDb);
    testOrganizationId = 'test-org';

    const user = await createTestUser({
      email: 'test@example.com',
      role: UserRole.ADMIN,
      organizationId: testOrganizationId,
    });
    testUserId = user.id;
  });

  afterEach(() => {
    vi.clearAllMocks();
    // Clean up any active intervals
    (campaignService as any).dialerIntervals.forEach((interval: NodeJS.Timeout) => {
      clearInterval(interval);
    });
    (campaignService as any).dialerIntervals.clear();
    (campaignService as any).activeCampaigns.clear();
  });

  describe('createCampaign', () => {
    it('should create a new campaign with valid data', async () => {
      const campaignData = {
        name: 'Test Campaign',
        description: 'A test campaign for unit testing',
        type: CampaignType.OUTBOUND,
        organizationId: testOrganizationId,
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
        script: 'Hello, this is a test campaign script.',
      };

      const campaign = await campaignService.createCampaign(campaignData);

      expect(campaign).toBeDefined();
      expect(campaign.name).toBe(campaignData.name);
      expect(campaign.description).toBe(campaignData.description);
      expect(campaign.type).toBe(campaignData.type);
      expect(campaign.organizationId).toBe(testOrganizationId);
      expect(campaign.active).toBe(false);
      expect(campaign.instructions).toMatchObject({
        script: campaignData.script,
        settings: campaignData.settings,
      });
      expect(campaign.analytics).toMatchObject({
        stats: {
          totalContacts: 0,
          contactsDialed: 0,
          contactsConnected: 0,
          contactsCompleted: 0,
          avgCallDuration: 0,
          conversionRate: 0,
          callbacks: 0,
        },
      });
      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Campaign created')
      );
    });

    it('should throw error when organization ID is missing', async () => {
      const campaignData = {
        name: 'Test Campaign',
        type: CampaignType.OUTBOUND,
        organizationId: '',
        settings: {} as any,
      };

      await expect(campaignService.createCampaign(campaignData)).rejects.toThrow(
        'Organization ID is required for campaign creation'
      );
    });
  });

  describe('importContacts', () => {
    it('should import contacts from CSV successfully', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      // Mock ContactService.importFromCSV
      const mockContactService = (campaignService as any).contactService;
      mockContactService.importFromCSV = vi.fn().mockResolvedValue({
        imported: 10,
        failed: 2,
        duplicates: 1,
      });

      // Mock fs.readFile
      const fs = await import('fs');
      (fs.readFile as any).mockImplementation((path: string, encoding: string, callback: Function) => {
        callback(null, 'phone,name\n+1234567890,John Doe\n+1987654321,Jane Smith');
      });

      const result = await campaignService.importContacts(campaign.id, '/test/path.csv');

      expect(result.imported).toBe(10);
      expect(result.failed).toBe(3); // failed + duplicates
      expect(mockContactService.importFromCSV).toHaveBeenCalledWith(
        campaign.id,
        expect.any(String),
        true
      );
    });

    it('should handle import errors gracefully', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      // Mock ContactService.importFromCSV to throw error
      const mockContactService = (campaignService as any).contactService;
      mockContactService.importFromCSV = vi.fn().mockRejectedValue(
        new Error('Import failed')
      );

      await expect(
        campaignService.importContacts(campaign.id, '/test/path.csv')
      ).rejects.toThrow('Import failed');

      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error importing contacts')
      );
    });
  });

  describe('startCampaign', () => {
    it('should start a campaign successfully', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: false,
      });

      // Mock ContactService methods
      const mockContactService = (campaignService as any).contactService;
      mockContactService.getCampaignContacts = vi.fn().mockResolvedValue({
        contacts: [
          { id: '1', phoneNumber: '+1234567890', status: ContactStatus.PENDING },
          { id: '2', phoneNumber: '+1987654321', status: ContactStatus.PENDING },
        ],
      });
      mockContactService.getContactStats = vi.fn().mockResolvedValue({
        total: 2,
        pending: 2,
        completed: 0,
      });

      await campaignService.startCampaign(campaign.id);

      // Verify campaign was updated to active
      const updatedCampaign = await testDb.campaign.findUnique({
        where: { id: campaign.id },
      });
      expect(updatedCampaign?.active).toBe(true);

      // Verify campaign is tracked in activeCampaigns
      const activeCampaigns = (campaignService as any).activeCampaigns;
      expect(activeCampaigns.has(campaign.id)).toBe(true);

      // Verify dialer interval was created
      const dialerIntervals = (campaignService as any).dialerIntervals;
      expect(dialerIntervals.has(campaign.id)).toBe(true);

      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Campaign started')
      );
    });

    it('should throw error for non-existent campaign', async () => {
      await expect(
        campaignService.startCampaign('non-existent-id')
      ).rejects.toThrow('Campaign not found');
    });

    it('should throw error if campaign is already active', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: true,
      });

      await expect(campaignService.startCampaign(campaign.id)).rejects.toThrow(
        'Campaign is already active'
      );
    });
  });

  describe('stopCampaign', () => {
    it('should stop an active campaign', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
        active: true,
      });

      // Simulate an active campaign
      const activeCampaigns = (campaignService as any).activeCampaigns;
      const dialerIntervals = (campaignService as any).dialerIntervals;

      activeCampaigns.set(campaign.id, { campaign, settings: {} });
      dialerIntervals.set(campaign.id, setInterval(() => {}, 1000));

      await campaignService.stopCampaign(campaign.id);

      // Verify campaign was updated to inactive
      const updatedCampaign = await testDb.campaign.findUnique({
        where: { id: campaign.id },
      });
      expect(updatedCampaign?.active).toBe(false);

      // Verify campaign was removed from tracking
      expect(activeCampaigns.has(campaign.id)).toBe(false);
      expect(dialerIntervals.has(campaign.id)).toBe(false);

      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Campaign stopped')
      );
    });
  });

  describe('getCampaignStats', () => {
    it('should return stats for active campaign', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      // Mock active campaign data
      const activeCampaigns = (campaignService as any).activeCampaigns;
      activeCampaigns.set(campaign.id, {
        stats: {
          totalContacts: 100,
          contactsDialed: 50,
          contactsConnected: 40,
          contactsCompleted: 35,
          avgCallDuration: 120,
          conversionRate: 0.7,
          callbacks: 5,
        },
      });

      const stats = await campaignService.getCampaignStats(campaign.id);

      expect(stats.totalContacts).toBe(100);
      expect(stats.contactsDialed).toBe(50);
      expect(stats.contactsConnected).toBe(40);
      expect(stats.contactsCompleted).toBe(35);
      expect(stats.avgCallDuration).toBe(120);
      expect(stats.conversionRate).toBe(0.7);
      expect(stats.callbacks).toBe(5);
    });

    it('should return stats from database for inactive campaign', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
        analytics: {
          stats: {
            totalContacts: 50,
            contactsDialed: 25,
            contactsConnected: 20,
            contactsCompleted: 18,
            avgCallDuration: 90,
            conversionRate: 0.8,
            callbacks: 2,
          },
        },
      });

      const stats = await campaignService.getCampaignStats(campaign.id);

      expect(stats.totalContacts).toBe(50);
      expect(stats.contactsDialed).toBe(25);
      expect(stats.contactsConnected).toBe(20);
      expect(stats.contactsCompleted).toBe(18);
      expect(stats.avgCallDuration).toBe(90);
      expect(stats.conversionRate).toBe(0.8);
      expect(stats.callbacks).toBe(2);
    });

    it('should throw error for non-existent campaign', async () => {
      await expect(
        campaignService.getCampaignStats('non-existent-id')
      ).rejects.toThrow('Campaign not found');
    });
  });

  describe('handleCampaignCall', () => {
    it('should generate TwiML response for campaign call', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
        instructions: {
          script: 'Welcome to our service',
        },
      });

      // Mock active campaign data
      const activeCampaigns = (campaignService as any).activeCampaigns;
      activeCampaigns.set(campaign.id, {
        campaign,
        settings: {},
        activeCalls: new Map([
          ['test-call-sid', {
            contact: { id: 'contact-1', status: 'pending' },
            call: { id: 'call-1' },
          }],
        ]),
        stats: { contactsConnected: 0 },
      });

      const twiml = await campaignService.handleCampaignCall(
        campaign.id,
        'contact-1',
        'test-call-sid'
      );

      expect(twiml).toContain('Welcome to our service');
      expect(twiml).toContain('<Response>');
      expect(twiml).toContain('<Say voice="alice">');

      // Verify stats were updated
      const campaignData = activeCampaigns.get(campaign.id);
      expect(campaignData.stats.contactsConnected).toBe(1);
    });

    it('should throw error for non-existent campaign', async () => {
      await expect(
        campaignService.handleCampaignCall('non-existent', 'contact-1', 'call-sid')
      ).rejects.toThrow('Campaign not found');
    });

    it('should throw error for non-existent call', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const activeCampaigns = (campaignService as any).activeCampaigns;
      activeCampaigns.set(campaign.id, {
        activeCalls: new Map(),
      });

      await expect(
        campaignService.handleCampaignCall(campaign.id, 'contact-1', 'invalid-sid')
      ).rejects.toThrow('Call not found');
    });
  });

  describe('completeCampaignCall', () => {
    it('should complete campaign call and update stats', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      // Create test call in database
      const call = await testDb.call.create({
        data: {
          id: 'test-call-id',
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganizationId,
          startTime: new Date(),
          status: 'IN_PROGRESS',
          metadata: {},
        },
      });

      // Mock active campaign data
      const activeCampaigns = (campaignService as any).activeCampaigns;
      activeCampaigns.set(campaign.id, {
        activeCalls: new Map([
          ['test-call-sid', {
            contact: { id: 'contact-1', status: 'connected' },
            call: call,
            startTime: new Date(Date.now() - 60000), // 1 minute ago
          }],
        ]),
        stats: {
          contactsCompleted: 0,
          avgCallDuration: 0,
          conversionRate: 0,
        },
      });

      await campaignService.completeCampaignCall(
        campaign.id,
        'test-call-sid',
        'success',
        'Customer was satisfied'
      );

      // Verify call was updated in database
      const updatedCall = await testDb.call.findUnique({
        where: { id: call.id },
      });
      expect(updatedCall?.status).toBe('COMPLETED');
      expect(updatedCall?.disposition).toBe('success');
      expect(updatedCall?.notes).toBe('Customer was satisfied');
      expect(updatedCall?.duration).toBeGreaterThan(0);

      // Verify stats were updated
      const campaignData = activeCampaigns.get(campaign.id);
      expect(campaignData.stats.contactsCompleted).toBe(1);
      expect(campaignData.stats.avgCallDuration).toBeGreaterThan(0);

      // Verify call was removed from active calls
      expect(campaignData.activeCalls.has('test-call-sid')).toBe(false);
    });
  });

  describe('scheduleCallback', () => {
    it('should schedule a callback for a contact', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const callbackTime = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours from now

      // Mock active campaign data
      const activeCampaigns = (campaignService as any).activeCampaigns;
      activeCampaigns.set(campaign.id, {
        contacts: [
          { id: 'contact-1', status: 'pending', nextAttempt: null },
        ],
        stats: { callbacks: 0 },
      });

      await campaignService.scheduleCallback(
        campaign.id,
        'contact-1',
        callbackTime,
        'Customer requested callback'
      );

      const campaignData = activeCampaigns.get(campaign.id);
      const contact = campaignData.contacts.find((c: any) => c.id === 'contact-1');

      expect(contact.status).toBe('scheduled');
      expect(contact.nextAttempt).toEqual(callbackTime);
      expect(contact.notes).toBe('Customer requested callback');
      expect(campaignData.stats.callbacks).toBe(1);

      expect(mockFastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('Callback scheduled')
      );
    });
  });

  describe('getCampaignContacts', () => {
    it('should delegate to ContactService', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganizationId,
      });

      const mockContacts = [
        { id: '1', phoneNumber: '+1234567890' },
        { id: '2', phoneNumber: '+1987654321' },
      ];

      // Mock ContactService
      const mockContactService = (campaignService as any).contactService;
      mockContactService.getCampaignContacts = vi.fn().mockResolvedValue({
        contacts: mockContacts,
      });

      const contacts = await campaignService.getCampaignContacts(campaign.id, 10, 0);

      expect(contacts).toEqual(mockContacts);
      expect(mockContactService.getCampaignContacts).toHaveBeenCalledWith(
        campaign.id,
        10,
        0
      );
    });
  });

  describe('Private helper methods', () => {
    it('should check if current time is within dialing hours', () => {
      const campaignService = new CampaignService(mockFastify, testDb);

      // Access private method via any cast for testing
      const isWithinDialingHours = (campaignService as any).isWithinDialingHours.bind(campaignService);

      const dialingHours = {
        start: '09:00',
        end: '17:00',
        timezone: 'UTC',
      };

      // Mock current time to be within hours (12:00)
      const mockDate = new Date();
      mockDate.setHours(12, 0, 0, 0);
      vi.spyOn(Date, 'now').mockReturnValue(mockDate.getTime());

      expect(isWithinDialingHours(dialingHours)).toBe(true);

      // Mock current time to be outside hours (20:00)
      mockDate.setHours(20, 0, 0, 0);
      vi.spyOn(Date, 'now').mockReturnValue(mockDate.getTime());

      expect(isWithinDialingHours(dialingHours)).toBe(false);
    });

    it('should normalize phone numbers correctly', () => {
      const campaignService = new CampaignService(mockFastify, testDb);

      // Access private method via any cast for testing
      const normalizePhoneNumber = (campaignService as any).normalizePhoneNumber.bind(campaignService);

      expect(normalizePhoneNumber('1234567890')).toBe('+11234567890');
      expect(normalizePhoneNumber('11234567890')).toBe('+11234567890');
      expect(normalizePhoneNumber('+1234567890')).toBe('+11234567890');
      expect(normalizePhoneNumber('(123) 456-7890')).toBe('+11234567890');
      expect(normalizePhoneNumber('123-456-7890')).toBe('+11234567890');
      expect(normalizePhoneNumber('123')).toBeNull(); // Too short
      expect(normalizePhoneNumber('')).toBeNull(); // Empty
      expect(normalizePhoneNumber('21234567890')).toBeNull(); // Wrong prefix
    });
  });
});
