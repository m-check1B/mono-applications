/**
 * @stack-2025/deepgram-agent-core - Configuration
 * Configuration builders and validators for Deepgram Voice Agent API
 */

import { 
  AgentConfig, 
  AgentConfigSchema, 
  LLMConfig, 
  LLMConfigSchema, 
  VoiceConfig, 
  VoiceConfigSchema,
  ProviderLLMConfig,
  OpenAIConfig,
  AnthropicConfig,
  DeepgramLLMConfig,
  OpenRouterConfig,
  KeepAliveConfig,
  VoiceAgentOptions,
  ConfigurationError
} from './types.js';

/**
 * Configuration Builder for Voice Agent
 */
export class VoiceAgentConfigBuilder {
  private config: Partial<AgentConfig> = {};

  /**
   * Configure listening (STT) settings
   */
  listen(config: Partial<VoiceConfig>): this {
    const validated = VoiceConfigSchema.parse({
      model: 'nova-2',
      language: 'en',
      smart_format: true,
      encoding: 'linear16',
      sample_rate: 16000,
      channels: 1,
      ...config
    });
    
    this.config.listen = validated;
    return this;
  }

  /**
   * Configure thinking (LLM) settings
   */
  think(config: ProviderLLMConfig): this {
    const validated = LLMConfigSchema.parse(config);
    this.config.think = validated;
    return this;
  }

  /**
   * Configure speaking (TTS) settings  
   */
  speak(config: Partial<VoiceConfig>): this {
    const validated = VoiceConfigSchema.parse({
      model: 'aura-asteria-en',
      language: 'en',
      encoding: 'linear16',
      sample_rate: 16000,
      channels: 1,
      container: 'wav',
      ...config
    });
    
    this.config.speak = validated;
    return this;
  }

  /**
   * Build and validate the complete configuration
   */
  build(): AgentConfig {
    if (!this.config.listen || !this.config.think || !this.config.speak) {
      throw new ConfigurationError('Missing required configuration sections: listen, think, or speak');
    }

    return AgentConfigSchema.parse(this.config);
  }
}

/**
 * Provider-specific LLM configuration builders
 */
export class LLMProviders {
  /**
   * OpenAI GPT configuration
   */
  static openai(config: Partial<OpenAIConfig> = {}): OpenAIConfig {
    return {
      provider: 'openai',
      model: 'gpt-4',
      max_tokens: 1000,
      temperature: 0.7,
      ...config
    };
  }

  /**
   * Anthropic Claude configuration
   */
  static anthropic(config: Partial<AnthropicConfig> = {}): AnthropicConfig {
    return {
      provider: 'anthropic',
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1000,
      temperature: 0.7,
      ...config
    };
  }

  /**
   * Deepgram native LLM configuration
   */
  static deepgram(config: Partial<DeepgramLLMConfig> = {}): DeepgramLLMConfig {
    return {
      provider: 'deepgram',
      model: 'hermes-2-pro-mistral-7b',
      max_tokens: 1000,
      temperature: 0.7,
      ...config
    };
  }

  /**
   * OpenRouter configuration (GPT-5 via OpenRouter API)
   */
  static openrouter(config: Partial<OpenRouterConfig> & { api_key: string }): OpenRouterConfig {
    const defaultHeaders: Record<string, string> = {};
    if (process.env.OPENROUTER_HTTP_REFERER) {
      defaultHeaders['HTTP-Referer'] = process.env.OPENROUTER_HTTP_REFERER;
    }
    if (process.env.OPENROUTER_TITLE) {
      defaultHeaders['X-Title'] = process.env.OPENROUTER_TITLE;
    }

    return {
      provider: 'openrouter',
      model: config.model || process.env.OPENROUTER_MODEL || 'openrouter/openai/gpt-5',
      api_key: config.api_key,
      base_url: config.base_url || process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      max_tokens: config.max_tokens || 1000,
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      system_prompt: config.system_prompt,
      functions: config.functions,
      headers: {
        ...defaultHeaders,
        ...(config.headers || {})
      }
    };
  }
}

/**
 * Pre-built voice model configurations
 */
export class VoiceModels {
  /**
   * High-quality English voice models
   */
  static english = {
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
  };

  /**
   * Multilingual voice models
   */
  static multilingual = {
    asteria: { model: 'aura-asteria-multilingual', language: 'en' },
    luna: { model: 'aura-luna-multilingual', language: 'en' },
    stella: { model: 'aura-stella-multilingual', language: 'en' },
    athena: { model: 'aura-athena-multilingual', language: 'en' },
    hera: { model: 'aura-hera-multilingual', language: 'en' },
    orion: { model: 'aura-orion-multilingual', language: 'en' }
  };

