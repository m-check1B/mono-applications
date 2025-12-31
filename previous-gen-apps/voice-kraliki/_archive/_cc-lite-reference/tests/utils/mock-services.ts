import { vi } from 'vitest';
import { getAdminCredentials, getAgentCredentials, getSupervisorCredentials } from './test-credentials';

// Mock API Service
export class MockApiService {
  private mockResponses: Map<string, any> = new Map();
  private mockErrors: Map<string, any> = new Map();

  constructor() {
    this.setupDefaultResponses();
  }

  private setupDefaultResponses() {
    // Authentication responses
    this.mockResponses.set('POST /auth/login', {
      success: true,
      user: {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'AGENT'
      },
      token: 'mock-jwt-token'
    });

    this.mockResponses.set('GET /auth/me', {
      result: {
        data: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'AGENT'
        }
      }
    });

    this.mockResponses.set('POST /auth/logout', {
      success: true
    });

    // Dashboard responses
    this.mockResponses.set('GET /dashboard', {
      activeCalls: [],
      recentCalls: [],
      teamStatus: {
        members: [],
        stats: {
          totalMembers: 0,
          availableAgents: 0,
          busyAgents: 0,
          onBreakAgents: 0,
          offlineAgents: 0
        }
      },
      callStats: {
        totalCalls: 0,
        activeCalls: 0,
        completedCalls: 0,
        averageDuration: 0,
        handledByAI: 0,
        handledByAgents: 0,
        missedCalls: 0
      }
    });

    this.mockResponses.set('GET /calls/active', []);
    this.mockResponses.set('GET /calls/recent', []);
    this.mockResponses.set('GET /team/status', {
      members: [],
      stats: {
        totalMembers: 0,
        availableAgents: 0,
        busyAgents: 0,
        onBreakAgents: 0,
        offlineAgents: 0
      }
    });

    this.mockResponses.set('GET /calls/stats', {
      totalCalls: 0,
      activeCalls: 0,
      completedCalls: 0,
      averageDuration: 0,
      handledByAI: 0,
      handledByAgents: 0,
      missedCalls: 0
    });
  }

  setMockResponse(method: string, path: string, response: any) {
    this.mockResponses.set(`${method.toUpperCase()} ${path}`, response);
  }

  setMockError(method: string, path: string, error: any) {
    this.mockErrors.set(`${method.toUpperCase()} ${path}`, error);
  }

  async request(method: string, path: string, data?: any) {
    const key = `${method.toUpperCase()} ${path}`;

    // Check for mock error first
    if (this.mockErrors.has(key)) {
      throw this.mockErrors.get(key);
    }

    // Check for mock response
    if (this.mockResponses.has(key)) {
      return this.mockResponses.get(key);
    }

    // Default response for unmocked endpoints
    return { success: true, data: {} };
  }

  async get(path: string) {
    return this.request('GET', path);
  }

  async post(path: string, data?: any) {
    return this.request('POST', path, data);
  }

  async put(path: string, data?: any) {
    return this.request('PUT', path, data);
  }

  async delete(path: string) {
    return this.request('DELETE', path);
  }

  reset() {
    this.mockResponses.clear();
    this.mockErrors.clear();
    this.setupDefaultResponses();
  }
}

// Mock WebSocket Service
export class MockWebSocketService {
  private callbacks: Map<string, Function[]> = new Map();
  private isConnected = false;
  private connectionPromise: Promise<void> | null = null;

  constructor() {
    this.setupEventCallbacks();
  }

  private setupEventCallbacks() {
    this.callbacks.set('open', []);
    this.callbacks.set('message', []);
    this.callbacks.set('error', []);
    this.callbacks.set('close', []);
  }

  connect(url: string = 'ws://localhost:3001/ws'): Promise<void> {
    if (this.isConnected) {
      return Promise.resolve();
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      // Simulate connection delay
      setTimeout(() => {
        this.isConnected = true;
        this.emit('open', { type: 'open' });
        resolve();
      }, 100);
    });

