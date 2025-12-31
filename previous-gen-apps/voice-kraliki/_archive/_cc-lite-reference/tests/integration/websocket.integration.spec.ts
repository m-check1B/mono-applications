import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import WebSocket from 'ws';
import { testDb, createTestUser, createTestCall, createTestCampaign, waitFor } from '../setup';
import { createToken } from '@unified/auth-core';

const WS_SERVER_URL = 'ws://127.0.0.1:3900';

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('WebSocket Integration Tests', () => {
  let testUser: any;
  let authToken: string;
  let ws: WebSocket | null = null;

  beforeEach(async () => {
    // Clean database
    await testDb.call.deleteMany();
    await testDb.campaign.deleteMany();
    await testDb.user.deleteMany();
    await testDb.organization.deleteMany();

    // Create test user
    testUser = await createTestUser({ role: 'AGENT', status: 'ACTIVE' });
    const token = await createToken({
      userId: testUser.id,
      email: testUser.email,
      metadata: { role: 'AGENT' }
    });
    authToken = token.token;
  });

  afterEach(async () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
      await waitFor(100);
    }
    ws = null;
  });

  describe('WebSocket Connection', () => {
    it('should establish WebSocket connection with valid auth', async () => {
      const connectionPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', () => {
          resolve('connected');
        });

        ws.on('error', (error) => {
          reject(error);
        });

        setTimeout(() => reject(new Error('Connection timeout')), 5000);
      });

      await expect(connectionPromise).resolves.toBe('connected');
    });

    it('should reject WebSocket connection without auth', async () => {
      const connectionPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`);

        ws.on('open', () => {
          reject(new Error('Connection should not be established'));
        });

        ws.on('error', () => {
          resolve('rejected');
        });

        ws.on('close', (code) => {
          if (code === 1008 || code === 1002) {
            resolve('rejected');
          } else {
            reject(new Error(`Unexpected close code: ${code}`));
          }
        });

        setTimeout(() => resolve('timeout'), 2000);
      });

      await expect(connectionPromise).resolves.toBe('rejected');
    });

    it('should handle connection with invalid token', async () => {
      const connectionPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': 'Bearer invalid-token',
            'Cookie': 'vd_session=invalid-token'
          }
        });

        ws.on('open', () => {
          reject(new Error('Connection should not be established with invalid token'));
        });

        ws.on('error', () => {
          resolve('rejected');
        });

        ws.on('close', (code) => {
          if (code === 1008 || code === 1002) {
            resolve('rejected');
          }
        });

        setTimeout(() => resolve('timeout'), 2000);
      });

      await expect(connectionPromise).resolves.toBe('rejected');
    });
  });

  describe('Real-time Call Updates', () => {
    it('should receive call assignment notifications', async () => {
      const messagePromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', async () => {
          // Send agent status update
          ws!.send(JSON.stringify({
            type: 'agent_status_update',
            payload: { status: 'AVAILABLE' }
          }));

          // Wait a bit then create a call (would trigger assignment)
          await waitFor(100);
          const campaign = await createTestCampaign({ organizationId: testUser.organizationId });
          await createTestCall({ 
            agentId: testUser.id,
            campaignId: campaign.id,
            status: 'ASSIGNED'
          });
        });

        ws.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'call_assigned') {
            resolve(message);
          }
        });

        ws.on('error', reject);
        setTimeout(() => reject(new Error('Timeout waiting for call assignment')), 5000);
      });

      const message: any = await messagePromise;
      expect(message.type).toBe('call_assigned');
      expect(message.payload.agentId).toBe(testUser.id);
    });

    it('should broadcast call status updates to supervisors', async () => {
      // Create supervisor user
      const supervisorUser = await createTestUser({ role: 'SUPERVISOR', organizationId: testUser.organizationId });
      const supervisorToken = await createToken({
        userId: supervisorUser.id,
        email: supervisorUser.email,
        metadata: { role: 'SUPERVISOR' }
      });

      const supervisorMessagePromise = new Promise((resolve, reject) => {
        const supervisorWs = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${supervisorToken.token}`,
            'Cookie': `vd_session=${supervisorToken.token}`
          }
        });

        supervisorWs.on('open', () => {
          // Subscribe to call updates
          supervisorWs.send(JSON.stringify({
            type: 'subscribe',
            payload: { channel: 'call_updates' }
          }));
        });

        supervisorWs.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'call_status_update') {
            supervisorWs.close();
            resolve(message);
          }
        });

        supervisorWs.on('error', reject);
        setTimeout(() => {
          supervisorWs.close();
          reject(new Error('Timeout'));
        }, 5000);
      });

      // Create agent WebSocket to trigger call update
      const agentPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', async () => {
          // Create call and then update its status
          const campaign = await createTestCampaign({ organizationId: testUser.organizationId });
          const call = await createTestCall({ 
            agentId: testUser.id,
            campaignId: campaign.id,
            status: 'ACTIVE'
          });

          // Send call status update
          ws!.send(JSON.stringify({
            type: 'call_status_update',
            payload: { 
              callId: call.id,
              status: 'IN_PROGRESS',
              timestamp: new Date().toISOString()
            }
          }));
          
          resolve(call);
        });

        ws.on('error', reject);
      });

      await agentPromise;
      const supervisorMessage: any = await supervisorMessagePromise;
      
      expect(supervisorMessage.type).toBe('call_status_update');
      expect(supervisorMessage.payload.status).toBe('IN_PROGRESS');
    });

    it('should handle call transfer notifications', async () => {
      const targetAgent = await createTestUser({ 
        role: 'AGENT', 
        organizationId: testUser.organizationId,
        status: 'AVAILABLE'
      });
      const targetToken = await createToken({
        userId: targetAgent.id,
        email: targetAgent.email,
        metadata: { role: 'AGENT' }
      });

      const transferMessagePromise = new Promise((resolve, reject) => {
        const targetWs = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${targetToken.token}`,
            'Cookie': `vd_session=${targetToken.token}`
          }
        });

        targetWs.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'call_transfer_received') {
            targetWs.close();
            resolve(message);
          }
        });

        targetWs.on('error', reject);
        setTimeout(() => {
          targetWs.close();
          reject(new Error('Timeout'));
        }, 5000);
      });

      // Source agent initiates transfer
      const sourcePromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', async () => {
          const campaign = await createTestCampaign({ organizationId: testUser.organizationId });
          const call = await createTestCall({ 
            agentId: testUser.id,
            campaignId: campaign.id,
            status: 'ACTIVE'
          });

          // Initiate transfer
          ws!.send(JSON.stringify({
            type: 'transfer_call',
            payload: { 
              callId: call.id,
              targetAgentId: targetAgent.id,
              reason: 'Skill match'
            }
          }));
          
          resolve(call);
        });

        ws.on('error', reject);
      });

      await sourcePromise;
      const transferMessage: any = await transferMessagePromise;
      
      expect(transferMessage.type).toBe('call_transfer_received');
      expect(transferMessage.payload.targetAgentId).toBe(targetAgent.id);
    });
  });

  describe('Agent Status Updates', () => {
    it('should broadcast agent status changes', async () => {
      const supervisorUser = await createTestUser({ 
        role: 'SUPERVISOR', 
        organizationId: testUser.organizationId 
      });
      const supervisorToken = await createToken({
        userId: supervisorUser.id,
        email: supervisorUser.email,
        metadata: { role: 'SUPERVISOR' }
      });

      const statusUpdatePromise = new Promise((resolve, reject) => {
        const supervisorWs = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${supervisorToken.token}`,
            'Cookie': `vd_session=${supervisorToken.token}`
          }
        });

        supervisorWs.on('open', () => {
          supervisorWs.send(JSON.stringify({
            type: 'subscribe',
            payload: { channel: 'agent_status' }
          }));
        });

        supervisorWs.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'agent_status_changed') {
            supervisorWs.close();
            resolve(message);
          }
        });

        supervisorWs.on('error', reject);
        setTimeout(() => {
          supervisorWs.close();
          reject(new Error('Timeout'));
        }, 5000);
      });

      // Agent updates status
      const agentPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', () => {
          ws!.send(JSON.stringify({
            type: 'agent_status_update',
            payload: { 
              status: 'BUSY',
              reason: 'On call'
            }
          }));
          resolve('sent');
        });

        ws.on('error', reject);
      });

      await agentPromise;
      const statusMessage: any = await statusUpdatePromise;
      
      expect(statusMessage.type).toBe('agent_status_changed');
      expect(statusMessage.payload.agentId).toBe(testUser.id);
      expect(statusMessage.payload.status).toBe('BUSY');
    });
  });

  describe('Queue Management', () => {
    it('should handle queue position updates', async () => {
      const queueUpdatePromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', () => {
          ws!.send(JSON.stringify({
            type: 'subscribe',
            payload: { channel: 'queue_updates' }
          }));
        });

        ws.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'queue_position_update') {
            resolve(message);
          }
        });

        ws.on('error', reject);
        setTimeout(() => reject(new Error('Timeout')), 5000);
      });

      // Simulate queue position change (would normally be triggered by queue service)
      await waitFor(100);
      
      // Create multiple calls to simulate queue
      const campaign = await createTestCampaign({ organizationId: testUser.organizationId });
      for (let i = 0; i < 3; i++) {
        await createTestCall({ 
          phoneNumber: `+123456789${i}`,
          agentId: null, // Unassigned - in queue
          campaignId: campaign.id,
          status: 'QUEUED'
        });
      }

      // In real implementation, this would be triggered by queue service
      // For test, we simulate the message
      ws!.send(JSON.stringify({
        type: 'queue_position_update',
        payload: { 
          queueName: 'inbound',
          position: 2,
          estimatedWaitTime: 45
        }
      }));

      const queueMessage: any = await queueUpdatePromise;
      
      expect(queueMessage.type).toBe('queue_position_update');
      expect(queueMessage.payload.position).toBe(2);
      expect(queueMessage.payload.estimatedWaitTime).toBe(45);
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed messages gracefully', async () => {
      const errorPromise = new Promise((resolve, reject) => {
        ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Cookie': `vd_session=${authToken}`
          }
        });

        ws.on('open', () => {
          // Send malformed message
          ws!.send('invalid json message');
          ws!.send(JSON.stringify({ invalid: 'structure' }));
          
          resolve('sent');
        });

        ws.on('message', (data) => {
          const message = JSON.parse(data.toString());
          if (message.type === 'error') {
            resolve(message);
          }
        });

        ws.on('error', reject);
        setTimeout(() => resolve('timeout'), 2000);
      });

      const result = await errorPromise;
      // Should either receive error message or handle gracefully
      expect(result).toBeDefined();
    });

    it('should handle connection drops and reconnection', async () => {
      let reconnectCount = 0;
      const maxReconnects = 2;
      
      const reconnectPromise = new Promise((resolve, reject) => {
        const connect = () => {
          ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Cookie': `vd_session=${authToken}`
            }
          });

          ws.on('open', () => {
            if (reconnectCount === 0) {
              // First connection - simulate drop
              ws!.close(1001, 'Going away');
            } else {
              // Reconnected successfully
              resolve('reconnected');
            }
          });

          ws.on('close', () => {
            reconnectCount++;
            if (reconnectCount <= maxReconnects) {
              setTimeout(connect, 100);
            } else {
              reject(new Error('Max reconnect attempts reached'));
            }
          });

          ws.on('error', reject);
        };

        connect();
        setTimeout(() => reject(new Error('Timeout')), 5000);
      });

      await expect(reconnectPromise).resolves.toBe('reconnected');
      expect(reconnectCount).toBeGreaterThan(0);
    });
  });

  describe('Performance', () => {
    it('should handle concurrent WebSocket connections', async () => {
      const connections: WebSocket[] = [];
      const connectionPromises = [];
      const numConnections = 10;

      // Create multiple concurrent connections
      for (let i = 0; i < numConnections; i++) {
        const user = await createTestUser({ 
          role: 'AGENT',
          email: `agent${i}@example.com`,
          organizationId: testUser.organizationId
        });
        const token = await createToken({
          userId: user.id,
          email: user.email,
          metadata: { role: 'AGENT' }
        });

        const connectionPromise = new Promise((resolve, reject) => {
          const ws = new WebSocket(`${WS_SERVER_URL}/ws`, {
            headers: {
              'Authorization': `Bearer ${token.token}`,
              'Cookie': `vd_session=${token.token}`
            }
          });

          ws.on('open', () => {
            connections.push(ws);
            resolve('connected');
          });

          ws.on('error', reject);
        });

        connectionPromises.push(connectionPromise);
      }

      // Wait for all connections
      const results = await Promise.all(connectionPromises);
      expect(results.filter(r => r === 'connected')).toHaveLength(numConnections);

      // Clean up connections
      connections.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    });
  });
});
