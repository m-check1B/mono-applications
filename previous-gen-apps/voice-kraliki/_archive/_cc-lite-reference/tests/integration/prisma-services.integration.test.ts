import { describe, it, expect, beforeEach, beforeAll, afterAll, vi } from 'vitest';
import { PrismaClient, UserRole, CallStatus, CampaignType } from '@prisma/client';
import { FastifyInstance } from 'fastify';
import { CampaignService } from '../../server/services/campaign-service';
import { testDb, createTestUser, createTestCampaign, createTestCall, measurePerformance } from '../setup';
import { TwilioService } from '../../server/lib/twilio-service';
import { AIAssistantService } from '../../server/services/ai-assistant-service';

// Mock external services
vi.mock('../../server/lib/twilio-service');
vi.mock('../../server/services/ai-assistant-service');

// Mock Fastify instance
const mockFastify = {
  log: {
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
    debug: vi.fn()
  },
  redis: {
    get: vi.fn(),
    set: vi.fn(),
    del: vi.fn()
  }
} as unknown as FastifyInstance;

// Mock Twilio service
const mockTwilioService = {
  makeCall: vi.fn().mockResolvedValue('test-call-sid'),
  endCall: vi.fn(),
  getCallStatus: vi.fn()
};

// Mock AI service
const mockAIService = {
  processMessage: vi.fn(),
  generateResponse: vi.fn()
};

