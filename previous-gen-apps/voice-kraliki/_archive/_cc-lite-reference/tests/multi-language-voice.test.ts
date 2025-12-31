/**
 * Comprehensive Multi-Language Voice Flow Testing Suite
 * Tests English, Spanish, and Czech voice flows with language detection and routing
 * 
 * Test Categories:
 * 1. Language Detection Tests
 * 2. Voice Service Routing Tests  
 * 3. Language Switching Scenarios
 * 4. Integration Tests
 * 5. Performance Tests
 * 6. Error Handling Tests
 */

import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { LanguageRouterService, LanguageDetector, createLanguageRouter } from '../server/services/language-router-service';
import { DeepgramVoiceService } from '../server/services/deepgram-voice-service';
import { CzechTTSService, createCzechTTSService } from '../server/services/czech-tts-service';
import { mockWebSocket, waitFor, testDb } from './setup';

// Test Data
const TEST_TEXTS = {
  english: {
    short: "Hello, how can I help you?",
    medium: "Hello, thank you for calling our customer service. How can I help you today?",
    long: "Hello and welcome to our customer service center. Thank you for calling us today. We really appreciate your business and we're here to help you with any questions or concerns you might have. How can I assist you today?",
    businessTerms: "We need to process your invoice and update your account with the new payment information.",
    contractions: "I don't think we can't resolve this issue. Shouldn't we contact the supervisor?"
  },
  spanish: {
    short: "Hola, ¿cómo puedo ayudarte?",
    medium: "Hola, gracias por llamar a nuestro servicio al cliente. ¿Cómo puedo ayudarte hoy?",
    long: "Hola y bienvenido a nuestro centro de servicio al cliente. Gracias por llamarnos hoy. Realmente apreciamos su negocio y estamos aquí para ayudarlo con cualquier pregunta o inquietud que pueda tener. ¿Cómo puedo ayudarte hoy?",
    businessTerms: "Necesitamos procesar su factura y actualizar su cuenta con la nueva información de pago.",
    accents: "Señor González, su número de teléfono móvil terminó en España."
  },
  czech: {
    short: "Ahoj, jak vám mohu pomoci?",
    medium: "Dobrý den, děkuji za zavolání do naší zákaznické služby. Jak vám dnes mohu pomoci?",
    long: "Dobrý den a vítejte v našem centru zákaznické služby. Děkujeme, že jste nás dnes kontaktovali. Velmi si vážíme vašeho obchodu a jsme tu, abychom vám pomohli s jakýmikoli otázkami nebo problémy, které byste mohli mít. Jak vám mohu dnes pomoci?",
    businessTerms: "Potřebujeme zpracovat vaši fakturu a aktualizovat váš účet s novými platebními informacemi.",
    diacritics: "Pošlete prosím dokumenty na naši e-mailovou adresu včetně příloh."
  }
};

const TEST_PHONE_NUMBERS = {
  czech: '+420123456789',
  spanish: '+34123456789',
  mexican: '+52123456789',
  american: '+1234567890',
  british: '+44123456789'
};

const TEST_AUDIO_CONTEXTS = {
  customerService: 'customer_service',
  sales: 'sales',
  support: 'support',
  emergency: 'emergency',
  healthcare: 'healthcare'
};

