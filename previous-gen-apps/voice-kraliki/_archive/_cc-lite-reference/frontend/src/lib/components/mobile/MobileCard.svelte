<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    subtitle?: string;
    icon?: string;
    onclick?: () => void;
    children?: Snippet;
    variant?: 'default' | 'highlighted' | 'bordered';
    padding?: 'sm' | 'md' | 'lg';
  }

  let {
    title,
    subtitle,
    icon,
    onclick,
    children,
    variant = 'default',
    padding = 'md'
  }: Props = $props();

  const variantClasses = {
    default: 'bg-white dark:bg-gray-800 shadow-sm',
    highlighted: 'bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-800',
    bordered: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
  };

  const paddingClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6'
  };
</script>

<div
  class="mobile-card rounded-lg transition-all duration-200
         {variantClasses[variant]} {paddingClasses[padding]}
         {onclick ? 'cursor-pointer hover:shadow-md active:scale-[0.98] touch-target-48' : ''}"
  onclick={onclick}
  role={onclick ? 'button' : undefined}
  tabindex={onclick ? 0 : undefined}
>
  {#if title || icon}
    <div class="flex items-center mb-3">
      {#if icon}
        <span class="text-2xl mr-3">{icon}</span>
      {/if}
      <div class="flex-1">
        {#if title}
          <h3 class="text-base font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
        {/if}
        {#if subtitle}
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {subtitle}
          </p>
        {/if}
      </div>
    </div>
  {/if}

  {#if children}
    {@render children()}
  {/if}
</div>

<style>
  .mobile-card {
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  .touch-target-48 {
    min-height: 48px;
  }
</style>
