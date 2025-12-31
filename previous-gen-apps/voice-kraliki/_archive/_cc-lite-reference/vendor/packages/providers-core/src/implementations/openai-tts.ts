/**
 * OpenAI TTS implementation
 */

import { BaseTTSClient, TTSProvider, SynthesisOptions } from '../voice';

export class OpenAITTSClient extends BaseTTSClient {
  provider: TTSProvider = 'openai-tts';
  
  private apiUrl = 'https://api.openai.com/v1';
  
  private getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.config.apiKey}`,
      'Content-Type': 'application/json',
    };
  }
  
  async synthesize(text: string, options?: SynthesisOptions): Promise<Uint8Array> {
    const voice = options?.voice || 'alloy';
    const speed = options?.speed || 1.0;
    
    const response = await fetch(`${this.apiUrl}/audio/speech`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        model: 'tts-1',
        input: text,
        voice: voice,
        speed: Math.max(0.25, Math.min(4.0, speed)),
        response_format: this.config.audioConfig?.format || 'mp3',
      }),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: response.statusText } })) as any;
      throw new Error(`OpenAI TTS error: ${error.error?.message || response.statusText}`);
    }
    
    const audioBuffer = await response.arrayBuffer();
    return new Uint8Array(audioBuffer);
  }
  
  async *synthesizeStream(text: string, options?: SynthesisOptions): AsyncIterable<Uint8Array> {
    // OpenAI doesn't support streaming TTS yet, so we'll return the whole audio
    const audioData = await this.synthesize(text, options);
    yield audioData;
  }
  
  async getVoices(language?: string) {
    // OpenAI has a fixed set of voices
    const voices = [
      { id: 'alloy', name: 'Alloy', language: 'en-US', gender: 'neutral' as const },
      { id: 'echo', name: 'Echo', language: 'en-US', gender: 'male' as const },
      { id: 'fable', name: 'Fable', language: 'en-US', gender: 'male' as const },
      { id: 'onyx', name: 'Onyx', language: 'en-US', gender: 'male' as const },
      { id: 'nova', name: 'Nova', language: 'en-US', gender: 'female' as const },
      { id: 'shimmer', name: 'Shimmer', language: 'en-US', gender: 'female' as const },
    ];
    
    if (language) {
      return voices.filter(voice => voice.language.startsWith(language));
    }
    
    return voices;
  }
  
  async getSupportedLanguages(): Promise<string[]> {
    // OpenAI TTS supports multiple languages but doesn't have a specific API for this
    return [
      'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 
      'cs', 'ar', 'zh', 'ja', 'hi', 'ko'
    ];
  }
}