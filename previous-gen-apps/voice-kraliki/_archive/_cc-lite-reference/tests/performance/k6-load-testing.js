import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';

// Custom metrics
const wsConnections = new Counter('websocket_connections');
const wsMessages = new Counter('websocket_messages');
const wsErrors = new Rate('websocket_errors');
const connectionDuration = new Trend('connection_duration');
const apiResponseTime = new Trend('api_response_time');
const callSetupTime = new Trend('call_setup_time');

// Test configuration
export const options = {
  scenarios: {
    // API Load Testing
    api_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 20 },   // Ramp up to 20 users
        { duration: '5m', target: 50 },   // Ramp up to 50 users
        { duration: '10m', target: 100 }, // Peak load: 100 users
        { duration: '5m', target: 50 },   // Ramp down to 50
        { duration: '2m', target: 0 },    // Ramp down to 0
      ],
      exec: 'apiLoadTest',
    },

    // WebSocket Stress Testing
    websocket_stress: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      exec: 'websocketStressTest',
    },

    // Call Center Simulation
    call_center_simulation: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { duration: '5m', target: 50 },   // 50 calls/second
        { duration: '10m', target: 100 }, // 100 calls/second
        { duration: '5m', target: 50 },   // Back to 50
      ],
      exec: 'callCenterSimulation',
    },

    // Database Stress Testing
    database_stress: {
      executor: 'shared-iterations',
      vus: 20,
      iterations: 1000,
      exec: 'databaseStressTest',
    }
  },

  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.1'],    // Error rate under 10%
    websocket_errors: ['rate<0.05'],  // WebSocket error rate under 5%
    connection_duration: ['p(90)<1000'], // 90% connections established under 1s
    call_setup_time: ['p(95)<2000'],  // 95% calls setup under 2s
  }
};

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:3010';
const WS_URL = __ENV.WS_URL || 'ws://127.0.0.1:3010/ws';

// Authentication helper
function authenticate() {
  const loginPayload = {
    email: 'test.assistant@stack2025.com',
    password: 'Stack2025!Test@Assistant#Secure$2024'
  };

  const response = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify(loginPayload), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (response.status === 200) {
    const token = response.json('token');
    return token;
  }

  return null;
}

