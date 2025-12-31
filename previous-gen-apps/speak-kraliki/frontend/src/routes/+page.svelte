<script lang="ts">
  import { goto } from '$app/navigation';
  import { t } from '$lib/i18n';
</script>

<svelte:head>
  <title>{$t('landing.title')} - AI Voice Employee Intelligence</title>
</svelte:head>

<div class="min-h-[calc(100vh-60px)] flex flex-col items-center justify-center p-8 relative overflow-hidden bg-grid-pattern">
  <div class="scanline"></div>
  <div class="scanline-fast"></div>
  
  <!-- Decorative Voice Pulse Grid -->
  <div class="absolute inset-0 z-0 opacity-10 pointer-events-none flex items-center justify-center">
    <div class="grid grid-cols-12 gap-4 w-[150%] h-[150%] rotate-12">
      {#each Array(144) as _, i}
        <div 
          class="w-full h-8 bg-terminal-green" 
          style="animation: pulse-glow {2 + (i % 5)}s ease-in-out infinite; animation-delay: {(i % 10) * 0.2}s; opacity: {0.1 + (i % 3) * 0.1}"
        ></div>
      {/each}
    </div>
  </div>

  <div class="brutal-card max-w-2xl w-full p-8 text-center relative z-20">
    <h1 class="text-4xl md:text-5xl mb-4 text-terminal-green font-display hover:animate-glitch cursor-default">
      {$t('landing.title').toUpperCase()}
    </h1>

    <p class="text-lg mb-2 text-muted-foreground font-mono">
      {$t('landing.subtitle')}
    </p>

    <div class="my-8 border-t-2 border-foreground"></div>

    <p class="mb-8 text-foreground/80 font-mono">
      {$t('landing.description')}
    </p>

    <div class="flex flex-col sm:flex-row gap-6 justify-center">
      <button
        onclick={() => goto('/login')}
        class="brutal-btn brutal-btn-primary hover:animate-pulse-glow"
      >
        {$t('landing.login').toUpperCase()}
      </button>

      <button
        onclick={() => goto('/register')}
        class="brutal-btn hover:animate-pulse-glow"
      >
        {$t('landing.register').toUpperCase()}
      </button>
    </div>

    <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
      <div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm">
        <div class="text-terminal-green text-2xl mb-2 font-display">01</div>
        <h3 class="text-sm font-bold mb-1 uppercase">{$t('landing.feature1.title')}</h3>
        <p class="text-xs text-muted-foreground font-mono">
          {$t('landing.feature1.desc')}
        </p>
      </div>

      <div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm">
        <div class="text-terminal-green text-2xl mb-2 font-display">02</div>
        <h3 class="text-sm font-bold mb-1 uppercase">{$t('landing.feature2.title')}</h3>
        <p class="text-xs text-muted-foreground font-mono">
          {$t('landing.feature2.desc')}
        </p>
      </div>

      <div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm">
        <div class="text-terminal-green text-2xl mb-2 font-display">03</div>
        <h3 class="text-sm font-bold mb-1 uppercase">{$t('landing.feature3.title')}</h3>
        <p class="text-xs text-muted-foreground font-mono">
          {$t('landing.feature3.desc')}
        </p>
      </div>
    </div>
  </div>
</div>

<style>
</style>
