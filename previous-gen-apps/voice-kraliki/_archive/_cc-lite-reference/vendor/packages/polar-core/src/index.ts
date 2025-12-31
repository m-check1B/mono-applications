/**
 * @stack-2025/polar-core
 * 
 * Polar payment processing for Stack 2025 applications
 * Provides subscription management, payment processing, and billing
 * 
 * A complete replacement for Stripe functionality using Polar's API
 */

export { PolarService } from './polar-service'
export { MockPolarService } from './mock-polar-service'
export { SubscriptionManager } from './subscription-manager'
export { PaymentProcessor } from './payment-processor'
export { WebhookHandler, PolarWebhookEventType } from './webhook-handler'
export type { WebhookHandlerFn } from './webhook-handler'

// Export all types
export * from './types'

// Export all schemas
export * from './schemas'

// Re-export commonly used enums for convenience
export {
  SubscriptionTier,
  PaymentStatus,
  BillingInterval,
  ApiProvider
} from './types'

// Export commonly used interfaces
export type {
  PolarCustomer,
  PolarSubscription,
  PolarPayment,
  PolarOrder,
  PolarProduct,
  PolarPrice,
  CheckoutSessionOptions,
  CustomerPortalOptions,
  RefundOptions,
  BYOKPricingConfig,
  BYOKSubscription,
  FeatureUsageData
} from './types'