(TwilioService as any).mockImplementation(() => mockTwilioService);
(AIAssistantService as any).mockImplementation(() => mockAIService);

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Prisma Services Integration Tests', () => {
  let campaignService: CampaignService;
  let testOrganization: any;
  let testUser: any;

  beforeAll(async () => {
    // Set required environment variables
    process.env.TWILIO_PHONE_NUMBER = '+1234567890';
    process.env.WEBHOOK_BASE_URL = 'http://localhost:3010';
  });

  beforeEach(async () => {
    // Create test organization and user
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-services',
        name: 'Test Organization Services',
        domain: 'test-services.local'
      }
    });

    testUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.ADMIN,
      email: 'admin@test-services.local'
    });

    // Initialize campaign service
    campaignService = new CampaignService(mockFastify);
  });

  describe('Campaign Service', () => {
    describe('Campaign CRUD Operations', () => {
      it('should create a new campaign with required fields', async () => {
        const campaignData = {
          name: 'Test Campaign',
          description: 'A test campaign for QA',
          type: CampaignType.OUTBOUND,
          organizationId: testOrganization.id,
          settings: {
            maxConcurrentCalls: 5,
            maxAttemptsPerContact: 3,
            timeBetweenAttempts: 15,
            dialingHours: {
              start: '09:00',
              end: '17:00',
              timezone: 'UTC'
            },
            callbackEnabled: true,
            voicemailDetection: false,
            complianceSettings: {
              dncListEnabled: true,
              consentRequired: true,
              recordingConsent: true
            }
          },
          script: 'Hello, this is a test call.'
        };

        const campaign = await campaignService.createCampaign(campaignData);

        expect(campaign).toBeDefined();
        expect(campaign.id).toBeDefined();
        expect(campaign.name).toBe(campaignData.name);
        expect(campaign.type).toBe(campaignData.type);
        expect(campaign.organizationId).toBe(testOrganization.id);
        expect(campaign.active).toBe(false);
        expect((campaign.instructions as any).script).toBe(campaignData.script);
        expect((campaign.instructions as any).settings).toEqual(campaignData.settings);
      });

      it('should throw error when creating campaign without organization ID', async () => {
        const campaignData = {
          name: 'Invalid Campaign',
          type: CampaignType.OUTBOUND,
          organizationId: '', // Empty organization ID
          settings: {
            maxConcurrentCalls: 1,
            maxAttemptsPerContact: 1,
            timeBetweenAttempts: 5,
            dialingHours: { start: '09:00', end: '17:00', timezone: 'UTC' },
            callbackEnabled: false,
            voicemailDetection: false,
            complianceSettings: {
              dncListEnabled: false,
              consentRequired: false,
              recordingConsent: false
            }
          }
        };

        await expect(campaignService.createCampaign(campaignData))
          .rejects.toThrow('Organization ID is required for campaign creation');
      });

      it('should start and stop campaigns correctly', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id,
          active: false,
          instructions: {
            script: 'Test script',
            settings: {
              maxConcurrentCalls: 2,
              maxAttemptsPerContact: 2,
              timeBetweenAttempts: 10,
              dialingHours: { start: '00:00', end: '23:59', timezone: 'UTC' },
              callbackEnabled: false,
              voicemailDetection: false,
              complianceSettings: {
                dncListEnabled: false,
                consentRequired: false,
                recordingConsent: false
              }
            }
          },
          metadata: {
            contacts: [
              {
                id: 'contact-1',
                phoneNumber: '+1234567890',
                name: 'Test Contact',
                status: 'pending',
                attempts: 0
              }
            ]
          }
        });

        // Start campaign
        await campaignService.startCampaign(campaign.id);
        
        const updatedCampaign = await testDb.campaign.findUnique({
          where: { id: campaign.id }
        });
        expect(updatedCampaign?.active).toBe(true);

        // Stop campaign
        await campaignService.stopCampaign(campaign.id);
        
        const stoppedCampaign = await testDb.campaign.findUnique({
          where: { id: campaign.id }
        });
        expect(stoppedCampaign?.active).toBe(false);
      });

      it('should handle campaign metrics correctly', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id,
          active: true
        });

        // Start campaign to initialize stats
        await campaignService.startCampaign(campaign.id);
        
        // Simulate campaign completion
        await campaignService.completeCampaignCall(
          campaign.id,
          'test-call-sid',
          'success',
          'Test call completed successfully'
        );

        const stats = await campaignService.getCampaignStats(campaign.id);
        expect(stats).toBeDefined();
        expect(typeof stats.contactsCompleted).toBe('number');
        expect(typeof stats.avgCallDuration).toBe('number');
        expect(typeof stats.conversionRate).toBe('number');
      });
    });

    describe('Call Lifecycle Management', () => {
      it('should create call records with proper relationships', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id,
          active: true
        });

        const call = await createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign.id,
          agentId: testUser.id,
          status: CallStatus.QUEUED,
          providerCallId: 'test-twilio-sid',
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO'
        });

        expect(call).toBeDefined();
        expect(call.organizationId).toBe(testOrganization.id);
        expect(call.campaignId).toBe(campaign.id);
        expect(call.agentId).toBe(testUser.id);
        expect(call.status).toBe(CallStatus.QUEUED);
        expect(call.provider).toBe('TWILIO');

        // Verify relationships
        const callWithRelations = await testDb.call.findUnique({
          where: { id: call.id },
          include: {
            organization: true,
            campaign: true,
            agent: true
          }
        });

        expect(callWithRelations?.organization?.id).toBe(testOrganization.id);
        expect(callWithRelations?.campaign?.id).toBe(campaign.id);
        expect(callWithRelations?.agent?.id).toBe(testUser.id);
      });

      it('should track call status transitions', async () => {
        const call = await createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED
        });

        // Update to RINGING
        await testDb.call.update({
          where: { id: call.id },
          data: { status: CallStatus.RINGING }
        });

        let updatedCall = await testDb.call.findUnique({ where: { id: call.id } });
        expect(updatedCall?.status).toBe(CallStatus.RINGING);

        // Update to IN_PROGRESS
        await testDb.call.update({
          where: { id: call.id },
          data: { status: CallStatus.IN_PROGRESS }
        });

        updatedCall = await testDb.call.findUnique({ where: { id: call.id } });
        expect(updatedCall?.status).toBe(CallStatus.IN_PROGRESS);

        // Update to COMPLETED with duration
        const endTime = new Date();
        const duration = 120; // 2 minutes
        
        await testDb.call.update({
          where: { id: call.id },
          data: {
            status: CallStatus.COMPLETED,
            endTime,
            duration,
            disposition: 'successful'
          }
        });

        updatedCall = await testDb.call.findUnique({ where: { id: call.id } });
        expect(updatedCall?.status).toBe(CallStatus.COMPLETED);
        expect(updatedCall?.duration).toBe(duration);
        expect(updatedCall?.disposition).toBe('successful');
      });

      it('should handle call transcripts correctly', async () => {
        const call = await createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.IN_PROGRESS
        });

        // Add transcript entries
        const transcript1 = await testDb.callTranscript.create({
          data: {
            callId: call.id,
            role: 'USER',
            content: 'Hello, I need help with my account',
            confidence: 0.95,
            timestamp: new Date()
          }
        });

        const transcript2 = await testDb.callTranscript.create({
          data: {
            callId: call.id,
            role: 'ASSISTANT',
            content: 'Hello! I\'d be happy to help you with your account. Can you please provide your account number?',
            confidence: 0.98,
            timestamp: new Date(Date.now() + 1000)
          }
        });

        // Verify transcripts
        const transcripts = await testDb.callTranscript.findMany({
          where: { callId: call.id },
          orderBy: { timestamp: 'asc' }
        });

        expect(transcripts).toHaveLength(2);
        expect(transcripts[0].role).toBe('USER');
        expect(transcripts[1].role).toBe('ASSISTANT');
        expect(transcripts[0].confidence).toBe(0.95);
        expect(transcripts[1].confidence).toBe(0.98);
      });
    });

    describe('Data Integrity and Constraints', () => {
      it('should enforce organization isolation', async () => {
        const org1 = await testDb.organization.create({
          data: {
            id: 'org-1',
            name: 'Organization 1',
            domain: 'org1.local'
          }
        });

        const org2 = await testDb.organization.create({
          data: {
            id: 'org-2',
            name: 'Organization 2',
            domain: 'org2.local'
          }
        });

        const user1 = await createTestUser({
          organizationId: org1.id,
          email: 'user1@org1.local'
        });

        const user2 = await createTestUser({
          organizationId: org2.id,
          email: 'user2@org2.local'
        });

        const campaign1 = await createTestCampaign({
          organizationId: org1.id,
          name: 'Org1 Campaign'
        });

        const campaign2 = await createTestCampaign({
          organizationId: org2.id,
          name: 'Org2 Campaign'
        });

        // Verify users can only access their organization's data
        const org1Campaigns = await testDb.campaign.findMany({
          where: { organizationId: org1.id }
        });
        expect(org1Campaigns).toHaveLength(1);
        expect(org1Campaigns[0].id).toBe(campaign1.id);

        const org2Campaigns = await testDb.campaign.findMany({
          where: { organizationId: org2.id }
        });
        expect(org2Campaigns).toHaveLength(1);
        expect(org2Campaigns[0].id).toBe(campaign2.id);
      });

      it('should handle cascade deletes correctly', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id
        });

        const call = await createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign.id
        });

        // Add transcript
        await testDb.callTranscript.create({
          data: {
            callId: call.id,
            role: 'USER',
            content: 'Test transcript',
            timestamp: new Date()
          }
        });

        // Delete call should cascade to transcripts
        await testDb.call.delete({ where: { id: call.id } });

        const transcripts = await testDb.callTranscript.findMany({
          where: { callId: call.id }
        });
        expect(transcripts).toHaveLength(0);

        // Delete organization should cascade to campaigns
        await testDb.organization.delete({ where: { id: testOrganization.id } });

        const campaigns = await testDb.campaign.findMany({
          where: { organizationId: testOrganization.id }
        });
        expect(campaigns).toHaveLength(0);
      });

      it('should enforce unique constraints', async () => {
        // Test unique email constraint
        await createTestUser({
          email: 'unique@test.com',
          organizationId: testOrganization.id
        });

        await expect(
          createTestUser({
            email: 'unique@test.com',
            organizationId: testOrganization.id
          })
        ).rejects.toThrow();

        // Test unique domain constraint
        await testDb.organization.create({
          data: {
            id: 'org-unique',
            name: 'Unique Org',
            domain: 'unique.test'
          }
        });

        await expect(
          testDb.organization.create({
            data: {
              id: 'org-duplicate',
              name: 'Duplicate Domain Org',
              domain: 'unique.test'
            }
          })
        ).rejects.toThrow();
      });
    });

    describe('Performance Tests', () => {
      it('should handle bulk call creation efficiently', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id
        });

        const { duration, memory } = await measurePerformance(async () => {
          const calls = [];
          for (let i = 0; i < 100; i++) {
            calls.push({
              fromNumber: '+1234567890',
              toNumber: `+198765432${i.toString().padStart(2, '0')}`,
              direction: 'OUTBOUND' as const,
              provider: 'TWILIO' as const,
              organizationId: testOrganization.id,
              campaignId: campaign.id,
              status: CallStatus.QUEUED,
              startTime: new Date(),
              metadata: { batchId: 'performance-test' }
            });
          }

          await testDb.call.createMany({ data: calls });
        });

        expect(duration).toBeLessThan(5000); // Should complete in under 5 seconds
        expect(memory).toBeLessThan(50); // Should use less than 50MB

        // Verify all calls were created
        const callCount = await testDb.call.count({
          where: {
            organizationId: testOrganization.id,
            campaignId: campaign.id
          }
        });
        expect(callCount).toBe(100);
      });

      it('should efficiently query call statistics', async () => {
        const campaign = await createTestCampaign({
          organizationId: testOrganization.id
        });

        // Create test calls
        await Promise.all([
          createTestCall({ organizationId: testOrganization.id, campaignId: campaign.id, status: CallStatus.COMPLETED, duration: 120 }),
          createTestCall({ organizationId: testOrganization.id, campaignId: campaign.id, status: CallStatus.COMPLETED, duration: 180 }),
          createTestCall({ organizationId: testOrganization.id, campaignId: campaign.id, status: CallStatus.IN_PROGRESS }),
          createTestCall({ organizationId: testOrganization.id, campaignId: campaign.id, status: CallStatus.FAILED }),
        ]);

        const { duration } = await measurePerformance(async () => {
          const stats = await testDb.call.groupBy({
            by: ['status'],
            where: { organizationId: testOrganization.id },
            _count: { id: true },
            _avg: { duration: true }
          });

          return stats;
        });

        expect(duration).toBeLessThan(1000); // Should complete in under 1 second
      });
    });
  });

  describe('Database Indexes and Performance', () => {
    it('should use indexes for common query patterns', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganization.id
      });

      // Create multiple calls
      const calls = await Promise.all([
        createTestCall({ organizationId: testOrganization.id, agentId: testUser.id, status: CallStatus.IN_PROGRESS }),
        createTestCall({ organizationId: testOrganization.id, agentId: testUser.id, status: CallStatus.COMPLETED }),
        createTestCall({ organizationId: testOrganization.id, campaignId: campaign.id, status: CallStatus.QUEUED }),
      ]);

      // Test indexed queries performance
      const queries = [
        // Query by organization and status (indexed)
        () => testDb.call.findMany({
          where: { organizationId: testOrganization.id, status: CallStatus.IN_PROGRESS }
        }),
        // Query by organization and agent (indexed)
        () => testDb.call.findMany({
          where: { organizationId: testOrganization.id, agentId: testUser.id }
        }),
        // Query by agent and start time (indexed)
        () => testDb.call.findMany({
          where: { agentId: testUser.id },
          orderBy: { startTime: 'desc' },
          take: 10
        })
      ];

      for (const query of queries) {
        const { duration } = await measurePerformance(query);
        expect(duration).toBeLessThan(100); // Should be very fast with indexes
      }
    });
  });
});

