<script lang="ts">
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth.svelte';

  interface NavItem {
    href: string;
    label: string;
    icon: string;
    roles?: string[];
  }

  const navItems: NavItem[] = [
    {
      href: '/operator',
      label: 'Dashboard',
      icon: '📊',
      roles: ['AGENT', 'SUPERVISOR', 'ADMIN']
    },
    {
      href: '/operator?tab=calls',
      label: 'Calls',
      icon: '📞',
      roles: ['AGENT', 'SUPERVISOR', 'ADMIN']
    },
    {
      href: '/sms',
      label: 'SMS',
      icon: '💬',
      roles: ['AGENT', 'SUPERVISOR', 'ADMIN']
    },
    {
      href: '/email',
      label: 'Email',
      icon: '📧',
      roles: ['AGENT', 'SUPERVISOR', 'ADMIN']
    },
    {
      href: '/supervisor',
      label: 'Monitor',
      icon: '👁️',
      roles: ['SUPERVISOR', 'ADMIN']
    },
    {
      href: '/admin',
      label: 'Admin',
      icon: '⚙️',
      roles: ['ADMIN']
    }
  ];

  function isActive(href: string): boolean {
    return $page.url.pathname === href || $page.url.pathname.startsWith(href + '/');
  }

  function canAccess(item: NavItem): boolean {
    if (!item.roles) return true;
    return item.roles.includes(auth.user?.role || '');
  }
</script>

<!-- Mobile Bottom Navigation (fixed at bottom) -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 safe-area-inset-bottom z-40">
  <div class="flex justify-around items-center h-16">
    {#each navItems.filter(canAccess) as item}
      <a
        href={item.href}
        class="flex flex-col items-center justify-center flex-1 h-full touch-target-48 transition-colors
               {isActive(item.href)
                 ? 'text-primary-600 dark:text-primary-400'
                 : 'text-gray-600 dark:text-gray-400 hover:text-primary-500'}"
        aria-label={item.label}
      >
        <span class="text-2xl mb-1">{item.icon}</span>
        <span class="text-xs font-medium">{item.label}</span>
      </a>
    {/each}
  </div>
</nav>

<style>
  /* Minimum 48px touch target for accessibility */
  .touch-target-48 {
    min-height: 48px;
    min-width: 48px;
  }

  /* Safe area for iPhone X+ notch/home indicator */
  .safe-area-inset-bottom {
    padding-bottom: env(safe-area-inset-bottom);
  }
</style>
