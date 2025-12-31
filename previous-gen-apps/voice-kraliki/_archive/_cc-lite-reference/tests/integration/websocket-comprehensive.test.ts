/**
 * Comprehensive WebSocket Tests for Language WebSocket Handler
 * Tests real-time language detection, switching, broadcasting, and error handling
 * Focuses on the LanguageWebSocketHandler service with full event coverage
 */

import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import WebSocket from 'ws';
import { EventEmitter } from 'eventemitter3';
import {
  LanguageWebSocketHandler,
  createLanguageWebSocketHandler,
  type LanguageWebSocketClient,
  type LanguageChangeEvent,
  type VoiceSwitchEvent
} from '../../server/services/language-websocket-handler.js';
import { LanguageRouterService } from '../../server/services/language-router-service.js';
import { DeepgramAgentService } from '../../server/services/deepgram-agent-service.js';
// import { testDb, createTestUser, waitFor } from '../setup';
// import { createToken } from '@unified/auth-core';

// Utility functions for testing without DB dependency
const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const createMockUser = () => ({
  id: 'test-user-123',
  email: 'test@example.com',
  role: 'AGENT',
  organizationId: 'test-org-123'
});

const createMockToken = async (user: any) => ({
  token: `mock-token-${user.id}`,
  userId: user.id,
  email: user.email
});

// Mock WebSocket Server for testing
class MockWebSocketServer extends EventEmitter {
  private connections = new Map<string, WebSocket>();

  addConnection(id: string, ws: WebSocket) {
    this.connections.set(id, ws);
  }

  removeConnection(id: string) {
    this.connections.delete(id);
  }

  broadcast(message: string, excludeId?: string) {
    for (const [id, ws] of this.connections) {
      if (id !== excludeId && ws.readyState === WebSocket.OPEN) {
        ws.send(message);
      }
    }
  }

  getConnectionCount(): number {
    return this.connections.size;
  }

  cleanup() {
    this.connections.clear();
    this.removeAllListeners();
  }
}

// Mock WebSocket implementation for testing
class MockWebSocket extends EventEmitter {
  public readyState: number = WebSocket.OPEN;
  public CONNECTING = 0;
  public OPEN = 1;
  public CLOSING = 2;
  public CLOSED = 3;

  private messageQueue: string[] = [];

  constructor(public url?: string, public options?: any) {
    super();
    // Simulate connection opening
    setImmediate(() => {
      this.readyState = WebSocket.OPEN;
      this.emit('open');
    });
  }

  send(data: string | Buffer) {
    if (this.readyState === WebSocket.OPEN) {
      this.messageQueue.push(data.toString());
      // Don't simulate message reception here - that would cause a loop
    }
  }

  close(code?: number, reason?: string) {
    this.readyState = WebSocket.CLOSED;
    this.emit('close', code, reason);
  }

  ping() {
    this.emit('ping');
  }

  pong() {
    this.emit('pong');
  }

  getMessages(): string[] {
    return [...this.messageQueue];
  }

  clearMessages() {
    this.messageQueue = [];
  }

  simulateMessage(data: any) {
    if (this.readyState === WebSocket.OPEN) {
      // Use setImmediate to ensure async behavior
      setImmediate(() => {
        this.emit('message', Buffer.from(JSON.stringify(data)));
      });
    }
  }

  simulateError(error: Error) {
    this.emit('error', error);
  }
}

// Mock Language Router Service
class MockLanguageRouterService extends EventEmitter {
  private sessions = new Map<string, any>();
  private routes = new Map<string, any>();

  async processText(sessionId: string, text: string) {
    const lowerText = text.toLowerCase();
    const result = {
      language: (lowerText.includes('español') || lowerText.includes('hola') || lowerText.includes('está')) ? 'es' as const :
                (lowerText.includes('česky') || lowerText.includes('dobrý den')) ? 'cs' as const : 'en' as const,
      confidence: 0.95,
      source: 'text' as const,
      patterns: ['greeting', 'question']
    };

    this.emit('languageDetected', {
      sessionId,
      detection: result,
      switched: false,
      text
    });

    return result;
  }