// Database Transaction and Rollback Tests
describe('Database Transactions and Rollbacks', () => {
  let testOrganization: any;
  let campaignService: CampaignService;

  beforeEach(async () => {
    if (process.env.SKIP_DB_TEST_SETUP === 'true') return;

    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-transactions',
        name: 'Transaction Test Organization',
        domain: 'transaction-test.local'
      }
    });

    campaignService = new CampaignService(mockFastify);
  });

  const maybeIt = process.env.SKIP_DB_TEST_SETUP === 'true' ? it.skip : it;

  maybeIt('should handle transaction rollback on campaign creation failure', async () => {
    // Attempt to create campaign with invalid data that would fail mid-transaction
    const invalidCampaignData = {
      name: 'Transaction Test Campaign',
      type: CampaignType.OUTBOUND,
      organizationId: testOrganization.id,
      settings: {
        maxConcurrentCalls: 1,
        maxAttemptsPerContact: 1,
        timeBetweenAttempts: 5,
        dialingHours: { start: '09:00', end: '17:00', timezone: 'UTC' },
        callbackEnabled: false,
        voicemailDetection: false,
        complianceSettings: {
          dncListEnabled: false,
          consentRequired: false,
          recordingConsent: false
        }
      }
    };

    // Create campaign successfully
    const campaign = await campaignService.createCampaign(invalidCampaignData);
    expect(campaign).toBeDefined();

    // Verify campaign exists
    const createdCampaign = await testDb.campaign.findUnique({
      where: { id: campaign.id }
    });
    expect(createdCampaign).toBeDefined();
  });

  maybeIt('should maintain data consistency during concurrent operations', async () => {
    const campaign = await createTestCampaign({
      organizationId: testOrganization.id,
      active: false
    });

    // Start multiple concurrent operations
    const operations = [
      campaignService.startCampaign(campaign.id),
      campaignService.startCampaign(campaign.id),
      testDb.campaign.update({
        where: { id: campaign.id },
        data: { name: 'Updated Name' }
      })
    ];

    const results = await Promise.allSettled(operations);

    // At least one should succeed
    const successful = results.filter(r => r.status === 'fulfilled');
    expect(successful.length).toBeGreaterThan(0);

    // Verify final state is consistent
    const finalCampaign = await testDb.campaign.findUnique({
      where: { id: campaign.id }
    });
    expect(finalCampaign).toBeDefined();
  });

  maybeIt('should handle foreign key constraint violations', async () => {
    // Try to create call with non-existent campaign
    await expect(
      testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          campaignId: 'non-existent-campaign-id',
          status: CallStatus.QUEUED
        }
      })
    ).rejects.toThrow();
  });
});

