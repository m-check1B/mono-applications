/**
 * @stack-2025/byok-core Type Definitions
 * Comprehensive type system for BYOK functionality
 */

import { z } from 'zod';

// Provider Types
export enum BYOKProvider {
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  GOOGLE_VERTEX = 'google-vertex',
  GOOGLE_GEMINI = 'google-gemini',
  DEEPGRAM = 'deepgram',
  ELEVENLABS = 'elevenlabs',
  TWILIO = 'twilio',
  TELNYX = 'telnyx',
  OPENROUTER = 'openrouter',
  CUSTOM = 'custom'
}

// Key Status
export enum KeyStatus {
  ACTIVE = 'active',
  INVALID = 'invalid',
  EXPIRED = 'expired',
  RATE_LIMITED = 'rate-limited',
  REVOKED = 'revoked'
}

// Subscription Tiers
export enum SubscriptionTier {
  MINI = 'mini',
  STANDARD = 'standard',
  PRO = 'pro',
  CORPORATE = 'corporate'
}

// BYOK Key Schema
export const BYOKKeySchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  provider: z.nativeEnum(BYOKProvider),
  keyName: z.string().min(1).max(100),
  encryptedKey: z.string(),
  keyHash: z.string(),
  status: z.nativeEnum(KeyStatus),
  lastValidated: z.date().nullable(),
  validationScore: z.number().min(0).max(100).nullable(),
  expiresAt: z.date().nullable(),
  metadata: z.record(z.any()).optional(),
  createdAt: z.date(),
  updatedAt: z.date()
});

export type BYOKKey = z.infer<typeof BYOKKeySchema>;

// Key Validation Result
export interface KeyValidationResult {
  isValid: boolean;
  status: KeyStatus;
  score: number;
  message?: string;
  capabilities?: string[];
  limits?: {
    rateLimit?: number;
    quotaRemaining?: number;
    expiresAt?: Date;
  };
}

// Usage Tracking
export interface BYOKUsage {
  id: string;
  keyId: string;
  userId: string;
  provider: BYOKProvider;
  operation: string;
  success: boolean;
  tokensUsed?: number;
  cost?: number;
  errorMessage?: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

// Fallback Chain
export interface FallbackChain {
  id: string;
  userId: string;
  provider: BYOKProvider;
  primaryKeyId: string;
  fallbackKeyIds: string[];
  strategy: 'sequential' | 'load-balance' | 'cost-optimize';
  enabled: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Audit Log
export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  resourceId: string;
  ipAddress?: string;
  userAgent?: string;
  success: boolean;
  errorMessage?: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

// Provider Configuration
export interface ProviderConfig {
  provider: BYOKProvider;
  endpoint?: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
  timeout?: number;
  retries?: number;
  customHeaders?: Record<string, string>;
}

// BYOK Manager Configuration
export interface BYOKConfig {
  encryptionKey: string;
  redisUrl?: string;
  cacheEnabled?: boolean;
  cacheTTL?: number;
  validationInterval?: number;
  auditingEnabled?: boolean;
  fallbackEnabled?: boolean;
  providers?: ProviderConfig[];
}

// Create Key Request
export const CreateKeyRequestSchema = z.object({
  provider: z.nativeEnum(BYOKProvider),
  keyName: z.string().min(1).max(100),
  apiKey: z.string().min(1),
  expiresAt: z.date().optional(),
  metadata: z.record(z.any()).optional()
});

export type CreateKeyRequest = z.infer<typeof CreateKeyRequestSchema>;

// Update Key Request
export const UpdateKeyRequestSchema = z.object({
  keyName: z.string().min(1).max(100).optional(),
  apiKey: z.string().min(1).optional(),
  expiresAt: z.date().optional(),
  metadata: z.record(z.any()).optional()
});

export type UpdateKeyRequest = z.infer<typeof UpdateKeyRequestSchema>;

// Provider-Specific Validations
export interface OpenAIValidation {
  models: string[];
  organization?: string;
  rateLimit: number;
  quotaRemaining?: number;
}

export interface DeepgramValidation {
  voices: string[];
  projects: string[];
  balance: number;
  usageLimit?: number;
}

export interface TwilioValidation {
  accountSid: string;
  phoneNumbers: string[];
  balance: number;
  capabilities: string[];
}

// Error Types
export class BYOKError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: any
  ) {
    super(message);
    this.name = 'BYOKError';
  }
}

// Error Codes
export enum BYOKErrorCode {
  KEY_NOT_FOUND = 'KEY_NOT_FOUND',
  INVALID_KEY = 'INVALID_KEY',
  ENCRYPTION_ERROR = 'ENCRYPTION_ERROR',
  VALIDATION_FAILED = 'VALIDATION_FAILED',
  PROVIDER_ERROR = 'PROVIDER_ERROR',
  RATE_LIMITED = 'RATE_LIMITED',
  QUOTA_EXCEEDED = 'QUOTA_EXCEEDED',
  UNAUTHORIZED = 'UNAUTHORIZED',
  CONFIGURATION_ERROR = 'CONFIGURATION_ERROR'
}

// Cache Keys
export const CacheKeys = {
  key: (keyId: string) => `byok:key:${keyId}`,
  userKeys: (userId: string) => `byok:user:${userId}:keys`,
  validation: (keyId: string) => `byok:validation:${keyId}`,
  usage: (userId: string, date: string) => `byok:usage:${userId}:${date}`,
  fallback: (userId: string, provider: BYOKProvider) => `byok:fallback:${userId}:${provider}`
} as const;

// Metrics
export interface BYOKMetrics {
  totalKeys: number;
  activeKeys: number;
  invalidKeys: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  cacheHitRate: number;
  validationSuccessRate: number;
  providerBreakdown: Record<BYOKProvider, number>;
}

// Export all types
export type {
  KeyValidationResult,
  BYOKUsage,
  FallbackChain,
  AuditLog,
  ProviderConfig,
  BYOKConfig,
  OpenAIValidation,
  DeepgramValidation,
  TwilioValidation,
  BYOKMetrics
};