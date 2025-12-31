/**
 * @stack-2025/deepgram-agent-core - Providers
 * LLM and voice provider configurations for Deepgram Voice Agent API
 */

import {
  ProviderLLMConfig,
  OpenAIConfig,
  AnthropicConfig,
  DeepgramLLMConfig,
  OpenRouterConfig,
  FunctionDefinition,
  ConfigurationError,
  LLMProvider
} from './types.js';

/**
 * Provider configuration factory
 */
export class ProviderFactory {
  /**
   * Create OpenAI configuration with validation
   */
  static createOpenAI(config: Partial<OpenAIConfig> & { model: string }): OpenAIConfig {
    const validModels = [
      'gpt-4',
      'gpt-4-turbo',
      'gpt-4-turbo-preview',
      'gpt-4-0125-preview',
      'gpt-4-1106-preview',
      'gpt-3.5-turbo',
      'gpt-3.5-turbo-0125',
      'gpt-3.5-turbo-1106'
    ];

    if (!validModels.includes(config.model) && !config.model.startsWith('gpt-')) {
      console.warn(`Model ${config.model} is not in the known list. Proceeding anyway.`);
    }

    return {
      provider: 'openai',
      model: config.model,
      max_tokens: config.max_tokens || 1000,
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      system_prompt: config.system_prompt,
      functions: config.functions,
      api_key: config.api_key || process.env.OPENAI_API_KEY
    };
  }

  /**
   * Create Anthropic configuration with validation
   */
  static createAnthropic(config: Partial<AnthropicConfig> & { model: string }): AnthropicConfig {
    const validModels = [
      'claude-3-5-sonnet-20241022',
      'claude-3-5-haiku-20241022',
      'claude-3-opus-20240229',
      'claude-3-sonnet-20240229',
      'claude-3-haiku-20240307'
    ];

    if (!validModels.includes(config.model) && !config.model.startsWith('claude-')) {
      console.warn(`Model ${config.model} is not in the known list. Proceeding anyway.`);
    }

    return {
      provider: 'anthropic',
      model: config.model,
      max_tokens: config.max_tokens || 1000,
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      system_prompt: config.system_prompt,
      functions: config.functions,
      api_key: config.api_key || process.env.ANTHROPIC_API_KEY
    };
  }

  /**
   * Create Deepgram LLM configuration
   */
  static createDeepgram(config: Partial<DeepgramLLMConfig> & { model: string }): DeepgramLLMConfig {
    const validModels = [
      'hermes-2-pro-mistral-7b',
      'hermes-2-pro-llama-3-8b',
      'nous-hermes-2-mixtral-8x7b'
    ];

    if (!validModels.includes(config.model)) {
      console.warn(`Model ${config.model} is not in the known Deepgram models list. Proceeding anyway.`);
    }

    return {
      provider: 'deepgram',
      model: config.model,
      max_tokens: config.max_tokens || 1000,
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      system_prompt: config.system_prompt,
      functions: config.functions
    };
  }

  /**
   * Create OpenRouter configuration with validation
   */
  static createOpenRouter(config: Partial<OpenRouterConfig> & { api_key: string }): OpenRouterConfig {
    if (!config.api_key) {
      throw new ConfigurationError('OpenRouter API key is required for OpenRouter provider');
    }

    const headers = {
      ...(config.headers || {}),
      ...(process.env.OPENROUTER_HTTP_REFERER ? { 'HTTP-Referer': process.env.OPENROUTER_HTTP_REFERER } : {}),
      ...(process.env.OPENROUTER_TITLE ? { 'X-Title': process.env.OPENROUTER_TITLE } : {}),
    };

    return {
      provider: 'openrouter',
      model: config.model || process.env.OPENROUTER_MODEL || 'openrouter/openai/gpt-5',
      api_key: config.api_key,
      base_url: config.base_url || process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      max_tokens: config.max_tokens || 1000,
      temperature: config.temperature !== undefined ? config.temperature : 0.7,
      system_prompt: config.system_prompt,
      functions: config.functions,
      headers
    };
  }

  /**
   * Auto-detect and create provider configuration
   */
  static autoDetect(config: ProviderLLMConfig): ProviderLLMConfig {
    switch (config.provider) {
      case 'openai':
        return this.createOpenAI(config as OpenAIConfig);
      case 'anthropic':
        return this.createAnthropic(config as AnthropicConfig);
      case 'deepgram':
        return this.createDeepgram(config as DeepgramLLMConfig);
      case 'openrouter':
        return this.createOpenRouter(config as OpenRouterConfig);
      default:
        throw new ConfigurationError(`Unknown provider: ${(config as any).provider}`);
    }
  }
}

