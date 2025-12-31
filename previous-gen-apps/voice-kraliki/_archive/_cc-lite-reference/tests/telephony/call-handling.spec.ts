import { describe, it, expect, beforeEach, vi } from 'vitest';
import { testDb, createTestUser, createTestCall, createTestCampaign, mockTwilioService, mockDeepgramService } from '../setup';
import { createToken } from '@unified/auth-core';
import twilio from 'twilio';

// Mock Twilio SDK
vi.mock('twilio', () => ({
  default: vi.fn(() => ({
    calls: {
      create: vi.fn(),
      get: vi.fn(),
      update: vi.fn(),
      remove: vi.fn()
    },
    conferences: {
      create: vi.fn(),
      get: vi.fn(),
      update: vi.fn()
    }
  }))
}));

describe('Call Handling Tests', () => {
  let testUser: any;
  let testSupervisor: any;
  let testCampaign: any;
  let twilioClient: any;

  beforeEach(async () => {
    // Clean database
    await testDb.call.deleteMany();
    await testDb.campaign.deleteMany();
    await testDb.user.deleteMany();
    await testDb.organization.deleteMany();

    // Create test users
    testUser = await createTestUser({ 
      role: 'AGENT',
      status: 'AVAILABLE',
      firstName: 'Agent',
      lastName: 'Smith'
    });
    
    testSupervisor = await createTestUser({ 
      role: 'SUPERVISOR',
      organizationId: testUser.organizationId,
      firstName: 'Super',
      lastName: 'Visor'
    });

    // Create test campaign
    testCampaign = await createTestCampaign({ 
      organizationId: testUser.organizationId,
      type: 'OUTBOUND',
      name: 'Test Campaign'
    });

    // Mock Twilio client
    twilioClient = twilio();
    vi.clearAllMocks();
  });

  describe('Inbound Call Handling', () => {
    it('should route inbound call to available agent', async () => {
      // Simulate inbound call webhook
      const inboundCallData = {
        From: '+1234567890',
        To: '+1987654321',
        CallSid: 'CA123456789',
        CallStatus: 'ringing'
      };

      // Mock call routing logic
      const routeInboundCall = async (callData: any) => {
        // Find available agent
        const availableAgent = await testDb.user.findFirst({
          where: { 
            status: 'AVAILABLE',
            role: 'AGENT',
            organizationId: testUser.organizationId
          }
        });

        if (!availableAgent) {
          throw new Error('No available agents');
        }

        // Create call record
        const call = await testDb.call.create({
          data: {
            phoneNumber: callData.From,
            direction: 'INBOUND',
            status: 'ASSIGNED',
            agentId: availableAgent.id,
            campaignId: testCampaign.id,
            providerCallId: callData.CallSid,
            startTime: new Date()
          }
        });

        // Update agent status
        await testDb.user.update({
          where: { id: availableAgent.id },
          data: { status: 'BUSY' }
        });

        return call;
      };

      const call = await routeInboundCall(inboundCallData);
      
      expect(call.phoneNumber).toBe('+1234567890');
      expect(call.direction).toBe('INBOUND');
      expect(call.agentId).toBe(testUser.id);
      expect(call.status).toBe('ASSIGNED');

      // Verify agent status updated
      const updatedAgent = await testDb.user.findUnique({ where: { id: testUser.id } });
      expect(updatedAgent?.status).toBe('BUSY');
    });

    it('should queue inbound call when no agents available', async () => {
      // Set all agents to busy
      await testDb.user.update({
        where: { id: testUser.id },
        data: { status: 'BUSY' }
      });

      const inboundCallData = {
        From: '+1234567890',
        To: '+1987654321',
        CallSid: 'CA123456789',
        CallStatus: 'ringing'
      };

      const queueInboundCall = async (callData: any) => {
        // Check for available agents
        const availableAgent = await testDb.user.findFirst({
          where: { 
            status: 'AVAILABLE',
            role: 'AGENT',
            organizationId: testUser.organizationId
          }
        });

        if (!availableAgent) {
          // Queue the call
          const call = await testDb.call.create({
            data: {
              phoneNumber: callData.From,
              direction: 'INBOUND',
              status: 'QUEUED',
              agentId: null, // Not assigned yet
              campaignId: testCampaign.id,
              providerCallId: callData.CallSid,
              startTime: new Date(),
              queuePosition: 1,
              estimatedWaitTime: 120 // 2 minutes
            }
          });

          return call;
        }

        throw new Error('Should be queued');
      };

      const queuedCall = await queueInboundCall(inboundCallData);
      
      expect(queuedCall.status).toBe('QUEUED');
      expect(queuedCall.agentId).toBeNull();
      expect(queuedCall.queuePosition).toBe(1);
    });

    it('should handle call priority routing', async () => {
      // Create VIP campaign
      const vipCampaign = await createTestCampaign({ 
        organizationId: testUser.organizationId,
        type: 'INBOUND',
        name: 'VIP Campaign',
        priority: 'HIGH'
      });

      // Create multiple calls
      const regularCall = await createTestCall({
        phoneNumber: '+1111111111',
        direction: 'INBOUND',
        status: 'QUEUED',
        campaignId: testCampaign.id,
        queuePosition: 1,
        priority: 'NORMAL'
      });

      const vipCall = await createTestCall({
        phoneNumber: '+2222222222',
        direction: 'INBOUND',
        status: 'QUEUED',
        campaignId: vipCampaign.id,
        queuePosition: 2,
        priority: 'HIGH'
      });

      // Route next call (should prioritize VIP)
      const routeNextCall = async () => {
        const nextCall = await testDb.call.findFirst({
          where: { status: 'QUEUED' },
          orderBy: [
            { priority: 'desc' }, // HIGH priority first
            { queuePosition: 'asc' }
          ]
        });

        if (nextCall) {
          await testDb.call.update({
            where: { id: nextCall.id },
            data: { 
              status: 'ASSIGNED',
              agentId: testUser.id
            }
          });
        }

        return nextCall;
      };

      const assignedCall = await routeNextCall();
      expect(assignedCall?.id).toBe(vipCall.id);
      expect(assignedCall?.priority).toBe('HIGH');
    });
  });

  describe('Outbound Call Handling', () => {
    it('should initiate outbound call successfully', async () => {
      const phoneNumber = '+1234567890';
      
      // Mock Twilio call creation
      twilioClient.calls.create.mockResolvedValue({
        sid: 'CA123456789',
        status: 'queued',
        from: '+1987654321',
        to: phoneNumber
      });

      const initiateOutboundCall = async (data: any) => {
        // Create call in Twilio
        const twilioCall = await twilioClient.calls.create({
          from: '+1987654321',
          to: data.phoneNumber,
          url: 'http://localhost:3001/webhooks/twilio/voice',
          statusCallback: 'http://localhost:3001/webhooks/twilio/status'
        });

        // Create call record
        const call = await testDb.call.create({
          data: {
            phoneNumber: data.phoneNumber,
            direction: 'OUTBOUND',
            status: 'DIALING',
            agentId: data.agentId,
            campaignId: data.campaignId,
            providerCallId: twilioCall.sid,
            startTime: new Date()
          }
        });

        return { call, twilioCall };
      };

      const result = await initiateOutboundCall({
        phoneNumber,
        agentId: testUser.id,
        campaignId: testCampaign.id
      });

      expect(twilioClient.calls.create).toHaveBeenCalledWith({
        from: '+1987654321',
        to: phoneNumber,
        url: 'http://localhost:3001/webhooks/twilio/voice',
        statusCallback: 'http://localhost:3001/webhooks/twilio/status'
      });

      expect(result.call.phoneNumber).toBe(phoneNumber);
      expect(result.call.direction).toBe('OUTBOUND');
      expect(result.call.status).toBe('DIALING');
      expect(result.twilioCall.sid).toBe('CA123456789');
    });

    it('should handle outbound call failure', async () => {
      const phoneNumber = 'invalid-number';
      
      // Mock Twilio error
      twilioClient.calls.create.mockRejectedValue(new Error('Invalid phone number'));

      const initiateOutboundCall = async (data: any) => {
        try {
          const twilioCall = await twilioClient.calls.create({
            from: '+1987654321',
            to: data.phoneNumber,
            url: 'http://localhost:3001/webhooks/twilio/voice'
          });
          
          // This shouldn't be reached
          return { success: true, twilioCall };
        } catch (error: any) {
          // Log failed call attempt
          await testDb.call.create({
            data: {
              phoneNumber: data.phoneNumber,
              direction: 'OUTBOUND',
              status: 'FAILED',
              agentId: data.agentId,
              campaignId: data.campaignId,
              failureReason: error.message,
              startTime: new Date(),
              endTime: new Date()
            }
          });
          
          throw error;
        }
      };

      await expect(initiateOutboundCall({
        phoneNumber,
        agentId: testUser.id,
        campaignId: testCampaign.id
      })).rejects.toThrow('Invalid phone number');

      // Verify failed call record
      const failedCall = await testDb.call.findFirst({
        where: { 
          phoneNumber,
          status: 'FAILED'
        }
      });
      expect(failedCall).toBeDefined();
      expect(failedCall?.failureReason).toBe('Invalid phone number');
    });
  });

  describe('Call Transfer', () => {
    it('should transfer call to another agent', async () => {
      const targetAgent = await createTestUser({ 
        role: 'AGENT',
        status: 'AVAILABLE',
        organizationId: testUser.organizationId
      });

      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789'
      });

      // Mock Twilio call update
      twilioClient.calls.get.mockReturnValue({
        update: vi.fn().mockResolvedValue({
          sid: 'CA123456789',
          status: 'in-progress'
        })
      });

      const transferCall = async (callId: string, targetAgentId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call || call.status !== 'ACTIVE') {
          throw new Error('Call not active or not found');
        }

        const targetAgent = await testDb.user.findUnique({ where: { id: targetAgentId } });
        if (!targetAgent || targetAgent.status !== 'AVAILABLE') {
          throw new Error('Target agent not available');
        }

        // Update call assignment
        const updatedCall = await testDb.call.update({
          where: { id: callId },
          data: {
            agentId: targetAgentId,
            transferredAt: new Date(),
            transferredFrom: call.agentId
          }
        });

        // Update agent statuses
        await testDb.user.update({
          where: { id: call.agentId },
          data: { status: 'AVAILABLE' }
        });

        await testDb.user.update({
          where: { id: targetAgentId },
          data: { status: 'BUSY' }
        });

        // Update Twilio call if needed
        if (call.providerCallId) {
          await twilioClient.calls(call.providerCallId).update({
            // Twilio-specific transfer logic would go here
          });
        }

        return updatedCall;
      };

      const transferredCall = await transferCall(activeCall.id, targetAgent.id);
      
      expect(transferredCall.agentId).toBe(targetAgent.id);
      expect(transferredCall.transferredFrom).toBe(testUser.id);
      expect(transferredCall.transferredAt).toBeDefined();

      // Verify agent status updates
      const originalAgent = await testDb.user.findUnique({ where: { id: testUser.id } });
      const newAgent = await testDb.user.findUnique({ where: { id: targetAgent.id } });
      
      expect(originalAgent?.status).toBe('AVAILABLE');
      expect(newAgent?.status).toBe('BUSY');
    });

    it('should handle warm transfer with conference', async () => {
      const targetAgent = await createTestUser({ 
        role: 'AGENT',
        status: 'AVAILABLE',
        organizationId: testUser.organizationId
      });

      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789'
      });

      // Mock Twilio conference creation
      twilioClient.conferences.create.mockResolvedValue({
        sid: 'CF123456789',
        status: 'in-progress',
        friendlyName: `transfer-${activeCall.id}`
      });

      const initiateWarmTransfer = async (callId: string, targetAgentId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call) throw new Error('Call not found');

        // Create conference for warm transfer
        const conference = await twilioClient.conferences.create({
          friendlyName: `transfer-${callId}`,
          statusCallback: 'http://localhost:3001/webhooks/twilio/conference'
        });

        // Update call with conference info
        const updatedCall = await testDb.call.update({
          where: { id: callId },
          data: {
            conferenceId: conference.sid,
            status: 'CONFERENCE',
            transferTargetAgent: targetAgentId
          }
        });

        return { call: updatedCall, conference };
      };

      const result = await initiateWarmTransfer(activeCall.id, targetAgent.id);
      
      expect(result.call.conferenceId).toBe('CF123456789');
      expect(result.call.status).toBe('CONFERENCE');
      expect(result.call.transferTargetAgent).toBe(targetAgent.id);
      expect(twilioClient.conferences.create).toHaveBeenCalled();
    });
  });

  describe('Call Controls', () => {
    it('should hold and unhold call', async () => {
      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789'
      });

      // Mock Twilio call update
      twilioClient.calls.get.mockReturnValue({
        update: vi.fn().mockResolvedValue({ status: 'in-progress' })
      });

      const holdCall = async (callId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call) throw new Error('Call not found');

        await testDb.call.update({
          where: { id: callId },
          data: { 
            status: 'ON_HOLD',
            holdStartTime: new Date()
          }
        });

        // Update Twilio call to play hold music
        if (call.providerCallId) {
          await twilioClient.calls(call.providerCallId).update({
            url: 'http://localhost:3001/twiml/hold-music'
          });
        }

        return true;
      };

      const unholdCall = async (callId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call) throw new Error('Call not found');

        const holdDuration = call.holdStartTime ? 
          Date.now() - new Date(call.holdStartTime).getTime() : 0;

        await testDb.call.update({
          where: { id: callId },
          data: { 
            status: 'ACTIVE',
            holdStartTime: null,
            totalHoldTime: (call.totalHoldTime || 0) + holdDuration
          }
        });

        return true;
      };

      // Test hold
      await holdCall(activeCall.id);
      const heldCall = await testDb.call.findUnique({ where: { id: activeCall.id } });
      expect(heldCall?.status).toBe('ON_HOLD');
      expect(heldCall?.holdStartTime).toBeDefined();

      // Test unhold
      await unholdCall(activeCall.id);
      const unheldCall = await testDb.call.findUnique({ where: { id: activeCall.id } });
      expect(unheldCall?.status).toBe('ACTIVE');
      expect(unheldCall?.holdStartTime).toBeNull();
      expect(unheldCall?.totalHoldTime).toBeGreaterThan(0);
    });

    it('should mute and unmute call', async () => {
      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789'
      });

      const muteCall = async (callId: string, muted: boolean) => {
        await testDb.call.update({
          where: { id: callId },
          data: { muted }
        });

        // In real implementation, would control agent's microphone
        // or Twilio call audio settings
        
        return true;
      };

      await muteCall(activeCall.id, true);
      const mutedCall = await testDb.call.findUnique({ where: { id: activeCall.id } });
      expect(mutedCall?.muted).toBe(true);

      await muteCall(activeCall.id, false);
      const unmutedCall = await testDb.call.findUnique({ where: { id: activeCall.id } });
      expect(unmutedCall?.muted).toBe(false);
    });

    it('should end call properly', async () => {
      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789',
        startTime: new Date(Date.now() - 300000) // 5 minutes ago
      });

      // Mock Twilio call update
      twilioClient.calls.get.mockReturnValue({
        update: vi.fn().mockResolvedValue({ status: 'completed' })
      });

      const endCall = async (callId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call) throw new Error('Call not found');

        const endTime = new Date();
        const duration = call.startTime ? 
          (endTime.getTime() - new Date(call.startTime).getTime()) / 1000 : 0;

        // Update call record
        const updatedCall = await testDb.call.update({
          where: { id: callId },
          data: {
            status: 'COMPLETED',
            endTime,
            duration: Math.round(duration)
          }
        });

        // Update agent status
        await testDb.user.update({
          where: { id: call.agentId! },
          data: { status: 'AVAILABLE' }
        });

        // End Twilio call
        if (call.providerCallId) {
          await twilioClient.calls(call.providerCallId).update({
            status: 'completed'
          });
        }

        return updatedCall;
      };

      const endedCall = await endCall(activeCall.id);
      
      expect(endedCall.status).toBe('COMPLETED');
      expect(endedCall.endTime).toBeDefined();
      expect(endedCall.duration).toBeGreaterThan(0);

      // Verify agent is available again
      const agent = await testDb.user.findUnique({ where: { id: testUser.id } });
      expect(agent?.status).toBe('AVAILABLE');
    });
  });

  describe('Call Recording', () => {
    it('should start and stop call recording', async () => {
      const activeCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'ACTIVE',
        providerCallId: 'CA123456789'
      });

      // Mock Twilio recording
      twilioClient.calls.get.mockReturnValue({
        recordings: {
          create: vi.fn().mockResolvedValue({
            sid: 'RE123456789',
            status: 'in-progress'
          }),
          list: vi.fn().mockResolvedValue([
            { sid: 'RE123456789', status: 'completed' }
          ])
        }
      });

      const startRecording = async (callId: string) => {
        const call = await testDb.call.findUnique({ where: { id: callId } });
        if (!call || !call.providerCallId) throw new Error('Call not found');

        const recording = await twilioClient.calls(call.providerCallId).recordings.create({
          recordingChannels: 'dual'
        });

        await testDb.call.update({
          where: { id: callId },
          data: {
            recordingId: recording.sid,
            recordingStarted: true
          }
        });

        return recording;
      };

      const recording = await startRecording(activeCall.id);
      
      expect(recording.sid).toBe('RE123456789');
      expect(recording.status).toBe('in-progress');

      const updatedCall = await testDb.call.findUnique({ where: { id: activeCall.id } });
      expect(updatedCall?.recordingId).toBe('RE123456789');
      expect(updatedCall?.recordingStarted).toBe(true);
    });
  });

  describe('Call Analytics', () => {
    it('should track call metrics', async () => {
      const completedCall = await createTestCall({
        agentId: testUser.id,
        campaignId: testCampaign.id,
        status: 'COMPLETED',
        startTime: new Date(Date.now() - 600000), // 10 minutes ago
        endTime: new Date(Date.now() - 300000), // 5 minutes ago
        duration: 300, // 5 minutes
        totalHoldTime: 30, // 30 seconds
        talkTime: 270 // 4.5 minutes
      });

      const getCallMetrics = async (agentId: string, dateRange: { start: Date, end: Date }) => {
        const calls = await testDb.call.findMany({
          where: {
            agentId,
            startTime: {
              gte: dateRange.start,
              lte: dateRange.end
            },
            status: 'COMPLETED'
          }
        });

        const totalCalls = calls.length;
        const totalDuration = calls.reduce((sum, call) => sum + (call.duration || 0), 0);
        const totalTalkTime = calls.reduce((sum, call) => sum + (call.talkTime || 0), 0);
        const totalHoldTime = calls.reduce((sum, call) => sum + (call.totalHoldTime || 0), 0);
        const averageDuration = totalCalls > 0 ? totalDuration / totalCalls : 0;

        return {
          totalCalls,
          totalDuration,
          totalTalkTime,
          totalHoldTime,
          averageDuration,
          talkTimeRatio: totalDuration > 0 ? totalTalkTime / totalDuration : 0
        };
      };

      const metrics = await getCallMetrics(testUser.id, {
        start: new Date(Date.now() - 24 * 60 * 60 * 1000), // Last 24 hours
        end: new Date()
      });

      expect(metrics.totalCalls).toBe(1);
      expect(metrics.totalDuration).toBe(300);
      expect(metrics.totalTalkTime).toBe(270);
      expect(metrics.totalHoldTime).toBe(30);
      expect(metrics.averageDuration).toBe(300);
      expect(metrics.talkTimeRatio).toBeCloseTo(0.9, 1); // 90% talk time
    });
  });
});
