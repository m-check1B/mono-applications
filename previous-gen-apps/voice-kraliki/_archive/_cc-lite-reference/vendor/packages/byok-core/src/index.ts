/**
 * @stack-2025/byok-core
 * Bring Your Own Keys implementation for Stack 2025
 * 
 * This package provides secure API key management for all Stack 2025 applications
 * with support for multiple providers, encryption, validation, and fallback chains.
 */

// Export all types
export * from './types';

// Export services
export { BYOKManager } from './services/byok-manager';
export { EncryptionService } from './services/encryption.service';
export { ValidationService } from './services/validation.service';
export { AuditService } from './services/audit.service';
export { FallbackService } from './services/fallback.service';

// Export factory function for easy initialization
import { BYOKConfig, BYOKManager } from './types';

/**
 * Create a new BYOK manager instance
 */
export function createBYOKManager(config: BYOKConfig): BYOKManager {
  return new BYOKManager(config);
}

// Export default configuration
export const defaultBYOKConfig: Partial<BYOKConfig> = {
  cacheEnabled: true,
  cacheTTL: 3600, // 1 hour
  validationInterval: 86400, // 24 hours
  auditingEnabled: true,
  fallbackEnabled: true,
  providers: [
    {
      provider: 'openai',
      timeout: 30000,
      retries: 3
    },
    {
      provider: 'anthropic',
      timeout: 30000,
      retries: 3
    },
    {
      provider: 'google-vertex',
      timeout: 30000,
      retries: 3
    },
    {
      provider: 'deepgram',
      timeout: 30000,
      retries: 3
    },
    {
      provider: 'twilio',
      timeout: 30000,
      retries: 3
    },
    {
      provider: 'openrouter',
      timeout: 30000,
      retries: 3
    }
  ]
};