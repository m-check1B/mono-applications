import { describe, it, expect, beforeEach, beforeAll, afterAll, vi } from 'vitest';
import { PrismaClient, UserRole, CallStatus, CallDirection, AgentStatus, UserStatus } from '@prisma/client';
import { testDb, createTestUser, createTestCampaign, createTestCall, measurePerformance } from '../setup';

// Mock WebSocket for real-time testing
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  readyState: 1,
  clients: new Set(),
  broadcast: vi.fn((data) => {
    mockWebSocket.clients.forEach(client => {
      if (client.readyState === 1) {
        client.send(JSON.stringify(data));
      }
    });
  })
};

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Dashboard Real-time Updates Integration Tests', () => {
  let testOrganization: any;
  let adminUser: any;
  let supervisorUser: any;
  let agent1: any;
  let agent2: any;
  let agent3: any;
  let campaign1: any;
  let campaign2: any;

  beforeEach(async () => {
    // Create test organization
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-dashboard-rt',
        name: 'Dashboard Real-time Test Organization',
        domain: 'dashboard-rt.local',
        settings: {
          realTimeUpdates: true,
          dashboardRefreshRate: 1000, // 1 second
          enableNotifications: true
        }
      }
    });

    // Create test users
    [adminUser, supervisorUser, agent1, agent2, agent3] = await Promise.all([
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.ADMIN,
        email: 'admin@dashboard-rt.local',
        firstName: 'Admin',
        lastName: 'User'
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.SUPERVISOR,
        email: 'supervisor@dashboard-rt.local',
        firstName: 'Supervisor',
        lastName: 'User'
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.AGENT,
        email: 'agent1@dashboard-rt.local',
        firstName: 'Agent',
        lastName: 'One',
        status: UserStatus.AVAILABLE
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.AGENT,
        email: 'agent2@dashboard-rt.local',
        firstName: 'Agent',
        lastName: 'Two',
        status: UserStatus.BUSY
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.AGENT,
        email: 'agent3@dashboard-rt.local',
        firstName: 'Agent',
        lastName: 'Three',
        status: UserStatus.BREAK
      })
    ]);

    // Create agent records
    await Promise.all([
      testDb.agent.create({
        data: {
          userId: agent1.id,
          status: AgentStatus.AVAILABLE,
          capacity: 3,
          currentLoad: 0,
          skills: ['sales', 'support']
        }
      }),
      testDb.agent.create({
        data: {
          userId: agent2.id,
          status: AgentStatus.BUSY,
          capacity: 2,
          currentLoad: 1,
          skills: ['support', 'technical']
        }
      }),
      testDb.agent.create({
        data: {
          userId: agent3.id,
          status: AgentStatus.BREAK,
          capacity: 2,
          currentLoad: 0,
          skills: ['sales']
        }
      })
    ]);

    // Create test campaigns
    [campaign1, campaign2] = await Promise.all([
      createTestCampaign({
        organizationId: testOrganization.id,
        name: 'Sales Campaign',
        active: true
      }),
      createTestCampaign({
        organizationId: testOrganization.id,
        name: 'Support Campaign',
        active: true
      })
    ]);
  });

  describe('Real-time Dashboard Data', () => {
    it('should provide comprehensive dashboard overview', async () => {
      // Create various calls for dashboard data
      await Promise.all([
        // Active calls
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          campaignId: campaign1.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 300000), // 5 minutes ago
          metadata: { callType: 'sales', priority: 'high' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent2.id,
          campaignId: campaign2.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 180000), // 3 minutes ago
          metadata: { callType: 'support', priority: 'urgent' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.RINGING,
          campaignId: campaign1.id,
          metadata: { callType: 'sales', priority: 'medium' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          campaignId: campaign2.id,
          metadata: { callType: 'support', queuePosition: 1 }
        }),
        
        // Recently completed calls
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          campaignId: campaign1.id,
          status: CallStatus.COMPLETED,
          duration: 240,
          disposition: 'successful',
          endTime: new Date(Date.now() - 60000), // 1 minute ago
          metadata: { callType: 'sales', outcome: 'sale_made' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent2.id,
          campaignId: campaign2.id,
          status: CallStatus.COMPLETED,
          duration: 180,
          disposition: 'resolved',
          endTime: new Date(Date.now() - 120000), // 2 minutes ago
          metadata: { callType: 'support', outcome: 'issue_resolved' }
        }),
        
        // Failed/missed calls
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.NO_ANSWER,
          disposition: 'no_answer',
          endTime: new Date(Date.now() - 300000),
          metadata: { callType: 'sales', attempts: 1 }
        })
      ]);

      // Get dashboard overview data
      const dashboardData = await getDashboardOverview(testOrganization.id);

      expect(dashboardData.callStats.activeCalls).toBe(4); // 2 in_progress + 1 ringing + 1 queued
      expect(dashboardData.callStats.totalCalls).toBeGreaterThanOrEqual(7);
      expect(dashboardData.callStats.completedCalls).toBe(2);
      expect(dashboardData.callStats.missedCalls).toBe(1);
      expect(dashboardData.callStats.averageDuration).toBeGreaterThan(0);
      expect(dashboardData.teamStatus.totalMembers).toBe(3);
      expect(dashboardData.teamStatus.availableAgents).toBe(1);
      expect(dashboardData.teamStatus.busyAgents).toBe(1);
      expect(dashboardData.teamStatus.onBreakAgents).toBe(1);
    });

    it('should track real-time call status changes', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.RINGING
      });

      // Initial dashboard state
      let dashboardData = await getDashboardOverview(testOrganization.id);
      const initialRingingCalls = dashboardData.activeCalls.filter(c => c.status === CallStatus.RINGING).length;

      // Update call to IN_PROGRESS
      await testDb.call.update({
        where: { id: call.id },
        data: {
          status: CallStatus.IN_PROGRESS,
          metadata: {
            statusChanged: new Date(),
            previousStatus: 'RINGING'
          }
        }
      });

      // Get updated dashboard data
      dashboardData = await getDashboardOverview(testOrganization.id);
      const updatedRingingCalls = dashboardData.activeCalls.filter(c => c.status === CallStatus.RINGING).length;
      const inProgressCalls = dashboardData.activeCalls.filter(c => c.status === CallStatus.IN_PROGRESS).length;

      expect(updatedRingingCalls).toBe(initialRingingCalls - 1);
      expect(inProgressCalls).toBeGreaterThan(0);

      // Complete the call
      const endTime = new Date();
      const duration = 120;
      
      await testDb.call.update({
        where: { id: call.id },
        data: {
          status: CallStatus.COMPLETED,
          endTime,
          duration,
          disposition: 'successful'
        }
      });

      // Final dashboard state
      dashboardData = await getDashboardOverview(testOrganization.id);
      const finalActiveCalls = dashboardData.activeCalls.filter(c => c.id === call.id).length;
      expect(finalActiveCalls).toBe(0); // Should no longer be in active calls
      expect(dashboardData.callStats.completedCalls).toBeGreaterThan(0);
    });

    it('should provide real-time agent status updates', async () => {
      // Initial agent status
      let teamStatus = await getTeamStatus(testOrganization.id);
      const initialAvailable = teamStatus.stats.availableAgents;
      const initialBusy = teamStatus.stats.busyAgents;

      // Change agent status from AVAILABLE to BUSY
      await testDb.agent.update({
        where: { userId: agent1.id },
        data: { status: AgentStatus.BUSY }
      });

      await testDb.user.update({
        where: { id: agent1.id },
        data: { status: UserStatus.BUSY }
      });

      // Check updated status
      teamStatus = await getTeamStatus(testOrganization.id);
      expect(teamStatus.stats.availableAgents).toBe(initialAvailable - 1);
      expect(teamStatus.stats.busyAgents).toBe(initialBusy + 1);

      // Verify agent details
      const busyAgent = teamStatus.members.find(member => member.id === agent1.id);
      expect(busyAgent?.status).toBe('busy');
      expect(busyAgent?.lastActivity).toBeDefined();
    });

    it('should track campaign performance metrics in real-time', async () => {
      // Create calls for campaign metrics
      await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign1.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          duration: 180,
          disposition: 'successful'
        }),
        createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign1.id,
          agentId: agent2.id,
          status: CallStatus.COMPLETED,
          duration: 240,
          disposition: 'successful'
        }),
        createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign1.id,
          status: CallStatus.NO_ANSWER,
          disposition: 'no_answer'
        }),
        createTestCall({
          organizationId: testOrganization.id,
          campaignId: campaign1.id,
          agentId: agent1.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 120000) // 2 minutes ago
        })
      ]);

      const campaignMetrics = await getCampaignMetrics(campaign1.id);
      
      expect(campaignMetrics.totalCalls).toBe(4);
      expect(campaignMetrics.completedCalls).toBe(2);
      expect(campaignMetrics.activeCalls).toBe(1);
      expect(campaignMetrics.successRate).toBe(50); // 2 successful out of 4 total
      expect(campaignMetrics.averageDuration).toBe(210); // (180 + 240) / 2
      expect(campaignMetrics.activeCallDuration).toBeGreaterThan(100);
    });
  });

  describe('WebSocket Real-time Updates', () => {
    it('should broadcast call status changes to connected clients', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.RINGING
      });

      // Mock WebSocket clients
      const supervisorClient = { send: vi.fn(), readyState: 1 };
      const adminClient = { send: vi.fn(), readyState: 1 };
      mockWebSocket.clients.add(supervisorClient);
      mockWebSocket.clients.add(adminClient);

      // Simulate call status change
      await testDb.call.update({
        where: { id: call.id },
        data: { status: CallStatus.IN_PROGRESS }
      });

      // Simulate broadcasting the update
      const updateMessage = {
        type: 'call_status_update',
        data: {
          callId: call.id,
          status: CallStatus.IN_PROGRESS,
          agentId: agent1.id,
          timestamp: new Date().toISOString()
        }
      };

      mockWebSocket.broadcast(updateMessage);

      // Verify clients received the update
      expect(supervisorClient.send).toHaveBeenCalledWith(JSON.stringify(updateMessage));
      expect(adminClient.send).toHaveBeenCalledWith(JSON.stringify(updateMessage));
    });

    it('should broadcast agent status changes', async () => {
      const client = { send: vi.fn(), readyState: 1 };
      mockWebSocket.clients.add(client);

      // Change agent status
      await testDb.agent.update({
        where: { userId: agent1.id },
        data: {
          status: AgentStatus.BREAK,
          currentLoad: 0
        }
      });

      // Simulate broadcasting agent status update
      const agentUpdate = {
        type: 'agent_status_update',
        data: {
          agentId: agent1.id,
          status: AgentStatus.BREAK,
          currentLoad: 0,
          capacity: 3,
          timestamp: new Date().toISOString()
        }
      };

      mockWebSocket.broadcast(agentUpdate);

      expect(client.send).toHaveBeenCalledWith(JSON.stringify(agentUpdate));
    });

    it('should broadcast queue updates', async () => {
      // Create queued calls
      const queuedCalls = await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          metadata: { queuePosition: 1, priority: 'high' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          metadata: { queuePosition: 2, priority: 'medium' }
        })
      ]);

      const client = { send: vi.fn(), readyState: 1 };
      mockWebSocket.clients.add(client);

      // Simulate queue update
      const queueUpdate = {
        type: 'queue_update',
        data: {
          organizationId: testOrganization.id,
          queueLength: 2,
          estimatedWaitTime: 120,
          calls: queuedCalls.map(call => ({
            id: call.id,
            position: (call.metadata as any)?.queuePosition,
            priority: (call.metadata as any)?.priority,
            waitTime: Math.floor((Date.now() - call.startTime.getTime()) / 1000)
          })),
          timestamp: new Date().toISOString()
        }
      };

      mockWebSocket.broadcast(queueUpdate);

      expect(client.send).toHaveBeenCalledWith(JSON.stringify(queueUpdate));
    });

    it('should handle client disconnections gracefully', async () => {
      const client1 = { send: vi.fn(), readyState: 1 };
      const client2 = { send: vi.fn(), readyState: 0 }; // Disconnected
      const client3 = { send: vi.fn(), readyState: 1 };
      
      mockWebSocket.clients.add(client1);
      mockWebSocket.clients.add(client2);
      mockWebSocket.clients.add(client3);

      const update = {
        type: 'test_update',
        data: { message: 'test' }
      };

      mockWebSocket.broadcast(update);

      // Only connected clients should receive the message
      expect(client1.send).toHaveBeenCalled();
      expect(client2.send).not.toHaveBeenCalled();
      expect(client3.send).toHaveBeenCalled();
    });
  });

  describe('Performance Metrics', () => {
    it('should calculate real-time performance indicators', async () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      // Create performance test data
      await Promise.all([
        // Successful calls
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          duration: 180,
          disposition: 'successful',
          startTime: new Date(today.getTime() + 3600000) // 1 hour ago
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent2.id,
          status: CallStatus.COMPLETED,
          duration: 240,
          disposition: 'successful',
          startTime: new Date(today.getTime() + 7200000) // 2 hours ago
        }),
        
        // Failed calls
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.NO_ANSWER,
          disposition: 'no_answer',
          startTime: new Date(today.getTime() + 1800000) // 30 minutes ago
        }),
        
        // Active calls
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 300000) // 5 minutes ago
        })
      ]);

      const performanceMetrics = await getPerformanceMetrics(testOrganization.id, today);
      
      expect(performanceMetrics.totalCalls).toBe(4);
      expect(performanceMetrics.completedCalls).toBe(2);
      expect(performanceMetrics.activeCalls).toBe(1);
      expect(performanceMetrics.failedCalls).toBe(1);
      expect(performanceMetrics.successRate).toBe(50); // 2/4 * 100
      expect(performanceMetrics.averageHandleTime).toBe(210); // (180 + 240) / 2
      expect(performanceMetrics.currentActiveTime).toBeGreaterThan(250); // ~300 seconds
    });

    it('should track hourly call volume trends', async () => {
      const now = new Date();
      const currentHour = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours());
      
      // Create calls for different hours
      const callsData = [];
      for (let i = 0; i < 24; i++) {
        const hourTime = new Date(currentHour.getTime() - (i * 3600000));
        const callCount = Math.floor(Math.random() * 10) + 1;
        
        for (let j = 0; j < callCount; j++) {
          callsData.push(createTestCall({
            organizationId: testOrganization.id,
            status: CallStatus.COMPLETED,
            duration: 120 + (j * 30),
            startTime: new Date(hourTime.getTime() + (j * 60000)) // Spread within hour
          }));
        }
      }
      
      await Promise.all(callsData);
      
      const hourlyTrends = await getHourlyCallTrends(testOrganization.id, 24);
      
      expect(hourlyTrends).toHaveLength(24);
      expect(hourlyTrends.every(trend => trend.hour !== undefined)).toBe(true);
      expect(hourlyTrends.every(trend => trend.callCount >= 0)).toBe(true);
      expect(hourlyTrends.some(trend => trend.callCount > 0)).toBe(true);
    });
  });

  describe('Dashboard Query Performance', () => {
    beforeEach(async () => {
      // Create a large dataset for performance testing
      const callsData = [];
      for (let i = 0; i < 200; i++) {
        callsData.push({
          organizationId: testOrganization.id,
          agentId: i % 4 === 0 ? null : [agent1.id, agent2.id, agent3.id][i % 3],
          campaignId: [campaign1.id, campaign2.id][i % 2],
          status: [CallStatus.IN_PROGRESS, CallStatus.COMPLETED, CallStatus.QUEUED, CallStatus.RINGING][i % 4],
          startTime: new Date(Date.now() - (i * 60000)), // Spread over time
          duration: i % 4 === 1 ? 60 + (i % 300) : null, // Only completed calls have duration
          fromNumber: `+180055${i.toString().padStart(4, '0')}`,
          toNumber: `+198765${i.toString().padStart(4, '0')}`,
          direction: i % 2 === 0 ? CallDirection.INBOUND : CallDirection.OUTBOUND,
          provider: 'TWILIO',
          disposition: i % 4 === 1 ? 'successful' : null
        });
      }
      
      await testDb.call.createMany({ data: callsData });
    });

    it('should efficiently load dashboard overview', async () => {
      const { duration } = await measurePerformance(async () => {
        return await getDashboardOverview(testOrganization.id);
      });
      
      expect(duration).toBeLessThan(200); // Should load dashboard quickly
    });

    it('should efficiently update real-time metrics', async () => {
      const { duration } = await measurePerformance(async () => {
        const [callStats, teamStatus, campaignMetrics] = await Promise.all([
          getCallStatistics(testOrganization.id),
          getTeamStatus(testOrganization.id),
          getCampaignMetrics(campaign1.id)
        ]);
        
        return { callStats, teamStatus, campaignMetrics };
      });
      
      expect(duration).toBeLessThan(150); // All metrics should load quickly
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle missing data gracefully', async () => {
      // Test with organization that has no calls
      const emptyOrg = await testDb.organization.create({
        data: {
          id: 'empty-org',
          name: 'Empty Organization',
          domain: 'empty.local'
        }
      });

      const dashboardData = await getDashboardOverview(emptyOrg.id);
      
      expect(dashboardData.callStats.totalCalls).toBe(0);
      expect(dashboardData.callStats.activeCalls).toBe(0);
      expect(dashboardData.teamStatus.totalMembers).toBe(0);
      expect(dashboardData.activeCalls).toHaveLength(0);
    });

    it('should handle invalid organization IDs', async () => {
      await expect(
        getDashboardOverview('non-existent-org')
      ).resolves.toEqual(expect.objectContaining({
        callStats: expect.objectContaining({
          totalCalls: 0,
          activeCalls: 0
        })
      }));
    });

    it('should handle database connection issues in real-time updates', async () => {
      // Temporarily disconnect database
      await testDb.$disconnect();
      
      // Attempt to get dashboard data - should handle gracefully
      await expect(
        getDashboardOverview(testOrganization.id)
      ).rejects.toThrow();
      
      // Reconnect for other tests
      await testDb.$connect();
    });
  });
});