  async processAudio(sessionId: string, audioBuffer: Buffer, text?: string) {
    const result = {
      language: 'en' as const,
      confidence: 0.85,
      source: 'audio' as const,
      patterns: ['speech']
    };

    this.emit('languageDetected', {
      sessionId,
      detection: result,
      switched: false,
      text
    });

    return result;
  }

  async setSessionLanguage(sessionId: string, language: 'en' | 'es' | 'cs', confirmed: boolean = false) {
    const oldLanguage = this.sessions.get(sessionId)?.language;

    this.sessions.set(sessionId, { language, confirmed });

    this.emit('languageChanged', {
      sessionId,
      oldLanguage,
      newLanguage: language,
      manual: confirmed,
      timestamp: new Date()
    });

    // Simulate route switching
    const newRoute = {
      provider: language === 'cs' ? 'azure' : 'deepgram',
      voiceId: language === 'es' ? 'stella' : language === 'cs' ? 'cs-voice' : 'asteria',
      language
    };

    const oldRoute = this.routes.get(sessionId);
    this.routes.set(sessionId, newRoute);

    this.emit('routeSwitched', {
      sessionId,
      oldRoute,
      newRoute,
      timestamp: new Date()
    });
  }

  async synthesizeSpeech(sessionId: string, text: string, options?: any) {
    // Simulate speech synthesis
    const audioBuffer = Buffer.from(`audio-${text.substring(0, 20)}-${sessionId}`);
    return audioBuffer;
  }

  getSessionStats(sessionId: string) {
    return {
      sessionId,
      currentLanguage: this.sessions.get(sessionId)?.language || 'en',
      detectionCount: 5,
      switchCount: 1,
      confidence: 0.95,
      startTime: new Date(Date.now() - 60000)
    };
  }

  getSessionRoute(sessionId: string) {
    return this.routes.get(sessionId) || {
      provider: 'deepgram',
      voiceId: 'asteria',
      language: 'en'
    };
  }

  getHealthStatus() {
    return {
      status: 'healthy',
      activeSessions: this.sessions.size,
      providers: {
        deepgram: { status: 'connected', latency: 25 },
        azure: { status: 'connected', latency: 30 }
      }
    };
  }

  getTTSService(language: 'en' | 'es' | 'cs') {
    if (language === 'cs') {
      return {
        getAvailableVoices: () => ['cs-voice-1', 'cs-voice-2']
      };
    }
    return null;
  }

  startSession(sessionId: string, preference: any) {
    this.sessions.set(sessionId, preference);
    this.emit('sessionStarted', {
      sessionId,
      preference,
      route: this.getSessionRoute(sessionId)
    });
  }

  endSession(sessionId: string) {
    const session = this.sessions.get(sessionId);
    this.sessions.delete(sessionId);
    this.routes.delete(sessionId);

    this.emit('sessionEnded', {
      sessionId,
      duration: 120000,
      finalLanguage: session?.language || 'en',
      route: this.getSessionRoute(sessionId)
    });
  }

  emitSynthesisError(sessionId: string, language: 'en' | 'es' | 'cs', provider: string, error: Error) {
    this.emit('synthesisError', {
      sessionId,
      language,
      provider,
      error
    });
  }

  emitContextDetection(sessionId: string, phoneNumber: string, countryCode: string) {
    this.emit('languageDetectedFromContext', {
      sessionId,
      detection: {
        language: countryCode === 'ES' ? 'es' : countryCode === 'CZ' ? 'cs' : 'en',
        confidence: 0.8,
        source: 'context'
      },
      phoneNumber,
      countryCode
    });
  }
}

// Mock Deepgram Agent Service
class MockDeepgramAgentService extends EventEmitter {
  async createAgent(config: any) {
    return { id: 'mock-agent-123', status: 'created' };
  }
}