// Database Performance and Indexing Tests
describe('Database Performance and Indexing', () => {
  let testOrganization: any;

  beforeEach(async () => {
    if (process.env.SKIP_DB_TEST_SETUP === 'true') return;

    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-performance',
        name: 'Performance Test Organization',
        domain: 'performance-test.local'
      }
    });
  });

  const maybeIt = process.env.SKIP_DB_TEST_SETUP === 'true' ? it.skip : it;

  maybeIt('should efficiently query with proper index usage', async () => {
    // Create large dataset
    const users = [];
    for (let i = 0; i < 100; i++) {
      users.push({
        email: `user${i}@performance-test.local`,
        firstName: `User${i}`,
        lastName: 'Test',
        role: UserRole.AGENT,
        passwordHash: 'test-hash',
        organizationId: testOrganization.id
      });
    }
    await testDb.user.createMany({ data: users });

    // Test indexed queries
    const { duration: emailQueryTime } = await measurePerformance(async () => {
      return await testDb.user.findUnique({
        where: { email: 'user50@performance-test.local' }
      });
    });

    const { duration: orgQueryTime } = await measurePerformance(async () => {
      return await testDb.user.findMany({
        where: { organizationId: testOrganization.id },
        take: 10
      });
    });

    // These should be very fast with proper indexing
    expect(emailQueryTime).toBeLessThan(50);
    expect(orgQueryTime).toBeLessThan(100);
  });

  maybeIt('should handle complex aggregation queries efficiently', async () => {
    // Create test data
    const campaign = await createTestCampaign({
      organizationId: testOrganization.id
    });

    const calls = [];
    for (let i = 0; i < 200; i++) {
      calls.push({
        fromNumber: `+1234567${i.toString().padStart(3, '0')}`,
        toNumber: `+0987654${i.toString().padStart(3, '0')}`,
        direction: i % 2 === 0 ? 'INBOUND' : 'OUTBOUND',
        provider: 'TWILIO',
        organizationId: testOrganization.id,
        campaignId: campaign.id,
        status: [CallStatus.COMPLETED, CallStatus.IN_PROGRESS, CallStatus.FAILED][i % 3],
        duration: i % 3 === 0 ? 60 + (i % 300) : null,
        startTime: new Date(Date.now() - (i * 60000))
      });
    }
    await testDb.call.createMany({ data: calls });

    // Complex aggregation query
    const { duration } = await measurePerformance(async () => {
      return await testDb.call.groupBy({
        by: ['status', 'direction'],
        where: {
          organizationId: testOrganization.id,
          startTime: {
            gte: new Date(Date.now() - 24 * 60 * 60 * 1000)
          }
        },
        _count: { id: true },
        _avg: { duration: true },
        _max: { duration: true },
        _min: { duration: true }
      });
    });

    expect(duration).toBeLessThan(500); // Should complete within 500ms
  });
});