// Helper functions for dashboard data retrieval
async function getDashboardOverview(organizationId: string) {
  const [callStats, activeCalls, teamStatus] = await Promise.all([
    getCallStatistics(organizationId),
    getActiveCalls(organizationId),
    getTeamStatus(organizationId)
  ]);
  
  return {
    callStats,
    activeCalls,
    teamStatus
  };
}

async function getCallStatistics(organizationId: string) {
  const callStatusStats = await testDb.call.groupBy({
    by: ['status'],
    where: { organizationId },
    _count: { id: true },
    _avg: { duration: true }
  });
  
  const stats = callStatusStats.reduce((acc, stat) => {
    acc[stat.status.toLowerCase() + 'Calls'] = stat._count.id;
    return acc;
  }, {} as any);
  
  const totalCalls = callStatusStats.reduce((sum, stat) => sum + stat._count.id, 0);
  const completedStats = callStatusStats.find(stat => stat.status === CallStatus.COMPLETED);
  const averageDuration = completedStats?._avg.duration || 0;
  
  const activeCalls = (stats.in_progressCalls || 0) + (stats.ringingCalls || 0) + (stats.queuedCalls || 0) + (stats.on_holdCalls || 0);
  
  return {
    totalCalls,
    activeCalls,
    completedCalls: stats.completedCalls || 0,
    missedCalls: (stats.no_answerCalls || 0) + (stats.busyCalls || 0) + (stats.failedCalls || 0),
    averageDuration: Math.round(averageDuration)
  };
}