  /**
   * Spanish voice models - Aura-2 native Spanish voices
   */
  static spanish = {
    // Peninsular Spanish
    nestor: { model: 'aura-2-nestor-es', language: 'es-ES' },
    carina: { model: 'aura-2-carina-es', language: 'es-ES' },
    alvaro: { model: 'aura-2-alvaro-es', language: 'es-ES' },
    diana: { model: 'aura-2-diana-es', language: 'es-ES' },
    
    // Latin American Spanish
    aquila: { model: 'aura-2-aquila-es', language: 'es-LA' },
    selena: { model: 'aura-2-selena-es', language: 'es-LA' },
    
    // Mexican Spanish
    estrella: { model: 'aura-2-estrella-es', language: 'es-MX' },
    sirio: { model: 'aura-2-sirio-es', language: 'es-MX' },
    
    // Colombian Spanish
    celeste: { model: 'aura-2-celeste-es', language: 'es-CO' },
    
    // Legacy
    asteria: { model: 'aura-asteria-es', language: 'es' }
  };

  /**
   * Czech voice models (external TTS fallback)
   */
  static czech = {
    kamila: { model: 'external-tts-czech-kamila', language: 'cs' },
    pavel: { model: 'external-tts-czech-pavel', language: 'cs' },
    jana: { model: 'external-tts-czech-jana', language: 'cs' },
    tomas: { model: 'external-tts-czech-tomas', language: 'cs' }
  };

