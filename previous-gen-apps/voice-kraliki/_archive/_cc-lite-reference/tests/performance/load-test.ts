import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { performance } from 'perf_hooks';
import { testDb, createTestUser, createTestCall, createTestCampaign, measurePerformance } from '../setup';
import { CallService } from '../../server/services/call.service';
import { CampaignService } from '../../server/services/campaign-service';
import { AIAssistantService } from '../../server/services/ai-assistant-service';
import { FastifyInstance } from 'fastify';
import { UserRole, CallStatus, CallDirection, TelephonyProvider, CampaignType } from '@prisma/client';

// Performance test configuration
const PERFORMANCE_CONFIG = {
  // Response time thresholds (milliseconds)
  thresholds: {
    database: {
      simple_query: 50,
      complex_query: 200,
      bulk_insert: 500,
    },
    api: {
      call_list: 300,
      call_create: 200,
      call_update: 150,
      campaign_stats: 400,
    },
    service: {
      ai_processing: 1000,
      sentiment_analysis: 800,
      call_handling: 100,
    },
  },
  // Load test parameters
  load: {
    concurrent_users: 50,
    requests_per_second: 100,
    test_duration: 30000, // 30 seconds
    ramp_up_time: 5000, // 5 seconds
  },
  // Memory thresholds (MB)
  memory: {
    max_heap_usage: 512,
    max_memory_leak: 50,
  },
};

// Mock fastify instance for testing
const mockFastify = {
  log: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
} as unknown as FastifyInstance;

