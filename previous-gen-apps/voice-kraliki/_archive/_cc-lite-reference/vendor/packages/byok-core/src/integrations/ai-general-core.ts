/**
 * @stack-2025/byok-core - AI General Core Integration
 * Integration with @stack-2025/ai-general-core for BYOK key management
 */

import { BYOKManager } from '../manager.js';
import { ProviderType, Environment, DecryptedKey } from '../types.js';

/**
 * BYOK-enabled AI configuration factory
 */
export class BYOKAIConfigFactory {
  private byokManager: BYOKManager;

  constructor(byokManager: BYOKManager) {
    this.byokManager = byokManager;
  }

  /**
   * Create AI providers configuration with BYOK keys
   */
  async createConfigWithBYOK(
    userId: string, 
    options: {
      fallbackToSystem?: boolean;
      preferredProviders?: ProviderType[];
      environment?: Environment;
    } = {}
  ) {
    const { fallbackToSystem = true, preferredProviders, environment = Environment.PRODUCTION } = options;
    
    const config = {
      providers: {} as any,
      defaultProvider: null as any,
      costThreshold: 1.0,
      cacheEnabled: true,
      cacheTTL: 3600
    };

    // Get providers to configure (either preferred or all available)
    const providersToCheck = preferredProviders || [
      ProviderType.OPENAI,
      ProviderType.ANTHROPIC,
      ProviderType.GOOGLE_VERTEX,
      ProviderType.GOOGLE_GEMINI,
      ProviderType.OPENROUTER
    ];

    let hasValidProvider = false;

    // Configure each provider with BYOK keys
    for (const provider of providersToCheck) {
      try {
        const key = await this.byokManager.getActiveKey(userId, provider, {
          environment,
          fallbackToSystem,
          validateKey: true
        });

        const providerConfig = this.createProviderConfig(provider, key);
        if (providerConfig) {
          config.providers[provider] = providerConfig;
          
          // Set first valid provider as default
          if (!hasValidProvider) {
            config.defaultProvider = provider;
            hasValidProvider = true;
          }
        }
      } catch (error) {
        console.warn(`Failed to configure ${provider} with BYOK:`, error);
        
        // Try system fallback if enabled
        if (fallbackToSystem) {
          try {
            const systemConfig = this.createSystemFallbackConfig(provider);
            if (systemConfig) {
              config.providers[provider] = systemConfig;
              
              if (!hasValidProvider) {
                config.defaultProvider = provider;
                hasValidProvider = true;
              }
            }
          } catch (fallbackError) {
            console.warn(`System fallback also failed for ${provider}:`, fallbackError);
          }
        }
      }
    }

    if (!hasValidProvider) {
      throw new Error('No valid AI providers configured with BYOK or system fallback');
    }

    return config;
  }

  /**
   * Create provider-specific configuration from BYOK key
   */
  private createProviderConfig(provider: ProviderType, key: DecryptedKey) {
    const baseConfig = {
      models: this.getDefaultModels(provider),
      enabled: true,
      rateLimits: {
        requestsPerMinute: 100,
        tokensPerMinute: 200000
      }
    };

    switch (provider) {
      case ProviderType.OPENAI:
        return {
          ...baseConfig,
          apiKey: key.keyData.apiKey,
          ...(key.keyData.organization && { organization: key.keyData.organization }),
          ...(key.keyData.project && { project: key.keyData.project })
        };

      case ProviderType.ANTHROPIC:
        return {
          ...baseConfig,
          apiKey: key.keyData.apiKey
        };

      case ProviderType.GOOGLE_VERTEX:
      case ProviderType.GOOGLE_GEMINI:
        return {
          ...baseConfig,
          apiKey: key.keyData.apiKey,
          ...(key.keyData.projectId && { projectId: key.keyData.projectId })
        };

      case ProviderType.OPENROUTER:
        return {
          ...baseConfig,
          apiKey: key.keyData.apiKey
        };

      default:
        return {
          ...baseConfig,
          apiKey: key.keyData.apiKey
        };
    }
  }

  /**
   * Create system fallback configuration
   */
  private createSystemFallbackConfig(provider: ProviderType) {
    // This would use environment variables as fallback
    const envVars = this.getEnvironmentVariables(provider);
    
    if (!envVars.apiKey) {
      return null;
    }

    return {
      ...envVars,
      models: this.getDefaultModels(provider),
      enabled: true,
      rateLimits: {
        requestsPerMinute: 50, // Lower limits for system keys
        tokensPerMinute: 100000
      },
      isSystemFallback: true
    };
  }

