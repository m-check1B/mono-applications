/**
 * Media Stream Handler for WebRTC/SIP telephony
 * Supports both Twilio and Telnyx media streams
 */

import { EventEmitter } from 'events';
import type { WebSocket } from 'ws';

export interface MediaStreamConfig {
  provider: 'twilio' | 'telnyx';
  sessionId: string;
  callSid?: string;
  streamSid?: string;
  accountSid?: string;
  trackLabel?: string;
  customParameters?: Record<string, any>;
}

export interface MediaMessage {
  event: string;
  sequenceNumber?: string;
  streamSid?: string;
  media?: {
    track: string;
    chunk: string;
    timestamp: string;
    payload: string;
  };
  mark?: {
    name: string;
  };
  start?: MediaStreamConfig;
  stop?: {
    streamSid: string;
  };
}

export interface AudioChunk {
  payload: Buffer;
  timestamp: number;
  sequenceNumber: number;
  trackId: string;
}

export class MediaStreamHandler extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: MediaStreamConfig;
  private isConnected = false;
  private audioBuffer: AudioChunk[] = [];
  private lastSequence = 0;

  constructor(config: MediaStreamConfig) {
    super();
    this.config = config;
  }

  /**
   * Connect to WebSocket and handle media stream
   */
  public connect(ws: WebSocket): void {
    this.ws = ws;
    this.isConnected = true;

    this.ws.on('message', (data: Buffer) => {
      this.handleMessage(data);
    });

    this.ws.on('close', () => {
      this.isConnected = false;
      this.emit('disconnected');
    });

    this.ws.on('error', (error: Error) => {
      this.emit('error', error);
    });
  }

  /**
   * Handle incoming media messages
   */
  private handleMessage(data: Buffer): void {
    try {
      const message: MediaMessage = JSON.parse(data.toString());

      switch (message.event) {
        case 'start':
          this.handleStart(message.start!);
          break;
        
        case 'media':
          this.handleMedia(message);
          break;
        
        case 'mark':
          this.handleMark(message.mark!);
          break;
        
        case 'stop':
          this.handleStop(message.stop!);
          break;
        
        default:
          this.emit('unknown-event', message);
      }
    } catch (error) {
      this.emit('error', error);
    }
  }

  /**
   * Handle stream start event
   */
  private handleStart(config: MediaStreamConfig): void {
    this.config = { ...this.config, ...config };
    this.emit('stream-started', config);
    console.log(`📞 Media stream started: ${config.callSid || config.sessionId}`);
  }

  /**
   * Handle media chunks
   */
  private handleMedia(message: MediaMessage): void {
    if (!message.media) return;

    const audioChunk: AudioChunk = {
      payload: Buffer.from(message.media.payload, 'base64'),
      timestamp: parseInt(message.media.timestamp),
      sequenceNumber: parseInt(message.sequenceNumber || '0'),
      trackId: message.media.track
    };

    // Check for packet loss
    if (this.lastSequence && audioChunk.sequenceNumber !== this.lastSequence + 1) {
      this.emit('packet-loss', {
        expected: this.lastSequence + 1,
        received: audioChunk.sequenceNumber
      });
    }
    this.lastSequence = audioChunk.sequenceNumber;

    // Buffer audio for processing
    this.audioBuffer.push(audioChunk);
    
    // Keep buffer size limited
    if (this.audioBuffer.length > 100) {
      this.audioBuffer.shift();
    }

    this.emit('audio', audioChunk);
  }

  /**
   * Handle mark events (used for synchronization)
   */
  private handleMark(mark: { name: string }): void {
    this.emit('mark', mark);
  }

  /**
   * Handle stream stop event
   */
  private handleStop(stop: { streamSid: string }): void {
    this.emit('stream-stopped', stop);
    console.log(`📞 Media stream stopped: ${stop.streamSid}`);
    this.cleanup();
  }

  /**
   * Send audio to the call
   */
  public sendAudio(audio: Buffer, _encoding: 'pcm16' | 'mulaw' = 'mulaw'): void {
    if (!this.ws || !this.isConnected) {
      throw new Error('WebSocket not connected');
    }

    const message = {
      event: 'media',
      streamSid: this.config.streamSid,
      media: {
        payload: audio.toString('base64')
      }
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Send text/DTMF to the call
   */
  public sendDTMF(digits: string): void {
    if (!this.ws || !this.isConnected) {
      throw new Error('WebSocket not connected');
    }

    const message = {
      event: 'dtmf',
      streamSid: this.config.streamSid,
      dtmf: {
        digits
      }
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Clear/mute the audio stream
   */
  public clear(): void {
    if (!this.ws || !this.isConnected) return;

    const message = {
      event: 'clear',
      streamSid: this.config.streamSid
    };

    this.ws.send(JSON.stringify(message));
  }

  /**
   * Get buffered audio chunks
   */
  public getAudioBuffer(): AudioChunk[] {
    return [...this.audioBuffer];
  }

  /**
   * Clear audio buffer
   */
  public clearBuffer(): void {
    this.audioBuffer = [];
    this.lastSequence = 0;
  }

  /**
   * Cleanup resources
   */
  private cleanup(): void {
    this.clearBuffer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }

  /**
   * Disconnect and cleanup
   */
  public disconnect(): void {
    if (this.ws && this.isConnected) {
      const message = {
        event: 'stop',
        streamSid: this.config.streamSid
      };
      this.ws.send(JSON.stringify(message));
    }
    this.cleanup();
  }
}

/**
 * Factory function to create provider-specific media handlers
 */
export function createMediaStreamHandler(
  provider: 'twilio' | 'telnyx',
  config: Partial<MediaStreamConfig>
): MediaStreamHandler {
  const fullConfig: MediaStreamConfig = {
    provider,
    sessionId: config.sessionId || `session-${Date.now()}`,
    ...config
  };

  return new MediaStreamHandler(fullConfig);
}