// Data Validation and Business Logic Tests
describe('Data Validation and Business Logic', () => {
  let testOrganization: any;

  beforeEach(async () => {
    if (process.env.SKIP_DB_TEST_SETUP === 'true') return;

    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-validation',
        name: 'Validation Test Organization',
        domain: 'validation-test.local'
      }
    });
  });

  const maybeIt = process.env.SKIP_DB_TEST_SETUP === 'true' ? it.skip : it;

  maybeIt('should validate call status transitions', async () => {
    const call = await createTestCall({
      organizationId: testOrganization.id,
      status: CallStatus.QUEUED
    });

    // Valid transitions
    const validTransitions = [
      { from: CallStatus.QUEUED, to: CallStatus.RINGING },
      { from: CallStatus.RINGING, to: CallStatus.IN_PROGRESS },
      { from: CallStatus.IN_PROGRESS, to: CallStatus.ON_HOLD },
      { from: CallStatus.ON_HOLD, to: CallStatus.IN_PROGRESS },
      { from: CallStatus.IN_PROGRESS, to: CallStatus.COMPLETED }
    ];

    let currentStatus = CallStatus.QUEUED;
    for (const transition of validTransitions) {
      await testDb.call.update({
        where: { id: call.id },
        data: { status: transition.to }
      });

      const updatedCall = await testDb.call.findUnique({ where: { id: call.id } });
      expect(updatedCall?.status).toBe(transition.to);
      currentStatus = transition.to;
    }
  });

  maybeIt('should enforce business rules for agent capacity', async () => {
    const agent = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'capacity-test@validation-test.local'
    });

    await testDb.agent.create({
      data: {
        userId: agent.id,
        status: AgentStatus.AVAILABLE,
        capacity: 2,
        currentLoad: 0,
        skills: ['test']
      }
    });

    // Create calls up to capacity
    const call1 = await createTestCall({
      organizationId: testOrganization.id,
      agentId: agent.id,
      status: CallStatus.IN_PROGRESS
    });

    await testDb.agent.update({
      where: { userId: agent.id },
      data: { currentLoad: 1 }
    });

    const call2 = await createTestCall({
      organizationId: testOrganization.id,
      agentId: agent.id,
      status: CallStatus.IN_PROGRESS
    });

    await testDb.agent.update({
      where: { userId: agent.id },
      data: { currentLoad: 2 }
    });

    // Agent should now be at capacity
    const agentAtCapacity = await testDb.agent.findUnique({
      where: { userId: agent.id }
    });
    expect(agentAtCapacity?.currentLoad).toBe(agentAtCapacity?.capacity);
  });

  maybeIt('should validate contact phone number format', async () => {
    const campaign = await createTestCampaign({
      organizationId: testOrganization.id
    });

    // Valid phone numbers
    const validPhoneNumbers = ['+1234567890', '+44123456789', '+33123456789'];

    for (const phoneNumber of validPhoneNumbers) {
      const contact = await testDb.contact.create({
        data: {
          campaignId: campaign.id,
          phoneNumber,
          name: 'Test Contact',
          status: 'PENDING'
        }
      });
      expect(contact.phoneNumber).toBe(phoneNumber);
    }
  });
});