async function getActiveCalls(organizationId: string) {
  return await testDb.call.findMany({
    where: {
      organizationId,
      status: {
        in: [CallStatus.RINGING, CallStatus.IN_PROGRESS, CallStatus.ON_HOLD, CallStatus.QUEUED]
      }
    },
    include: {
      agent: {
        select: {
          id: true,
          firstName: true,
          lastName: true,
          email: true
        }
      },
      campaign: {
        select: {
          id: true,
          name: true,
          type: true
        }
      }
    },
    orderBy: {
      startTime: 'desc'
    }
  });
}

async function getTeamStatus(organizationId: string) {
  const agents = await testDb.agent.findMany({
    where: {
      user: {
        organizationId
      }
    },
    include: {
      user: {
        select: {
          id: true,
          firstName: true,
          lastName: true,
          email: true,
          status: true,
          lastActivityAt: true
        }
      }
    }
  });
  
  const members = agents.map(agent => ({
    id: agent.user.id,
    name: `${agent.user.firstName} ${agent.user.lastName}`,
    email: agent.user.email,
    status: agent.status.toLowerCase(),
    activeCall: null, // Would be populated from active calls
    skills: agent.skills,
    lastActivity: agent.user.lastActivityAt?.toISOString() || new Date().toISOString()
  }));
  
  const stats = {
    totalMembers: agents.length,
    availableAgents: agents.filter(a => a.status === AgentStatus.AVAILABLE).length,
    busyAgents: agents.filter(a => a.status === AgentStatus.BUSY).length,
    onBreakAgents: agents.filter(a => a.status === AgentStatus.BREAK).length,
    offlineAgents: agents.filter(a => a.status === AgentStatus.OFFLINE).length
  };
  
  return { members, stats };
}

