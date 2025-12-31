/**
 * Sentiment Analysis Test Suite
 * Tests the sentiment analysis functionality with sample conversations
 */

import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import { FastifyInstance } from 'fastify';
import { build } from '../server/app'; // Adjust path as needed
import { SentimentAnalysisService } from '../server/services/sentiment-analysis-service';
import { PrismaClient } from '@prisma/client';

describe('Sentiment Analysis Integration Tests', () => {
  let app: FastifyInstance;
  let prisma: PrismaClient;
  let sentimentService: SentimentAnalysisService;
  let testCallId: string;
  let testOrganizationId: string;

  beforeAll(async () => {
    app = build();
    await app.ready();

    prisma = new PrismaClient();
    sentimentService = new SentimentAnalysisService(app);

    // Create test organization
    const testOrg = await prisma.organization.create({
      data: {
        name: 'Test Organization',
        domain: 'test.example.com'
      }
    });
    testOrganizationId = testOrg.id;

    // Create test call
    const testCall = await prisma.call.create({
      data: {
        fromNumber: '+1234567890',
        toNumber: '+0987654321',
        direction: 'INBOUND',
        provider: 'TWILIO',
        organizationId: testOrganizationId,
        status: 'IN_PROGRESS'
      }
    });
    testCallId = testCall.id;
  });

  afterAll(async () => {
    // Cleanup test data
    await prisma.sentimentAnalysis.deleteMany({
      where: { callId: testCallId }
    });
    await prisma.call.deleteMany({
      where: { organizationId: testOrganizationId }
    });
    await prisma.organization.deleteMany({
      where: { id: testOrganizationId }
    });

    await prisma.$disconnect();
    await app.close();
  });

  describe('Basic Sentiment Analysis', () => {
    test('should analyze positive customer message', async () => {
      const positiveMessage = "Thank you so much! Your service has been excellent and I'm very satisfied with the resolution.";

      const result = await sentimentService.analyzeSentiment(
        positiveMessage,
        testCallId,
        'test_session_1'
      );

      expect(result).toBeDefined();
      expect(result.overall).toBe('POSITIVE');
      expect(result.confidence).toBeGreaterThan(0.5);
      expect(result.emotions).toHaveLength(expect.any(Number));
      expect(result.emotions.some(e => e.emotion === 'JOY' || e.emotion === 'SATISFACTION')).toBe(true);
    });

    test('should analyze negative customer message', async () => {
      const negativeMessage = "This is absolutely terrible! I'm extremely frustrated and angry with this poor service!";

      const result = await sentimentService.analyzeSentiment(
        negativeMessage,
        testCallId,
        'test_session_2'
      );

      expect(result).toBeDefined();
      expect(result.overall).toBe('NEGATIVE');
      expect(result.confidence).toBeGreaterThan(0.5);
      expect(result.emotions).toHaveLength(expect.any(Number));
      expect(result.emotions.some(e => e.emotion === 'ANGER' || e.emotion === 'FRUSTRATION')).toBe(true);
    });

    test('should analyze neutral customer message', async () => {
      const neutralMessage = "I need to update my account information. Can you help me with that?";

      const result = await sentimentService.analyzeSentiment(
        neutralMessage,
        testCallId,
        'test_session_3'
      );

      expect(result).toBeDefined();
      expect(result.overall).toBe('NEUTRAL');
      expect(result.emotions).toHaveLength(expect.any(Number));
    });
  });

  describe('Emotion Detection', () => {
    test('should detect frustration in customer message', async () => {
      const frustratedMessage = "I've been waiting for 30 minutes and I'm getting really frustrated with this delay!";

      const result = await sentimentService.analyzeSentiment(
        frustratedMessage,
        testCallId,
        'test_session_4'
      );

      const frustrationEmotion = result.emotions.find(e => e.emotion === 'FRUSTRATION');
      expect(frustrationEmotion).toBeDefined();
      expect(frustrationEmotion?.intensity).toBeGreaterThan(0.5);
    });

    test('should detect confusion in customer message', async () => {
      const confusedMessage = "I don't understand what you're saying. This is all very confusing to me.";

      const result = await sentimentService.analyzeSentiment(
        confusedMessage,
        testCallId,
        'test_session_5'
      );

      const confusionEmotion = result.emotions.find(e => e.emotion === 'CONFUSION');
      expect(confusionEmotion).toBeDefined();
      expect(confusionEmotion?.intensity).toBeGreaterThan(0.3);
    });
  });

  describe('Real-time Sentiment Tracking', () => {
    test('should track sentiment changes over conversation', async () => {
      const sessionId = 'test_session_realtime';

      // Start with neutral message
      await sentimentService.analyzeSentiment(
        "Hello, I need help with my account.",
        testCallId,
        sessionId
      );

      // Add frustrated message
      await sentimentService.analyzeSentiment(
        "This is taking too long and I'm getting frustrated!",
        testCallId,
        sessionId
      );

      // Add satisfied message
      await sentimentService.analyzeSentiment(
        "Great! Thank you for resolving this quickly.",
        testCallId,
        sessionId
      );

      // Get real-time data
      const realTimeData = await sentimentService.getRealTimeSentiment(sessionId);

      expect(realTimeData).toBeDefined();
      expect(realTimeData?.sentimentHistory).toHaveLength(3);
      expect(realTimeData?.currentSentiment).toBe('POSITIVE');
    });
  });

  describe('Sentiment Triggers', () => {
    test('should identify positive triggers', async () => {
      const messageWithTriggers = "Thank you very much! This is excellent service and I really appreciate your help.";

      const result = await sentimentService.analyzeSentiment(
        messageWithTriggers,
        testCallId,
        'test_session_6'
      );

      expect(result.triggers).toHaveLength(expect.any(Number));
      expect(result.triggers.some(t => t.type === 'POSITIVE')).toBe(true);
      expect(result.triggers.some(t => t.trigger.includes('thank'))).toBe(true);
    });

    test('should identify negative triggers', async () => {
      const messageWithTriggers = "This is absolutely horrible and unacceptable! I'm very angry about this.";

      const result = await sentimentService.analyzeSentiment(
        messageWithTriggers,
        testCallId,
        'test_session_7'
      );

      expect(result.triggers).toHaveLength(expect.any(Number));
      expect(result.triggers.some(t => t.type === 'NEGATIVE')).toBe(true);
      expect(result.triggers.some(t => t.trigger.includes('horrible') || t.trigger.includes('angry'))).toBe(true);
    });
  });

  describe('Conversation Context', () => {
    test('should use conversation context for better analysis', async () => {
      const context = {
        conversationPhase: 'resolution' as const,
        customerType: 'escalated' as const,
        callReason: 'complaint',
        urgency: 'high' as const
      };

      const result = await sentimentService.analyzeSentiment(
        "I guess that's okay for now.",
        testCallId,
        'test_session_8',
        undefined,
        context
      );

      expect(result.context.conversationPhase).toBe('resolution');
      expect(result.context.customerType).toBe('escalated');
      expect(result.context.urgency).toBe('high');
    });
  });

  describe('Sentiment Trends', () => {
    test('should calculate improving sentiment trend', async () => {
      const sessionId = 'test_session_trend';

      // Simulate improving sentiment conversation
      await sentimentService.analyzeSentiment("I'm not happy about this issue.", testCallId, sessionId);
      await sentimentService.analyzeSentiment("Okay, I see what you mean.", testCallId, sessionId);
      await sentimentService.analyzeSentiment("That sounds like a good solution.", testCallId, sessionId);

      const result = await sentimentService.analyzeSentiment(
        "Perfect! Thank you for your help.",
        testCallId,
        sessionId
      );

      expect(result.trend).toBe('IMPROVING');
    });
  });

  describe('Error Handling', () => {
    test('should handle empty text gracefully', async () => {
      await expect(
        sentimentService.analyzeSentiment('', testCallId, 'test_session_empty')
      ).rejects.toThrow('Text is required');
    });

    test('should handle very long text by truncating', async () => {
      const longText = 'A'.repeat(6000); // Exceeds 5000 char limit

      const result = await sentimentService.analyzeSentiment(
        longText,
        testCallId,
        'test_session_long'
      );

      expect(result).toBeDefined();
      expect(result.metadata.textLength).toBeLessThanOrEqual(5000);
    });
  });

  describe('Service Health', () => {
    test('should return healthy status', () => {
      const health = sentimentService.getHealthStatus();

      expect(health.status).toBe('healthy');
      expect(health.config).toBeDefined();
      expect(health.config.processingVersion).toBe('2.0');
    });
  });

  describe('Performance Metrics', () => {
    test('should complete analysis within reasonable time', async () => {
      const startTime = Date.now();

      await sentimentService.analyzeSentiment(
        "This is a test message for performance measurement.",
        testCallId,
        'test_session_perf'
      );

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      // Should complete within 5 seconds (adjust based on OpenAI response times)
      expect(processingTime).toBeLessThan(5000);
    });
  });
});

