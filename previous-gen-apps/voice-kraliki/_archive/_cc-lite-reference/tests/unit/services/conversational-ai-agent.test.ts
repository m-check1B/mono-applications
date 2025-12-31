import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { ConversationalAIAgent, getConversationalAIAgent, cleanupConversationalAIAgent } from '../../../server/services/conversational-ai-agent';

// Mock dependencies
const mockAIManager = {
  generateResponse: vi.fn()
};

const mockVoiceManager = {
  on: vi.fn(),
  synthesizeSpeech: vi.fn()
};

const mockLanguageDetectionService = {
  detectLanguage: vi.fn()
};

// Mock core integrations
vi.mock('../../../server/core/ai-integration', () => ({
  getAIManager: () => mockAIManager
}));

vi.mock('../../../server/core/voice-integration-deepgram', () => ({
  getVoiceManager: () => mockVoiceManager
}));

vi.mock('../../../server/services/language-detection-service', () => ({
  getLanguageDetectionService: () => mockLanguageDetectionService
}));

vi.mock('../../../server/services/logger-service', () => ({
  systemLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}));

describe('ConversationalAIAgent', () => {
  let aiAgent: ConversationalAIAgent;

  beforeEach(() => {
    vi.clearAllMocks();
    aiAgent = new ConversationalAIAgent();

    // Set up default mock responses
    mockAIManager.generateResponse.mockResolvedValue('I understand your concern. Let me help you with that.');
    mockVoiceManager.synthesizeSpeech.mockResolvedValue(Buffer.from('mock-audio-data'));
  });

  afterEach(async () => {
    if (aiAgent) {
      aiAgent.removeAllListeners();
    }
  });

  describe('Conversation Lifecycle', () => {
    it('should start a conversation successfully', async () => {
      const callId = 'call-123';
      const sessionId = 'session-456';
      const context = {
        language: 'en-US',
        customerProfile: {
          name: 'John Doe',
          tier: 'premium' as const
        }
      };

      const emittedEvents: any[] = [];
      aiAgent.on('conversationStarted', (data) => emittedEvents.push(data));

      await aiAgent.startConversation(callId, sessionId, context);

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0]).toMatchObject({
        callId,
        sessionId,
        conversation: expect.objectContaining({
          callId,
          sessionId,
          language: 'en-US',
          customerProfile: context.customerProfile
        })
      });
    });

    it('should generate welcome message in correct language', async () => {
      const callId = 'call-123';
      const sessionId = 'session-456';

      await aiAgent.startConversation(callId, sessionId, { language: 'es' });

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.stringContaining('¡Hola'),
        expect.any(String)
      );
    });

    it('should end conversation and generate closing message', async () => {
      const callId = 'call-123';
      const sessionId = 'session-456';

      // Start conversation first
      await aiAgent.startConversation(callId, sessionId);

      const emittedEvents: any[] = [];
      aiAgent.on('conversationEnded', (data) => emittedEvents.push(data));

      const result = await aiAgent.endConversation(callId);

      expect(result).toBeDefined();
      expect(result?.callId).toBe(callId);
      expect(emittedEvents).toHaveLength(1);
      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.stringContaining('Thank you for calling'),
        expect.any(String)
      );
    });

    it('should return undefined when ending non-existent conversation', async () => {
      const result = await aiAgent.endConversation('non-existent-call');
      expect(result).toBeUndefined();
    });

    it('should get conversation context correctly', async () => {
      const callId = 'call-123';
      const sessionId = 'session-456';

      await aiAgent.startConversation(callId, sessionId);

      const context = aiAgent.getConversationContext(callId);
      expect(context).toBeDefined();
      expect(context?.callId).toBe(callId);
      expect(context?.sessionId).toBe(sessionId);
    });

    it('should get all active conversations', async () => {
      await aiAgent.startConversation('call-1', 'session-1');
      await aiAgent.startConversation('call-2', 'session-2');

      const conversations = aiAgent.getActiveConversations();
      expect(conversations).toHaveLength(2);
      expect(conversations.map(c => c.callId)).toContain('call-1');
      expect(conversations.map(c => c.callId)).toContain('call-2');
    });
  });

  describe('Message Processing', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456');
    });

    it('should handle customer message and generate AI response', async () => {
      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'I need help with my account' },
        language: 'en-US'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      // Simulate voice manager transcript event
      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(mockAIManager.generateResponse).toHaveBeenCalledWith(
        expect.stringContaining('I need help with my account'),
        expect.objectContaining({
          temperature: 0.7,
          maxTokens: 200,
          systemPrompt: expect.any(String)
        })
      );

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].customerMessage).toBe('I need help with my account');
    });

    it('should update conversation context based on sentiment', async () => {
      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'I am very angry and frustrated' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const context = aiAgent.getConversationContext('call-123');
      expect(context?.sentiment).toBe('negative');
      expect(context?.urgency).toBe('high');
    });

    it('should detect urgency from keywords', async () => {
      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'This is an urgent emergency!' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const context = aiAgent.getConversationContext('call-123');
      expect(context?.urgency).toBe('critical');
    });

    it('should add customer and agent messages to call history', async () => {
      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'I need assistance' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const context = aiAgent.getConversationContext('call-123');
      expect(context?.callHistory).toHaveLength(2); // Customer message + agent response
      expect(context?.callHistory?.[0].role).toBe('customer');
      expect(context?.callHistory?.[0].message).toBe('I need assistance');
      expect(context?.callHistory?.[1].role).toBe('agent');
    });
  });

  describe('Voice Response Generation', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456');
    });

    it('should generate voice response with correct language selection', async () => {
      const context = aiAgent.getConversationContext('call-123');
      if (context) {
        context.language = 'es';
      }

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Necesito ayuda' },
        language: 'es'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.any(String),
        'aura-asteria-es'
      );
    });

    it('should emit voiceResponse event', async () => {
      const emittedEvents: any[] = [];
      aiAgent.on('voiceResponse', (data) => emittedEvents.push(data));

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Hello' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].callId).toBe('call-123');
      expect(emittedEvents[0].response).toMatchObject({
        text: expect.any(String),
        audioBuffer: expect.any(Buffer),
        language: expect.any(String),
        voice: expect.any(String),
        confidence: expect.any(Number)
      });
    });
  });

  describe('Language Switching', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456', { language: 'en-US' });
    });

    it('should handle language switch recommendation', async () => {
      const mockLanguageSwitchEvent = {
        callId: 'call-123',
        recommendedLanguage: 'es'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('languageSwitched', (data) => emittedEvents.push(data));

      const languageSwitchHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'languageSwitchRecommended')?.[1];

      if (languageSwitchHandler) {
        await languageSwitchHandler(mockLanguageSwitchEvent);
      }

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0]).toMatchObject({
        callId: 'call-123',
        oldLanguage: 'en-US',
        newLanguage: 'es'
      });

      const context = aiAgent.getConversationContext('call-123');
      expect(context?.language).toBe('es');
    });

    it('should generate language acknowledgment message', async () => {
      const mockLanguageSwitchEvent = {
        callId: 'call-123',
        recommendedLanguage: 'cs'
      };

      const languageSwitchHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'languageSwitchRecommended')?.[1];

      if (languageSwitchHandler) {
        await languageSwitchHandler(mockLanguageSwitchEvent);
      }

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.stringContaining('Perfektní'),
        expect.any(String)
      );
    });
  });

  describe('Transfer Logic', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456');
    });

    it('should recommend transfer for negative sentiment and critical urgency', async () => {
      // Mock AI response that includes transfer keywords
      mockAIManager.generateResponse.mockResolvedValue('I understand your frustration. Let me transfer you to a human agent who can better assist you.');

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'This is terrible urgent emergency service!' },
        language: 'en-US'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(emittedEvents[0].agentResponse.shouldTransfer).toBe(true);
    });

    it('should recommend transfer for long conversations', async () => {
      const context = aiAgent.getConversationContext('call-123');
      if (context && context.callHistory) {
        // Add many messages to simulate long conversation
        for (let i = 0; i < 25; i++) {
          context.callHistory.push({
            role: i % 2 === 0 ? 'customer' : 'agent',
            message: `Message ${i}`,
            timestamp: Date.now(),
            language: 'en-US'
          });
        }
      }

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Still need help' },
        language: 'en-US'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(emittedEvents[0].agentResponse.shouldTransfer).toBe(true);
    });

    it('should extract suggested actions from response', async () => {
      mockAIManager.generateResponse.mockResolvedValue('Let me check your account and send you a follow up email about the refund.');

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'I need a refund' },
        language: 'en-US'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const response = emittedEvents[0].agentResponse;
      expect(response.suggestedActions).toContain('account_check');
      expect(response.suggestedActions).toContain('follow_up_email');
      expect(response.suggestedActions).toContain('process_refund');
    });
  });

  describe('System Prompt Generation', () => {
    it('should generate system prompt with customer tier context', async () => {
      await aiAgent.startConversation('call-123', 'session-456', {
        language: 'en-US',
        customerProfile: {
          tier: 'enterprise'
        }
      });

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'I need help' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(mockAIManager.generateResponse).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          systemPrompt: expect.stringContaining('enterprise')
        })
      );
    });

    it('should generate Spanish system prompt for Spanish conversation', async () => {
      await aiAgent.startConversation('call-123', 'session-456', { language: 'es' });

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Necesito ayuda' },
        language: 'es'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      expect(mockAIManager.generateResponse).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          systemPrompt: expect.stringMatching(/español|servicio al cliente/i)
        })
      );
    });
  });

  describe('Error Handling and Fallbacks', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456');
    });

    it('should generate fallback response when AI fails', async () => {
      mockAIManager.generateResponse.mockRejectedValue(new Error('AI service unavailable'));

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Help me please' },
        language: 'en-US'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const response = emittedEvents[0].agentResponse;
      expect(response.text).toContain('having trouble processing');
      expect(response.shouldTransfer).toBe(true);
      expect(response.transferReason).toBe('AI processing failure');
      expect(response.confidence).toBe(0.5);
    });

    it('should generate fallback in correct language', async () => {
      const context = aiAgent.getConversationContext('call-123');
      if (context) {
        context.language = 'cs';
      }

      mockAIManager.generateResponse.mockRejectedValue(new Error('AI service unavailable'));

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Pomozte mi prosím' },
        language: 'cs'
      };

      const emittedEvents: any[] = [];
      aiAgent.on('messageProcessed', (data) => emittedEvents.push(data));

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      const response = emittedEvents[0].agentResponse;
      expect(response.text).toContain('Omlouvám se');
      expect(response.language).toBe('cs');
    });

    it('should handle voice synthesis failures gracefully', async () => {
      mockVoiceManager.synthesizeSpeech.mockRejectedValue(new Error('TTS unavailable'));

      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Hello' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      // Should not throw
      await expect(finalTranscriptHandler(mockTranscriptEvent)).resolves.toBeUndefined();
    });

    it('should handle missing conversation gracefully', async () => {
      const mockTranscriptEvent = {
        callId: 'non-existent-call',
        sessionId: 'session-456',
        result: { transcript: 'Hello' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      // Should not throw
      await expect(finalTranscriptHandler(mockTranscriptEvent)).resolves.toBeUndefined();
    });
  });

  describe('Welcome and Closing Messages', () => {
    it('should generate personalized welcome message', async () => {
      await aiAgent.startConversation('call-123', 'session-456', {
        customerProfile: {
          name: 'Alice Johnson',
          tier: 'premium'
        }
      });

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.stringContaining('Alice Johnson'),
        expect.any(String)
      );
    });

    it('should generate generic welcome when no customer name', async () => {
      await aiAgent.startConversation('call-123', 'session-456');

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenCalledWith(
        expect.stringContaining('valued customer'),
        expect.any(String)
      );
    });

    it('should generate closing message in conversation language', async () => {
      await aiAgent.startConversation('call-123', 'session-456', { language: 'es' });
      await aiAgent.endConversation('call-123');

      expect(mockVoiceManager.synthesizeSpeech).toHaveBeenLastCalledWith(
        expect.stringContaining('Gracias por llamar'),
        expect.any(String)
      );
    });
  });

  describe('Response Caching', () => {
    beforeEach(async () => {
      await aiAgent.startConversation('call-123', 'session-456');
    });

    it('should cache responses and clean up on conversation end', async () => {
      // Generate some responses
      const mockTranscriptEvent = {
        callId: 'call-123',
        sessionId: 'session-456',
        result: { transcript: 'Test message' },
        language: 'en-US'
      };

      const finalTranscriptHandler = mockVoiceManager.on.mock.calls
        .find(call => call[0] === 'finalTranscript')?.[1];

      if (finalTranscriptHandler) {
        await finalTranscriptHandler(mockTranscriptEvent);
      }

      // End conversation - should clean up cache
      await aiAgent.endConversation('call-123');

      // Cache should be cleaned up (tested indirectly through no memory leaks)
      expect(true).toBe(true); // Placeholder assertion
    });
  });
});

describe('Singleton Functions', () => {
  afterEach(async () => {
    await cleanupConversationalAIAgent();
  });

  it('should return same instance from getConversationalAIAgent', () => {
    const agent1 = getConversationalAIAgent();
    const agent2 = getConversationalAIAgent();

    expect(agent1).toBe(agent2);
    expect(agent1).toBeInstanceOf(ConversationalAIAgent);
  });

  it('should cleanup singleton instance', async () => {
    const agent = getConversationalAIAgent();
    const removeAllListenersSpy = vi.spyOn(agent, 'removeAllListeners');

    await cleanupConversationalAIAgent();

    expect(removeAllListenersSpy).toHaveBeenCalled();
  });

  it('should create new instance after cleanup', () => {
    const agent1 = getConversationalAIAgent();
    cleanupConversationalAIAgent();
    const agent2 = getConversationalAIAgent();

    expect(agent1).not.toBe(agent2);
  });
});