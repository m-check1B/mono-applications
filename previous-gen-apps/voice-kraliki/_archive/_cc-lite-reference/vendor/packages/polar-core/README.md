# @stack-2025/polar-core

A comprehensive Polar payment processing package for Stack 2025 applications. This package provides a complete replacement for Stripe functionality using Polar's API, designed specifically for the Stack 2025 ecosystem.

## Overview

@stack-2025/polar-core offers:

- 🔄 **Drop-in Stripe Replacement** - Compatible with existing payment routes
- 🎭 **Mock Service** - Full testing support without real API keys
- 💳 **Payment Processing** - One-time payments and recurring subscriptions
- 🔐 **BYOK Support** - Bring Your Own Keys subscription tiers
- 📊 **Subscription Management** - Complete lifecycle management
- 🪝 **Webhook Handling** - Comprehensive event processing
- 🛡️ **Type Safety** - Full TypeScript support with Zod validation

## Installation

```bash
pnpm add @stack-2025/polar-core
```

## Quick Start

### Basic Setup

```typescript
import { PolarService } from '@stack-2025/polar-core'

// Initialize Polar service
const polar = new PolarService(
  process.env.POLAR_ACCESS_TOKEN!,
  process.env.POLAR_WEBHOOK_SECRET
)

// Create a customer
const customer = await polar.createCustomer({
  email: 'user@example.com',
  name: 'John Doe',
  metadata: {
    app: 'cc-light',
    source: 'signup'
  }
})

// Create checkout session
const checkout = await polar.createCheckoutSession({
  customerId: customer.id,
  productId: 'prod_cc_light_starter',
  successUrl: 'https://yourapp.com/success',
  cancelUrl: 'https://yourapp.com/cancel'
})

console.log('Checkout URL:', checkout.url)
```

### Mock Mode for Testing

```typescript
import { PolarService } from '@stack-2025/polar-core'

// Enable mock mode
process.env.PAYMENT_MOCK_MODE = 'true'

const polar = new PolarService('polar_mock', 'mock_webhook_secret')

// All operations work the same but use mock data
const customer = await polar.createCustomer({
  email: 'test@example.com',
  name: 'Test User'
})
```

## Core Services

### PolarService

The main service class that provides all Polar API functionality:

```typescript
import { PolarService } from '@stack-2025/polar-core'

const polar = new PolarService(accessToken, webhookSecret)

// Customer management
const customer = await polar.createCustomer(data)
const updated = await polar.updateCustomer(customerId, updates)
const customer = await polar.getCustomer(customerId)

// Checkout and payments
const session = await polar.createCheckoutSession(options)
const portal = await polar.createPortalSession(options)

// Subscription management
const subscriptions = await polar.listSubscriptions(customerId)
const canceled = await polar.cancelSubscription(subscriptionId)
const resumed = await polar.resumeSubscription(subscriptionId)
```

### SubscriptionManager

Advanced subscription lifecycle management:

```typescript
import { PolarService, SubscriptionManager } from '@stack-2025/polar-core'

const polar = new PolarService(accessToken, webhookSecret)
const subscriptions = new SubscriptionManager(polar)

// Create subscription
const subscription = await subscriptions.createSubscription({
  customerId: 'cus_123',
  productId: 'prod_starter',
  trialDays: 14
})

// Upgrade/downgrade
const upgraded = await subscriptions.upgradeSubscription(
  subscriptionId,
  'prod_pro',
  true // prorate
)

// Pause and resume
const paused = await subscriptions.pauseSubscription(subscriptionId)
const resumed = await subscriptions.resumeSubscription(subscriptionId)

// Check feature access
const access = await subscriptions.checkFeatureAccess(
  customerId,
  'ai_calls',
  'cc-light'
)
```

### PaymentProcessor

Handle one-time payments and orders:

```typescript
import { PolarService, PaymentProcessor } from '@stack-2025/polar-core'

const polar = new PolarService(accessToken, webhookSecret)
const payments = new PaymentProcessor(polar)

// Process one-time payment
const payment = await payments.processPayment({
  customerId: 'cus_123',
  amount: 2900, // $29.00
  productId: 'prod_one_time',
  description: 'Premium feature unlock',
  successUrl: 'https://app.com/success',
  cancelUrl: 'https://app.com/cancel'
})

// Check payment status
const status = await payments.getPaymentStatus(payment.orderId)

// Get payment analytics
const analytics = await payments.getPaymentAnalytics(customerId, {
  startDate: new Date('2024-01-01'),
  endDate: new Date('2024-12-31')
})
```

### WebhookHandler

Process Polar webhooks with ease:

