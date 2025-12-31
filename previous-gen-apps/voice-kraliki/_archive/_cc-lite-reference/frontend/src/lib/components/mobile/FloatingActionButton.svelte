<script lang="ts">
  interface Props {
    icon?: string;
    label?: string;
    onclick?: () => void;
    variant?: 'primary' | 'secondary' | 'success' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    position?: 'bottom-right' | 'bottom-left' | 'bottom-center';
  }

  let {
    icon = '➕',
    label = 'Action',
    onclick,
    variant = 'primary',
    size = 'md',
    position = 'bottom-right'
  }: Props = $props();

  const sizeClasses = {
    sm: 'w-12 h-12 text-lg',
    md: 'w-14 h-14 text-2xl',
    lg: 'w-16 h-16 text-3xl'
  };

  const variantClasses = {
    primary: 'bg-primary-600 hover:bg-primary-700 shadow-primary-500/50',
    secondary: 'bg-gray-600 hover:bg-gray-700 shadow-gray-500/50',
    success: 'bg-green-600 hover:bg-green-700 shadow-green-500/50',
    danger: 'bg-red-600 hover:bg-red-700 shadow-red-500/50'
  };

  const positionClasses = {
    'bottom-right': 'bottom-20 right-6 md:bottom-6',
    'bottom-left': 'bottom-20 left-6 md:bottom-6',
    'bottom-center': 'bottom-20 left-1/2 -translate-x-1/2 md:bottom-6'
  };
</script>

<button
  class="fab fixed rounded-full flex items-center justify-center
         text-white shadow-lg transition-all duration-200
         hover:scale-110 active:scale-95 touch-target-48
         {sizeClasses[size]} {variantClasses[variant]} {positionClasses[position]}"
  onclick={onclick}
  aria-label={label}
  title={label}
>
  <span class="fab-icon">{icon}</span>
</button>

<style>
  .fab {
    z-index: 50;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }

  .fab:active {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  }

  .touch-target-48 {
    min-height: 48px;
    min-width: 48px;
  }

  /* Ripple effect on click (mobile-like) */
  .fab::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    transition: transform 0.3s;
  }

  .fab:active::after {
    transform: scale(1);
    transition: transform 0s;
  }
</style>