  /**
   * Get environment variables for provider
   */
  private getEnvironmentVariables(provider: ProviderType): any {
    switch (provider) {
      case ProviderType.OPENAI:
        return {
          apiKey: process.env.OPENAI_API_KEY,
          organization: process.env.OPENAI_ORGANIZATION,
          project: process.env.OPENAI_PROJECT
        };

      case ProviderType.ANTHROPIC:
        return {
          apiKey: process.env.ANTHROPIC_API_KEY
        };

      case ProviderType.GOOGLE_VERTEX:
        return {
          apiKey: process.env.GOOGLE_VERTEX_API_KEY,
          projectId: process.env.GOOGLE_PROJECT_ID
        };

      case ProviderType.GOOGLE_GEMINI:
        return {
          apiKey: process.env.GOOGLE_GEMINI_API_KEY,
          projectId: process.env.GOOGLE_PROJECT_ID
        };

      case ProviderType.OPENROUTER:
        return {
          apiKey: process.env.OPENROUTER_API_KEY
        };

      default:
        return { apiKey: null };
    }
  }

  /**
   * Get default models for provider
   */
  private getDefaultModels(provider: ProviderType) {
    const modelConfigs = {
      [ProviderType.OPENAI]: [
        {
          provider,
          model: 'gpt-4o-mini',
          maxTokens: 16384,
          temperature: 0.7,
          costPerToken: 0.00015,
          priority: 1
        },
        {
          provider,
          model: 'gpt-4o',
          maxTokens: 4096,
          temperature: 0.7,
          costPerToken: 0.005,
          priority: 2
        }
      ],
      [ProviderType.ANTHROPIC]: [
        {
          provider,
          model: 'claude-3-5-sonnet-20241022',
          maxTokens: 8192,
          temperature: 0.7,
          costPerToken: 0.003,
          priority: 1
        }
      ],
      [ProviderType.GOOGLE_VERTEX]: [
        {
          provider,
          model: 'gemini-1.5-flash',
          maxTokens: 8192,
          temperature: 0.7,
          costPerToken: 0.000075,
          priority: 1
        }
      ],
      [ProviderType.GOOGLE_GEMINI]: [
        {
          provider,
          model: 'gemini-1.5-flash',
          maxTokens: 8192,
          temperature: 0.7,
          costPerToken: 0.000075,
          priority: 1
        }
      ],
      [ProviderType.OPENROUTER]: [
        {
          provider,
          model: 'openai/gpt-4o-mini',
          maxTokens: 16384,
          temperature: 0.7,
          costPerToken: 0.00015,
          priority: 1
        }
      ]
    };

    return modelConfigs[provider] || [];
  }

  /**
   * Monitor key usage and update analytics
   */
  async recordUsage(
    userId: string,
    provider: ProviderType,
    operation: string,
    tokens: number,
    cost: number,
    success: boolean,
    error?: string
  ) {
    try {
      // This would record usage in the BYOK system
      console.log(`Recording BYOK usage: ${provider} ${operation} - ${tokens} tokens, $${cost}`);
    } catch (error) {
      console.warn('Failed to record BYOK usage:', error);
    }
  }
}

/**
 * Middleware for automatic BYOK integration
 */
export class BYOKAIMiddleware {
  private configFactory: BYOKAIConfigFactory;

  constructor(byokManager: BYOKManager) {
    this.configFactory = new BYOKAIConfigFactory(byokManager);
  }

  /**
   * Middleware to inject BYOK configuration
   */
  async middleware(req: any, res: any, next: any) {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return next();
      }

      // Create BYOK-enabled AI config
      const aiConfig = await this.configFactory.createConfigWithBYOK(userId, {
        fallbackToSystem: true,
        environment: req.environment || Environment.PRODUCTION
      });

      // Attach to request
      req.aiConfig = aiConfig;
      req.byokEnabled = true;

      next();
    } catch (error) {
      console.warn('BYOK middleware failed:', error);
      // Continue without BYOK if it fails
      req.byokEnabled = false;
      next();
    }
  }

  /**
   * Usage tracking middleware
   */
  usageMiddleware(req: any, res: any, next: any) {
    if (!req.byokEnabled || !req.user?.id) {
      return next();
    }

    // Wrap response to track usage
    const originalSend = res.send;
    const userId = req.user.id;

    res.send = function(data: any) {
      // Extract usage information from response
      try {
        const usage = extractUsageFromResponse(data);
        if (usage) {
          // Record usage asynchronously
          recordUsageAsync(userId, usage);
        }
      } catch (error) {
        console.warn('Failed to extract usage for BYOK tracking:', error);
      }

      return originalSend.call(this, data);
    };

    next();
  }
}

// Helper functions
function extractUsageFromResponse(data: any) {
  // Extract usage information based on response format
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data);
    } catch {
      return null;
    }
  }

  if (data && data.usage) {
    return {
      tokens: data.usage.total_tokens || 0,
      cost: data.usage.cost || 0,
      model: data.model || 'unknown',
      provider: data.provider || 'unknown'
    };
  }

  return null;
}

async function recordUsageAsync(userId: string, usage: any) {
  try {
    // This would record the usage in the BYOK system
    console.log(`Recording async usage for ${userId}:`, usage);
  } catch (error) {
    console.warn('Async usage recording failed:', error);
  }
}

/**
 * Factory function for BYOK AI integration
 */
export function createBYOKAIIntegration(byokManager: BYOKManager) {
  return {
    configFactory: new BYOKAIConfigFactory(byokManager),
    middleware: new BYOKAIMiddleware(byokManager)
  };
}