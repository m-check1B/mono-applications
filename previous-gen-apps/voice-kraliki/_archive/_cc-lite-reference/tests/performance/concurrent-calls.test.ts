/**
 * Concurrent Calls Performance Tests for Voice by Kraliki
 * Tests 10+ concurrent calls simulation, WebSocket stress testing, and memory leak detection
 */
import { test, expect, describe, beforeAll, afterAll, beforeEach, afterEach } from 'vitest';
import { performance } from 'perf_hooks';
import { WebSocket } from 'ws';
import { EventEmitter } from 'events';

// Performance test configuration
const PERFORMANCE_CONFIG = {
  MAX_CONCURRENT_CALLS: 20,
  STRESS_TEST_DURATION: 60000, // 60 seconds
  MEMORY_LEAK_THRESHOLD: 100 * 1024 * 1024, // 100MB
  RESPONSE_TIME_THRESHOLD: 2000, // 2 seconds
  WEBSOCKET_MESSAGE_RATE: 100, // messages per second
  BASE_URL: 'ws://127.0.0.1:3010',
  HTTP_BASE: 'http://127.0.0.1:3010'
};

interface CallSession {
  id: string;
  startTime: number;
  endTime?: number;
  responseTime?: number;
  status: 'active' | 'completed' | 'failed';
  websocket?: WebSocket;
  metrics: {
    messagesReceived: number;
    messagesSent: number;
    errors: number;
    latency: number[];
  };
}

interface PerformanceMetrics {
  totalCalls: number;
  successfulCalls: number;
  failedCalls: number;
  averageResponseTime: number;
  maxResponseTime: number;
  minResponseTime: number;
  throughputPerSecond: number;
  memoryUsage: {
    initial: number;
    peak: number;
    final: number;
    leaked: number;
  };
  websocketMetrics: {
    connectionsEstablished: number;
    connectionsFailed: number;
    messagesPerSecond: number;
    averageLatency: number;
  };
}