describe('Multi-Language Voice Flow Integration', () => {
  let languageRouter: LanguageRouterService;
  let mockDeepgramService: any;
  let mockCzechTTSService: any;

  beforeAll(async () => {
    // Initialize test database
    await testDb.$connect();
  });

  afterAll(async () => {
    await testDb.$disconnect();
  });

  beforeEach(async () => {
    // Mock Deepgram service
    mockDeepgramService = {
      startTranscription: vi.fn().mockResolvedValue(undefined),
      stopTranscription: vi.fn().mockResolvedValue({
        endTime: new Date(),
        duration: 1000,
        transcripts: []
      }),
      processAudioStream: vi.fn(),
      synthesizeSpeech: vi.fn().mockResolvedValue(Buffer.from('mock-audio')),
      getTranscription: vi.fn().mockReturnValue({
        callId: 'test-call',
        sessionId: 'test-session',
        transcripts: []
      }),
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
      destroy: vi.fn().mockResolvedValue(undefined)
    };

    // Mock Czech TTS service
    mockCzechTTSService = {
      synthesize: vi.fn().mockResolvedValue(Buffer.from('mock-czech-audio')),
      synthesizeStream: vi.fn(),
      testTTS: vi.fn().mockResolvedValue(true),
      getAvailableVoices: vi.fn().mockReturnValue([]),
      clearCache: vi.fn(),
      getCacheStats: vi.fn().mockReturnValue({ entries: 0, sizeBytes: 0, sizeMB: 0 }),
      destroy: vi.fn(),
      on: vi.fn(),
      emit: vi.fn()
    };

    // Initialize language router with mocked services
    languageRouter = createLanguageRouter({
      deepgramApiKey: 'test-key',
      openaiApiKey: 'test-openai-key',
      czechTTSConfig: {
        elevenlabsApiKey: 'test-elevenlabs-key',
        defaultProvider: 'elevenlabs',
        defaultVoice: 'kamila-cs',
        cacheEnabled: true,
        maxCacheSize: 50
      },
      confidenceThreshold: 0.7,
      textSampleSize: 20,
      audioSampleDuration: 3,
      defaultLanguage: 'en',
      enableAutoDetection: true,
      enableAutoSwitching: true,
      enableRegionalAccents: true
    });

    // Replace real services with mocks
    languageRouter['deepgramService'] = mockDeepgramService;
    languageRouter['czechTTSService'] = mockCzechTTSService;
  });

  afterEach(async () => {
    if (languageRouter) {
      await languageRouter.destroy();
    }
  });

  describe('Language Detection Tests', () => {
    describe('Text-based Language Detection', () => {
      it('should accurately detect English text with high confidence', () => {
        const result = LanguageDetector.detectFromText(TEST_TEXTS.english.medium);
        
        expect(result.language).toBe('en');
        expect(result.confidence).toBeGreaterThan(0.6);
        expect(result.source).toBe('text');
        expect(result.patterns).toBeDefined();
        expect(result.timestamp).toBeInstanceOf(Date);
      });

      it('should accurately detect Spanish text with high confidence', () => {
        const result = LanguageDetector.detectFromText(TEST_TEXTS.spanish.medium);
        
        expect(result.language).toBe('es');
        expect(result.confidence).toBeGreaterThan(0.6);
        expect(result.source).toBe('text');
        expect(result.patterns).toContain('spanish-diacritics');
      });

      it('should accurately detect Czech text with high confidence', () => {
        const result = LanguageDetector.detectFromText(TEST_TEXTS.czech.medium);
        
        expect(result.language).toBe('cs');
        expect(result.confidence).toBeGreaterThan(0.6);
        expect(result.source).toBe('text');
        expect(result.patterns).toContain('czech-diacritics');
      });

      it('should handle business terminology correctly', () => {
        const englishBusiness = LanguageDetector.detectFromText(TEST_TEXTS.english.businessTerms);
        const spanishBusiness = LanguageDetector.detectFromText(TEST_TEXTS.spanish.businessTerms);
        const czechBusiness = LanguageDetector.detectFromText(TEST_TEXTS.czech.businessTerms);

        expect(englishBusiness.language).toBe('en');
        expect(spanishBusiness.language).toBe('es');
        expect(czechBusiness.language).toBe('cs');

        // All should have high confidence for business terms
        expect(englishBusiness.confidence).toBeGreaterThan(0.5);
        expect(spanishBusiness.confidence).toBeGreaterThan(0.5);
        expect(czechBusiness.confidence).toBeGreaterThan(0.5);
      });

      it('should detect diacritics and special characters', () => {
        const spanishResult = LanguageDetector.detectFromText(TEST_TEXTS.spanish.accents);
        const czechResult = LanguageDetector.detectFromText(TEST_TEXTS.czech.diacritics);

        expect(spanishResult.patterns).toContain('spanish-diacritics');
        expect(czechResult.patterns).toContain('czech-diacritics');
      });

      it('should handle short text with lower confidence', () => {
        const shortEnglish = LanguageDetector.detectFromText("Hello");
        const shortSpanish = LanguageDetector.detectFromText("Hola");
        const shortCzech = LanguageDetector.detectFromText("Ahoj");

        // Short texts should have lower confidence
        expect(shortEnglish.confidence).toBeLessThan(0.5);
        expect(shortSpanish.confidence).toBeLessThan(0.5);
        expect(shortCzech.confidence).toBeLessThan(0.5);
      });

      it('should fallback to English for very short or unclear text', () => {
        const veryShort = LanguageDetector.detectFromText("Hi");
        const unclear = LanguageDetector.detectFromText("123 456");

        expect(veryShort.language).toBe('en');
        expect(unclear.language).toBe('en');
        expect(veryShort.confidence).toBeLessThan(0.4);
        expect(unclear.confidence).toBeLessThan(0.4);
      });
    });

    describe('Context-based Language Detection', () => {
      it('should detect language from Czech phone numbers', () => {
        const result = LanguageDetector.detectFromContext(TEST_PHONE_NUMBERS.czech, 'CZ');
        
        expect(result.language).toBe('cs');
        expect(result.confidence).toBe(0.9);
        expect(result.source).toBe('context');
        expect(result.patterns).toContain('phone-number');
        expect(result.patterns).toContain('country-cz');
      });

      it('should detect language from Spanish phone numbers', () => {
        const spanishResult = LanguageDetector.detectFromContext(TEST_PHONE_NUMBERS.spanish, 'ES');
        const mexicanResult = LanguageDetector.detectFromContext(TEST_PHONE_NUMBERS.mexican, 'MX');

        expect(spanishResult.language).toBe('es');
        expect(mexicanResult.language).toBe('es');
        expect(spanishResult.confidence).toBe(0.9);
        expect(mexicanResult.confidence).toBe(0.9);
      });

      it('should detect language from English-speaking countries', () => {
        const americanResult = LanguageDetector.detectFromContext(TEST_PHONE_NUMBERS.american, 'US');
        const britishResult = LanguageDetector.detectFromContext(TEST_PHONE_NUMBERS.british, 'GB');

        expect(americanResult.language).toBe('en');
        expect(britishResult.language).toBe('en');
        expect(americanResult.confidence).toBe(0.8);
        expect(britishResult.confidence).toBe(0.8);
      });

      it('should handle unknown country codes gracefully', () => {
        const result = LanguageDetector.detectFromContext('+999123456789', 'XX');
        
        expect(result.language).toBe('en');
        expect(result.confidence).toBe(0.6);
      });
    });

    describe('Audio-based Language Detection', () => {
      it('should use transcript for audio detection when available', async () => {
        const audioBuffer = Buffer.from('mock-audio-data');
        const transcript = TEST_TEXTS.spanish.medium;
        
        const result = await LanguageDetector.detectFromAudio(audioBuffer, transcript);
        
        expect(result.language).toBe('es');
        expect(result.source).toBe('audio');
        expect(result.confidence).toBeGreaterThan(0.5);
      });

      it('should fallback to English for audio without transcript', async () => {
        const audioBuffer = Buffer.from('mock-audio-data');
        
        const result = await LanguageDetector.detectFromAudio(audioBuffer);
        
        expect(result.language).toBe('en');
        expect(result.source).toBe('audio');
        expect(result.confidence).toBe(0.3);
      });
    });
  });

  describe('Language Router Service Tests', () => {
    describe('Session Management', () => {
      it('should start session with context-based language detection', async () => {
        const sessionId = 'test-session-1';
        const callId = 'test-call-1';
        
        const preference = await languageRouter.startSession(sessionId, {
          callId,
          phoneNumber: TEST_PHONE_NUMBERS.czech,
          countryCode: 'CZ'
        });

        expect(preference.sessionId).toBe(sessionId);
        expect(preference.preferredLanguage).toBe('cs');
        expect(preference.detectedLanguage).toBe('cs');
        expect(preference.allowAutoSwitch).toBe(true);
        
        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.language).toBe('cs');
        expect(route?.provider).toBe('czech-tts');
      });

      it('should start session with manual language preference', async () => {
        const sessionId = 'test-session-2';
        const callId = 'test-call-2';
        
        const preference = await languageRouter.startSession(sessionId, {
          callId,
          preferredLanguage: 'es'
        });

        expect(preference.preferredLanguage).toBe('es');
        
        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.language).toBe('es');
        expect(route?.provider).toBe('deepgram');
        expect(route?.voiceId).toBe('stella');
      });

      it('should fall back to default language when no detection possible', async () => {
        const sessionId = 'test-session-3';
        const callId = 'test-call-3';
        
        const preference = await languageRouter.startSession(sessionId, {
          callId
        });

        expect(preference.preferredLanguage).toBe('en');
        
        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.language).toBe('en');
        expect(route?.provider).toBe('deepgram');
      });

      it('should end session and cleanup resources', async () => {
        const sessionId = 'test-session-4';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-4',
          preferredLanguage: 'en'
        });

        expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');
        
        await languageRouter.endSession(sessionId);
        
        expect(languageRouter.getSessionLanguage(sessionId)).toBeUndefined();
        expect(languageRouter.getSessionRoute(sessionId)).toBeUndefined();
      });
    });

    describe('Text Processing and Language Switching', () => {
      it('should detect and switch language during conversation', async () => {
        const sessionId = 'test-session-switch';
        
        // Start with English
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-switch',
          preferredLanguage: 'en'
        });

        expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');

        // Process Spanish text - should trigger switch
        const detection = await languageRouter.processText(sessionId, TEST_TEXTS.spanish.long);
        
        expect(detection.language).toBe('es');
        expect(detection.confidence).toBeGreaterThan(0.7);
        
        // Language should have switched
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('es');
        
        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.language).toBe('es');
        expect(route?.provider).toBe('deepgram');
      });

      it('should not switch for low-confidence detections', async () => {
        const sessionId = 'test-session-no-switch';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-no-switch',
          preferredLanguage: 'en'
        });

        // Process short ambiguous text
        const detection = await languageRouter.processText(sessionId, "Si");
        
        // Should detect but not switch due to low confidence
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');
      });

      it('should handle manual language switching', async () => {
        const sessionId = 'test-session-manual';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-manual',
          preferredLanguage: 'en'
        });

        // Manually set language
        await languageRouter.setSessionLanguage(sessionId, 'cs', true);
        
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('cs');
        
        const route = languageRouter.getSessionRoute(sessionId);
        expect(route?.language).toBe('cs');
        expect(route?.provider).toBe('czech-tts');
      });
    });
  });

  describe('Voice Service Integration Tests', () => {
    describe('TTS Service Routing', () => {
      it('should route English TTS to Deepgram service', async () => {
        const sessionId = 'test-tts-en';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-tts-en',
          preferredLanguage: 'en'
        });

        const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.english.short);
        
        expect(mockDeepgramService.synthesizeSpeech).toHaveBeenCalledWith(
          TEST_TEXTS.english.short,
          'asteria'
        );
        expect(audioBuffer).toEqual(Buffer.from('mock-audio'));
      });

      it('should route Spanish TTS to Deepgram service', async () => {
        const sessionId = 'test-tts-es';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-tts-es',
          preferredLanguage: 'es'
        });

        const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.spanish.short);
        
        expect(mockDeepgramService.synthesizeSpeech).toHaveBeenCalledWith(
          TEST_TEXTS.spanish.short,
          'stella'
        );
        expect(audioBuffer).toEqual(Buffer.from('mock-audio'));
      });

      it('should route Czech TTS to Czech TTS service', async () => {
        const sessionId = 'test-tts-cs';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-tts-cs',
          preferredLanguage: 'cs'
        });

        const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.czech.short);
        
        expect(mockCzechTTSService.synthesize).toHaveBeenCalledWith(
          TEST_TEXTS.czech.short,
          { voice: 'kamila-cs' }
        );
        expect(audioBuffer).toEqual(Buffer.from('mock-czech-audio'));
      });

      it('should handle TTS service errors gracefully', async () => {
        const sessionId = 'test-tts-error';
        
        await languageRouter.startSession(sessionId, {
          callId: 'test-call-tts-error',
          preferredLanguage: 'en'
        });

        // Mock service to throw error
        mockDeepgramService.synthesizeSpeech.mockRejectedValue(new Error('TTS Error'));

        const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, "Test text");
        
        expect(audioBuffer).toBeNull();
      });
    });

    describe('Service Health and Status', () => {
      it('should report service availability correctly', () => {
        const health = languageRouter.getHealthStatus();
        
        expect(health.deepgramAvailable).toBe(true);
        expect(health.czechTTSAvailable).toBe(true);
        expect(health.config.autoDetectionEnabled).toBe(true);
        expect(health.config.autoSwitchingEnabled).toBe(true);
        expect(health.config.confidenceThreshold).toBe(0.7);
        expect(health.config.defaultLanguage).toBe('en');
      });

      it('should track active sessions', async () => {
        const session1 = 'session-1';
        const session2 = 'session-2';
        
        await languageRouter.startSession(session1, { callId: 'call-1' });
        await languageRouter.startSession(session2, { callId: 'call-2' });
        
        const activeSessions = languageRouter.getActiveSessions();
        expect(activeSessions).toHaveLength(2);
        expect(activeSessions).toContain(session1);
        expect(activeSessions).toContain(session2);
        
        const health = languageRouter.getHealthStatus();
        expect(health.activeSessions).toBe(2);
      });

      it('should provide session statistics', async () => {
        const sessionId = 'stats-session';
        
        await languageRouter.startSession(sessionId, {
          callId: 'stats-call',
          preferredLanguage: 'es'
        });

        const stats = languageRouter.getSessionStats(sessionId);
        
        expect(stats).toBeDefined();
        expect(stats?.sessionId).toBe(sessionId);
        expect(stats?.currentLanguage).toBe('es');
        expect(stats?.preferredLanguage).toBe('es');
        expect(stats?.provider).toBe('deepgram');
        expect(stats?.autoSwitchEnabled).toBe(true);
        expect(stats?.lastUpdate).toBeInstanceOf(Date);
      });
    });
  });

  describe('Integration Scenarios', () => {
    describe('Customer Journey - English to Spanish Switch', () => {
      it('should handle customer starting in English and switching to Spanish', async () => {
        const sessionId = 'journey-en-es';
        const callId = 'call-journey-en-es';
        
        // Customer calls from US number
        const preference = await languageRouter.startSession(sessionId, {
          callId,
          phoneNumber: TEST_PHONE_NUMBERS.american,
          countryCode: 'US'
        });

        expect(preference.preferredLanguage).toBe('en');

        // Agent greets in English
        let audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.english.medium);
        expect(audioBuffer).toBeDefined();

        // Customer responds in Spanish
        const detection = await languageRouter.processText(sessionId, TEST_TEXTS.spanish.long);
        expect(detection.language).toBe('es');

        // Language should switch to Spanish
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('es');

        // Agent now responds in Spanish
        audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.spanish.medium);
        expect(mockDeepgramService.synthesizeSpeech).toHaveBeenCalledWith(
          TEST_TEXTS.spanish.medium,
          'stella'
        );
      });
    });

    describe('Czech Customer Support Flow', () => {
      it('should handle Czech customer from context detection', async () => {
        const sessionId = 'czech-support';
        const callId = 'call-czech-support';
        
        // Czech customer with Prague number
        const preference = await languageRouter.startSession(sessionId, {
          callId,
          phoneNumber: TEST_PHONE_NUMBERS.czech,
          countryCode: 'CZ'
        });

        expect(preference.preferredLanguage).toBe('cs');
        expect(preference.detectedLanguage).toBe('cs');

        // Immediate Czech greeting
        const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.czech.medium);
        
        expect(mockCzechTTSService.synthesize).toHaveBeenCalledWith(
          TEST_TEXTS.czech.medium,
          { voice: 'kamila-cs' }
        );

        // Customer response in Czech should reinforce detection
        const detection = await languageRouter.processText(sessionId, TEST_TEXTS.czech.businessTerms);
        expect(detection.language).toBe('cs');
        expect(detection.confidence).toBeGreaterThan(0.7);
      });
    });

    describe('Mixed Language Conversation Handling', () => {
      it('should handle conversation with multiple language switches', async () => {
        const sessionId = 'mixed-conversation';
        
        await languageRouter.startSession(sessionId, {
          callId: 'mixed-call',
          preferredLanguage: 'en'
        });

        // Start English
        await languageRouter.processText(sessionId, TEST_TEXTS.english.medium);
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');

        // Switch to Spanish
        await languageRouter.processText(sessionId, TEST_TEXTS.spanish.long);
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('es');

        // Back to English
        await languageRouter.processText(sessionId, TEST_TEXTS.english.businessTerms);
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');

        // To Czech
        await languageRouter.processText(sessionId, TEST_TEXTS.czech.diacritics);
        expect(languageRouter.getSessionLanguage(sessionId)).toBe('cs');
      });
    });

    describe('Regional Accent and Dialect Handling', () => {
      it('should handle different Spanish-speaking regions', async () => {
        // Spain
        const sessionES = 'session-spain';
        await languageRouter.startSession(sessionES, {
          callId: 'call-spain',
          phoneNumber: TEST_PHONE_NUMBERS.spanish,
          countryCode: 'ES'
        });

        // Mexico  
        const sessionMX = 'session-mexico';
        await languageRouter.startSession(sessionMX, {
          callId: 'call-mexico',
          phoneNumber: TEST_PHONE_NUMBERS.mexican,
          countryCode: 'MX'
        });

        // Both should detect Spanish
        expect(languageRouter.getSessionLanguage(sessionES)).toBe('es');
        expect(languageRouter.getSessionLanguage(sessionMX)).toBe('es');

        // Both should use same voice service but could have different configs
        const routeES = languageRouter.getSessionRoute(sessionES);
        const routeMX = languageRouter.getSessionRoute(sessionMX);
        
        expect(routeES?.provider).toBe('deepgram');
        expect(routeMX?.provider).toBe('deepgram');
        expect(routeES?.language).toBe('es');
        expect(routeMX?.language).toBe('es');
      });
    });
  });

  describe('Performance Tests', () => {
    it('should detect language quickly for short texts', async () => {
      const startTime = Date.now();
      
      // Test multiple short text detections
      for (let i = 0; i < 10; i++) {
        LanguageDetector.detectFromText(TEST_TEXTS.english.short);
        LanguageDetector.detectFromText(TEST_TEXTS.spanish.short);
        LanguageDetector.detectFromText(TEST_TEXTS.czech.short);
      }
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete in under 100ms for 30 detections
      expect(duration).toBeLessThan(100);
    });

    it('should handle concurrent session processing', async () => {
      const startTime = Date.now();
      const sessionPromises: Promise<any>[] = [];
      
      // Create 20 concurrent sessions
      for (let i = 0; i < 20; i++) {
        const sessionId = `perf-session-${i}`;
        const promise = languageRouter.startSession(sessionId, {
          callId: `perf-call-${i}`,
          preferredLanguage: i % 3 === 0 ? 'en' : i % 3 === 1 ? 'es' : 'cs'
        });
        sessionPromises.push(promise);
      }
      
      await Promise.all(sessionPromises);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete in under 500ms
      expect(duration).toBeLessThan(500);
      
      // All sessions should be active
      const activeSessions = languageRouter.getActiveSessions();
      expect(activeSessions).toHaveLength(20);
    });

    it('should measure TTS synthesis performance', async () => {
      const sessionId = 'perf-tts';
      
      await languageRouter.startSession(sessionId, {
        callId: 'perf-tts-call',
        preferredLanguage: 'en'
      });

      const startTime = Date.now();
      
      // Multiple TTS requests
      const ttsPromises = [
        languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.english.short),
        languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.english.medium),
        languageRouter.synthesizeSpeech(sessionId, TEST_TEXTS.english.long)
      ];
      
      await Promise.all(ttsPromises);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete quickly with mocked services
      expect(duration).toBeLessThan(50);
    });

    it('should measure language switching latency', async () => {
      const sessionId = 'perf-switch';
      
      await languageRouter.startSession(sessionId, {
        callId: 'perf-switch-call',
        preferredLanguage: 'en'
      });

      const startTime = Date.now();
      
      // Multiple language switches
      await languageRouter.processText(sessionId, TEST_TEXTS.spanish.long);
      await languageRouter.processText(sessionId, TEST_TEXTS.czech.long);
      await languageRouter.processText(sessionId, TEST_TEXTS.english.long);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete language switches quickly
      expect(duration).toBeLessThan(100);
      
      // Final language should be English
      expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle invalid session IDs gracefully', async () => {
      await expect(
        languageRouter.processText('invalid-session', "Test text")
      ).rejects.toThrow('Session invalid-session not found');
    });

    it('should handle TTS service unavailability', async () => {
      // Set services to null
      languageRouter['deepgramService'] = null;
      languageRouter['czechTTSService'] = null;
      
      const sessionId = 'error-session';
      
      await languageRouter.startSession(sessionId, {
        callId: 'error-call',
        preferredLanguage: 'en'
      });

      const audioBuffer = await languageRouter.synthesizeSpeech(sessionId, "Test text");
      expect(audioBuffer).toBeNull();
    });

    it('should handle empty or malformed text input', async () => {
      const sessionId = 'edge-session';
      
      await languageRouter.startSession(sessionId, {
        callId: 'edge-call',
        preferredLanguage: 'en'
      });

      // Empty text
      const emptyResult = await languageRouter.processText(sessionId, "");
      expect(emptyResult.language).toBe('en');
      expect(emptyResult.confidence).toBeLessThan(0.5);

      // Only numbers
      const numbersResult = await languageRouter.processText(sessionId, "12345");
      expect(numbersResult.language).toBe('en');
      expect(numbersResult.confidence).toBeLessThan(0.5);

      // Special characters
      const symbolsResult = await languageRouter.processText(sessionId, "!@#$%");
      expect(symbolsResult.language).toBe('en');
      expect(symbolsResult.confidence).toBeLessThan(0.5);
    });

    it('should handle service initialization errors', async () => {
      // Create router with invalid configuration
      const invalidRouter = createLanguageRouter({
        deepgramApiKey: '',
        czechTTSConfig: {
          elevenlabsApiKey: '',
          defaultProvider: 'elevenlabs',
          defaultVoice: 'invalid-voice',
          cacheEnabled: false,
          maxCacheSize: 0
        }
      });

      // Should still initialize but with limited functionality
      expect(invalidRouter).toBeDefined();
      
      await invalidRouter.destroy();
    });

    it('should handle concurrent language switches gracefully', async () => {
      const sessionId = 'concurrent-switch';
      
      await languageRouter.startSession(sessionId, {
        callId: 'concurrent-call',
        preferredLanguage: 'en'
      });

      // Multiple concurrent text processing requests
      const concurrentPromises = [
        languageRouter.processText(sessionId, TEST_TEXTS.spanish.medium),
        languageRouter.processText(sessionId, TEST_TEXTS.czech.medium),
        languageRouter.processText(sessionId, TEST_TEXTS.english.medium)
      ];

      const results = await Promise.allSettled(concurrentPromises);
      
      // All should resolve
      expect(results.every(r => r.status === 'fulfilled')).toBe(true);
      
      // Final language should be stable
      const finalLanguage = languageRouter.getSessionLanguage(sessionId);
      expect(['en', 'es', 'cs']).toContain(finalLanguage);
    });

    it('should handle memory limits and resource cleanup', async () => {
      // Create many sessions to test memory handling
      const sessions: string[] = [];
      
      for (let i = 0; i < 100; i++) {
        const sessionId = `memory-session-${i}`;
        sessions.push(sessionId);
        
        await languageRouter.startSession(sessionId, {
          callId: `memory-call-${i}`,
          preferredLanguage: 'en'
        });
      }

      expect(languageRouter.getActiveSessions()).toHaveLength(100);

      // End all sessions
      for (const sessionId of sessions) {
        await languageRouter.endSession(sessionId);
      }

      expect(languageRouter.getActiveSessions()).toHaveLength(0);
    });
  });

  describe('Configuration and Customization', () => {
    it('should allow runtime configuration updates', () => {
      const originalThreshold = languageRouter.getHealthStatus().config.confidenceThreshold;
      
      languageRouter.updateConfig({
        confidenceThreshold: 0.9,
        enableAutoSwitching: false
      });

      const updatedHealth = languageRouter.getHealthStatus();
      expect(updatedHealth.config.confidenceThreshold).toBe(0.9);
      expect(updatedHealth.config.autoSwitchingEnabled).toBe(false);
    });

    it('should respect confidence threshold settings', async () => {
      // Update to high threshold
      languageRouter.updateConfig({ confidenceThreshold: 0.95 });
      
      const sessionId = 'threshold-test';
      
      await languageRouter.startSession(sessionId, {
        callId: 'threshold-call',
        preferredLanguage: 'en'
      });

      // Process text that would normally switch language
      await languageRouter.processText(sessionId, TEST_TEXTS.spanish.short);
      
      // Should not switch due to high threshold
      expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');
    });

    it('should disable auto-switching when configured', async () => {
      languageRouter.updateConfig({ enableAutoSwitching: false });
      
      const sessionId = 'no-auto-switch';
      
      await languageRouter.startSession(sessionId, {
        callId: 'no-auto-call',
        preferredLanguage: 'en'
      });

      // Process Spanish text
      await languageRouter.processText(sessionId, TEST_TEXTS.spanish.long);
      
      // Should remain English
      expect(languageRouter.getSessionLanguage(sessionId)).toBe('en');
    });
  });
});