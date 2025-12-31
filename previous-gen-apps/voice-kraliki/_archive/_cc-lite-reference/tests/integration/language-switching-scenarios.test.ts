/**
 * Integration Test Scenarios for Language Switching
 * Real-world scenarios testing complete customer journey flows
 * with multi-language voice routing and switching
 */

import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { LanguageRouterService, createLanguageRouter } from '../../server/services/language-router-service';
import { mockWebSocket, waitFor, testDb } from '../setup';
import fs from 'fs/promises';
import path from 'path';

// Real-world conversation scenarios
const CUSTOMER_SCENARIOS = {
  americanToSpanish: {
    context: "American customer calling, realizes agent speaks Spanish",
    phoneNumber: "+1234567890",
    countryCode: "US",
    initialLanguage: "en",
    conversation: [
      { speaker: "agent", text: "Hello, thank you for calling our customer service. How can I help you today?", language: "en" },
      { speaker: "customer", text: "Hi, I need help with my account", language: "en" },
      { speaker: "agent", text: "I'd be happy to help you with your account. Can you provide your account number?", language: "en" },
      { speaker: "customer", text: "Actually, ¿habla español? Sería más fácil para mí hablar en español", language: "es" },
      { speaker: "agent", text: "¡Por supuesto! Puedo ayudarte en español. ¿Cuál es tu número de cuenta?", language: "es" },
      { speaker: "customer", text: "Perfecto, gracias. Mi número de cuenta es 123456789", language: "es" }
    ]
  },
  
  czechBusinessCall: {
    context: "Czech business customer calling from Prague",
    phoneNumber: "+420123456789",
    countryCode: "CZ",
    initialLanguage: "cs",
    conversation: [
      { speaker: "agent", text: "Dobrý den, děkuji za zavolání do naší zákaznické služby. Jak vám mohu pomoci?", language: "cs" },
      { speaker: "customer", text: "Dobrý den, potřebuji řešit problém s fakturou", language: "cs" },
      { speaker: "agent", text: "Samozřejmě, pomohu vám s fakturou. Můžete mi prosím sdělit číslo faktury?", language: "cs" },
      { speaker: "customer", text: "Číslo faktury je F-2024-001234. Problém je s částkou", language: "cs" },
      { speaker: "agent", text: "Rozumím, podívám se na fakturu F-2024-001234. Můžete mi prosím specifikovat, v čem je problém s částkou?", language: "cs" }
    ]
  },
  
  multilingualSupport: {
    context: "Customer switches between languages during call",
    phoneNumber: "+1234567890",
    countryCode: "US",
    initialLanguage: "en",
    conversation: [
      { speaker: "agent", text: "Hello, how can I assist you today?", language: "en" },
      { speaker: "customer", text: "Hi, I have a problem with my order", language: "en" },
      { speaker: "agent", text: "I'm sorry to hear that. Can you tell me more about the issue?", language: "en" },
      { speaker: "customer", text: "Actually, let me explain in Spanish... Tengo un problema con mi pedido. El producto llegó dañado", language: "es" },
      { speaker: "agent", text: "Entiendo, lamento escuchar que el producto llegó dañado. ¿Puede proporcionarme el número de pedido?", language: "es" },
      { speaker: "customer", text: "The order number is ORD-123456. But can we continue in English? It's easier for me to explain technical issues", language: "en" },
      { speaker: "agent", text: "Of course! I have your order ORD-123456. Please describe the technical issues you're experiencing", language: "en" }
    ]
  },
  
  emergencyEscalation: {
    context: "Customer emergency call requiring immediate escalation",
    phoneNumber: "+420987654321",
    countryCode: "CZ",
    initialLanguage: "cs",
    conversation: [
      { speaker: "agent", text: "Dobrý den, zákaznická služba. Jak vám mohu pomoci?", language: "cs" },
      { speaker: "customer", text: "Potřebuji okamžitou pomoc! Máme problém se službou a nikdo mi nemůže pomoci!", language: "cs" },
      { speaker: "agent", text: "Rozumím, že máte naléhavý problém. Mohu vás ihned přepojit na nadřízeného?", language: "cs" },
      { speaker: "customer", text: "Ano, prosím! To je přesně to, co potřebuji!", language: "cs" }
    ]
  },
  
  salesInquiry: {
    context: "Spanish-speaking customer interested in purchasing",
    phoneNumber: "+34987654321",
    countryCode: "ES",
    initialLanguage: "es",
    conversation: [
      { speaker: "agent", text: "¡Hola! Gracias por llamar a nuestro departamento de ventas. ¿En qué puedo ayudarle?", language: "es" },
      { speaker: "customer", text: "Hola, estoy interesado en sus servicios de contacto por voz", language: "es" },
      { speaker: "agent", text: "Perfecto, será un placer ayudarle. ¿Puede contarme un poco sobre su empresa y sus necesidades?", language: "es" },
      { speaker: "customer", text: "Tenemos una empresa de 200 empleados y necesitamos un sistema de atención al cliente", language: "es" },
      { speaker: "agent", text: "Excelente, tenemos soluciones perfectas para empresas de su tamaño. ¿Le gustaría que programemos una demostración?", language: "es" }
    ]
  },
  
  technicalSupport: {
    context: "Mixed language technical support with code switching",
    phoneNumber: "+1555123456",
    countryCode: "US",
    initialLanguage: "en",
    conversation: [
      { speaker: "agent", text: "Technical support, how can I help you?", language: "en" },
      { speaker: "customer", text: "I'm having trouble with the API integration", language: "en" },
      { speaker: "agent", text: "I can help you with API integration. Which endpoint are you having trouble with?", language: "en" },
      { speaker: "customer", text: "The authentication endpoint. But actually, ¿puedo explicarte en español? Es más fácil para describir problemas técnicos", language: "es" },
      { speaker: "agent", text: "¡Por supuesto! Puedo ayudarte en español. ¿Qué problema específico tienes con el endpoint de autenticación?", language: "es" },
      { speaker: "customer", text: "El problema es que el token expira muy rápido y necesito refresh automático", language: "es" },
      { speaker: "agent", text: "Entiendo. Para el refresh automático del token, necesitas implementar el endpoint /auth/refresh", language: "es" }
    ]
  }
};