/**
 * Function definition helpers for common use cases
 */
export class FunctionDefinitions {
  /**
   * Get current time function
   */
  static getCurrentTime(): FunctionDefinition {
    return {
      name: 'get_current_time',
      description: 'Get the current date and time',
      parameters: {
        type: 'object',
        properties: {
          timezone: {
            type: 'string',
            description: 'Timezone (e.g., "America/New_York", "Europe/London")',
          }
        }
      }
    };
  }

  /**
   * Weather lookup function
   */
  static getWeather(): FunctionDefinition {
    return {
      name: 'get_weather',
      description: 'Get current weather information for a location',
      parameters: {
        type: 'object',
        properties: {
          location: {
            type: 'string',
            description: 'City name or coordinates (lat,lng)'
          },
          units: {
            type: 'string',
            enum: ['metric', 'imperial', 'kelvin'],
            description: 'Temperature units'
          }
        },
        required: ['location']
      }
    };
  }

  /**
   * Send email function
   */
  static sendEmail(): FunctionDefinition {
    return {
      name: 'send_email',
      description: 'Send an email message',
      parameters: {
        type: 'object',
        properties: {
          to: {
            type: 'string',
            description: 'Recipient email address'
          },
          subject: {
            type: 'string',
            description: 'Email subject'
          },
          body: {
            type: 'string',
            description: 'Email body content'
          }
        },
        required: ['to', 'subject', 'body']
      }
    };
  }

  /**
   * Calendar scheduling function
   */
  static scheduleEvent(): FunctionDefinition {
    return {
      name: 'schedule_event',
      description: 'Schedule a calendar event',
      parameters: {
        type: 'object',
        properties: {
          title: {
            type: 'string',
            description: 'Event title'
          },
          start_time: {
            type: 'string',
            description: 'Start time in ISO format'
          },
          end_time: {
            type: 'string',
            description: 'End time in ISO format'
          },
          attendees: {
            type: 'string',
            description: 'Comma-separated list of attendee emails'
          },
          description: {
            type: 'string',
            description: 'Event description'
          }
        },
        required: ['title', 'start_time', 'end_time']
      }
    };
  }

  /**
   * Database query function
   */
  static queryDatabase(): FunctionDefinition {
    return {
      name: 'query_database',
      description: 'Execute a database query',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'SQL query to execute'
          },
          parameters: {
            type: 'string',
            description: 'JSON string of query parameters'
          }
        },
        required: ['query']
      }
    };
  }

  /**
   * Web search function
   */
  static webSearch(): FunctionDefinition {
    return {
      name: 'web_search',
      description: 'Search the web for information',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query'
          },
          num_results: {
            type: 'string',
            description: 'Number of results to return (default: 5)'
          }
        },
        required: ['query']
      }
    };
  }

  /**
   * Custom function builder
   */
  static custom(
    name: string,
    description: string,
    parameters: FunctionDefinition['parameters']
  ): FunctionDefinition {
    return { name, description, parameters };
  }
}

/**
 * Provider-specific configurations for different industries
 */
export class IndustryProviders {
  /**
   * Healthcare provider configurations
   */
  static healthcare = {
    claude: (): AnthropicConfig => ProviderFactory.createAnthropic({
      model: 'claude-3-5-sonnet-20241022',
      temperature: 0.2,
      system_prompt: `You are a healthcare virtual assistant. You must:
- Always recommend consulting with healthcare professionals for medical advice
- Never provide specific medical diagnoses
- Be accurate and careful with health-related information
- Respect patient privacy and confidentiality
- Use clear, non-technical language when possible`,
      functions: [
        FunctionDefinitions.scheduleEvent(),
        FunctionDefinitions.getCurrentTime()
      ]
    }),

    gpt4: (): OpenAIConfig => ProviderFactory.createOpenAI({
      model: 'gpt-4',
      temperature: 0.2,
      system_prompt: `You are a healthcare virtual assistant. You must:
- Always recommend consulting with healthcare professionals for medical advice
- Never provide specific medical diagnoses
- Be accurate and careful with health-related information
- Respect patient privacy and confidentiality
- Use clear, non-technical language when possible`,
      functions: [
        FunctionDefinitions.scheduleEvent(),
        FunctionDefinitions.getCurrentTime()
      ]
    })
  };

