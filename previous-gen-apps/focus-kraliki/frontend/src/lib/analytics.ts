/**
 * Privacy-first analytics using Plausible Analytics (self-hosted)
 *
 * Features:
 * - No cookies required (GDPR compliant)
 * - Lightweight (~1KB)
 * - Respects Do Not Track
 * - Automatic page view tracking with SvelteKit
 */

import { browser } from '$app/environment';
import { page } from '$app/stores';

const ANALYTICS_HOST = 'https://analytics.verduona.com';
const SITE_DOMAIN = 'focus.kraliki.com';

interface EventProps {
  [key: string]: string | number | boolean;
}

/**
 * Check if tracking should occur
 */
function shouldTrack(): boolean {
  if (!browser) return false;

  // Skip localhost unless explicitly testing
  if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1';
    if (isLocalhost) return false;
  }

  // Respect Do Not Track
  if (typeof navigator !== 'undefined' && navigator.doNotTrack === '1') return false;

  return true;
}

/**
 * Send analytics event
 */
function send(payload: Record<string, unknown>): void {
  if (!shouldTrack()) return;

  const url = `${ANALYTICS_HOST}/api/event`;
  const body = JSON.stringify(payload);

  // Use sendBeacon for reliability
  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: 'application/json' });
    navigator.sendBeacon(url, blob);
  } else {
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: true,
    }).catch(() => {
      // Silently fail - analytics should never break the app
    });
  }
}

/**
 * Track a page view
 */
export function trackPageview(url?: string): void {
  if (!browser || typeof window === 'undefined') return;

  send({
    n: 'pageview',
    u: url || window.location.href,
    d: SITE_DOMAIN,
    r: document.referrer || null,
    w: window.innerWidth,
  });
}

/**
 * Track a custom event
 */
export function trackEvent(name: string, props?: EventProps): void {
  if (!browser || typeof window === 'undefined') return;

  const payload: Record<string, unknown> = {
    n: name,
    u: window.location.href,
    d: SITE_DOMAIN,
    r: document.referrer || null,
    w: window.innerWidth,
  };

  if (props) {
    payload.p = props;
  }

  send(payload);
}

// Convenience methods

export function trackSignup(method?: string): void {
  trackEvent('signup', method ? { method } : undefined);
}

export function trackSubscription(plan: string, value?: number): void {
  trackEvent('subscription', { plan, ...(value !== undefined && { value }) });
}

export function trackFeature(feature: string, action?: string): void {
  trackEvent('feature_used', { feature, ...(action && { action }) });
}

export function trackOnboarding(step: string, completed: boolean = true): void {
  trackEvent('onboarding', { step, completed });
}

/**
 * Initialize analytics with automatic page view tracking
 * Call this in your root +layout.svelte onMount
 */
export function initAnalytics(): () => void {
  if (!browser) return () => {};

  // Track navigation changes
  const unsubscribe = page.subscribe(($page) => {
    if ($page.url) {
      trackPageview($page.url.href);
    }
  });

  return unsubscribe;
}
