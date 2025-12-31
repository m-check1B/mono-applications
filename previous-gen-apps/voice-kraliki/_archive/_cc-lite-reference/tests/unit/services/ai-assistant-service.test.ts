import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AIAssistantService } from '../../../server/services/ai-assistant-service';
import { testDb, createTestCall } from '../../setup';
import { FastifyInstance } from 'fastify';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';

const skipDb = process.env.SKIP_DB_TEST_SETUP === 'true';
const describeWithDb = skipDb ? describe.skip : describe;

// Mock dependencies
const mockFastify = {
  log: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
} as unknown as FastifyInstance;

// Mock OpenAI
vi.mock('openai', () => ({
  default: vi.fn().mockImplementation(() => ({
    chat: {
      completions: {
        create: vi.fn(),
      },
    },
  })),
}));

// Mock Anthropic
vi.mock('@anthropic-ai/sdk', () => ({
  default: vi.fn().mockImplementation(() => ({
    messages: {
      create: vi.fn(),
    },
  })),
}));

describeWithDb('AIAssistantService', () => {
  let aiService: AIAssistantService;
  let mockOpenAI: OpenAI;
  let mockAnthropic: Anthropic;

  beforeEach(() => {
    // Set up environment variables
    process.env.OPENAI_API_KEY = 'test-openai-key';
    process.env.ANTHROPIC_API_KEY = 'test-anthropic-key';

    aiService = new AIAssistantService(mockFastify);

    // Get mock instances
    mockOpenAI = (aiService as any).openai;
    mockAnthropic = (aiService as any).anthropic;
  });

  afterEach(() => {
    vi.clearAllMocks();
    delete process.env.OPENAI_API_KEY;
    delete process.env.ANTHROPIC_API_KEY;
  });

  describe('processCallInput', () => {
    const mockContext = {
      callId: 'test-call-id',
      organizationId: 'test-org',
      transcripts: [
        {
          id: '1',
          callId: 'test-call-id',
          role: 'USER' as const,
          content: 'I need help with my billing',
          timestamp: new Date(),
          confidence: 0.9,
          speakerId: 'user',
          metadata: null,
        },
      ],
      customerInfo: { id: 'customer-1', name: 'John Doe' },
      agentInfo: { id: 'agent-1', name: 'Agent Smith' },
    };

    it('should process call input and return AI response', async () => {
      // Mock OpenAI responses
      mockOpenAI.chat.completions.create = vi.fn()
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'billing_inquiry' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'neutral' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'I can help you with your billing question.' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'Check account status\nReview recent charges' } }],
        });

      const response = await aiService.processCallInput(
        'I have a question about my latest bill',
        mockContext
      );

      expect(response).toBeDefined();
      expect(response.text).toContain('billing');
      expect(response.intent).toBe('billing_inquiry');
      expect(response.sentiment).toBe('neutral');
      expect(response.confidence).toBe(0.85);
      expect(response.suggestedActions).toBeDefined();
      expect(response.shouldTransfer).toBe(false);
      expect(response.metadata).toHaveProperty('processingTime');
      expect(response.metadata).toHaveProperty('model');
    });

    it('should handle AI service errors gracefully', async () => {
      // Mock OpenAI to throw error
      mockOpenAI.chat.completions.create = vi.fn().mockRejectedValue(
        new Error('OpenAI API error')
      );

      const response = await aiService.processCallInput(
        'Help me please',
        mockContext
      );

      expect(response.text).toContain('trouble understanding');
      expect(response.confidence).toBe(0.3);
      expect(response.sentiment).toBe('neutral');
      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error processing call input')
      );
    });

    it('should detect escalation scenarios', async () => {
      const negativeContext = {
        ...mockContext,
        transcripts: [
          ...mockContext.transcripts,
          {
            id: '2',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'I want to speak to a manager now!',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: null,
          },
        ],
      };

      // Mock negative sentiment and complaint intent
      mockOpenAI.chat.completions.create = vi.fn()
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'complaint' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'negative' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'I understand your frustration.' } }],
        })
        .mockResolvedValueOnce({
          choices: [{ message: { content: 'Escalate to supervisor' } }],
        });

      const response = await aiService.processCallInput(
        'I want to speak to a manager now!',
        negativeContext
      );

      expect(response.shouldTransfer).toBe(true);
      expect(response.transferTarget).toBe('supervisor');
    });
  });

  describe('analyzeIntent', () => {
    const mockContext = {
      callId: 'test-call-id',
      organizationId: 'test-org',
      transcripts: [],
    };

    it('should analyze intent using OpenAI', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'technical_support' } }],
      });

      const analyzeIntent = (aiService as any).analyzeIntent.bind(aiService);
      const intent = await analyzeIntent(
        'My internet is not working properly',
        mockContext
      );

      expect(intent).toBe('technical_support');
      expect(mockOpenAI.chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'gpt-4',
          messages: expect.arrayContaining([
            expect.objectContaining({
              role: 'system',
              content: expect.stringContaining('customer intent'),
            }),
          ]),
        })
      );
    });

    it('should fall back to keyword analysis when OpenAI fails', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockRejectedValue(
        new Error('API error')
      );

      const analyzeIntent = (aiService as any).analyzeIntent.bind(aiService);

      expect(await analyzeIntent('I need to pay my bill', mockContext)).toBe('billing_inquiry');
      expect(await analyzeIntent('Something is broken', mockContext)).toBe('technical_support');
      expect(await analyzeIntent('I want to buy something', mockContext)).toBe('sales_inquiry');
      expect(await analyzeIntent('Cancel my account', mockContext)).toBe('cancellation_request');
      expect(await analyzeIntent('I have a complaint', mockContext)).toBe('complaint');
      expect(await analyzeIntent('Hello there', mockContext)).toBe('general_inquiry');

      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error analyzing intent with AI')
      );
    });

    it('should work without OpenAI configured', async () => {
      const aiServiceNoOpenAI = new AIAssistantService(mockFastify);
      (aiServiceNoOpenAI as any).openai = null;

      const analyzeIntent = (aiServiceNoOpenAI as any).analyzeIntent.bind(aiServiceNoOpenAI);
      const intent = await analyzeIntent('I need help with billing', mockContext);

      expect(intent).toBe('billing_inquiry');
    });
  });

  describe('analyzeSentiment', () => {
    const mockContext = {
      callId: 'test-call-id',
      organizationId: 'test-org',
      transcripts: [],
    };

    it('should analyze sentiment using OpenAI', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'positive' } }],
      });

      const analyzeSentiment = (aiService as any).analyzeSentiment.bind(aiService);
      const sentiment = await analyzeSentiment(
        'Thank you so much for your excellent service!',
        mockContext
      );

      expect(sentiment).toBe('positive');
      expect(mockOpenAI.chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'gpt-3.5-turbo',
          messages: expect.arrayContaining([
            expect.objectContaining({
              role: 'system',
              content: expect.stringContaining('sentiment'),
            }),
          ]),
        })
      );
    });

    it('should fall back to keyword analysis', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockRejectedValue(
        new Error('API error')
      );

      const analyzeSentiment = (aiService as any).analyzeSentiment.bind(aiService);

      expect(await analyzeSentiment('This is great!', mockContext)).toBe('positive');
      expect(await analyzeSentiment('I hate this service', mockContext)).toBe('negative');
      expect(await analyzeSentiment('Okay, I understand', mockContext)).toBe('neutral');
    });

    it('should handle invalid AI responses', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'invalid_sentiment' } }],
      });

      const analyzeSentiment = (aiService as any).analyzeSentiment.bind(aiService);
      const sentiment = await analyzeSentiment('Test message', mockContext);

      expect(sentiment).toBe('neutral');
    });
  });

  describe('generateResponse', () => {
    const mockContext = {
      callId: 'test-call-id',
      organizationId: 'test-org',
      transcripts: [],
    };

    it('should prefer Claude for response generation', async () => {
      mockAnthropic.messages.create = vi.fn().mockResolvedValue({
        content: [{ type: 'text', text: 'I can help you with that billing question.' }],
      });

      const generateResponse = (aiService as any).generateResponse.bind(aiService);
      const response = await generateResponse(
        'I have a billing question',
        'billing_inquiry',
        mockContext
      );

      expect(response).toBe('I can help you with that billing question.');
      expect(mockAnthropic.messages.create).toHaveBeenCalled();
    });

    it('should use GPT when Claude is unavailable', async () => {
      (aiService as any).anthropic = null;

      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'I can assist with your technical issue.' } }],
      });

      const generateResponse = (aiService as any).generateResponse.bind(aiService);
      const response = await generateResponse(
        'My device is broken',
        'technical_support',
        mockContext
      );

      expect(response).toBe('I can assist with your technical issue.');
      expect(mockOpenAI.chat.completions.create).toHaveBeenCalled();
    });

    it('should fall back to template responses', async () => {
      (aiService as any).anthropic = null;
      (aiService as any).openai = null;

      const generateResponse = (aiService as any).generateResponse.bind(aiService);
      const response = await generateResponse(
        'I have a complaint',
        'complaint',
        mockContext
      );

      expect(response).toContain('apologize');
      expect(response).toContain('help resolve');
    });

    it('should handle AI service errors in response generation', async () => {
      mockAnthropic.messages.create = vi.fn().mockRejectedValue(
        new Error('Claude API error')
      );

      const generateResponse = (aiService as any).generateResponse.bind(aiService);
      const response = await generateResponse(
        'Help me',
        'general_inquiry',
        mockContext
      );

      expect(response).toContain('happy to help');
      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error generating Claude response')
      );
    });
  });

  describe('generateAgentSuggestions', () => {
    const mockContext = {
      callId: 'test-call-id',
      organizationId: 'test-org',
      transcripts: [],
    };

    it('should generate keyword-based suggestions', async () => {
      const generateAgentSuggestions = (aiService as any).generateAgentSuggestions.bind(aiService);

      let suggestions = await generateAgentSuggestions(
        'I want a refund for my purchase',
        mockContext
      );
      expect(suggestions).toContain('Offer to check refund eligibility');

      suggestions = await generateAgentSuggestions(
        'I want to speak to a manager',
        mockContext
      );
      expect(suggestions).toContain('Acknowledge request for escalation');

      suggestions = await generateAgentSuggestions(
        'I want to cancel my subscription',
        mockContext
      );
      expect(suggestions).toContain('Offer retention discount (10-20% off)');
    });

    it('should include AI-powered suggestions when available', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'Check account history\nOffer alternative solution\nSchedule follow-up' } }],
      });

      const generateAgentSuggestions = (aiService as any).generateAgentSuggestions.bind(aiService);
      const suggestions = await generateAgentSuggestions(
        'I am having issues with my service',
        mockContext
      );

      expect(suggestions).toContain('Check account history');
      expect(suggestions).toContain('Offer alternative solution');
      expect(suggestions).toContain('Schedule follow-up');
      expect(suggestions.length).toBeLessThanOrEqual(3);
    });

    it('should handle AI errors in suggestion generation', async () => {
      mockOpenAI.chat.completions.create = vi.fn().mockRejectedValue(
        new Error('API error')
      );

      const generateAgentSuggestions = (aiService as any).generateAgentSuggestions.bind(aiService);
      const suggestions = await generateAgentSuggestions(
        'I need help',
        mockContext
      );

      expect(Array.isArray(suggestions)).toBe(true);
      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error generating agent suggestions')
      );
    });
  });

  describe('checkEscalation', () => {
    it('should escalate on consecutive negative sentiment', () => {
      const mockContext = {
        callId: 'test-call-id',
        organizationId: 'test-org',
        transcripts: [
          {
            id: '1',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'This is terrible',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: { sentiment: 'negative' },
          },
          {
            id: '2',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'Worst service ever',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: { sentiment: 'negative' },
          },
          {
            id: '3',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'I hate this',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: { sentiment: 'negative' },
          },
        ],
      };

      const checkEscalation = (aiService as any).checkEscalation.bind(aiService);
      const result = checkEscalation('negative', 'general_inquiry', mockContext);

      expect(result.shouldTransfer).toBe(true);
      expect(result.target).toBe('supervisor');
    });

    it('should escalate on complaint with negative sentiment', () => {
      const mockContext = {
        callId: 'test-call-id',
        organizationId: 'test-org',
        transcripts: [],
      };

      const checkEscalation = (aiService as any).checkEscalation.bind(aiService);
      const result = checkEscalation('negative', 'complaint', mockContext);

      expect(result.shouldTransfer).toBe(true);
      expect(result.target).toBe('supervisor');
    });

    it('should escalate on explicit manager request', () => {
      const mockContext = {
        callId: 'test-call-id',
        organizationId: 'test-org',
        transcripts: [
          {
            id: '1',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'I want to speak to your supervisor',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: null,
          },
        ],
      };

      const checkEscalation = (aiService as any).checkEscalation.bind(aiService);
      const result = checkEscalation('neutral', 'general_inquiry', mockContext);

      expect(result.shouldTransfer).toBe(true);
      expect(result.target).toBe('supervisor');
    });

    it('should not escalate under normal conditions', () => {
      const mockContext = {
        callId: 'test-call-id',
        organizationId: 'test-org',
        transcripts: [
          {
            id: '1',
            callId: 'test-call-id',
            role: 'USER' as const,
            content: 'I need help with my account',
            timestamp: new Date(),
            confidence: 0.9,
            speakerId: 'user',
            metadata: { sentiment: 'neutral' },
          },
        ],
      };

      const checkEscalation = (aiService as any).checkEscalation.bind(aiService);
      const result = checkEscalation('neutral', 'general_inquiry', mockContext);

      expect(result.shouldTransfer).toBe(false);
    });
  });

  describe('generateCallSummary', () => {
    it('should generate call summary using AI', async () => {
      const testCall = await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: 'test-org',
          startTime: new Date(),
          duration: 300,
          disposition: 'resolved',
          metadata: {},
        },
      });

      await testDb.callTranscript.createMany({
        data: [
          {
            callId: testCall.id,
            role: 'USER',
            content: 'I need help with billing',
            timestamp: new Date(),
          },
          {
            callId: testCall.id,
            role: 'ASSISTANT',
            content: 'I can help you with that',
            timestamp: new Date(),
          },
        ],
      });

      mockOpenAI.chat.completions.create = vi.fn().mockResolvedValue({
        choices: [{ message: { content: 'Customer called about billing issue. Agent provided assistance and resolved the matter. No follow-up needed.' } }],
      });

      const summary = await aiService.generateCallSummary(testCall.id);

      expect(summary).toContain('billing');
      expect(summary).toContain('resolved');
      expect(mockOpenAI.chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'gpt-4',
          messages: expect.arrayContaining([
            expect.objectContaining({
              role: 'system',
              content: expect.stringContaining('call summary'),
            }),
          ]),
        })
      );
    });

    it('should handle missing call data', async () => {
      const summary = await aiService.generateCallSummary('non-existent-call');
      expect(summary).toBe('No call data available for summary.');
    });

    it('should fall back when OpenAI is unavailable', async () => {
      (aiService as any).openai = null;

      const testCall = await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: 'test-org',
          startTime: new Date(),
          duration: 120,
          disposition: 'completed',
          metadata: {},
        },
      });

      const summary = await aiService.generateCallSummary(testCall.id);

      expect(summary).toContain('Call duration: 120 seconds');
      expect(summary).toContain('Disposition: completed');
    });

    it('should handle AI service errors', async () => {
      const testCall = await testDb.call.create({
        data: {
          fromNumber: '+1234567890',
          toNumber: '+1987654321',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: 'test-org',
          startTime: new Date(),
          metadata: {},
        },
      });

      mockOpenAI.chat.completions.create = vi.fn().mockRejectedValue(
        new Error('API error')
      );

      const summary = await aiService.generateCallSummary(testCall.id);

      expect(summary).toBe('Error generating summary.');
      expect(mockFastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Error generating call summary')
      );
    });
  });

  describe('getRecentTranscripts', () => {
    it('should format recent transcripts correctly', () => {
      const transcripts = [
        {
          id: '1',
          callId: 'test-call',
          role: 'USER' as const,
          content: 'Hello',
          timestamp: new Date('2023-01-01T10:00:00Z'),
          confidence: 0.9,
          speakerId: 'user',
          metadata: null,
        },
        {
          id: '2',
          callId: 'test-call',
          role: 'ASSISTANT' as const,
          content: 'Hi there',
          timestamp: new Date('2023-01-01T10:01:00Z'),
          confidence: 0.9,
          speakerId: 'assistant',
          metadata: null,
        },
        {
          id: '3',
          callId: 'test-call',
          role: 'USER' as const,
          content: 'I need help',
          timestamp: new Date('2023-01-01T10:02:00Z'),
          confidence: 0.9,
          speakerId: 'user',
          metadata: null,
        },
      ];

      const getRecentTranscripts = (aiService as any).getRecentTranscripts.bind(aiService);
      const result = getRecentTranscripts(transcripts, 2);

      expect(result).toBe('ASSISTANT: Hi there\nUSER: I need help');
    });

    it('should handle empty transcripts', () => {
      const getRecentTranscripts = (aiService as any).getRecentTranscripts.bind(aiService);
      const result = getRecentTranscripts([], 5);

      expect(result).toBe('');
    });
  });
});
