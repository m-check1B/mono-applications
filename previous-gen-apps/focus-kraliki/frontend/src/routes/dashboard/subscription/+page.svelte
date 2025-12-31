<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { authStore } from '$lib/stores/auth';
  import { logger } from '$lib/utils/logger';
  import { Check, Crown, Zap, Shield, Calendar, Mic, Users, Loader2 } from 'lucide-svelte';

  interface Plan {
    id: string;
    name: string;
    price: number;
    currency: string;
    interval: string;
    features: string[];
    recommended: boolean;
  }

  let plans: Plan[] = [];
  let isLoading = true;
  let isSubscribing = false;
  let selectedPlan: string | null = null;
  let error: string | null = null;
  let subscriptionStatus: any = null;

  $: currentUser = $authStore.user;
  $: isPremium = currentUser?.isPremium || false;

  onMount(async () => {
    await Promise.all([loadPlans(), loadSubscriptionStatus()]);
  });

  async function loadPlans() {
    try {
      const response: any = await api.billing.getPlans();
      plans = response.plans || [];
    } catch (err: any) {
      logger.error('Failed to load plans', err);
      // Use fallback plans if API fails
      plans = [
        {
          id: 'monthly',
          name: 'Pro Monthly',
          price: 9.00,
          currency: 'USD',
          interval: 'month',
          features: [
            'Unlimited AI requests',
            'Priority support',
            'Advanced analytics',
            'Calendar sync',
            'Voice commands',
            'Team features (coming soon)'
          ],
          recommended: false
        },
        {
          id: 'yearly',
          name: 'Pro Yearly',
          price: 79.00,
          currency: 'USD',
          interval: 'year',
          features: [
            'Unlimited AI requests',
            'Priority support',
            'Advanced analytics',
            'Calendar sync',
            'Voice commands',
            'Team features (coming soon)',
            '2 months free (save $29)'
          ],
          recommended: true
        }
      ];
    } finally {
      isLoading = false;
    }
  }

  async function loadSubscriptionStatus() {
    try {
      subscriptionStatus = await api.billing.subscriptionStatus();
    } catch (err) {
      logger.error('Failed to load subscription status', err);
    }
  }

  async function subscribe(planId: 'monthly' | 'yearly') {
    if (isSubscribing) return;

    isSubscribing = true;
    selectedPlan = planId;
    error = null;

    try {
      const response: any = await api.billing.createCheckoutSession({ plan: planId });

      if (response?.url) {
        // Redirect to Stripe Checkout
        window.location.href = response.url;
      } else {
        error = 'Failed to create checkout session';
      }
    } catch (err: any) {
      error = err.detail || err.message || 'Failed to start subscription';
    } finally {
      isSubscribing = false;
      selectedPlan = null;
    }
  }

  async function openBillingPortal() {
    try {
      const response: any = await api.billing.portalSession();
      if (response?.url) {
        window.open(response.url, '_blank', 'noopener');
      }
    } catch (err: any) {
      error = err.detail || 'Failed to open billing portal';
    }
  }

  function formatPrice(price: number, currency: string, interval: string): string {
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    });
    return `${formatter.format(price)}/${interval}`;
  }

  const featureIcons: Record<string, any> = {
    'Unlimited AI requests': Zap,
    'Priority support': Shield,
    'Advanced analytics': Crown,
    'Calendar sync': Calendar,
    'Voice commands': Mic,
    'Team features (coming soon)': Users
  };
</script>

