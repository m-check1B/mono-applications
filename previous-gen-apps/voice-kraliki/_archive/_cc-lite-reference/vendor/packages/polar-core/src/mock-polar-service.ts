/**
 * Mock Polar Service for Testing
 * Provides simulated Polar functionality for development without real API keys
 */

export interface MockPolarProduct {
  id: string;
  name: string;
  description: string;
  type: 'individual' | 'business';
  is_recurring: boolean;
  metadata: Record<string, any>;
  prices: MockPolarPrice[];
  benefits: string[];
}

export interface MockPolarPrice {
  id: string;
  product_id: string;
  type: 'one_time' | 'recurring';
  recurring_interval?: 'month' | 'year';
  amount_cents: number;
  currency: string;
  is_archived: boolean;
}

export interface MockPolarCheckoutSession {
  id: string;
  url: string;
  customer_id: string;
  product_id: string;
  status: 'open' | 'expired' | 'completed';
  success_url: string;
  cancel_url?: string;
  metadata?: Record<string, any>;
}

export interface MockPolarSubscription {
  id: string;
  customer_id: string;
  product_id: string;
  price_id: string;
  status: 'incomplete' | 'incomplete_expired' | 'trialing' | 'active' | 'past_due' | 'canceled' | 'unpaid';
  current_period_start: Date;
  current_period_end: Date;
  trial_start?: Date;
  trial_end?: Date;
  cancel_at_period_end: boolean;
  metadata?: Record<string, any>;
}

export interface MockPolarCustomer {
  id: string;
  email: string;
  name?: string;
  avatar_url?: string;
  metadata?: Record<string, any>;
  created_at: Date;
}

export class MockPolarService {
  private products: Map<string, MockPolarProduct> = new Map();
  private customers: Map<string, MockPolarCustomer> = new Map();
  private subscriptions: Map<string, MockPolarSubscription> = new Map();
  private checkoutSessions: Map<string, MockPolarCheckoutSession> = new Map();
  private customerSubscriptions: Map<string, string[]> = new Map(); // customer_id -> subscription_ids[]

  constructor() {
    this.initializeMockData();
    console.log('🎭 Mock Polar Service initialized for testing');
  }

  private initializeMockData() {
    // Initialize with Stack 2025 products adapted for Polar
    const mockProducts = [
      // CC Light
      {
        id: 'prod_cc_light_starter',
        name: 'CC Light Starter',
        description: 'Perfect for small call centers',
        type: 'business' as const,
        is_recurring: true,
        metadata: { app: 'cc-light', tier: 'starter' },
        benefits: ['5 agents', '100 calls/month', 'Basic reporting', 'Email support'],
        prices: [
          {
            id: 'price_cc_light_starter_monthly',
            product_id: 'prod_cc_light_starter',
            type: 'recurring' as const,
            recurring_interval: 'month' as const,
            amount_cents: 2900,
            currency: 'usd',
            is_archived: false
          },
          {
            id: 'price_cc_light_starter_yearly',
            product_id: 'prod_cc_light_starter',
            type: 'recurring' as const,
            recurring_interval: 'year' as const,
            amount_cents: 29000,
            currency: 'usd',
            is_archived: false
          }
        ]
      },
      // CC Gym
      {
        id: 'prod_cc_gym_trainer',
        name: 'CC Gym Trainer',
        description: 'For individual trainers',
        type: 'individual' as const,
        is_recurring: true,
        metadata: { app: 'cc-gym', tier: 'trainer' },
        benefits: ['Unlimited scenarios', 'Advanced analytics', 'Priority support'],
        prices: [
          {
            id: 'price_cc_gym_trainer_monthly',
            product_id: 'prod_cc_gym_trainer',
            type: 'recurring' as const,
            recurring_interval: 'month' as const,
            amount_cents: 3900,
            currency: 'usd',
            is_archived: false
          }
        ]
      },
      // Invoice Gym
      {
        id: 'prod_invoice_freelancer',
        name: 'Invoice Gym Freelancer',
        description: 'For freelancers and small businesses',
        type: 'individual' as const,
        is_recurring: true,
        metadata: { app: 'invoice-gym', tier: 'freelancer' },
        benefits: ['Unlimited invoices', 'Custom branding', 'Payment tracking'],
        prices: [
          {
            id: 'price_invoice_freelancer_monthly',
            product_id: 'prod_invoice_freelancer',
            type: 'recurring' as const,
            recurring_interval: 'month' as const,
            amount_cents: 1900,
            currency: 'usd',
            is_archived: false
          }
        ]
      },
      // Productivity Hub
      {
        id: 'prod_productivity_personal',
        name: 'Productivity Hub Personal',
        description: 'For individuals seeking productivity gains',
        type: 'individual' as const,
        is_recurring: true,
        metadata: { app: 'productivity-hub', tier: 'personal' },
        benefits: ['AI-powered insights', 'Custom workflows', 'Unlimited projects'],
        prices: [
          {
            id: 'price_productivity_personal_monthly',
            product_id: 'prod_productivity_personal',
            type: 'recurring' as const,
            recurring_interval: 'month' as const,
            amount_cents: 900,
            currency: 'usd',
            is_archived: false
          }
        ]
      },
      // BYOK Unified Plans
      {
        id: 'prod_byok_mini',
        name: 'BYOK Mini',
        description: 'Bring Your Own Keys - Mini Plan',
        type: 'individual' as const,
        is_recurring: true,
        metadata: { tier: 'mini', byok: 'true' },
        benefits: ['2 apps access', 'Basic support', '30-day retention'],
        prices: [
          {
            id: 'price_byok_mini_monthly',
            product_id: 'prod_byok_mini',
            type: 'recurring' as const,
            recurring_interval: 'month' as const,
            amount_cents: 1900,
            currency: 'usd',
            is_archived: false
          },
          {
            id: 'price_byok_mini_yearly',
            product_id: 'prod_byok_mini',
            type: 'recurring' as const,
            recurring_interval: 'year' as const,
            amount_cents: 19000,
            currency: 'usd',
            is_archived: false
          }
        ]
      }
    ];

    mockProducts.forEach(product => {
      this.products.set(product.id, product);
    });
  }