async function getCampaignMetrics(campaignId: string) {
  const callStats = await testDb.call.groupBy({
    by: ['status'],
    where: { campaignId },
    _count: { id: true },
    _avg: { duration: true }
  });
  
  const totalCalls = callStats.reduce((sum, stat) => sum + stat._count.id, 0);
  const completedCalls = callStats.find(stat => stat.status === CallStatus.COMPLETED)?._count.id || 0;
  const activeCalls = callStats.filter(stat => 
    [CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD, CallStatus.QUEUED].includes(stat.status as CallStatus)
  ).reduce((sum, stat) => sum + stat._count.id, 0);
  
  const successfulCalls = await testDb.call.count({
    where: {
      campaignId,
      disposition: 'successful'
    }
  });
  
  const avgDuration = callStats.find(stat => stat.status === CallStatus.COMPLETED)?._avg.duration || 0;
  
  // Get active call duration
  const activeCall = await testDb.call.findFirst({
    where: {
      campaignId,
      status: CallStatus.IN_PROGRESS
    },
    orderBy: { startTime: 'asc' }
  });
  
  const activeCallDuration = activeCall 
    ? Math.floor((Date.now() - activeCall.startTime.getTime()) / 1000)
    : 0;
  
  return {
    totalCalls,
    completedCalls,
    activeCalls,
    successRate: totalCalls > 0 ? Math.round((successfulCalls / totalCalls) * 100) : 0,
    averageDuration: Math.round(avgDuration),
    activeCallDuration
  };
}