describe('Sample Conversation Scenarios', () => {
  let app: FastifyInstance;
  let sentimentService: SentimentAnalysisService;

  beforeAll(async () => {
    app = build();
    await app.ready();
    sentimentService = new SentimentAnalysisService(app);
  });

  afterAll(async () => {
    await app.close();
  });

  test('Customer Support Resolution - Happy Path', async () => {
    const conversation = [
      { role: 'customer', text: "Hi, I'm having trouble with my account login." },
      { role: 'agent', text: "I'd be happy to help you with that. Can you provide your email address?" },
      { role: 'customer', text: "Sure, it's john@example.com" },
      { role: 'agent', text: "I found your account. Let me reset your password for you." },
      { role: 'customer', text: "Thank you! That worked perfectly. I really appreciate your quick help." }
    ];

    const sessionId = 'happy_path_session';
    const callId = 'test_call_happy';

    for (const message of conversation) {
      if (message.role === 'customer') {
        const result = await sentimentService.analyzeSentiment(
          message.text,
          callId,
          sessionId
        );
        console.log(`Customer: "${message.text}" -> Sentiment: ${result.overall} (${result.confidence.toFixed(2)})`);
      }
    }

    const finalSentiment = await sentimentService.getRealTimeSentiment(sessionId);
    expect(finalSentiment?.currentSentiment).toBe('POSITIVE');
  });

  test('Escalated Complaint - Challenging Scenario', async () => {
    const conversation = [
      { role: 'customer', text: "I am absolutely furious! Your service has been terrible and I demand to speak to a manager!" },
      { role: 'agent', text: "I understand your frustration and I sincerely apologize. Let me see how I can help resolve this for you." },
      { role: 'customer', text: "I've been a customer for 5 years and this is the worst experience I've ever had!" },
      { role: 'agent', text: "I truly understand how disappointing this must be for a loyal customer like yourself. Let me make this right." },
      { role: 'customer', text: "Well... I suppose you're trying to help. What can you actually do?" },
      { role: 'agent', text: "I can offer you a full refund and a premium service upgrade at no additional cost." },
      { role: 'customer', text: "That actually sounds fair. I appreciate you taking this seriously." }
    ];

    const sessionId = 'escalated_session';
    const callId = 'test_call_escalated';

    for (const message of conversation) {
      if (message.role === 'customer') {
        const result = await sentimentService.analyzeSentiment(
          message.text,
          callId,
          sessionId
        );
        console.log(`Customer: "${message.text}" -> Sentiment: ${result.overall} (${result.confidence.toFixed(2)})`);
      }
    }

    const finalSentiment = await sentimentService.getRealTimeSentiment(sessionId);
    expect(finalSentiment?.currentSentiment).toBe('POSITIVE');
  });
});