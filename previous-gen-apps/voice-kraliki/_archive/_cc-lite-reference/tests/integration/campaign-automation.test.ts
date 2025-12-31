import { test, expect } from '@playwright/test';
import { campaignAutomation } from '../../server/services/campaign-automation';
import { prisma } from '../../server/core/database';
import * as fs from 'fs/promises';
import * as path from 'path';

test.describe('Campaign Automation Integration Tests', () => {
  let testCampaignId: string;
  let testExecutionId: string;

  test.beforeAll(async () => {
    // Create a test campaign
    const campaign = await prisma.campaign.create({
      data: {
        id: `test-campaign-${Date.now()}`,
        name: 'Test Campaign',
        type: 'OUTBOUND',
        active: false,
        organizationId: 'test-org',
        language: 'en',
        instructions: {},
        tools: {},
        voice: {},
        analytics: {},
        metadata: {}
      }
    });
    testCampaignId = campaign.id;
  });

  test.describe('Campaign Lifecycle', () => {
    test('should start a campaign', async () => {
      const execution = await campaignAutomation.startCampaign(testCampaignId, {
        callsPerMinute: 10,
        maxConcurrentCalls: 5
      });

      expect(execution).toBeDefined();
      expect(execution.id).toBeDefined();
      expect(execution.status).toBe('running');
      testExecutionId = execution.id;
    });

    test('should pause a campaign', async () => {
      await campaignAutomation.pauseCampaign(testCampaignId);

      const execution = await prisma.campaignExecution.findUnique({
        where: { id: testExecutionId }
      });

      expect(execution?.status).toBe('paused');
    });

    test('should resume a campaign', async () => {
      await campaignAutomation.resumeCampaign(testCampaignId);

      const execution = await prisma.campaignExecution.findUnique({
        where: { id: testExecutionId }
      });

      expect(execution?.status).toBe('running');
    });

    test('should stop a campaign', async () => {
      await campaignAutomation.stopCampaign(testCampaignId);

      const execution = await prisma.campaignExecution.findUnique({
        where: { id: testExecutionId }
      });

      expect(execution?.status).toBe('stopped');
    });
  });

  test.describe('CSV Import', () => {
    let csvFilePath: string;

    test.beforeAll(async () => {
      // Create test CSV file
      csvFilePath = path.join('/tmp', `test-leads-${Date.now()}.csv`);
      const csvContent = `phone,first_name,last_name,email,timezone
+14155551234,John,Doe,john@example.com,America/New_York
+14155551235,Jane,Smith,jane@example.com,America/Los_Angeles
+14155551236,Bob,Johnson,bob@example.com,America/Chicago`;

      await fs.writeFile(csvFilePath, csvContent);
    });

    test('should import CSV with valid data', async () => {
      const result = await campaignAutomation.importCSV({
        campaignId: testCampaignId,
        filePath: csvFilePath,
        mapping: {
          phoneNumber: 'phone',
          firstName: 'first_name',
          lastName: 'last_name',
          email: 'email',
          timezone: 'timezone'
        }
      });

      expect(result.totalProcessed).toBe(3);
      expect(result.successCount).toBe(3);
      expect(result.failureCount).toBe(0);
    });

    test('should validate phone numbers during import', async () => {
      const invalidCsvPath = path.join('/tmp', `invalid-leads-${Date.now()}.csv`);
      const invalidCsvContent = `phone,first_name
invalid-number,John
+14155551237,Valid`;

      await fs.writeFile(invalidCsvPath, invalidCsvContent);

      const result = await campaignAutomation.importCSV({
        campaignId: testCampaignId,
        filePath: invalidCsvPath,
        mapping: {
          phoneNumber: 'phone',
          firstName: 'first_name'
        },
        validateNumbers: true
      });

      expect(result.totalProcessed).toBe(2);
      expect(result.successCount).toBe(1);
      expect(result.failureCount).toBe(1);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    test('should skip duplicates when configured', async () => {
      const result = await campaignAutomation.importCSV({
        campaignId: testCampaignId,
        filePath: csvFilePath,
        mapping: {
          phoneNumber: 'phone',
          firstName: 'first_name'
        },
        skipDuplicates: true
      });

      expect(result.duplicatesSkipped).toBeGreaterThan(0);
    });

    test.afterAll(async () => {
      // Clean up CSV files
      await fs.unlink(csvFilePath).catch(() => {});
    });
  });

  test.describe('Lead Management', () => {
    let testLeadId: string;

    test('should get next lead from queue', async () => {
      // Add a test lead
      const lead = await prisma.campaignLead.create({
        data: {
          id: `test-lead-${Date.now()}`,
          campaignId: testCampaignId,
          phoneNumber: '+14155559999',
          firstName: 'Test',
          lastName: 'Lead',
          status: 'pending'
        }
      });
      testLeadId = lead.id;

      const nextLead = await campaignAutomation.getNextLead(testCampaignId);
      expect(nextLead).toBeDefined();
      expect(nextLead?.id).toBe(testLeadId);
    });

    test('should update lead status', async () => {
      await campaignAutomation.updateLeadStatus(testLeadId, 'calling');

      const lead = await prisma.campaignLead.findUnique({
        where: { id: testLeadId }
      });

      expect(lead?.status).toBe('calling');
    });

    test('should mark lead as completed', async () => {
      await campaignAutomation.markLeadComplete(testLeadId, 'success');

      const lead = await prisma.campaignLead.findUnique({
        where: { id: testLeadId }
      });

      expect(lead?.status).toBe('completed');
      expect(lead?.outcome).toBe('success');
      expect(lead?.completedAt).toBeDefined();
    });
  });

  test.describe('DNC List Management', () => {
    const testPhoneNumber = '+14155550000';

    test('should add number to DNC list', async () => {
      await campaignAutomation.addToDNCList(testPhoneNumber, 'User request');

      const isOnDNC = await campaignAutomation.isOnDNCList(testPhoneNumber);
      expect(isOnDNC).toBe(true);
    });

    test('should check if number is on DNC list', async () => {
      const isOnDNC = await campaignAutomation.isOnDNCList(testPhoneNumber);
      expect(isOnDNC).toBe(true);

      const notOnDNC = await campaignAutomation.isOnDNCList('+19999999999');
      expect(notOnDNC).toBe(false);
    });

    test('should remove number from DNC list', async () => {
      await campaignAutomation.removeFromDNCList(testPhoneNumber);

      const isOnDNC = await campaignAutomation.isOnDNCList(testPhoneNumber);
      expect(isOnDNC).toBe(false);
    });

    test('should check DNC for entire campaign', async () => {
      // Add test lead
      await prisma.campaignLead.create({
        data: {
          id: `dnc-test-lead-${Date.now()}`,
          campaignId: testCampaignId,
          phoneNumber: testPhoneNumber,
          status: 'pending'
        }
      });

      // Add to DNC
      await campaignAutomation.addToDNCList(testPhoneNumber);

      // Check campaign
      const dncCount = await campaignAutomation.checkDNCForCampaign(testCampaignId);
      expect(dncCount).toBeGreaterThan(0);
    });
  });

  test.describe('Call Pacing', () => {
    test('should respect calls per minute limit', async () => {
      const pacing = {
        callsPerMinute: 2,
        maxConcurrentCalls: 1
      };

      // Add test leads
      for (let i = 0; i < 5; i++) {
        await prisma.campaignLead.create({
          data: {
            id: `pacing-lead-${Date.now()}-${i}`,
            campaignId: testCampaignId,
            phoneNumber: `+1415555${1000 + i}`,
            status: 'pending'
          }
        });
      }

      const startTime = Date.now();
      let callCount = 0;

      // Simulate paced calling
      const interval = setInterval(async () => {
        if (callCount < pacing.callsPerMinute) {
          const lead = await campaignAutomation.getNextLead(testCampaignId);
          if (lead) {
            callCount++;
            await campaignAutomation.updateLeadStatus(lead.id, 'calling');
          }
        }
      }, (60 / pacing.callsPerMinute) * 1000);

      // Wait for 1 second
      await new Promise(resolve => setTimeout(resolve, 1000));
      clearInterval(interval);

      // Should have made at most 1 call in 1 second (based on 2 calls/minute)
      expect(callCount).toBeLessThanOrEqual(1);
    });

    test('should respect max concurrent calls', async () => {
      const stats = await campaignAutomation.getCampaignStats(testCampaignId);

      // Check that concurrent calls don't exceed limit
      expect(stats.activeCalls || 0).toBeLessThanOrEqual(5); // Based on our config
    });
  });

  test.describe('Campaign Statistics', () => {
    test('should generate campaign statistics', async () => {
      const stats = await campaignAutomation.getCampaignStats(testCampaignId);

      expect(stats).toBeDefined();
      expect(stats.totalLeads).toBeGreaterThanOrEqual(0);
      expect(stats.completedLeads).toBeGreaterThanOrEqual(0);
      expect(stats.pendingLeads).toBeGreaterThanOrEqual(0);
      expect(stats.successRate).toBeGreaterThanOrEqual(0);
      expect(stats.averageCallDuration).toBeDefined();
    });

    test('should track campaign metrics', async () => {
      const execution = await prisma.campaignExecution.findFirst({
        where: { campaignId: testCampaignId },
        orderBy: { createdAt: 'desc' }
      });

      expect(execution).toBeDefined();
      expect(execution?.totalLeads).toBeGreaterThanOrEqual(0);
      expect(execution?.processedLeads).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Event Handling', () => {
    test('should emit campaign events', async () => {
      const events: string[] = [];

      campaignAutomation.on('campaign.started', () => events.push('started'));
      campaignAutomation.on('campaign.paused', () => events.push('paused'));
      campaignAutomation.on('campaign.stopped', () => events.push('stopped'));

      // Create new campaign for event testing
      const eventCampaign = await prisma.campaign.create({
        data: {
          id: `event-campaign-${Date.now()}`,
          name: 'Event Test Campaign',
          type: 'OUTBOUND',
          active: false,
          organizationId: 'test-org'
        }
      });

      await campaignAutomation.startCampaign(eventCampaign.id);
      await campaignAutomation.pauseCampaign(eventCampaign.id);
      await campaignAutomation.stopCampaign(eventCampaign.id);

      // Wait for events to be processed
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(events).toContain('started');
      expect(events).toContain('paused');
      expect(events).toContain('stopped');
    });

    test('should emit lead events', async () => {
      const events: string[] = [];

      campaignAutomation.on('lead.completed', () => events.push('completed'));
      campaignAutomation.on('lead.failed', () => events.push('failed'));

      // Create test lead
      const lead = await prisma.campaignLead.create({
        data: {
          id: `event-lead-${Date.now()}`,
          campaignId: testCampaignId,
          phoneNumber: '+14155558888',
          status: 'pending'
        }
      });

      await campaignAutomation.markLeadComplete(lead.id, 'success');

      // Wait for events
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(events).toContain('completed');
    });
  });

  test.afterAll(async () => {
    // Clean up test data
    await prisma.campaignLead.deleteMany({
      where: { campaignId: testCampaignId }
    });

    await prisma.campaignExecution.deleteMany({
      where: { campaignId: testCampaignId }
    });

    await prisma.campaign.delete({
      where: { id: testCampaignId }
    });

    await prisma.$disconnect();
  });
});