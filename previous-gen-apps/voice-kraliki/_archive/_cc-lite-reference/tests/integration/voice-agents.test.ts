/**
 * Voice Agent Tests for Voice by Kraliki
 * Tests language detection accuracy, STT/TTS pipeline, and multi-language switching
 */
import { test, expect, describe, beforeAll, afterAll } from 'vitest';
import { VoiceAgent } from '../../server/services/voice-agent';
import { LanguageDetector } from '../../server/services/language-detector';
import { STTService } from '../../server/services/stt-service';
import { TTSService } from '../../server/services/tts-service';
import { AudioBuffer } from '../../server/utils/audio-utils';

describe('Voice Agent Integration Tests', () => {
  let voiceAgent: VoiceAgent;
  let languageDetector: LanguageDetector;
  let sttService: STTService;
  let ttsService: TTSService;

  beforeAll(async () => {
    voiceAgent = new VoiceAgent({
      provider: 'deepgram',
      apiKey: process.env.DEEPGRAM_API_KEY || 'mock_key',
      model: 'nova-2'
    });

    languageDetector = new LanguageDetector({
      confidence_threshold: 0.8
    });

    sttService = new STTService({
      provider: 'deepgram',
      apiKey: process.env.DEEPGRAM_API_KEY || 'mock_key'
    });

    ttsService = new TTSService({
      provider: 'deepgram',
      apiKey: process.env.DEEPGRAM_API_KEY || 'mock_key'
    });

    await voiceAgent.initialize();
  });

  afterAll(async () => {
    await voiceAgent.cleanup();
  });

  describe('Language Detection Accuracy', () => {
    test('should detect English with high confidence', async () => {
      const englishTexts = [
        "Hello, how can I help you today?",
        "I would like to speak with customer service please.",
        "Can you transfer me to technical support?",
        "What are your business hours?"
      ];

      for (const text of englishTexts) {
        const result = await languageDetector.detectLanguage(text);

        expect(result.language).toBe('en');
        expect(result.confidence).toBeGreaterThan(0.8);
        expect(result.alternatives).toBeInstanceOf(Array);
      }
    });

    test('should detect Spanish with high confidence', async () => {
      const spanishTexts = [
        "Hola, ¿cómo puedo ayudarle hoy?",
        "Quisiera hablar con servicio al cliente, por favor.",
        "¿Puede transferirme a soporte técnico?",
        "¿Cuáles son sus horarios de atención?"
      ];

      for (const text of spanishTexts) {
        const result = await languageDetector.detectLanguage(text);

        expect(result.language).toBe('es');
        expect(result.confidence).toBeGreaterThan(0.8);
      }
    });

    test('should detect French with high confidence', async () => {
      const frenchTexts = [
        "Bonjour, comment puis-je vous aider aujourd'hui?",
        "Je voudrais parler au service client s'il vous plaît.",
        "Pouvez-vous me transférer au support technique?",
        "Quels sont vos horaires d'ouverture?"
      ];

      for (const text of frenchTexts) {
        const result = await languageDetector.detectLanguage(text);

        expect(result.language).toBe('fr');
        expect(result.confidence).toBeGreaterThan(0.8);
      }
    });

    test('should handle mixed language scenarios', async () => {
      const mixedTexts = [
        "Hello, je voudrais parler français s'il vous plaît.", // English + French
        "Hola, I need help with my account.", // Spanish + English
        "Bonjour, ¿habla usted español?" // French + Spanish
      ];

      for (const text of mixedTexts) {
        const result = await languageDetector.detectLanguage(text);

        expect(result.language).toMatch(/^(en|es|fr)$/);
        expect(result.confidence).toBeGreaterThan(0.5);
        expect(result.mixed_languages).toBe(true);
        expect(result.detected_languages?.length).toBeGreaterThan(1);
      }
    });

    test('should provide language alternatives for ambiguous content', async () => {
      const ambiguousTexts = [
        "OK", // Very short
        "123-456-7890", // Numbers
        "email@domain.com", // Email
        "..." // Punctuation only
      ];

      for (const text of ambiguousTexts) {
        const result = await languageDetector.detectLanguage(text);

        expect(result.confidence).toBeLessThan(0.5);
        expect(result.alternatives.length).toBeGreaterThan(0);
      }
    });
  });

  describe('STT/TTS Pipeline Tests', () => {
    test('should process English audio through complete pipeline', async () => {
      // Mock audio data for English speech
      const englishAudioBuffer = createMockAudioBuffer('en', 'Hello, this is a test message.');

      // STT: Audio to text
      const transcriptionResult = await sttService.transcribe(englishAudioBuffer, {
        language: 'en',
        model: 'nova-2',
        detect_language: false
      });

      expect(transcriptionResult.text).toBeDefined();
      expect(transcriptionResult.confidence).toBeGreaterThan(0.7);
      expect(transcriptionResult.language).toBe('en');

      // TTS: Text back to audio
      const synthesisResult = await ttsService.synthesize(transcriptionResult.text, {
        language: 'en',
        voice: 'aura-asteria-en',
        model: 'aura'
      });

      expect(synthesisResult.audio_data).toBeDefined();
      expect(synthesisResult.content_type).toBe('audio/wav');
      expect(synthesisResult.duration).toBeGreaterThan(0);
    });

    test('should handle Spanish STT/TTS pipeline', async () => {
      const spanishAudioBuffer = createMockAudioBuffer('es', 'Hola, este es un mensaje de prueba.');

      const transcriptionResult = await sttService.transcribe(spanishAudioBuffer, {
        language: 'es',
        model: 'nova-2',
        detect_language: false
      });

      expect(transcriptionResult.text).toBeDefined();
      expect(transcriptionResult.confidence).toBeGreaterThan(0.7);
      expect(transcriptionResult.language).toBe('es');

      const synthesisResult = await ttsService.synthesize(transcriptionResult.text, {
        language: 'es',
        voice: 'aura-luna-es',
        model: 'aura'
      });

      expect(synthesisResult.audio_data).toBeDefined();
      expect(synthesisResult.content_type).toBe('audio/wav');
    });

    test('should maintain audio quality through pipeline', async () => {
      const highQualityAudio = createMockAudioBuffer('en', 'Testing audio quality preservation.', {
        sampleRate: 44100,
        bitDepth: 16,
        channels: 1
      });

      const transcriptionResult = await sttService.transcribe(highQualityAudio, {
        language: 'en',
        model: 'nova-2',
        quality: 'high'
      });

      expect(transcriptionResult.confidence).toBeGreaterThan(0.85);

      const synthesisResult = await ttsService.synthesize(transcriptionResult.text, {
        language: 'en',
        voice: 'aura-asteria-en',
        quality: 'high',
        sample_rate: 44100
      });

      expect(synthesisResult.sample_rate).toBe(44100);
    });

    test('should handle audio processing errors gracefully', async () => {
      // Test with corrupted audio data
      const corruptedAudio = Buffer.from('not_audio_data');

      const transcriptionResult = await sttService.transcribe(corruptedAudio, {
        language: 'en',
        model: 'nova-2'
      });

      expect(transcriptionResult.error).toBeDefined();
      expect(transcriptionResult.error_type).toBe('audio_processing_error');

      // Test with empty audio
      const emptyAudio = Buffer.alloc(0);
      const emptyResult = await sttService.transcribe(emptyAudio, {
        language: 'en',
        model: 'nova-2'
      });

      expect(emptyResult.error).toBeDefined();
      expect(emptyResult.error_type).toBe('empty_audio_error');
    });
  });

  describe('Multi-language Switching Tests', () => {
    test('should switch between languages seamlessly', async () => {
      const callSession = await voiceAgent.createSession({
        sessionId: 'test_multilang_001',
        defaultLanguage: 'en'
      });

      // Start with English
      let result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('en', 'Hello, I need help with my account.')
      );
      expect(result.detected_language).toBe('en');
      expect(result.response_language).toBe('en');

      // Switch to Spanish
      result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('es', 'Prefiero continuar en español, por favor.')
      );
      expect(result.detected_language).toBe('es');
      expect(result.response_language).toBe('es');
      expect(result.language_switched).toBe(true);

      // Verify session language was updated
      expect(callSession.current_language).toBe('es');

      // Continue in Spanish
      result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('es', '¿Puede ayudarme con mi factura?')
      );
      expect(result.detected_language).toBe('es');
      expect(result.response_language).toBe('es');
      expect(result.language_switched).toBe(false);
    });

    test('should handle rapid language switches', async () => {
      const callSession = await voiceAgent.createSession({
        sessionId: 'test_rapid_switch_001',
        defaultLanguage: 'en',
        language_detection: true
      });

      const languages = [
        { lang: 'en', text: 'Hello there' },
        { lang: 'es', text: 'Hola' },
        { lang: 'fr', text: 'Bonjour' },
        { lang: 'en', text: 'Back to English' },
        { lang: 'es', text: 'Y otra vez español' }
      ];

      const results = [];
      for (const { lang, text } of languages) {
        const result = await voiceAgent.processAudio(callSession,
          createMockAudioBuffer(lang, text)
        );
        results.push(result);
      }

      // Verify each language was detected correctly
      expect(results[0].detected_language).toBe('en');
      expect(results[1].detected_language).toBe('es');
      expect(results[2].detected_language).toBe('fr');
      expect(results[3].detected_language).toBe('en');
      expect(results[4].detected_language).toBe('es');

      // Verify language switches were tracked
      expect(results[1].language_switched).toBe(true);
      expect(results[2].language_switched).toBe(true);
      expect(results[3].language_switched).toBe(true);
      expect(results[4].language_switched).toBe(true);
    });

    test('should maintain conversation context across language switches', async () => {
      const callSession = await voiceAgent.createSession({
        sessionId: 'test_context_preserve_001',
        defaultLanguage: 'en',
        context_preservation: true
      });

      // Establish context in English
      let result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('en', 'My account number is 123456789 and I have a billing issue.')
      );
      expect(result.extracted_entities.account_number).toBe('123456789');

      // Switch to Spanish but reference previous context
      result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('es', 'Sí, es sobre esa cuenta que mencioné.')
      );
      expect(result.detected_language).toBe('es');
      expect(result.context.account_number).toBe('123456789');
      expect(result.context_preserved).toBe(true);
    });

    test('should provide appropriate fallback for unsupported languages', async () => {
      const callSession = await voiceAgent.createSession({
        sessionId: 'test_unsupported_lang_001',
        defaultLanguage: 'en',
        fallback_language: 'en'
      });

      // Test with potentially unsupported language
      const result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('zh', '你好，我需要帮助') // Chinese
      );

      expect(result.detected_language).toBe('zh');
      expect(result.supported).toBe(false);
      expect(result.fallback_used).toBe(true);
      expect(result.response_language).toBe('en');
    });
  });

  describe('Voice Agent Performance Tests', () => {
    test('should process audio within acceptable latency limits', async () => {
      const callSession = await voiceAgent.createSession({
        sessionId: 'test_performance_001',
        defaultLanguage: 'en'
      });

      const audioBuffer = createMockAudioBuffer('en', 'This is a performance test message.');

      const startTime = Date.now();
      const result = await voiceAgent.processAudio(callSession, audioBuffer);
      const endTime = Date.now();

      const processingTime = endTime - startTime;

      // Should process within 2 seconds for typical audio
      expect(processingTime).toBeLessThan(2000);
      expect(result.processing_time_ms).toBeLessThan(2000);
      expect(result.text).toBeDefined();
    });

    test('should handle concurrent audio processing', async () => {
      const concurrentSessions = 5;
      const sessions = [];

      // Create multiple sessions
      for (let i = 0; i < concurrentSessions; i++) {
        const session = await voiceAgent.createSession({
          sessionId: `concurrent_test_${i}`,
          defaultLanguage: 'en'
        });
        sessions.push(session);
      }

      // Process audio concurrently
      const audioBuffer = createMockAudioBuffer('en', 'Concurrent processing test.');
      const promises = sessions.map(session =>
        voiceAgent.processAudio(session, audioBuffer)
      );

      const results = await Promise.all(promises);

      // All should succeed
      results.forEach((result, index) => {
        expect(result.error).toBeUndefined();
        expect(result.session_id).toBe(`concurrent_test_${index}`);
        expect(result.text).toBeDefined();
      });
    });
  });

  describe('Voice Agent Error Handling', () => {
    test('should handle STT service failures gracefully', async () => {
      // Mock STT service failure
      const originalTranscribe = sttService.transcribe;
      sttService.transcribe = async () => {
        throw new Error('STT service unavailable');
      };

      const callSession = await voiceAgent.createSession({
        sessionId: 'test_stt_failure_001',
        defaultLanguage: 'en'
      });

      const result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('en', 'This should fail.')
      );

      expect(result.error).toBeDefined();
      expect(result.error_type).toBe('stt_service_error');
      expect(result.fallback_response).toBeDefined();

      // Restore original function
      sttService.transcribe = originalTranscribe;
    });

    test('should handle TTS service failures gracefully', async () => {
      // Mock TTS service failure
      const originalSynthesize = ttsService.synthesize;
      ttsService.synthesize = async () => {
        throw new Error('TTS service unavailable');
      };

      const callSession = await voiceAgent.createSession({
        sessionId: 'test_tts_failure_001',
        defaultLanguage: 'en'
      });

      const result = await voiceAgent.processAudio(callSession,
        createMockAudioBuffer('en', 'This should partially succeed.')
      );

      expect(result.text).toBeDefined(); // STT should work
      expect(result.audio_response).toBeUndefined(); // TTS should fail
      expect(result.tts_error).toBeDefined();

      // Restore original function
      ttsService.synthesize = originalSynthesize;
    });
  });
});

// Helper functions
function createMockAudioBuffer(language: string, text: string, options?: {
  sampleRate?: number;
  bitDepth?: number;
  channels?: number;
}): Buffer {
  // Create mock audio buffer based on text and language
  // This would normally be actual audio data
  const config = {
    sampleRate: options?.sampleRate || 16000,
    bitDepth: options?.bitDepth || 16,
    channels: options?.channels || 1
  };

  // Generate mock audio data based on text length and language
  const durationMs = text.length * 100; // ~100ms per character
  const sampleCount = Math.floor((config.sampleRate * durationMs) / 1000);
  const buffer = Buffer.alloc(sampleCount * 2); // 16-bit samples

  // Add metadata for testing
  (buffer as any).metadata = {
    language,
    text,
    duration: durationMs,
    sampleRate: config.sampleRate,
    channels: config.channels
  };

  return buffer;
}