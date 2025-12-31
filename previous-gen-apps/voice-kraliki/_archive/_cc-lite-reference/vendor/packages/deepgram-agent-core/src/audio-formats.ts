/**
 * Audio Format Configuration
 * Comprehensive audio format handling for browser and Twilio environments
 */

export interface AudioFormat {
  name: string;
  mimeType: string;
  sampleRate: number | number[];
  bitDepth?: number;
  channels: number;
  codec?: string;
  compression?: 'none' | 'lossy' | 'lossless';
  fileExtension: string;
  supported: {
    browser: boolean;
    twilio: boolean;
    deepgram: boolean;
    openai: boolean;
    gemini: boolean;
  };
}

/**
 * Supported audio formats across platforms
 */
export const AUDIO_FORMATS: Record<string, AudioFormat> = {
  // Uncompressed formats
  'pcm16': {
    name: 'PCM 16-bit',
    mimeType: 'audio/pcm',
    sampleRate: [8000, 16000, 24000, 44100, 48000],
    bitDepth: 16,
    channels: 1,
    codec: 'pcm_s16le',
    compression: 'none',
    fileExtension: 'pcm',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: true,
      gemini: true
    }
  },
  'pcm24': {
    name: 'PCM 24-bit',
    mimeType: 'audio/pcm',
    sampleRate: [24000, 44100, 48000],
    bitDepth: 24,
    channels: 1,
    codec: 'pcm_s24le',
    compression: 'none',
    fileExtension: 'pcm',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: false,
      gemini: true
    }
  },
  'linear16': {
    name: 'Linear PCM 16-bit',
    mimeType: 'audio/l16',
    sampleRate: [8000, 16000, 24000],
    bitDepth: 16,
    channels: 1,
    codec: 'pcm_s16be',
    compression: 'none',
    fileExtension: 'raw',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: true,
      gemini: true
    }
  },

  // Telephony formats
  'g711_ulaw': {
    name: 'G.711 μ-law',
    mimeType: 'audio/basic',
    sampleRate: [8000],
    bitDepth: 8,
    channels: 1,
    codec: 'pcm_mulaw',
    compression: 'lossy',
    fileExtension: 'ulaw',
    supported: {
      browser: false,
      twilio: true,
      deepgram: true,
      openai: true,
      gemini: false
    }
  },
  'g711_alaw': {
    name: 'G.711 A-law',
    mimeType: 'audio/x-alaw-basic',
    sampleRate: [8000],
    bitDepth: 8,
    channels: 1,
    codec: 'pcm_alaw',
    compression: 'lossy',
    fileExtension: 'alaw',
    supported: {
      browser: false,
      twilio: true,
      deepgram: true,
      openai: true,
      gemini: false
    }
  },

  // Compressed formats
  'opus': {
    name: 'Opus',
    mimeType: 'audio/opus',
    sampleRate: [8000, 16000, 24000, 48000],
    channels: 1,
    codec: 'opus',
    compression: 'lossy',
    fileExtension: 'opus',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: false,
      gemini: true
    }
  },
  'ogg_opus': {
    name: 'Ogg Opus',
    mimeType: 'audio/ogg',
    sampleRate: [16000, 24000, 48000],
    channels: 1,
    codec: 'opus',
    compression: 'lossy',
    fileExtension: 'ogg',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: false,
      gemini: true
    }
  },
  'webm_opus': {
    name: 'WebM Opus',
    mimeType: 'audio/webm',
    sampleRate: [16000, 24000, 48000],
    channels: 1,
    codec: 'opus',
    compression: 'lossy',
    fileExtension: 'webm',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: false,
      gemini: true
    }
  },
  'mp3': {
    name: 'MP3',
    mimeType: 'audio/mpeg',
    sampleRate: [8000, 16000, 22050, 44100, 48000],
    channels: 1,
    codec: 'mp3',
    compression: 'lossy',
    fileExtension: 'mp3',
    supported: {
      browser: true,
      twilio: false,
      deepgram: true,
      openai: false,
      gemini: true
    }
  }
};

