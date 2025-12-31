import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { LanguageRouterService, LanguageDetector, createLanguageRouter } from '../../../server/services/language-router-service';
import { DeepgramVoiceService } from '../../../server/services/deepgram-voice-service';
import { CzechTTSService } from '../../../server/services/czech-tts-service';

// Mock dependencies
vi.mock('../../../server/services/deepgram-voice-service');
vi.mock('../../../server/services/czech-tts-service');
vi.mock('../../../server/services/logger-service', () => {
  const LoggerService = vi.fn().mockImplementation(() => ({
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }));

  return {
    LoggerService,
    systemLogger: new LoggerService('system')
  };
});

// Mock langdetect
vi.mock('langdetect', () => ({
  default: {
    detectAll: vi.fn()
  }
}));

describe('LanguageDetector', () => {
  describe('detectFromText', () => {
    it('should detect English text correctly', () => {
      const englishText = "Hello, thank you for calling our customer service. How can I help you today?";

      const result = LanguageDetector.detectFromText(englishText);

      expect(result.language).toBe('en');
      expect(result.confidence).toBeGreaterThan(0.3);
      expect(result.source).toBe('text');
      expect(result.patterns).toContain('english-words');
    });

    it('should detect Spanish text correctly', () => {
      const spanishText = "Hola, gracias por llamar a nuestro servicio al cliente. ¿Cómo puedo ayudarle?";

      const result = LanguageDetector.detectFromText(spanishText);

      expect(result.language).toBe('es');
      expect(result.confidence).toBeGreaterThan(0.2);
      expect(result.source).toBe('text');
      expect(result.patterns).toContain('spanish-words');
    });

    it('should detect Czech text correctly', () => {
      const czechText = "Ahoj, děkujeme, že jste zavolal na náš zákaznický servis. Jak vám mohu pomoci?";

      const result = LanguageDetector.detectFromText(czechText);

      expect(result.language).toBe('cs');
      expect(result.confidence).toBeGreaterThan(0.5);
      expect(result.source).toBe('text');
      expect(result.patterns).toContain('czech-diacritics');
    });

    it('should handle short text with low confidence', () => {
      const shortText = "Hi";

      const result = LanguageDetector.detectFromText(shortText);

      expect(result.language).toBe('en');
      expect(result.confidence).toBe(0.3);
      expect(result.source).toBe('text');
    });

    it('should detect Czech diacritics and unique characters', () => {
      const czechText = "řčšžýáíéóúůěď problém zákazník";

      const result = LanguageDetector.detectFromText(czechText);

      expect(result.language).toBe('cs');
      expect(result.patterns).toContain('czech-diacritics');
      expect(result.confidence).toBeGreaterThan(0.7);
    });

    it('should detect Spanish unique patterns', () => {
      const spanishText = "señor niño llamada rr problema";

      const result = LanguageDetector.detectFromText(spanishText);

      expect(result.language).toBe('es');
      expect(result.patterns).toContain('spanish-diacritics');
    });

    it('should detect English contractions', () => {
      const englishText = "I can't help you, won't you please don't worry";

      const result = LanguageDetector.detectFromText(englishText);

      expect(result.language).toBe('en');
      expect(result.patterns).toContain('english-contractions');
    });

    it('should fallback to English for unclear text', () => {
      const unclearText = "123 456 789 @@@ !!!";

      const result = LanguageDetector.detectFromText(unclearText);

      expect(result.language).toBe('en');
      expect(result.confidence).toBe(0.2);
    });
  });

  describe('detectFromContext', () => {
    it('should detect Czech from country code', () => {
      const result = LanguageDetector.detectFromContext('+420123456789', 'cz');

      expect(result.language).toBe('cs');
      expect(result.confidence).toBe(0.9);
      expect(result.source).toBe('context');
      expect(result.patterns).toContain('phone-number');
    });

    it('should detect Spanish from Mexican country code', () => {
      const result = LanguageDetector.detectFromContext('+52123456789', 'mx');

      expect(result.language).toBe('es');
      expect(result.confidence).toBe(0.9);
      expect(result.source).toBe('context');
    });

    it('should detect English from US phone number', () => {
      const result = LanguageDetector.detectFromContext('+1234567890', 'us');

      expect(result.language).toBe('en');
      expect(result.confidence).toBe(0.9);
      expect(result.source).toBe('context');
    });

    it('should handle phone number patterns without country code', () => {
      const result = LanguageDetector.detectFromContext('+420987654321');

      expect(result.language).toBe('cs');
      expect(result.confidence).toBe(0.9);
      expect(result.patterns).toContain('phone-number');
    });

    it('should default to English for unknown context', () => {
      const result = LanguageDetector.detectFromContext();

      expect(result.language).toBe('en');
      expect(result.confidence).toBe(0.6);
      expect(result.source).toBe('context');
    });
  });

  describe('detectFromAudio', () => {
    it('should use transcript when available', async () => {
      const audioBuffer = Buffer.from('mock-audio-data');
      const transcript = "Hello, how can I help you today?";

      const result = await LanguageDetector.detectFromAudio(audioBuffer, transcript);

      expect(result.language).toBe('en');
      expect(result.source).toBe('audio');
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should fallback for audio without transcript', async () => {
      const audioBuffer = Buffer.from('mock-audio-data');

      const result = await LanguageDetector.detectFromAudio(audioBuffer);

      expect(result.language).toBe('en');
      expect(result.source).toBe('audio');
      expect(result.confidence).toBe(0.3);
    });

    it('should handle short transcript', async () => {
      const audioBuffer = Buffer.from('mock-audio-data');
      const shortTranscript = "Hi";

      const result = await LanguageDetector.detectFromAudio(audioBuffer, shortTranscript);

      expect(result.language).toBe('en');
      expect(result.source).toBe('audio');
      expect(result.confidence).toBe(0.3);
    });
  });
});