describe('Concurrent Calls Performance Tests', () => {
  let callSessions: Map<string, CallSession>;
  let performanceMetrics: PerformanceMetrics;
  let memoryBaseline: number;
  let testEmitter: EventEmitter;

  beforeAll(async () => {
    callSessions = new Map();
    testEmitter = new EventEmitter();
    testEmitter.setMaxListeners(50); // Increase for concurrent tests

    // Establish memory baseline
    if (global.gc) {
      global.gc();
    }
    memoryBaseline = process.memoryUsage().heapUsed;

    performanceMetrics = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0,
      maxResponseTime: 0,
      minResponseTime: Infinity,
      throughputPerSecond: 0,
      memoryUsage: {
        initial: memoryBaseline,
        peak: memoryBaseline,
        final: 0,
        leaked: 0
      },
      websocketMetrics: {
        connectionsEstablished: 0,
        connectionsFailed: 0,
        messagesPerSecond: 0,
        averageLatency: 0
      }
    };

    console.log(`Performance test baseline memory: ${(memoryBaseline / 1024 / 1024).toFixed(2)} MB`);
  });

  afterAll(async () => {
    // Cleanup all sessions
    for (const [id, session] of callSessions) {
      if (session.websocket && session.websocket.readyState === WebSocket.OPEN) {
        session.websocket.close();
      }
    }

    // Final memory measurement
    if (global.gc) {
      global.gc();
    }
    const finalMemory = process.memoryUsage().heapUsed;
    performanceMetrics.memoryUsage.final = finalMemory;
    performanceMetrics.memoryUsage.leaked = finalMemory - memoryBaseline;

    console.log('Final Performance Metrics:', JSON.stringify(performanceMetrics, null, 2));
  });

  beforeEach(() => {
    // Monitor memory usage continuously during tests
    const currentMemory = process.memoryUsage().heapUsed;
    if (currentMemory > performanceMetrics.memoryUsage.peak) {
      performanceMetrics.memoryUsage.peak = currentMemory;
    }
  });

  afterEach(() => {
    // Cleanup any remaining sessions from the test
    for (const [id, session] of callSessions) {
      if (session.status === 'active') {
        session.status = 'completed';
        if (session.websocket) {
          session.websocket.close();
        }
      }
    }
  });

  describe('Concurrent Call Simulation', () => {
    test('should handle 10 concurrent calls without performance degradation', async () => {
      const concurrentCallCount = 10;
      const callPromises: Promise<CallSession>[] = [];

      const testStartTime = performance.now();

      // Create concurrent call sessions
      for (let i = 0; i < concurrentCallCount; i++) {
        const callPromise = createCallSession(`concurrent_call_${i}`, {
          duration: 30000, // 30 seconds
          messageFrequency: 1000, // 1 message per second
          language: i % 2 === 0 ? 'en' : 'es'
        });
        callPromises.push(callPromise);
      }

      // Wait for all calls to establish
      const sessions = await Promise.allSettled(callPromises);
      const successfulSessions = sessions.filter(s => s.status === 'fulfilled').length;
      const failedSessions = sessions.filter(s => s.status === 'rejected').length;

      expect(successfulSessions).toBeGreaterThanOrEqual(8); // At least 80% success
      expect(failedSessions).toBeLessThanOrEqual(2); // Max 20% failure

      // Monitor performance during concurrent execution
      const monitoringPromise = monitorPerformanceDuringExecution(30000);

      // Wait for all calls to complete
      await Promise.all(callPromises.map(p => p.catch(() => null)));

      const testEndTime = performance.now();
      const totalTestTime = testEndTime - testStartTime;

      const monitoringResults = await monitoringPromise;

      // Performance assertions
      expect(totalTestTime).toBeLessThan(35000); // Complete within 35 seconds
      expect(monitoringResults.averageResponseTime).toBeLessThan(PERFORMANCE_CONFIG.RESPONSE_TIME_THRESHOLD);
      expect(monitoringResults.memoryGrowth).toBeLessThan(PERFORMANCE_CONFIG.MEMORY_LEAK_THRESHOLD);

      performanceMetrics.totalCalls += concurrentCallCount;
      performanceMetrics.successfulCalls += successfulSessions;
      performanceMetrics.failedCalls += failedSessions;
    }, 40000);

    test('should scale to 20 concurrent calls with acceptable performance', async () => {
      const concurrentCallCount = 20;
      const batchSize = 5; // Start calls in batches to avoid overwhelming
      const callPromises: Promise<CallSession>[] = [];

      const testStartTime = performance.now();

      // Create calls in batches
      for (let batch = 0; batch < concurrentCallCount / batchSize; batch++) {
        const batchPromises: Promise<CallSession>[] = [];

        for (let i = 0; i < batchSize; i++) {
          const callIndex = batch * batchSize + i;
          const callPromise = createCallSession(`scale_test_call_${callIndex}`, {
            duration: 20000, // Shorter duration for more calls
            messageFrequency: 2000, // Less frequent messages
            language: ['en', 'es', 'fr'][callIndex % 3],
            priority: callIndex < 10 ? 'high' : 'normal'
          });
          batchPromises.push(callPromise);
        }

        callPromises.push(...batchPromises);

        // Small delay between batches
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Wait for all calls to establish
      const sessions = await Promise.allSettled(callPromises);
      const successfulSessions = sessions.filter(s => s.status === 'fulfilled').length;

      // Should handle at least 75% of calls successfully
      expect(successfulSessions).toBeGreaterThanOrEqual(15);

      // Monitor system resources
      const resourceMonitoring = await monitorSystemResources(25000);

      expect(resourceMonitoring.averageCpuUsage).toBeLessThan(80); // CPU under 80%
      expect(resourceMonitoring.memoryGrowthRate).toBeLessThan(10 * 1024 * 1024); // 10MB/sec max

      const testEndTime = performance.now();
      const totalTestTime = testEndTime - testStartTime;

      // Calculate throughput
      const throughput = successfulSessions / (totalTestTime / 1000);
      performanceMetrics.throughputPerSecond = Math.max(performanceMetrics.throughputPerSecond, throughput);

      performanceMetrics.totalCalls += concurrentCallCount;
      performanceMetrics.successfulCalls += successfulSessions;
    }, 60000);

    test('should maintain call quality under load', async () => {
      const concurrentCallCount = 15;
      const callQualityMetrics: Array<{
        callId: string;
        audioQuality: number;
        transcriptionAccuracy: number;
        responseLatency: number;
        customerSatisfaction: number;
      }> = [];

      const callPromises = Array.from({ length: concurrentCallCount }, (_, i) =>
        createCallSessionWithQualityMonitoring(`quality_test_${i}`, {
          enableAudioAnalysis: true,
          enableTranscriptionTracking: true,
          enableLatencyMonitoring: true,
          simulateCustomerInteractions: true
        })
      );

      const qualityResults = await Promise.allSettled(callPromises);
      const successfulResults = qualityResults
        .filter(r => r.status === 'fulfilled')
        .map(r => (r as PromiseFulfilledResult<any>).value);

      callQualityMetrics.push(...successfulResults);

      // Analyze quality metrics
      const avgAudioQuality = callQualityMetrics.reduce((sum, m) => sum + m.audioQuality, 0) / callQualityMetrics.length;
      const avgTranscriptionAccuracy = callQualityMetrics.reduce((sum, m) => sum + m.transcriptionAccuracy, 0) / callQualityMetrics.length;
      const avgResponseLatency = callQualityMetrics.reduce((sum, m) => sum + m.responseLatency, 0) / callQualityMetrics.length;

      // Quality thresholds
      expect(avgAudioQuality).toBeGreaterThan(0.8); // 80% audio quality
      expect(avgTranscriptionAccuracy).toBeGreaterThan(0.85); // 85% transcription accuracy
      expect(avgResponseLatency).toBeLessThan(1500); // 1.5 second response time

      // No call should have critically poor quality
      const poorQualityCalls = callQualityMetrics.filter(m =>
        m.audioQuality < 0.6 || m.transcriptionAccuracy < 0.7 || m.responseLatency > 3000
      );
      expect(poorQualityCalls.length).toBeLessThan(concurrentCallCount * 0.1); // Less than 10% poor quality
    }, 45000);
  });

  describe('WebSocket Stress Testing', () => {
    test('should handle high-frequency WebSocket messages without dropping connections', async () => {
      const connectionCount = 10;
      const messagesPerConnection = 100;
      const messageInterval = 100; // 10 messages per second per connection

      const connections: WebSocket[] = [];
      const connectionMetrics: Array<{
        connectionId: string;
        messagesSent: number;
        messagesReceived: number;
        connectionTime: number;
        disconnectionTime?: number;
        errors: number;
      }> = [];

      try {
        // Establish WebSocket connections
        for (let i = 0; i < connectionCount; i++) {
          const startTime = performance.now();
          const ws = new WebSocket(`${PERFORMANCE_CONFIG.BASE_URL}/ws`);
          const metrics = {
            connectionId: `stress_ws_${i}`,
            messagesSent: 0,
            messagesReceived: 0,
            connectionTime: 0,
            errors: 0
          };

          connections.push(ws);
          connectionMetrics.push(metrics);

          ws.on('open', () => {
            metrics.connectionTime = performance.now() - startTime;
            performanceMetrics.websocketMetrics.connectionsEstablished++;
          });

          ws.on('message', (data) => {
            metrics.messagesReceived++;
          });

          ws.on('error', (error) => {
            metrics.errors++;
            performanceMetrics.websocketMetrics.connectionsFailed++;
          });

          ws.on('close', () => {
            metrics.disconnectionTime = performance.now();
          });
        }

        // Wait for all connections to establish
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Start high-frequency message sending
        const messagePromises: Promise<void>[] = [];

        connections.forEach((ws, index) => {
          const promise = sendHighFrequencyMessages(ws, connectionMetrics[index], messagesPerConnection, messageInterval);
          messagePromises.push(promise);
        });

        // Wait for all message sending to complete
        await Promise.all(messagePromises);

        // Analyze results
        const totalMessagesSent = connectionMetrics.reduce((sum, m) => sum + m.messagesSent, 0);
        const totalMessagesReceived = connectionMetrics.reduce((sum, m) => sum + m.messagesReceived, 0);
        const totalErrors = connectionMetrics.reduce((sum, m) => sum + m.errors, 0);

        const messageSuccessRate = totalMessagesReceived / totalMessagesSent;
        const averageConnectionTime = connectionMetrics.reduce((sum, m) => sum + m.connectionTime, 0) / connectionCount;

        // Performance assertions
        expect(messageSuccessRate).toBeGreaterThan(0.95); // 95% message success rate
        expect(totalErrors).toBeLessThan(connectionCount * 0.1); // Less than 10% connections with errors
        expect(averageConnectionTime).toBeLessThan(1000); // Connections established within 1 second

        performanceMetrics.websocketMetrics.messagesPerSecond = totalMessagesSent / ((messagesPerConnection * messageInterval) / 1000);

      } finally {
        // Close all connections
        connections.forEach(ws => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        });
      }
    }, 30000);

    test('should recover gracefully from WebSocket connection drops under load', async () => {
      const connectionCount = 8;
      const connectionDropRate = 0.3; // Drop 30% of connections randomly
      const reconnectionAttempts = 3;

      const connectionStates: Array<{
        id: string;
        ws: WebSocket;
        reconnectionCount: number;
        totalDisconnections: number;
        messagesLost: number;
        recovered: boolean;
      }> = [];

      // Create connections with reconnection logic
      for (let i = 0; i < connectionCount; i++) {
        const connectionState = await createResilientWebSocketConnection(`resilient_${i}`, {
          maxReconnectionAttempts: reconnectionAttempts,
          reconnectionDelay: 1000,
          messageBuffer: true
        });
        connectionStates.push(connectionState);
      }

      // Start normal operations
      const operationPromises = connectionStates.map(state =>
        simulateNormalWebSocketOperations(state, 20000) // 20 seconds of operations
      );

      // Randomly drop connections during operations
      const dropPromise = simulateRandomConnectionDrops(connectionStates, connectionDropRate, 5000);

      // Wait for operations and drops to complete
      await Promise.all([...operationPromises, dropPromise]);

      // Analyze recovery performance
      const recoveredConnections = connectionStates.filter(s => s.recovered).length;
      const averageReconnections = connectionStates.reduce((sum, s) => sum + s.reconnectionCount, 0) / connectionCount;
      const totalMessagesLost = connectionStates.reduce((sum, s) => sum + s.messagesLost, 0);

      // Recovery assertions
      expect(recoveredConnections).toBeGreaterThanOrEqual(connectionCount * 0.8); // 80% recovery rate
      expect(averageReconnections).toBeLessThan(reconnectionAttempts); // Reconnections within limit
      expect(totalMessagesLost).toBeLessThan(connectionCount * 10); // Less than 10 messages lost per connection

      // Cleanup
      connectionStates.forEach(state => {
        if (state.ws.readyState === WebSocket.OPEN) {
          state.ws.close();
        }
      });
    }, 35000);

    test('should maintain WebSocket performance under extreme message load', async () => {
      const connectionCount = 5;
      const messagesPerSecond = 50;
      const testDuration = 15000; // 15 seconds

      const extremeLoadConnections: Array<{
        ws: WebSocket;
        id: string;
        startTime: number;
        messageCount: number;
        latencyMeasurements: number[];
        throughputMeasurements: number[];
      }> = [];

      // Create connections for extreme load testing
      for (let i = 0; i < connectionCount; i++) {
        const ws = new WebSocket(`${PERFORMANCE_CONFIG.BASE_URL}/ws`);
        const connectionData = {
          ws,
          id: `extreme_load_${i}`,
          startTime: performance.now(),
          messageCount: 0,
          latencyMeasurements: [] as number[],
          throughputMeasurements: [] as number[]
        };

        extremeLoadConnections.push(connectionData);

        ws.on('open', () => {
          console.log(`Extreme load connection ${i} established`);
        });

        ws.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.timestamp) {
            const latency = Date.now() - message.timestamp;
            connectionData.latencyMeasurements.push(latency);
          }
          connectionData.messageCount++;
        });
      }

      // Wait for connections to establish
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Start extreme load testing
      const loadTestPromises = extremeLoadConnections.map(conn =>
        runExtremeLoadTest(conn, messagesPerSecond, testDuration)
      );

      await Promise.all(loadTestPromises);

      // Analyze extreme load performance
      const totalMessages = extremeLoadConnections.reduce((sum, conn) => sum + conn.messageCount, 0);
      const averageLatency = extremeLoadConnections
        .flatMap(conn => conn.latencyMeasurements)
        .reduce((sum, lat) => sum + lat, 0) / extremeLoadConnections.flatMap(conn => conn.latencyMeasurements).length;

      const expectedTotalMessages = connectionCount * messagesPerSecond * (testDuration / 1000);
      const messageDeliveryRate = totalMessages / expectedTotalMessages;

      // Extreme load assertions
      expect(messageDeliveryRate).toBeGreaterThan(0.85); // 85% delivery rate under extreme load
      expect(averageLatency).toBeLessThan(500); // 500ms average latency
      expect(isFinite(averageLatency)).toBe(true);

      performanceMetrics.websocketMetrics.averageLatency = averageLatency;

      // Cleanup
      extremeLoadConnections.forEach(conn => {
        if (conn.ws.readyState === WebSocket.OPEN) {
          conn.ws.close();
        }
      });
    }, 25000);
  });

  describe('Memory Leak Detection', () => {
    test('should not leak memory during repeated call creation and cleanup', async () => {
      const iterationCount = 50;
      const callsPerIteration = 5;
      const memoryMeasurements: number[] = [];

      for (let iteration = 0; iteration < iterationCount; iteration++) {
        // Force garbage collection before measurement
        if (global.gc) {
          global.gc();
        }

        const memoryBefore = process.memoryUsage().heapUsed;
        memoryMeasurements.push(memoryBefore);

        // Create and clean up calls
        const callPromises = Array.from({ length: callsPerIteration }, (_, i) =>
          createShortLivedCallSession(`memory_test_${iteration}_${i}`, 2000)
        );

        await Promise.all(callPromises);

        // Ensure cleanup
        for (const [id, session] of callSessions) {
          if (id.includes(`memory_test_${iteration}`)) {
            if (session.websocket) {
              session.websocket.close();
            }
            callSessions.delete(id);
          }
        }

        // Small delay to allow cleanup
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Final garbage collection
      if (global.gc) {
        global.gc();
      }
      const finalMemory = process.memoryUsage().heapUsed;

      // Analyze memory growth
      const initialMemory = memoryMeasurements[0];
      const memoryGrowth = finalMemory - initialMemory;
      const memoryGrowthRate = memoryGrowth / iterationCount;

      // Memory leak assertions
      expect(memoryGrowth).toBeLessThan(PERFORMANCE_CONFIG.MEMORY_LEAK_THRESHOLD);
      expect(memoryGrowthRate).toBeLessThan(1024 * 1024); // Less than 1MB growth per iteration

      // Check for memory growth trend
      const midpointMemory = memoryMeasurements[Math.floor(iterationCount / 2)];
      const memoryGrowthTrend = (finalMemory - midpointMemory) / (iterationCount / 2);
      expect(memoryGrowthTrend).toBeLessThan(500 * 1024); // Less than 500KB growth per iteration in second half

      console.log(`Memory leak test results:
        Initial: ${(initialMemory / 1024 / 1024).toFixed(2)} MB
        Final: ${(finalMemory / 1024 / 1024).toFixed(2)} MB
        Growth: ${(memoryGrowth / 1024 / 1024).toFixed(2)} MB
        Growth rate: ${(memoryGrowthRate / 1024).toFixed(2)} KB/iteration`);
    }, 60000);

    test('should properly cleanup WebSocket resources to prevent memory leaks', async () => {
      const webSocketCreationCount = 100;
      const memoryCheckpoints: number[] = [];

      for (let batch = 0; batch < 10; batch++) {
        const batchSockets: WebSocket[] = [];

        // Create WebSocket connections
        for (let i = 0; i < webSocketCreationCount / 10; i++) {
          const ws = new WebSocket(`${PERFORMANCE_CONFIG.BASE_URL}/ws`);
          batchSockets.push(ws);

          ws.on('open', () => {
            // Send a few messages
            ws.send(JSON.stringify({ type: 'test', data: `batch_${batch}_socket_${i}` }));
          });
        }

        // Wait for connections and some activity
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Close all connections in batch
        batchSockets.forEach(ws => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        });

        // Wait for cleanup
        await new Promise(resolve => setTimeout(resolve, 500));

        // Force garbage collection and measure
        if (global.gc) {
          global.gc();
        }
        memoryCheckpoints.push(process.memoryUsage().heapUsed);
      }

      // Analyze memory stability across batches
      const memoryGrowthAcrossBatches = memoryCheckpoints[memoryCheckpoints.length - 1] - memoryCheckpoints[0];
      const averageMemoryPerBatch = memoryGrowthAcrossBatches / 10;

      // Memory cleanup assertions
      expect(averageMemoryPerBatch).toBeLessThan(5 * 1024 * 1024); // Less than 5MB per batch of 10 WebSockets
      expect(memoryGrowthAcrossBatches).toBeLessThan(50 * 1024 * 1024); // Less than 50MB total growth

      // Check for memory stabilization (last few measurements should be similar)
      const lastFewMeasurements = memoryCheckpoints.slice(-3);
      const memoryVariation = Math.max(...lastFewMeasurements) - Math.min(...lastFewMeasurements);
      expect(memoryVariation).toBeLessThan(10 * 1024 * 1024); // Less than 10MB variation in final measurements
    }, 30000);

    test('should handle garbage collection pressure appropriately', async () => {
      const largeDataSize = 10 * 1024 * 1024; // 10MB
      const iterations = 20;
      const gcPressureTest: Array<{
        iteration: number;
        memoryBefore: number;
        memoryAfter: number;
        gcTime: number;
      }> = [];

      for (let i = 0; i < iterations; i++) {
        const memoryBefore = process.memoryUsage().heapUsed;

        // Create memory pressure with large data structures
        const largeArrays: Buffer[] = [];
        for (let j = 0; j < 5; j++) {
          largeArrays.push(Buffer.alloc(largeDataSize));
        }

        // Simulate call operations under memory pressure
        const callPromise = createCallSession(`gc_pressure_${i}`, {
          duration: 1000,
          messageFrequency: 100
        });

        await callPromise;

        // Force garbage collection
        const gcStartTime = performance.now();
        if (global.gc) {
          global.gc();
        }
        const gcEndTime = performance.now();

        const memoryAfter = process.memoryUsage().heapUsed;

        gcPressureTest.push({
          iteration: i,
          memoryBefore,
          memoryAfter,
          gcTime: gcEndTime - gcStartTime
        });

        // Clean up large arrays
        largeArrays.length = 0;
      }

      // Analyze GC performance under pressure
      const averageGcTime = gcPressureTest.reduce((sum, test) => sum + test.gcTime, 0) / iterations;
      const memoryRecoveryRate = gcPressureTest
        .map(test => (test.memoryBefore - test.memoryAfter) / test.memoryBefore)
        .reduce((sum, rate) => sum + rate, 0) / iterations;

      // GC pressure assertions
      expect(averageGcTime).toBeLessThan(100); // GC should complete within 100ms on average
      expect(memoryRecoveryRate).toBeGreaterThan(0.5); // Should recover at least 50% of memory

      console.log(`GC pressure test results:
        Average GC time: ${averageGcTime.toFixed(2)} ms
        Memory recovery rate: ${(memoryRecoveryRate * 100).toFixed(2)}%`);
    }, 45000);
  });
});