  /**
   * Financial services provider configurations
   */
  static financial = {
    claude: (): AnthropicConfig => ProviderFactory.createAnthropic({
      model: 'claude-3-5-sonnet-20241022',
      temperature: 0.1,
      system_prompt: `You are a financial services virtual assistant. You must:
- Be accurate with financial calculations and information
- Never provide specific investment advice
- Comply with financial regulations
- Protect sensitive financial information
- Recommend consulting with financial advisors for major decisions`,
      functions: [
        FunctionDefinitions.queryDatabase(),
        FunctionDefinitions.getCurrentTime(),
        FunctionDefinitions.sendEmail()
      ]
    }),

    gpt4: (): OpenAIConfig => ProviderFactory.createOpenAI({
      model: 'gpt-4',
      temperature: 0.1,
      system_prompt: `You are a financial services virtual assistant. You must:
- Be accurate with financial calculations and information
- Never provide specific investment advice
- Comply with financial regulations
- Protect sensitive financial information
- Recommend consulting with financial advisors for major decisions`,
      functions: [
        FunctionDefinitions.queryDatabase(),
        FunctionDefinitions.getCurrentTime(),
        FunctionDefinitions.sendEmail()
      ]
    })
  };

  /**
   * Customer service provider configurations
   */
  static customerService = {
    gpt4: (): OpenAIConfig => ProviderFactory.createOpenAI({
      model: 'gpt-4',
      temperature: 0.3,
      system_prompt: `You are a customer service representative. You should:
- Be polite, helpful, and professional
- Focus on solving customer problems
- Escalate complex issues to human agents when appropriate
- Keep responses concise and clear
- Show empathy for customer concerns`,
      functions: [
        FunctionDefinitions.queryDatabase(),
        FunctionDefinitions.sendEmail(),
        FunctionDefinitions.scheduleEvent()
      ]
    }),

    deepgram: (): DeepgramLLMConfig => ProviderFactory.createDeepgram({
      model: 'hermes-2-pro-mistral-7b',
      temperature: 0.3,
      system_prompt: `You are a customer service representative. You should:
- Be polite, helpful, and professional
- Focus on solving customer problems
- Escalate complex issues to human agents when appropriate
- Keep responses concise and clear
- Show empathy for customer concerns`,
      functions: [
        FunctionDefinitions.queryDatabase(),
        FunctionDefinitions.sendEmail()
      ]
    })
  };

  /**
   * Education provider configurations
   */
  static education = {
    claude: (): AnthropicConfig => ProviderFactory.createAnthropic({
      model: 'claude-3-5-sonnet-20241022',
      temperature: 0.7,
      system_prompt: `You are an educational assistant. You should:
- Encourage learning and curiosity
- Provide clear explanations adapted to the student's level
- Use examples and analogies to aid understanding
- Be patient and supportive
- Encourage critical thinking`,
      functions: [
        FunctionDefinitions.webSearch(),
        FunctionDefinitions.scheduleEvent(),
        FunctionDefinitions.getCurrentTime()
      ]
    }),

    gpt4: (): OpenAIConfig => ProviderFactory.createOpenAI({
      model: 'gpt-4',
      temperature: 0.7,
      system_prompt: `You are an educational assistant. You should:
- Encourage learning and curiosity
- Provide clear explanations adapted to the student's level
- Use examples and analogies to aid understanding
- Be patient and supportive
- Encourage critical thinking`,
      functions: [
        FunctionDefinitions.webSearch(),
        FunctionDefinitions.scheduleEvent(),
        FunctionDefinitions.getCurrentTime()
      ]
    })
  };
}

/**
 * Provider availability checker
 */
export class ProviderChecker {
  /**
   * Check if provider API keys are available
   */
  static checkAvailability(): {
    openai: boolean;
    anthropic: boolean;
    deepgram: boolean;
  } {
    return {
      openai: !!process.env.OPENAI_API_KEY,
      anthropic: !!process.env.ANTHROPIC_API_KEY,
      deepgram: !!process.env.DEEPGRAM_API_KEY
    };
  }

  /**
   * Get the first available provider
   */
  static getFirstAvailable(): LLMProvider | null {
    const availability = this.checkAvailability();
    
    if (availability.openai) return 'openai';
    if (availability.anthropic) return 'anthropic';
    if (availability.deepgram) return 'deepgram';
    
    return null;
  }

  /**
   * Validate provider configuration
   */
  static validateProvider(config: ProviderLLMConfig): boolean {
    const availability = this.checkAvailability();

    switch (config.provider) {
      case 'openai':
        return availability.openai || !!(config as OpenAIConfig).api_key;
      case 'anthropic':
        return availability.anthropic || !!(config as AnthropicConfig).api_key;
      case 'deepgram':
        return availability.deepgram;
      default:
        return false;
    }
  }
}
