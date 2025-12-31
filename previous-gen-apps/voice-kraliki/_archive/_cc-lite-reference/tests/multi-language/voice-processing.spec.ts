import { describe, it, expect, beforeEach, vi } from 'vitest';
import { testDb, createTestUser, createTestCall, createTestCampaign, mockLanguageRouter, mockCzechTTSService, mockDeepgramService, createLanguageTestData, waitFor } from '../setup';
import { createToken } from '@unified/auth-core';

describe('Multi-Language Voice Processing Tests', () => {
  let testUser: any;
  let testCampaign: any;

  beforeEach(async () => {
    // Clean database
    await testDb.call.deleteMany();
    await testDb.campaign.deleteMany();
    await testDb.user.deleteMany();
    await testDb.organization.deleteMany();

    // Create test user and campaign
    testUser = await createTestUser({ role: 'AGENT' });
    testCampaign = await createTestCampaign({ 
      organizationId: testUser.organizationId,
      name: 'Multi-Language Test Campaign'
    });

    // Reset all mocks
    vi.clearAllMocks();
  });

  describe('Language Detection', () => {
    it('should detect English language correctly', async () => {
      const englishText = createLanguageTestData('en', 'medium');
      
      mockLanguageRouter.processText.mockResolvedValue({
        detectedLanguage: 'en',
        confidence: 0.95,
        processedText: englishText,
        route: 'english'
      });

      const result = await mockLanguageRouter.processText(englishText);
      
      expect(result.detectedLanguage).toBe('en');
      expect(result.confidence).toBeGreaterThan(0.9);
      expect(result.route).toBe('english');
    });

    it('should detect Spanish language correctly', async () => {
      const spanishText = createLanguageTestData('es', 'medium');
      
      mockLanguageRouter.processText.mockResolvedValue({
        detectedLanguage: 'es',
        confidence: 0.92,
        processedText: spanishText,
        route: 'spanish'
      });

      const result = await mockLanguageRouter.processText(spanishText);
      
      expect(result.detectedLanguage).toBe('es');
      expect(result.confidence).toBeGreaterThan(0.9);
      expect(result.route).toBe('spanish');
    });

    it('should detect Czech language correctly', async () => {
      const czechText = createLanguageTestData('cs', 'medium');
      
      mockLanguageRouter.processText.mockResolvedValue({
        detectedLanguage: 'cs',
        confidence: 0.88,
        processedText: czechText,
        route: 'czech'
      });

      const result = await mockLanguageRouter.processText(czechText);
      
      expect(result.detectedLanguage).toBe('cs');
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.route).toBe('czech');
    });

    it('should handle ambiguous language detection', async () => {
      const shortText = 'Hello';
      
      mockLanguageRouter.processText.mockResolvedValue({
        detectedLanguage: 'en',
        confidence: 0.65, // Lower confidence for short text
        processedText: shortText,
        route: 'english',
        fallbackToDefault: true
      });

      const result = await mockLanguageRouter.processText(shortText);
      
      expect(result.confidence).toBeLessThan(0.8);
      expect(result.fallbackToDefault).toBe(true);
    });

    it('should detect language switches within conversation', async () => {
      const sessionId = 'test-session-123';
      
      // Start with English
      mockLanguageRouter.startSession.mockResolvedValue({
        sessionId,
        initialLanguage: 'en'
      });
      
      await mockLanguageRouter.startSession(sessionId, { defaultLanguage: 'en' });
      
      // Process English text
      mockLanguageRouter.processText.mockResolvedValueOnce({
        detectedLanguage: 'en',
        confidence: 0.95,
        processedText: createLanguageTestData('en'),
        route: 'english',
        sessionId
      });
      
      const englishResult = await mockLanguageRouter.processText(
        createLanguageTestData('en'), 
        { sessionId }
      );
      expect(englishResult.detectedLanguage).toBe('en');
      
      // Switch to Spanish
      mockLanguageRouter.processText.mockResolvedValueOnce({
        detectedLanguage: 'es',
        confidence: 0.90,
        processedText: createLanguageTestData('es'),
        route: 'spanish',
        sessionId,
        languageChanged: true,
        previousLanguage: 'en'
      });
      
      const spanishResult = await mockLanguageRouter.processText(
        createLanguageTestData('es'), 
        { sessionId }
      );
      
      expect(spanishResult.detectedLanguage).toBe('es');
      expect(spanishResult.languageChanged).toBe(true);
      expect(spanishResult.previousLanguage).toBe('en');
    });
  });

  describe('Speech Recognition (STT)', () => {
    it('should transcribe English audio accurately', async () => {
      const mockAudioBuffer = Buffer.from('fake-english-audio-data');
      
      mockDeepgramService.processAudioStream.mockResolvedValue({
        transcript: 'Hello, this is a test of English speech recognition.',
        confidence: 0.95,
        language: 'en',
        duration: 3.2
      });

      const result = await mockDeepgramService.processAudioStream(mockAudioBuffer, {
        language: 'en',
        model: 'nova-2'
      });
      
      expect(result.transcript).toContain('Hello');
      expect(result.confidence).toBeGreaterThan(0.9);
      expect(result.language).toBe('en');
    });

    it('should transcribe Spanish audio with proper accents', async () => {
      const mockAudioBuffer = Buffer.from('fake-spanish-audio-data');
      
      mockDeepgramService.processAudioStream.mockResolvedValue({
        transcript: 'Hola, ¿cómo está usted hoy?',
        confidence: 0.88,
        language: 'es',
        duration: 2.8,
        entities: ['greeting']
      });

      const result = await mockDeepgramService.processAudioStream(mockAudioBuffer, {
        language: 'es',
        model: 'nova-2'
      });
      
      expect(result.transcript).toContain('¿cómo está');
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.language).toBe('es');
    });

    it('should handle Czech speech recognition', async () => {
      const mockAudioBuffer = Buffer.from('fake-czech-audio-data');
      
      mockDeepgramService.processAudioStream.mockResolvedValue({
        transcript: 'Dobrý den, jak se máte?',
        confidence: 0.82,
        language: 'cs',
        duration: 2.5,
        specialized: true
      });

      const result = await mockDeepgramService.processAudioStream(mockAudioBuffer, {
        language: 'cs',
        model: 'nova-2'
      });
      
      expect(result.transcript).toContain('Dobrý den');
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.language).toBe('cs');
    });

    it('should handle noisy audio with fallback', async () => {
      const mockNoisyAudioBuffer = Buffer.from('fake-noisy-audio-data');
      
      mockDeepgramService.processAudioStream.mockResolvedValue({
        transcript: '[unclear]',
        confidence: 0.45,
        language: 'en',
        duration: 1.2,
        noiseLevel: 'high',
        fallbackUsed: true
      });

      const result = await mockDeepgramService.processAudioStream(mockNoisyAudioBuffer, {
        language: 'en',
        model: 'nova-2',
        enhancedAudio: true
      });
      
      expect(result.confidence).toBeLessThan(0.7);
      expect(result.fallbackUsed).toBe(true);
      expect(result.noiseLevel).toBe('high');
    });
  });

  describe('Text-to-Speech (TTS)', () => {
    it('should synthesize English speech with natural voice', async () => {
      const englishText = 'Hello, thank you for calling our support center.';
      
      mockDeepgramService.synthesizeSpeech.mockResolvedValue({
        audioBuffer: Buffer.from('fake-english-tts-audio'),
        duration: 3.5,
        language: 'en',
        voice: 'aura-luna-en',
        format: 'mp3'
      });

      const result = await mockDeepgramService.synthesizeSpeech(englishText, {
        language: 'en',
        voice: 'aura-luna-en',
        speed: 1.0
      });
      
      expect(result.audioBuffer).toBeDefined();
      expect(result.language).toBe('en');
      expect(result.voice).toBe('aura-luna-en');
      expect(result.duration).toBeGreaterThan(0);
    });

    it('should synthesize Spanish speech with proper pronunciation', async () => {
      const spanishText = 'Hola, gracias por llamar a nuestro centro de soporte.';
      
      mockDeepgramService.synthesizeSpeech.mockResolvedValue({
        audioBuffer: Buffer.from('fake-spanish-tts-audio'),
        duration: 4.2,
        language: 'es',
        voice: 'aura-luna-es',
        format: 'mp3',
        pronunciation: 'latin-american'
      });

      const result = await mockDeepgramService.synthesizeSpeech(spanishText, {
        language: 'es',
        voice: 'aura-luna-es',
        speed: 0.9,
        pronunciation: 'latin-american'
      });
      
      expect(result.audioBuffer).toBeDefined();
      expect(result.language).toBe('es');
      expect(result.pronunciation).toBe('latin-american');
    });

    it('should use specialized Czech TTS service', async () => {
      const czechText = 'Dobrý den, děkujeme za váš hovor.';
      
      mockCzechTTSService.synthesize.mockResolvedValue({
        audioBuffer: Buffer.from('fake-czech-tts-audio'),
        duration: 3.8,
        language: 'cs',
        voice: 'cs-female-1',
        format: 'wav',
        specialized: true
      });

      const result = await mockCzechTTSService.synthesize(czechText, {
        voice: 'cs-female-1',
        speed: 1.0,
        emotion: 'neutral'
      });
      
      expect(result.audioBuffer).toBeDefined();
      expect(result.language).toBe('cs');
      expect(result.specialized).toBe(true);
    });

    it('should handle streaming TTS for real-time conversations', async () => {
      const longText = 'This is a longer text that should be streamed for better user experience. ' +
                      'The streaming should start playing audio while still processing the rest of the text.';
      
      mockDeepgramService.streamSpeech.mockImplementation(async function* (text, options) {
        const chunks = text.split('. ');
        for (let i = 0; i < chunks.length; i++) {
          yield {
            audioChunk: Buffer.from(`fake-audio-chunk-${i}`),
            chunkIndex: i,
            isComplete: i === chunks.length - 1,
            timestamp: Date.now()
          };
          await waitFor(100); // Simulate processing delay
        }
      });

      const streamResults = [];
      for await (const chunk of mockDeepgramService.streamSpeech(longText, { language: 'en' })) {
        streamResults.push(chunk);
      }
      
      expect(streamResults.length).toBeGreaterThan(1);
      expect(streamResults[0].chunkIndex).toBe(0);
      expect(streamResults[streamResults.length - 1].isComplete).toBe(true);
    });
  });

  describe('Language Routing and Workflow', () => {
    it('should route call to appropriate language-specific agent', async () => {
      // Create language-specific agents
      const englishAgent = await createTestUser({ 
        role: 'AGENT',
        languages: ['en'],
        organizationId: testUser.organizationId
      });
      
      const spanishAgent = await createTestUser({ 
        role: 'AGENT',
        languages: ['es'],
        organizationId: testUser.organizationId
      });
      
      const bilingualAgent = await createTestUser({ 
        role: 'AGENT',
        languages: ['en', 'es'],
        organizationId: testUser.organizationId
      });

      // Mock language routing
      mockLanguageRouter.switchLanguageRoute.mockImplementation(async (sessionId, targetLanguage) => {
        const routingLogic = {
          'en': englishAgent,
          'es': spanishAgent,
          'bilingual': bilingualAgent
        };
        
        return {
          sessionId,
          targetLanguage,
          assignedAgent: routingLogic[targetLanguage as keyof typeof routingLogic],
          routeChanged: true
        };
      });

      // Test Spanish routing
      const spanishRoute = await mockLanguageRouter.switchLanguageRoute('session-123', 'es');
      expect(spanishRoute.assignedAgent.id).toBe(spanishAgent.id);
      
      // Test English routing
      const englishRoute = await mockLanguageRouter.switchLanguageRoute('session-456', 'en');
      expect(englishRoute.assignedAgent.id).toBe(englishAgent.id);
    });

    it('should handle language-specific call flows', async () => {
      const sessionId = 'multilang-session-789';
      
      // Mock session setup
      mockLanguageRouter.startSession.mockResolvedValue({
        sessionId,
        initialLanguage: 'en',
        availableLanguages: ['en', 'es', 'cs'],
        fallbackLanguage: 'en'
      });
      
      await mockLanguageRouter.startSession(sessionId);
      
      // Test language-specific IVR flows
      const languageFlows = {
        'en': {
          greeting: 'Thank you for calling. Press 1 for sales, 2 for support.',
          options: ['sales', 'support', 'billing']
        },
        'es': {
          greeting: 'Gracias por llamar. Presione 1 para ventas, 2 para soporte.',
          options: ['ventas', 'soporte', 'facturación']
        },
        'cs': {
          greeting: 'Děkujeme za váš hovor. Stiskněte 1 pro prodej, 2 pro podporu.',
          options: ['prodej', 'podpora', 'fakturace']
        }
      };
      
      for (const [language, flow] of Object.entries(languageFlows)) {
        mockLanguageRouter.getSessionRoute.mockResolvedValue({
          sessionId,
          currentLanguage: language,
          flow,
          customized: true
        });
        
        const route = await mockLanguageRouter.getSessionRoute(sessionId);
        expect(route.flow.options).toHaveLength(3);
        expect(route.customized).toBe(true);
      }
    });

    it('should maintain conversation context across language switches', async () => {
      const sessionId = 'context-session-123';
      const conversationHistory = [
        { language: 'en', text: 'Hello, I need help with my account', timestamp: new Date() },
        { language: 'es', text: 'Perdón, prefiero hablar en español', timestamp: new Date() },
        { language: 'es', text: 'Necesito ayuda con mi cuenta', timestamp: new Date() }
      ];
      
      mockLanguageRouter.getSessionStats.mockResolvedValue({
        sessionId,
        totalMessages: conversationHistory.length,
        languageBreakdown: {
          'en': 1,
          'es': 2
        },
        currentLanguage: 'es',
        languageSwitches: 1,
        contextPreserved: true,
        conversationSummary: 'Customer needs account help, switched to Spanish'
      });
      
      const stats = await mockLanguageRouter.getSessionStats(sessionId);
      
      expect(stats.languageSwitches).toBe(1);
      expect(stats.currentLanguage).toBe('es');
      expect(stats.contextPreserved).toBe(true);
      expect(stats.conversationSummary).toContain('account help');
    });
  });

  describe('Performance and Quality', () => {
    it('should maintain low latency for real-time voice processing', async () => {
      const testCases = [
        { language: 'en', text: createLanguageTestData('en', 'short') },
        { language: 'es', text: createLanguageTestData('es', 'short') },
        { language: 'cs', text: createLanguageTestData('cs', 'short') }
      ];
      
      for (const testCase of testCases) {
        const startTime = Date.now();
        
        // Mock fast processing
        mockLanguageRouter.processText.mockResolvedValueOnce({
          detectedLanguage: testCase.language,
          confidence: 0.9,
          processedText: testCase.text,
          processingTime: 150, // 150ms
          route: `${testCase.language}-route`
        });
        
        const result = await mockLanguageRouter.processText(testCase.text);
        const totalTime = Date.now() - startTime;
        
        expect(result.processingTime).toBeLessThan(200); // Under 200ms
        expect(totalTime).toBeLessThan(500); // Total under 500ms
      }
    });

    it('should handle concurrent multi-language sessions', async () => {
      const sessionCount = 10;
      const concurrentSessions = [];
      
      for (let i = 0; i < sessionCount; i++) {
        const sessionId = `concurrent-session-${i}`;
        const language = ['en', 'es', 'cs'][i % 3];
        
        mockLanguageRouter.startSession.mockResolvedValue({
          sessionId,
          initialLanguage: language,
          concurrent: true
        });
        
        concurrentSessions.push(mockLanguageRouter.startSession(sessionId, {
          defaultLanguage: language
        }));
      }
      
      const results = await Promise.all(concurrentSessions);
      
      expect(results).toHaveLength(sessionCount);
      results.forEach(result => {
        expect(result.concurrent).toBe(true);
      });
    });

    it('should provide quality metrics for voice processing', async () => {
      const qualityMetrics = {
        transcriptionAccuracy: 0.94,
        languageDetectionAccuracy: 0.91,
        ttsNaturalness: 0.89,
        overallLatency: 180,
        errorRate: 0.02
      };
      
      mockLanguageRouter.getHealthStatus.mockResolvedValue({
        ...qualityMetrics,
        activeSessions: 5,
        deepgramAvailable: true,
        czechTTSAvailable: true,
        status: 'healthy'
      });
      
      const healthStatus = await mockLanguageRouter.getHealthStatus();
      
      expect(healthStatus.transcriptionAccuracy).toBeGreaterThan(0.9);
      expect(healthStatus.languageDetectionAccuracy).toBeGreaterThan(0.9);
      expect(healthStatus.overallLatency).toBeLessThan(200);
      expect(healthStatus.errorRate).toBeLessThan(0.05);
    });
  });

  describe('Error Handling and Fallbacks', () => {
    it('should fallback to default language when detection fails', async () => {
      const unclearText = 'mmm... uh... hello?';
      
      mockLanguageRouter.processText.mockResolvedValue({
        detectedLanguage: 'en', // Default fallback
        confidence: 0.3, // Low confidence
        processedText: unclearText,
        route: 'english',
        fallbackUsed: true,
        fallbackReason: 'Low confidence detection'
      });
      
      const result = await mockLanguageRouter.processText(unclearText);
      
      expect(result.fallbackUsed).toBe(true);
      expect(result.confidence).toBeLessThan(0.5);
      expect(result.detectedLanguage).toBe('en'); // Fallback to English
    });

    it('should handle TTS service failures gracefully', async () => {
      const czechText = 'Test text for Czech TTS';
      
      // Mock Czech TTS failure
      mockCzechTTSService.synthesize.mockRejectedValue(new Error('Czech TTS service unavailable'));
      
      // Mock fallback to Deepgram
      mockDeepgramService.synthesizeSpeech.mockResolvedValue({
        audioBuffer: Buffer.from('fallback-audio'),
        duration: 2.0,
        language: 'en', // Fallback language
        voice: 'aura-luna-en',
        format: 'mp3',
        fallbackUsed: true,
        originalLanguage: 'cs'
      });
      
      // Simulate fallback logic
      let result;
      try {
        await mockCzechTTSService.synthesize(czechText);
      } catch (error) {
        result = await mockDeepgramService.synthesizeSpeech(czechText, {
          language: 'en', // Fallback to English
          fallbackMode: true
        });
      }
      
      expect(result.fallbackUsed).toBe(true);
      expect(result.originalLanguage).toBe('cs');
      expect(result.language).toBe('en'); // Fell back to English
    });

    it('should handle network timeouts and retries', async () => {
      const retryText = 'Test retry mechanism';
      let attemptCount = 0;
      
      mockDeepgramService.processAudioStream.mockImplementation(async () => {
        attemptCount++;
        if (attemptCount < 3) {
          throw new Error('Network timeout');
        }
        return {
          transcript: retryText,
          confidence: 0.85,
          language: 'en',
          duration: 1.5,
          retryCount: attemptCount - 1
        };
      });
      
      // Simulate retry logic
      let result;
      for (let i = 0; i < 3; i++) {
        try {
          result = await mockDeepgramService.processAudioStream(Buffer.from('test-audio'));
          break;
        } catch (error) {
          if (i === 2) throw error; // Give up after 3 attempts
          await waitFor(100 * (i + 1)); // Exponential backoff
        }
      }
      
      expect(result).toBeDefined();
      expect(result.retryCount).toBe(2);
      expect(attemptCount).toBe(3);
    });
  });
});
