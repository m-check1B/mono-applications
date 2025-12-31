import { describe, it, expect, beforeEach, beforeAll, afterAll, vi } from 'vitest';
import { PrismaClient, UserRole, CallStatus, CallDirection, TelephonyProvider, ContactStatus } from '@prisma/client';
import { testDb, createTestUser, createTestCampaign, createTestCall, measurePerformance } from '../setup';

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Call Lifecycle Integration Tests', () => {
  let testOrganization: any;
  let agentUser: any;
  let supervisorUser: any;
  let testCampaign: any;
  let testContact: any;

  beforeEach(async () => {
    // Create test organization
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-call-lifecycle',
        name: 'Test Call Lifecycle Organization',
        domain: 'call-test.local',
        settings: {
          timezone: 'UTC',
          recordingEnabled: true,
          transcriptionEnabled: true
        }
      }
    });

    // Create test users
    agentUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'agent@call-test.local',
      status: 'AVAILABLE'
    });

    supervisorUser = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.SUPERVISOR,
      email: 'supervisor@call-test.local'
    });

    // Create test campaign
    testCampaign = await createTestCampaign({
      organizationId: testOrganization.id,
      name: 'Call Lifecycle Test Campaign',
      active: true
    });

    // Create test contact
    testContact = await testDb.contact.create({
      data: {
        campaignId: testCampaign.id,
        phoneNumber: '+1234567890',
        name: 'Test Contact',
        email: 'contact@test.com',
        status: ContactStatus.PENDING
      }
    });
  });

  describe('Call Initiation', () => {
    it('should create outbound call with all required fields', async () => {
      const callData = {
        providerCallId: 'twilio-call-sid-123',
        fromNumber: '+1800555000',
        toNumber: testContact.phoneNumber,
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: testOrganization.id,
        agentId: agentUser.id,
        campaignId: testCampaign.id,
        contactId: testContact.id,
        status: CallStatus.QUEUED,
        metadata: {
          callType: 'sales',
          priority: 'high',
          expectedDuration: 300
        }
      };

      const call = await testDb.call.create({ data: callData });

      expect(call).toBeDefined();
      expect(call.id).toBeDefined();
      expect(call.providerCallId).toBe(callData.providerCallId);
      expect(call.fromNumber).toBe(callData.fromNumber);
      expect(call.toNumber).toBe(callData.toNumber);
      expect(call.direction).toBe(CallDirection.OUTBOUND);
      expect(call.provider).toBe(TelephonyProvider.TWILIO);
      expect(call.status).toBe(CallStatus.QUEUED);
      expect(call.organizationId).toBe(testOrganization.id);
      expect(call.agentId).toBe(agentUser.id);
      expect(call.campaignId).toBe(testCampaign.id);
      expect(call.contactId).toBe(testContact.id);
      expect(call.startTime).toBeDefined();
      expect(call.endTime).toBeNull();
      expect(call.duration).toBeNull();
      expect(call.metadata).toEqual(callData.metadata);
      expect(call.createdAt).toBeDefined();
    });

    it('should create inbound call without campaign or contact', async () => {
      const callData = {
        providerCallId: 'twilio-inbound-456',
        fromNumber: '+1987654321',
        toNumber: '+1800555000',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: testOrganization.id,
        status: CallStatus.RINGING,
        metadata: {
          callType: 'support',
          source: 'direct_dial'
        }
      };

      const call = await testDb.call.create({ data: callData });

      expect(call.direction).toBe(CallDirection.INBOUND);
      expect(call.status).toBe(CallStatus.RINGING);
      expect(call.campaignId).toBeNull();
      expect(call.contactId).toBeNull();
      expect(call.agentId).toBeNull(); // Will be assigned when answered
    });

    it('should validate required fields', async () => {
      // Test missing required fields
      await expect(
        testDb.call.create({
          data: {
            // Missing fromNumber, toNumber, direction, provider, organizationId
            status: CallStatus.QUEUED
          } as any
        })
      ).rejects.toThrow();
    });
  });

  describe('Call Status Transitions', () => {
    let testCall: any;

    beforeEach(async () => {
      testCall = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agentUser.id,
        campaignId: testCampaign.id,
        contactId: testContact.id,
        status: CallStatus.QUEUED,
        direction: CallDirection.OUTBOUND,
        fromNumber: '+1800555000',
        toNumber: testContact.phoneNumber
      });
    });

    it('should transition from QUEUED to RINGING', async () => {
      const updatedCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.RINGING,
          metadata: {
            ...(testCall.metadata as any),
            statusHistory: [
              { status: 'QUEUED', timestamp: testCall.createdAt },
              { status: 'RINGING', timestamp: new Date() }
            ]
          }
        }
      });

      expect(updatedCall.status).toBe(CallStatus.RINGING);
      expect((updatedCall.metadata as any).statusHistory).toHaveLength(2);
    });

    it('should transition from RINGING to IN_PROGRESS when answered', async () => {
      const answeredTime = new Date();
      
      const updatedCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.IN_PROGRESS,
          startTime: answeredTime,
          metadata: {
            ...(testCall.metadata as any),
            answeredAt: answeredTime,
            callConnected: true
          }
        }
      });

      expect(updatedCall.status).toBe(CallStatus.IN_PROGRESS);
      expect(updatedCall.startTime).toEqual(answeredTime);
      expect((updatedCall.metadata as any).callConnected).toBe(true);
    });

    it('should handle call completion with duration calculation', async () => {
      const startTime = new Date(Date.now() - 300000); // 5 minutes ago
      const endTime = new Date();
      const duration = Math.floor((endTime.getTime() - startTime.getTime()) / 1000);

      const completedCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.COMPLETED,
          startTime,
          endTime,
          duration,
          disposition: 'successful',
          notes: 'Call completed successfully. Customer was satisfied.',
          metadata: {
            ...(testCall.metadata as any),
            completionReason: 'natural_end',
            customerSatisfaction: 5,
            callQuality: 'excellent'
          }
        }
      });

      expect(completedCall.status).toBe(CallStatus.COMPLETED);
      expect(completedCall.endTime).toEqual(endTime);
      expect(completedCall.duration).toBe(duration);
      expect(completedCall.disposition).toBe('successful');
      expect(completedCall.notes).toBeDefined();
      expect((completedCall.metadata as any).customerSatisfaction).toBe(5);
    });

    it('should handle call failures and missed calls', async () => {
      // Test NO_ANSWER status
      const noAnswerCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.NO_ANSWER,
          endTime: new Date(),
          disposition: 'no_answer',
          metadata: {
            ...(testCall.metadata as any),
            ringDuration: 30,
            attempts: 1
          }
        }
      });

      expect(noAnswerCall.status).toBe(CallStatus.NO_ANSWER);
      expect(noAnswerCall.disposition).toBe('no_answer');

      // Create another call for BUSY test
      const busyCall = await createTestCall({
        organizationId: testOrganization.id,
        status: CallStatus.BUSY,
        disposition: 'busy_signal',
        endTime: new Date()
      });

      expect(busyCall.status).toBe(CallStatus.BUSY);

      // Create another call for FAILED test
      const failedCall = await createTestCall({
        organizationId: testOrganization.id,
        status: CallStatus.FAILED,
        disposition: 'network_error',
        endTime: new Date(),
        notes: 'Call failed due to network connectivity issues'
      });

      expect(failedCall.status).toBe(CallStatus.FAILED);
      expect(failedCall.notes).toContain('network connectivity');
    });

    it('should handle call transfers and holds', async () => {
      // Put call on hold
      const heldCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.ON_HOLD,
          metadata: {
            ...(testCall.metadata as any),
            holdReason: 'customer_request',
            holdStartTime: new Date()
          }
        }
      });

      expect(heldCall.status).toBe(CallStatus.ON_HOLD);
      expect((heldCall.metadata as any).holdReason).toBe('customer_request');

      // Resume call
      const resumedCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          status: CallStatus.IN_PROGRESS,
          metadata: {
            ...(heldCall.metadata as any),
            holdEndTime: new Date(),
            totalHoldTime: 60 // seconds
          }
        }
      });

      expect(resumedCall.status).toBe(CallStatus.IN_PROGRESS);

      // Transfer call to supervisor
      const transferredCall = await testDb.call.update({
        where: { id: testCall.id },
        data: {
          supervisorId: supervisorUser.id,
          metadata: {
            ...(resumedCall.metadata as any),
            transferReason: 'escalation',
            originalAgent: agentUser.id,
            transferTime: new Date()
          }
        }
      });

      expect(transferredCall.supervisorId).toBe(supervisorUser.id);
      expect((transferredCall.metadata as any).transferReason).toBe('escalation');
    });
  });

  describe('Call Transcription and Recording', () => {
    let activeCall: any;

    beforeEach(async () => {
      activeCall = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agentUser.id,
        status: CallStatus.IN_PROGRESS,
        recordingUrl: 'https://api.twilio.com/recordings/test-recording-sid'
      });
    });

    it('should create call transcripts in real-time', async () => {
      const transcripts = [
        {
          callId: activeCall.id,
          role: 'USER',
          content: 'Hello, I need help with my account',
          confidence: 0.95,
          speakerId: 'customer',
          timestamp: new Date(Date.now() - 5000)
        },
        {
          callId: activeCall.id,
          role: 'ASSISTANT',
          content: 'Hello! I\'d be happy to help you with your account. May I have your account number?',
          confidence: 0.98,
          speakerId: 'agent',
          timestamp: new Date(Date.now() - 3000)
        },
        {
          callId: activeCall.id,
          role: 'USER',
          content: 'Yes, it\'s 123456789',
          confidence: 0.92,
          speakerId: 'customer',
          timestamp: new Date()
        }
      ];

      // Create transcripts
      const createdTranscripts = await testDb.callTranscript.createMany({
        data: transcripts
      });

      expect(createdTranscripts.count).toBe(3);

      // Verify transcripts are correctly ordered
      const retrievedTranscripts = await testDb.callTranscript.findMany({
        where: { callId: activeCall.id },
        orderBy: { timestamp: 'asc' }
      });

      expect(retrievedTranscripts).toHaveLength(3);
      expect(retrievedTranscripts[0].role).toBe('USER');
      expect(retrievedTranscripts[1].role).toBe('ASSISTANT');
      expect(retrievedTranscripts[2].role).toBe('USER');
      expect(retrievedTranscripts[0].confidence).toBe(0.95);
      expect(retrievedTranscripts[1].confidence).toBe(0.98);
      expect(retrievedTranscripts[2].confidence).toBe(0.92);
    });

    it('should handle recording creation and management', async () => {
      const recording = await testDb.recording.create({
        data: {
          twilioRecordingSid: 'RE123456789',
          url: 'https://api.twilio.com/recordings/RE123456789.mp3',
          duration: 300, // 5 minutes
          callId: activeCall.id,
          status: 'completed'
        }
      });

      expect(recording).toBeDefined();
      expect(recording.twilioRecordingSid).toBe('RE123456789');
      expect(recording.duration).toBe(300);
      expect(recording.status).toBe('completed');

      // Create transcription from recording
      const transcription = await testDb.transcription.create({
        data: {
          twilioTranscriptionSid: 'TR123456789',
          text: 'This is the full transcription of the call...',
          recordingId: recording.id,
          callId: activeCall.id
        }
      });

      expect(transcription).toBeDefined();
      expect(transcription.text).toContain('full transcription');
      expect(transcription.recordingId).toBe(recording.id);

      // Verify relationship
      const recordingWithTranscription = await testDb.recording.findUnique({
        where: { id: recording.id },
        include: { transcriptions: true }
      });

      expect(recordingWithTranscription?.transcriptions).toHaveLength(1);
      expect(recordingWithTranscription?.transcriptions[0].id).toBe(transcription.id);
    });

    it('should handle transcript search and analysis', async () => {
      // Create multiple calls with transcripts for search testing
      const calls = await Promise.all([
        createTestCall({ organizationId: testOrganization.id }),
        createTestCall({ organizationId: testOrganization.id }),
        createTestCall({ organizationId: testOrganization.id })
      ]);

      // Create transcripts with different content
      const transcriptData = [
        { callId: calls[0].id, role: 'USER', content: 'I want to cancel my subscription', confidence: 0.95 },
        { callId: calls[0].id, role: 'ASSISTANT', content: 'I can help you with cancellation', confidence: 0.98 },
        { callId: calls[1].id, role: 'USER', content: 'I need technical support for login issues', confidence: 0.93 },
        { callId: calls[1].id, role: 'ASSISTANT', content: 'Let me help you troubleshoot login problems', confidence: 0.97 },
        { callId: calls[2].id, role: 'USER', content: 'I want to upgrade my plan', confidence: 0.96 },
        { callId: calls[2].id, role: 'ASSISTANT', content: 'I\'d be happy to help with plan upgrades', confidence: 0.99 }
      ];

      await testDb.callTranscript.createMany({ data: transcriptData });

      // Search for cancellation-related transcripts
      const cancellationTranscripts = await testDb.callTranscript.findMany({
        where: {
          content: {
            contains: 'cancel',
            mode: 'insensitive'
          }
        },
        include: {
          call: {
            select: { id: true, organizationId: true }
          }
        }
      });

      expect(cancellationTranscripts.length).toBeGreaterThan(0);
      expect(cancellationTranscripts[0].content).toContain('cancel');

      // Search for technical support transcripts
      const supportTranscripts = await testDb.callTranscript.findMany({
        where: {
          content: {
            contains: 'technical support',
            mode: 'insensitive'
          }
        }
      });

      expect(supportTranscripts.length).toBeGreaterThan(0);
      expect(supportTranscripts[0].content).toContain('technical support');

      // Analyze transcript confidence scores
      const avgConfidence = await testDb.callTranscript.aggregate({
        where: {
          call: {
            organizationId: testOrganization.id
          }
        },
        _avg: {
          confidence: true
        },
        _min: {
          confidence: true
        },
        _max: {
          confidence: true
        }
      });

      expect(avgConfidence._avg.confidence).toBeGreaterThan(0.9);
      expect(avgConfidence._min.confidence).toBeGreaterThan(0.9);
      expect(avgConfidence._max.confidence).toBeLessThanOrEqual(1.0);
    });
  });

  describe('Call Analytics and Metrics', () => {
    beforeEach(async () => {
      // Create a variety of calls for analytics testing
      const callsData = [
        // Completed successful calls
        { status: CallStatus.COMPLETED, duration: 120, disposition: 'successful', agentId: agentUser.id },
        { status: CallStatus.COMPLETED, duration: 180, disposition: 'successful', agentId: agentUser.id },
        { status: CallStatus.COMPLETED, duration: 300, disposition: 'successful', agentId: agentUser.id },
        
        // Completed calls with issues
        { status: CallStatus.COMPLETED, duration: 60, disposition: 'complaint', agentId: agentUser.id },
        { status: CallStatus.COMPLETED, duration: 90, disposition: 'escalated', agentId: agentUser.id },
        
        // Failed/missed calls
        { status: CallStatus.NO_ANSWER, duration: null, disposition: 'no_answer' },
        { status: CallStatus.BUSY, duration: null, disposition: 'busy' },
        { status: CallStatus.FAILED, duration: null, disposition: 'network_error' },
        
        // Active calls
        { status: CallStatus.IN_PROGRESS, duration: null, agentId: agentUser.id },
        { status: CallStatus.IN_PROGRESS, duration: null, agentId: supervisorUser.id }
      ];

      await Promise.all(callsData.map(callData => 
        createTestCall({
          organizationId: testOrganization.id,
          campaignId: testCampaign.id,
          ...callData
        })
      ));
    });

    it('should calculate call statistics correctly', async () => {
      // Get call statistics
      const callStats = await testDb.call.groupBy({
        by: ['status'],
        where: { organizationId: testOrganization.id },
        _count: { id: true },
        _avg: { duration: true }
      });

      const completedStats = callStats.find(stat => stat.status === CallStatus.COMPLETED);
      const inProgressStats = callStats.find(stat => stat.status === CallStatus.IN_PROGRESS);
      const noAnswerStats = callStats.find(stat => stat.status === CallStatus.NO_ANSWER);

      expect(completedStats?._count.id).toBe(5);
      expect(inProgressStats?._count.id).toBe(2);
      expect(noAnswerStats?._count.id).toBe(1);
      expect(completedStats?._avg.duration).toBeGreaterThan(100);
    });

    it('should track agent performance metrics', async () => {
      const agentStats = await testDb.call.groupBy({
        by: ['agentId'],
        where: {
          organizationId: testOrganization.id,
          agentId: { not: null }
        },
        _count: { id: true },
        _avg: { duration: true }
      });

      const agentPerformance = agentStats.find(stat => stat.agentId === agentUser.id);
      expect(agentPerformance?._count.id).toBeGreaterThan(0);
      expect(agentPerformance?._avg.duration).toBeGreaterThan(0);
    });

    it('should analyze call dispositions', async () => {
      const dispositionStats = await testDb.call.groupBy({
        by: ['disposition'],
        where: {
          organizationId: testOrganization.id,
          disposition: { not: null }
        },
        _count: { id: true }
      });

      const successfulCalls = dispositionStats.find(stat => stat.disposition === 'successful')?._count.id || 0;
      const totalCalls = dispositionStats.reduce((sum, stat) => sum + stat._count.id, 0);
      const successRate = successfulCalls / totalCalls;

      expect(successRate).toBeGreaterThan(0);
      expect(successRate).toBeLessThanOrEqual(1);
    });

    it('should calculate average handle time by campaign', async () => {
      const campaignStats = await testDb.call.aggregate({
        where: {
          organizationId: testOrganization.id,
          campaignId: testCampaign.id,
          status: CallStatus.COMPLETED
        },
        _avg: { duration: true },
        _count: { id: true },
        _sum: { duration: true }
      });

      expect(campaignStats._count.id).toBeGreaterThan(0);
      expect(campaignStats._avg.duration).toBeGreaterThan(0);
      expect(campaignStats._sum.duration).toBeGreaterThan(0);
    });
  });

  describe('Contact Integration', () => {
    it('should update contact status based on call outcomes', async () => {
      // Create call for the contact
      const call = await createTestCall({
        organizationId: testOrganization.id,
        contactId: testContact.id,
        campaignId: testCampaign.id,
        status: CallStatus.COMPLETED,
        disposition: 'successful',
        duration: 180
      });

      // Update contact status based on call outcome
      await testDb.contact.update({
        where: { id: testContact.id },
        data: {
          status: ContactStatus.COMPLETED,
          outcome: 'sale_made',
          notes: 'Customer purchased premium package',
          attempts: 1,
          lastAttempt: new Date()
        }
      });

      const updatedContact = await testDb.contact.findUnique({
        where: { id: testContact.id },
        include: { calls: true }
      });

      expect(updatedContact?.status).toBe(ContactStatus.COMPLETED);
      expect(updatedContact?.outcome).toBe('sale_made');
      expect(updatedContact?.attempts).toBe(1);
      expect(updatedContact?.calls).toHaveLength(1);
      expect(updatedContact?.calls[0].id).toBe(call.id);
    });

    it('should handle callback scheduling', async () => {
      // Customer requests callback
      const callbackTime = new Date(Date.now() + 24 * 60 * 60 * 1000); // Tomorrow
      
      await testDb.contact.update({
        where: { id: testContact.id },
        data: {
          status: ContactStatus.SCHEDULED,
          nextAttempt: callbackTime,
          notes: 'Customer requested callback tomorrow at 2 PM',
          metadata: {
            callbackRequested: true,
            preferredTime: '14:00',
            timezone: 'UTC'
          }
        }
      });

      const scheduledContact = await testDb.contact.findUnique({
        where: { id: testContact.id }
      });

      expect(scheduledContact?.status).toBe(ContactStatus.SCHEDULED);
      expect(scheduledContact?.nextAttempt).toEqual(callbackTime);
      expect((scheduledContact?.metadata as any)?.callbackRequested).toBe(true);
    });

    it('should track contact attempt history', async () => {
      const attempts = [
        { status: CallStatus.NO_ANSWER, disposition: 'no_answer', attempt: 1 },
        { status: CallStatus.BUSY, disposition: 'busy', attempt: 2 },
        { status: CallStatus.COMPLETED, disposition: 'successful', attempt: 3, duration: 150 }
      ];

      // Create calls for each attempt
      for (const attempt of attempts) {
        await createTestCall({
          organizationId: testOrganization.id,
          contactId: testContact.id,
          campaignId: testCampaign.id,
          status: attempt.status,
          disposition: attempt.disposition,
          duration: attempt.duration || null,
          metadata: { attemptNumber: attempt.attempt }
        });
      }

      // Update contact with final attempt count
      await testDb.contact.update({
        where: { id: testContact.id },
        data: {
          attempts: 3,
          status: ContactStatus.COMPLETED,
          lastAttempt: new Date()
        }
      });

      // Verify contact has all related calls
      const contactWithCalls = await testDb.contact.findUnique({
        where: { id: testContact.id },
        include: {
          calls: {
            orderBy: { createdAt: 'asc' }
          }
        }
      });

      expect(contactWithCalls?.calls).toHaveLength(3);
      expect(contactWithCalls?.attempts).toBe(3);
      expect(contactWithCalls?.calls[0].status).toBe(CallStatus.NO_ANSWER);
      expect(contactWithCalls?.calls[1].status).toBe(CallStatus.BUSY);
      expect(contactWithCalls?.calls[2].status).toBe(CallStatus.COMPLETED);
    });
  });

  describe('Performance and Optimization', () => {
    it('should efficiently query active calls', async () => {
      // Create multiple active calls
      await Promise.all(Array(20).fill(null).map((_, i) => 
        createTestCall({
          organizationId: testOrganization.id,
          agentId: i % 2 === 0 ? agentUser.id : supervisorUser.id,
          status: CallStatus.IN_PROGRESS,
          fromNumber: `+180055500${i}`,
          toNumber: `+198765432${i}`
        })
      ));

      const { duration } = await measurePerformance(async () => {
        return await testDb.call.findMany({
          where: {
            organizationId: testOrganization.id,
            status: CallStatus.IN_PROGRESS
          },
          include: {
            agent: {
              select: { id: true, firstName: true, lastName: true }
            },
            campaign: {
              select: { id: true, name: true }
            }
          },
          orderBy: { startTime: 'desc' }
        });
      });

      expect(duration).toBeLessThan(100); // Should be very fast with proper indexing
    });

    it('should handle bulk call status updates efficiently', async () => {
      // Create multiple calls in progress
      const calls = await Promise.all(Array(50).fill(null).map(() => 
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.IN_PROGRESS
        })
      ));

      const callIds = calls.map(call => call.id);
      
      const { duration } = await measurePerformance(async () => {
        await testDb.call.updateMany({
          where: {
            id: { in: callIds }
          },
          data: {
            status: CallStatus.COMPLETED,
            endTime: new Date(),
            duration: 120,
            disposition: 'bulk_completed'
          }
        });
      });

      expect(duration).toBeLessThan(1000); // Should complete within 1 second
      
      // Verify all calls were updated
      const updatedCalls = await testDb.call.findMany({
        where: { id: { in: callIds } }
      });
      
      expect(updatedCalls.every(call => call.status === CallStatus.COMPLETED)).toBe(true);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle orphaned calls gracefully', async () => {
      // Create call with non-existent agent
      await expect(
        testDb.call.create({
          data: {
            fromNumber: '+1234567890',
            toNumber: '+0987654321',
            direction: CallDirection.OUTBOUND,
            provider: TelephonyProvider.TWILIO,
            organizationId: testOrganization.id,
            agentId: 'non-existent-agent-id',
            status: CallStatus.QUEUED
          }
        })
      ).rejects.toThrow();
    });

    it('should handle concurrent call updates', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        status: CallStatus.RINGING
      });

      // Simulate concurrent updates
      const updates = [
        testDb.call.update({
          where: { id: call.id },
          data: { status: CallStatus.IN_PROGRESS }
        }),
        testDb.call.update({
          where: { id: call.id },
          data: { agentId: agentUser.id }
        })
      ];

      // Both should complete without error
      const results = await Promise.allSettled(updates);
      expect(results.every(result => result.status === 'fulfilled')).toBe(true);
    });

    it('should maintain data consistency during cascade deletes', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        contactId: testContact.id
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

      // Verify transcript is deleted
      const transcripts = await testDb.callTranscript.findMany({
        where: { callId: call.id }
      });
      expect(transcripts).toHaveLength(0);

      // Contact should still exist
      const contact = await testDb.contact.findUnique({
        where: { id: testContact.id }
      });
      expect(contact).toBeDefined();
    });
  });
});