    return this.connectionPromise;
  }

  disconnect() {
    this.isConnected = false;
    this.emit('close', { type: 'close', code: 1000, reason: 'Normal closure' });
  }

  send(data: any) {
    if (!this.isConnected) {
      throw new Error('WebSocket is not connected');
    }

    // Simulate server response
    setTimeout(() => {
      const response = this.generateServerResponse(data);
      if (response) {
        this.emit('message', {
          type: 'message',
          data: JSON.stringify(response)
        });
      }
    }, 50);
  }

  private generateServerResponse(clientData: any): any {
    try {
      const parsedData = typeof clientData === 'string' ? JSON.parse(clientData) : clientData;

      if (parsedData.type === 'subscribe') {
        return {
          event: 'subscription_confirmed',
          data: { events: parsedData.events },
          timestamp: new Date().toISOString()
        };
      }

      return null;
    } catch {
      return null;
    }
  }

  on(event: string, callback: Function) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)!.push(callback);
  }

  off(event: string, callback: Function) {
    if (this.callbacks.has(event)) {
      const callbacks = this.callbacks.get(event)!;
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    if (this.callbacks.has(event)) {
      this.callbacks.get(event)!.forEach(callback => callback(data));
    }
  }

  simulateMessage(message: any) {
    this.emit('message', {
      type: 'message',
      data: JSON.stringify(message)
    });
  }

  simulateError(error: any) {
    this.emit('error', {
      type: 'error',
      error
    });
  }

  simulateDisconnection() {
    this.isConnected = false;
    this.emit('close', {
      type: 'close',
      code: 1006,
      reason: 'Connection lost'
    });
  }

  getConnectionState() {
    return this.isConnected;
  }

  reset() {
    this.isConnected = false;
    this.connectionPromise = null;
    this.setupEventCallbacks();
  }
}

// Mock Auth Service
export class MockAuthService {
  private users: Map<string, any> = new Map();
  private sessions: Map<string, any> = new Map();
  private currentUser: any = null;

  constructor() {
    this.setupDefaultUsers();
  }

  private setupDefaultUsers() {
    const adminCredentials = getAdminCredentials();
    const agentCredentials = getAgentCredentials();
    const supervisorCredentials = getSupervisorCredentials();

    const defaultUsers = [
      {
        id: 'admin-123',
        email: adminCredentials.email,
        password: adminCredentials.password,
        name: 'Admin User',
        role: 'ADMIN'
      },
      {
        id: 'agent-123',
        email: agentCredentials.email,
        password: agentCredentials.password,
        name: 'Agent User',
        role: 'AGENT'
      },
      {
        id: 'supervisor-123',
        email: supervisorCredentials.email,
        password: supervisorCredentials.password,
        name: 'Supervisor User',
        role: 'SUPERVISOR'
      }
    ];

    defaultUsers.forEach(user => {
      this.users.set(user.email, user);
    });
  }

