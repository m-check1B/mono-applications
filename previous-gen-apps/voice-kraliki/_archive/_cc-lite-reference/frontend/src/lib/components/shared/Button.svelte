<script lang="ts">
  type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'gray';
  type ButtonSize = 'sm' | 'md' | 'lg';

  interface Props {
    variant?: ButtonVariant;
    size?: ButtonSize;
    disabled?: boolean;
    loading?: boolean;
    class?: string;
    title?: string;
    ariaLabel?: string;
    onclick?: (event: MouseEvent) => void;
    children?: import('svelte').Snippet;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    class: className = '',
    title,
    ariaLabel,
    onclick,
    children
  }: Props = $props();

  const variantClasses = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    warning: 'bg-yellow-500 hover:bg-yellow-600 text-white',
    gray: 'bg-gray-100 hover:bg-gray-200 text-gray-900 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-white',
  } satisfies Record<ButtonVariant, string>;

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const classes = `
    inline-flex items-center justify-center font-semibold rounded-lg
    transition-colors duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${className}
  `.trim().replace(/\s+/g, ' ');
</script>

<button
  {onclick}
  disabled={disabled || loading}
  class={classes}
>
  {#if loading}
    <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  {/if}
  {@render children?.()}
</button>