  async createCustomer(data: {
    email: string;
    name?: string;
    avatar_url?: string;
    metadata?: Record<string, any>;
  }): Promise<MockPolarCustomer> {
    const customerId = `cus_polar_mock_${Date.now()}`;
    const customer: MockPolarCustomer = {
      id: customerId,
      email: data.email,
      name: data.name,
      avatar_url: data.avatar_url,
      metadata: data.metadata || {},
      created_at: new Date()
    };
    
    this.customers.set(customerId, customer);
    console.log('🎭 Mock Polar customer created', { customerId, email: data.email });
    
    return customer;
  }

  async getCustomer(customerId: string): Promise<MockPolarCustomer | null> {
    return this.customers.get(customerId) || null;
  }

  async updateCustomer(customerId: string, data: {
    email?: string;
    name?: string;
    avatar_url?: string;
    metadata?: Record<string, any>;
  }): Promise<MockPolarCustomer | null> {
    const existing = this.customers.get(customerId);
    if (!existing) return null;

    const updated = {
      ...existing,
      ...data,
      metadata: { ...existing.metadata, ...data.metadata }
    };
    
    this.customers.set(customerId, updated);
    return updated;
  }

  async createCheckoutSession(data: {
    customer_id?: string;
    email?: string;
    product_id: string;
    success_url: string;
    cancel_url?: string;
    metadata?: Record<string, any>;
    trial_days?: number;
    discount_id?: string;
  }): Promise<MockPolarCheckoutSession> {
    const sessionId = `cs_polar_mock_${Date.now()}`;
    const mockUrl = `http://localhost:3000/mock-polar-checkout?session=${sessionId}&product=${data.product_id}`;
    
    let customerId = data.customer_id;
    if (!customerId && data.email) {
      // Create customer automatically
      const customer = await this.createCustomer({
        email: data.email,
        metadata: { created_from_checkout: 'true' }
      });
      customerId = customer.id;
    }
    
    const session: MockPolarCheckoutSession = {
      id: sessionId,
      url: mockUrl,
      customer_id: customerId || `cus_polar_mock_${Date.now()}`,
      product_id: data.product_id,
      status: 'open',
      success_url: data.success_url,
      cancel_url: data.cancel_url,
      metadata: data.metadata
    };
    
    this.checkoutSessions.set(sessionId, session);
    
    console.log('🎭 Mock Polar checkout session created', {
      sessionId,
      productId: data.product_id,
      url: mockUrl
    });
    
    // Auto-complete checkout session after 3 seconds (simulate user payment)
    setTimeout(() => {
      this.completeCheckoutSession(sessionId, data.trial_days);
    }, 3000);
    
    return session;
  }

