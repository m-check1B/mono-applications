import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { DeepgramVoiceService } from '../server/services/deepgram-voice-service';
import { mockWebSocket, waitFor } from './setup';

describe('Deepgram Voice Integration', () => {
  let voiceService: DeepgramVoiceService;
  
  beforeEach(() => {
    voiceService = new DeepgramVoiceService({
      apiKey: 'test-api-key',
      enableTranscription: true,
      enableTextToSpeech: true,
      enableVoiceActivity: true,
      enableSpeakerDiarization: true,
      callCenterMode: true
    });
  });

  afterEach(async () => {
    await voiceService.destroy();
  });

  describe('Speech-to-Text', () => {
    it('should start transcription for a call', async () => {
      const callId = 'test-call-123';
      const sessionId = 'session-456';
      
      const startPromise = voiceService.startTranscription(callId, sessionId);
      
      // Mock the connection
      voiceService.emit('transcriptionStarted', { callId, sessionId });
      
      await expect(startPromise).resolves.toBeUndefined();
      
      const transcription = voiceService.getTranscription(callId);
      expect(transcription).toBeDefined();
      expect(transcription?.callId).toBe(callId);
      expect(transcription?.sessionId).toBe(sessionId);
    });

    it('should process audio stream', async () => {
      const callId = 'test-call-123';
      const sessionId = 'session-456';
      const audioBuffer = Buffer.from('mock-audio-data');
      
      await voiceService.startTranscription(callId, sessionId);
      
      // Should not throw
      expect(() => {
        voiceService.processAudioStream(callId, audioBuffer);
      }).not.toThrow();
    });

    it('should handle transcription results', async () => {
      const callId = 'test-call-123';
      const sessionId = 'session-456';
      
      let transcriptReceived = false;
      
      voiceService.on('transcript', (data) => {
        expect(data.callId).toBe(callId);
        expect(data.result).toBeDefined();
        transcriptReceived = true;
      });
      
      await voiceService.startTranscription(callId, sessionId);
      
      // Simulate transcript event
      voiceService.emit('transcript', {
        callId,
        sessionId,
        result: {
          transcript: 'Hello, how can I help you?',
          confidence: 0.95,
          isFinal: true,
          timestamp: new Date()
        },
        speaker: 'Speaker 1'
      });
      
      expect(transcriptReceived).toBe(true);
    });

    it('should detect keywords for escalation', async () => {
      const callId = 'test-call-123';
      let escalationDetected = false;
      
      voiceService.on('escalationDetected', (data) => {
        expect(data.callId).toBe(callId);
        escalationDetected = true;
      });
      
      await voiceService.startTranscription(callId, 'session-456');
      
      // Simulate transcript with escalation keyword
      voiceService.emit('finalTranscript', {
        callId,
        sessionId: 'session-456',
        result: {
          transcript: 'I want to speak to your supervisor',
          confidence: 0.95,
          isFinal: true,
          timestamp: new Date()
        }
      });
      
      await waitFor(100);
      expect(escalationDetected).toBe(true);
    });

    it('should handle speaker diarization', async () => {
      const callId = 'test-call-123';
      await voiceService.startTranscription(callId, 'session-456');
      
      const transcription = voiceService.getTranscription(callId);
      
      // Simulate multiple speakers
      voiceService.emit('transcript', {
        callId,
        sessionId: 'session-456',
        result: {
          transcript: 'Hello',
          confidence: 0.95,
          speaker: 0,
          isFinal: false,
          timestamp: new Date()
        }
      });
      
      voiceService.emit('transcript', {
        callId,
        sessionId: 'session-456',
        result: {
          transcript: 'Hi there',
          confidence: 0.93,
          speaker: 1,
          isFinal: false,
          timestamp: new Date()
        }
      });
      
      expect(transcription?.speakers.size).toBe(2);
      expect(transcription?.speakers.get(0)).toBe('Speaker 1');
      expect(transcription?.speakers.get(1)).toBe('Speaker 2');
    });

    it('should stop transcription and return results', async () => {
      const callId = 'test-call-123';
      await voiceService.startTranscription(callId, 'session-456');
      
      // Add some transcripts
      const transcription = voiceService.getTranscription(callId);
      transcription?.transcripts.push({
        transcript: 'Test transcript',
        confidence: 0.95,
        isFinal: true,
        timestamp: new Date()
      });
      
      const result = await voiceService.stopTranscription(callId);
      
      expect(result).toBeDefined();
      expect(result?.endTime).toBeDefined();
      expect(result?.duration).toBeGreaterThan(0);
      
      // Should be removed from active transcriptions
      expect(voiceService.getTranscription(callId)).toBeUndefined();
    });
  });

  describe('Text-to-Speech', () => {
    it('should synthesize speech from text', async () => {
      const text = 'Hello, welcome to our call center';
      
      // Mock the TTS response
      vi.spyOn(voiceService['ttsClient'], 'synthesize').mockResolvedValue({
        audio: Buffer.from('mock-audio'),
        format: 'wav',
        duration: 2.5
      });
      
      const audio = await voiceService.synthesizeSpeech(text, 'asteria');
      
      expect(audio).toBeInstanceOf(Buffer);
      expect(audio.length).toBeGreaterThan(0);
    });

    it('should stream speech for long texts', async () => {
      const longText = 'This is a very long text. '.repeat(50);
      
      vi.spyOn(voiceService['ttsClient'], 'synthesize').mockResolvedValue({
        audio: Buffer.from('mock-audio-chunk'),
        format: 'wav',
        duration: 1.0
      });
      
      const chunks: Buffer[] = [];
      
      for await (const chunk of voiceService.streamSpeech(longText, 'luna')) {
        chunks.push(chunk);
      }
      
      expect(chunks.length).toBeGreaterThan(1);
      expect(chunks[0]).toBeInstanceOf(Buffer);
    });

    it('should support different voices', async () => {
      const voices = ['asteria', 'luna', 'stella', 'zeus'] as const;
      
      vi.spyOn(voiceService['ttsClient'], 'synthesize').mockResolvedValue({
        audio: Buffer.from('mock-audio'),
        format: 'wav'
      });
      
      for (const voice of voices) {
        const audio = await voiceService.synthesizeSpeech('Test', voice);
        expect(audio).toBeInstanceOf(Buffer);
      }
    });
  });

  describe('WebSocket Integration', () => {
    it('should handle WebSocket connection for real-time audio', () => {
      const ws = mockWebSocket();
      const callId = 'test-call-123';
      const sessionId = 'session-456';
      
      voiceService.handleWebSocketConnection(ws as any, callId, sessionId);
      
      // Should start transcription
      const transcription = voiceService.getTranscription(callId);
      expect(transcription).toBeDefined();
    });

    it('should process audio from WebSocket', () => {
      const ws = mockWebSocket();
      const callId = 'test-call-123';
      const audioData = Buffer.from('audio-data');
      
      voiceService.handleWebSocketConnection(ws as any, callId, 'session');
      
      // Simulate receiving audio
      const messageHandler = ws.on.mock.calls.find(
        call => call[0] === 'message'
      )?.[1];
      
      expect(messageHandler).toBeDefined();
      messageHandler(audioData);
      
      // Audio should be processed
      expect(() => messageHandler(audioData)).not.toThrow();
    });

    it('should stop transcription on WebSocket close', async () => {
      const ws = mockWebSocket();
      const callId = 'test-call-123';
      
      voiceService.handleWebSocketConnection(ws as any, callId, 'session');
      
      // Simulate WebSocket close
      const closeHandler = ws.on.mock.calls.find(
        call => call[0] === 'close'
      )?.[1];
      
      expect(closeHandler).toBeDefined();
      await closeHandler();
      
      // Transcription should be stopped
      expect(voiceService.getTranscription(callId)).toBeUndefined();
    });
  });

  describe('Analytics and Monitoring', () => {
    it('should track active transcriptions', async () => {
      await voiceService.startTranscription('call-1', 'session-1');
      await voiceService.startTranscription('call-2', 'session-2');
      
      const active = voiceService.getActiveTranscriptions();
      expect(active).toHaveLength(2);
      expect(active[0].callId).toBe('call-1');
      expect(active[1].callId).toBe('call-2');
    });

    it('should analyze sentiment from transcripts', async () => {
      const callId = 'test-call-123';
      await voiceService.startTranscription(callId, 'session-456');
      
      const transcription = voiceService.getTranscription(callId);
      
      // Add positive transcripts
      transcription?.transcripts.push(
        {
          transcript: 'Thank you so much, this is excellent service!',
          confidence: 0.95,
          isFinal: true,
          timestamp: new Date()
        },
        {
          transcript: 'I am very happy with the resolution.',
          confidence: 0.93,
          isFinal: true,
          timestamp: new Date()
        }
      );
      
      const result = await voiceService.stopTranscription(callId);
      
      expect(result?.sentiment).toBe('positive');
      expect(result?.keywords).toContain('excellent');
      expect(result?.keywords).toContain('happy');
    });

    it('should detect compliance alerts', async () => {
      const callId = 'test-call-123';
      let complianceAlertReceived = false;
      
      voiceService.on('complianceAlert', (data) => {
        expect(data.callId).toBe(callId);
        complianceAlertReceived = true;
      });
      
      await voiceService.startTranscription(callId, 'session-456');
      
      // Simulate transcript with compliance keyword
      voiceService.emit('finalTranscript', {
        callId,
        sessionId: 'session-456',
        result: {
          transcript: 'I will contact my lawyer about this',
          confidence: 0.95,
          isFinal: true,
          timestamp: new Date()
        }
      });
      
      await waitFor(100);
      expect(complianceAlertReceived).toBe(true);
    });
  });
});