# Migration Guide: From Stripe to Polar

This guide helps you migrate from `@unified/stripe-core` to `@stack-2025/polar-core` in your Stack 2025 applications.

## Overview

The migration involves:
1. Package replacement
2. Environment variable updates
3. API method changes
4. Database schema updates
5. Webhook handling changes

## Step 1: Package Installation

```bash
# Remove Stripe package
pnpm remove @unified/stripe-core

# Install Polar package
pnpm add @stack-2025/polar-core
```

## Step 2: Environment Variables

Update your `.env` files:

### Before (Stripe)
```env
STRIPE_SECRET_KEY=sk_test_123...
STRIPE_PUBLISHABLE_KEY=pk_test_123...
STRIPE_WEBHOOK_SECRET=whsec_123...
STRIPE_SUCCESS_URL=https://app.com/success
STRIPE_CANCEL_URL=https://app.com/cancel
STRIPE_PORTAL_RETURN_URL=https://app.com/settings
```

### After (Polar)
```env
POLAR_ACCESS_TOKEN=polar_at_123...
POLAR_WEBHOOK_SECRET=polar_wh_123...
POLAR_SUCCESS_URL=https://app.com/success
POLAR_CANCEL_URL=https://app.com/cancel
POLAR_PORTAL_RETURN_URL=https://app.com/settings

# Enable mock mode for development
PAYMENT_MOCK_MODE=true
```

## Step 3: Code Changes

### Service Initialization

#### Before (Stripe)
```typescript
import { StripeService } from '@unified/stripe-core'

const stripe = new StripeService(
  process.env.STRIPE_SECRET_KEY!,
  process.env.STRIPE_WEBHOOK_SECRET
)
```

#### After (Polar)
```typescript
import { PolarService } from '@stack-2025/polar-core'

const polar = new PolarService(
  process.env.POLAR_ACCESS_TOKEN!,
  process.env.POLAR_WEBHOOK_SECRET
)
```

### Customer Management

#### Before (Stripe)
```typescript
// Create customer
const customer = await stripe.createCustomer({
  email: 'user@example.com',
  name: 'John Doe'
})

// Get customer
const customer = await stripe.getCustomer(customerId)

// Update customer
const updated = await stripe.updateCustomer(customerId, {
  name: 'Jane Doe'
})
```

#### After (Polar)
```typescript
// Create customer - Same API!
const customer = await polar.createCustomer({
  email: 'user@example.com',
  name: 'John Doe'
})

// Get customer - Same API!
const customer = await polar.getCustomer(customerId)

// Update customer - Same API!
const updated = await polar.updateCustomer(customerId, {
  name: 'Jane Doe'
})
```

### Checkout Sessions

#### Before (Stripe)
```typescript
const session = await stripe.createCheckoutSession({
  customerId: user.stripeCustomerId,
  priceId: 'price_123',
  successUrl: '/success',
  cancelUrl: '/cancel',
  metadata: { userId: user.id }
})
```

#### After (Polar)
```typescript
const session = await polar.createCheckoutSession({
  customerId: user.polarCustomerId, // Updated field name
  productId: 'prod_123',            // productId instead of priceId
  successUrl: '/success',
  cancelUrl: '/cancel',
  metadata: { userId: user.id }
})
```

### Customer Portal

#### Before (Stripe)
```typescript
const portal = await stripe.createPortalSession({
  customerId: user.stripeCustomerId,
  returnUrl: '/settings'
})
```

#### After (Polar)
```typescript
const portal = await polar.createPortalSession({
  customerId: user.polarCustomerId, // Updated field name
  returnUrl: '/settings'
})
```

### Subscription Management

#### Before (Stripe)
```typescript
// List subscriptions
const subscriptions = await stripe.listSubscriptions(customerId)

// Cancel subscription
const canceled = await stripe.cancelSubscription(subscriptionId)

// Resume subscription
const resumed = await stripe.resumeSubscription(subscriptionId)

// Get status
const status = await stripe.getSubscriptionStatus(customerId)
```