  private completeCheckoutSession(sessionId: string, trialDays?: number) {
    const session = this.checkoutSessions.get(sessionId);
    if (!session) return;
    
    session.status = 'completed';
    
    // Create subscription
    const subscriptionId = `sub_polar_mock_${Date.now()}`;
    const product = this.products.get(session.product_id);
    const monthlyPrice = product?.prices.find(p => p.recurring_interval === 'month');
    
    const now = new Date();
    const trialStart = trialDays ? now : undefined;
    const trialEnd = trialDays ? new Date(now.getTime() + trialDays * 24 * 60 * 60 * 1000) : undefined;
    const periodStart = trialEnd || now;
    const periodEnd = new Date(periodStart.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 days
    
    const subscription: MockPolarSubscription = {
      id: subscriptionId,
      customer_id: session.customer_id,
      product_id: session.product_id,
      price_id: monthlyPrice?.id || 'price_mock',
      status: trialDays ? 'trialing' : 'active',
      current_period_start: periodStart,
      current_period_end: periodEnd,
      trial_start: trialStart,
      trial_end: trialEnd,
      cancel_at_period_end: false,
      metadata: session.metadata
    };
    
    this.subscriptions.set(subscriptionId, subscription);
    
    // Track customer subscriptions
    const existingSubscriptions = this.customerSubscriptions.get(session.customer_id) || [];
    existingSubscriptions.push(subscriptionId);
    this.customerSubscriptions.set(session.customer_id, existingSubscriptions);
    
    console.log('🎭 Mock Polar checkout completed', {
      sessionId,
      subscriptionId,
      customerId: session.customer_id,
      trialDays
    });
  }

  async getSubscription(subscriptionId: string): Promise<MockPolarSubscription | null> {
    return this.subscriptions.get(subscriptionId) || null;
  }

  async listCustomerSubscriptions(customerId: string): Promise<MockPolarSubscription[]> {
    const subscriptionIds = this.customerSubscriptions.get(customerId) || [];
    const subscriptions: MockPolarSubscription[] = [];
    
    for (const subId of subscriptionIds) {
      const subscription = this.subscriptions.get(subId);
      if (subscription) {
        subscriptions.push(subscription);
      }
    }
    
    return subscriptions;
  }

  async cancelSubscription(subscriptionId: string, immediately = false): Promise<MockPolarSubscription | null> {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) return null;
    
    if (immediately) {
      subscription.status = 'canceled';
    } else {
      subscription.cancel_at_period_end = true;
    }
    
    this.subscriptions.set(subscriptionId, subscription);
    return subscription;
  }

  async resumeSubscription(subscriptionId: string): Promise<MockPolarSubscription | null> {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) return null;
    
    subscription.cancel_at_period_end = false;
    if (subscription.status === 'canceled') {
      subscription.status = 'active';
    }
    
    this.subscriptions.set(subscriptionId, subscription);
    return subscription;
  }

  async getCustomerPortalUrl(customerId: string, returnUrl: string): Promise<string> {
    console.log('🎭 Mock Polar customer portal accessed', { customerId, returnUrl });
    return `http://localhost:3000/mock-polar-portal?customer=${customerId}&return_url=${encodeURIComponent(returnUrl)}`;
  }

  async getSubscriptionStatus(customerId: string): Promise<{
    active: boolean;
    tier: string | null;
    currentPeriodEnd: Date | null;
    trialEnd: Date | null;
    cancelAtPeriodEnd: boolean;
  }> {
    const subscriptions = await this.listCustomerSubscriptions(customerId);
    const activeSubscription = subscriptions.find(sub => 
      sub.status === 'active' || sub.status === 'trialing'
    );
    
    if (!activeSubscription) {
      return {
        active: false,
        tier: null,
        currentPeriodEnd: null,
        trialEnd: null,
        cancelAtPeriodEnd: false
      };
    }
    
    const product = this.products.get(activeSubscription.product_id);
    const tier = product?.metadata.tier || 'unknown';
    
    return {
      active: true,
      tier,
      currentPeriodEnd: activeSubscription.current_period_end,
      trialEnd: activeSubscription.trial_end || null,
      cancelAtPeriodEnd: activeSubscription.cancel_at_period_end
    };
  }

  async constructWebhookEvent(payload: string, signature: string, secret: string): Promise<any> {
    // Mock webhook event construction
    return {
      id: `evt_polar_mock_${Date.now()}`,
      type: 'subscription.created',
      data: {
        object: {
          id: `sub_polar_mock_${Date.now()}`,
          customer_id: `cus_polar_mock_${Date.now()}`,
          product_id: `prod_polar_mock_${Date.now()}`,
          status: 'active',
          metadata: {}
        }
      },
      created_at: new Date().toISOString()
    };
  }

  // Get all products for testing
  getAllProducts(): MockPolarProduct[] {
    return Array.from(this.products.values());
  }

  // Get product by ID
  getProduct(productId: string): MockPolarProduct | undefined {
    return this.products.get(productId);
  }

  // Get all customers for testing
  getAllCustomers(): MockPolarCustomer[] {
    return Array.from(this.customers.values());
  }

  // Get all subscriptions for testing
  getAllSubscriptions(): MockPolarSubscription[] {
    return Array.from(this.subscriptions.values());
  }
}