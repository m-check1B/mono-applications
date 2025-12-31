/**
 * @stack-2025/byok-core Validation Service
 * Provider-specific API key validation
 */

import { OpenAI } from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { Twilio } from 'twilio';
import {
  BYOKProvider,
  KeyStatus,
  KeyValidationResult,
  OpenAIValidation,
  DeepgramValidation,
  TwilioValidation,
  BYOKError,
  BYOKErrorCode
} from '../types';

export class ValidationService {
  /**
   * Validate an API key with its provider
   */
  async validateKey(
    provider: BYOKProvider,
    apiKey: string
  ): Promise<KeyValidationResult> {
    try {
      switch (provider) {
        case BYOKProvider.OPENAI:
          return await this.validateOpenAI(apiKey);
        case BYOKProvider.ANTHROPIC:
          return await this.validateAnthropic(apiKey);
        case BYOKProvider.GOOGLE_VERTEX:
        case BYOKProvider.GOOGLE_GEMINI:
          return await this.validateGoogle(apiKey);
        case BYOKProvider.DEEPGRAM:
          return await this.validateDeepgram(apiKey);
        case BYOKProvider.ELEVENLABS:
          return await this.validateElevenLabs(apiKey);
        case BYOKProvider.TWILIO:
          return await this.validateTwilio(apiKey);
        case BYOKProvider.TELNYX:
          return await this.validateTelnyx(apiKey);
        case BYOKProvider.OPENROUTER:
          return await this.validateOpenRouter(apiKey);
        case BYOKProvider.CUSTOM:
          return await this.validateCustom(apiKey);
        default:
          throw new BYOKError(
            `Unsupported provider: ${provider}`,
            BYOKErrorCode.PROVIDER_ERROR,
            400
          );
      }
    } catch (error) {
      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: error.message || 'Validation failed'
      };
    }
  }

  /**
   * Validate OpenAI API key
   */
  private async validateOpenAI(apiKey: string): Promise<KeyValidationResult> {
    try {
      const openai = new OpenAI({ apiKey });
      
      // Test with a simple models list request
      const models = await openai.models.list();
      const modelList = models.data.map(m => m.id);

      // Check for key capabilities
      const hasGPT4 = modelList.some(m => m.includes('gpt-4'));
      const hasGPT35 = modelList.some(m => m.includes('gpt-3.5'));
      const hasDallE = modelList.some(m => m.includes('dall-e'));
      const hasWhisper = modelList.some(m => m.includes('whisper'));

      // Calculate score based on capabilities
      let score = 50; // Base score for valid key
      if (hasGPT4) score += 20;
      if (hasGPT35) score += 10;
      if (hasDallE) score += 10;
      if (hasWhisper) score += 10;

      return {
        isValid: true,
        status: KeyStatus.ACTIVE,
        score,
        capabilities: modelList,
        limits: {
          rateLimit: 10000, // Default rate limit
        }
      };
    } catch (error: any) {
      if (error?.status === 401) {
        return {
          isValid: false,
          status: KeyStatus.INVALID,
          score: 0,
          message: 'Invalid API key'
        };
      }
      if (error?.status === 429) {
        return {
          isValid: true,
          status: KeyStatus.RATE_LIMITED,
          score: 25,
          message: 'Rate limited but valid'
        };
      }
      throw error;
    }
  }

  /**
   * Validate Anthropic API key
   */
  private async validateAnthropic(apiKey: string): Promise<KeyValidationResult> {
    try {
      const anthropic = new Anthropic({ apiKey });
      
      // Test with a simple completion
      const response = await anthropic.messages.create({
        model: 'claude-3-haiku-20240307',
        max_tokens: 1,
        messages: [{ role: 'user', content: 'Hi' }]
      });

      return {
        isValid: true,
        status: KeyStatus.ACTIVE,
        score: 90,
        capabilities: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
        limits: {
          rateLimit: 1000
        }
      };
    } catch (error: any) {
      if (error?.status === 401) {
        return {
          isValid: false,
          status: KeyStatus.INVALID,
          score: 0,
          message: 'Invalid API key'
        };
      }
      throw error;
    }
  }

  /**
   * Validate Google API key
   */
  private async validateGoogle(apiKey: string): Promise<KeyValidationResult> {
    try {
      // Simple validation for Google Vertex AI / Gemini
      const response = await fetch(
        'https://generativelanguage.googleapis.com/v1beta/models?key=' + apiKey
      );

      if (response.ok) {
        const data = await response.json();
        return {
          isValid: true,
          status: KeyStatus.ACTIVE,
          score: 85,
          capabilities: data.models?.map((m: any) => m.name) || ['gemini-pro'],
          limits: {
            rateLimit: 60
          }
        };
      }

      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: 'Invalid API key'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Validate Deepgram API key
   */
  private async validateDeepgram(apiKey: string): Promise<KeyValidationResult> {
    try {
      const response = await fetch('https://api.deepgram.com/v1/projects', {
        headers: {
          'Authorization': `Token ${apiKey}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isValid: true,
          status: KeyStatus.ACTIVE,
          score: 80,
          capabilities: ['aura-voices', 'transcription', 'translation'],
          limits: {
            rateLimit: 100
          }
        };
      }

      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: 'Invalid API key'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Validate ElevenLabs API key
   */
  private async validateElevenLabs(apiKey: string): Promise<KeyValidationResult> {
    try {
      const response = await fetch('https://api.elevenlabs.io/v1/user', {
        headers: {
          'xi-api-key': apiKey
        }
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isValid: true,
          status: KeyStatus.ACTIVE,
          score: 75,
          capabilities: ['text-to-speech', 'voice-cloning'],
          limits: {
            quotaRemaining: data.subscription?.character_limit
          }
        };
      }

      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: 'Invalid API key'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Validate Twilio credentials
   */
  private async validateTwilio(apiKey: string): Promise<KeyValidationResult> {
    try {
      // Twilio uses Account SID and Auth Token
      // Format: accountSid:authToken
      const [accountSid, authToken] = apiKey.split(':');
      
      if (!accountSid || !authToken) {
        return {
          isValid: false,
          status: KeyStatus.INVALID,
          score: 0,
          message: 'Invalid format. Use accountSid:authToken'
        };
      }

      const client = new Twilio(accountSid, authToken);
      const account = await client.api.accounts(accountSid).fetch();

      return {
        isValid: true,
        status: KeyStatus.ACTIVE,
        score: 85,
        capabilities: ['voice', 'sms', 'whatsapp'],
        limits: {
          rateLimit: 100
        }
      };
    } catch (error: any) {
      if (error?.status === 401) {
        return {
          isValid: false,
          status: KeyStatus.INVALID,
          score: 0,
          message: 'Invalid credentials'
        };
      }
      throw error;
    }
  }

  /**
   * Validate Telnyx API key
   */
  private async validateTelnyx(apiKey: string): Promise<KeyValidationResult> {
    try {
      const response = await fetch('https://api.telnyx.com/v2/api_keys', {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (response.ok) {
        return {
          isValid: true,
          status: KeyStatus.ACTIVE,
          score: 80,
          capabilities: ['voice', 'sms', 'fax'],
          limits: {
            rateLimit: 100
          }
        };
      }

      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: 'Invalid API key'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Validate OpenRouter API key
   */
  private async validateOpenRouter(apiKey: string): Promise<KeyValidationResult> {
    try {
      const response = await fetch('https://openrouter.ai/api/v1/auth/key', {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isValid: true,
          status: KeyStatus.ACTIVE,
          score: 95, // High score for OpenRouter as it provides access to many models
          capabilities: ['multi-model', 'gpt-4', 'claude', 'gemini', 'llama'],
          limits: {
            quotaRemaining: data.data?.usage?.limit,
            rateLimit: data.data?.rate_limit || 100
          }
        };
      }

      return {
        isValid: false,
        status: KeyStatus.INVALID,
        score: 0,
        message: 'Invalid API key'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Validate custom provider API key
   */
  private async validateCustom(apiKey: string): Promise<KeyValidationResult> {
    // For custom providers, we just check if the key is not empty
    // Actual validation would be provider-specific
    if (apiKey && apiKey.length > 0) {
      return {
        isValid: true,
        status: KeyStatus.ACTIVE,
        score: 50,
        capabilities: ['custom'],
        message: 'Custom provider - validation not implemented'
      };
    }

    return {
      isValid: false,
      status: KeyStatus.INVALID,
      score: 0,
      message: 'Invalid API key'
    };
  }

  /**
   * Batch validate multiple keys
   */
  async validateBatch(
    keys: Array<{ provider: BYOKProvider; apiKey: string }>
  ): Promise<Map<string, KeyValidationResult>> {
    const results = new Map<string, KeyValidationResult>();

    await Promise.all(
      keys.map(async ({ provider, apiKey }) => {
        const result = await this.validateKey(provider, apiKey);
        results.set(`${provider}:${apiKey.substring(0, 8)}...`, result);
      })
    );

    return results;
  }
}