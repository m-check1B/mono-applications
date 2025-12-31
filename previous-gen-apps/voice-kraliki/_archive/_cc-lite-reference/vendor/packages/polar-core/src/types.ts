import { z } from 'zod'

// Stack 2025 Unified BYOK Subscription tiers
export enum SubscriptionTier {
  MINI = 'mini',
  STANDARD = 'standard', 
  PRO = 'pro',
  CORPORATE = 'corporate'
}

// Payment status for Polar
export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  SUCCEEDED = 'succeeded',
  FAILED = 'failed',
  REFUNDED = 'refunded',
  CANCELED = 'canceled'
}

// Billing interval
export enum BillingInterval {
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
  ONE_TIME = 'one_time'
}

// Polar Customer data
export interface PolarCustomer {
  id: string
  customerId: string
  email: string
  name?: string
  avatar_url?: string
  metadata?: Record<string, any>
  createdAt: Date
  updatedAt: Date
}

// Polar Subscription data
export interface PolarSubscription {
  id: string
  subscriptionId: string
  customerId: string
  tier: SubscriptionTier
  status: 'incomplete' | 'incomplete_expired' | 'trialing' | 'active' | 'past_due' | 'canceled' | 'unpaid'
  currentPeriodStart: Date
  currentPeriodEnd: Date
  cancelAtPeriodEnd: boolean
  trialStart?: Date
  trialEnd?: Date
  metadata?: Record<string, any>
  createdAt: Date
  updatedAt: Date
}

// Polar Payment data
export interface PolarPayment {
  id: string
  paymentId: string
  customerId: string
  amount: number
  currency: string
  status: PaymentStatus
  description?: string
  metadata?: Record<string, any>
  createdAt: Date
}

// Polar Order data
export interface PolarOrder {
  id: string
  orderId: string
  customerId: string
  subscriptionId?: string
  amount: number
  currency: string
  status: string
  billing_reason?: string
  metadata?: Record<string, any>
  createdAt: Date
}

// Polar Webhook event
export interface PolarWebhookEvent {
  id: string
  type: string
  data: any
  created_at: string
}

// BYOK Pricing configuration for Stack 2025 with Polar
export interface BYOKPricingConfig {
  tier: SubscriptionTier
  name: string
  description: string
  targetAudience: string
  pricing: {
    monthly: number
    yearly: number
    yearlyDiscount?: number // Percentage discount for yearly
  }
  polarProductIds: {
    monthly: string
    yearly: string
  }
  // Feature access across all Stack 2025 apps
  appAccess: {
    maxApps: number // Number of apps user can enable
    availableApps: string[] // List of available app IDs
  }
  // Cross-app feature limits
  featureLimits: {
    // CC-Light limits
    ccLight?: {
      maxAgents: number
      maxCallsPerMonth: number
    }
    // CC-Gym limits  
    ccGym?: {
      maxTrainingScenarios: number
      maxTrainingHoursPerMonth: number
    }
    // Invoice-Gym limits
    invoiceGym?: {
      maxInvoicesPerMonth: number
    }
    // Productivity-Hub limits
    productivityHub?: {
      maxAiRequestsPerMonth: number
    }
    // Script-Factory limits
    scriptFactory?: {
      maxScriptGenerationsPerMonth: number
    }
    // Global limits
    dataRetentionDays: number
    supportLevel: 'community' | 'email' | 'priority' | 'dedicated'
    analyticsLevel: 'basic' | 'standard' | 'advanced' | 'enterprise'
  }
  // BYOK requirements
  byokRequirements: {
    requiredProviders: ApiProvider[]
    optionalProviders: ApiProvider[]
    customEndpointSupport: boolean
    telephonyRequired: boolean
  }
}

// Checkout session options for Polar
export interface CheckoutSessionOptions {
  customerId?: string
  email?: string
  productId: string
  quantity?: number
  successUrl: string
  cancelUrl?: string
  metadata?: Record<string, any>
  allowPromotionCodes?: boolean
  trialDays?: number
  discountId?: string
}

// Customer portal options for Polar
export interface CustomerPortalOptions {
  customerId: string
  returnUrl: string
}

// Refund options for Polar
export interface RefundOptions {
  paymentId: string
  amount?: number // Partial refund if specified
  reason?: 'duplicate' | 'fraudulent' | 'requested_by_customer'
  metadata?: Record<string, any>
}

// API Provider types for BYOK
export enum ApiProvider {
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  GOOGLE_VERTEX = 'google_vertex',
  DEEPGRAM = 'deepgram', 
  TWILIO = 'twilio',
  TELNYX = 'telnyx',
  CUSTOM_ENDPOINT = 'custom_endpoint'
}

// BYOK Feature usage tracking
export interface FeatureUsageData {
  userId: string
  subscriptionTier: SubscriptionTier
  billingPeriodStart: Date
  billingPeriodEnd: Date
  appUsage: {
    [appId: string]: {
      // Generic feature counters
      requests: number
      activeUsers: number
      storageUsed: number
      // App-specific counters
      customMetrics?: Record<string, number>
    }
  }
  totalFeatureUsage: {
    callsHandled: number
    trainingHours: number
    invoicesGenerated: number
    aiRequestsMade: number
    scriptsGenerated: number
  }
}

// BYOK Subscription with app access control
export interface BYOKSubscription extends PolarSubscription {
  enabledApps: string[] // List of app IDs user has access to
  featureLimits: BYOKPricingConfig['featureLimits']
  currentUsage: FeatureUsageData
  apiKeyStatus: {
    [provider: string]: {
      configured: boolean
      lastValidated: Date
      isValid: boolean
    }
  }
}

// Polar Product for catalog
export interface PolarProduct {
  id: string
  name: string
  description?: string
  type: 'individual' | 'business'
  organization_id: string
  is_recurring: boolean
  is_archived: boolean
  prices: PolarPrice[]
  benefits: PolarBenefit[]
  medias: PolarMedia[]
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

// Polar Price for products
export interface PolarPrice {
  id: string
  product_id: string
  type: 'one_time' | 'recurring'
  recurring_interval?: 'month' | 'year'
  amount_cents: number
  currency: string
  is_archived: boolean
  created_at: string
  updated_at: string
}

// Polar Benefit for products
export interface PolarBenefit {
  id: string
  type: 'custom' | 'articles' | 'ads' | 'discord' | 'github_repository'
  description: string
  selectable: boolean
  deletable: boolean
  organization_id?: string
  created_at: string
  updated_at: string
}

// Polar Media for products
export interface PolarMedia {
  id: string
  organization_id: string
  name: string
  path: string
  mime_type: string
  size: number
  storage_version?: string
  checksum_etag?: string
  checksum_sha256_base64?: string
  checksum_sha256_hex?: string
  last_modified_at?: string
  version?: string
  is_uploaded: boolean
  created_at: string
  updated_at: string
}