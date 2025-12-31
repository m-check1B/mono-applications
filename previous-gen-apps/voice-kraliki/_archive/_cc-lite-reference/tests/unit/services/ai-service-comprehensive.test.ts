import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AIService } from '@server/lib/ai-service';
import fs from 'fs';
import path from 'path';

// Mock OpenAI
const mockOpenAI = {
  chat: {
    completions: {
      create: vi.fn()
    }
  },
  audio: {
    transcriptions: {
      create: vi.fn()
    },
    speech: {
      create: vi.fn()
    }
  }
};

vi.mock('openai', () => {
  return {
    default: vi.fn(() => mockOpenAI)
  };
});

// Mock fs
vi.mock('fs', () => ({
  writeFileSync: vi.fn(),
  createReadStream: vi.fn(),
  existsSync: vi.fn().mockReturnValue(true),
  unlinkSync: vi.fn(),
  default: {
    writeFileSync: vi.fn(),
    createReadStream: vi.fn(),
    existsSync: vi.fn().mockReturnValue(true),
    unlinkSync: vi.fn()
  }
}));

// Mock path
vi.mock('path', () => ({
  join: vi.fn((...args) => args.join('/')),
  default: {
    join: vi.fn((...args) => args.join('/'))
  }
}));

// Mock logger
vi.mock('@server/services/logger-service', () => ({
  systemLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

describe('AIService', () => {
  let aiService: AIService;
  let originalEnv: string | undefined;

  beforeEach(() => {
    originalEnv = process.env.OPENAI_API_KEY;
    process.env.OPENAI_API_KEY = 'test-api-key';

    vi.clearAllMocks();

    // Reset mock implementations
    mockOpenAI.chat.completions.create.mockResolvedValue({
      choices: [{
        message: {
          content: 'AI response text',
          function_call: null
        }
      }]
    });

    mockOpenAI.audio.transcriptions.create.mockResolvedValue({
      text: 'Transcribed text'
    });

    mockOpenAI.audio.speech.create.mockResolvedValue({
      arrayBuffer: () => Promise.resolve(new ArrayBuffer(1024))
    });

    aiService = new AIService();
  });

  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.OPENAI_API_KEY = originalEnv;
    } else {
      delete process.env.OPENAI_API_KEY;
    }
    vi.clearAllMocks();
  });

  describe('Constructor', () => {
    it('should initialize with valid API key', () => {
      expect(aiService).toBeDefined();
    });

    it('should throw error without API key', () => {
      delete process.env.OPENAI_API_KEY;

      expect(() => new AIService()).toThrow(
        'OPENAI_API_KEY environment variable is required'
      );
    });

    it('should throw error with empty API key', () => {
      process.env.OPENAI_API_KEY = '';

      expect(() => new AIService()).toThrow(
        'OPENAI_API_KEY environment variable is required'
      );
    });

    it('should throw error with whitespace-only API key', () => {
      process.env.OPENAI_API_KEY = '   ';

      expect(() => new AIService()).toThrow(
        'OPENAI_API_KEY environment variable is required'
      );
    });
  });

  describe('generateGreeting', () => {
    it('should generate greeting message', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: 'Hello! Welcome to our service. How can I help you today?'
          }
        }]
      });

      const result = await aiService.generateGreeting();

      expect(result).toEqual({
        text: 'Hello! Welcome to our service. How can I help you today?',
        type: 'standard'
      });

      expect(mockOpenAI.chat.completions.create).toHaveBeenCalledWith({
        model: 'gpt-3.5-turbo',
        messages: [{
          role: 'system',
          content: expect.stringContaining('call center AI assistant')
        }],
        max_tokens: 50,
        temperature: 0.7
      });
    });

    it('should handle OpenAI API errors with fallback', async () => {
      mockOpenAI.chat.completions.create.mockRejectedValue(new Error('API Error'));

      const result = await aiService.generateGreeting();

      expect(result).toEqual({
        text: 'Hello! Thank you for calling. How can I assist you today?',
        type: 'standard'
      });
    });

    it('should handle empty response with fallback', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: ''
          }
        }]
      });

      const result = await aiService.generateGreeting();

      expect(result.text).toBe('Hello! Thank you for calling. How can I assist you today?');
    });
  });

  describe('speechToText', () => {
    const mockAudioBuffer = Buffer.from('mock audio data', 'utf8');

    beforeEach(() => {
      vi.mocked(fs.createReadStream).mockReturnValue({} as any);
    });

    it('should transcribe audio buffer', async () => {
      mockOpenAI.audio.transcriptions.create.mockResolvedValue({
        text: 'Hello, I need help with my account'
      });

      const result = await aiService.speechToText(mockAudioBuffer);

      expect(result).toBe('Hello, I need help with my account');
      expect(fs.writeFileSync).toHaveBeenCalledWith(
        expect.stringContaining('/tmp/audio_'),
        mockAudioBuffer
      );
      expect(mockOpenAI.audio.transcriptions.create).toHaveBeenCalledWith({
        file: expect.any(Object),
        model: 'whisper-1',
        language: 'en'
      });
      expect(fs.unlinkSync).toHaveBeenCalled();
    });

    it('should clean up temporary file even on error', async () => {
      mockOpenAI.audio.transcriptions.create.mockRejectedValue(new Error('Transcription failed'));

      await aiService.speechToText(mockAudioBuffer);

      expect(fs.unlinkSync).toHaveBeenCalled();
    });

    it('should return null for small audio buffers', async () => {
      const smallBuffer = Buffer.from('small');

      const result = await aiService.speechToText(smallBuffer);

      expect(result).toBeNull();
      expect(mockOpenAI.audio.transcriptions.create).not.toHaveBeenCalled();
    });

    it('should return null on transcription errors', async () => {
      mockOpenAI.audio.transcriptions.create.mockRejectedValue(new Error('API Error'));

      const result = await aiService.speechToText(mockAudioBuffer);

      expect(result).toBeNull();
    });

    it('should handle empty transcription response', async () => {
      mockOpenAI.audio.transcriptions.create.mockResolvedValue({
        text: ''
      });

      const result = await aiService.speechToText(mockAudioBuffer);

      expect(result).toBeNull();
    });
  });

  describe('generateResponse', () => {
    const callId = 'test-call-123';

    it('should generate AI response with function calling', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: 'I can help you with pricing information.',
            function_call: {
              arguments: JSON.stringify({
                intent: 'pricing_inquiry',
                shouldTransfer: true,
                transferTo: 'sales',
                confidence: 0.9
              })
            }
          }
        }]
      });

      const result = await aiService.generateResponse('How much does it cost?', callId);

      expect(result).toEqual({
        text: 'I can help you with pricing information.',
        confidence: 0.9,
        intent: 'pricing_inquiry',
        shouldTransfer: true,
        transferTo: 'sales'
      });
    });

    it('should handle function call parsing errors', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: 'I can help you.',
            function_call: {
              arguments: 'invalid json'
            }
          }
        }]
      });

      const result = await aiService.generateResponse('Hello', callId);

      expect(result).toEqual({
        text: 'I can help you.',
        confidence: 0.8,
        intent: 'general_inquiry'
      });
    });

    it('should maintain conversation context', async () => {
      await aiService.generateResponse('First message', callId);
      await aiService.generateResponse('Second message', callId);

      const context = aiService.getContext(callId);
      expect(context).toHaveLength(4); // 2 user messages + 2 assistant responses
      expect(context[0].role).toBe('user');
      expect(context[0].content).toBe('First message');
    });

    it('should limit conversation context to last 6 messages', async () => {
      // Add many messages
      for (let i = 1; i <= 10; i++) {
        await aiService.generateResponse(`Message ${i}`, callId);
      }

      // Check that GPT is called with limited context
      const lastCall = mockOpenAI.chat.completions.create.mock.calls.slice(-1)[0];
      const messages = lastCall[0].messages;

      // Should have system message + max 6 conversation messages
      expect(messages.length).toBeLessThanOrEqual(7);
    });

    it('should throw error on OpenAI API failure', async () => {
      mockOpenAI.chat.completions.create.mockRejectedValue(new Error('API Error'));

      await expect(aiService.generateResponse('Hello', callId))
        .rejects.toThrow('API Error');
    });
  });

  describe('textToSpeech', () => {
    it('should convert text to speech', async () => {
      const mockArrayBuffer = new ArrayBuffer(1024);
      mockOpenAI.audio.speech.create.mockResolvedValue({
        arrayBuffer: () => Promise.resolve(mockArrayBuffer)
      });

      const result = await aiService.textToSpeech('Hello world');

      expect(result).toBeInstanceOf(Buffer);
      expect(result?.length).toBe(1024);
      expect(mockOpenAI.audio.speech.create).toHaveBeenCalledWith({
        model: 'tts-1',
        voice: 'alloy',
        input: 'Hello world',
        response_format: 'mp3'
      });
    });

    it('should return null on TTS errors', async () => {
      mockOpenAI.audio.speech.create.mockRejectedValue(new Error('TTS Error'));

      const result = await aiService.textToSpeech('Hello world');

      expect(result).toBeNull();
    });
  });

  describe('analyzeSentiment', () => {
    it('should analyze sentiment correctly', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: JSON.stringify({
              sentiment: 'positive',
              confidence: 0.85,
              emotions: ['happy', 'satisfied']
            })
          }
        }]
      });

      const result = await aiService.analyzeSentiment('I love your service!');

      expect(result).toEqual({
        sentiment: 'positive',
        confidence: 0.85,
        emotions: ['happy', 'satisfied']
      });
    });

    it('should handle invalid JSON response', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: 'invalid json response'
          }
        }]
      });

      const result = await aiService.analyzeSentiment('Some text');

      expect(result).toEqual({
        sentiment: 'neutral',
        confidence: 0.5
      });
    });

    it('should return neutral sentiment on API errors', async () => {
      mockOpenAI.chat.completions.create.mockRejectedValue(new Error('API Error'));

      const result = await aiService.analyzeSentiment('Some text');

      expect(result).toEqual({
        sentiment: 'neutral',
        confidence: 0.5
      });
    });
  });

  describe('generateCallSummary', () => {
    const callId = 'test-call-summary';

    beforeEach(() => {
      // Add some conversation context
      const context = [
        { role: 'user', content: 'I need help with billing', timestamp: new Date() },
        { role: 'assistant', content: 'I can help with that', timestamp: new Date() },
        { role: 'user', content: 'Thank you', timestamp: new Date() }
      ];
      aiService['conversationContext'].set(callId, context);
    });

    it('should generate call summary', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: [{
          message: {
            content: JSON.stringify({
              summary: 'Customer requested billing assistance',
              keyPoints: ['Billing inquiry', 'Issue resolved'],
              outcome: 'Resolved',
              nextSteps: ['Monitor billing status']
            })
          }
        }]
      });

      const result = await aiService.generateCallSummary(callId);

      expect(result).toEqual({
        summary: 'Customer requested billing assistance',
        keyPoints: ['Billing inquiry', 'Issue resolved'],
        outcome: 'Resolved',
        nextSteps: ['Monitor billing status']
      });
    });

    it('should return null for empty conversation', async () => {
      const result = await aiService.generateCallSummary('empty-call');

      expect(result).toBeNull();
    });

    it('should return fallback summary on errors', async () => {
      mockOpenAI.chat.completions.create.mockRejectedValue(new Error('API Error'));

      const result = await aiService.generateCallSummary(callId);

      expect(result).toEqual({
        summary: 'Call completed with AI assistance',
        keyPoints: ['Customer inquiry processed'],
        outcome: 'AI handled',
        nextSteps: ['Monitor for follow-up']
      });
    });
  });

  describe('Context Management', () => {
    const callId = 'context-test';

    it('should clear conversation context', () => {
      aiService['conversationContext'].set(callId, [
        { role: 'user', content: 'Test message', timestamp: new Date() }
      ]);

      aiService.clearContext(callId);

      expect(aiService.getContext(callId)).toEqual([]);
    });

    it('should get conversation context', () => {
      const context = [
        { role: 'user', content: 'Test message', timestamp: new Date() }
      ];
      aiService['conversationContext'].set(callId, context);

      const result = aiService.getContext(callId);

      expect(result).toEqual(context);
    });

    it('should return empty array for non-existent context', () => {
      const result = aiService.getContext('non-existent');

      expect(result).toEqual([]);
    });
  });

  describe('shouldEscalateToHuman', () => {
    const callId = 'escalation-test';

    it('should escalate for long conversations', () => {
      const longContext = Array.from({ length: 12 }, (_, i) => ({
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}`,
        timestamp: new Date()
      }));
      aiService['conversationContext'].set(callId, longContext);

      const result = aiService.shouldEscalateToHuman(callId);

      expect(result).toBe(true);
    });

    it('should escalate for frustrated customers', () => {
      const context = [
        { role: 'user', content: 'I am frustrated with this service', timestamp: new Date() },
        { role: 'assistant', content: 'I understand', timestamp: new Date() },
        { role: 'user', content: 'I want to speak to a human agent', timestamp: new Date() }
      ];
      aiService['conversationContext'].set(callId, context);

      const result = aiService.shouldEscalateToHuman(callId);

      expect(result).toBe(true);
    });

    it('should not escalate for normal conversations', () => {
      const context = [
        { role: 'user', content: 'Hello', timestamp: new Date() },
        { role: 'assistant', content: 'How can I help?', timestamp: new Date() }
      ];
      aiService['conversationContext'].set(callId, context);

      const result = aiService.shouldEscalateToHuman(callId);

      expect(result).toBe(false);
    });

    it('should not escalate when no context exists', () => {
      const result = aiService.shouldEscalateToHuman('no-context');

      expect(result).toBe(false);
    });
  });

  describe('Error Handling and Resilience', () => {
    it('should handle network timeouts gracefully', async () => {
      mockOpenAI.chat.completions.create.mockRejectedValue(new Error('Request timeout'));

      await expect(aiService.generateResponse('Hello', 'test-call'))
        .rejects.toThrow('Request timeout');
    });

    it('should handle malformed API responses', async () => {
      mockOpenAI.chat.completions.create.mockResolvedValue({
        choices: []
      });

      const result = await aiService.generateResponse('Hello', 'test-call');

      expect(result).toEqual({
        text: 'I understand. Let me help you with that.',
        confidence: 0.8,
        intent: 'general_inquiry'
      });
    });

    it('should handle rate limiting errors', async () => {
      const rateLimitError = new Error('Rate limit exceeded');
      rateLimitError.name = 'RateLimitError';
      mockOpenAI.chat.completions.create.mockRejectedValue(rateLimitError);

      await expect(aiService.generateResponse('Hello', 'test-call'))
        .rejects.toThrow('Rate limit exceeded');
    });
  });

  describe('Performance and Memory Management', () => {
    it('should handle multiple concurrent calls', async () => {
      const promises = Array.from({ length: 10 }, (_, i) =>
        aiService.generateResponse(`Message ${i}`, `call-${i}`)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result).toHaveProperty('text');
        expect(result).toHaveProperty('confidence');
      });
    });

    it('should manage memory for conversation contexts', () => {
      // Create many conversations
      for (let i = 0; i < 100; i++) {
        aiService['conversationContext'].set(`call-${i}`, [
          { role: 'user', content: `Message ${i}`, timestamp: new Date() }
        ]);
      }

      expect(aiService['conversationContext'].size).toBe(100);

      // Clear some contexts
      for (let i = 0; i < 50; i++) {
        aiService.clearContext(`call-${i}`);
      }

      expect(aiService['conversationContext'].size).toBe(50);
    });
  });
});