  async login(email: string, password: string): Promise<any> {
    const user = this.users.get(email);

    if (!user || user.password !== password) {
      throw new Error('Invalid credentials');
    }

    const session = {
      id: `session-${Date.now()}`,
      userId: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    };

    this.sessions.set(session.id, session);
    this.currentUser = session;

    return {
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      },
      session: session.id,
      token: `mock-jwt-${session.id}`
    };
  }

  async logout(sessionId: string): Promise<any> {
    this.sessions.delete(sessionId);
    this.currentUser = null;
    return { success: true };
  }

  async getCurrentUser(sessionId: string): Promise<any> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Invalid session');
    }

    // Check if session is expired
    if (new Date(session.expiresAt) < new Date()) {
      this.sessions.delete(sessionId);
      throw new Error('Session expired');
    }

    return {
      result: {
        data: {
          id: session.userId,
          email: session.email,
          name: session.name,
          role: session.role
        }
      }
    };
  }

  async refreshToken(sessionId: string): Promise<any> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Invalid session');
    }

    // Extend session
    session.expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();

    return {
      token: `mock-jwt-refreshed-${session.id}`,
      expiresAt: session.expiresAt
    };
  }

  hasPermission(user: any, permission: string): boolean {
    const permissions = {
      ADMIN: ['*'],
      SUPERVISOR: ['view_dashboard', 'view_agents', 'manage_agents', 'view_calls', 'assign_calls', 'view_reports'],
      AGENT: ['view_dashboard', 'make_calls', 'answer_calls', 'view_own_calls']
    };

    const userPermissions = permissions[user.role] || [];
    return userPermissions.includes('*') || userPermissions.includes(permission);
  }

  hasRole(user: any, role: string): boolean {
    return user.role === role;
  }

  getCurrentSession(): any {
    return this.currentUser;
  }

  reset() {
    this.users.clear();
    this.sessions.clear();
    this.currentUser = null;
    this.setupDefaultUsers();
  }
}

// Mock Dashboard Service
export class MockDashboardService {
  private calls: any[] = [];
  private agents: any[] = [];
  private stats: any = {};

  constructor() {
    this.setupMockData();
  }

  private setupMockData() {
    this.calls = [
      {
        id: 'call-1',
        phoneNumber: '+1234567890',
        status: 'ACTIVE',
        direction: 'INBOUND',
        duration: 120,
        agentId: 'agent-123',
        campaign: 'Sales Campaign',
        startTime: new Date(Date.now() - 120000).toISOString()
      },
      {
        id: 'call-2',
        phoneNumber: '+0987654321',
        status: 'COMPLETED',
        direction: 'OUTBOUND',
        duration: 300,
        agentId: 'agent-123',
        campaign: 'Support Campaign',
        startTime: new Date(Date.now() - 300000).toISOString(),
        endTime: new Date(Date.now() - 0).toISOString()
      }
    ];

    this.agents = [
      {
        id: 'agent-123',
        name: 'John Doe',
        email: 'john.doe@example.com',
        status: 'available',
        activeCall: null,
        skills: ['sales', 'support']
      },
      {
        id: 'agent-456',
        name: 'Jane Smith',
        email: 'jane.smith@example.com',
        status: 'busy',
        activeCall: 'call-1',
        skills: ['support', 'technical']
      }
    ];

    this.stats = {
      totalCalls: 150,
      activeCalls: 1,
      completedCalls: 149,
      averageDuration: 240,
      handledByAI: 45,
      handledByAgents: 105,
      missedCalls: 5
    };
  }

  async getDashboardData(): Promise<any> {
    return {
      activeCalls: this.calls.filter(call => call.status === 'ACTIVE'),
      recentCalls: this.calls.filter(call => call.status === 'COMPLETED'),
      teamStatus: {
        members: this.agents,
        stats: {
          totalMembers: this.agents.length,
          availableAgents: this.agents.filter(a => a.status === 'available').length,
          busyAgents: this.agents.filter(a => a.status === 'busy').length,
          onBreakAgents: this.agents.filter(a => a.status === 'on_break').length,
          offlineAgents: this.agents.filter(a => a.status === 'offline').length
        }
      },
      callStats: this.stats
    };
  }

  async getCallDetails(callId: string): Promise<any> {
    const call = this.calls.find(c => c.id === callId);
    if (!call) {
      throw new Error('Call not found');
    }
    return call;
  }

  async getTeamStatus(): Promise<any> {
    return {
      members: this.agents,
      stats: {
        totalMembers: this.agents.length,
        availableAgents: this.agents.filter(a => a.status === 'available').length,
        busyAgents: this.agents.filter(a => a.status === 'busy').length,
        onBreakAgents: this.agents.filter(a => a.status === 'on_break').length,
        offlineAgents: this.agents.filter(a => a.status === 'offline').length
      }
    };
  }