// API Load Testing Scenario
export function apiLoadTest() {
  const token = authenticate();

  if (!token) {
    console.error('Authentication failed');
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  // Test critical API endpoints
  const endpoints = [
    '/api/calls',
    '/api/agents',
    '/api/campaigns',
    '/api/dashboard/stats',
    '/api/reports/daily'
  ];

  endpoints.forEach(endpoint => {
    const start = Date.now();
    const response = http.get(`${BASE_URL}${endpoint}`, { headers });
    const duration = Date.now() - start;

    check(response, {
      [`${endpoint} status is 200`]: (r) => r.status === 200,
      [`${endpoint} response time < 500ms`]: () => duration < 500,
    });

    apiResponseTime.add(duration);
  });

  // Test POST operations (creating resources)
  const campaignData = {
    name: `Load Test Campaign ${Math.random()}`,
    description: 'Performance testing campaign',
    type: 'outbound',
    priority: 'medium'
  };

  const createResponse = http.post(
    `${BASE_URL}/api/campaigns`,
    JSON.stringify(campaignData),
    { headers }
  );

  check(createResponse, {
    'Campaign creation successful': (r) => r.status === 201,
  });

  sleep(1);
}

// WebSocket Stress Testing Scenario
export function websocketStressTest() {
  const token = authenticate();

  if (!token) {
    console.error('Authentication failed for WebSocket test');
    return;
  }

  const url = `${WS_URL}?token=${token}`;

  const res = ws.connect(url, function (socket) {
    wsConnections.add(1);
    const connectionStart = Date.now();

    socket.on('open', function open() {
      connectionDuration.add(Date.now() - connectionStart);

      // Send periodic heartbeat messages
      socket.setInterval(function timeout() {
        socket.send(JSON.stringify({
          type: 'HEARTBEAT',
          timestamp: Date.now()
        }));
      }, 5000);

      // Simulate agent status updates
      socket.setInterval(function statusUpdate() {
        socket.send(JSON.stringify({
          type: 'AGENT_STATUS_UPDATE',
          data: {
            agentId: `agent-${__VU}`,
            status: Math.random() > 0.5 ? 'available' : 'busy',
            timestamp: Date.now()
          }
        }));
        wsMessages.add(1);
      }, 10000);
    });

    socket.on('message', function message(data) {
      wsMessages.add(1);

      try {
        const parsedData = JSON.parse(data);

        check(parsedData, {
          'Message has valid type': (msg) => msg.type !== undefined,
          'Message has data': (msg) => msg.data !== undefined,
        });
      } catch (e) {
        wsErrors.add(1);
      }
    });

    socket.on('error', function error(e) {
      wsErrors.add(1);
      console.error('WebSocket error:', e);
    });

    socket.on('close', function close() {
      console.log('WebSocket connection closed');
    });

    // Keep connection alive for test duration
    socket.setTimeout(function () {
      socket.close();
    }, 30000); // Close after 30 seconds
  });

  check(res, { 'WebSocket connected successfully': (r) => r && r.status === 101 });

  sleep(1);
}

// Call Center Simulation Scenario
export function callCenterSimulation() {
  const token = authenticate();

  if (!token) {
    console.error('Authentication failed for call simulation');
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  // Simulate incoming call
  const callData = {
    phoneNumber: `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
    direction: 'inbound',
    customerName: `Customer ${Math.random().toString(36).substring(7)}`,
    priority: Math.random() > 0.8 ? 'high' : 'normal'
  };

  const callSetupStart = Date.now();

  // Create call
  const createCallResponse = http.post(
    `${BASE_URL}/api/calls`,
    JSON.stringify(callData),
    { headers }
  );

  check(createCallResponse, {
    'Call creation successful': (r) => r.status === 201,
  });

  if (createCallResponse.status === 201) {
    const callId = createCallResponse.json('id');

    // Simulate call progression
    const callStates = ['ringing', 'answered', 'connected'];

    callStates.forEach((state, index) => {
      sleep(1); // Simulate time between state changes

      const updateResponse = http.patch(
        `${BASE_URL}/api/calls/${callId}`,
        JSON.stringify({ status: state }),
        { headers }
      );

      check(updateResponse, {
        [`Call ${state} update successful`]: (r) => r.status === 200,
      });
    });

    callSetupTime.add(Date.now() - callSetupStart);

    // Simulate call duration (random between 30s and 5 minutes)
    const callDuration = Math.random() * 270 + 30;
    sleep(callDuration / 1000); // Convert to seconds for k6

    // End call
    const endCallResponse = http.patch(
      `${BASE_URL}/api/calls/${callId}`,
      JSON.stringify({
        status: 'completed',
        outcome: Math.random() > 0.7 ? 'resolved' : 'transferred'
      }),
      { headers }
    );

    check(endCallResponse, {
      'Call completion successful': (r) => r.status === 200,
    });
  }

  sleep(Math.random() * 5); // Random delay between calls
}

// Database Stress Testing Scenario
export function databaseStressTest() {
  const token = authenticate();

  if (!token) {
    console.error('Authentication failed for database stress test');
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  // Test database-heavy operations
  const operations = [
    // Complex queries
    { method: 'GET', url: '/api/reports/agent-performance?days=30' },
    { method: 'GET', url: '/api/analytics/call-volume?range=week' },
    { method: 'GET', url: '/api/campaigns/statistics' },

    // Write operations
    {
      method: 'POST',
      url: '/api/call-notes',
      data: {
        callId: `call-${Math.random().toString(36)}`,
        content: `Performance test note ${Date.now()}`,
        agentId: `agent-${__VU}`
      }
    },

    // Bulk operations
    { method: 'GET', url: '/api/calls?limit=100&offset=0' },
    { method: 'GET', url: '/api/agents?include=stats,performance' }
  ];

  operations.forEach(operation => {
    const start = Date.now();
    let response;

    if (operation.method === 'GET') {
      response = http.get(`${BASE_URL}${operation.url}`, { headers });
    } else if (operation.method === 'POST') {
      response = http.post(
        `${BASE_URL}${operation.url}`,
        JSON.stringify(operation.data),
        { headers }
      );
    }

    const duration = Date.now() - start;

    check(response, {
      [`${operation.url} returns valid response`]: (r) => r.status >= 200 && r.status < 400,
      [`${operation.url} responds quickly`]: () => duration < 1000,
    });

    apiResponseTime.add(duration);
  });

  sleep(0.5);
}

// Data export for analysis
export function handleSummary(data) {
  return {
    'performance-report.json': JSON.stringify(data, null, 2),
    'performance-summary.txt': `
Performance Test Summary
=======================

Total Requests: ${data.metrics.http_reqs.values.count}
Average Response Time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
95th Percentile: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
Error Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%

WebSocket Connections: ${data.metrics.websocket_connections?.values.count || 0}
WebSocket Messages: ${data.metrics.websocket_messages?.values.count || 0}
WebSocket Error Rate: ${((data.metrics.websocket_errors?.values.rate || 0) * 100).toFixed(2)}%

Call Setup Time (95th): ${(data.metrics.call_setup_time?.values['p(95)'] || 0).toFixed(2)}ms
Connection Duration (90th): ${(data.metrics.connection_duration?.values['p(90)'] || 0).toFixed(2)}ms

Test Status: ${data.metrics.http_req_failed.values.rate < 0.1 ? 'PASSED' : 'FAILED'}
    `.trim()
  };
}

// Utility functions for test data generation
export function generatePhoneNumber() {
  return `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`;
}

export function generateCustomerName() {
  const firstNames = ['John', 'Jane', 'Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];

  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];

  return `${firstName} ${lastName}`;
}

export function getRandomCallOutcome() {
  const outcomes = ['resolved', 'transferred', 'callback_scheduled', 'no_answer', 'voicemail'];
  return outcomes[Math.floor(Math.random() * outcomes.length)];
}