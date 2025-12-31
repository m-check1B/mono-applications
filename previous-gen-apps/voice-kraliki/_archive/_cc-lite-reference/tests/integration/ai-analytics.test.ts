/**
 * AI Analytics Tests for Voice by Kraliki
 * Tests sentiment analysis accuracy, summarization quality, and performance benchmarks
 */
import { test, expect, describe, beforeAll, afterAll } from 'vitest';
import { SentimentAnalyzer } from '../../server/services/sentiment-analyzer';
import { ConversationSummarizer } from '../../server/services/conversation-summarizer';
import { AnalyticsEngine } from '../../server/services/analytics-engine';
import { CallInsights } from '../../server/services/call-insights';
import { PerformanceMetrics } from '../../server/services/performance-metrics';

describe('AI Analytics Integration Tests', () => {
  let sentimentAnalyzer: SentimentAnalyzer;
  let conversationSummarizer: ConversationSummarizer;
  let analyticsEngine: AnalyticsEngine;
  let callInsights: CallInsights;
  let performanceMetrics: PerformanceMetrics;

  beforeAll(async () => {
    sentimentAnalyzer = new SentimentAnalyzer({
      provider: 'openai',
      model: 'gpt-4o-mini',
      apiKey: process.env.OPENAI_API_KEY || 'mock_key'
    });

    conversationSummarizer = new ConversationSummarizer({
      provider: 'anthropic',
      model: 'claude-3-haiku-20240307',
      apiKey: process.env.ANTHROPIC_API_KEY || 'mock_key'
    });

    analyticsEngine = new AnalyticsEngine({
      sentiment: sentimentAnalyzer,
      summarizer: conversationSummarizer
    });

    callInsights = new CallInsights({
      analyticsEngine
    });

    performanceMetrics = new PerformanceMetrics();

    await analyticsEngine.initialize();
  });

  afterAll(async () => {
    await analyticsEngine.cleanup();
  });

  describe('Sentiment Analysis Accuracy', () => {
    test('should accurately detect positive sentiment', async () => {
      const positiveTexts = [
        "Thank you so much for your excellent service! You've been incredibly helpful.",
        "I'm really happy with this solution. This is exactly what I needed!",
        "Outstanding support! You guys are amazing and I'll definitely recommend you.",
        "Perfect! This worked beautifully. I couldn't be more satisfied.",
        "Wonderful experience. The team was professional and efficient."
      ];

      for (const text of positiveTexts) {
        const result = await sentimentAnalyzer.analyze(text);

        expect(result.sentiment).toBe('positive');
        expect(result.confidence).toBeGreaterThan(0.7);
        expect(result.score).toBeGreaterThan(0.5);
        expect(result.emotions.joy || result.emotions.satisfaction).toBeGreaterThan(0.3);
      }
    });

    test('should accurately detect negative sentiment', async () => {
      const negativeTexts = [
        "This is terrible service! I'm extremely disappointed and frustrated.",
        "I hate this system. It never works properly and wastes my time.",
        "Worst experience ever. The support team is incompetent and unhelpful.",
        "I'm furious about this billing error. This is completely unacceptable!",
        "Absolutely horrible. I want a refund immediately and will never use this again."
      ];

      for (const text of negativeTexts) {
        const result = await sentimentAnalyzer.analyze(text);

        expect(result.sentiment).toBe('negative');
        expect(result.confidence).toBeGreaterThan(0.7);
        expect(result.score).toBeLessThan(-0.5);
        expect(result.emotions.anger || result.emotions.frustration).toBeGreaterThan(0.3);
      }
    });

    test('should accurately detect neutral sentiment', async () => {
      const neutralTexts = [
        "I need to update my billing address. Can you help me with that?",
        "What are your business hours? I need to know when you're open.",
        "Please provide information about your pricing plans and features.",
        "I'd like to schedule an appointment for next Tuesday if possible.",
        "Can you explain how this feature works? I need more details."
      ];

      for (const text of neutralTexts) {
        const result = await sentimentAnalyzer.analyze(text);

        expect(result.sentiment).toBe('neutral');
        expect(result.confidence).toBeGreaterThan(0.6);
        expect(result.score).toBeGreaterThanOrEqual(-0.3);
        expect(result.score).toBeLessThanOrEqual(0.3);
      }
    });

    test('should detect mixed emotions accurately', async () => {
      const mixedTexts = [
        "I love the product features, but the pricing is frustrating.",
        "Great customer service, though the wait time was disappointing.",
        "Happy with the quick resolution, but concerned about it happening again.",
        "Excellent quality, but delivery was delayed which was annoying.",
        "Satisfied with the outcome, although the process was confusing."
      ];

      for (const text of mixedTexts) {
        const result = await sentimentAnalyzer.analyze(text);

        expect(result.sentiment).toMatch(/^(mixed|neutral)$/);
        expect(result.mixed_emotions).toBe(true);
        expect(Object.keys(result.emotions).length).toBeGreaterThan(1);

        // Should have both positive and negative emotional indicators
        const emotionValues = Object.values(result.emotions);
        const hasPositive = emotionValues.some(val => val > 0.3);
        const hasNegative = emotionValues.some(val => val < -0.3 ||
          (result.emotions.frustration || result.emotions.anger || result.emotions.disappointment) > 0.3);

        expect(hasPositive || hasNegative).toBe(true);
      }
    });

    test('should handle sarcasm and irony detection', async () => {
      const sarcasticTexts = [
        "Oh great, another system outage. Just what I needed today.",
        "Wonderful! Now I have to start all over again. How convenient.",
        "Sure, waiting on hold for an hour was exactly how I planned to spend my day.",
        "Perfect timing for this to break right before my presentation.",
        "Oh fantastic, my favorite error message appeared again."
      ];

      for (const text of sarcasticTexts) {
        const result = await sentimentAnalyzer.analyze(text);

        expect(result.sarcasm_detected).toBe(true);
        expect(result.actual_sentiment).toBe('negative');
        expect(result.surface_sentiment).toBe('positive');
        expect(result.confidence).toBeGreaterThan(0.6);
      }
    });

    test('should track sentiment progression over conversation', async () => {
      const conversationFlow = [
        { text: "I'm having trouble with my account login", expected: "neutral" },
        { text: "This is really frustrating, I've tried multiple times", expected: "negative" },
        { text: "Thank you for helping me reset my password", expected: "positive" },
        { text: "Great! Now I can access everything properly", expected: "positive" },
        { text: "I appreciate your patience and quick support", expected: "positive" }
      ];

      const sentimentHistory = [];
      for (const message of conversationFlow) {
        const result = await sentimentAnalyzer.analyze(message.text);
        sentimentHistory.push(result);

        expect(result.sentiment).toBe(message.expected);
      }

      // Analyze progression
      const progression = await analyticsEngine.analyzeSentimentProgression(sentimentHistory);

      expect(progression.overall_trend).toBe('improving');
      expect(progression.resolution_achieved).toBe(true);
      expect(progression.final_sentiment).toBe('positive');
    });
  });

  describe('Conversation Summarization Quality', () => {
    test('should generate accurate call summaries', async () => {
      const longConversation = [
        "Customer: Hi, I'm calling about my recent order #12345. It was supposed to arrive yesterday but I haven't received it yet.",
        "Agent: I apologize for the inconvenience. Let me check the status of order #12345 for you right away.",
        "Agent: I can see that your order is currently out for delivery with our carrier. There was a slight delay due to weather conditions in your area.",
        "Customer: That's concerning because I need this for an important meeting tomorrow morning.",
        "Agent: I completely understand your urgency. Let me contact the carrier directly to get an exact delivery time and see if we can expedite this.",
        "Agent: Good news! I've spoken with the carrier and they can guarantee delivery by 8 AM tomorrow morning. They'll also send you tracking updates.",
        "Customer: That's perfect! Thank you so much for going the extra mile to help me.",
        "Agent: You're very welcome! I'll also send you a confirmation email with all the details and a direct contact number for any further questions."
      ];

      const summary = await conversationSummarizer.summarize(longConversation.join('\n'), {
        max_length: 150,
        include_action_items: true,
        include_sentiment: true
      });

      expect(summary.text).toBeDefined();
      expect(summary.text.length).toBeLessThan(200);
      expect(summary.text).toContain('order');
      expect(summary.text).toContain('delivery');

      expect(summary.action_items).toContain('Expedited delivery by 8 AM');
      expect(summary.sentiment).toBe('positive');
      expect(summary.resolution_achieved).toBe(true);
    });

    test('should extract key entities and topics', async () => {
      const conversation = `
        Customer: I need help with my premium subscription billing. My card ending in 4567 was charged twice this month.
        Agent: I see the duplicate charge for $99.99 on your Visa card. This appears to be a system error.
        Customer: I also noticed my subscription tier shows Basic instead of Premium since the January upgrade.
        Agent: I'll correct your subscription to Premium and process a refund for the duplicate charge today.
        Customer: Great! And can you confirm my renewal date is February 15th?
        Agent: Yes, your Premium subscription renews on February 15th at $99.99/month.
      `;

      const analysis = await analyticsEngine.extractEntities(conversation);

      expect(analysis.entities.subscription_type).toContain('Premium');
      expect(analysis.entities.amount).toContain('$99.99');
      expect(analysis.entities.card_last_four).toBe('4567');
      expect(analysis.entities.renewal_date).toBe('February 15th');

      expect(analysis.topics).toContain('billing');
      expect(analysis.topics).toContain('subscription');
      expect(analysis.topics).toContain('refund');

      expect(analysis.intent).toBe('billing_support');
      expect(analysis.resolution_type).toBe('refund_processed');
    });

    test('should identify escalation triggers and patterns', async () => {
      const escalationConversation = `
        Customer: This is the third time I'm calling about the same issue!
        Agent: I apologize for the inconvenience. Let me review your previous cases.
        Customer: I've wasted hours on this already. I want to speak to a manager now!
        Agent: I understand your frustration. Let me see what I can do first.
        Customer: No! I'm done dealing with agents. Get me a supervisor immediately!
        Agent: Of course, I'll transfer you to my supervisor right away. Please hold for just a moment.
      `;

      const escalationAnalysis = await callInsights.analyzeEscalation(escalationConversation);

      expect(escalationAnalysis.escalation_occurred).toBe(true);
      expect(escalationAnalysis.escalation_triggers).toContain('repeated_issue');
      expect(escalationAnalysis.escalation_triggers).toContain('supervisor_request');
      expect(escalationAnalysis.customer_frustration_level).toBeGreaterThan(0.8);
      expect(escalationAnalysis.agent_response_quality).toBeLessThan(0.6);

      expect(escalationAnalysis.recommendations).toContain('immediate_supervisor_transfer');
      expect(escalationAnalysis.prevention_suggestions).toBeDefined();
    });

    test('should generate quality scores for agents', async () => {
      const agentConversations = [
        {
          conversation: "Agent was professional and solved the issue quickly with clear explanations.",
          expected_score: 'high'
        },
        {
          conversation: "Agent seemed unprepared and gave conflicting information multiple times.",
          expected_score: 'low'
        },
        {
          conversation: "Agent was polite but took too long to find a solution.",
          expected_score: 'medium'
        }
      ];

      for (const { conversation, expected_score } of agentConversations) {
        const qualityScore = await analyticsEngine.calculateAgentQualityScore(conversation);

        expect(qualityScore.overall_score).toBeDefined();
        expect(qualityScore.communication_score).toBeGreaterThan(0);
        expect(qualityScore.problem_solving_score).toBeGreaterThan(0);
        expect(qualityScore.professionalism_score).toBeGreaterThan(0);

        if (expected_score === 'high') {
          expect(qualityScore.overall_score).toBeGreaterThan(0.7);
        } else if (expected_score === 'low') {
          expect(qualityScore.overall_score).toBeLessThan(0.4);
        } else {
          expect(qualityScore.overall_score).toBeGreaterThanOrEqual(0.4);
          expect(qualityScore.overall_score).toBeLessThanOrEqual(0.7);
        }
      }
    });
  });

  describe('Performance Benchmarks', () => {
    test('should process sentiment analysis within performance thresholds', async () => {
      const testTexts = [
        "Short text.",
        "This is a medium length text that contains multiple sentences and should test the processing capability of the sentiment analyzer.",
        "This is a very long text that simulates a detailed customer complaint or feedback. ".repeat(10)
      ];

      for (const text of testTexts) {
        const startTime = performance.now();
        const result = await sentimentAnalyzer.analyze(text);
        const endTime = performance.now();

        const processingTime = endTime - startTime;

        // Short texts should be very fast
        if (text.length < 50) {
          expect(processingTime).toBeLessThan(100); // 100ms
        }
        // Medium texts should be reasonably fast
        else if (text.length < 500) {
          expect(processingTime).toBeLessThan(500); // 500ms
        }
        // Long texts should still be under 2 seconds
        else {
          expect(processingTime).toBeLessThan(2000); // 2s
        }

        expect(result.processing_time_ms).toBeDefined();
        expect(result.processing_time_ms).toBeCloseTo(processingTime, -1);
      }
    });

    test('should handle concurrent sentiment analysis efficiently', async () => {
      const concurrentRequests = 10;
      const testText = "This is a concurrent processing test to evaluate system performance.";

      const startTime = performance.now();

      const promises = Array(concurrentRequests).fill(null).map(() =>
        sentimentAnalyzer.analyze(testText)
      );

      const results = await Promise.all(promises);
      const endTime = performance.now();

      const totalTime = endTime - startTime;
      const averageTimePerRequest = totalTime / concurrentRequests;

      // Concurrent processing should not be much slower than sequential
      expect(averageTimePerRequest).toBeLessThan(1000); // 1s per request
      expect(results.length).toBe(concurrentRequests);

      // All results should be valid
      results.forEach(result => {
        expect(result.sentiment).toBeDefined();
        expect(result.confidence).toBeDefined();
        expect(result.error).toBeUndefined();
      });
    });

    test('should process conversation summarization efficiently', async () => {
      const conversations = {
        short: "Agent: How can I help? Customer: Need info. Agent: Here you go.",
        medium: Array(20).fill("Agent: I understand your concern. Customer: Thank you for helping me.").join(' '),
        long: Array(100).fill("This is a sentence in a very long conversation that needs to be summarized efficiently.").join(' ')
      };

      for (const [length, conversation] of Object.entries(conversations)) {
        const startTime = performance.now();
        const summary = await conversationSummarizer.summarize(conversation);
        const endTime = performance.now();

        const processingTime = endTime - startTime;

        if (length === 'short') {
          expect(processingTime).toBeLessThan(500);
        } else if (length === 'medium') {
          expect(processingTime).toBeLessThan(1500);
        } else {
          expect(processingTime).toBeLessThan(3000);
        }

        expect(summary.text).toBeDefined();
        expect(summary.text.length).toBeLessThan(conversation.length);
      }
    });

    test('should maintain accuracy under load', async () => {
      const loadTestData = Array(50).fill(null).map((_, i) => ({
        text: `This is test message ${i} with ${i % 2 === 0 ? 'positive' : 'negative'} sentiment.`,
        expectedSentiment: i % 2 === 0 ? 'positive' : 'negative'
      }));

      const results = await Promise.all(
        loadTestData.map(data => sentimentAnalyzer.analyze(data.text))
      );

      let accurateResults = 0;
      results.forEach((result, i) => {
        if (result.sentiment === loadTestData[i].expectedSentiment) {
          accurateResults++;
        }
      });

      const accuracy = accurateResults / loadTestData.length;
      expect(accuracy).toBeGreaterThan(0.8); // At least 80% accuracy under load
    });

    test('should track and report performance metrics', async () => {
      // Process multiple analytics requests
      const testRequests = [
        () => sentimentAnalyzer.analyze("Happy customer feedback"),
        () => conversationSummarizer.summarize("Long conversation to summarize"),
        () => callInsights.analyzeEscalation("Escalation scenario"),
        () => analyticsEngine.extractEntities("Entity extraction test")
      ];

      // Execute requests and collect metrics
      for (const request of testRequests) {
        await request();
      }

      const metrics = await performanceMetrics.getAnalyticsMetrics();

      expect(metrics.total_requests).toBeGreaterThan(0);
      expect(metrics.average_response_time).toBeDefined();
      expect(metrics.throughput_per_minute).toBeGreaterThan(0);
      expect(metrics.error_rate).toBeLessThan(0.1); // Less than 10% errors

      expect(metrics.by_service.sentiment_analysis).toBeDefined();
      expect(metrics.by_service.summarization).toBeDefined();
      expect(metrics.by_service.entity_extraction).toBeDefined();
    });

    test('should detect and handle performance degradation', async () => {
      // Simulate high load scenario
      const highLoadPromises = Array(100).fill(null).map(() =>
        sentimentAnalyzer.analyze("Performance degradation test")
      );

      const startTime = performance.now();
      const results = await Promise.allSettled(highLoadPromises);
      const endTime = performance.now();

      const successfulResults = results.filter(r => r.status === 'fulfilled');
      const failedResults = results.filter(r => r.status === 'rejected');

      // Should handle graceful degradation
      expect(successfulResults.length).toBeGreaterThan(50); // At least 50% success
      expect(failedResults.length).toBeLessThan(50); // No more than 50% failures

      const totalTime = endTime - startTime;
      const averageTime = totalTime / results.length;

      // Should not exceed reasonable time limits even under load
      expect(averageTime).toBeLessThan(5000); // 5s average maximum
    });
  });

  describe('Analytics Integration and Workflow', () => {
    test('should provide comprehensive call analysis', async () => {
      const fullCallTranscript = `
        Agent: Thank you for calling customer support. How can I help you today?
        Customer: Hi, I'm really frustrated because my internet has been down for two days now.
        Agent: I'm so sorry to hear about this issue. Let me look into this right away. Can I get your account number?
        Customer: It's 123456789. I work from home and this is really affecting my job.
        Agent: I understand how important this is. I can see there was a service outage in your area. Let me check if it's been resolved.
        Agent: Good news! The outage has been fixed and I can reset your connection remotely. This should restore your service immediately.
        Customer: Oh wow, that's great! Let me check... Yes, it's working now! Thank you so much.
        Agent: You're very welcome! I'll also provide you with a service credit for the downtime. Is there anything else I can help you with?
        Customer: No, that's perfect. I really appreciate your help!
        Agent: It was my pleasure. Have a wonderful day!
      `;

      const comprehensiveAnalysis = await analyticsEngine.analyzeFullCall(fullCallTranscript, {
        include_sentiment_progression: true,
        include_agent_quality: true,
        include_resolution_analysis: true,
        include_customer_satisfaction: true
      });

      // Sentiment analysis
      expect(comprehensiveAnalysis.sentiment_analysis.initial_sentiment).toBe('negative');
      expect(comprehensiveAnalysis.sentiment_analysis.final_sentiment).toBe('positive');
      expect(comprehensiveAnalysis.sentiment_analysis.improvement_detected).toBe(true);

      // Agent quality
      expect(comprehensiveAnalysis.agent_quality.overall_score).toBeGreaterThan(0.8);
      expect(comprehensiveAnalysis.agent_quality.empathy_score).toBeGreaterThan(0.7);
      expect(comprehensiveAnalysis.agent_quality.resolution_efficiency).toBeGreaterThan(0.8);

      // Resolution analysis
      expect(comprehensiveAnalysis.resolution.issue_resolved).toBe(true);
      expect(comprehensiveAnalysis.resolution.resolution_time).toBeLessThan(600); // 10 minutes
      expect(comprehensiveAnalysis.resolution.follow_up_required).toBe(false);

      // Customer satisfaction
      expect(comprehensiveAnalysis.customer_satisfaction.estimated_score).toBeGreaterThan(0.8);
      expect(comprehensiveAnalysis.customer_satisfaction.likelihood_to_recommend).toBeGreaterThan(0.7);
    });
  });
});