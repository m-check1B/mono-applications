<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let isOnline = $state(false);
  let checkingConnection = $state(true);

  onMount(() => {
    // Check initial connection status
    isOnline = navigator.onLine;
    checkingConnection = false;

    // Listen for online/offline events
    const handleOnline = () => {
      isOnline = true;
      setTimeout(() => {
        goto('/');
      }, 1000);
    };

    const handleOffline = () => {
      isOnline = false;
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  });

  const handleRetry = () => {
    checkingConnection = true;
    setTimeout(() => {
      checkingConnection = false;
      if (navigator.onLine) {
        goto('/');
      }
    }, 1000);
  };
</script>

<svelte:head>
  <title>Voice by Kraliki - Offline</title>
</svelte:head>

<div class="flex flex-col items-center justify-center min-h-screen min-h-dvh p-4 text-center bg-gradient-to-br from-slate-900 to-slate-800">
  <!-- Offline Icon -->
  <div class="offline-icon w-32 h-32 mb-8 rounded-full bg-blue-500/20 flex items-center justify-center">
    <span class="text-7xl">📡</span>
  </div>

  <!-- Main Heading -->
  <h1 class="text-3xl md:text-4xl font-bold mb-4 text-blue-400">
    You're Offline
  </h1>

  <!-- Description -->
  <p class="text-lg text-slate-400 max-w-md mb-8">
    It looks like you've lost your internet connection. Please check your connection and try again.
  </p>

  <!-- Retry Button -->
  <button
    onclick={handleRetry}
    disabled={checkingConnection}
    class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
           transition-all duration-200 hover:scale-105 active:scale-95
           disabled:opacity-50 disabled:cursor-not-allowed
           touch-target-48"
  >
    {#if checkingConnection}
      Checking Connection...
    {:else}
      Retry Connection
    {/if}
  </button>

  <!-- Status Indicator -->
  <div class="mt-6 text-sm">
    {#if isOnline}
      <span class="text-green-400">✓ Connection detected! Redirecting...</span>
    {:else if checkingConnection}
      <span class="text-slate-500">Checking connection status...</span>
    {:else}
      <span class="text-slate-500">Still offline. Waiting for connection...</span>
    {/if}
  </div>

  <!-- App Info -->
  <div class="mt-12 text-xs text-slate-600">
    <p>Voice by Kraliki Communications Platform</p>
    <p class="mt-1">Some features may be available offline</p>
  </div>
</div>

<style>
  .touch-target-48 {
    min-height: 48px;
    min-width: 48px;
  }

  .offline-icon {
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
</style>
