/**
 * @stack-2025/byok-core - Type Definitions
 * Core types for the Bring Your Own Keys system
 */

import { z } from 'zod';

/**
 * Supported provider types
 */
export enum ProviderType {
  // LLM Providers
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  GOOGLE_VERTEX = 'google_vertex',
  GOOGLE_GEMINI = 'google_gemini',
  OPENROUTER = 'openrouter',
  HUGGINGFACE = 'huggingface',
  
  // Voice & Speech
  DEEPGRAM = 'deepgram',
  ELEVENLABS = 'elevenlabs',
  
  // Telephony
  TWILIO = 'twilio',
  TELNYX = 'telnyx'
}

/**
 * Key status enum
 */
export enum KeyStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  INVALID = 'invalid',
  EXPIRED = 'expired',
  RATE_LIMITED = 'rate_limited',
  SUSPENDED = 'suspended'
}

/**
 * Environment types
 */
export enum Environment {
  DEVELOPMENT = 'development',
  STAGING = 'staging',
  PRODUCTION = 'production'
}

/**
 * Event types for audit logging
 */
export enum EventType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  VALIDATE = 'validate',
  USE = 'use',
  ROTATE = 'rotate',
  EXPIRE = 'expire'
}

/**
 * Base provider key data interface
 */
export interface BaseKeyData {
  [key: string]: string | number | boolean | undefined;
}

/**
 * OpenAI key configuration
 */
export interface OpenAIKeyData extends BaseKeyData {
  apiKey: string;
  organization?: string;
  project?: string;
}

/**
 * Anthropic key configuration
 */
export interface AnthropicKeyData extends BaseKeyData {
  apiKey: string;
}

/**
 * Google key configuration
 */
export interface GoogleKeyData extends BaseKeyData {
  apiKey?: string;
  projectId?: string;
  keyFile?: string; // Path to service account JSON
  credentials?: Record<string, any>; // Service account JSON content
}

/**
 * Deepgram key configuration
 */
export interface DeepgramKeyData extends BaseKeyData {
  apiKey: string;
  projectId?: string;
}

/**
 * Twilio key configuration
 */
export interface TwilioKeyData extends BaseKeyData {
  accountSid: string;
  authToken: string;
  apiKeySid?: string;
  apiKeySecret?: string;
}

/**
 * Union of all key data types
 */
export type ProviderKeyData = 
  | OpenAIKeyData 
  | AnthropicKeyData 
  | GoogleKeyData 
  | DeepgramKeyData 
  | TwilioKeyData 
  | BaseKeyData;

/**
 * Key configuration schema
 */
export const KeyConfigSchema = z.object({
  userId: z.string(),
  organizationId: z.string().optional(),
  provider: z.nativeEnum(ProviderType),
  keyData: z.record(z.any()),
  alias: z.string().optional(),
  description: z.string().optional(),
  environment: z.nativeEnum(Environment).default(Environment.PRODUCTION),
  metadata: z.record(z.any()).default({}),
  capabilities: z.array(z.string()).default([]),
  expiresAt: z.date().optional(),
  rateLimit: z.record(z.any()).optional(),
  quotaConfig: z.record(z.any()).optional()
});

export type KeyConfig = z.infer<typeof KeyConfigSchema>;

/**
 * Stored key information (encrypted)
 */