/**
 * Audio conversion utilities
 */
export class AudioConverter {
  /**
   * Convert PCM16 to G.711 μ-law for Twilio
   */
  static pcm16ToMulaw(pcmBuffer: ArrayBuffer, sampleRate = 16000): ArrayBuffer {
    const pcmView = new Int16Array(pcmBuffer);
    const mulawBuffer = new Uint8Array(pcmView.length);
    
    // Resample if needed (simple decimation for 16kHz to 8kHz)
    const decimationFactor = sampleRate / 8000;
    const outputLength = Math.floor(pcmView.length / decimationFactor);
    
    for (let i = 0; i < outputLength; i++) {
      const pcmSample = pcmView[Math.floor(i * decimationFactor)];
      mulawBuffer[i] = this.linearToMulaw(pcmSample);
    }
    
    return mulawBuffer.buffer.slice(0, outputLength);
  }

  /**
   * Convert G.711 μ-law to PCM16 for processing
   */
  static mulawToPcm16(mulawBuffer: ArrayBuffer): ArrayBuffer {
    const mulawView = new Uint8Array(mulawBuffer);
    const pcmBuffer = new Int16Array(mulawView.length);
    
    for (let i = 0; i < mulawView.length; i++) {
      pcmBuffer[i] = this.mulawToLinear(mulawView[i]);
    }
    
    return pcmBuffer.buffer;
  }

  /**
   * μ-law encoding
   */
  private static linearToMulaw(sample: number): number {
    const MULAW_MAX = 0x1FFF;
    const MULAW_BIAS = 33;
    const sign = sample < 0 ? 0x80 : 0;
    
    if (sign) sample = -sample;
    if (sample > MULAW_MAX) sample = MULAW_MAX;
    
    sample += MULAW_BIAS;
    const exponent = Math.floor(Math.log2(sample)) - 5;
    const mantissa = (sample >> (exponent + 3)) & 0x0F;
    
    return ~(sign | (exponent << 4) | mantissa) & 0xFF;
  }

  /**
   * μ-law decoding
   */
  private static mulawToLinear(mulaw: number): number {
    const MULAW_BIAS = 33;
    mulaw = ~mulaw;
    const sign = mulaw & 0x80;
    const exponent = (mulaw >> 4) & 0x07;
    const mantissa = mulaw & 0x0F;
    
    let sample = ((mantissa << 3) + MULAW_BIAS) << exponent;
    if (sign) sample = -sample;
    
    return sample;
  }

  /**
   * Resample audio to target sample rate
   */
  static resample(
    audioBuffer: ArrayBuffer,
    fromRate: number,
    toRate: number
  ): ArrayBuffer {
    if (fromRate === toRate) return audioBuffer;
    
    const ratio = fromRate / toRate;
    const inputView = new Int16Array(audioBuffer);
    const outputLength = Math.floor(inputView.length / ratio);
    const outputBuffer = new Int16Array(outputLength);
    
    for (let i = 0; i < outputLength; i++) {
      const sourceIndex = i * ratio;
      const index = Math.floor(sourceIndex);
      const fraction = sourceIndex - index;
      
      if (index + 1 < inputView.length) {
        // Linear interpolation
        outputBuffer[i] = Math.round(
          inputView[index] * (1 - fraction) + 
          inputView[index + 1] * fraction
        );
      } else {
        outputBuffer[i] = inputView[index];
      }
    }
    
    return outputBuffer.buffer;
  }

  /**
   * Convert stereo to mono
   */
  static stereoToMono(stereoBuffer: ArrayBuffer): ArrayBuffer {
    const stereoView = new Int16Array(stereoBuffer);
    const monoLength = Math.floor(stereoView.length / 2);
    const monoBuffer = new Int16Array(monoLength);
    
    for (let i = 0; i < monoLength; i++) {
      // Average left and right channels
      monoBuffer[i] = Math.round((stereoView[i * 2] + stereoView[i * 2 + 1]) / 2);
    }
    
    return monoBuffer.buffer;
  }

