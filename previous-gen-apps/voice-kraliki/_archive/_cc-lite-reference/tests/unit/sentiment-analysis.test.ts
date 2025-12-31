/**
 * Sentiment Analysis Unit Tests for Voice by Kraliki
 * Tests sentiment detection accuracy, edge cases, and performance
 */
import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { SentimentAnalyzer } from '../../server/services/sentiment-analyzer';
import { OpenAIProvider } from '../../server/providers/openai-provider';
import { AnthropicProvider } from '../../server/providers/anthropic-provider';

// Mock the external providers
vi.mock('../../server/providers/openai-provider');
vi.mock('../../server/providers/anthropic-provider');

describe('Sentiment Analysis Unit Tests', () => {
  let sentimentAnalyzer: SentimentAnalyzer;
  let mockOpenAIProvider: vi.Mocked<OpenAIProvider>;
  let mockAnthropicProvider: vi.Mocked<AnthropicProvider>;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Create mock providers
    mockOpenAIProvider = {
      analyzeSentiment: vi.fn(),
      isAvailable: vi.fn().mockReturnValue(true),
      getRateLimit: vi.fn().mockReturnValue({ remaining: 100, resetTime: Date.now() + 3600000 })
    } as any;

    mockAnthropicProvider = {
      analyzeSentiment: vi.fn(),
      isAvailable: vi.fn().mockReturnValue(true),
      getRateLimit: vi.fn().mockReturnValue({ remaining: 100, resetTime: Date.now() + 3600000 })
    } as any;

    // Initialize sentiment analyzer with mocked providers
    sentimentAnalyzer = new SentimentAnalyzer({
      providers: {
        openai: mockOpenAIProvider,
        anthropic: mockAnthropicProvider
      },
      defaultProvider: 'openai',
      confidenceThreshold: 0.7,
      enableEmotionDetection: true,
      enableSarcasmDetection: true
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Basic Sentiment Detection', () => {
    test('should correctly identify positive sentiment', async () => {
      const positiveText = 'I am extremely happy with your excellent service! Thank you so much!';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'positive',
        confidence: 0.95,
        score: 0.85,
        emotions: {
          joy: 0.9,
          satisfaction: 0.8,
          gratitude: 0.85
        }
      });

      const result = await sentimentAnalyzer.analyze(positiveText);

      expect(result.sentiment).toBe('positive');
      expect(result.confidence).toBeGreaterThan(0.9);
      expect(result.score).toBeGreaterThan(0.7);
      expect(result.emotions.joy).toBeGreaterThan(0.8);
      expect(mockOpenAIProvider.analyzeSentiment).toHaveBeenCalledWith(
        positiveText,
        expect.objectContaining({
          enableEmotionDetection: true,
          confidenceThreshold: 0.7
        })
      );
    });

    test('should correctly identify negative sentiment', async () => {
      const negativeText = 'This is absolutely terrible! I hate this service and want my money back immediately!';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'negative',
        confidence: 0.92,
        score: -0.88,
        emotions: {
          anger: 0.9,
          frustration: 0.85,
          disappointment: 0.8
        }
      });

      const result = await sentimentAnalyzer.analyze(negativeText);

      expect(result.sentiment).toBe('negative');
      expect(result.confidence).toBeGreaterThan(0.9);
      expect(result.score).toBeLessThan(-0.7);
      expect(result.emotions.anger).toBeGreaterThan(0.8);
    });

    test('should correctly identify neutral sentiment', async () => {
      const neutralText = 'I need to update my account information. What is the process for that?';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'neutral',
        confidence: 0.85,
        score: 0.1,
        emotions: {
          curiosity: 0.3,
          neutral: 0.9
        }
      });

      const result = await sentimentAnalyzer.analyze(neutralText);

      expect(result.sentiment).toBe('neutral');
      expect(result.confidence).toBeGreaterThan(0.7);
      expect(result.score).toBeGreaterThanOrEqual(-0.3);
      expect(result.score).toBeLessThanOrEqual(0.3);
    });

    test('should handle mixed sentiment appropriately', async () => {
      const mixedText = 'I love the product features but I am frustrated with the poor customer support.';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'mixed',
        confidence: 0.8,
        score: 0.2,
        emotions: {
          satisfaction: 0.6,
          frustration: 0.7,
          love: 0.5
        },
        mixed_emotions: true,
        positive_aspects: ['product features'],
        negative_aspects: ['customer support']
      });

      const result = await sentimentAnalyzer.analyze(mixedText);

      expect(result.sentiment).toBe('mixed');
      expect(result.mixed_emotions).toBe(true);
      expect(result.positive_aspects).toContain('product features');
      expect(result.negative_aspects).toContain('customer support');
      expect(result.emotions.satisfaction).toBeGreaterThan(0.5);
      expect(result.emotions.frustration).toBeGreaterThan(0.5);
    });
  });

  describe('Advanced Emotion Detection', () => {
    test('should detect complex emotional states', async () => {
      const emotionalText = 'I am so disappointed and hurt by this betrayal of trust. This makes me anxious about future interactions.';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'negative',
        confidence: 0.9,
        score: -0.75,
        emotions: {
          disappointment: 0.9,
          hurt: 0.8,
          anxiety: 0.7,
          betrayal: 0.85,
          trust_loss: 0.9
        },
        emotional_complexity: 'high',
        primary_emotion: 'disappointment',
        secondary_emotions: ['hurt', 'anxiety', 'betrayal']
      });

      const result = await sentimentAnalyzer.analyze(emotionalText);

      expect(result.emotions.disappointment).toBeGreaterThan(0.8);
      expect(result.emotions.anxiety).toBeGreaterThan(0.6);
      expect(result.emotional_complexity).toBe('high');
      expect(result.primary_emotion).toBe('disappointment');
      expect(result.secondary_emotions).toContain('hurt');
    });

    test('should detect subtle emotions in professional contexts', async () => {
      const professionalText = 'While I appreciate your prompt response, I must express my concern about the proposed solution.';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'neutral',
        confidence: 0.75,
        score: -0.1,
        emotions: {
          appreciation: 0.6,
          concern: 0.7,
          professionalism: 0.9,
          politeness: 0.85,
          subtle_disagreement: 0.6
        },
        tone: 'professional',
        politeness_level: 'high'
      });

      const result = await sentimentAnalyzer.analyze(professionalText);

      expect(result.emotions.appreciation).toBeGreaterThan(0.5);
      expect(result.emotions.concern).toBeGreaterThan(0.6);
      expect(result.tone).toBe('professional');
      expect(result.politeness_level).toBe('high');
    });

    test('should detect emotional escalation patterns', async () => {
      const escalatingTexts = [
        'I have a small issue with my account.',
        'This issue is becoming quite frustrating.',
        'I am getting very annoyed by this problem!',
        'This is completely unacceptable! I demand to speak to a manager!'
      ];

      const mockResponses = [
        { sentiment: 'neutral', confidence: 0.8, score: 0.0, emotions: { mild_concern: 0.4 }, escalation_level: 0 },
        { sentiment: 'negative', confidence: 0.85, score: -0.4, emotions: { frustration: 0.6 }, escalation_level: 1 },
        { sentiment: 'negative', confidence: 0.9, score: -0.7, emotions: { annoyance: 0.8 }, escalation_level: 2 },
        { sentiment: 'negative', confidence: 0.95, score: -0.9, emotions: { anger: 0.9, demand: 0.8 }, escalation_level: 3 }
      ];

      const results = [];
      for (let i = 0; i < escalatingTexts.length; i++) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValueOnce(mockResponses[i]);
        const result = await sentimentAnalyzer.analyze(escalatingTexts[i]);
        results.push(result);
      }

      // Verify escalation pattern
      expect(results[0].escalation_level).toBe(0);
      expect(results[1].escalation_level).toBe(1);
      expect(results[2].escalation_level).toBe(2);
      expect(results[3].escalation_level).toBe(3);

      // Verify sentiment progression
      expect(results[0].sentiment).toBe('neutral');
      expect(results[3].sentiment).toBe('negative');
      expect(results[3].score).toBeLessThan(results[0].score);
    });
  });

  describe('Sarcasm and Irony Detection', () => {
    test('should detect obvious sarcasm', async () => {
      const sarcasticText = 'Oh great, another system outage. This is exactly what I needed today!';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'negative',
        confidence: 0.9,
        score: -0.8,
        emotions: {
          sarcasm: 0.9,
          frustration: 0.8,
          irony: 0.85
        },
        sarcasm_detected: true,
        surface_sentiment: 'positive',
        actual_sentiment: 'negative',
        sarcasm_confidence: 0.9
      });

      const result = await sentimentAnalyzer.analyze(sarcasticText);

      expect(result.sarcasm_detected).toBe(true);
      expect(result.surface_sentiment).toBe('positive');
      expect(result.actual_sentiment).toBe('negative');
      expect(result.sarcasm_confidence).toBeGreaterThan(0.8);
      expect(result.emotions.sarcasm).toBeGreaterThan(0.8);
    });

    test('should detect subtle irony', async () => {
      const ironicText = 'Your "help" was absolutely wonderful. I especially loved waiting on hold for two hours.';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'negative',
        confidence: 0.85,
        score: -0.7,
        emotions: {
          irony: 0.8,
          sarcasm: 0.7,
          frustration: 0.9
        },
        sarcasm_detected: true,
        irony_markers: ['quotes around help', 'exaggerated praise', 'specific negative detail'],
        sarcasm_confidence: 0.8
      });

      const result = await sentimentAnalyzer.analyze(ironicText);

      expect(result.sarcasm_detected).toBe(true);
      expect(result.emotions.irony).toBeGreaterThan(0.7);
      expect(result.irony_markers).toContain('quotes around help');
    });

    test('should distinguish between sarcasm and genuine positive sentiment', async () => {
      const genuineText = 'Thank you so much for your excellent help! You resolved my issue quickly and professionally.';

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'positive',
        confidence: 0.95,
        score: 0.9,
        emotions: {
          gratitude: 0.9,
          satisfaction: 0.85,
          appreciation: 0.8
        },
        sarcasm_detected: false,
        sarcasm_confidence: 0.1,
        genuineness_score: 0.95
      });

      const result = await sentimentAnalyzer.analyze(genuineText);

      expect(result.sarcasm_detected).toBe(false);
      expect(result.sentiment).toBe('positive');
      expect(result.genuineness_score).toBeGreaterThan(0.9);
      expect(result.emotions.gratitude).toBeGreaterThan(0.8);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle empty or whitespace-only text', async () => {
      const emptyTexts = ['', '   ', '\n\t\r', '...'];

      for (const text of emptyTexts) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
          sentiment: 'neutral',
          confidence: 0.0,
          score: 0.0,
          emotions: {},
          error: 'insufficient_content',
          warning: 'Text too short or empty for reliable analysis'
        });

        const result = await sentimentAnalyzer.analyze(text);

        expect(result.confidence).toBeLessThan(0.3);
        expect(result.error).toBe('insufficient_content');
        expect(result.warning).toContain('too short');
      }
    });

    test('should handle very long text appropriately', async () => {
      const longText = 'This is a very long text. '.repeat(1000); // 3000+ words

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'neutral',
        confidence: 0.8,
        score: 0.0,
        emotions: { neutral: 0.9 },
        text_length: longText.length,
        truncated: true,
        analysis_method: 'chunked'
      });

      const result = await sentimentAnalyzer.analyze(longText);

      expect(result.text_length).toBeGreaterThan(3000);
      expect(result.truncated).toBe(true);
      expect(result.analysis_method).toBe('chunked');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    test('should handle special characters and emojis', async () => {
      const emojiTexts = [
        'I love this! 😍❤️🎉',
        'This is terrible 😡💔😤',
        '🤔 Not sure about this...',
        '👍👎 Mixed feelings'
      ];

      const mockResponses = [
        { sentiment: 'positive', confidence: 0.9, score: 0.8, emotions: { love: 0.9 }, emoji_sentiment: 'very_positive' },
        { sentiment: 'negative', confidence: 0.9, score: -0.8, emotions: { anger: 0.9 }, emoji_sentiment: 'very_negative' },
        { sentiment: 'neutral', confidence: 0.7, score: 0.0, emotions: { uncertainty: 0.7 }, emoji_sentiment: 'uncertain' },
        { sentiment: 'mixed', confidence: 0.8, score: 0.0, emotions: { ambivalence: 0.8 }, emoji_sentiment: 'conflicted' }
      ];

      for (let i = 0; i < emojiTexts.length; i++) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValueOnce(mockResponses[i]);
        const result = await sentimentAnalyzer.analyze(emojiTexts[i]);

        expect(result.emoji_sentiment).toBeDefined();
        expect(result.confidence).toBeGreaterThan(0.6);
      }
    });

    test('should handle non-English text gracefully', async () => {
      const multiLanguageTexts = [
        'Estoy muy feliz con el servicio', // Spanish - positive
        'Je suis très déçu par cette expérience', // French - negative
        '这个服务很好', // Chinese - positive
        'Dieser Service ist schrecklich' // German - negative
      ];

      const mockResponses = [
        { sentiment: 'positive', confidence: 0.85, score: 0.7, language: 'es' },
        { sentiment: 'negative', confidence: 0.85, score: -0.7, language: 'fr' },
        { sentiment: 'positive', confidence: 0.8, score: 0.6, language: 'zh' },
        { sentiment: 'negative', confidence: 0.8, score: -0.6, language: 'de' }
      ];

      for (let i = 0; i < multiLanguageTexts.length; i++) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValueOnce(mockResponses[i]);
        const result = await sentimentAnalyzer.analyze(multiLanguageTexts[i]);

        expect(result.language).toBeDefined();
        expect(result.confidence).toBeGreaterThan(0.7);
      }
    });
  });

  describe('Provider Fallback and Reliability', () => {
    test('should fallback to secondary provider when primary fails', async () => {
      const testText = 'This is a test message for fallback testing.';

      // Mock primary provider failure
      mockOpenAIProvider.analyzeSentiment.mockRejectedValue(new Error('API rate limit exceeded'));

      // Mock secondary provider success
      mockAnthropicProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'neutral',
        confidence: 0.8,
        score: 0.1,
        emotions: { neutral: 0.8 },
        provider: 'anthropic'
      });

      const result = await sentimentAnalyzer.analyze(testText);

      expect(result.sentiment).toBe('neutral');
      expect(result.provider).toBe('anthropic');
      expect(mockOpenAIProvider.analyzeSentiment).toHaveBeenCalled();
      expect(mockAnthropicProvider.analyzeSentiment).toHaveBeenCalled();
    });

    test('should handle all providers failing gracefully', async () => {
      const testText = 'This should trigger fallback to local analysis.';

      // Mock all providers failing
      mockOpenAIProvider.analyzeSentiment.mockRejectedValue(new Error('OpenAI unavailable'));
      mockAnthropicProvider.analyzeSentiment.mockRejectedValue(new Error('Anthropic unavailable'));

      const result = await sentimentAnalyzer.analyze(testText);

      expect(result.sentiment).toBeDefined();
      expect(result.error).toBeDefined();
      expect(result.fallback_method).toBe('local_analysis');
      expect(result.confidence).toBeLessThan(0.6); // Lower confidence for fallback
    });

    test('should respect rate limits and queue requests', async () => {
      const testTexts = Array.from({ length: 5 }, (_, i) => `Test message ${i}`);

      // Mock rate limit reached
      mockOpenAIProvider.getRateLimit.mockReturnValue({
        remaining: 0,
        resetTime: Date.now() + 60000
      });

      mockOpenAIProvider.analyzeSentiment.mockRejectedValue(new Error('Rate limit exceeded'));

      // Mock secondary provider with rate limits
      mockAnthropicProvider.getRateLimit.mockReturnValue({
        remaining: 3,
        resetTime: Date.now() + 60000
      });

      mockAnthropicProvider.analyzeSentiment
        .mockResolvedValueOnce({ sentiment: 'neutral', confidence: 0.8, score: 0.0 })
        .mockResolvedValueOnce({ sentiment: 'neutral', confidence: 0.8, score: 0.0 })
        .mockResolvedValueOnce({ sentiment: 'neutral', confidence: 0.8, score: 0.0 })
        .mockRejectedValue(new Error('Rate limit exceeded'));

      const results = [];
      for (const text of testTexts) {
        try {
          const result = await sentimentAnalyzer.analyze(text);
          results.push(result);
        } catch (error) {
          results.push({ error: error.message });
        }
      }

      // Should have 3 successful results and 2 rate limit errors
      const successful = results.filter(r => !r.error).length;
      const rateLimited = results.filter(r => r.error?.includes('Rate limit')).length;

      expect(successful).toBe(3);
      expect(rateLimited).toBe(2);
    });
  });

  describe('Performance and Caching', () => {
    test('should cache results for identical text within time window', async () => {
      const testText = 'This is a test for caching functionality.';
      const mockResult = {
        sentiment: 'neutral',
        confidence: 0.8,
        score: 0.0,
        emotions: { neutral: 0.8 }
      };

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue(mockResult);

      // First analysis
      const result1 = await sentimentAnalyzer.analyze(testText);

      // Second analysis (should use cache)
      const result2 = await sentimentAnalyzer.analyze(testText);

      expect(result1).toEqual(result2);
      expect(result2.cached).toBe(true);
      expect(mockOpenAIProvider.analyzeSentiment).toHaveBeenCalledTimes(1);
    });

    test('should process multiple analyses concurrently without blocking', async () => {
      const testTexts = [
        'First concurrent message',
        'Second concurrent message',
        'Third concurrent message'
      ];

      const mockResults = testTexts.map((text, i) => ({
        sentiment: 'neutral',
        confidence: 0.8,
        score: 0.0,
        emotions: { neutral: 0.8 },
        text_id: i
      }));

      mockOpenAIProvider.analyzeSentiment
        .mockImplementation(async (text) => {
          await new Promise(resolve => setTimeout(resolve, 100)); // Simulate processing time
          return mockResults[testTexts.indexOf(text)];
        });

      const startTime = performance.now();

      const promises = testTexts.map(text => sentimentAnalyzer.analyze(text));
      const results = await Promise.all(promises);

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      // Should complete in roughly the time of one request (concurrent processing)
      expect(totalTime).toBeLessThan(300); // 3 * 100ms would be 300ms sequential
      expect(results).toHaveLength(3);
      results.forEach((result, i) => {
        expect(result.text_id).toBe(i);
      });
    });

    test('should track and report performance metrics', async () => {
      const testText = 'Performance metrics test message.';

      mockOpenAIProvider.analyzeSentiment.mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 50));
        return {
          sentiment: 'neutral',
          confidence: 0.8,
          score: 0.0,
          emotions: { neutral: 0.8 }
        };
      });

      const result = await sentimentAnalyzer.analyze(testText);

      expect(result.processing_time_ms).toBeGreaterThan(40);
      expect(result.processing_time_ms).toBeLessThan(100);
      expect(result.provider_response_time).toBeDefined();
      expect(result.total_analysis_time).toBeDefined();
    });
  });

  describe('Context and Conversation Awareness', () => {
    test('should maintain context across multiple messages in a conversation', async () => {
      const conversationMessages = [
        'My account number is 123456789.',
        'I have been having issues with billing.',
        'This is very frustrating!',
        'Thank you for helping me resolve this.'
      ];

      const mockResults = [
        { sentiment: 'neutral', confidence: 0.8, score: 0.0, context: { account: '123456789' } },
        { sentiment: 'negative', confidence: 0.8, score: -0.4, context: { issue: 'billing', account: '123456789' } },
        { sentiment: 'negative', confidence: 0.9, score: -0.7, context: { escalation: true, account: '123456789' } },
        { sentiment: 'positive', confidence: 0.9, score: 0.8, context: { resolution: true, account: '123456789' } }
      ];

      const conversationId = 'test_conversation_001';
      const results = [];

      for (let i = 0; i < conversationMessages.length; i++) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValueOnce(mockResults[i]);

        const result = await sentimentAnalyzer.analyzeWithContext(
          conversationMessages[i],
          { conversationId, messageIndex: i }
        );
        results.push(result);
      }

      // Verify context preservation
      expect(results[1].context.account).toBe('123456789');
      expect(results[2].context.escalation).toBe(true);
      expect(results[3].context.resolution).toBe(true);
    });

    test('should detect sentiment progression in conversations', async () => {
      const conversationId = 'progression_test';
      const messages = [
        'I need help with something.',
        'This is taking too long.',
        'I am getting very frustrated!',
        'Finally! Thank you for fixing it.'
      ];

      const mockResults = messages.map((msg, i) => ({
        sentiment: ['neutral', 'negative', 'negative', 'positive'][i],
        confidence: 0.8 + (i * 0.05),
        score: [0.0, -0.3, -0.8, 0.7][i],
        progression_detected: i > 0,
        sentiment_change: i > 0 ? ['neutral_to_negative', 'escalating_negative', 'negative_to_positive'][i - 1] : null
      }));

      const results = [];
      for (let i = 0; i < messages.length; i++) {
        mockOpenAIProvider.analyzeSentiment.mockResolvedValueOnce(mockResults[i]);

        const result = await sentimentAnalyzer.analyzeWithContext(
          messages[i],
          { conversationId, messageIndex: i }
        );
        results.push(result);
      }

      expect(results[1].sentiment_change).toBe('neutral_to_negative');
      expect(results[2].sentiment_change).toBe('escalating_negative');
      expect(results[3].sentiment_change).toBe('negative_to_positive');
    });
  });

  describe('Configuration and Customization', () => {
    test('should respect custom confidence thresholds', async () => {
      const customAnalyzer = new SentimentAnalyzer({
        providers: { openai: mockOpenAIProvider },
        defaultProvider: 'openai',
        confidenceThreshold: 0.9, // Higher threshold
        enableEmotionDetection: true
      });

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'positive',
        confidence: 0.85, // Below custom threshold
        score: 0.7,
        emotions: { happiness: 0.7 }
      });

      const result = await customAnalyzer.analyze('This is a test message.');

      expect(result.confidence).toBe(0.85);
      expect(result.meets_confidence_threshold).toBe(false);
      expect(result.warning).toContain('confidence below threshold');
    });

    test('should support custom emotion categories', async () => {
      const customEmotions = ['excitement', 'confusion', 'impatience', 'relief'];
      const customAnalyzer = new SentimentAnalyzer({
        providers: { openai: mockOpenAIProvider },
        defaultProvider: 'openai',
        emotionCategories: customEmotions,
        enableEmotionDetection: true
      });

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'positive',
        confidence: 0.9,
        score: 0.8,
        emotions: {
          excitement: 0.8,
          relief: 0.6
        }
      });

      const result = await customAnalyzer.analyze('Finally got it working!');

      expect(result.emotions.excitement).toBe(0.8);
      expect(result.emotions.relief).toBe(0.6);
    });

    test('should support domain-specific sentiment analysis', async () => {
      const domainAnalyzer = new SentimentAnalyzer({
        providers: { openai: mockOpenAIProvider },
        defaultProvider: 'openai',
        domain: 'customer_service',
        domainKeywords: ['billing', 'support', 'account', 'service'],
        enableDomainAdaptation: true
      });

      mockOpenAIProvider.analyzeSentiment.mockResolvedValue({
        sentiment: 'negative',
        confidence: 0.9,
        score: -0.7,
        domain_relevance: 0.95,
        domain_specific_emotions: {
          billing_frustration: 0.8,
          service_dissatisfaction: 0.7
        }
      });

      const result = await domainAnalyzer.analyze('Your billing system is completely broken!');

      expect(result.domain_relevance).toBe(0.95);
      expect(result.domain_specific_emotions.billing_frustration).toBe(0.8);
    });
  });
});