#### After (Polar)
```typescript
// List subscriptions - Same API!
const subscriptions = await polar.listSubscriptions(customerId)

// Cancel subscription - Same API!
const canceled = await polar.cancelSubscription(subscriptionId)

// Resume subscription - Same API!
const resumed = await polar.resumeSubscription(subscriptionId)

// Get status - Same API!
const status = await polar.getSubscriptionStatus(customerId)
```

## Step 4: Database Schema Updates

Update your database schema to support Polar:

### User Table Changes

```sql
-- Add Polar customer ID field
ALTER TABLE users ADD COLUMN polar_customer_id VARCHAR(255);

-- Optional: Keep Stripe ID for migration period
-- ALTER TABLE users ADD COLUMN stripe_customer_id_backup VARCHAR(255);
-- UPDATE users SET stripe_customer_id_backup = stripe_customer_id;

-- Update existing customer ID field
UPDATE users 
SET polar_customer_id = stripe_customer_id 
WHERE stripe_customer_id IS NOT NULL;

-- Eventually rename/remove old field
-- ALTER TABLE users DROP COLUMN stripe_customer_id;
```

### Subscription Table Changes

```sql
-- Update subscription provider
ALTER TABLE subscriptions ADD COLUMN provider VARCHAR(50) DEFAULT 'polar';

-- Update existing subscriptions
UPDATE subscriptions SET provider = 'stripe' WHERE provider IS NULL;

-- Add Polar-specific fields
ALTER TABLE subscriptions ADD COLUMN polar_subscription_id VARCHAR(255);
ALTER TABLE subscriptions ADD COLUMN trial_start TIMESTAMP;
ALTER TABLE subscriptions ADD COLUMN trial_end TIMESTAMP;
```

## Step 5: Webhook Changes

### Webhook Event Types

Update your webhook handlers for Polar event types:

#### Before (Stripe)
```typescript
import { WebhookHandler } from '@unified/stripe-core'

const webhooks = new WebhookHandler(stripe)

webhooks.on('checkout.session.completed', async (event) => {
  // Handle Stripe checkout completion
})

webhooks.on('customer.subscription.updated', async (event) => {
  // Handle Stripe subscription update
})
```

#### After (Polar)
```typescript
import { WebhookHandler, PolarWebhookEventType } from '@stack-2025/polar-core'

const webhooks = new WebhookHandler(polar)

webhooks.on(PolarWebhookEventType.CHECKOUT_SUCCEEDED, async (event) => {
  // Handle Polar checkout completion
})

webhooks.on(PolarWebhookEventType.SUBSCRIPTION_UPDATED, async (event) => {
  // Handle Polar subscription update
})
```

### Webhook Processing

#### Before (Stripe)
```typescript
fastify.post('/api/payments/webhook', async (request, reply) => {
  const signature = request.headers['stripe-signature']
  const event = await stripe.constructWebhookEvent(
    request.rawBody,
    signature,
    process.env.STRIPE_WEBHOOK_SECRET!
  )
  
  // Process event...
})
```

#### After (Polar)
```typescript
fastify.post('/api/payments/webhook', async (request, reply) => {
  const signature = request.headers['polar-signature'] // Different header
  
  const result = await webhooks.processWebhook(
    request.rawBody,
    signature,
    process.env.POLAR_WEBHOOK_SECRET!
  )
  
  return { received: result.success }
})
```

## Step 6: Product Configuration

Update your product configurations:

#### Before (Stripe Prices)
```typescript
export const CC_LIGHT_PRODUCTS = {
  starter: {
    prices: {
      monthly: 'price_cc_light_starter_monthly',
      yearly: 'price_cc_light_starter_yearly'
    }
  }
}
```

#### After (Polar Products)
```typescript
export const CC_LIGHT_PRODUCTS = {
  starter: {
    pricing: {
      monthly: 'prod_cc_light_starter',         // Product ID
      yearly: 'prod_cc_light_starter_yearly'    // Different product for yearly
    }
  }
}
```

## Step 7: Frontend Updates

Update your frontend code to use the new field names:

### React/TypeScript Updates

```typescript
// Before
interface User {
  stripeCustomerId?: string
}

// After  
interface User {
  polarCustomerId?: string
}

// API calls remain the same - only backend changes needed
const response = await fetch('/api/payments/checkout', {
  method: 'POST',
  body: JSON.stringify({
    productId: 'prod_cc_light_starter', // productId instead of priceId
    metadata: { source: 'pricing_page' }
  })
})
```

