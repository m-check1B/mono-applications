import { describe, it, expect, beforeEach, beforeAll, afterAll, vi } from 'vitest';
import { PrismaClient, UserRole, CallStatus, CallDirection, AgentStatus, UserStatus } from '@prisma/client';
import { testDb, createTestUser, createTestCampaign, createTestCall, measurePerformance } from '../setup';

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Active Calls Tracking Integration Tests', () => {
  let testOrganization: any;
  let agent1: any;
  let agent2: any;
  let agent3: any;
  let supervisor: any;
  let campaign1: any;
  let campaign2: any;

  beforeEach(async () => {
    // Create test organization
    testOrganization = await testDb.organization.create({
      data: {
        id: 'test-org-active-calls',
        name: 'Active Calls Test Organization',
        domain: 'active-calls.local',
        settings: {
          maxConcurrentCalls: 10,
          callMonitoring: true,
          realTimeUpdates: true
        }
      }
    });

    // Create test agents with different statuses
    agent1 = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'agent1@active-calls.local',
      firstName: 'Agent',
      lastName: 'One',
      status: UserStatus.AVAILABLE
    });

    agent2 = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'agent2@active-calls.local',
      firstName: 'Agent',
      lastName: 'Two',
      status: UserStatus.BUSY
    });

    agent3 = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.AGENT,
      email: 'agent3@active-calls.local',
      firstName: 'Agent',
      lastName: 'Three',
      status: UserStatus.AVAILABLE
    });

    supervisor = await createTestUser({
      organizationId: testOrganization.id,
      role: UserRole.SUPERVISOR,
      email: 'supervisor@active-calls.local',
      firstName: 'Supervisor',
      lastName: 'User'
    });

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
          status: AgentStatus.AVAILABLE,
          capacity: 4,
          currentLoad: 0,
          skills: ['sales']
        }
      })
    ]);

    // Create test campaigns
    campaign1 = await createTestCampaign({
      organizationId: testOrganization.id,
      name: 'Sales Campaign',
      active: true
    });

    campaign2 = await createTestCampaign({
      organizationId: testOrganization.id,
      name: 'Support Campaign',
      active: true
    });
  });

  describe('Real-time Call Tracking', () => {
    it('should track active calls across all agents', async () => {
      // Create active calls for different agents
      const activeCalls = await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          campaignId: campaign1.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 120000), // 2 minutes ago
          metadata: { callType: 'sales', priority: 'high' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          campaignId: campaign1.id,
          status: CallStatus.RINGING,
          startTime: new Date(Date.now() - 30000), // 30 seconds ago
          metadata: { callType: 'sales', priority: 'medium' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent2.id,
          campaignId: campaign2.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 300000), // 5 minutes ago
          metadata: { callType: 'support', priority: 'urgent' }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent3.id,
          campaignId: campaign1.id,
          status: CallStatus.ON_HOLD,
          startTime: new Date(Date.now() - 180000), // 3 minutes ago
          metadata: { callType: 'sales', holdReason: 'customer_request' }
        })
      ]);

      // Query active calls
      const activeCallsQuery = await testDb.call.findMany({
        where: {
          organizationId: testOrganization.id,
          status: {
            in: [CallStatus.RINGING, CallStatus.IN_PROGRESS, CallStatus.ON_HOLD]
          }
        },
        include: {
          agent: {
            select: {
              id: true,
              firstName: true,
              lastName: true,
              email: true,
              status: true
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

      expect(activeCallsQuery).toHaveLength(4);
      expect(activeCallsQuery.every(call => call.organizationId === testOrganization.id)).toBe(true);
      expect(activeCallsQuery.filter(call => call.status === CallStatus.IN_PROGRESS)).toHaveLength(2);
      expect(activeCallsQuery.filter(call => call.status === CallStatus.RINGING)).toHaveLength(1);
      expect(activeCallsQuery.filter(call => call.status === CallStatus.ON_HOLD)).toHaveLength(1);
    });

    it('should track call duration in real-time', async () => {
      const startTime = new Date(Date.now() - 180000); // 3 minutes ago
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.IN_PROGRESS,
        startTime
      });

      // Calculate current duration
      const currentTime = new Date();
      const expectedDuration = Math.floor((currentTime.getTime() - startTime.getTime()) / 1000);

      // Query call with calculated duration
      const callWithDuration = await testDb.call.findUnique({
        where: { id: call.id },
        select: {
          id: true,
          status: true,
          startTime: true,
          agentId: true,
          metadata: true
        }
      });

      expect(callWithDuration).toBeDefined();
      expect(callWithDuration?.startTime).toEqual(startTime);
      
      // Calculate duration (this would be done in real-time in the application)
      const actualDuration = Math.floor((currentTime.getTime() - callWithDuration!.startTime.getTime()) / 1000);
      expect(actualDuration).toBeGreaterThan(170); // Should be around 180 seconds
      expect(actualDuration).toBeLessThan(200);
    });

    it('should track agent workload and capacity', async () => {
      // Create multiple calls for agent1
      const agent1Calls = await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.IN_PROGRESS
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.RINGING
        })
      ]);

      // Update agent workload
      await testDb.agent.update({
        where: { userId: agent1.id },
        data: { currentLoad: 2 }
      });

      // Query agent with active calls count
      const agentWorkload = await testDb.agent.findUnique({
        where: { userId: agent1.id },
        include: {
          user: {
            include: {
              agentCalls: {
                where: {
                  status: {
                    in: [CallStatus.RINGING, CallStatus.IN_PROGRESS, CallStatus.ON_HOLD]
                  }
                }
              }
            }
          }
        }
      });

      expect(agentWorkload?.currentLoad).toBe(2);
      expect(agentWorkload?.capacity).toBe(3);
      expect(agentWorkload?.user?.agentCalls).toHaveLength(2);
      
      // Check if agent is at capacity
      const isAtCapacity = agentWorkload!.currentLoad >= agentWorkload!.capacity;
      expect(isAtCapacity).toBe(false); // 2/3 capacity
    });

    it('should provide real-time dashboard metrics', async () => {
      // Create various calls for dashboard metrics
      await Promise.all([
        // Active calls
        createTestCall({ organizationId: testOrganization.id, agentId: agent1.id, status: CallStatus.IN_PROGRESS }),
        createTestCall({ organizationId: testOrganization.id, agentId: agent2.id, status: CallStatus.IN_PROGRESS }),
        createTestCall({ organizationId: testOrganization.id, agentId: agent3.id, status: CallStatus.RINGING }),
        createTestCall({ organizationId: testOrganization.id, status: CallStatus.QUEUED }), // Unassigned
        
        // Recently completed calls
        createTestCall({ 
          organizationId: testOrganization.id, 
          agentId: agent1.id, 
          status: CallStatus.COMPLETED, 
          duration: 120,
          endTime: new Date(Date.now() - 60000) // 1 minute ago
        }),
        createTestCall({ 
          organizationId: testOrganization.id, 
          agentId: agent2.id, 
          status: CallStatus.COMPLETED, 
          duration: 180,
          endTime: new Date(Date.now() - 120000) // 2 minutes ago
        }),
        
        // Failed calls
        createTestCall({ 
          organizationId: testOrganization.id, 
          status: CallStatus.NO_ANSWER,
          endTime: new Date(Date.now() - 300000) // 5 minutes ago
        })
      ]);

      // Get real-time dashboard metrics
      const dashboardMetrics = await testDb.call.groupBy({
        by: ['status'],
        where: { organizationId: testOrganization.id },
        _count: { id: true }
      });

      const metricsMap = dashboardMetrics.reduce((acc, metric) => {
        acc[metric.status] = metric._count.id;
        return acc;
      }, {} as Record<string, number>);

      expect(metricsMap[CallStatus.IN_PROGRESS]).toBe(2);
      expect(metricsMap[CallStatus.RINGING]).toBe(1);
      expect(metricsMap[CallStatus.QUEUED]).toBe(1);
      expect(metricsMap[CallStatus.COMPLETED]).toBe(2);
      expect(metricsMap[CallStatus.NO_ANSWER]).toBe(1);

      // Get agent availability
      const agentAvailability = await testDb.agent.findMany({
        where: {
          user: {
            organizationId: testOrganization.id
          }
        },
        include: {
          user: {
            select: {
              firstName: true,
              lastName: true,
              status: true
            }
          }
        }
      });

      const availableAgents = agentAvailability.filter(agent => agent.status === AgentStatus.AVAILABLE);
      const busyAgents = agentAvailability.filter(agent => agent.status === AgentStatus.BUSY);
      
      expect(availableAgents.length).toBeGreaterThan(0);
      expect(busyAgents.length).toBeGreaterThan(0);
    });
  });

  describe('Call Queue Management', () => {
    it('should manage call queue efficiently', async () => {
      // Create call queue
      const callQueue = await testDb.callQueue.create({
        data: {
          organizationId: testOrganization.id,
          name: 'Main Queue',
          priority: 'HIGH',
          status: 'ACTIVE',
          maxWaitTime: 300, // 5 minutes
          estimatedWait: 60 // 1 minute
        }
      });

      // Create queued calls
      const queuedCalls = await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          metadata: {
            queueId: callQueue.id,
            queuePosition: 1,
            queuedAt: new Date(Date.now() - 30000) // 30 seconds ago
          }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          metadata: {
            queueId: callQueue.id,
            queuePosition: 2,
            queuedAt: new Date(Date.now() - 15000) // 15 seconds ago
          }
        }),
        createTestCall({
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED,
          metadata: {
            queueId: callQueue.id,
            queuePosition: 3,
            queuedAt: new Date()
          }
        })
      ]);

      // Query queue status
      const queueStatus = await testDb.call.findMany({
        where: {
          organizationId: testOrganization.id,
          status: CallStatus.QUEUED
        },
        orderBy: {
          startTime: 'asc' // FIFO queue
        }
      });

      expect(queueStatus).toHaveLength(3);
      
      // Verify queue order (oldest first)
      expect((queueStatus[0].metadata as any)?.queuePosition).toBe(1);
      expect((queueStatus[1].metadata as any)?.queuePosition).toBe(2);
      expect((queueStatus[2].metadata as any)?.queuePosition).toBe(3);
    });

    it('should handle call assignment from queue', async () => {
      // Create queued call
      const queuedCall = await createTestCall({
        organizationId: testOrganization.id,
        status: CallStatus.QUEUED,
        metadata: {
          queuedAt: new Date(),
          priority: 'high'
        }
      });

      // Find available agent
      const availableAgent = await testDb.agent.findFirst({
        where: {
          user: {
            organizationId: testOrganization.id
          },
          status: AgentStatus.AVAILABLE,
          currentLoad: {
            lt: testDb.agent.fields.capacity
          }
        },
        include: {
          user: true
        }
      });

      expect(availableAgent).toBeDefined();

      // Assign call to agent
      const assignedCall = await testDb.call.update({
        where: { id: queuedCall.id },
        data: {
          agentId: availableAgent!.userId,
          status: CallStatus.RINGING,
          metadata: {
            ...(queuedCall.metadata as any),
            assignedAt: new Date(),
            queueTime: 30 // seconds in queue
          }
        }
      });

      // Update agent load
      await testDb.agent.update({
        where: { userId: availableAgent!.userId },
        data: {
          currentLoad: {
            increment: 1
          },
          status: AgentStatus.BUSY
        }
      });

      expect(assignedCall.status).toBe(CallStatus.RINGING);
      expect(assignedCall.agentId).toBe(availableAgent!.userId);
      expect((assignedCall.metadata as any)?.assignedAt).toBeDefined();
    });

    it('should track queue wait times and SLA metrics', async () => {
      const queueEntryTime = new Date(Date.now() - 120000); // 2 minutes ago
      const assignmentTime = new Date();
      
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.IN_PROGRESS,
        startTime: queueEntryTime,
        metadata: {
          queuedAt: queueEntryTime,
          assignedAt: assignmentTime,
          queueWaitTime: 120, // 2 minutes
          slaTarget: 60, // 1 minute SLA
          slaMet: false
        }
      });

      // Calculate SLA metrics
      const slaMetrics = await testDb.call.aggregate({
        where: {
          organizationId: testOrganization.id,
          status: {
            in: [CallStatus.IN_PROGRESS, CallStatus.COMPLETED]
          }
        },
        _avg: {
          duration: true
        },
        _count: {
          id: true
        }
      });

      expect(slaMetrics._count.id).toBeGreaterThan(0);
      
      // Check if this call exceeded SLA
      const queueWaitTime = (call.metadata as any)?.queueWaitTime;
      const slaTarget = (call.metadata as any)?.slaTarget;
      const slaMet = queueWaitTime <= slaTarget;
      
      expect(slaMet).toBe(false); // 120 > 60 seconds
    });
  });

  describe('Real-time Status Updates', () => {
    it('should track status changes with timestamps', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.QUEUED
      });

      const statusHistory = [];

      // Simulate status progression
      const statuses = [
        { status: CallStatus.RINGING, event: 'call_initiated' },
        { status: CallStatus.IN_PROGRESS, event: 'call_answered' },
        { status: CallStatus.ON_HOLD, event: 'call_held' },
        { status: CallStatus.IN_PROGRESS, event: 'call_resumed' },
        { status: CallStatus.COMPLETED, event: 'call_ended' }
      ];

      for (const [index, { status, event }] of statuses.entries()) {
        const timestamp = new Date(Date.now() + index * 1000);
        statusHistory.push({ status, event, timestamp });
        
        await testDb.call.update({
          where: { id: call.id },
          data: {
            status: status as CallStatus,
            metadata: {
              statusHistory,
              lastStatusChange: timestamp,
              currentEvent: event
            }
          }
        });
      }

      const finalCall = await testDb.call.findUnique({
        where: { id: call.id }
      });

      expect(finalCall?.status).toBe(CallStatus.COMPLETED);
      expect((finalCall?.metadata as any)?.statusHistory).toHaveLength(5);
      expect((finalCall?.metadata as any)?.currentEvent).toBe('call_ended');
    });

    it('should handle concurrent status updates', async () => {
      const call = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.RINGING
      });

      // Simulate concurrent updates
      const updates = [
        testDb.call.update({
          where: { id: call.id },
          data: {
            status: CallStatus.IN_PROGRESS,
            metadata: { event: 'answered', timestamp: new Date() }
          }
        }),
        testDb.call.update({
          where: { id: call.id },
          data: {
            agentId: agent2.id,
            metadata: { event: 'transferred', timestamp: new Date() }
          }
        })
      ];

      const results = await Promise.allSettled(updates);
      expect(results.every(result => result.status === 'fulfilled')).toBe(true);

      const updatedCall = await testDb.call.findUnique({
        where: { id: call.id }
      });

      expect(updatedCall).toBeDefined();
      expect(updatedCall?.status).toBe(CallStatus.IN_PROGRESS);
    });
  });

  describe('Agent Performance Tracking', () => {
    it('should track agent call statistics in real-time', async () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      // Create calls for agent performance tracking
      await Promise.all([
        // Completed calls
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          duration: 120,
          disposition: 'successful',
          startTime: new Date(today.getTime() + 60000) // Today
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          duration: 180,
          disposition: 'successful',
          startTime: new Date(today.getTime() + 120000) // Today
        }),
        
        // Current active call
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 300000) // 5 minutes ago
        }),
        
        // Missed call
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.NO_ANSWER,
          disposition: 'no_answer',
          startTime: new Date(today.getTime() + 180000) // Today
        })
      ]);

      // Get agent performance metrics
      const agentStats = await testDb.call.groupBy({
        by: ['agentId', 'status'],
        where: {
          organizationId: testOrganization.id,
          agentId: agent1.id,
          startTime: {
            gte: today
          }
        },
        _count: { id: true },
        _avg: { duration: true }
      });

      const completedCalls = agentStats.find(stat => stat.status === CallStatus.COMPLETED);
      const activeCalls = agentStats.find(stat => stat.status === CallStatus.IN_PROGRESS);
      const missedCalls = agentStats.find(stat => stat.status === CallStatus.NO_ANSWER);

      expect(completedCalls?._count.id).toBe(2);
      expect(activeCalls?._count.id).toBe(1);
      expect(missedCalls?._count.id).toBe(1);
      expect(completedCalls?._avg.duration).toBe(150); // (120 + 180) / 2
    });

    it('should calculate agent utilization rates', async () => {
      const workdayStart = new Date();
      workdayStart.setHours(9, 0, 0, 0);
      const workdayEnd = new Date();
      workdayEnd.setHours(17, 0, 0, 0);
      
      // Create calls spanning work hours
      await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          startTime: new Date(workdayStart.getTime() + 60000),
          endTime: new Date(workdayStart.getTime() + 180000), // 2 minute call
          duration: 120
        }),
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          startTime: new Date(workdayStart.getTime() + 300000),
          endTime: new Date(workdayStart.getTime() + 600000), // 5 minute call
          duration: 300
        })
      ]);

      // Calculate utilization
      const totalCallTime = await testDb.call.aggregate({
        where: {
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.COMPLETED,
          startTime: {
            gte: workdayStart,
            lte: workdayEnd
          }
        },
        _sum: { duration: true },
        _count: { id: true }
      });

      const totalWorkSeconds = (workdayEnd.getTime() - workdayStart.getTime()) / 1000;
      const totalCallSeconds = totalCallTime._sum.duration || 0;
      const utilizationRate = (totalCallSeconds / totalWorkSeconds) * 100;

      expect(totalCallTime._count.id).toBe(2);
      expect(totalCallSeconds).toBe(420); // 120 + 300
      expect(utilizationRate).toBeGreaterThan(0);
      expect(utilizationRate).toBeLessThan(100);
    });
  });

  describe('Performance Optimization', () => {
    it('should efficiently query active calls with complex filters', async () => {
      // Create a large number of calls for performance testing
      const callsData = [];
      const statuses = [CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD, CallStatus.COMPLETED];
      const agents = [agent1.id, agent2.id, agent3.id];
      const campaigns = [campaign1.id, campaign2.id];

      for (let i = 0; i < 100; i++) {
        callsData.push({
          organizationId: testOrganization.id,
          agentId: i % 4 === 0 ? null : agents[i % agents.length],
          campaignId: campaigns[i % campaigns.length],
          status: statuses[i % statuses.length],
          startTime: new Date(Date.now() - (i * 60000)), // Spread over time
          duration: statuses[i % statuses.length] === CallStatus.COMPLETED ? 60 + (i % 300) : null,
          fromNumber: `+180055${i.toString().padStart(4, '0')}`,
          toNumber: `+198765${i.toString().padStart(4, '0')}`,
          direction: i % 2 === 0 ? CallDirection.INBOUND : CallDirection.OUTBOUND,
          provider: 'TWILIO'
        });
      }

      await testDb.call.createMany({ data: callsData });

      // Performance test: Complex active calls query
      const { duration } = await measurePerformance(async () => {
        return await testDb.call.findMany({
          where: {
            organizationId: testOrganization.id,
            status: {
              in: [CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD]
            },
            startTime: {
              gte: new Date(Date.now() - 3600000) // Last hour
            }
          },
          include: {
            agent: {
              select: {
                firstName: true,
                lastName: true,
                email: true
              }
            },
            campaign: {
              select: {
                name: true,
                type: true
              }
            }
          },
          orderBy: [
            { status: 'asc' },
            { startTime: 'desc' }
          ],
          take: 20
        });
      });

      expect(duration).toBeLessThan(100); // Should be very fast with proper indexing
    });

    it('should efficiently aggregate real-time statistics', async () => {
      const { duration } = await measurePerformance(async () => {
        // Multiple aggregate queries that would run for dashboard
        const [callStatusStats, agentStats, campaignStats] = await Promise.all([
          // Call status distribution
          testDb.call.groupBy({
            by: ['status'],
            where: { organizationId: testOrganization.id },
            _count: { id: true }
          }),
          
          // Agent workload
          testDb.call.groupBy({
            by: ['agentId'],
            where: {
              organizationId: testOrganization.id,
              status: {
                in: [CallStatus.IN_PROGRESS, CallStatus.RINGING, CallStatus.ON_HOLD]
              }
            },
            _count: { id: true }
          }),
          
          // Campaign performance
          testDb.call.groupBy({
            by: ['campaignId'],
            where: {
              organizationId: testOrganization.id,
              startTime: {
                gte: new Date(Date.now() - 86400000) // Last 24 hours
              }
            },
            _count: { id: true },
            _avg: { duration: true }
          })
        ]);

        return { callStatusStats, agentStats, campaignStats };
      });

      expect(duration).toBeLessThan(200); // Should aggregate quickly
    });
  });

  describe('Data Consistency and Integrity', () => {
    it('should maintain consistency during agent status changes', async () => {
      // Create active call for agent
      const activeCall = await createTestCall({
        organizationId: testOrganization.id,
        agentId: agent1.id,
        status: CallStatus.IN_PROGRESS
      });

      // Agent goes offline - should handle gracefully
      await testDb.agent.update({
        where: { userId: agent1.id },
        data: {
          status: AgentStatus.OFFLINE,
          currentLoad: 0
        }
      });

      await testDb.user.update({
        where: { id: agent1.id },
        data: { status: UserStatus.OFFLINE }
      });

      // Call should still exist and be trackable
      const callAfterAgentOffline = await testDb.call.findUnique({
        where: { id: activeCall.id },
        include: {
          agent: true
        }
      });

      expect(callAfterAgentOffline).toBeDefined();
      expect(callAfterAgentOffline?.agentId).toBe(agent1.id);
      expect(callAfterAgentOffline?.agent?.status).toBe(UserStatus.OFFLINE);
    });

    it('should handle organization-level call isolation', async () => {
      // Create another organization
      const otherOrg = await testDb.organization.create({
        data: {
          id: 'other-org',
          name: 'Other Organization',
          domain: 'other.local'
        }
      });

      const otherOrgUser = await createTestUser({
        organizationId: otherOrg.id,
        email: 'user@other.local'
      });

      // Create calls for both organizations
      await Promise.all([
        createTestCall({
          organizationId: testOrganization.id,
          agentId: agent1.id,
          status: CallStatus.IN_PROGRESS
        }),
        createTestCall({
          organizationId: otherOrg.id,
          agentId: otherOrgUser.id,
          status: CallStatus.IN_PROGRESS
        })
      ]);

      // Query should only return calls for specific organization
      const orgCalls = await testDb.call.findMany({
        where: { organizationId: testOrganization.id }
      });

      const otherOrgCalls = await testDb.call.findMany({
        where: { organizationId: otherOrg.id }
      });

      expect(orgCalls.every(call => call.organizationId === testOrganization.id)).toBe(true);
      expect(otherOrgCalls.every(call => call.organizationId === otherOrg.id)).toBe(true);
      expect(orgCalls.length).toBeGreaterThan(0);
      expect(otherOrgCalls.length).toBeGreaterThan(0);
    });
  });
});
