/**
 * @stack-2025/byok-core - Deepgram Agent Core Integration
 * Integration with @stack-2025/deepgram-agent-core for BYOK key management
 */

import { BYOKManager } from '../manager.js';
import { ProviderType, Environment, DecryptedKey } from '../types.js';

/**
 * BYOK-enabled Deepgram configuration
 */
export class BYOKDeepgramConfig {
  private byokManager: BYOKManager;

  constructor(byokManager: BYOKManager) {
    this.byokManager = byokManager;
  }

  /**
   * Get Deepgram configuration with BYOK key
   */
  async getDeepgramConfig(
    userId: string,
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
      validateKey?: boolean;
    } = {}
  ) {
    const {
      environment = Environment.PRODUCTION,
      fallbackToSystem = true,
      validateKey = true
    } = options;

    try {
      // Get BYOK key for Deepgram
      const key = await this.byokManager.getActiveKey(userId, ProviderType.DEEPGRAM, {
        environment,
        fallbackToSystem,
        validateKey
      });

      return this.createDeepgramConfig(key);
    } catch (error) {
      if (fallbackToSystem) {
        // Try system fallback
        const systemApiKey = process.env.DEEPGRAM_API_KEY;
        if (systemApiKey) {
          return this.createSystemConfig(systemApiKey);
        }
      }
      
      throw new Error(`Failed to get Deepgram configuration: ${error}`);
    }
  }

  /**
   * Create Deepgram Voice Agent configuration with BYOK
   */
  async createVoiceAgentConfig(
    userId: string,
    agentConfig: {
      listen?: any;
      think?: any;
      speak?: any;
    },
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
    } = {}
  ) {
    const deepgramConfig = await this.getDeepgramConfig(userId, options);
    
    // Enhanced configuration with BYOK key
    return {
      api_key: deepgramConfig.apiKey,
      url: 'wss://api.deepgram.com/v1/agentic/audio',
      
      // Agent configuration
      config: {
        listen: {
          model: 'nova-2',
          language: 'en',
          smart_format: true,
          encoding: 'linear16',
          sample_rate: 16000,
          channels: 1,
          ...agentConfig.listen
        },
        
        think: {
          provider: 'openai', // Can be overridden
          model: 'gpt-4o-mini',
          max_tokens: 1000,
          temperature: 0.7,
          system_prompt: 'You are a helpful voice assistant.',
          ...agentConfig.think
        },
        
        speak: {
          model: 'aura-asteria-en',
          language: 'en',
          encoding: 'linear16',
          sample_rate: 16000,
          channels: 1,
          container: 'wav',
          ...agentConfig.speak
        }
      },
      
      // Connection settings
      keep_alive: {
        enabled: true,
        interval: 30000,
        timeout: 5000,
        max_retries: 3
      },
      
      auto_reconnect: true,
      max_reconnect_attempts: 5,
      reconnect_interval: 1000,
      conversation_context: true,
      
      // BYOK-specific metadata
      byok: {
        enabled: true,
        userId,
        keyId: deepgramConfig.keyId,
        environment: options.environment || Environment.PRODUCTION
      }
    };
  }

  /**
   * Create STT configuration with BYOK
   */
  async createSTTConfig(
    userId: string,
    sttOptions: {
      model?: string;
      language?: string;
      smart_format?: boolean;
      punctuate?: boolean;
      diarize?: boolean;
    } = {},
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
    } = {}
  ) {
    const deepgramConfig = await this.getDeepgramConfig(userId, options);
    
    return {
      api_key: deepgramConfig.apiKey,
      model: sttOptions.model || 'nova-2',
      language: sttOptions.language || 'en',
      smart_format: sttOptions.smart_format ?? true,
      punctuate: sttOptions.punctuate ?? true,
      diarize: sttOptions.diarize ?? false,
      
      // Advanced features
      multichannel: false,
      alternatives: 1,
      profanity_filter: false,
      redact: [],
      
      // BYOK metadata
      byok: {
        enabled: true,
        userId,
        keyId: deepgramConfig.keyId,
        environment: options.environment || Environment.PRODUCTION
      }
    };
  }

  /**
   * Create TTS configuration with BYOK
   */
  async createTTSConfig(
    userId: string,
    ttsOptions: {
      model?: string;
      language?: string;
      encoding?: string;
      sample_rate?: number;
      container?: string;
    } = {},
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
    } = {}
  ) {
    const deepgramConfig = await this.getDeepgramConfig(userId, options);
    
    return {
      api_key: deepgramConfig.apiKey,
      model: ttsOptions.model || 'aura-asteria-en',
      language: ttsOptions.language || 'en',
      encoding: ttsOptions.encoding || 'linear16',
      sample_rate: ttsOptions.sample_rate || 16000,
      container: ttsOptions.container || 'wav',
      
      // BYOK metadata
      byok: {
        enabled: true,
        userId,
        keyId: deepgramConfig.keyId,
        environment: options.environment || Environment.PRODUCTION
      }
    };
  }

  /**
   * Get available voice models for user's Deepgram key
   */
  async getAvailableVoices(
    userId: string,
    options: {
      environment?: Environment;
      language?: string;
    } = {}
  ): Promise<{
    english: Record<string, { model: string; language: string }>;
    multilingual: Record<string, { model: string; language: string }>;
  }> {
    // Verify user has valid Deepgram key
    await this.getDeepgramConfig(userId, {
      environment: options.environment,
      validateKey: true
    });

    // Return available voices (this could be extended to check actual API capabilities)
    return {
      english: {
        asteria: { model: 'aura-asteria-en', language: 'en' },
        luna: { model: 'aura-luna-en', language: 'en' },
        stella: { model: 'aura-stella-en', language: 'en' },
        athena: { model: 'aura-athena-en', language: 'en' },
        hera: { model: 'aura-hera-en', language: 'en' },
        orion: { model: 'aura-orion-en', language: 'en' },
        arcas: { model: 'aura-arcas-en', language: 'en' },
        perseus: { model: 'aura-perseus-en', language: 'en' },
        angus: { model: 'aura-angus-en', language: 'en' },
        orpheus: { model: 'aura-orpheus-en', language: 'en' },
        helios: { model: 'aura-helios-en', language: 'en' },
        zeus: { model: 'aura-zeus-en', language: 'en' }
      },
      multilingual: {
        asteria: { model: 'aura-asteria-multilingual', language: 'en' },
        luna: { model: 'aura-luna-multilingual', language: 'en' },
        stella: { model: 'aura-stella-multilingual', language: 'en' },
        athena: { model: 'aura-athena-multilingual', language: 'en' },
        hera: { model: 'aura-hera-multilingual', language: 'en' },
        orion: { model: 'aura-orion-multilingual', language: 'en' }
      }
    };
  }

  /**
   * Get STT models available for user's key
   */
  async getSTTModels(userId: string, options: { environment?: Environment } = {}) {
    // Verify user has valid Deepgram key
    await this.getDeepgramConfig(userId, {
      environment: options.environment,
      validateKey: true
    });

    return {
      nova2: { model: 'nova-2', language: 'en' },
      nova2General: { model: 'nova-2-general', language: 'en' },
      nova2Meeting: { model: 'nova-2-meeting', language: 'en' },
      nova2Phonecall: { model: 'nova-2-phonecall', language: 'en' },
      nova2Finance: { model: 'nova-2-finance', language: 'en' },
      nova2Conversational: { model: 'nova-2-conversational', language: 'en' },
      nova2Medical: { model: 'nova-2-medical', language: 'en' },
      nova2Drivethru: { model: 'nova-2-drivethru', language: 'en' }
    };
  }

  /**
   * Record usage for billing and analytics
   */
  async recordUsage(
    userId: string,
    usage: {
      operation: 'stt' | 'tts' | 'voice_agent';
      duration?: number; // in seconds
      characters?: number; // for TTS
      audioMinutes?: number; // for STT
      model?: string;
      cost?: number;
      success: boolean;
      error?: string;
    }
  ) {
    try {
      // This would integrate with the BYOK usage tracking system
      console.log(`Recording Deepgram usage for ${userId}:`, usage);
    } catch (error) {
      console.warn('Failed to record Deepgram usage:', error);
    }
  }

  // Private helper methods

  private createDeepgramConfig(key: DecryptedKey) {
    const keyData = key.keyData as any;
    
    return {
      apiKey: keyData.apiKey,
      projectId: keyData.projectId,
      keyId: key.id,
      environment: key.environment,
      capabilities: key.capabilities,
      healthScore: key.healthScore,
      metadata: key.metadata
    };
  }

  private createSystemConfig(apiKey: string) {
    return {
      apiKey,
      projectId: process.env.DEEPGRAM_PROJECT_ID,
      keyId: 'system-fallback',
      environment: Environment.PRODUCTION,
      capabilities: ['stt', 'tts', 'voice-agent', 'live'],
      healthScore: 100,
      metadata: { isSystemFallback: true }
    };
  }
}