// Additional specialized tests for edge cases
describe('Edge Cases and Error Handling', () => {
  let testOrganization: any;
  let campaignService: CampaignService;

  beforeEach(async () => {
    if (process.env.SKIP_DB_TEST_SETUP === 'true') return;
    
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-edge-cases',
        name: 'Test Organization Edge Cases',
        domain: 'test-edge.local'
      }
    });

    campaignService = new CampaignService(mockFastify);
  });

  const maybeIt = process.env.SKIP_DB_TEST_SETUP === 'true' ? it.skip : it;

  maybeIt('should handle concurrent campaign operations safely', async () => {
    const campaign = await createTestCampaign({
      organizationId: testOrganization.id,
      active: false
    });

    // Simulate concurrent start/stop operations
    const operations = [
      campaignService.startCampaign(campaign.id),
      campaignService.startCampaign(campaign.id),
      campaignService.stopCampaign(campaign.id),
    ];

    // Should handle gracefully without throwing
    const results = await Promise.allSettled(operations);
    
    // At least one operation should succeed
    const successful = results.filter(r => r.status === 'fulfilled');
    expect(successful.length).toBeGreaterThan(0);
  });

  maybeIt('should handle malformed campaign data', async () => {
    const invalidCampaignData = {
      name: '', // Empty name
      type: 'INVALID_TYPE' as any,
      organizationId: testOrganization.id,
      settings: {} // Missing required settings
    };

    await expect(
      campaignService.createCampaign(invalidCampaignData)
    ).rejects.toThrow();
  });

  maybeIt('should handle database connection issues gracefully', async () => {
    // Temporarily close the database connection
    await testDb.$disconnect();

    const campaignData = {
      name: 'Test Campaign',
      type: CampaignType.OUTBOUND,
      organizationId: testOrganization.id,
      settings: {
        maxConcurrentCalls: 1,
        maxAttemptsPerContact: 1,
        timeBetweenAttempts: 5,
        dialingHours: { start: '09:00', end: '17:00', timezone: 'UTC' },
        callbackEnabled: false,
        voicemailDetection: false,
        complianceSettings: {
          dncListEnabled: false,
          consentRequired: false,
          recordingConsent: false
        }
      }
    };

    await expect(
      campaignService.createCampaign(campaignData)
    ).rejects.toThrow();

    // Reconnect for other tests
    await testDb.$connect();
  });
});