describe('Performance and Load Tests', () => {
  let testOrganizationId: string;
  let testUsers: any[];
  let testCampaigns: any[];
  let callService: CallService;
  let campaignService: CampaignService;
  let aiService: AIAssistantService;

  beforeAll(async () => {
    testOrganizationId = 'perf-test-org';

    // Create test services
    callService = new CallService(mockFastify, testDb);
    campaignService = new CampaignService(mockFastify, testDb);
    aiService = new AIAssistantService(mockFastify);

    // Create test users
    testUsers = [];
    for (let i = 0; i < 10; i++) {
      const user = await createTestUser({
        email: `perfuser${i}@test.com`,
        username: `perfuser${i}`,
        role: i < 2 ? UserRole.SUPERVISOR : UserRole.AGENT,
        organizationId: testOrganizationId,
      });
      testUsers.push(user);
    }

    // Create test campaigns
    testCampaigns = [];
    for (let i = 0; i < 3; i++) {
      const campaign = await createTestCampaign({
        name: `Performance Test Campaign ${i + 1}`,
        organizationId: testOrganizationId,
        type: CampaignType.OUTBOUND,
      });
      testCampaigns.push(campaign);
    }
  });

  afterAll(async () => {
    // Cleanup test data
    await testDb.call.deleteMany({
      where: { organizationId: testOrganizationId },
    });
    await testDb.campaign.deleteMany({
      where: { organizationId: testOrganizationId },
    });
    await testDb.user.deleteMany({
      where: { organizationId: testOrganizationId },
    });
  });

  describe('Database Performance', () => {
    it('should perform simple queries within threshold', async () => {
      const { duration } = await measurePerformance(async () => {
        await testDb.user.findMany({
          where: { organizationId: testOrganizationId },
          take: 10,
        });
      });

      expect(duration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.database.simple_query);
    });

    it('should perform complex queries within threshold', async () => {
      // Create test data
      const calls = [];
      for (let i = 0; i < 100; i++) {
        const call = await createTestCall({
          organizationId: testOrganizationId,
          agentId: testUsers[i % testUsers.length].id,
          campaignId: testCampaigns[i % testCampaigns.length].id,
          status: i % 3 === 0 ? CallStatus.COMPLETED : CallStatus.IN_PROGRESS,
          duration: i % 3 === 0 ? 120 + (i % 300) : null,
        });
        calls.push(call);
      }

      const { duration } = await measurePerformance(async () => {
        await testDb.call.findMany({
          where: {
            organizationId: testOrganizationId,
          },
          include: {
            agent: {
              select: {
                id: true,
                firstName: true,
                lastName: true,
                email: true,
              },
            },
            campaign: {
              select: {
                id: true,
                name: true,
                type: true,
              },
            },
            transcripts: {
              take: 5,
              orderBy: { timestamp: 'desc' },
            },
          },
          orderBy: { startTime: 'desc' },
          take: 50,
        });
      });

      expect(duration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.database.complex_query);
    });

    it('should perform bulk inserts within threshold', async () => {
      const callsData = Array.from({ length: 100 }, (_, i) => ({
        fromNumber: `+123456${String(i).padStart(4, '0')}`,
        toNumber: '+1987654321',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: testOrganizationId,
        agentId: testUsers[i % testUsers.length].id,
        startTime: new Date(),
        metadata: { batchId: 'performance-test' },
      }));

      const { duration } = await measurePerformance(async () => {
        await testDb.call.createMany({
          data: callsData,
        });
      });

      expect(duration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.database.bulk_insert);

      // Cleanup
      await testDb.call.deleteMany({
        where: {
          metadata: { path: ['batchId'], equals: 'performance-test' },
        },
      });
    });

    it('should handle concurrent database operations', async () => {
      const concurrentOperations = Array.from({ length: 20 }, async (_, i) => {
        return measurePerformance(async () => {
          // Mix of read and write operations
          if (i % 3 === 0) {
            // Create call
            return createTestCall({
              organizationId: testOrganizationId,
              agentId: testUsers[i % testUsers.length].id,
            });
          } else if (i % 3 === 1) {
            // Read calls
            return testDb.call.findMany({
              where: { organizationId: testOrganizationId },
              take: 10,
            });
          } else {
            // Read users
            return testDb.user.findMany({
              where: { organizationId: testOrganizationId },
            });
          }
        });
      });

      const results = await Promise.all(concurrentOperations);

      // All operations should complete within reasonable time
      results.forEach((result, index) => {
        expect(result.duration).toBeLessThan(1000); // 1 second max
      });

      // Average response time should be reasonable
      const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
      expect(avgDuration).toBeLessThan(300);
    });
  });

  describe('Service Layer Performance', () => {
    it('should handle call service operations within threshold', async () => {
      // Test call listing performance
      const { duration: listDuration } = await measurePerformance(async () => {
        await callService.listCalls(
          { organizationId: testOrganizationId },
          50,
          0
        );
      });
      expect(listDuration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.api.call_list);

      // Test call creation performance
      const { duration: createDuration } = await measurePerformance(async () => {
        await callService.createCall({
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: CallDirection.INBOUND,
          provider: TelephonyProvider.TWILIO,
          organizationId: testOrganizationId,
          agentId: testUsers[0].id,
        });
      });
      expect(createDuration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.api.call_create);

      // Test call stats performance
      const { duration: statsDuration } = await measurePerformance(async () => {
        await callService.getCallStats(testOrganizationId);
      });
      expect(statsDuration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.api.campaign_stats);
    });

    it('should handle campaign service operations within threshold', async () => {
      const campaign = testCampaigns[0];

      // Test campaign stats performance
      const { duration } = await measurePerformance(async () => {
        await campaignService.getCampaignStats(campaign.id);
      });

      expect(duration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.api.campaign_stats);
    });

    it('should handle AI service operations within threshold', async () => {
      const mockContext = {
        callId: 'test-call',
        organizationId: testOrganizationId,
        transcripts: [
          {
            id: '1',
            callId: 'test-call',
            role: 'USER' as const,
            content: 'I need help with my billing account',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: null,
          },
        ],
      };

      // Mock AI API responses to avoid external dependencies
      const mockOpenAI = {
        chat: {
          completions: {
            create: vi.fn().mockResolvedValue({
              choices: [{ message: { content: 'billing_inquiry' } }],
            }),
          },
        },
      };

      (aiService as any).openai = mockOpenAI;

      const { duration } = await measurePerformance(async () => {
        await aiService.processCallInput(
          'I have a question about my billing',
          mockContext
        );
      });

      expect(duration).toBeLessThan(PERFORMANCE_CONFIG.thresholds.service.ai_processing);
    });

    it('should handle concurrent service operations', async () => {
      const concurrentTasks = Array.from({ length: 10 }, async (_, i) => {
        return measurePerformance(async () => {
          // Alternate between different service operations
          if (i % 3 === 0) {
            return callService.listCalls({ organizationId: testOrganizationId }, 10, i * 10);
          } else if (i % 3 === 1) {
            return callService.getCallStats(testOrganizationId);
          } else {
            return campaignService.getCampaignStats(testCampaigns[0].id);
          }
        });
      });

      const results = await Promise.all(concurrentTasks);

      // All concurrent operations should complete within reasonable time
      results.forEach(result => {
        expect(result.duration).toBeLessThan(1000);
      });

      // Average should be good
      const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
      expect(avgDuration).toBeLessThan(400);
    });
  });

  describe('Memory Performance', () => {
    it('should not exceed memory thresholds', async () => {
      const initialMemory = process.memoryUsage();

      // Perform memory-intensive operations
      const operations = [];
      for (let i = 0; i < 100; i++) {
        operations.push(
          callService.createCall({
            fromNumber: `+123456${String(i).padStart(4, '0')}`,
            toNumber: '+1987654321',
            direction: CallDirection.INBOUND,
            provider: TelephonyProvider.TWILIO,
            organizationId: testOrganizationId,
          })
        );
      }

      await Promise.all(operations);

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage();
      const memoryIncreaseMB = (finalMemory.heapUsed - initialMemory.heapUsed) / 1024 / 1024;

      expect(memoryIncreaseMB).toBeLessThan(PERFORMANCE_CONFIG.memory.max_memory_leak);
      expect(finalMemory.heapUsed / 1024 / 1024).toBeLessThan(PERFORMANCE_CONFIG.memory.max_heap_usage);
    });

    it('should handle memory cleanup properly', async () => {
      const memorySnapshots = [];

      // Take initial memory snapshot
      memorySnapshots.push(process.memoryUsage().heapUsed);

      // Create and process many objects
      for (let batch = 0; batch < 10; batch++) {
        const calls = [];
        for (let i = 0; i < 50; i++) {
          const call = await createTestCall({
            organizationId: testOrganizationId,
            agentId: testUsers[i % testUsers.length].id,
          });
          calls.push(call);
        }

        // Process calls (simulate heavy operations)
        await Promise.all(calls.map(call =>
          callService.addTranscript(
            call.id,
            'USER',
            `Test message ${batch}-${Math.random()}`,
            0.9
          )
        ));

        // Take memory snapshot
        memorySnapshots.push(process.memoryUsage().heapUsed);

        // Clean up batch
        await testDb.callTranscript.deleteMany({
          where: { callId: { in: calls.map(c => c.id) } },
        });
        await testDb.call.deleteMany({
          where: { id: { in: calls.map(c => c.id) } },
        });

        // Force garbage collection
        if (global.gc) {
          global.gc();
        }
      }

      // Memory should not continuously increase
      const memoryGrowth = memorySnapshots[memorySnapshots.length - 1] - memorySnapshots[0];
      const memoryGrowthMB = memoryGrowth / 1024 / 1024;

      expect(memoryGrowthMB).toBeLessThan(PERFORMANCE_CONFIG.memory.max_memory_leak);
    });
  });

  describe('Load Testing', () => {
    it('should handle high concurrent user load', async () => {
      const concurrentUsers = PERFORMANCE_CONFIG.load.concurrent_users;
      const userSessions = [];

      // Simulate concurrent user sessions
      for (let i = 0; i < concurrentUsers; i++) {
        const userSession = simulateUserSession(
          testUsers[i % testUsers.length],
          testOrganizationId,
          callService,
          campaignService
        );
        userSessions.push(userSession);
      }

      const startTime = performance.now();
      const results = await Promise.allSettled(userSessions);
      const endTime = performance.now();

      const totalDuration = endTime - startTime;
      const successfulSessions = results.filter(r => r.status === 'fulfilled').length;
      const failedSessions = results.filter(r => r.status === 'rejected').length;

      // At least 90% of sessions should succeed
      const successRate = successfulSessions / concurrentUsers;
      expect(successRate).toBeGreaterThan(0.9);

      // Overall test should complete within reasonable time
      expect(totalDuration).toBeLessThan(10000); // 10 seconds

      console.log(`Load test results:
        - Concurrent users: ${concurrentUsers}
        - Success rate: ${(successRate * 100).toFixed(1)}%
        - Total duration: ${totalDuration.toFixed(0)}ms
        - Failed sessions: ${failedSessions}`);
    });

    it('should maintain performance under sustained load', async () => {
      const testDuration = 10000; // 10 seconds
      const requestInterval = 100; // Every 100ms
      const startTime = Date.now();
      const results = [];

      while (Date.now() - startTime < testDuration) {
        const requestStart = performance.now();

        try {
          // Simulate common operations
          await Promise.all([
            callService.listCalls({ organizationId: testOrganizationId }, 10, 0),
            callService.getCallStats(testOrganizationId),
            campaignService.getCampaignStats(testCampaigns[0].id),
          ]);

          const requestDuration = performance.now() - requestStart;
          results.push({ success: true, duration: requestDuration });
        } catch (error) {
          results.push({ success: false, error: error.message });
        }

        // Wait before next iteration
        await new Promise(resolve => setTimeout(resolve, requestInterval));
      }

      // Analyze results
      const successfulRequests = results.filter(r => r.success);
      const successRate = successfulRequests.length / results.length;
      const avgResponseTime = successfulRequests.reduce((sum, r) => sum + r.duration, 0) / successfulRequests.length;

      expect(successRate).toBeGreaterThan(0.95); // 95% success rate
      expect(avgResponseTime).toBeLessThan(500); // Average response time under 500ms

      console.log(`Sustained load test results:
        - Total requests: ${results.length}
        - Success rate: ${(successRate * 100).toFixed(1)}%
        - Average response time: ${avgResponseTime.toFixed(0)}ms`);
    });

    it('should handle database connection pool exhaustion gracefully', async () => {
      // Create many concurrent database operations
      const concurrentQueries = Array.from({ length: 100 }, async (_, i) => {
        try {
          const result = await testDb.call.findMany({
            where: { organizationId: testOrganizationId },
            take: 1,
          });
          return { success: true, result: result.length };
        } catch (error) {
          return { success: false, error: error.message };
        }
      });

      const results = await Promise.allSettled(concurrentQueries);
      const successful = results.filter(r =>
        r.status === 'fulfilled' && r.value.success
      ).length;

      // Most queries should succeed even under high load
      const successRate = successful / results.length;
      expect(successRate).toBeGreaterThan(0.8); // 80% minimum success rate
    });
  });

  describe('Response Time Distribution', () => {
    it('should have acceptable response time percentiles', async () => {
      const responseTimes = [];

      // Collect response times for multiple operations
      for (let i = 0; i < 100; i++) {
        const startTime = performance.now();
        await callService.listCalls({ organizationId: testOrganizationId }, 10, 0);
        const duration = performance.now() - startTime;
        responseTimes.push(duration);
      }

      // Sort response times
      responseTimes.sort((a, b) => a - b);

      // Calculate percentiles
      const p50 = responseTimes[Math.floor(responseTimes.length * 0.5)];
      const p90 = responseTimes[Math.floor(responseTimes.length * 0.9)];
      const p95 = responseTimes[Math.floor(responseTimes.length * 0.95)];
      const p99 = responseTimes[Math.floor(responseTimes.length * 0.99)];

      // Assert percentile thresholds
      expect(p50).toBeLessThan(100); // 50th percentile under 100ms
      expect(p90).toBeLessThan(250); // 90th percentile under 250ms
      expect(p95).toBeLessThan(400); // 95th percentile under 400ms
      expect(p99).toBeLessThan(800); // 99th percentile under 800ms

      console.log(`Response time percentiles:
        - P50: ${p50.toFixed(1)}ms
        - P90: ${p90.toFixed(1)}ms
        - P95: ${p95.toFixed(1)}ms
        - P99: ${p99.toFixed(1)}ms`);
    });
  });
});

// Helper function to simulate user session
async function simulateUserSession(
  user: any,
  organizationId: string,
  callService: CallService,
  campaignService: CampaignService
) {
  // Simulate typical user workflow
  const operations = [
    () => callService.listCalls({ organizationId, agentId: user.id }, 10, 0),
    () => callService.getCallStats(organizationId, { agentId: user.id }),
    () => callService.createCall({
      fromNumber: `+${Math.floor(Math.random() * 9000000000) + 1000000000}`,
      toNumber: '+1987654321',
      direction: CallDirection.INBOUND,
      provider: TelephonyProvider.TWILIO,
      organizationId,
      agentId: user.id,
    }),
    () => callService.getActiveCalls(organizationId),
  ];

  // Execute operations with some delay between them
  for (const operation of operations) {
    await operation();
    await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
  }

  return { userId: user.id, success: true };
}