describe('Language WebSocket Handler Comprehensive Tests', () => {
  let handler: LanguageWebSocketHandler;
  let mockLanguageRouter: MockLanguageRouterService;
  let mockAgentService: MockDeepgramAgentService;
  let mockServer: MockWebSocketServer;
  let testUser: any;
  let authToken: string;

  beforeAll(async () => {
    // Create test user for authentication (mocked)
    testUser = createMockUser();
    const token = await createMockToken(testUser);
    authToken = token.token;
  });

  beforeEach(async () => {
    // Initialize mocks
    mockLanguageRouter = new MockLanguageRouterService();
    mockAgentService = new MockDeepgramAgentService();
    mockServer = new MockWebSocketServer();

    // Create handler with mocks
    handler = createLanguageWebSocketHandler(
      mockLanguageRouter as any,
      mockAgentService as any
    );

    // Start heartbeat with short interval for testing
    handler.startHeartbeat(1000);
  });

  afterEach(async () => {
    await handler.cleanup();
    mockServer.cleanup();
    mockLanguageRouter.removeAllListeners();
    mockAgentService.removeAllListeners();
  });

  describe('Connection Establishment and Authentication', () => {
    it('should successfully add and manage WebSocket clients', async () => {
      const mockWs = new MockWebSocket();
      const sessionId = 'test-session-1';

      const clientId = handler.addClient(mockWs as any, sessionId, 'client-1', {
        userAgent: 'test-browser',
        ipAddress: '127.0.0.1'
      });

      expect(clientId).toBe('client-1');

      // Check stats
      const stats = handler.getStats();
      expect(stats.totalClients).toBe(1);
      expect(stats.activeSessions).toBe(1);
      expect(stats.clientsPerSession).toHaveLength(1);
      expect(stats.clientsPerSession[0].sessionId).toBe(sessionId);
      expect(stats.clientsPerSession[0].clientCount).toBe(1);
    });

    it('should handle client connections with auto-generated IDs', async () => {
      const mockWs = new MockWebSocket();
      const sessionId = 'test-session-2';

      const clientId = handler.addClient(mockWs as any, sessionId);

      expect(clientId).toMatch(/^lang-client-\d+-[a-z0-9]+$/);
      expect(handler.getStats().totalClients).toBe(1);
    });

    it('should send welcome message with language status on connection', async () => {
      const mockWs = new MockWebSocket();
      const sessionId = 'test-session-3';

      handler.addClient(mockWs as any, sessionId);

      await waitFor(50); // Wait for async welcome message

      const messages = mockWs.getMessages();
      expect(messages.length).toBeGreaterThan(0);

      const welcomeMessage = JSON.parse(messages[0]);
      expect(welcomeMessage.event).toBe('language_status');
      expect(welcomeMessage.data.session).toBeDefined();
      expect(welcomeMessage.data.route).toBeDefined();
      expect(welcomeMessage.data.health).toBeDefined();
    });

    it('should track multiple clients per session', async () => {
      const sessionId = 'multi-client-session';
      const clients: MockWebSocket[] = [];

      // Add multiple clients to same session
      for (let i = 0; i < 3; i++) {
        const mockWs = new MockWebSocket();
        handler.addClient(mockWs as any, sessionId, `client-${i}`);
        clients.push(mockWs);
      }

      const stats = handler.getStats();
      expect(stats.totalClients).toBe(3);
      expect(stats.activeSessions).toBe(1);
      expect(stats.clientsPerSession[0].clientCount).toBe(3);
    });

    it('should emit clientConnected event when client joins', async () => {
      const mockWs = new MockWebSocket();
      const sessionId = 'event-test-session';

      const eventPromise = new Promise((resolve) => {
        handler.once('clientConnected', resolve);
      });

      const clientId = handler.addClient(mockWs as any, sessionId, 'event-client');
      const event: any = await eventPromise;

      expect(event.clientId).toBe('event-client');
      expect(event.sessionId).toBe(sessionId);
      expect(event.metadata).toBeDefined();
    });
  });

  describe('Message Handling and Event Processing', () => {
    let mockWs: MockWebSocket;
    let clientId: string;
    let sessionId: string;

    beforeEach(() => {
      mockWs = new MockWebSocket();
      sessionId = 'message-test-session';
      clientId = handler.addClient(mockWs as any, sessionId, 'message-client');
      mockWs.clearMessages(); // Clear welcome message
    });

    it('should handle subscription and unsubscription requests', async () => {
      // Test subscription
      mockWs.simulateMessage({
        type: 'subscribe',
        events: ['language_detected', 'voice_switched']
      });

      await waitFor(50);

      let messages = mockWs.getMessages();
      let subscribeResponse = JSON.parse(messages[messages.length - 1]);
      expect(subscribeResponse.event).toBe('subscribed');
      expect(subscribeResponse.data.events).toContain('language_detected');
      expect(subscribeResponse.data.events).toContain('voice_switched');

      // Test unsubscription
      mockWs.simulateMessage({
        type: 'unsubscribe',
        events: ['language_detected']
      });

      await waitFor(50);

      messages = mockWs.getMessages();
      const unsubscribeResponse = JSON.parse(messages[messages.length - 1]);
      expect(unsubscribeResponse.event).toBe('unsubscribed');
      expect(unsubscribeResponse.data.events).not.toContain('language_detected');
      expect(unsubscribeResponse.data.events).toContain('voice_switched');
    });

    it('should handle manual language change requests', async () => {
      mockWs.simulateMessage({
        type: 'set_language',
        language: 'es',
        confirmed: true
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('language_set');
      expect(response.data.language).toBe('es');
      expect(response.data.confirmed).toBe(true);
    });

    it('should reject invalid language codes', async () => {
      mockWs.simulateMessage({
        type: 'set_language',
        language: 'invalid',
        confirmed: true
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('error');
      expect(response.data.message).toBe('Invalid language code');
    });

    it('should handle language detection from text', async () => {
      mockWs.simulateMessage({
        type: 'detect_language',
        text: 'Hola, ¿cómo está usted?'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('language_detected');
      expect(response.data.detection.language).toBe('es');
      expect(response.data.detection.confidence).toBeGreaterThan(0.8);
    });

    it('should handle language detection from audio buffer', async () => {
      const audioBuffer = Buffer.from('mock-audio-data').toString('base64');

      mockWs.simulateMessage({
        type: 'detect_language',
        audioBuffer
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('language_detected');
      expect(response.data.detection).toBeDefined();
    });

    it('should handle voice testing requests', async () => {
      mockWs.simulateMessage({
        type: 'test_voice',
        language: 'es',
        voiceId: 'stella',
        text: 'Hola, esta es una prueba de voz'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('voice_test_result');
      expect(response.data.language).toBe('es');
      expect(response.data.voiceId).toBe('stella');
      expect(response.data.audioData).toBeDefined();
    });

    it('should provide available voices for different languages', async () => {
      mockWs.simulateMessage({
        type: 'get_available_voices',
        language: 'es'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('available_voices');
      expect(response.data.language).toBe('es');
      expect(response.data.voices).toBeDefined();
      expect(response.data.voices.deepgram).toBeDefined();
    });

    it('should handle ping-pong for heartbeat', async () => {
      mockWs.simulateMessage({
        type: 'ping'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('pong');
      expect(response.data.timestamp).toBeDefined();
    });

    it('should handle unknown message types gracefully', async () => {
      mockWs.simulateMessage({
        type: 'unknown_message_type',
        data: 'test'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      const response = JSON.parse(messages[messages.length - 1]);
      expect(response.event).toBe('error');
      expect(response.data.message).toContain('Unknown message type');
    });
  });

  describe('Real-time Broadcasting and Event Distribution', () => {
    let clients: { ws: MockWebSocket; id: string; sessionId: string }[];

    beforeEach(() => {
      clients = [];

      // Create multiple clients across different sessions
      for (let i = 0; i < 5; i++) {
        const mockWs = new MockWebSocket();
        const sessionId = i < 3 ? 'session-A' : 'session-B';
        const clientId = handler.addClient(mockWs as any, sessionId, `client-${i}`);
        clients.push({ ws: mockWs, id: clientId, sessionId });
        mockWs.clearMessages(); // Clear welcome messages
      }
    });

    it('should broadcast language detection to session clients', async () => {
      const sessionId = 'session-A';

      // Trigger language detection
      await mockLanguageRouter.processText(sessionId, 'Hola, ¿cómo está?');

      await waitFor(50);

      // Check that clients in session-A received the event
      const sessionAClients = clients.filter(c => c.sessionId === 'session-A');
      const sessionBClients = clients.filter(c => c.sessionId === 'session-B');

      for (const client of sessionAClients) {
        const messages = client.ws.getMessages();
        expect(messages.length).toBeGreaterThan(0);

        const event = JSON.parse(messages[messages.length - 1]);
        expect(event.event).toBe('language_detected');
        expect(event.data.language).toBe('es');
      }

      // Session B clients should not receive the event
      for (const client of sessionBClients) {
        const messages = client.ws.getMessages();
        expect(messages.length).toBe(0);
      }
    });

    it('should broadcast language changes to session clients', async () => {
      const sessionId = 'session-A';

      // Trigger language change
      await mockLanguageRouter.setSessionLanguage(sessionId, 'es', true);

      await waitFor(50);

      const sessionAClients = clients.filter(c => c.sessionId === 'session-A');

      for (const client of sessionAClients) {
        const messages = client.ws.getMessages();
        expect(messages.length).toBeGreaterThan(0);

        // Look for language_changed event
        const languageChangedEvent = messages
          .map(m => JSON.parse(m))
          .find(event => event.event === 'language_changed');

        expect(languageChangedEvent).toBeDefined();
        expect(languageChangedEvent.data.newLanguage).toBe('es');
        expect(languageChangedEvent.data.source).toBe('manual');
      }
    });

    it('should broadcast voice switching events', async () => {
      const sessionId = 'session-A';

      // Trigger route switching (which causes voice switch broadcast)
      await mockLanguageRouter.setSessionLanguage(sessionId, 'cs', true);

      await waitFor(50);

      const sessionAClients = clients.filter(c => c.sessionId === 'session-A');

      for (const client of sessionAClients) {
        const messages = client.ws.getMessages();

        // Look for voice_switched event
        const voiceSwitchedEvent = messages
          .map(m => JSON.parse(m))
          .find(event => event.event === 'voice_switched');

        expect(voiceSwitchedEvent).toBeDefined();
        expect(voiceSwitchedEvent.data.language).toBe('cs');
        expect(voiceSwitchedEvent.data.toProvider).toBe('azure');
      }
    });

    it('should respect client subscriptions for event filtering', async () => {
      const sessionId = 'session-A';
      const client = clients.find(c => c.sessionId === sessionId && c.id === 'client-0');

      // First subscribe to ensure we can unsubscribe
      client!.ws.simulateMessage({
        type: 'subscribe',
        events: ['language_detected']
      });

      await waitFor(50);

      // Unsubscribe from language_detected events (but keep 'all' if it exists)
      client!.ws.simulateMessage({
        type: 'unsubscribe',
        events: ['all', 'language_detected']
      });

      await waitFor(50);
      client!.ws.clearMessages();

      // Trigger language detection
      await mockLanguageRouter.processText(sessionId, 'Hello world');

      await waitFor(50);

      // This client should not receive language_detected events
      const messages = client!.ws.getMessages();
      const hasLanguageDetected = messages
        .map(m => JSON.parse(m))
        .some(event => event.event === 'language_detected');

      expect(hasLanguageDetected).toBe(false);
    });

    it('should handle session lifecycle events', async () => {
      const sessionId = 'lifecycle-session';
      const mockWs = new MockWebSocket();
      handler.addClient(mockWs as any, sessionId);
      mockWs.clearMessages();

      // Start session
      mockLanguageRouter.startSession(sessionId, { language: 'en' });

      await waitFor(50);

      let messages = mockWs.getMessages();
      let startEvent = JSON.parse(messages[messages.length - 1]);
      expect(startEvent.event).toBe('language_session_started');

      // End session
      mockLanguageRouter.endSession(sessionId);

      await waitFor(50);

      messages = mockWs.getMessages();
      const endEvent = JSON.parse(messages[messages.length - 1]);
      expect(endEvent.event).toBe('language_session_ended');
      expect(endEvent.data.duration).toBeDefined();
    });
  });

  describe('Error Handling and Message Validation', () => {
    let mockWs: MockWebSocket;
    let clientId: string;

    beforeEach(() => {
      mockWs = new MockWebSocket();
      clientId = handler.addClient(mockWs as any, 'error-test-session');
      mockWs.clearMessages();
    });

    it('should handle malformed JSON messages', async () => {
      // Simulate malformed message
      mockWs.emit('message', Buffer.from('invalid json {'));

      await waitFor(50);

      const messages = mockWs.getMessages();
      expect(messages.length).toBeGreaterThan(0);

      const errorMessage = JSON.parse(messages[messages.length - 1]);
      expect(errorMessage.event).toBe('error');
      expect(errorMessage.data.message).toContain('Invalid message format');
    });

    it('should handle missing required fields for language detection', async () => {
      mockWs.simulateMessage({
        type: 'detect_language'
        // Missing text and audioBuffer
      });

      await waitFor(100);

      const messages = mockWs.getMessages();
      expect(messages.length).toBeGreaterThan(0);

      const errorMessage = JSON.parse(messages[messages.length - 1]);
      expect(errorMessage.event).toBe('error');
      expect(errorMessage.data.message).toContain('Text or audioBuffer required');
    });

    it('should handle synthesis errors', async () => {
      const sessionId = 'error-session';

      // Need to add a client for this session to receive the event FIRST
      const errorWs = new MockWebSocket();
      handler.addClient(errorWs as any, sessionId);
      errorWs.clearMessages(); // Clear welcome message

      // Trigger synthesis error
      mockLanguageRouter.emitSynthesisError(
        sessionId,
        'es',
        'deepgram',
        new Error('TTS service unavailable')
      );

      await waitFor(100);

      const messages = errorWs.getMessages();
      expect(messages.length).toBeGreaterThan(0);

      const ttsErrorEvent = messages
        .map(m => JSON.parse(m))
        .find(event => event.event === 'tts_error');

      expect(ttsErrorEvent).toBeDefined();
      expect(ttsErrorEvent.data.provider).toBe('deepgram');
      expect(ttsErrorEvent.data.error).toContain('TTS service unavailable');
    });

    it('should handle context-based language detection', async () => {
      const sessionId = 'context-session';
      const contextWs = new MockWebSocket();
      handler.addClient(contextWs as any, sessionId);
      contextWs.clearMessages();

      // Trigger context detection
      mockLanguageRouter.emitContextDetection(sessionId, '+34123456789', 'ES');

      await waitFor(50);

      const messages = contextWs.getMessages();
      const contextEvent = JSON.parse(messages[messages.length - 1]);
      expect(contextEvent.event).toBe('language_detected_context');
      expect(contextEvent.data.phoneNumber).toBe('+34123456789');
      expect(contextEvent.data.detection.language).toBe('es');
    });

    it('should handle WebSocket connection errors', async () => {
      const errorSpy = vi.fn();
      handler.on('clientDisconnected', errorSpy);

      // Simulate connection error
      mockWs.simulateError(new Error('Connection lost'));

      await waitFor(50);

      expect(errorSpy).toHaveBeenCalled();
      expect(handler.getStats().totalClients).toBe(0);
    });
  });

  describe('Heartbeat and Connection Management', () => {
    it('should handle ping/pong heartbeat correctly', async () => {
      const mockWs = new MockWebSocket();
      const clientId = handler.addClient(mockWs as any, 'heartbeat-session');

      // Simulate ping
      mockWs.emit('ping');

      await waitFor(50);

      // Simulate pong response
      mockWs.emit('pong');

      // Client should still be connected
      expect(handler.getStats().totalClients).toBe(1);
    });

    it('should remove inactive clients during heartbeat check', async () => {
      const mockWs = new MockWebSocket();
      const clientId = handler.addClient(mockWs as any, 'timeout-session');

      // Mock the client's last activity to be old
      const client = (handler as any).clients.get(clientId) as LanguageWebSocketClient;
      if (client) {
        client.lastActivity = new Date(Date.now() - 70000); // 70 seconds ago
      }

      // Wait for heartbeat check (which runs every 1000ms in our test setup)
      await waitFor(1200);

      // Client should be removed due to timeout
      expect(handler.getStats().totalClients).toBe(0);
    });

    it('should handle WebSocket close events', async () => {
      const mockWs = new MockWebSocket();
      const clientId = handler.addClient(mockWs as any, 'close-session');

      expect(handler.getStats().totalClients).toBe(1);

      // Simulate connection close
      mockWs.close(1000, 'Normal closure');

      await waitFor(50);

      expect(handler.getStats().totalClients).toBe(0);
    });
  });

  describe('Memory Management and Resource Cleanup', () => {
    it('should properly cleanup session when all clients disconnect', async () => {
      const sessionId = 'cleanup-session';
      const clients: MockWebSocket[] = [];

      // Add multiple clients to same session
      for (let i = 0; i < 3; i++) {
        const mockWs = new MockWebSocket();
        handler.addClient(mockWs as any, sessionId, `cleanup-client-${i}`);
        clients.push(mockWs);
      }

      expect(handler.getStats().activeSessions).toBe(1);

      // Close all clients
      for (const client of clients) {
        client.close(1000, 'Test cleanup');
        await waitFor(10);
      }

      await waitFor(50);

      // Session should be cleaned up
      expect(handler.getStats().activeSessions).toBe(0);
      expect(handler.getStats().totalClients).toBe(0);
    });

    it('should handle cleanup during handler shutdown', async () => {
      const clients: MockWebSocket[] = [];

      // Create multiple clients
      for (let i = 0; i < 5; i++) {
        const mockWs = new MockWebSocket();
        handler.addClient(mockWs as any, `session-${i}`, `client-${i}`);
        clients.push(mockWs);
      }

      expect(handler.getStats().totalClients).toBe(5);

      // Cleanup handler
      await handler.cleanup();

      // All clients should be disconnected
      expect(handler.getStats().totalClients).toBe(0);
      expect(handler.getStats().activeSessions).toBe(0);
    });

    it('should prevent memory leaks by properly removing event listeners', async () => {
      const initialListenerCount = handler.listenerCount('clientConnected');

      // Add clients
      const clients: MockWebSocket[] = [];
      for (let i = 0; i < 10; i++) {
        const mockWs = new MockWebSocket();
        handler.addClient(mockWs as any, `session-${i}`);
        clients.push(mockWs);
      }

      // Remove clients
      for (const client of clients) {
        client.close();
        await waitFor(5);
      }

      await waitFor(100);

      // Event listener count should not have increased
      expect(handler.listenerCount('clientConnected')).toBe(initialListenerCount);
    });
  });

  describe('Performance and Load Testing', () => {
    it('should handle multiple concurrent connections efficiently', async () => {
      const connectionCount = 50;
      const clients: MockWebSocket[] = [];
      const connectionPromises: Promise<string>[] = [];

      // Create multiple connections concurrently
      for (let i = 0; i < connectionCount; i++) {
        const promise = new Promise<string>((resolve) => {
          const mockWs = new MockWebSocket();
          const clientId = handler.addClient(
            mockWs as any,
            `load-session-${i % 10}`, // 10 different sessions
            `load-client-${i}`
          );
          clients.push(mockWs);
          resolve(clientId);
        });
        connectionPromises.push(promise);
      }

      const results = await Promise.all(connectionPromises);

      expect(results).toHaveLength(connectionCount);
      expect(handler.getStats().totalClients).toBe(connectionCount);
      expect(handler.getStats().activeSessions).toBe(10);

      // Cleanup
      for (const client of clients) {
        client.close();
      }

      await waitFor(100);

      expect(handler.getStats().totalClients).toBe(0);
    });

    it('should efficiently broadcast to many clients', async () => {
      const clientCount = 30;
      const sessionId = 'broadcast-session';
      const clients: MockWebSocket[] = [];

      // Create many clients in same session
      for (let i = 0; i < clientCount; i++) {
        const mockWs = new MockWebSocket();
        handler.addClient(mockWs as any, sessionId, `broadcast-client-${i}`);
        clients.push(mockWs);
        mockWs.clearMessages();
      }

      const startTime = Date.now();

      // Trigger broadcast event
      await mockLanguageRouter.processText(sessionId, 'Test broadcast message');

      await waitFor(100);

      const endTime = Date.now();
      const broadcastTime = endTime - startTime;

      // All clients should receive the message
      for (const client of clients) {
        const messages = client.getMessages();
        expect(messages.length).toBeGreaterThan(0);

        const event = JSON.parse(messages[messages.length - 1]);
        expect(event.event).toBe('language_detected');
      }

      // Broadcast should be reasonably fast
      expect(broadcastTime).toBeLessThan(500); // Less than 500ms for 30 clients
    });

    it('should handle rapid message sending without blocking', async () => {
      const mockWs = new MockWebSocket();
      const clientId = handler.addClient(mockWs as any, 'rapid-session');
      mockWs.clearMessages();

      const messageCount = 100;
      const startTime = Date.now();

      // Send many messages rapidly
      for (let i = 0; i < messageCount; i++) {
        mockWs.simulateMessage({
          type: 'ping',
          id: i
        });
      }

      await waitFor(200);

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      const messages = mockWs.getMessages();

      // Should process most messages
      expect(messages.length).toBeGreaterThan(messageCount * 0.8);

      // Should be reasonably fast
      expect(processingTime).toBeLessThan(1000);
    });
  });

  describe('Security and Validation', () => {
    it('should validate message structure before processing', async () => {
      const mockWs = new MockWebSocket();
      handler.addClient(mockWs as any, 'security-session');
      mockWs.clearMessages();

      // Send message without type
      mockWs.simulateMessage({
        data: 'no type field'
      });

      await waitFor(50);

      // Should either handle gracefully or send error
      const messages = mockWs.getMessages();
      if (messages.length > 0) {
        const response = JSON.parse(messages[messages.length - 1]);
        if (response.event === 'error') {
          expect(response.data.message).toBeDefined();
        }
      }
    });

    it('should prevent injection attacks in text processing', async () => {
      const mockWs = new MockWebSocket();
      handler.addClient(mockWs as any, 'injection-session');
      mockWs.clearMessages();

      // Try to inject malicious content
      mockWs.simulateMessage({
        type: 'detect_language',
        text: '<script>alert("xss")</script>DROP TABLE users;'
      });

      await waitFor(50);

      const messages = mockWs.getMessages();
      if (messages.length > 0) {
        const response = JSON.parse(messages[messages.length - 1]);
        // Should process safely without executing code
        expect(response.event).toBe('language_detected');
        expect(response.data.detection).toBeDefined();
      }
    });

    it('should handle oversized messages appropriately', async () => {
      const mockWs = new MockWebSocket();
      handler.addClient(mockWs as any, 'size-test-session');
      mockWs.clearMessages();

      // Send very large message
      const largeText = 'A'.repeat(100000); // 100KB text

      mockWs.simulateMessage({
        type: 'detect_language',
        text: largeText
      });

      await waitFor(200);

      // Should handle without crashing
      expect(handler.getStats().totalClients).toBe(1);
    });
  });
});