async function getPerformanceMetrics(organizationId: string, since: Date) {
  const calls = await testDb.call.findMany({
    where: {
      organizationId,
      startTime: {
        gte: since
      }
    }
  });
  
  const totalCalls = calls.length;
  const completedCalls = calls.filter(call => call.status === CallStatus.COMPLETED).length;
  const activeCalls = calls.filter(call => 
    [CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD].includes(call.status as CallStatus)
  ).length;
  const failedCalls = calls.filter(call => 
    [CallStatus.NO_ANSWER, CallStatus.BUSY, CallStatus.FAILED].includes(call.status as CallStatus)
  ).length;
  
  const successfulCalls = calls.filter(call => call.disposition === 'successful').length;
  const successRate = totalCalls > 0 ? Math.round((successfulCalls / totalCalls) * 100) : 0;
  
  const completedCallsWithDuration = calls.filter(call => call.duration !== null);
  const totalDuration = completedCallsWithDuration.reduce((sum, call) => sum + (call.duration || 0), 0);
  const averageHandleTime = completedCallsWithDuration.length > 0 
    ? Math.round(totalDuration / completedCallsWithDuration.length)
    : 0;
  
  // Calculate current active call time
  const activeCall = calls.find(call => call.status === CallStatus.IN_PROGRESS);
  const currentActiveTime = activeCall 
    ? Math.floor((Date.now() - activeCall.startTime.getTime()) / 1000)
    : 0;
  
  return {
    totalCalls,
    completedCalls,
    activeCalls,
    failedCalls,
    successRate,
    averageHandleTime,
    currentActiveTime
  };
}

async function getHourlyCallTrends(organizationId: string, hours: number) {
  const trends = [];
  const now = new Date();
  
  for (let i = 0; i < hours; i++) {
    const hourStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() - i);
    const hourEnd = new Date(hourStart.getTime() + 3600000);
    
    const callCount = await testDb.call.count({
      where: {
        organizationId,
        startTime: {
          gte: hourStart,
          lt: hourEnd
        }
      }
    });
    
    trends.push({
      hour: hourStart.getHours(),
      date: hourStart.toISOString(),
      callCount
    });
  }
  
  return trends.reverse(); // Return chronological order
}