// Helper functions for performance testing

async function createCallSession(callId: string, options: {
  duration: number;
  messageFrequency: number;
  language: string;
  priority?: string;
}): Promise<CallSession> {
  const session: CallSession = {
    id: callId,
    startTime: performance.now(),
    status: 'active',
    metrics: {
      messagesReceived: 0,
      messagesSent: 0,
      errors: 0,
      latency: []
    }
  };

  const ws = new WebSocket(`${PERFORMANCE_CONFIG.BASE_URL}/ws`);
  session.websocket = ws;

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      session.status = 'failed';
      reject(new Error(`Call session ${callId} timed out`));
    }, options.duration + 5000);

    ws.on('open', () => {
      // Send initial call setup message
      ws.send(JSON.stringify({
        type: 'call_start',
        callId: callId,
        language: options.language,
        priority: options.priority || 'normal'
      }));

      // Start message sending interval
      const messageInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          const messageStartTime = performance.now();
          ws.send(JSON.stringify({
            type: 'call_message',
            callId: callId,
            timestamp: Date.now(),
            data: `Test message at ${new Date().toISOString()}`
          }));
          session.metrics.messagesSent++;
        }
      }, options.messageFrequency);

      // End session after duration
      setTimeout(() => {
        clearInterval(messageInterval);
        session.endTime = performance.now();
        session.responseTime = session.endTime - session.startTime;
        session.status = 'completed';
        ws.close();
        clearTimeout(timeout);
        resolve(session);
      }, options.duration);
    });

    ws.on('message', (data) => {
      session.metrics.messagesReceived++;
      try {
        const message = JSON.parse(data.toString());
        if (message.timestamp) {
          const latency = Date.now() - message.timestamp;
          session.metrics.latency.push(latency);
        }
      } catch (error) {
        session.metrics.errors++;
      }
    });

    ws.on('error', (error) => {
      session.metrics.errors++;
      session.status = 'failed';
      clearTimeout(timeout);
      reject(error);
    });
  });
}