## Step 8: Testing Migration

### 1. Enable Mock Mode
```env
PAYMENT_MOCK_MODE=true
```

### 2. Test All Payment Flows
```typescript
import { PolarService } from '@stack-2025/polar-core'

// Mock mode automatically enabled
const polar = new PolarService('polar_mock', 'mock_secret')

// All operations work with mock data
const customer = await polar.createCustomer({
  email: 'test@example.com'
})

const checkout = await polar.createCheckoutSession({
  customerId: customer.id,
  productId: 'prod_cc_light_starter',
  successUrl: '/success'
})

console.log('Mock checkout URL:', checkout.url)
```

### 3. Verify Database Updates
```sql
-- Check customer migration
SELECT 
  id, 
  email, 
  polar_customer_id, 
  stripe_customer_id_backup
FROM users 
WHERE polar_customer_id IS NOT NULL
LIMIT 5;

-- Check subscription migration
SELECT 
  id,
  user_id,
  provider,
  status,
  polar_subscription_id
FROM subscriptions
WHERE provider = 'polar'
LIMIT 5;
```

## Step 9: Deployment Checklist

### Pre-deployment
- [ ] All environment variables updated
- [ ] Database schema migrated
- [ ] Code changes tested in mock mode
- [ ] Webhook endpoints updated
- [ ] Frontend updated to use new field names

### Deployment
- [ ] Deploy backend changes first
- [ ] Update webhook URLs in Polar dashboard
- [ ] Test webhooks in staging
- [ ] Monitor error logs
- [ ] Verify payment flows work end-to-end

### Post-deployment
- [ ] Monitor subscription status accuracy
- [ ] Verify customer portal access
- [ ] Check webhook processing
- [ ] Monitor payment success rates
- [ ] Update monitoring/alerting

## Common Issues and Solutions

### Issue: Customer ID Mismatch
**Problem**: Users can't access their subscriptions after migration.

**Solution**: 
```sql
-- Ensure customer ID mapping is correct
UPDATE users 
SET polar_customer_id = COALESCE(polar_customer_id, stripe_customer_id)
WHERE polar_customer_id IS NULL AND stripe_customer_id IS NOT NULL;
```

### Issue: Product ID vs Price ID
**Problem**: Checkout sessions fail because of wrong ID type.

**Solution**: Update checkout calls to use `productId` instead of `priceId`:
```typescript
// Wrong
const session = await polar.createCheckoutSession({
  priceId: 'price_123' // This won't work
})

// Correct
const session = await polar.createCheckoutSession({
  productId: 'prod_123' // Use product ID
})
```

### Issue: Webhook Signature Verification
**Problem**: Webhooks fail signature verification.

**Solution**: Check webhook header name:
```typescript
// Stripe uses 'stripe-signature'
// Polar uses 'polar-signature'
const signature = request.headers['polar-signature']
```

### Issue: Missing Trial Information
**Problem**: Trial periods not showing correctly.

**Solution**: Update subscription queries to include trial fields:
```sql
ALTER TABLE subscriptions 
ADD COLUMN trial_start TIMESTAMP,
ADD COLUMN trial_end TIMESTAMP;
```

## Rollback Plan

If issues arise, you can rollback:

### 1. Code Rollback
```bash
# Revert to Stripe
pnpm remove @stack-2025/polar-core
pnpm add @unified/stripe-core

# Deploy previous version
```

### 2. Database Rollback
```sql
-- Restore Stripe customer IDs
UPDATE users 
SET stripe_customer_id = stripe_customer_id_backup
WHERE stripe_customer_id_backup IS NOT NULL;

-- Mark subscriptions as Stripe
UPDATE subscriptions SET provider = 'stripe';
```

### 3. Environment Rollback
```env
# Restore Stripe variables
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Support

For migration issues:
1. Check the mock mode works first
2. Verify environment variables are correct
3. Test webhook signature verification
4. Check database field mappings
5. Review error logs for specific issues

The @stack-2025/polar-core package is designed to be a drop-in replacement with minimal changes required.