  /**
   * STT models for listening
   */
  static stt = {
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
 * Default keep-alive configuration
 */
export const DEFAULT_KEEP_ALIVE: KeepAliveConfig = {
  enabled: true,
  interval: 30000, // 30 seconds
  timeout: 5000,   // 5 seconds
  max_retries: 3
};

/**
 * Pre-built configurations for common use cases
 */
export class PresetConfigs {
  /**
   * Customer service agent configuration
   */
  static customerService(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-conversational',
        language: 'en',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.3,
        system_prompt: 'You are a helpful customer service representative. Be polite, professional, and solution-oriented.'
      }))
      .speak(VoiceModels.english.asteria);
  }

  /**
   * Personal assistant configuration
   */
  static personalAssistant(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-general',
        language: 'en',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.7,
        system_prompt: 'You are a personal assistant. Be helpful, friendly, and proactive in assisting with tasks.'
      }))
      .speak(VoiceModels.english.luna);
  }

  /**
   * Medical consultation configuration
   */
  static medicalConsultation(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-medical',
        language: 'en',
        smart_format: true
      })
      .think(LLMProviders.anthropic({
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.2,
        system_prompt: 'You are a medical consultation assistant. Be accurate, careful, and always recommend consulting with healthcare professionals for medical advice.'
      }))
      .speak(VoiceModels.english.athena);
  }

  /**
   * Drive-thru order taking configuration
   */
  static driveThru(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-drivethru',
        language: 'en',
        smart_format: true,
        sample_rate: 8000 // Lower quality for telephony
      })
      .think(LLMProviders.deepgram({
        model: 'hermes-2-pro-mistral-7b',
        temperature: 0.1,
        system_prompt: 'You are a drive-thru order assistant. Be quick, accurate, and confirm orders clearly.'
      }))
      .speak({
        model: 'aura-orion-en',
        language: 'en',
        sample_rate: 8000
      });
  }

  /**
   * Financial services configuration
   */
  static financialServices(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-finance',
        language: 'en',
        smart_format: true
      })
      .think(LLMProviders.anthropic({
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.1,
        system_prompt: 'You are a financial services assistant. Be accurate, secure, and compliant with financial regulations.'
      }))
      .speak(VoiceModels.english.zeus);
  }

  /**
   * Czech customer service configuration
   */
  static czechCustomerService(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-conversational',
        language: 'cs',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.3,
        system_prompt: 'Jste profesionální a nápomocný AI asistent pro moderní kontaktní centrum. Vaše role je pomáhat volajícím s jejich dotazy přátelským a efektivním způsobem. Buďte zdvořilý, profesionální a zaměřený na řešení problémů.'
      }))
      .speak(VoiceModels.czech.kamila);
  }

  /**
   * Healthcare configuration (Czech)
   */
  static czechHealthcare(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-medical',
        language: 'cs',
        smart_format: true
      })
      .think(LLMProviders.anthropic({
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.2,
        system_prompt: 'Jste lékařský konzultační asistent. Buďte přesní, opatrní a vždy doporučte konzultaci s odbornými lékaři pro lékařské rady. Projevujte empatii a porozumění.'
      }))
      .speak(VoiceModels.czech.jana);
  }

  /**
   * Spanish customer service configuration
   */
  static spanishCustomerService(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-conversational',
        language: 'es',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.3,
        system_prompt: 'Eres un asistente de atención al cliente profesional y servicial para un centro de contacto moderno. Tu función es ayudar a los usuarios con sus consultas de manera amigable y eficiente. Sé cortés, profesional y enfocado en resolver problemas.'
      }))
      .speak(VoiceModels.spanish.nestor);
  }

  /**
   * Spanish healthcare configuration
   */
  static spanishHealthcare(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-medical',
        language: 'es',
        smart_format: true
      })
      .think(LLMProviders.anthropic({
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.2,
        system_prompt: 'Eres un asistente de consulta médica. Sé preciso, cuidadoso y siempre recomienda consultar con profesionales médicos para obtener asesoramiento médico. Muestra empatía y comprensión hacia los pacientes.'
      }))
      .speak(VoiceModels.spanish.sirio);
  }

  /**
   * Spanish sales configuration
   */
  static spanishSales(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-conversational',
        language: 'es',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.7,
        system_prompt: 'Eres un asistente de ventas entusiasta y persuasivo. Tu objetivo es ayudar a los clientes a encontrar las mejores soluciones para sus necesidades. Sé energético, informativo y enfocado en los beneficios del producto.'
      }))
      .speak(VoiceModels.spanish.aquila);
  }

  /**
   * Spanish corporate/professional configuration
   */
  static spanishCorporate(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-general',
        language: 'es',
        smart_format: true
      })
      .think(LLMProviders.anthropic({
        model: 'claude-3-5-sonnet-20241022',
        temperature: 0.3,
        system_prompt: 'Eres un asistente corporativo profesional. Proporciona información precisa, mantén un tono formal pero accesible, y enfócate en la eficiencia y claridad en todas las comunicaciones empresariales.'
      }))
      .speak(VoiceModels.spanish.alvaro);
  }

  /**
   * Spanish marketing/entertainment configuration
   */
  static spanishMarketing(): VoiceAgentConfigBuilder {
    return new VoiceAgentConfigBuilder()
      .listen({
        model: 'nova-2-conversational',
        language: 'es',
        smart_format: true
      })
      .think(LLMProviders.openai({
        model: 'gpt-4',
        temperature: 0.8,
        system_prompt: 'Eres un asistente de marketing creativo y expresivo. Tu objetivo es captar la atención, crear conexiones emocionales y comunicar mensajes de marca de manera memorable y atractiva.'
      }))
      .speak(VoiceModels.spanish.diana);
  }
}

/**
 * Utility functions for configuration validation and defaults
 */
export class ConfigUtils {
  /**
   * Validate and merge with defaults
   */
  static validateOptions(options: Partial<VoiceAgentOptions>): VoiceAgentOptions {
    if (!options.api_key) {
      throw new ConfigurationError('API key is required');
    }

    return {
      api_key: options.api_key,
      url: 'wss://api.deepgram.com/v1/agentic/audio',
      keep_alive: DEFAULT_KEEP_ALIVE,
      auto_reconnect: true,
      max_reconnect_attempts: 5,
      reconnect_interval: 1000,
      conversation_context: true,
      ...options
    };
  }

  /**
   * Create default agent configuration
   */
  static defaultConfig(): AgentConfig {
    return new VoiceAgentConfigBuilder()
      .listen(VoiceModels.stt.nova2)
      .think(LLMProviders.openai())
      .speak(VoiceModels.english.asteria)
      .build();
  }

  /**
   * Validate environment variables for provider API keys
   */
  static validateEnvironment(): { openai?: string; anthropic?: string; deepgram?: string } {
    return {
      openai: process.env.OPENAI_API_KEY,
      anthropic: process.env.ANTHROPIC_API_KEY,
      deepgram: process.env.DEEPGRAM_API_KEY
    };
  }
}

/**
 * Export convenience function for creating configurations
 */
export function createVoiceAgentConfig(): VoiceAgentConfigBuilder {
  return new VoiceAgentConfigBuilder();
}