<div class="max-w-4xl mx-auto space-y-8 p-6">
  <!-- Header -->
  <div class="text-center">
    <h1 class="text-3xl font-bold flex items-center justify-center gap-3">
      <Crown class="w-8 h-8 text-primary" />
      Upgrade to Pro
    </h1>
    <p class="text-muted-foreground mt-2">
      Unlock unlimited AI capabilities and premium features
    </p>
  </div>

  {#if isPremium}
    <!-- Already Premium -->
    <div class="bg-primary/10 border border-primary/20 rounded-lg p-6 text-center">
      <div class="flex items-center justify-center gap-2 mb-4">
        <Crown class="w-6 h-6 text-primary" />
        <span class="text-xl font-semibold text-primary">You're a Pro member!</span>
      </div>
      <p class="text-muted-foreground mb-4">
        Thank you for supporting Focus by Kraliki. You have access to all premium features.
      </p>
      <button
        on:click={openBillingPortal}
        class="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Manage Subscription
      </button>
    </div>
  {:else}
    <!-- Pricing Cards -->
    {#if isLoading}
      <div class="flex items-center justify-center py-12">
        <Loader2 class="w-8 h-8 animate-spin text-primary" />
      </div>
    {:else}
      <div class="grid md:grid-cols-2 gap-6">
        {#each plans as plan}
          <div
            class="relative bg-card border rounded-xl p-6 {plan.recommended
              ? 'border-primary shadow-lg ring-2 ring-primary/20'
              : 'border-border'}"
          >
            {#if plan.recommended}
              <div class="absolute -top-3 left-1/2 -translate-x-1/2">
                <span class="bg-primary text-primary-foreground text-sm font-medium px-3 py-1 rounded-full">
                  Best Value
                </span>
              </div>
            {/if}

            <div class="text-center mb-6">
              <h2 class="text-xl font-semibold">{plan.name}</h2>
              <div class="mt-4">
                <span class="text-4xl font-bold">${plan.price}</span>
                <span class="text-muted-foreground">/{plan.interval}</span>
              </div>
              {#if plan.interval === 'year'}
                <p class="text-sm text-primary mt-1">
                  ${(plan.price / 12).toFixed(2)}/month billed annually
                </p>
              {/if}
            </div>

            <ul class="space-y-3 mb-6">
              {#each plan.features as feature}
                <li class="flex items-center gap-3">
                  <Check class="w-5 h-5 text-primary flex-shrink-0" />
                  <span class="text-sm">{feature}</span>
                </li>
              {/each}
            </ul>

            <button
              on:click={() => subscribe(plan.id as 'monthly' | 'yearly')}
              disabled={isSubscribing}
              class="w-full py-3 rounded-lg font-medium transition-colors disabled:opacity-50 {plan.recommended
                ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'}"
            >
              {#if isSubscribing && selectedPlan === plan.id}
                <Loader2 class="w-5 h-5 animate-spin inline mr-2" />
                Processing...
              {:else}
                Subscribe Now
              {/if}
            </button>
          </div>
        {/each}
      </div>
    {/if}
  {/if}

  {#if error}
    <div class="bg-destructive/10 border border-destructive/20 text-destructive rounded-lg p-4 text-center">
      {error}
    </div>
  {/if}

  <!-- Free Tier Info -->
  <div class="bg-muted/50 rounded-lg p-6">
    <h3 class="font-semibold mb-3">Current Free Tier Includes:</h3>
    <ul class="grid md:grid-cols-2 gap-2 text-sm text-muted-foreground">
      <li class="flex items-center gap-2">
        <Check class="w-4 h-4" />
        Limited AI requests per day
      </li>
      <li class="flex items-center gap-2">
        <Check class="w-4 h-4" />
        Basic task management
      </li>
      <li class="flex items-center gap-2">
        <Check class="w-4 h-4" />
        Standard support
      </li>
      <li class="flex items-center gap-2">
        <Check class="w-4 h-4" />
        BYOK (Bring Your Own Key) option
      </li>
    </ul>
    <p class="text-sm text-muted-foreground mt-4">
      Want unlimited AI without subscribing?
      <a href="/dashboard/settings" class="text-primary hover:underline">
        Use your own OpenRouter API key
      </a>
    </p>
  </div>

  <!-- FAQ Section -->
  <div class="space-y-4">
    <h3 class="text-xl font-semibold">Frequently Asked Questions</h3>

    <div class="space-y-3">
      <details class="bg-card border border-border rounded-lg p-4">
        <summary class="font-medium cursor-pointer">Can I cancel anytime?</summary>
        <p class="mt-2 text-sm text-muted-foreground">
          Yes! You can cancel your subscription at any time. You'll continue to have access until the end of your billing period.
        </p>
      </details>

      <details class="bg-card border border-border rounded-lg p-4">
        <summary class="font-medium cursor-pointer">What payment methods do you accept?</summary>
        <p class="mt-2 text-sm text-muted-foreground">
          We accept all major credit cards (Visa, Mastercard, American Express) through our secure payment processor, Stripe.
        </p>
      </details>

      <details class="bg-card border border-border rounded-lg p-4">
        <summary class="font-medium cursor-pointer">What's the difference between Pro and BYOK?</summary>
        <p class="mt-2 text-sm text-muted-foreground">
          Pro gives you unlimited AI requests through our hosted infrastructure. BYOK (Bring Your Own Key) lets you use your own OpenRouter API key, giving you complete control over your AI usage and billing.
        </p>
      </details>

      <details class="bg-card border border-border rounded-lg p-4">
        <summary class="font-medium cursor-pointer">Is there a free trial?</summary>
        <p class="mt-2 text-sm text-muted-foreground">
          The free tier gives you a taste of Focus by Kraliki's capabilities. You can use it indefinitely with limited AI requests, or upgrade to Pro for unlimited access.
        </p>
      </details>
    </div>
  </div>
</div>