export interface StoredKey {
  id: string;
  userId: string;
  organizationId?: string;
  provider: ProviderType;
  providerService?: string;
  alias?: string;
  description?: string;
  environment: Environment;
  encryptedKeyData: string;
  encryptionNonce: string;
  keyHash: string;
  metadata: Record<string, any>;
  capabilities: string[];
  status: KeyStatus;
  lastValidatedAt?: Date;
  validationError?: string;
  healthScore: number;
  usageTracking: boolean;
  rateLimitConfig: Record<string, any>;
  quotaConfig: Record<string, any>;
  expiresAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Decrypted key for usage
 */
export interface DecryptedKey {
  id: string;
  provider: ProviderType;
  keyData: ProviderKeyData;
  metadata: Record<string, any>;
  capabilities: string[];
  environment: Environment;
  healthScore: number;
  expiresAt?: Date;
}

/**
 * Key validation result
 */
export interface KeyValidationResult {
  keyId: string;
  isValid: boolean;
  errorMessage?: string;
  errorCode?: string;
  testResults: Record<string, any>;
  responseTime: number;
  testsRun: string[];
  providerResponse?: Record<string, any>;
  healthScore: number;
}

/**
 * Usage statistics
 */
export interface KeyUsageStats {
  keyId: string;
  timeframe: {
    start: Date;
    end: Date;
  };
  requests: number;
  tokens: number;
  cost: number;
  successRate: number;
  averageResponseTime: number;
  errors: Array<{
    code: string;
    count: number;
  }>;
  breakdown: {
    byDay: Array<{
      date: string;
      requests: number;
      tokens: number;
      cost: number;
    }>;
    byOperation: Record<string, {
      requests: number;
      tokens: number;
      cost: number;
    }>;
    byModel: Record<string, {
      requests: number;
      tokens: number;
      cost: number;
    }>;
  };
}

/**
 * Fallback chain configuration
 */
export interface FallbackChain {
  id: string;
  userId: string;
  provider: ProviderType;
  environment: Environment;
  chainName?: string;
  primaryKeyId?: string;
  fallbackSequence: string[]; // Array of key IDs in order
  useSystemFallback: boolean;
  systemFallbackPriority: number;
  maxRetries: number;
  retryDelayMs: number;
  circuitBreakerConfig: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Usage alert configuration
 */
export interface UsageAlert {
  id: string;
  userId: string;
  keyId?: string; // null means all keys
  alertName: string;
  alertType: 'cost' | 'requests' | 'tokens' | 'quota';
  thresholdValue: number;
  thresholdPeriod: 'daily' | 'weekly' | 'monthly';
  notificationChannels: Array<'email' | 'webhook' | 'in-app'>;
  isActive: boolean;
  lastTriggeredAt?: Date;
  triggerCount: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Audit log entry
 */
export interface AuditLogEntry {
  id: string;
  userId?: string;
  keyId?: string;
  eventType: EventType;
  eventAction: string;
  eventTimestamp: Date;
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
  requestId?: string;
  oldValues?: Record<string, any>;
  newValues?: Record<string, any>;
  success: boolean;
  errorMessage?: string;
  additionalData: Record<string, any>;
}

/**
 * Provider configuration template
 */
export interface ProviderConfig {
  id: string;
  providerType: ProviderType;
  providerService?: string;
  providerVersion?: string;
  keySchema: Record<string, any>; // JSON schema
  metadataSchema: Record<string, any>;
  capabilities: string[];
  validationConfig: Record<string, any>;
  testEndpoints: Array<{
    name: string;
    method: string;
    url: string;
    headers?: Record<string, string>;
    body?: Record<string, any>;
    expectedStatus: number;
    timeout: number;
  }>;
  rateLimits: Record<string, any>;
  description?: string;
  setupInstructions?: string;
  exampleConfig: Record<string, any>;
  isActive: boolean;
  isBeta: boolean;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * BYOK Manager configuration options
 */
export interface BYOKManagerOptions {
  encryptionKey: string;
  database: {
    connectionString?: string;
    client?: any; // Database client instance
  };
  cache?: {
    redis?: {
      url?: string;
      client?: any; // Redis client instance
    };
    ttl?: number;
  };
  validation?: {
    enabled?: boolean;
    parallelValidation?: boolean;
    timeout?: number;
  };
  audit?: {
    enabled?: boolean;
    retentionDays?: number;
  };
  fallback?: {
    enabled?: boolean;
    systemKeys?: Record<ProviderType, ProviderKeyData>;
  };
}

/**
 * Key retrieval options
 */
export interface KeyRetrievalOptions {
  environment?: Environment;
  fallbackToSystem?: boolean;
  validateKey?: boolean;
  cacheResult?: boolean;
  metadata?: boolean;
}

/**
 * Key listing options
 */
export interface KeyListOptions {
  provider?: ProviderType;
  environment?: Environment;
  status?: KeyStatus;
  limit?: number;
  offset?: number;
  sortBy?: 'created_at' | 'updated_at' | 'alias' | 'provider';
  sortOrder?: 'asc' | 'desc';
  includeExpired?: boolean;
}

/**
 * Key update options
 */
export interface KeyUpdateOptions {
  alias?: string;
  description?: string;
  metadata?: Record<string, any>;
  capabilities?: string[];
  rateLimitConfig?: Record<string, any>;
  quotaConfig?: Record<string, any>;
  expiresAt?: Date;
  status?: KeyStatus;
}

/**
 * Analytics query options
 */
export interface AnalyticsOptions {
  timeRange?: '1h' | '24h' | '7d' | '30d' | '90d' | 'custom';
  startDate?: Date;
  endDate?: Date;
  providers?: ProviderType[];
  environments?: Environment[];
  metrics?: Array<'requests' | 'tokens' | 'cost' | 'errors'>;
  groupBy?: 'hour' | 'day' | 'week' | 'month';
  includeSystemKeys?: boolean;
}

/**
 * Migration plan
 */
export interface MigrationPlan {
  from: 'environment' | 'file' | 'external';
  providers: ProviderType[];
  preserveExisting: boolean;
  dryRun: boolean;
  steps: Array<{
    provider: ProviderType;
    action: 'migrate' | 'skip' | 'manual';
    reason?: string;
    existingConfig?: ProviderKeyData;
    newKeyId?: string;
  }>;
  estimatedDuration: number; // in seconds
  warnings: string[];
  errors: string[];
}

/**
 * Error types
 */
export class BYOKError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'BYOKError';
  }
}

export class KeyNotFoundError extends BYOKError {
  constructor(keyId: string, provider?: ProviderType) {
    super(`Key not found: ${keyId}${provider ? ` for provider ${provider}` : ''}`, 'KEY_NOT_FOUND');
    this.name = 'KeyNotFoundError';
  }
}

export class KeyValidationError extends BYOKError {
  constructor(message: string, keyId: string, validationErrors: string[]) {
    super(message, 'KEY_VALIDATION_FAILED', { keyId, validationErrors });
    this.name = 'KeyValidationError';
  }
}

export class EncryptionError extends BYOKError {
  constructor(message: string, operation: 'encrypt' | 'decrypt') {
    super(message, 'ENCRYPTION_ERROR', { operation });
    this.name = 'EncryptionError';
  }
}

export class ProviderError extends BYOKError {
  constructor(message: string, provider: ProviderType, statusCode?: number) {
    super(message, 'PROVIDER_ERROR', { provider, statusCode });
    this.name = 'ProviderError';
  }
}

/**
 * Configuration validation schemas
 */
export const OpenAIKeyDataSchema = z.object({
  apiKey: z.string().regex(/^sk-[a-zA-Z0-9]{48}$/, 'Invalid OpenAI API key format'),
  organization: z.string().regex(/^org-[a-zA-Z0-9]{24}$/).optional(),
  project: z.string().regex(/^proj_[a-zA-Z0-9]{24}$/).optional()
});

export const AnthropicKeyDataSchema = z.object({
  apiKey: z.string().regex(/^sk-ant-[a-zA-Z0-9_-]+$/, 'Invalid Anthropic API key format')
});

export const GoogleKeyDataSchema = z.object({
  apiKey: z.string().optional(),
  projectId: z.string().optional(),
  keyFile: z.string().optional(),
  credentials: z.record(z.any()).optional()
}).refine(
  data => data.apiKey || data.keyFile || data.credentials,
  'Either apiKey, keyFile, or credentials must be provided'
);

export const DeepgramKeyDataSchema = z.object({
  apiKey: z.string().min(40, 'Deepgram API key must be at least 40 characters'),
  projectId: z.string().uuid().optional()
});

export const TwilioKeyDataSchema = z.object({
  accountSid: z.string().regex(/^AC[a-fA-F0-9]{32}$/, 'Invalid Twilio Account SID format'),
  authToken: z.string().min(32, 'Twilio Auth Token must be at least 32 characters'),
  apiKeySid: z.string().regex(/^SK[a-fA-F0-9]{32}$/).optional(),
  apiKeySecret: z.string().optional()
});

/**
 * Provider schema mapping
 */
export const PROVIDER_SCHEMAS: Record<ProviderType, z.ZodSchema<any>> = {
  [ProviderType.OPENAI]: OpenAIKeyDataSchema,
  [ProviderType.ANTHROPIC]: AnthropicKeyDataSchema,
  [ProviderType.GOOGLE_VERTEX]: GoogleKeyDataSchema,
  [ProviderType.GOOGLE_GEMINI]: GoogleKeyDataSchema,
  [ProviderType.DEEPGRAM]: DeepgramKeyDataSchema,
  [ProviderType.TWILIO]: TwilioKeyDataSchema,
  [ProviderType.TELNYX]: z.record(z.any()), // Generic schema for now
  [ProviderType.OPENROUTER]: OpenAIKeyDataSchema, // Same format as OpenAI
  [ProviderType.HUGGINGFACE]: z.record(z.any()),
  [ProviderType.ELEVENLABS]: z.record(z.any())
};

/**
 * Default capabilities per provider
 */
export const DEFAULT_CAPABILITIES: Record<ProviderType, string[]> = {
  [ProviderType.OPENAI]: ['chat', 'completion', 'embedding', 'image', 'audio', 'realtime'],
  [ProviderType.ANTHROPIC]: ['chat', 'completion'],
  [ProviderType.GOOGLE_VERTEX]: ['chat', 'completion', 'embedding', 'image'],
  [ProviderType.GOOGLE_GEMINI]: ['chat', 'completion', 'image', 'live'],
  [ProviderType.DEEPGRAM]: ['stt', 'tts', 'voice-agent', 'live'],
  [ProviderType.TWILIO]: ['voice', 'sms', 'whatsapp', 'video'],
  [ProviderType.TELNYX]: ['voice', 'sms'],
  [ProviderType.OPENROUTER]: ['chat', 'completion'],
  [ProviderType.HUGGINGFACE]: ['chat', 'completion', 'embedding'],
  [ProviderType.ELEVENLABS]: ['tts', 'voice-cloning']
};