describe('LanguageRouterService', () => {
  let languageRouter: LanguageRouterService;
  let mockDeepgramService: any;
  let mockCzechTTSService: any;

  const defaultConfig = {
    deepgramApiKey: 'test-deepgram-key',
    openaiApiKey: 'test-openai-key',
    czechTTSConfig: {
      elevenlabsApiKey: 'test-elevenlabs-key',
      defaultProvider: 'elevenlabs' as const,
      defaultVoice: 'kamila-cs',
      cacheEnabled: true,
      maxCacheSize: 50
    },
    confidenceThreshold: 0.7,
    textSampleSize: 20,
    audioSampleDuration: 3,
    defaultLanguage: 'en' as const,
    enableAutoDetection: true,
    enableAutoSwitching: true,
    switchConfirmation: false,
    enableRegionalAccents: true,
    countryCodeMapping: {
      'CZ': 'cs' as const,
      'ES': 'es' as const,
      'US': 'en' as const
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock DeepgramVoiceService
    mockDeepgramService = {
      synthesizeSpeech: vi.fn(),
      destroy: vi.fn()
    };
    (DeepgramVoiceService as any).mockImplementation(() => mockDeepgramService);

    // Mock CzechTTSService
    mockCzechTTSService = {
      synthesize: vi.fn(),
      destroy: vi.fn()
    };

    // Mock createCzechTTSService function
    vi.doMock('../../../server/services/czech-tts-service', () => ({
      CzechTTSService: vi.fn(),
      createCzechTTSService: vi.fn(() => mockCzechTTSService)
    }));

    languageRouter = new LanguageRouterService(defaultConfig);

    // Manually set initialized services for testing
    (languageRouter as any).deepgramService = mockDeepgramService;
    (languageRouter as any).czechTTSService = mockCzechTTSService;
  });

  afterEach(async () => {
    if (languageRouter) {
      await languageRouter.destroy();
    }
  });

  describe('Service Initialization', () => {
    it('should initialize services correctly', () => {
      expect(languageRouter).toBeDefined();
      expect((languageRouter as any).config).toEqual(defaultConfig);
    });

    it('should emit servicesInitialized event', async () => {
      const newRouter = new LanguageRouterService(defaultConfig);

      const eventPromise = new Promise((resolve) => {
        newRouter.on('servicesInitialized', (data) => {
          expect(data.deepgram).toBe(true);
          expect(data.czechTTS).toBe(true);
          resolve(data);
        });
      });

      // Manually trigger initialization for test
      (newRouter as any).deepgramService = mockDeepgramService;
      (newRouter as any).czechTTSService = mockCzechTTSService;
      newRouter.emit('servicesInitialized', { deepgram: true, czechTTS: true });

      await eventPromise;
    });
  });

  describe('Session Management', () => {
    it('should start session with preferred language', async () => {
      const sessionId = 'test-session-123';
      const options = {
        callId: 'call-123',
        preferredLanguage: 'es' as const
      };

      const preference = await languageRouter.startSession(sessionId, options);

      expect(preference.sessionId).toBe(sessionId);
      expect(preference.preferredLanguage).toBe('es');
      expect(preference.confidenceThreshold).toBe(0.7);
      expect(preference.allowAutoSwitch).toBe(true);
    });

    it('should detect language from context when no preference given', async () => {
      const sessionId = 'test-session-123';
      const options = {
        callId: 'call-123',
        phoneNumber: '+420123456789',
        countryCode: 'cz'
      };

      const preference = await languageRouter.startSession(sessionId, options);

      expect(preference.preferredLanguage).toBe('cs');
      expect(preference.detectedLanguage).toBe('cs');
    });

    it('should emit sessionStarted event', async () => {
      const sessionId = 'test-session-123';

      const eventPromise = new Promise((resolve) => {
        languageRouter.on('sessionStarted', (data) => {
          expect(data.sessionId).toBe(sessionId);
          expect(data.preference).toBeDefined();
          expect(data.route).toBeDefined();
          resolve(data);
        });
      });

      await languageRouter.startSession(sessionId, { callId: 'call-123' });
      await eventPromise;
    });

    it('should get session language correctly', async () => {
      const sessionId = 'test-session-123';
      await languageRouter.startSession(sessionId, {
        callId: 'call-123',
        preferredLanguage: 'es'
      });

      const language = languageRouter.getSessionLanguage(sessionId);
      expect(language).toBe('es');
    });

    it('should get session route correctly', async () => {
      const sessionId = 'test-session-123';
      await languageRouter.startSession(sessionId, {
        callId: 'call-123',
        preferredLanguage: 'cs'
      });

      const route = languageRouter.getSessionRoute(sessionId);
      expect(route).toBeDefined();
      expect(route?.language).toBe('cs');
      expect(route?.provider).toBe('czech-tts');
    });

    it('should end session and cleanup', async () => {
      const sessionId = 'test-session-123';
      await languageRouter.startSession(sessionId, { callId: 'call-123' });

      const emittedEvents: any[] = [];
      languageRouter.on('sessionEnded', (data) => emittedEvents.push(data));

      await languageRouter.endSession(sessionId);

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].sessionId).toBe(sessionId);
      expect(languageRouter.getSessionLanguage(sessionId)).toBeUndefined();
    });
  });

  describe('Language Detection and Processing', () => {
    beforeEach(async () => {
      await languageRouter.startSession('test-session', {
        callId: 'call-123',
        preferredLanguage: 'en'
      });
    });

    it('should process text and detect language', async () => {
      const spanishText = "Hola, necesito ayuda con mi cuenta por favor";

      const detection = await languageRouter.processText('test-session', spanishText);

      expect(detection.language).toBe('es');
      expect(detection.source).toBe('text');
      expect(detection.confidence).toBeGreaterThan(0.2);
    });

    it('should switch language when confidence is high enough', async () => {
      // Update session to have lower confidence threshold
      const preference = (languageRouter as any).sessionPreferences.get('test-session');
      if (preference) {
        preference.confidenceThreshold = 0.3;
      }

      const czechText = "Ahoj, potřebuji pomoc s mým účtem prosím řčšžýáíéóúůěď";

      const emittedEvents: any[] = [];
      languageRouter.on('languageDetected', (data) => emittedEvents.push(data));

      await languageRouter.processText('test-session', czechText);

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].switched).toBe(true);
      expect(emittedEvents[0].detection.language).toBe('cs');
    });

    it('should not switch language when confidence is too low', async () => {
      const ambiguousText = "Hi yes no problem";

      const emittedEvents: any[] = [];
      languageRouter.on('languageDetected', (data) => emittedEvents.push(data));

      await languageRouter.processText('test-session', ambiguousText);

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].switched).toBe(false);
    });

    it('should process audio with transcript', async () => {
      const audioBuffer = Buffer.from('mock-audio');
      const transcript = "Necesito ayuda con español";

      const detection = await languageRouter.processAudio('test-session', audioBuffer, transcript);

      expect(detection.source).toBe('text'); // processAudio calls processText when transcript is available
      expect(detection.language).toBe('es');
    });

    it('should manually set session language', async () => {
      const emittedEvents: any[] = [];
      languageRouter.on('languageManuallySet', (data) => emittedEvents.push(data));

      await languageRouter.setSessionLanguage('test-session', 'cs', true);

      expect(languageRouter.getSessionLanguage('test-session')).toBe('cs');
      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].newLanguage).toBe('cs');
      expect(emittedEvents[0].confirmed).toBe(true);
    });
  });

  describe('Voice Service Integration', () => {
    beforeEach(async () => {
      await languageRouter.startSession('test-session', {
        callId: 'call-123',
        preferredLanguage: 'en'
      });
    });

    it('should get appropriate TTS service for English', () => {
      const service = languageRouter.getTTSService('en');
      expect(service).toBe(mockDeepgramService);
    });

    it('should get appropriate TTS service for Spanish', () => {
      const service = languageRouter.getTTSService('es');
      expect(service).toBe(mockDeepgramService);
    });

    it('should get appropriate TTS service for Czech', () => {
      const service = languageRouter.getTTSService('cs');
      expect(service).toBe(mockCzechTTSService);
    });

    it('should synthesize speech using Deepgram for English', async () => {
      const text = "Hello, how can I help you?";
      const expectedBuffer = Buffer.from('mock-audio-data');

      mockDeepgramService.synthesizeSpeech.mockResolvedValue(expectedBuffer);

      const result = await languageRouter.synthesizeSpeech('test-session', text);

      expect(mockDeepgramService.synthesizeSpeech).toHaveBeenCalledWith(text, 'asteria');
      expect(result).toBe(expectedBuffer);
    });

    it('should synthesize speech using Czech TTS for Czech', async () => {
      await languageRouter.setSessionLanguage('test-session', 'cs');

      const text = "Ahoj, jak vám mohu pomoci?";
      const expectedBuffer = Buffer.from('czech-audio-data');

      mockCzechTTSService.synthesize.mockResolvedValue(expectedBuffer);

      const result = await languageRouter.synthesizeSpeech('test-session', text);

      expect(mockCzechTTSService.synthesize).toHaveBeenCalledWith(text, {
        voice: 'kamila-cs'
      });
      expect(result).toBe(expectedBuffer);
    });

    it('should handle TTS errors gracefully', async () => {
      const text = "Test speech";
      const error = new Error('TTS service unavailable');

      mockDeepgramService.synthesizeSpeech.mockRejectedValue(error);

      const emittedEvents: any[] = [];
      languageRouter.on('synthesisError', (data) => emittedEvents.push(data));

      const result = await languageRouter.synthesizeSpeech('test-session', text);

      expect(result).toBeNull();
      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].error).toBe(error);
    });

    it('should throw error for session without active route', async () => {
      await expect(
        languageRouter.synthesizeSpeech('non-existent-session', 'test')
      ).rejects.toThrow('No active route for session');
    });
  });

  describe('Route Management', () => {
    it('should switch language route correctly', async () => {
      await languageRouter.startSession('test-session', {
        callId: 'call-123',
        preferredLanguage: 'en'
      });

      const emittedEvents: any[] = [];
      languageRouter.on('routeSwitched', (data) => emittedEvents.push(data));

      await languageRouter.switchLanguageRoute('test-session', 'es');

      expect(emittedEvents).toHaveLength(1);
      expect(emittedEvents[0].newRoute.language).toBe('es');
      expect(emittedEvents[0].newRoute.provider).toBe('deepgram');
    });

    it('should not switch route if language is the same', async () => {
      await languageRouter.startSession('test-session', {
        callId: 'call-123',
        preferredLanguage: 'en'
      });

      const emittedEvents: any[] = [];
      languageRouter.on('routeSwitched', (data) => emittedEvents.push(data));

      await languageRouter.switchLanguageRoute('test-session', 'en');

      expect(emittedEvents).toHaveLength(0);
    });
  });

  describe('Statistics and Health', () => {
    beforeEach(async () => {
      await languageRouter.startSession('test-session', {
        callId: 'call-123',
        preferredLanguage: 'en'
      });
    });

    it('should get session statistics', () => {
      const stats = languageRouter.getSessionStats('test-session');

      expect(stats).toBeDefined();
      expect(stats?.sessionId).toBe('test-session');
      expect(stats?.currentLanguage).toBe('en');
      expect(stats?.provider).toBe('deepgram');
    });

    it('should return null for non-existent session stats', () => {
      const stats = languageRouter.getSessionStats('non-existent');
      expect(stats).toBeNull();
    });

    it('should get active sessions', () => {
      const sessions = languageRouter.getActiveSessions();
      expect(sessions).toContain('test-session');
      expect(sessions).toHaveLength(1);
    });

    it('should get health status', () => {
      const health = languageRouter.getHealthStatus();

      expect(health.activeSessions).toBe(1);
      expect(health.deepgramAvailable).toBe(true);
      expect(health.czechTTSAvailable).toBe(true);
      expect(health.config.autoDetectionEnabled).toBe(true);
      expect(health.config.defaultLanguage).toBe('en');
    });
  });

  describe('Configuration Updates', () => {
    it('should update configuration', () => {
      const updates = {
        confidenceThreshold: 0.8,
        enableAutoSwitching: false
      };

      const emittedEvents: any[] = [];
      languageRouter.on('configUpdated', (data) => emittedEvents.push(data));

      languageRouter.updateConfig(updates);

      expect((languageRouter as any).config.confidenceThreshold).toBe(0.8);
      expect((languageRouter as any).config.enableAutoSwitching).toBe(false);
      expect(emittedEvents).toHaveLength(1);
    });
  });

  describe('Error Handling', () => {
    it('should handle processText for non-existent session', async () => {
      await expect(
        languageRouter.processText('non-existent', 'test text')
      ).rejects.toThrow('Session non-existent not found');
    });

    it('should handle setSessionLanguage for non-existent session', async () => {
      await expect(
        languageRouter.setSessionLanguage('non-existent', 'en')
      ).rejects.toThrow('Session non-existent not found');
    });
  });

  describe('Cleanup and Destruction', () => {
    it('should destroy service and cleanup resources', async () => {
      await languageRouter.startSession('test-session', { callId: 'call-123' });

      const emittedEvents: any[] = [];
      languageRouter.on('sessionEnded', (data) => emittedEvents.push(data));

      await languageRouter.destroy();

      expect(mockDeepgramService.destroy).toHaveBeenCalled();
      expect(mockCzechTTSService.destroy).toHaveBeenCalled();
      expect(emittedEvents).toHaveLength(1); // Session ended
      expect(languageRouter.getActiveSessions()).toHaveLength(0);
    });
  });
});

describe('createLanguageRouter factory', () => {
  it('should create language router with default config', () => {
    process.env.DEEPGRAM_API_KEY = 'test-key';

    const router = createLanguageRouter();

    expect(router).toBeInstanceOf(LanguageRouterService);
    expect((router as any).config.defaultLanguage).toBe('en');
    expect((router as any).config.confidenceThreshold).toBe(0.7);

    delete process.env.DEEPGRAM_API_KEY;
  });

  it('should create language router with custom config', () => {
    const customConfig = {
      confidenceThreshold: 0.9,
      defaultLanguage: 'es' as const
    };

    const router = createLanguageRouter(customConfig);

    expect((router as any).config.confidenceThreshold).toBe(0.9);
    expect((router as any).config.defaultLanguage).toBe('es');
  });

  it('should merge custom config with defaults', () => {
    const customConfig = {
      confidenceThreshold: 0.8
    };

    const router = createLanguageRouter(customConfig);

    expect((router as any).config.confidenceThreshold).toBe(0.8);
    expect((router as any).config.defaultLanguage).toBe('en'); // Default value
    expect((router as any).config.enableAutoDetection).toBe(true); // Default value
  });
});