/**
 * BYOK Deepgram middleware for Express/tRPC
 */
export class BYOKDeepgramMiddleware {
  private config: BYOKDeepgramConfig;

  constructor(byokManager: BYOKManager) {
    this.config = new BYOKDeepgramConfig(byokManager);
  }

  /**
   * Express middleware to inject Deepgram config
   */
  async middleware(req: any, res: any, next: any) {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return next();
      }

      // Get Deepgram configuration
      const deepgramConfig = await this.config.getDeepgramConfig(userId, {
        environment: req.environment || Environment.PRODUCTION,
        fallbackToSystem: true,
        validateKey: false // Skip validation for performance
      });

      // Attach to request
      req.deepgramConfig = deepgramConfig;
      req.byokDeepgram = true;

      next();
    } catch (error) {
      console.warn('BYOK Deepgram middleware failed:', error);
      req.byokDeepgram = false;
      next();
    }
  }

  /**
   * Usage tracking middleware
   */
  usageMiddleware() {
    return async (req: any, res: any, next: any) => {
      if (!req.byokDeepgram || !req.user?.id) {
        return next();
      }

      const userId = req.user.id;
      const startTime = Date.now();
      
      // Wrap response to capture usage
      const originalSend = res.send;
      res.send = function(data: any) {
        const duration = (Date.now() - startTime) / 1000;
        
        // Extract usage info and record asynchronously
        extractDeepgramUsage(data, req.path, duration)
          .then(usage => {
            if (usage) {
              recordDeepgramUsage(userId, usage);
            }
          })
          .catch(error => {
            console.warn('Failed to record Deepgram usage:', error);
          });

        return originalSend.call(this, data);
      };

      next();
    };
  }
}

