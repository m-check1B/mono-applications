import { z } from 'zod'
import { SubscriptionTier, PaymentStatus, BillingInterval } from './types'

// Customer schemas
export const createCustomerSchema = z.object({
  email: z.string().email(),
  name: z.string().optional(),
  avatar_url: z.string().url().optional(),
  metadata: z.record(z.any()).optional(),
})

export const updateCustomerSchema = z.object({
  email: z.string().email().optional(),
  name: z.string().optional(),
  avatar_url: z.string().url().optional(),
  metadata: z.record(z.any()).optional(),
})

// Subscription schemas
export const createSubscriptionSchema = z.object({
  customerId: z.string(),
  productId: z.string(),
  priceId: z.string().optional(),
  trialDays: z.number().optional(),
  metadata: z.record(z.any()).optional(),
})

export const updateSubscriptionSchema = z.object({
  productId: z.string().optional(),
  priceId: z.string().optional(),
  quantity: z.number().optional(),
  metadata: z.record(z.any()).optional(),
  cancelAtPeriodEnd: z.boolean().optional(),
})

// Payment schemas (Polar uses orders for payments)
export const createOrderSchema = z.object({
  amount: z.number().positive(),
  currency: z.string().default('usd'),
  customerId: z.string(),
  productId: z.string(),
  description: z.string().optional(),
  metadata: z.record(z.any()).optional(),
})

// Checkout schemas
export const createCheckoutSessionSchema = z.object({
  customerId: z.string().optional(),
  email: z.string().email().optional(),
  productId: z.string(),
  quantity: z.number().default(1),
  successUrl: z.string().url(),
  cancelUrl: z.string().url().optional(),
  metadata: z.record(z.any()).optional(),
  allowPromotionCodes: z.boolean().default(false),
  trialDays: z.number().optional(),
  discountId: z.string().optional(),
})

// Webhook schemas
export const webhookEventSchema = z.object({
  id: z.string(),
  type: z.string(),
  data: z.object({
    object: z.any(),
  }),
  created_at: z.string(),
})

// Pricing schemas
export const pricingConfigSchema = z.object({
  tier: z.nativeEnum(SubscriptionTier),
  name: z.string(),
  description: z.string(),
  features: z.array(z.string()),
  limits: z.record(z.union([z.number(), z.boolean()])),
  pricing: z.object({
    monthly: z.number(),
    yearly: z.number(),
  }),
  polarProductIds: z.object({
    monthly: z.string(),
    yearly: z.string(),
  }),
})

// Refund schemas (Polar doesn't have direct refunds, but we can track them)
export const createRefundSchema = z.object({
  paymentId: z.string(),
  amount: z.number().positive().optional(),
  reason: z.enum(['duplicate', 'fraudulent', 'requested_by_customer']).optional(),
  metadata: z.record(z.any()).optional(),
})

// Product schemas
export const createProductSchema = z.object({
  name: z.string(),
  description: z.string().optional(),
  type: z.enum(['individual', 'business']).default('individual'),
  is_recurring: z.boolean().default(true),
  prices: z.array(z.object({
    type: z.enum(['one_time', 'recurring']),
    recurring_interval: z.enum(['month', 'year']).optional(),
    amount_cents: z.number().positive(),
    currency: z.string().default('usd'),
  })).optional(),
  benefits: z.array(z.string()).optional(),
  metadata: z.record(z.any()).optional(),
})

// Price schemas
export const createPriceSchema = z.object({
  product_id: z.string(),
  type: z.enum(['one_time', 'recurring']),
  recurring_interval: z.enum(['month', 'year']).optional(),
  amount_cents: z.number().positive(),
  currency: z.string().default('usd'),
})

// Customer portal schema
export const customerPortalSchema = z.object({
  customerId: z.string(),
  returnUrl: z.string().url(),
})

// Usage record schema (for metered billing)
export const createUsageRecordSchema = z.object({
  subscriptionId: z.string(),
  quantity: z.number().positive(),
  timestamp: z.date().optional(),
  action: z.enum(['increment', 'set']).default('increment'),
  metadata: z.record(z.any()).optional(),
})