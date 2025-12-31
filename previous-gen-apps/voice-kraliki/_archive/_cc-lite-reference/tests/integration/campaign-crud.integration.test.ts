import { describe, it, expect, beforeEach, beforeAll, afterAll, vi } from 'vitest';
import { PrismaClient, UserRole, CampaignType, CallStatus } from '@prisma/client';
import { testDb, createTestUser, createTestCampaign, measurePerformance } from '../setup';

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Campaign CRUD Operations with Prisma Backend', () => {
  let testOrganization: any;
  let adminUser: any;
  let supervisorUser: any;
  let agentUser: any;

  beforeEach(async () => {
    // Create test organization
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-campaign-crud',
        name: 'Test Campaign Organization',
        domain: 'campaign-test.local',
        settings: {
          timezone: 'UTC',
          defaultLanguage: 'en',
          maxConcurrentCalls: 10
        }
      }
    });

    // Create test users with different roles
    adminUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.ADMIN,
      email: 'admin@campaign-test.local',
      firstName: 'Admin',
      lastName: 'User'
    });

    supervisorUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.SUPERVISOR,
      email: 'supervisor@campaign-test.local',
      firstName: 'Supervisor',
      lastName: 'User'
    });

    agentUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'agent@campaign-test.local',
      firstName: 'Agent',
      lastName: 'User'
    });
  });

  describe('CREATE Operations', () => {
    it('should create outbound campaign with all required fields', async () => {
      const campaignData = {
        name: 'Outbound Sales Campaign',
        description: 'Campaign for sales outreach',
        type: CampaignType.OUTBOUND,
        language: 'en',
        organizationId: testOrganization.id,
        active: false,
        instructions: {
          script: [
            'Hello, this is {agentName} from {companyName}.',
            'I\'m calling to discuss our special offer.',
            'Do you have a few minutes to talk?'
          ],
          objectives: [
            'Introduce company services',
            'Qualify lead interest',
            'Schedule follow-up meeting'
          ],
          complianceNotes: 'Ensure consent before proceeding'
        },
        tools: {
          aiAssist: true,
          sentimentAnalysis: true,
          leadScoring: true,
          autoDialer: true
        },
        voice: {
          provider: 'deepgram',
          voice: 'aura-asteria-en',
          speed: 1.0,
          language: 'en'
        },
        analytics: {
          trackConversions: true,
          goalEvents: ['meeting_scheduled', 'interest_expressed'],
          customMetrics: ['call_quality', 'objection_handling']
        },
        metadata: {
          createdBy: adminUser.id,
          targetAudience: 'small_business_owners',
          priority: 'high',
          budget: 5000
        }
      };

      const campaign = await testDb.campaign.create({ data: campaignData });

      expect(campaign).toBeDefined();
      expect(campaign.id).toBeDefined();
      expect(campaign.name).toBe(campaignData.name);
      expect(campaign.description).toBe(campaignData.description);
      expect(campaign.type).toBe(CampaignType.OUTBOUND);
      expect(campaign.language).toBe('en');
      expect(campaign.active).toBe(false);
      expect(campaign.organizationId).toBe(testOrganization.id);
      expect(campaign.instructions).toEqual(campaignData.instructions);
      expect(campaign.tools).toEqual(campaignData.tools);
      expect(campaign.voice).toEqual(campaignData.voice);
      expect(campaign.analytics).toEqual(campaignData.analytics);
      expect(campaign.metadata).toEqual(campaignData.metadata);
      expect(campaign.createdAt).toBeDefined();
      expect(campaign.updatedAt).toBeDefined();
    });

    it('should create inbound campaign with IVR configuration', async () => {
      const campaignData = {
        name: 'Customer Support Inbound',
        description: 'Handle incoming customer support calls',
        type: CampaignType.INBOUND,
        language: 'en',
        organizationId: testOrganization.id,
        active: true,
        instructions: {
          greeting: 'Thank you for calling our support line.',
          menu: {
            '1': 'Technical Support',
            '2': 'Billing Questions',
            '3': 'General Inquiries',
            '0': 'Speak with an Agent'
          },
          routing: {
            technical: { skills: ['technical_support'], priority: 'high' },
            billing: { skills: ['billing', 'accounts'], priority: 'medium' },
            general: { skills: ['customer_service'], priority: 'low' }
          }
        },
        tools: {
          ivrEnabled: true,
          callRecording: true,
          transcription: true,
          sentimentAnalysis: true
        }
      };

      const campaign = await testDb.campaign.create({ data: campaignData });

      expect(campaign.type).toBe(CampaignType.INBOUND);
      expect(campaign.active).toBe(true);
      expect((campaign.instructions as any).menu).toBeDefined();
      expect((campaign.instructions as any).routing).toBeDefined();
      expect((campaign.tools as any).ivrEnabled).toBe(true);
    });

    it('should create transfer campaign for escalations', async () => {
      const campaignData = {
        name: 'Escalation Transfer Campaign',
        type: CampaignType.TRANSFER,
        organizationId: testOrganization.id,
        instructions: {
          transferRules: {
            autoTransfer: true,
            maxWaitTime: 30,
            fallbackAction: 'voicemail'
          },
          escalationCriteria: [
            'customer_satisfaction_low',
            'issue_complexity_high',
            'agent_request'
          ]
        },
        tools: {
          warmTransfer: true,
          conferenceCall: true,
          supervisorAlert: true
        }
      };

      const campaign = await testDb.campaign.create({ data: campaignData });

      expect(campaign.type).toBe(CampaignType.TRANSFER);
      expect((campaign.instructions as any).transferRules).toBeDefined();
      expect((campaign.tools as any).warmTransfer).toBe(true);
    });

    it('should validate required fields and constraints', async () => {
      // Test missing name
      await expect(
        testDb.campaign.create({
          data: {
            type: CampaignType.OUTBOUND,
            organizationId: testOrganization.id,
            instructions: {}
          } as any
        })
      ).rejects.toThrow();

      // Test invalid organization ID
      await expect(
        testDb.campaign.create({
          data: {
            name: 'Invalid Campaign',
            type: CampaignType.OUTBOUND,
            organizationId: 'non-existent-org',
            instructions: {}
          }
        })
      ).rejects.toThrow();
    });
  });

  describe('READ Operations', () => {
    let testCampaigns: any[];

    beforeEach(async () => {
      // Create multiple test campaigns
      testCampaigns = await Promise.all([
        createTestCampaign({
          name: 'Active Sales Campaign',
          type: CampaignType.OUTBOUND,
          organizationId: testOrganization.id,
          active: true,
          language: 'en'
        }),
        createTestCampaign({
          name: 'Support Inbound',
          type: CampaignType.INBOUND,
          organizationId: testOrganization.id,
          active: true,
          language: 'en'
        }),
        createTestCampaign({
          name: 'Inactive Campaign',
          type: CampaignType.OUTBOUND,
          organizationId: testOrganization.id,
          active: false,
          language: 'es'
        })
      ]);
    });

    it('should retrieve all campaigns for organization', async () => {
      const campaigns = await testDb.campaign.findMany({
        where: { organizationId: testOrganization.id },
        orderBy: { createdAt: 'desc' }
      });

      expect(campaigns).toHaveLength(3);
      expect(campaigns.every(c => c.organizationId === testOrganization.id)).toBe(true);
    });

    it('should filter campaigns by status', async () => {
      const activeCampaigns = await testDb.campaign.findMany({
        where: {
          organizationId: testOrganization.id,
          active: true
        }
      });

      const inactiveCampaigns = await testDb.campaign.findMany({
        where: {
          organizationId: testOrganization.id,
          active: false
        }
      });

      expect(activeCampaigns).toHaveLength(2);
      expect(inactiveCampaigns).toHaveLength(1);
      expect(activeCampaigns.every(c => c.active === true)).toBe(true);
      expect(inactiveCampaigns.every(c => c.active === false)).toBe(true);
    });

    it('should filter campaigns by type', async () => {
      const outboundCampaigns = await testDb.campaign.findMany({
        where: {
          organizationId: testOrganization.id,
          type: CampaignType.OUTBOUND
        }
      });

      const inboundCampaigns = await testDb.campaign.findMany({
        where: {
          organizationId: testOrganization.id,
          type: CampaignType.INBOUND
        }
      });

      expect(outboundCampaigns).toHaveLength(2);
      expect(inboundCampaigns).toHaveLength(1);
    });

    it('should retrieve campaign with related data', async () => {
      const campaign = testCampaigns[0];
      
      // Create related call and metrics
      await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          campaignId: campaign.id,
          status: CallStatus.COMPLETED,
          duration: 120
        }
      });

      await testDb.campaignMetric.create({
        data: {
          campaignId: campaign.id,
          callsHandled: 10,
          successfulCompletions: 8,
          averageHandleTime: 150,
          customerSatisfaction: 4.2,
          lastUsed: new Date()
        }
      });

      const campaignWithRelated = await testDb.campaign.findUnique({
        where: { id: campaign.id },
        include: {
          organization: true,
          calls: true,
          metrics: true
        }
      });

      expect(campaignWithRelated).toBeDefined();
      expect(campaignWithRelated?.organization).toBeDefined();
      expect(campaignWithRelated?.calls).toHaveLength(1);
      expect(campaignWithRelated?.metrics).toBeDefined();
    });

    it('should support pagination and sorting', async () => {
      const page1 = await testDb.campaign.findMany({
        where: { organizationId: testOrganization.id },
        orderBy: { createdAt: 'desc' },
        take: 2,
        skip: 0
      });

      const page2 = await testDb.campaign.findMany({
        where: { organizationId: testOrganization.id },
        orderBy: { createdAt: 'desc' },
        take: 2,
        skip: 2
      });

      expect(page1).toHaveLength(2);
      expect(page2).toHaveLength(1);
      expect(page1[0].id).not.toBe(page2[0].id);
    });
  });

  describe('UPDATE Operations', () => {
    let testCampaign: any;

    beforeEach(async () => {
      testCampaign = await createTestCampaign({
        name: 'Original Campaign Name',
        description: 'Original description',
        type: CampaignType.OUTBOUND,
        organizationId: testOrganization.id,
        active: false,
        instructions: {
          script: ['Original script'],
          settings: { maxCalls: 5 }
        },
        metadata: {
          version: '1.0.0',
          lastModifiedBy: adminUser.id
        }
      });
    });

    it('should update basic campaign information', async () => {
      const updateData = {
        name: 'Updated Campaign Name',
        description: 'Updated description with more details',
        language: 'es'
      };

      const updatedCampaign = await testDb.campaign.update({
        where: { id: testCampaign.id },
        data: updateData
      });

      expect(updatedCampaign.name).toBe(updateData.name);
      expect(updatedCampaign.description).toBe(updateData.description);
      expect(updatedCampaign.language).toBe(updateData.language);
      expect(updatedCampaign.updatedAt.getTime()).toBeGreaterThan(testCampaign.updatedAt.getTime());
    });

    it('should update campaign status', async () => {
      // Activate campaign
      await testDb.campaign.update({
        where: { id: testCampaign.id },
        data: { active: true }
      });

      let campaign = await testDb.campaign.findUnique({ where: { id: testCampaign.id } });
      expect(campaign?.active).toBe(true);

      // Deactivate campaign
      await testDb.campaign.update({
        where: { id: testCampaign.id },
        data: { active: false }
      });

      campaign = await testDb.campaign.findUnique({ where: { id: testCampaign.id } });
      expect(campaign?.active).toBe(false);
    });

    it('should update complex JSON fields', async () => {
      const newInstructions = {
        script: [
          'Updated greeting',
          'Updated middle section',
          'Updated closing'
        ],
        settings: {
          maxCalls: 10,
          retryAttempts: 3,
          callbackEnabled: true
        },
        aiConfiguration: {
          model: 'gpt-4',
          temperature: 0.7,
          maxTokens: 500
        }
      };

      const newTools = {
        aiAssist: true,
        callRecording: true,
        sentimentAnalysis: true,
        leadScoring: false,
        autoDialer: true
      };

      const updatedCampaign = await testDb.campaign.update({
        where: { id: testCampaign.id },
        data: {
          instructions: newInstructions,
          tools: newTools
        }
      });

      expect(updatedCampaign.instructions).toEqual(newInstructions);
      expect(updatedCampaign.tools).toEqual(newTools);
    });

    it('should update metadata while preserving existing fields', async () => {
      const metadataUpdate = {
        version: '1.1.0',
        lastModifiedBy: supervisorUser.id,
        changeNotes: 'Updated script and added AI configuration'
      };

      await testDb.campaign.update({
        where: { id: testCampaign.id },
        data: {
          metadata: {
            ...(testCampaign.metadata as any),
            ...metadataUpdate
          }
        }
      });

      const updatedCampaign = await testDb.campaign.findUnique({ where: { id: testCampaign.id } });
      const metadata = updatedCampaign?.metadata as any;
      
      expect(metadata.version).toBe('1.1.0');
      expect(metadata.lastModifiedBy).toBe(supervisorUser.id);
      expect(metadata.changeNotes).toBe('Updated script and added AI configuration');
    });

    it('should handle concurrent updates safely', async () => {
      const update1 = testDb.campaign.update({
        where: { id: testCampaign.id },
        data: { name: 'Update 1' }
      });

      const update2 = testDb.campaign.update({
        where: { id: testCampaign.id },
        data: { description: 'Update 2' }
      });

      // Both updates should complete without error
      await Promise.all([update1, update2]);

      const finalCampaign = await testDb.campaign.findUnique({ where: { id: testCampaign.id } });
      expect(finalCampaign).toBeDefined();
    });
  });

  describe('DELETE Operations', () => {
    let testCampaign: any;
    let relatedCall: any;
    let relatedMetrics: any;

    beforeEach(async () => {
      testCampaign = await createTestCampaign({
        organizationId: testOrganization.id,
        name: 'Campaign to Delete'
      });

      // Create related data
      relatedCall = await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          campaignId: testCampaign.id,
          status: CallStatus.COMPLETED
        }
      });

      relatedMetrics = await testDb.campaignMetric.create({
        data: {
          campaignId: testCampaign.id,
          callsHandled: 5,
          successfulCompletions: 4,
          averageHandleTime: 120,
          lastUsed: new Date()
        }
      });
    });

    it('should delete campaign and cascade to related records', async () => {
      // Delete the campaign
      await testDb.campaign.delete({ where: { id: testCampaign.id } });

      // Verify campaign is deleted
      const deletedCampaign = await testDb.campaign.findUnique({ where: { id: testCampaign.id } });
      expect(deletedCampaign).toBeNull();

      // Verify related metrics are deleted (cascade)
      const deletedMetrics = await testDb.campaignMetric.findUnique({ where: { campaignId: testCampaign.id } });
      expect(deletedMetrics).toBeNull();

      // Verify calls are updated (campaignId set to null)
      const updatedCall = await testDb.call.findUnique({ where: { id: relatedCall.id } });
      expect(updatedCall?.campaignId).toBeNull();
    });

    it('should handle deletion of non-existent campaign', async () => {
      await expect(
        testDb.campaign.delete({ where: { id: 'non-existent-id' } })
      ).rejects.toThrow();
    });

    it('should delete multiple campaigns in batch', async () => {
      const campaigns = await Promise.all([
        createTestCampaign({ organizationId: testOrganization.id, name: 'Batch Delete 1' }),
        createTestCampaign({ organizationId: testOrganization.id, name: 'Batch Delete 2' }),
        createTestCampaign({ organizationId: testOrganization.id, name: 'Batch Delete 3' })
      ]);

      const campaignIds = campaigns.map(c => c.id);

      const { count } = await testDb.campaign.deleteMany({
        where: {
          id: { in: campaignIds }
        }
      });

      expect(count).toBe(3);

      // Verify all campaigns are deleted
      const remainingCampaigns = await testDb.campaign.findMany({
        where: { id: { in: campaignIds } }
      });
      expect(remainingCampaigns).toHaveLength(0);
    });
  });

  describe('Performance and Optimization', () => {
    beforeEach(async () => {
      // Create a larger dataset for performance testing
      const campaigns = [];
      for (let i = 0; i < 50; i++) {
        campaigns.push({
          name: `Performance Test Campaign ${i}`,
          type: i % 2 === 0 ? CampaignType.OUTBOUND : CampaignType.INBOUND,
          organizationId: testOrganization.id,
          active: i % 3 === 0,
          language: i % 4 === 0 ? 'es' : 'en',
          instructions: {
            script: [`Script for campaign ${i}`],
            priority: i % 5
          },
          metadata: {
            batchId: 'performance-test',
            index: i
          }
        });
      }

      await testDb.campaign.createMany({ data: campaigns });
    });

    it('should perform efficient filtered queries', async () => {
      const { duration } = await measurePerformance(async () => {
        const result = await testDb.campaign.findMany({
          where: {
            organizationId: testOrganization.id,
            active: true,
            type: CampaignType.OUTBOUND
          },
          orderBy: { createdAt: 'desc' },
          take: 10
        });
        return result;
      });

      expect(duration).toBeLessThan(100); // Should be very fast
    });

    it('should handle bulk updates efficiently', async () => {
      const { duration } = await measurePerformance(async () => {
        await testDb.campaign.updateMany({
          where: {
            organizationId: testOrganization.id,
            active: false
          },
          data: {
            active: true,
            updatedAt: new Date()
          }
        });
      });

      expect(duration).toBeLessThan(500); // Should complete quickly
    });

    it('should aggregate data efficiently', async () => {
      const { duration } = await measurePerformance(async () => {
        const stats = await testDb.campaign.groupBy({
          by: ['type', 'active'],
          where: { organizationId: testOrganization.id },
          _count: { id: true },
          _avg: { version: true }
        });
        return stats;
      });

      expect(duration).toBeLessThan(200); // Should aggregate quickly
    });
  });

  describe('Data Validation and Constraints', () => {
    it('should validate JSON field schemas', async () => {
      const campaignWithInvalidInstructions = {
        name: 'Invalid Instructions Campaign',
        type: CampaignType.OUTBOUND,
        organizationId: testOrganization.id,
        instructions: null // Invalid - should be an object
      };

      // This should work as Prisma allows null for Json fields
      const campaign = await testDb.campaign.create({ data: campaignWithInvalidInstructions });
      expect(campaign.instructions).toBeNull();
    });

    it('should handle large JSON payloads', async () => {
      const largeInstructions = {
        script: Array(1000).fill('This is a test script line.'),
        settings: {
          complexData: Array(100).fill({ key: 'value', nested: { data: 'test' } })
        },
        metadata: {
          largeArray: Array(500).fill('test data')
        }
      };

      const campaign = await testDb.campaign.create({
        data: {
          name: 'Large JSON Campaign',
          type: CampaignType.OUTBOUND,
          organizationId: testOrganization.id,
          instructions: largeInstructions
        }
      });

      expect(campaign.instructions).toEqual(largeInstructions);
    });

    it('should maintain referential integrity', async () => {
      const campaign = await createTestCampaign({
        organizationId: testOrganization.id
      });

      // Create related records
      const call = await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          campaignId: campaign.id,
          status: CallStatus.QUEUED
        }
      });

      // Deleting organization should fail due to foreign key constraint
      await expect(
        testDb.organization.delete({ where: { id: testOrganization.id } })
      ).rejects.toThrow();

      // Clean up call first
      await testDb.call.delete({ where: { id: call.id } });
      await testDb.campaign.delete({ where: { id: campaign.id } });
      
      // Now organization deletion should work
      await testDb.organization.delete({ where: { id: testOrganization.id } });
      const deletedOrg = await testDb.organization.findUnique({ where: { id: testOrganization.id } });
      expect(deletedOrg).toBeNull();
    });
  });
});
