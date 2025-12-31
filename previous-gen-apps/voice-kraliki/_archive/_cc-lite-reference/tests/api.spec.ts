import { test, expect } from '@playwright/test';

test.describe('API/tRPC Tests', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    // Get auth token
    const loginResponse = await request.post('http://localhost:3010/trpc/auth.login', {
      data: {
        json: {
          email: 'admin@demo.com',
          password: 'demo123!'
        }
      }
    });
    
    const cookies = await loginResponse.headers();
    authToken = cookies['set-cookie']?.match(/vd_session=([^;]+)/)?.[1] || '';
  });

  test('should fetch dashboard metrics', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/dashboard.getMetrics', {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.result?.data).toHaveProperty('calls');
    expect(data.result?.data).toHaveProperty('performance');
    expect(data.result?.data).toHaveProperty('team');
  });

  test('should fetch call history', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/telephony.getCallHistory?input=' + encodeURIComponent(JSON.stringify({
      limit: 10,
      offset: 0
    })), {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.result?.data).toHaveProperty('calls');
    expect(data.result?.data).toHaveProperty('total');
    expect(data.result?.data).toHaveProperty('hasMore');
  });

  test('should fetch team members', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/team.getAvailability', {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.result?.data).toHaveProperty('available');
    expect(data.result?.data).toHaveProperty('busy');
    expect(data.result?.data).toHaveProperty('onBreak');
    expect(data.result?.data).toHaveProperty('offline');
  });

  test('should fetch analytics data', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/analytics.getRealtimeMetrics', {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.result?.data).toHaveProperty('calls');
    expect(data.result?.data).toHaveProperty('agents');
    expect(data.result?.data).toHaveProperty('performance');
  });

  test('should fetch IVR configuration', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/ivr.getConfig', {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.result?.data).toHaveProperty('mainMenu');
    expect(data.result?.data).toHaveProperty('businessHours');
  });

  test('should handle unauthorized requests', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/dashboard.getMetrics');
    
    expect(response.status()).toBe(401);
    const data = await response.json();
    expect(data.error).toBeDefined();
  });

  test('should validate input parameters', async ({ request }) => {
    const response = await request.get('http://localhost:3010/trpc/telephony.getCallHistory?input=' + encodeURIComponent(JSON.stringify({
      limit: -1, // Invalid limit
      offset: 0
    })), {
      headers: {
        'Cookie': `vd_session=${authToken}`
      }
    });
    
    const data = await response.json();
    expect(data.error).toBeDefined();
  });

  test('should handle batch requests', async ({ request }) => {
    const batchRequest = [
      { id: '1', method: 'query', path: 'dashboard.getMetrics' },
      { id: '2', method: 'query', path: 'team.getAvailability' }
    ];
    
    const response = await request.post('http://localhost:3010/trpc', {
      headers: {
        'Cookie': `vd_session=${authToken}`,
        'Content-Type': 'application/json'
      },
      data: batchRequest
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });
});