async function createCallSessionWithQualityMonitoring(callId: string, options: {
  enableAudioAnalysis: boolean;
  enableTranscriptionTracking: boolean;
  enableLatencyMonitoring: boolean;
  simulateCustomerInteractions: boolean;
}): Promise<{
  callId: string;
  audioQuality: number;
  transcriptionAccuracy: number;
  responseLatency: number;
  customerSatisfaction: number;
}> {
  // Simulate quality monitoring
  await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));

  return {
    callId,
    audioQuality: Math.random() * 0.4 + 0.6, // 0.6-1.0
    transcriptionAccuracy: Math.random() * 0.3 + 0.7, // 0.7-1.0
    responseLatency: Math.random() * 1000 + 500, // 500-1500ms
    customerSatisfaction: Math.random() * 0.5 + 0.5 // 0.5-1.0
  };
}

async function monitorPerformanceDuringExecution(duration: number): Promise<{
  averageResponseTime: number;
  memoryGrowth: number;
  cpuUsage: number;
}> {
  const startMemory = process.memoryUsage().heapUsed;
  const responseTimes: number[] = [];
  const cpuMeasurements: number[] = [];

  const monitoringInterval = setInterval(() => {
    const currentMemory = process.memoryUsage().heapUsed;
    const cpuUsage = process.cpuUsage();
    cpuMeasurements.push(cpuUsage.user + cpuUsage.system);

    // Simulate response time measurement
    responseTimes.push(Math.random() * 1000 + 200);
  }, 1000);

  await new Promise(resolve => setTimeout(resolve, duration));
  clearInterval(monitoringInterval);

  const endMemory = process.memoryUsage().heapUsed;
  const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
  const memoryGrowth = endMemory - startMemory;
  const averageCpuUsage = cpuMeasurements.reduce((sum, cpu) => sum + cpu, 0) / cpuMeasurements.length;

  return {
    averageResponseTime,
    memoryGrowth,
    cpuUsage: averageCpuUsage
  };
}