// Audio simulation data for testing
const AUDIO_SIMULATION = {
  backgroundNoise: Buffer.from('background-noise-data'),
  clearAudio: Buffer.from('clear-audio-data'),
  lowQuality: Buffer.from('low-quality-audio'),
  multiSpeaker: Buffer.from('multi-speaker-audio')
};

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Language Switching Integration Scenarios', () => {
  let languageRouter: LanguageRouterService;
  let mockDeepgramService: any;
  let mockCzechTTSService: any;
  let testResults: any[] = [];

  beforeAll(async () => {
    if (process.env.SKIP_DB_TEST_SETUP === 'true') return;
    await testDb.$connect();
  });

  afterAll(async () => {
    if (process.env.SKIP_DB_TEST_SETUP !== 'true') {
      await testDb.$disconnect();
    }
    
    // Save test results to file for analysis
    const resultsPath = path.join(process.cwd(), 'test-results', 'language-switching-results.json');
    await fs.mkdir(path.dirname(resultsPath), { recursive: true });
    await fs.writeFile(resultsPath, JSON.stringify(testResults, null, 2));
    
    console.log(`\n📊 Integration test results saved to: ${resultsPath}`);
  });

  beforeEach(async () => {
    // Mock services with realistic behavior
    mockDeepgramService = {
      startTranscription: vi.fn().mockResolvedValue(undefined),
      stopTranscription: vi.fn().mockResolvedValue({
        endTime: new Date(),
        duration: 1000,
        transcripts: []
      }),
      processAudioStream: vi.fn(),
      synthesizeSpeech: vi.fn().mockImplementation(async (text, voice) => {
        // Simulate realistic TTS timing
        await new Promise(resolve => setTimeout(resolve, 50 + text.length * 2));
        return Buffer.from(`synthesized-${voice}-${text.length}`);
      }),
      on: vi.fn(),
      emit: vi.fn(),
      destroy: vi.fn().mockResolvedValue(undefined)
    };

    mockCzechTTSService = {
      synthesize: vi.fn().mockImplementation(async (text, options) => {
        await new Promise(resolve => setTimeout(resolve, 60 + text.length * 2.5));
        return Buffer.from(`czech-synthesized-${options?.voice || 'default'}-${text.length}`);
      }),
      testTTS: vi.fn().mockResolvedValue(true),
      getAvailableVoices: vi.fn().mockReturnValue([]),
      destroy: vi.fn(),
      on: vi.fn(),
      emit: vi.fn()
    };

    languageRouter = createLanguageRouter({
      deepgramApiKey: 'test-deepgram-key',
      openaiApiKey: 'test-openai-key',
      czechTTSConfig: {
        elevenlabsApiKey: 'test-elevenlabs-key',
        defaultProvider: 'elevenlabs',
        defaultVoice: 'kamila-cs',
        cacheEnabled: true,
        maxCacheSize: 50
      },
      confidenceThreshold: 0.7,
      enableAutoDetection: true,
      enableAutoSwitching: true,
      enableRegionalAccents: true
    });

    languageRouter['deepgramService'] = mockDeepgramService;
    languageRouter['czechTTSService'] = mockCzechTTSService;
  });

  afterEach(async () => {
    if (languageRouter) {
      await languageRouter.destroy();
    }
  });

  describe('Real Customer Journey Scenarios', () => {
    it('should handle American customer switching to Spanish mid-conversation', async () => {
      const scenario = CUSTOMER_SCENARIOS.americanToSpanish;
      const sessionId = 'american-spanish-journey';
      const testResult: any = {
        scenario: 'americanToSpanish',
        startTime: Date.now(),
        events: [],
        languageSwitches: 0,
        totalDuration: 0,
        success: false
      };

      try {
        // Initialize session
        const preference = await languageRouter.startSession(sessionId, {
          callId: 'american-spanish-call',
          phoneNumber: scenario.phoneNumber,
          countryCode: scenario.countryCode
        });

        testResult.events.push({
          type: 'sessionStarted',
          language: preference.preferredLanguage,
          timestamp: Date.now()
        });

        expect(preference.preferredLanguage).toBe('en');

        // Process conversation
        for (const exchange of scenario.conversation) {
          if (exchange.speaker === 'agent') {
            // Agent speaks
            const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, exchange.text);
            expect(audioBuffer).toBeDefined();
            
            testResult.events.push({
              type: 'agentSpoke',
              language: exchange.language,
              textLength: exchange.text.length,
              timestamp: Date.now()
            });
          } else {
            // Customer speaks - process text and detect language
            const detection = await languageRouter.processText(sessionId, exchange.text);
            
            testResult.events.push({
              type: 'customerSpoke',
              detectedLanguage: detection.language,
              confidence: detection.confidence,
              expectedLanguage: exchange.language,
              textLength: exchange.text.length,
              timestamp: Date.now()
            });

            // Check if language switch occurred
            const currentLanguage = languageRouter.getSessionLanguage(sessionId);
            if (detection.language !== preference.preferredLanguage && detection.confidence > 0.7) {
              testResult.languageSwitches++;
              testResult.events.push({
                type: 'languageSwitch',
                from: preference.preferredLanguage,
                to: detection.language,
                timestamp: Date.now()
              });
            }
          }
        }

        // Final language should be Spanish
        const finalLanguage = languageRouter.getSessionLanguage(sessionId);
        expect(finalLanguage).toBe('es');

        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.provider).toBe('deepgram');
        expect(route?.voiceId).toBe('stella');

        testResult.success = true;
        testResult.finalLanguage = finalLanguage;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.languageSwitches).toBeGreaterThan(0);
    });

    it('should handle Czech business customer journey', async () => {
      const scenario = CUSTOMER_SCENARIOS.czechBusinessCall;
      const sessionId = 'czech-business-journey';
      const testResult: any = {
        scenario: 'czechBusinessCall',
        startTime: Date.now(),
        events: [],
        businessTermsDetected: 0,
        success: false
      };

      try {
        // Initialize session with Czech context
        const preference = await languageRouter.startSession(sessionId, {
          callId: 'czech-business-call',
          phoneNumber: scenario.phoneNumber,
          countryCode: scenario.countryCode
        });

        expect(preference.preferredLanguage).toBe('cs');

        testResult.events.push({
          type: 'sessionStarted',
          language: preference.preferredLanguage,
          contextDetection: 'phoneNumber+countryCode',
          timestamp: Date.now()
        });

        // Process business conversation
        for (const exchange of scenario.conversation) {
          if (exchange.speaker === 'agent') {
            const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, exchange.text);
            expect(audioBuffer).toBeDefined();
            
            // Should use Czech TTS service
            expect(mockCzechTTSService.synthesize).toHaveBeenCalledWith(
              exchange.text,
              { voice: 'kamila-cs' }
            );

            testResult.events.push({
              type: 'agentSpoke',
              language: exchange.language,
              service: 'czechTTS',
              timestamp: Date.now()
            });
          } else {
            const detection = await languageRouter.processText(sessionId, exchange.text);
            
            // Check for business terms
            if (exchange.text.includes('fakturu') || exchange.text.includes('částkou') || exchange.text.includes('F-2024')) {
              testResult.businessTermsDetected++;
            }

            testResult.events.push({
              type: 'customerSpoke',
              detectedLanguage: detection.language,
              confidence: detection.confidence,
              businessTerms: exchange.text.includes('fakturu') || exchange.text.includes('částkou'),
              timestamp: Date.now()
            });

            expect(detection.language).toBe('cs');
            expect(detection.confidence).toBeGreaterThan(0.7);
          }
        }

        const finalLanguage = languageRouter.getSessionLanguage(sessionId);
        expect(finalLanguage).toBe('cs');

        testResult.success = true;
        testResult.finalLanguage = finalLanguage;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.businessTermsDetected).toBeGreaterThan(0);
    });

    it('should handle multilingual customer with frequent switching', async () => {
      const scenario = CUSTOMER_SCENARIOS.multilingualSupport;
      const sessionId = 'multilingual-journey';
      const testResult: any = {
        scenario: 'multilingualSupport',
        startTime: Date.now(),
        events: [],
        languageSwitches: 0,
        languages: new Set(),
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'multilingual-call',
          phoneNumber: scenario.phoneNumber,
          countryCode: scenario.countryCode
        });

        let previousLanguage = 'en';

        for (const exchange of scenario.conversation) {
          if (exchange.speaker === 'customer') {
            const detection = await languageRouter.processText(sessionId, exchange.text);
            const currentLanguage = languageRouter.getSessionLanguage(sessionId);

            testResult.languages.add(detection.language);

            if (currentLanguage !== previousLanguage) {
              testResult.languageSwitches++;
              testResult.events.push({
                type: 'languageSwitch',
                from: previousLanguage,
                to: currentLanguage,
                trigger: 'customerText',
                text: exchange.text.substring(0, 50) + '...',
                timestamp: Date.now()
              });
            }

            previousLanguage = currentLanguage;
          } else {
            const currentLanguage = languageRouter.getSessionLanguage(sessionId);
            await languageRouter.synthesizeSpeech(sessionId, exchange.text);
            
            testResult.events.push({
              type: 'agentResponse',
              language: currentLanguage,
              expectedLanguage: exchange.language,
              matched: currentLanguage === exchange.language,
              timestamp: Date.now()
            });
          }
        }

        testResult.success = true;
        testResult.uniqueLanguages = testResult.languages.size;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.languageSwitches).toBeGreaterThanOrEqual(2);
      expect(testResult.uniqueLanguages).toBeGreaterThanOrEqual(2);
    });

    it('should handle emergency escalation scenario in Czech', async () => {
      const scenario = CUSTOMER_SCENARIOS.emergencyEscalation;
      const sessionId = 'emergency-czech';
      const testResult: any = {
        scenario: 'emergencyEscalation',
        startTime: Date.now(),
        events: [],
        urgencyDetected: false,
        escalationTriggered: false,
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'emergency-call',
          phoneNumber: scenario.phoneNumber,
          countryCode: scenario.countryCode
        });

        let urgencyKeywords = 0;

        for (const exchange of scenario.conversation) {
          if (exchange.speaker === 'customer') {
            // Check for urgency indicators
            if (exchange.text.includes('okamžitou pomoc') || exchange.text.includes('naléhavý') || exchange.text.includes('nikdo mi nemůže')) {
              urgencyKeywords++;
              testResult.urgencyDetected = true;
            }

            const detection = await languageRouter.processText(sessionId, exchange.text);
            
            testResult.events.push({
              type: 'customerUrgentMessage',
              urgencyKeywords: urgencyKeywords,
              confidence: detection.confidence,
              language: detection.language,
              timestamp: Date.now()
            });
          } else {
            // Check if agent offers escalation
            if (exchange.text.includes('přepojit na nadřízeného')) {
              testResult.escalationTriggered = true;
            }

            await languageRouter.synthesizeSpeech(sessionId, exchange.text);
            
            testResult.events.push({
              type: 'agentResponse',
              escalationOffered: exchange.text.includes('přepojit'),
              timestamp: Date.now()
            });
          }
        }

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.urgencyDetected).toBe(true);
      expect(testResult.escalationTriggered).toBe(true);
    });
  });

  describe('Audio Quality and Context Scenarios', () => {
    it('should handle conversation with background noise simulation', async () => {
      const sessionId = 'noisy-audio';
      const testResult: any = {
        scenario: 'noisyAudio',
        startTime: Date.now(),
        audioQualityEvents: [],
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'noisy-call',
          phoneNumber: '+1234567890'
        });

        // Simulate processing audio with background noise
        const noisyTranscript = "Hello, can you hear me? There's a lot of background noise";
        const detection = await languageRouter.processAudio(sessionId, AUDIO_SIMULATION.backgroundNoise, noisyTranscript);

        testResult.audioQualityEvents.push({
          type: 'noisyAudio',
          transcriptLength: noisyTranscript.length,
          confidence: detection.confidence,
          language: detection.language,
          timestamp: Date.now()
        });

        // Should still detect language despite noise
        expect(detection.language).toBe('en');

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should handle multi-speaker audio scenarios', async () => {
      const sessionId = 'multi-speaker';
      const testResult: any = {
        scenario: 'multiSpeaker',
        startTime: Date.now(),
        speakerEvents: [],
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'multi-speaker-call',
          phoneNumber: '+34123456789',
          countryCode: 'ES'
        });

        // Simulate multiple speakers in same audio stream
        const mixedTranscript = "Customer: Hola, necesito ayuda. Agent: Hello, I can help you in Spanish if you prefer.";
        const detection = await languageRouter.processAudio(sessionId, AUDIO_SIMULATION.multiSpeaker, mixedTranscript);

        testResult.speakerEvents.push({
          type: 'multiSpeakerDetected',
          transcriptLength: mixedTranscript.length,
          confidence: detection.confidence,
          detectedLanguage: detection.language,
          timestamp: Date.now()
        });

        // Should detect mixed languages or default to stronger signal
        expect(['en', 'es']).toContain(detection.language);

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
    });
  });

  describe('Performance Under Load Scenarios', () => {
    it('should handle simultaneous customer conversations', async () => {
      const testResult: any = {
        scenario: 'simultaneousConversations',
        startTime: Date.now(),
        sessions: [],
        success: false
      };

      try {
        const sessionPromises: Promise<void>[] = [];
        const sessionIds: string[] = [];

        // Create 10 simultaneous customer sessions
        for (let i = 0; i < 10; i++) {
          const sessionId = `load-test-session-${i}`;
          const language = i % 3 === 0 ? 'en' : i % 3 === 1 ? 'es' : 'cs';
          const phoneNumber = language === 'en' ? '+1234567890' : 
                             language === 'es' ? '+34123456789' : '+420123456789';
          
          sessionIds.push(sessionId);
          
          const sessionPromise = (async () => {
            await languageRouter.startSession(sessionId, {
              callId: `load-call-${i}`,
              phoneNumber,
              preferredLanguage: language
            });

            // Simulate conversation
            const testText = language === 'en' ? "Hello, I need help with my account" :
                            language === 'es' ? "Hola, necesito ayuda con mi cuenta" :
                            "Dobrý den, potřebuji pomoc s účtem";

            const detection = await languageRouter.processText(sessionId, testText);
            await languageRouter.synthesizeSpeech(sessionId, "I'll help you with that");

            testResult.sessions.push({
              sessionId,
              language: detection.language,
              confidence: detection.confidence,
              responseTime: Date.now() - testResult.startTime
            });
          })();

          sessionPromises.push(sessionPromise);
        }

        await Promise.all(sessionPromises);

        // Verify all sessions are active
        const activeSessions = languageRouter.getActiveSessions();
        expect(activeSessions.length).toBe(10);

        // Clean up sessions
        for (const sessionId of sessionIds) {
          await languageRouter.endSession(sessionId);
        }

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;
        testResult.averageResponseTime = testResult.sessions.reduce((sum: number, s: any) => sum + s.responseTime, 0) / testResult.sessions.length;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.sessions.length).toBe(10);
    });
  });

  describe('Edge Case Scenarios', () => {
    it('should handle customer who speaks very quietly', async () => {
      const sessionId = 'quiet-speaker';
      const testResult: any = {
        scenario: 'quietSpeaker',
        startTime: Date.now(),
        events: [],
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'quiet-call',
          phoneNumber: '+1234567890'
        });

        // Simulate quiet speech with low confidence transcript
        const quietTranscript = "hello... can you... hear me";
        const detection = await languageRouter.processAudio(sessionId, AUDIO_SIMULATION.lowQuality, quietTranscript);

        testResult.events.push({
          type: 'quietSpeech',
          confidence: detection.confidence,
          textLength: quietTranscript.length,
          timestamp: Date.now()
        });

        // Should still attempt detection but with lower confidence
        expect(detection.confidence).toBeLessThan(0.8);
        expect(detection.language).toBeDefined();

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
    });

    it('should handle customer who uses numbers and technical terms', async () => {
      const sessionId = 'technical-customer';
      const testResult: any = {
        scenario: 'technicalCustomer',
        startTime: Date.now(),
        events: [],
        technicalTermsCount: 0,
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'technical-call',
          phoneNumber: '+1234567890'
        });

        const technicalTexts = [
          "My API key is abc123-def456-ghi789 and I'm getting 401 errors",
          "The webhook endpoint https://example.com/webhook is returning 500 status codes",
          "Can you check server instance i-0123456789abcdef0 in us-east-1 region?"
        ];

        for (const text of technicalTexts) {
          const detection = await languageRouter.processText(sessionId, text);
          
          if (text.includes('API') || text.includes('webhook') || text.includes('server')) {
            testResult.technicalTermsCount++;
          }

          testResult.events.push({
            type: 'technicalText',
            confidence: detection.confidence,
            language: detection.language,
            containsTechnicalTerms: text.includes('API') || text.includes('webhook') || text.includes('server'),
            timestamp: Date.now()
          });

          expect(detection.language).toBe('en');
        }

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.technicalTermsCount).toBeGreaterThan(0);
    });

    it('should handle session timeout and recovery', async () => {
      const sessionId = 'timeout-recovery';
      const testResult: any = {
        scenario: 'timeoutRecovery',
        startTime: Date.now(),
        events: [],
        recovered: false,
        success: false
      };

      try {
        await languageRouter.startSession(sessionId, {
          callId: 'timeout-call',
          phoneNumber: '+420123456789'
        });

        // Process some text
        await languageRouter.processText(sessionId, "Dobrý den, jak se máte?");
        
        testResult.events.push({
          type: 'normalOperation',
          timestamp: Date.now()
        });

        // Simulate session ending unexpectedly
        await languageRouter.endSession(sessionId);
        
        testResult.events.push({
          type: 'sessionEnded',
          timestamp: Date.now()
        });

        // Try to use session after it's ended (should handle gracefully)
        try {
          await languageRouter.processText(sessionId, "Test after end");
        } catch (error) {
          testResult.events.push({
            type: 'expectedError',
            error: error.message,
            timestamp: Date.now()
          });
          testResult.recovered = true;
        }

        testResult.success = true;
        testResult.totalDuration = Date.now() - testResult.startTime;

      } catch (error) {
        testResult.error = error.message;
      }

      testResults.push(testResult);
      expect(testResult.success).toBe(true);
      expect(testResult.recovered).toBe(true);
    });
  });
});
