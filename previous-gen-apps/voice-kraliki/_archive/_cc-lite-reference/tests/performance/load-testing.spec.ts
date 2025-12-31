import { describe, it, expect, beforeEach, vi } from 'vitest';
import { testDb, createTestUser, createTestCall, createTestCampaign, measurePerformance } from '../setup';
import { createToken } from '@unified/auth-core';
import { appRouter } from '../../server/trpc/app.router';
import { createContext } from '../../server/trpc';
import WebSocket from 'ws';

const PERFORMANCE_THRESHOLDS = {
  API_RESPONSE_TIME: 500, // ms
  DATABASE_QUERY_TIME: 100, // ms
  CONCURRENT_USERS: 50,
  MEMORY_LIMIT: 512, // MB
  CPU_USAGE: 80 // %
};

describe('Performance and Load Testing', () => {
  let testUsers: any[] = [];
  let testCampaign: any;

  beforeEach(async () => {
    // Clean database
    await testDb.call.deleteMany();
    await testDb.campaign.deleteMany();
    await testDb.user.deleteMany();
    await testDb.organization.deleteMany();

    // Create test campaign
    testCampaign = await createTestCampaign({
      name: 'Load Test Campaign',
      type: 'OUTBOUND'
    });

    // Create test users for concurrent testing
    testUsers = [];
    for (let i = 0; i < 20; i++) {
      const user = await createTestUser({
        role: 'AGENT',
        email: `loadtest${i}@example.com`,
        organizationId: testCampaign.organizationId
      });
      testUsers.push(user);
    }
  });

  describe('API Performance Tests', () => {
    it('should handle concurrent API requests within performance thresholds', async () => {
      const concurrentRequests = 25;
      const requests = [];

      for (let i = 0; i < concurrentRequests; i++) {
        const user = testUsers[i % testUsers.length];
        const token = await createToken({
          userId: user.id,
          email: user.email,
          metadata: { role: 'AGENT' }
        });

        const requestPromise = measurePerformance(async () => {
          const ctx = await createContext({
            req: { 
              headers: { authorization: `Bearer ${token.token}` },
              ip: '127.0.0.1',
              user 
            },
            reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
          });
          const caller = appRouter.createCaller(ctx);
          
          return await caller.dashboard.getStats();
        });

        requests.push(requestPromise);
      }

      const results = await Promise.all(requests);
      
      // Check response times
      const averageResponseTime = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
      const maxResponseTime = Math.max(...results.map(r => r.duration));
      
      expect(averageResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.API_RESPONSE_TIME);
      expect(maxResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.API_RESPONSE_TIME * 2);
      
      // All requests should succeed
      results.forEach(result => {
        expect(result.result).toBeDefined();
        expect(result.result.totalCalls).toBeTypeOf('number');
      });
    });

    it('should handle large paginated queries efficiently', async () => {
      const user = testUsers[0];
      const token = await createToken({
        userId: user.id,
        email: user.email,
        metadata: { role: 'SUPERVISOR' }
      });

      // Create large dataset
      const callPromises = [];
      for (let i = 0; i < 500; i++) {
        callPromises.push(createTestCall({
          phoneNumber: `+123456${i.toString().padStart(4, '0')}`,
          agentId: testUsers[i % testUsers.length].id,
          campaignId: testCampaign.id,
          status: 'COMPLETED'
        }));
      }
      await Promise.all(callPromises);

      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);

      // Test different page sizes
      const pageSizes = [10, 50, 100];
      
      for (const pageSize of pageSizes) {
        const result = await measurePerformance(async () => {
          return await caller.callApi.getCalls({ 
            page: 1, 
            limit: pageSize 
          });
        });

        expect(result.duration).toBeLessThan(PERFORMANCE_THRESHOLDS.DATABASE_QUERY_TIME * 2);
        expect(result.result.calls).toHaveLength(pageSize);
        expect(result.result.totalCount).toBe(500);
      }
    });

    it('should maintain performance with complex analytics queries', async () => {
      const supervisorUser = await createTestUser({ 
        role: 'SUPERVISOR',
        organizationId: testCampaign.organizationId
      });
      const token = await createToken({
        userId: supervisorUser.id,
        email: supervisorUser.email,
        metadata: { role: 'SUPERVISOR' }
      });

      // Create varied test data for analytics
      const now = new Date();
      const callData = [];
      
      for (let i = 0; i < 100; i++) {
        const startTime = new Date(now.getTime() - (i * 60000)); // Spread over last 100 minutes
        callData.push(createTestCall({
          phoneNumber: `+123456${i.toString().padStart(3, '0')}`,
          agentId: testUsers[i % testUsers.length].id,
          campaignId: testCampaign.id,
          status: 'COMPLETED',
          startTime,
          endTime: new Date(startTime.getTime() + 180000), // 3 minute calls
          duration: 180
        }));
      }
      
      await Promise.all(callData);

      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user: supervisorUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);

      // Test complex analytics queries
      const analyticsTests = [
        () => caller.analytics.getCallVolumeAnalytics({
          startDate: new Date(now.getTime() - 24 * 60 * 60 * 1000),
          endDate: now,
          granularity: 'hourly'
        }),
        () => caller.analytics.getPerformanceAnalytics({
          startDate: new Date(now.getTime() - 24 * 60 * 60 * 1000),
          endDate: now
        }),
        () => caller.analytics.getAgentPerformanceReport({
          startDate: new Date(now.getTime() - 24 * 60 * 60 * 1000),
          endDate: now,
          agentIds: testUsers.slice(0, 10).map(u => u.id)
        })
      ];

      for (const analyticsTest of analyticsTests) {
        const result = await measurePerformance(analyticsTest);
        
        expect(result.duration).toBeLessThan(PERFORMANCE_THRESHOLDS.DATABASE_QUERY_TIME * 5);
        expect(result.result).toBeDefined();
      }
    });
  });

  describe('Database Performance Tests', () => {
    it('should handle concurrent database operations efficiently', async () => {
      const concurrentOperations = 50;
      const operations = [];

      // Mix of read and write operations
      for (let i = 0; i < concurrentOperations; i++) {
        if (i % 3 === 0) {
          // Write operation - create call
          operations.push(measurePerformance(async () => {
            return await createTestCall({
              phoneNumber: `+987654${i.toString().padStart(3, '0')}`,
              agentId: testUsers[i % testUsers.length].id,
              campaignId: testCampaign.id,
              status: 'ACTIVE'
            });
          }));
        } else {
          // Read operation - query calls
          operations.push(measurePerformance(async () => {
            return await testDb.call.findMany({
              where: { 
                campaignId: testCampaign.id,
                status: 'ACTIVE'
              },
              take: 10
            });
          }));
        }
      }

      const results = await Promise.all(operations);
      
      const averageDbTime = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
      const maxDbTime = Math.max(...results.map(r => r.duration));
      
      expect(averageDbTime).toBeLessThan(PERFORMANCE_THRESHOLDS.DATABASE_QUERY_TIME);
      expect(maxDbTime).toBeLessThan(PERFORMANCE_THRESHOLDS.DATABASE_QUERY_TIME * 3);
    });

    it('should optimize queries with proper indexing', async () => {
      // Create large dataset to test query performance
      const largeDataSet = [];
      for (let i = 0; i < 1000; i++) {
        largeDataSet.push(createTestCall({
          phoneNumber: `+555${i.toString().padStart(7, '0')}`,
          agentId: testUsers[i % testUsers.length].id,
          campaignId: testCampaign.id,
          status: ['ACTIVE', 'COMPLETED', 'FAILED'][i % 3] as any,
          startTime: new Date(Date.now() - (i * 1000))
        }));
      }
      await Promise.all(largeDataSet);

      // Test indexed queries
      const indexedQueries = [
        // Query by agent ID (should be indexed)
        () => testDb.call.findMany({
          where: { agentId: testUsers[0].id },
          take: 10
        }),
        // Query by campaign ID (should be indexed)
        () => testDb.call.findMany({
          where: { campaignId: testCampaign.id },
          orderBy: { startTime: 'desc' },
          take: 10
        }),
        // Query by status (should be indexed)
        () => testDb.call.findMany({
          where: { status: 'ACTIVE' },
          take: 10
        }),
        // Query by date range (should be indexed)
        () => testDb.call.findMany({
          where: {
            startTime: {
              gte: new Date(Date.now() - 60 * 60 * 1000) // Last hour
            }
          },
          take: 10
        })
      ];

      for (const query of indexedQueries) {
        const result = await measurePerformance(query);
        
        expect(result.duration).toBeLessThan(PERFORMANCE_THRESHOLDS.DATABASE_QUERY_TIME);
        expect(result.result).toBeDefined();
      }
    });
  });

  describe('WebSocket Performance Tests', () => {
    it('should handle concurrent WebSocket connections', async () => {
      const connectionCount = 20;
      const connections: WebSocket[] = [];
      const connectionPromises = [];

      // Create concurrent WebSocket connections
      for (let i = 0; i < connectionCount; i++) {
        const user = testUsers[i % testUsers.length];
        const token = await createToken({
          userId: user.id,
          email: user.email,
          metadata: { role: 'AGENT' }
        });

        const connectionPromise = new Promise((resolve, reject) => {
          const startTime = Date.now();
          const ws = new WebSocket('ws://localhost:3001/ws', {
            headers: {
              'Authorization': `Bearer ${token.token}`,
              'Cookie': `vd_session=${token.token}`
            }
          });

          ws.on('open', () => {
            const connectionTime = Date.now() - startTime;
            connections.push(ws);
            resolve({ connectionTime, success: true });
          });

          ws.on('error', () => {
            resolve({ connectionTime: Date.now() - startTime, success: false });
          });

          setTimeout(() => {
            resolve({ connectionTime: Date.now() - startTime, success: false, timeout: true });
          }, 5000);
        });

        connectionPromises.push(connectionPromise);
      }

      const results: any[] = await Promise.all(connectionPromises);
      
      const successfulConnections = results.filter(r => r.success).length;
      const averageConnectionTime = results.reduce((sum, r) => sum + r.connectionTime, 0) / results.length;
      
      expect(successfulConnections).toBeGreaterThanOrEqual(connectionCount * 0.9); // 90% success rate
      expect(averageConnectionTime).toBeLessThan(1000); // Under 1 second
      
      // Clean up connections
      connections.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    });

    it('should handle high-frequency message broadcasting', async () => {
      const user = testUsers[0];
      const token = await createToken({
        userId: user.id,
        email: user.email,
        metadata: { role: 'SUPERVISOR' }
      });

      const messageCount = 100;
      const receivedMessages: any[] = [];
      
      const messageTest = new Promise((resolve, reject) => {
        const ws = new WebSocket('ws://localhost:3001/ws', {
          headers: {
            'Authorization': `Bearer ${token.token}`,
            'Cookie': `vd_session=${token.token}`
          }
        });

        const startTime = Date.now();

        ws.on('open', () => {
          // Send rapid messages
          for (let i = 0; i < messageCount; i++) {
            ws.send(JSON.stringify({
              type: 'ping',
              payload: { messageId: i, timestamp: Date.now() }
            }));
          }
        });

        ws.on('message', (data) => {
          const message = JSON.parse(data.toString());
          receivedMessages.push(message);
          
          if (receivedMessages.length >= messageCount) {
            const totalTime = Date.now() - startTime;
            ws.close();
            resolve({ totalTime, messageCount: receivedMessages.length });
          }
        });

        ws.on('error', reject);
        
        setTimeout(() => {
          ws.close();
          resolve({ 
            totalTime: Date.now() - startTime, 
            messageCount: receivedMessages.length,
            timeout: true 
          });
        }, 10000);
      });

      const result: any = await messageTest;
      
      expect(result.messageCount).toBeGreaterThanOrEqual(messageCount * 0.95); // 95% message delivery
      expect(result.totalTime).toBeLessThan(5000); // Under 5 seconds for 100 messages
    });
  });

  describe('Memory and Resource Usage Tests', () => {
    it('should manage memory efficiently under load', async () => {
      const initialMemory = process.memoryUsage();
      
      // Simulate heavy load
      const heavyOperations = [];
      for (let i = 0; i < 100; i++) {
        heavyOperations.push(
          (async () => {
            // Create and process data
            const calls = await Promise.all(
              Array.from({ length: 10 }, (_, j) => 
                createTestCall({
                  phoneNumber: `+${i}${j.toString().padStart(9, '0')}`,
                  agentId: testUsers[j % testUsers.length].id,
                  campaignId: testCampaign.id
                })
              )
            );
            
            // Process the calls (simulate business logic)
            return calls.map(call => ({
              ...call,
              processed: true,
              timestamp: new Date().toISOString()
            }));
          })()
        );
      }

      await Promise.all(heavyOperations);
      
      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }
      
      const finalMemory = process.memoryUsage();
      const memoryGrowth = (finalMemory.heapUsed - initialMemory.heapUsed) / 1024 / 1024; // MB
      
      expect(memoryGrowth).toBeLessThan(PERFORMANCE_THRESHOLDS.MEMORY_LIMIT);
    });

    it('should handle cleanup of resources properly', async () => {
      let activeConnections = 0;
      const maxConnections = 10;
      const connectionCycles = 5;
      
      for (let cycle = 0; cycle < connectionCycles; cycle++) {
        const connections: WebSocket[] = [];
        
        // Create connections
        for (let i = 0; i < maxConnections; i++) {
          const user = testUsers[i % testUsers.length];
          const token = await createToken({
            userId: user.id,
            email: user.email,
            metadata: { role: 'AGENT' }
          });
          
          const ws = new WebSocket('ws://localhost:3001/ws', {
            headers: {
              'Authorization': `Bearer ${token.token}`,
              'Cookie': `vd_session=${token.token}`
            }
          });
          
          connections.push(ws);
          activeConnections++;
        }
        
        // Wait for connections to establish
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Close all connections
        connections.forEach(ws => {
          if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
            ws.close();
            activeConnections--;
          }
        });
        
        // Wait for cleanup
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      expect(activeConnections).toBe(0);
    });
  });

  describe('Stress Testing', () => {
    it('should maintain stability under extreme load', async () => {
      const extremeLoad = 100;
      const stressOperations = [];
      const errors: any[] = [];
      const successes: any[] = [];
      
      for (let i = 0; i < extremeLoad; i++) {
        const user = testUsers[i % testUsers.length];
        const token = await createToken({
          userId: user.id,
          email: user.email,
          metadata: { role: 'AGENT' }
        });
        
        const operation = (async () => {
          try {
            const ctx = await createContext({
              req: { 
                headers: { authorization: `Bearer ${token.token}` },
                ip: '127.0.0.1',
                user 
              },
              reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
            });
            const caller = appRouter.createCaller(ctx);
            
            // Mix of operations
            const operations = [
              () => caller.dashboard.getStats(),
              () => caller.callApi.getCalls({ page: 1, limit: 10 }),
              () => caller.agent.updateStatus({ status: 'AVAILABLE' })
            ];
            
            const randomOp = operations[i % operations.length];
            const result = await randomOp();
            
            successes.push({ operation: i, result });
          } catch (error) {
            errors.push({ operation: i, error: error.message });
          }
        })();
        
        stressOperations.push(operation);
      }
      
      await Promise.all(stressOperations);
      
      const successRate = successes.length / (successes.length + errors.length);
      const errorRate = errors.length / (successes.length + errors.length);
      
      expect(successRate).toBeGreaterThan(0.9); // 90% success rate under stress
      expect(errorRate).toBeLessThan(0.1); // Less than 10% error rate
    });
  });
});