  /**
   * Convert between bit depths
   */
  static convertBitDepth(
    audioBuffer: ArrayBuffer,
    fromBits: number,
    toBits: number
  ): ArrayBuffer {
    if (fromBits === toBits) return audioBuffer;
    
    if (fromBits === 16 && toBits === 24) {
      const input = new Int16Array(audioBuffer);
      const output = new Uint8Array(input.length * 3);
      
      for (let i = 0; i < input.length; i++) {
        const sample = input[i];
        const sample24 = sample << 8; // Shift to 24-bit range
        
        // Little-endian 24-bit
        output[i * 3] = sample24 & 0xFF;
        output[i * 3 + 1] = (sample24 >> 8) & 0xFF;
        output[i * 3 + 2] = (sample24 >> 16) & 0xFF;
      }
      
      return output.buffer;
    }
    
    if (fromBits === 24 && toBits === 16) {
      const input = new Uint8Array(audioBuffer);
      const output = new Int16Array(input.length / 3);
      
      for (let i = 0; i < output.length; i++) {
        // Little-endian 24-bit to 16-bit
        const sample24 = 
          input[i * 3] |
          (input[i * 3 + 1] << 8) |
          (input[i * 3 + 2] << 16);
        
        output[i] = sample24 >> 8; // Shift back to 16-bit range
      }
      
      return output.buffer;
    }
    
    return audioBuffer;
  }
}

/**
 * Audio format detection
 */
export class AudioFormatDetector {
  /**
   * Detect format from MIME type
   */
  static detectFromMimeType(mimeType: string): string | null {
    for (const [key, format] of Object.entries(AUDIO_FORMATS)) {
      if (format.mimeType === mimeType) {
        return key;
      }
    }
    return null;
  }

  /**
   * Detect format from file extension
   */
  static detectFromExtension(extension: string): string | null {
    const ext = extension.toLowerCase().replace('.', '');
    for (const [key, format] of Object.entries(AUDIO_FORMATS)) {
      if (format.fileExtension === ext) {
        return key;
      }
    }
    return null;
  }

  /**
   * Get best format for environment
   */
  static getBestFormat(environment: 'browser' | 'twilio'): string {
    if (environment === 'browser') {
      return 'pcm16'; // Best for real-time processing
    } else if (environment === 'twilio') {
      return 'g711_ulaw'; // Required for Twilio
    }
    return 'pcm16';
  }

  /**
   * Get compatible formats between services
   */
  static getCompatibleFormats(
    services: ('browser' | 'twilio' | 'deepgram' | 'openai' | 'gemini')[]
  ): string[] {
    return Object.entries(AUDIO_FORMATS)
      .filter(([_, format]) => {
        return services.every(service => format.supported[service]);
      })
      .map(([key]) => key);
  }
}

/**
 * Audio configuration for different scenarios
 */
export const AUDIO_CONFIGS = {
  browser: {
    input: {
      format: 'pcm16',
      sampleRate: 16000,
      channels: 1,
      bitDepth: 16
    },
    output: {
      format: 'pcm16',
      sampleRate: 24000,
      channels: 1,
      bitDepth: 16
    }
  },
  twilio: {
    input: {
      format: 'g711_ulaw',
      sampleRate: 8000,
      channels: 1,
      bitDepth: 8
    },
    output: {
      format: 'g711_ulaw',
      sampleRate: 8000,
      channels: 1,
      bitDepth: 8
    }
  },
  highQuality: {
    input: {
      format: 'pcm24',
      sampleRate: 48000,
      channels: 1,
      bitDepth: 24
    },
    output: {
      format: 'pcm24',
      sampleRate: 48000,
      channels: 1,
      bitDepth: 24
    }
  }
};