// Helper functions for usage tracking
async function extractDeepgramUsage(data: any, path: string, duration: number) {
  try {
    if (typeof data === 'string') {
      data = JSON.parse(data);
    }

    let operation: 'stt' | 'tts' | 'voice_agent' = 'stt';
    if (path.includes('/tts')) operation = 'tts';
    if (path.includes('/voice-agent') || path.includes('/agentic')) operation = 'voice_agent';

    return {
      operation,
      duration,
      audioMinutes: data.metadata?.duration_seconds ? data.metadata.duration_seconds / 60 : undefined,
      characters: data.metadata?.characters || data.text?.length,
      model: data.model,
      cost: data.metadata?.cost || 0,
      success: !data.error,
      error: data.error?.message
    };
  } catch (error) {
    console.warn('Failed to extract Deepgram usage:', error);
    return null;
  }
}

async function recordDeepgramUsage(userId: string, usage: any) {
  try {
    // This would record in the BYOK system
    console.log(`Recording Deepgram usage for ${userId}:`, usage);
  } catch (error) {
    console.warn('Failed to record Deepgram usage:', error);
  }
}

/**
 * Preset configurations for common Deepgram use cases with BYOK
 */
export class BYOKDeepgramPresets {
  private config: BYOKDeepgramConfig;

  constructor(byokManager: BYOKManager) {
    this.config = new BYOKDeepgramConfig(byokManager);
  }

  /**
   * Customer service voice agent preset
   */
  async customerService(userId: string, options: { environment?: Environment } = {}) {
    return this.config.createVoiceAgentConfig(userId, {
      listen: {
        model: 'nova-2-conversational',
        language: 'en',
        smart_format: true
      },
      think: {
        provider: 'openai',
        model: 'gpt-4o-mini',
        temperature: 0.3,
        system_prompt: 'You are a helpful customer service representative. Be polite, professional, and solution-oriented.'
      },
      speak: {
        model: 'aura-asteria-en',
        language: 'en'
      }
    }, options);
  }

  /**
   * Medical consultation preset
   */
  async medicalConsultation(userId: string, options: { environment?: Environment } = {}) {
    return this.config.createVoiceAgentConfig(userId, {
      listen: {
        model: 'nova-2-medical',
        language: 'en',
        smart_format: true
      },
      think: {
        provider: 'anthropic',
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.2,
        system_prompt: 'You are a medical consultation assistant. Be accurate, careful, and always recommend consulting with healthcare professionals for medical advice.'
      },
      speak: {
        model: 'aura-athena-en',
        language: 'en'
      }
    }, options);
  }

  /**
   * Drive-thru ordering preset
   */
  async driveThru(userId: string, options: { environment?: Environment } = {}) {
    return this.config.createVoiceAgentConfig(userId, {
      listen: {
        model: 'nova-2-drivethru',
        language: 'en',
        smart_format: true,
        sample_rate: 8000 // Phone quality
      },
      think: {
        provider: 'deepgram',
        model: 'hermes-2-pro-mistral-7b',
        temperature: 0.1,
        system_prompt: 'You are a drive-thru order assistant. Be quick, accurate, and confirm orders clearly.'
      },
      speak: {
        model: 'aura-orion-en',
        language: 'en',
        sample_rate: 8000
      }
    }, options);
  }
}

/**
 * Factory function for BYOK Deepgram integration
 */
export function createBYOKDeepgramIntegration(byokManager: BYOKManager) {
  return {
    config: new BYOKDeepgramConfig(byokManager),
    middleware: new BYOKDeepgramMiddleware(byokManager),
    presets: new BYOKDeepgramPresets(byokManager)
  };
}