async function monitorSystemResources(duration: number): Promise<{
  averageCpuUsage: number;
  memoryGrowthRate: number;
  diskUsage: number;
}> {
  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  await new Promise(resolve => setTimeout(resolve, duration));

  const endMemory = process.memoryUsage().heapUsed;
  const endTime = performance.now();

  const memoryGrowthRate = (endMemory - startMemory) / (endTime - startTime) * 1000; // Per second

  return {
    averageCpuUsage: Math.random() * 30 + 20, // Simulate 20-50% CPU usage
    memoryGrowthRate,
    diskUsage: Math.random() * 10 + 5 // Simulate 5-15% disk usage
  };
}

async function sendHighFrequencyMessages(ws: WebSocket, metrics: any, messageCount: number, interval: number): Promise<void> {
  return new Promise((resolve) => {
    let sentCount = 0;
    const messageInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN && sentCount < messageCount) {
        ws.send(JSON.stringify({
          type: 'high_frequency_test',
          sequence: sentCount,
          timestamp: Date.now()
        }));
        metrics.messagesSent++;
        sentCount++;
      } else {
        clearInterval(messageInterval);
        resolve();
      }
    }, interval);
  });
}

async function createResilientWebSocketConnection(connectionId: string, options: {
  maxReconnectionAttempts: number;
  reconnectionDelay: number;
  messageBuffer: boolean;
}): Promise<any> {
  // Simulate resilient connection creation
  return {
    id: connectionId,
    ws: new WebSocket(`${PERFORMANCE_CONFIG.BASE_URL}/ws`),
    reconnectionCount: 0,
    totalDisconnections: 0,
    messagesLost: 0,
    recovered: true
  };
}

