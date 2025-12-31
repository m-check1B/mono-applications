<script lang="ts">
  /**
   * Focus by Kraliki Onboarding Modal
   * Guides new users through key features on first login
   */
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { browser } from '$app/environment';

  interface OnboardingFeature {
    icon: string;
    title: string;
    description: string;
  }

  interface Props {
    onComplete?: () => void;
    onSkip?: () => void;
  }

  let { onComplete, onSkip }: Props = $props();

  const STORAGE_KEY = 'focus_kraliki_onboarding_completed';
  const STEPS = ['welcome', 'features', 'complete'] as const;

  const features: OnboardingFeature[] = [
    {
      icon: 'voice',
      title: 'Voice Capture',
      description: 'Add tasks naturally by speaking - just say what you need to do'
    },
    {
      icon: 'ai',
      title: 'AI Insights',
      description: 'Get smart recommendations and automatic task prioritization'
    },
    {
      icon: 'calendar',
      title: 'Calendar Sync',
      description: 'Connect Google Calendar for seamless scheduling'
    },
    {
      icon: 'zap',
      title: 'Shadow Analysis',
      description: 'Discover hidden patterns in how you actually work'
    }
  ];

  // Icon SVG paths
  const iconPaths: Record<string, string> = {
    voice: 'M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z M19 10v2a7 7 0 0 1-14 0v-2 M12 19v4 M8 23h8',
    ai: 'M12 2L2 7l10 5 10-5-10-5z M2 17l10 5 10-5 M2 12l10 5 10-5',
    calendar: 'M19 4H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z M16 2v4 M8 2v4 M3 10h18',
    zap: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z'
  };

  let isVisible = $state(false);
  let currentStep = $state(0);
  let isTransitioning = $state(false);

  onMount(() => {
    if (browser) {
      const completed = localStorage.getItem(STORAGE_KEY);
      isVisible = !completed;
    }
  });

  function handleNext() {
    if (isTransitioning) return;
    isTransitioning = true;

    if (currentStep < STEPS.length - 1) {
      currentStep++;
    } else {
      handleComplete();
    }

    setTimeout(() => {
      isTransitioning = false;
    }, 300);
  }

  function handleSkip() {
    if (browser) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        completed: true,
        skipped: true,
        completedAt: new Date().toISOString()
      }));
    }
    isVisible = false;
    onSkip?.();
  }

  function handleComplete() {
    if (browser) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        completed: true,
        skipped: false,
        completedAt: new Date().toISOString()
      }));
    }
    isVisible = false;
    onComplete?.();
  }
</script>

{#if isVisible}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-void/80 backdrop-blur-sm"
    transition:fade={{ duration: 200 }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="onboarding-title"
  >
    <div
      class="relative w-full max-w-lg mx-4 bg-background border-3 border-foreground shadow-brutal overflow-hidden"
      transition:fly={{ y: 20, duration: 300 }}
    >
      <!-- Progress Dots -->
      <div class="absolute top-4 left-1/2 -translate-x-1/2 flex gap-2">
        {#each STEPS as _, i}
          <div
            class="w-2 h-2 border-2 border-foreground transition-colors"
            class:bg-foreground={i <= currentStep}
          ></div>
        {/each}
      </div>

      <!-- Skip Button -->
      <button
        class="absolute top-4 right-4 text-xs text-muted-foreground hover:text-foreground uppercase tracking-wider"
        onclick={handleSkip}
      >
        Skip
      </button>

      <!-- Content -->
      <div class="pt-12 pb-6 px-6">
        {#if currentStep === 0}
          <!-- Welcome Step -->
          <div class="text-center" in:fade={{ duration: 200, delay: 100 }}>
            <div class="text-5xl mb-4">
              <span class="text-terminal-green">&gt;_</span>
            </div>
            <h1 id="onboarding-title" class="text-2xl font-bold uppercase tracking-wide mb-2">
              Welcome to Focus by Kraliki
            </h1>
            <p class="text-muted-foreground mb-8">
              Your AI-powered productivity companion
            </p>
            <p class="text-sm text-muted-foreground">
              Let's take a quick tour of the key features.
            </p>
          </div>
        {:else if currentStep === 1}
          <!-- Features Step -->
          <div in:fade={{ duration: 200, delay: 100 }}>
            <h2 class="text-lg font-bold uppercase tracking-wide mb-6 text-center">
              Key Features
            </h2>
            <div class="space-y-4">
              {#each features as feature, i}
                <div
                  class="flex items-start gap-4 p-3 border-2 border-foreground/20 hover:border-terminal-green transition-colors"
                  in:fly={{ x: -20, duration: 200, delay: 100 + i * 50 }}
                >
                  <div class="flex-shrink-0 w-10 h-10 border-2 border-foreground flex items-center justify-center">
                    <svg
                      class="w-5 h-5 text-terminal-green"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="square"
                    >
                      <path d={iconPaths[feature.icon]} />
                    </svg>
                  </div>
                  <div>
                    <h3 class="font-bold uppercase text-sm">{feature.title}</h3>
                    <p class="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        {:else}
          <!-- Complete Step -->
          <div class="text-center" in:fade={{ duration: 200, delay: 100 }}>
            <div class="text-5xl mb-4 text-terminal-green">
              &#x2713;
            </div>
            <h2 class="text-2xl font-bold uppercase tracking-wide mb-2">
              You're All Set!
            </h2>
            <p class="text-muted-foreground mb-4">
              Start exploring Focus by Kraliki and boost your productivity.
            </p>
            <p class="text-sm text-muted-foreground">
              Try saying "Add task review PR tomorrow high priority" to get started!
            </p>
          </div>
        {/if}
      </div>

      <!-- Action Button -->
      <div class="p-6 pt-0">
        <button
          class="w-full py-3 uppercase tracking-wide font-bold border-2 border-foreground bg-foreground text-background hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[5px_5px_0px_0px_hsl(var(--foreground))] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[1px_1px_0px_0px_hsl(var(--foreground))] transition-all shadow-[3px_3px_0px_0px_hsl(var(--foreground))]"
          onclick={handleNext}
          disabled={isTransitioning}
        >
          {#if currentStep === 0}
            Get Started
          {:else if currentStep === STEPS.length - 1}
            Let's Go!
          {:else}
            Continue
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .border-3 {
    border-width: 3px;
  }

  .shadow-brutal {
    box-shadow: 6px 6px 0px 0px hsl(var(--foreground));
  }
</style>