```typescript
import { 
  PolarService, 
  WebhookHandler, 
  PolarWebhookEventType 
} from '@stack-2025/polar-core'

const polar = new PolarService(accessToken, webhookSecret)
const webhooks = new WebhookHandler(polar)

// Register event handlers
webhooks.on(PolarWebhookEventType.SUBSCRIPTION_CREATED, async (event) => {
  console.log('New subscription:', event.data.object.id)
  // Update database, send welcome email, etc.
})

webhooks.on(PolarWebhookEventType.CHECKOUT_SUCCEEDED, async (event) => {
  console.log('Payment successful:', event.data.object.id)
  // Grant access, send receipt, etc.
})

// Register default Stack 2025 handlers
webhooks.registerDefaultHandlers()

// Process webhook in your API route
export async function POST(request: Request) {
  const payload = await request.text()
  const signature = request.headers.get('polar-signature') || ''
  
  const result = await webhooks.processWebhook(payload, signature)
  
  return Response.json({ received: result.success })
}
```

## Integration with Existing Apps

### Replacing Stripe in Payment Routes

The package is designed as a drop-in replacement for Stripe. Here's how to migrate:

#### Before (Stripe):

```typescript
import { StripeService } from '@unified/stripe-core'

const stripe = new StripeService(
  process.env.STRIPE_SECRET_KEY!,
  process.env.STRIPE_WEBHOOK_SECRET
)

const session = await stripe.createCheckoutSession({
  customerId: user.stripeCustomerId,
  priceId: 'price_123',
  successUrl: '/success',
  cancelUrl: '/cancel'
})
```

#### After (Polar):

```typescript
import { PolarService } from '@stack-2025/polar-core'

const polar = new PolarService(
  process.env.POLAR_ACCESS_TOKEN!,
  process.env.POLAR_WEBHOOK_SECRET
)

const session = await polar.createCheckoutSession({
  customerId: user.polarCustomerId,
  productId: 'prod_123', // Note: productId instead of priceId
  successUrl: '/success',
  cancelUrl: '/cancel'
})
```

### Environment Variables

Update your `.env` files:

```env
# Polar Configuration
POLAR_ACCESS_TOKEN=polar_access_token_123
POLAR_WEBHOOK_SECRET=polar_webhook_secret_123

# Mock mode for development/testing
PAYMENT_MOCK_MODE=true
```

## Stack 2025 BYOK Integration

The package includes full support for Stack 2025's BYOK (Bring Your Own Keys) subscription model:

```typescript
import { BYOKPricingConfig, SubscriptionTier } from '@stack-2025/polar-core'

// Define BYOK pricing configuration
const byokConfig: BYOKPricingConfig = {
  tier: SubscriptionTier.PRO,
  name: 'BYOK Pro',
  description: 'Professional plan with your own API keys',
  targetAudience: 'Power users and small teams',
  pricing: {
    monthly: 9900, // $99.00
    yearly: 99900,  // $999.00
    yearlyDiscount: 15 // 15% discount
  },
  polarProductIds: {
    monthly: 'prod_byok_pro_monthly',
    yearly: 'prod_byok_pro_yearly'
  },
  appAccess: {
    maxApps: 5,
    availableApps: ['cc-light', 'cc-gym', 'invoice-gym']
  },
  featureLimits: {
    ccLight: {
      maxAgents: 25,
      maxCallsPerMonth: -1 // Unlimited
    },
    dataRetentionDays: 365,
    supportLevel: 'priority',
    analyticsLevel: 'advanced'
  },
  byokRequirements: {
    requiredProviders: ['openai', 'deepgram'],
    optionalProviders: ['anthropic', 'twilio'],
    customEndpointSupport: true,
    telephonyRequired: false
  }
}
```

## Product Configuration

### Stack 2025 App Products

Pre-configured products for Stack 2025 apps:

```typescript
// CC Light
const ccLightProducts = {
  starter: {
    id: 'prod_cc_light_starter',
    name: 'CC Light Starter',
    monthlyPrice: 2900, // $29/month
    yearlyPrice: 29000, // $290/year
    features: ['5 agents', '100 calls/month', 'Basic reporting']
  },
  professional: {
    id: 'prod_cc_light_pro',
    name: 'CC Light Professional', 
    monthlyPrice: 9900, // $99/month
    yearlyPrice: 99000, // $990/year
    features: ['25 agents', 'Unlimited calls', 'Advanced analytics']
  }
}

// CC Gym
const ccGymProducts = {
  trainer: {
    id: 'prod_cc_gym_trainer',
    name: 'CC Gym Trainer',
    monthlyPrice: 3900, // $39/month
    features: ['Unlimited scenarios', 'Advanced analytics']
  }
}

// BYOK Unified
const byokProducts = {
  mini: {
    id: 'prod_byok_mini',
    name: 'BYOK Mini',
    monthlyPrice: 1900, // $19/month
    yearlyPrice: 19000, // $190/year
    appAccess: 2
  },
  standard: {
    id: 'prod_byok_standard', 
    name: 'BYOK Standard',
    monthlyPrice: 4900, // $49/month
    yearlyPrice: 49000, // $490/year
    appAccess: 5
  }
}
```

## Mock Service for Testing

The package includes a comprehensive mock service that simulates all Polar functionality:

```typescript
import { MockPolarService } from '@stack-2025/polar-core'

const mockPolar = new MockPolarService()

// Get all mock products
const products = mockPolar.getAllProducts()

// Create mock customer
const customer = await mockPolar.createCustomer({
  email: 'test@example.com',
  name: 'Test User'
})

// Mock checkout (auto-completes after 3 seconds)
const checkout = await mockPolar.createCheckoutSession({
  customer_id: customer.id,
  product_id: 'prod_cc_light_starter',
  success_url: '/success',
  trial_days: 14
})

// Get subscription status
const status = await mockPolar.getSubscriptionStatus(customer.id)
```

## Error Handling

All methods include proper error handling with descriptive messages:

```typescript
import { PolarService } from '@stack-2025/polar-core'

const polar = new PolarService(accessToken)

try {
  const customer = await polar.createCustomer({
    email: 'invalid-email' // This will throw a validation error
  })
} catch (error) {
  if (error.message.includes('validation')) {
    console.log('Validation error:', error.message)
  } else if (error.message.includes('Polar API')) {
    console.log('API error:', error.message)
  }
}
```

## Type Safety

Full TypeScript support with comprehensive type definitions:

```typescript
import type { 
  PolarCustomer,
  PolarSubscription,
  CheckoutSessionOptions,
  SubscriptionTier
} from '@stack-2025/polar-core'

// All types are exported for use in your application
const customer: PolarCustomer = {
  id: 'cus_123',
  customerId: 'cus_123',
  email: 'user@example.com',
  name: 'John Doe',
  createdAt: new Date(),
  updatedAt: new Date()
}

const checkoutOptions: CheckoutSessionOptions = {
  productId: 'prod_123',
  successUrl: 'https://app.com/success',
  cancelUrl: 'https://app.com/cancel',
  trialDays: 14
}
```

## Migration Guide

### From @unified/stripe-core to @stack-2025/polar-core

1. **Install the new package**:
   ```bash
   pnpm remove @unified/stripe-core
   pnpm add @stack-2025/polar-core
   ```

2. **Update imports**:
   ```typescript
   // Before
   import { StripeService } from '@unified/stripe-core'
   
   // After  
   import { PolarService } from '@stack-2025/polar-core'
   ```

3. **Update initialization**:
   ```typescript
   // Before
   const stripe = new StripeService(apiKey, webhookSecret)
   
   // After
   const polar = new PolarService(accessToken, webhookSecret)
   ```

4. **Update method calls**:
   - `createCheckoutSession` now takes `productId` instead of `priceId`
   - `listSubscriptions` returns `PolarSubscription[]` instead of `Stripe.Subscription[]`
   - Webhook events have different structure (see webhook documentation)

5. **Update environment variables**:
   ```env
   # Replace
   STRIPE_SECRET_KEY=sk_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   
   # With
   POLAR_ACCESS_TOKEN=polar_...
   POLAR_WEBHOOK_SECRET=polar_whsec_...
   ```

## API Reference

### PolarService

- `createCustomer(data)` - Create a new customer
- `getCustomer(customerId)` - Get customer by ID
- `updateCustomer(customerId, data)` - Update customer information
- `createCheckoutSession(options)` - Create payment checkout
- `createPortalSession(options)` - Create customer portal session
- `listSubscriptions(customerId)` - List customer subscriptions
- `cancelSubscription(subscriptionId, immediately?)` - Cancel subscription
- `resumeSubscription(subscriptionId)` - Resume canceled subscription
- `getSubscriptionStatus(customerId)` - Get subscription status
- `constructWebhookEvent(payload, signature, secret?)` - Process webhook

### SubscriptionManager

- `createSubscription(data)` - Create new subscription
- `updateSubscription(subscriptionId, updates)` - Update subscription
- `upgradeSubscription(subscriptionId, newProductId, prorate?)` - Upgrade plan
- `downgradeSubscription(subscriptionId, newProductId, immediate?)` - Downgrade plan
- `pauseSubscription(subscriptionId, pauseUntil?)` - Pause subscription
- `resumeSubscription(subscriptionId)` - Resume paused subscription
- `getSubscriptionDetails(subscriptionId)` - Get detailed subscription info
- `checkFeatureAccess(customerId, feature, appId?)` - Check feature access

### PaymentProcessor

- `createPaymentCheckout(options)` - Create one-time payment checkout
- `createOrder(data)` - Create order/payment intent
- `processPayment(data)` - Process complete payment flow
- `getPaymentStatus(orderId)` - Get payment status
- `listCustomerPayments(customerId, options?)` - List customer payments
- `getPaymentAnalytics(customerId, period)` - Get payment analytics

### WebhookHandler

- `on(eventType, handler)` - Register event handler
- `off(eventType, handler?)` - Remove event handler
- `processWebhook(payload, signature, secret?)` - Process incoming webhook
- `registerDefaultHandlers()` - Register Stack 2025 default handlers
- `registerBYOKHandlers()` - Register BYOK-specific handlers
- `registerAppHandlers(appId)` - Register app-specific handlers

## Support

For issues, questions, or contributions, please refer to the Stack 2025 documentation or open an issue in the repository.

## License

MIT - See LICENSE file for details.