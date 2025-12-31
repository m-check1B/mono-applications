import { test, expect } from '@playwright/test';
import { VoiceManager } from '../../server/voice/voice-manager';
import { TwilioProvider } from '../../server/voice/providers/twilio-provider';
import { TelnyxProvider } from '../../server/voice/providers/telnyx-provider';
import { DeepgramPipeline } from '../../server/voice/processors/deepgram-pipeline';
import { GeminiMultimodal } from '../../server/voice/processors/gemini-multimodal';

test.describe('Voice System Integration Tests', () => {
  let voiceManager: VoiceManager;

  test.beforeAll(async () => {
    // Initialize voice manager with test configuration
    voiceManager = VoiceManager.getInstance();
    await voiceManager.initialize({
      defaultTelephonyProvider: 'twilio',
      defaultVoiceProcessor: 'deepgram-pipeline',
      providers: {
        twilio: {
          accountSid: process.env.TWILIO_ACCOUNT_SID || 'test_sid',
          authToken: process.env.TWILIO_AUTH_TOKEN || 'test_token',
          phoneNumber: process.env.TWILIO_PHONE_NUMBER || '+1234567890'
        },
        telnyx: {
          apiKey: process.env.TELNYX_API_KEY || 'test_key',
          connectionId: process.env.TELNYX_CONNECTION_ID || 'test_connection'
        }
      },
      processors: {
        'deepgram-pipeline': {
          deepgramApiKey: process.env.DEEPGRAM_API_KEY || 'test_key',
          openrouterApiKey: process.env.OPENROUTER_API_KEY || 'test_key'
        },
        'gemini-multimodal': {
          apiKey: process.env.GEMINI_API_KEY || 'test_key'
        }
      }
    });
  });

  test.describe('Telephony Providers', () => {
    test('should initialize Twilio provider', async () => {
      const provider = voiceManager.getTelephonyProvider('twilio');
      expect(provider).toBeDefined();
      expect(provider.name).toBe('twilio');
    });

    test('should initialize Telnyx provider', async () => {
      const provider = voiceManager.getTelephonyProvider('telnyx');
      expect(provider).toBeDefined();
      expect(provider.name).toBe('telnyx');
    });

    test('should switch between providers', async () => {
      await voiceManager.setDefaultTelephonyProvider('telnyx');
      expect(voiceManager.getDefaultTelephonyProvider().name).toBe('telnyx');

      await voiceManager.setDefaultTelephonyProvider('twilio');
      expect(voiceManager.getDefaultTelephonyProvider().name).toBe('twilio');
    });
  });

  test.describe('Voice Processors', () => {
    test('should initialize Deepgram pipeline', async () => {
      const processor = voiceManager.getVoiceProcessor('deepgram-pipeline');
      expect(processor).toBeDefined();
      expect(processor.name).toBe('deepgram-pipeline');
    });

    test('should initialize Gemini multimodal', async () => {
      const processor = voiceManager.getVoiceProcessor('gemini-multimodal');
      expect(processor).toBeDefined();
      expect(processor.name).toBe('gemini-multimodal');
    });

    test('should switch between processors', async () => {
      await voiceManager.setDefaultVoiceProcessor('gemini-multimodal');
      expect(voiceManager.getDefaultVoiceProcessor().name).toBe('gemini-multimodal');

      await voiceManager.setDefaultVoiceProcessor('deepgram-pipeline');
      expect(voiceManager.getDefaultVoiceProcessor().name).toBe('deepgram-pipeline');
    });
  });

  test.describe('Call Session Management', () => {
    test('should create call session with Twilio and Deepgram', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'twilio',
        voiceProcessor: 'deepgram-pipeline',
        metadata: {
          campaignId: 'test-campaign',
          leadId: 'test-lead'
        }
      });

      expect(sessionId).toBeDefined();

      const session = voiceManager.getCallSession(sessionId);
      expect(session).toBeDefined();
      expect(session.telephonyProvider).toBe('twilio');
      expect(session.voiceProcessor).toBe('deepgram-pipeline');
    });

    test('should create call session with Telnyx and Gemini', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'telnyx',
        voiceProcessor: 'gemini-multimodal',
        metadata: {
          campaignId: 'test-campaign-2',
          leadId: 'test-lead-2'
        }
      });

      expect(sessionId).toBeDefined();

      const session = voiceManager.getCallSession(sessionId);
      expect(session).toBeDefined();
      expect(session.telephonyProvider).toBe('telnyx');
      expect(session.voiceProcessor).toBe('gemini-multimodal');
    });

    test('should end call session', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'twilio',
        voiceProcessor: 'deepgram-pipeline'
      });

      await voiceManager.endCallSession(sessionId);

      const session = voiceManager.getCallSession(sessionId);
      expect(session.status).toBe('ended');
    });
  });

  test.describe('Audio Processing', () => {
    test('should convert μ-law to PCM', async () => {
      const { convertMuLawToPCM } = await import('../../server/voice/utils/audio-converter');

      // Create test μ-law buffer
      const muLawBuffer = Buffer.from([0xFF, 0x7F, 0x00, 0x80]);
      const pcmBuffer = convertMuLawToPCM(muLawBuffer);

      expect(pcmBuffer).toBeDefined();
      expect(pcmBuffer.length).toBe(muLawBuffer.length * 2); // PCM is 16-bit
    });

    test('should handle audio streaming', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'twilio',
        voiceProcessor: 'deepgram-pipeline'
      });

      const session = voiceManager.getCallSession(sessionId);

      // Simulate audio chunk
      const audioChunk = Buffer.from([0xFF, 0x7F, 0x00, 0x80]);
      await session.processAudioChunk(audioChunk);

      expect(session.audioBufferSize).toBeGreaterThan(0);
    });
  });

  test.describe('Provider Hot-Swapping', () => {
    test('should hot-swap telephony provider during session', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'twilio',
        voiceProcessor: 'deepgram-pipeline'
      });

      // Hot-swap to Telnyx
      await voiceManager.hotSwapTelephonyProvider(sessionId, 'telnyx');

      const session = voiceManager.getCallSession(sessionId);
      expect(session.telephonyProvider).toBe('telnyx');
    });

    test('should hot-swap voice processor during session', async () => {
      const sessionId = await voiceManager.createCallSession({
        telephonyProvider: 'twilio',
        voiceProcessor: 'deepgram-pipeline'
      });

      // Hot-swap to Gemini
      await voiceManager.hotSwapVoiceProcessor(sessionId, 'gemini-multimodal');

      const session = voiceManager.getCallSession(sessionId);
      expect(session.voiceProcessor).toBe('gemini-multimodal');
    });
  });

  test.describe('Error Handling', () => {
    test('should handle provider initialization failure gracefully', async () => {
      try {
        await voiceManager.initialize({
          defaultTelephonyProvider: 'invalid-provider',
          defaultVoiceProcessor: 'deepgram-pipeline'
        });
      } catch (error) {
        expect(error.message).toContain('provider');
      }
    });

    test('should handle session creation failure gracefully', async () => {
      try {
        await voiceManager.createCallSession({
          telephonyProvider: 'invalid',
          voiceProcessor: 'invalid'
        });
      } catch (error) {
        expect(error.message).toBeDefined();
      }
    });
  });

  test.afterAll(async () => {
    // Clean up
    await voiceManager.shutdown();
  });
});