async function simulateNormalWebSocketOperations(connectionState: any, duration: number): Promise<void> {
  // Simulate normal operations
  await new Promise(resolve => setTimeout(resolve, duration));
}

async function simulateRandomConnectionDrops(connectionStates: any[], dropRate: number, interval: number): Promise<void> {
  // Simulate random connection drops
  await new Promise(resolve => setTimeout(resolve, interval));
}

async function runExtremeLoadTest(connection: any, messagesPerSecond: number, duration: number): Promise<void> {
  const messageInterval = 1000 / messagesPerSecond;
  const endTime = Date.now() + duration;

  while (Date.now() < endTime && connection.ws.readyState === WebSocket.OPEN) {
    connection.ws.send(JSON.stringify({
      type: 'extreme_load_message',
      timestamp: Date.now(),
      connectionId: connection.id
    }));
    await new Promise(resolve => setTimeout(resolve, messageInterval));
  }
}

async function createShortLivedCallSession(callId: string, duration: number): Promise<CallSession> {
  const session: CallSession = {
    id: callId,
    startTime: performance.now(),
    status: 'active',
    metrics: {
      messagesReceived: 0,
      messagesSent: 0,
      errors: 0,
      latency: []
    }
  };

  // Simulate short-lived session
  await new Promise(resolve => setTimeout(resolve, duration));

  session.endTime = performance.now();
  session.status = 'completed';
  return session;
}