  async getCallStats(): Promise<any> {
    return this.stats;
  }

  async getRecentCalls(): Promise<any[]> {
    return this.calls.filter(call => call.status === 'COMPLETED');
  }

  simulateCallUpdate(callId: string, updates: any) {
    const callIndex = this.calls.findIndex(c => c.id === callId);
    if (callIndex > -1) {
      this.calls[callIndex] = { ...this.calls[callIndex], ...updates };
    }
  }

  simulateAgentStatusUpdate(agentId: string, status: string, activeCall: string | null = null) {
    const agentIndex = this.agents.findIndex(a => a.id === agentId);
    if (agentIndex > -1) {
      this.agents[agentIndex] = {
        ...this.agents[agentIndex],
        status,
        activeCall
      };
    }
  }

  reset() {
    this.calls = [];
    this.agents = [];
    this.stats = {};
    this.setupMockData();
  }
}

// Mock Notification Service
export class MockNotificationService {
  private notifications: any[] = [];
  private callbacks: Map<string, Function[]> = new Map();

  constructor() {
    this.setupEventCallbacks();
  }

  private setupEventCallbacks() {
    this.callbacks.set('notification', []);
  }

  async sendNotification(type: string, message: string, data: any = {}): Promise<any> {
    const notification = {
      id: `notification-${Date.now()}`,
      type,
      message,
      data,
      timestamp: new Date().toISOString(),
      read: false
    };

    this.notifications.push(notification);
    this.emit('notification', notification);

    return notification;
  }

  async getNotifications(): Promise<any[]> {
    return this.notifications;
  }

  async markAsRead(notificationId: string): Promise<any> {
    const notification = this.notifications.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
    }
    return notification;
  }

  async markAllAsRead(): Promise<any> {
    this.notifications.forEach(n => n.read = true);
    return { success: true };
  }

  async deleteNotification(notificationId: string): Promise<any> {
    const index = this.notifications.findIndex(n => n.id === notificationId);
    if (index > -1) {
      this.notifications.splice(index, 1);
    }
    return { success: true };
  }

  on(event: string, callback: Function) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)!.push(callback);
  }

  off(event: string, callback: Function) {
    if (this.callbacks.has(event)) {
      const callbacks = this.callbacks.get(event)!;
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    if (this.callbacks.has(event)) {
      this.callbacks.get(event)!.forEach(callback => callback(data));
    }
  }

  simulateNotification(notification: any) {
    this.notifications.push(notification);
    this.emit('notification', notification);
  }

  reset() {
    this.notifications = [];
    this.callbacks.clear();
    this.setupEventCallbacks();
  }
}

// Service Factory
export class ServiceFactory {
  private static instances: Map<string, any> = new Map();

  static getApiService(): MockApiService {
    if (!this.instances.has('api')) {
      this.instances.set('api', new MockApiService());
    }
    return this.instances.get('api') as MockApiService;
  }

  static getWebSocketService(): MockWebSocketService {
    if (!this.instances.has('websocket')) {
      this.instances.set('websocket', new MockWebSocketService());
    }
    return this.instances.get('websocket') as MockWebSocketService;
  }

  static getAuthService(): MockAuthService {
    if (!this.instances.has('auth')) {
      this.instances.set('auth', new MockAuthService());
    }
    return this.instances.get('auth') as MockAuthService;
  }

  static getDashboardService(): MockDashboardService {
    if (!this.instances.has('dashboard')) {
      this.instances.set('dashboard', new MockDashboardService());
    }
    return this.instances.get('dashboard') as MockDashboardService;
  }

  static getNotificationService(): MockNotificationService {
    if (!this.instances.has('notification')) {
      this.instances.set('notification', new MockNotificationService());
    }
    return this.instances.get('notification') as MockNotificationService;
  }

  static resetAll() {
    this.instances.forEach(service => {
      if (typeof service.reset === 'function') {
        service.reset();
      }
    });
    this.instances.clear();
  }
}
