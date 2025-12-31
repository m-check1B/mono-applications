<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fly, scale, fade } from 'svelte/transition';
  import { quintOut, elasticOut } from 'svelte/easing';
  import Button from '../shared/Button.svelte';
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import { trpc } from '$lib/trpc/client';

  type Call = {
    id: string;
    providerCallId?: string;
    customerName: string;
    customerPhone: string;
    duration: number;
    status: 'active' | 'on-hold' | 'ringing';
    sentiment?: 'positive' | 'neutral' | 'negative';
  };

  let { call = $bindable<Call | null>(null) } = $props();

  let elapsed = $state(0);
  let interval: ReturnType<typeof setInterval> | null = null;
  let micLevel = $state(75);
  let headsetLevel = $state(65);
  let isProcessing = $state(false);

  // Simulate audio levels
  let audioInterval: ReturnType<typeof setInterval> | null = null;

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startTimer = () => {
    if (interval) clearInterval(interval);
    interval = setInterval(() => {
      elapsed += 1;
    }, 1000);
  };

  const stopTimer = () => {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
  };

  const startAudioSimulation = () => {
    if (audioInterval) clearInterval(audioInterval);
    audioInterval = setInterval(() => {
      // Simulate fluctuating audio levels
      micLevel = Math.floor(Math.random() * 30) + 60; // 60-90
      headsetLevel = Math.floor(Math.random() * 25) + 55; // 55-80
    }, 500);
  };

  const stopAudioSimulation = () => {
    if (audioInterval) {
      clearInterval(audioInterval);
      audioInterval = null;
    }
  };

  $effect(() => {
    if (call?.status === 'active') {
      elapsed = call.duration;
      startTimer();
      startAudioSimulation();
    } else {
      stopTimer();
      stopAudioSimulation();
    }
    return () => {
      stopTimer();
      stopAudioSimulation();
    };
  });

  const handleHold = async () => {
    if (!call || isProcessing) return;

    isProcessing = true;
    try {
      // In real implementation, would call hold/resume endpoint
      // For now, toggle the status locally
      if (call.status === 'on-hold') {
        call = { ...call, status: 'active' };
      } else {
        call = { ...call, status: 'on-hold' };
      }
      console.log('Hold/Resume call', call.providerCallId || call.id);
    } catch (error) {
      console.error('Failed to hold/resume call:', error);
    } finally {
      isProcessing = false;
    }
  };

  const handleTransfer = async () => {
    if (!call || isProcessing) return;

    const transferTo = prompt('Enter phone number to transfer to:');
    if (!transferTo) return;

    isProcessing = true;
    try {
      const callId = call.providerCallId || call.id;
      await trpc.telephony.transferCall.mutate({
        callId,
        to: transferTo
      });

      console.log('Call transferred successfully');
      // Call will be ended after transfer
      call = null;
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('call-ended', { detail: { requiresWrapUp: true } }));
      }
    } catch (error: any) {
      console.error('Failed to transfer call:', error);
      alert(`Transfer failed: ${error.message}`);
    } finally {
      isProcessing = false;
    }
  };

  const handleHangup = async () => {
    if (!call || isProcessing) return;

    isProcessing = true;
    try {
      const callId = call.providerCallId || call.id;
      await trpc.telephony.hangupCall.mutate({ callId });

      console.log('Call ended successfully');
      call = null;

      // Trigger wrap-up mode
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('call-ended', { detail: { requiresWrapUp: true } }));
      }
    } catch (error: any) {
      console.error('Failed to hang up call:', error);
      // Still end the call locally even if API fails
      call = null;
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('call-ended', { detail: { requiresWrapUp: true } }));
      }
    } finally {
      isProcessing = false;
    }
  };

  const handleMute = () => {
    // Mute would be handled by Twilio Device in real implementation
    console.log('Mute call', call?.providerCallId || call?.id);
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Active Call</h2>
      {#if call}
        <div in:scale={{ duration: 300, easing: elasticOut }}>
          <Badge variant={call.status === 'active' ? 'success' : call.status === 'on-hold' ? 'warning' : 'primary'}>
            {call.status.toUpperCase()}
          </Badge>
        </div>
      {/if}
    </div>
  {/snippet}

  {#if call}
    <div class="space-y-6" in:fly={{ y: 20, duration: 400, easing: quintOut }} out:fade={{ duration: 200 }}>
      <!-- Timer -->
      <div class="text-center" in:scale={{ duration: 500, easing: elasticOut, delay: 100 }}>
        <div class="text-5xl font-mono font-bold text-gray-900 dark:text-white tabular-nums">
          {formatTime(elapsed)}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400 mt-2">Call Duration</div>
      </div>

      <!-- Customer Info -->
      <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2"
           in:fly={{ x: -20, duration: 400, easing: quintOut, delay: 200 }}>
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Customer</span>
          {#if call.sentiment}
            <Badge variant={call.sentiment === 'positive' ? 'success' : call.sentiment === 'negative' ? 'danger' : 'gray'}>
              {call.sentiment === 'positive' ? '😊' : call.sentiment === 'negative' ? '😞' : '😐'} {call.sentiment}
            </Badge>
          {/if}
        </div>
        <div class="text-lg font-semibold text-gray-900 dark:text-white">{call.customerName}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">{call.customerPhone}</div>
      </div>

      <!-- Audio Levels -->
      <div class="grid grid-cols-2 gap-4"
           in:fly={{ y: 20, duration: 400, easing: quintOut, delay: 300 }}>
        <!-- Microphone Level -->
        <div>
          <div class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
              </svg>
              <span>Microphone</span>
            </div>
            <span>{micLevel}%</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-300 ease-out"
              style={`width: ${micLevel}%`}
            ></div>
          </div>
        </div>

        <!-- Headset Level -->
        <div>
          <div class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
            <div class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
              </svg>
              <span>Headset</span>
            </div>
            <span>{headsetLevel}%</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 ease-out"
              style={`width: ${headsetLevel}%`}
            ></div>
          </div>
        </div>
      </div>

      <!-- Live Transcript -->
      <div class="bg-gray-900 dark:bg-black rounded-lg p-4 h-32 overflow-y-auto"
           in:fly={{ y: 20, duration: 400, easing: quintOut, delay: 400 }}>
        <div class="space-y-2 text-sm">
          <div>
            <span class="font-semibold text-blue-400">CUSTOMER:</span>
            <span class="ml-2 text-gray-300">Hi, I'm having trouble with my billing account.</span>
          </div>
          <div>
            <span class="font-semibold text-green-400">AGENT:</span>
            <span class="ml-2 text-gray-300">I'd be happy to help you with that. Can you provide your account number?</span>
          </div>
        </div>
      </div>

      <!-- Call Controls -->
      <div class="grid grid-cols-3 gap-3"
           in:fly={{ y: 20, duration: 400, easing: quintOut, delay: 500 }}>
        <Button
          variant={call.status === 'on-hold' ? 'primary' : 'secondary'}
          size="lg"
          onclick={handleHold}
          class="flex-col h-20"
        >
          <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {call.status === 'on-hold' ? 'Resume' : 'Hold'}
        </Button>

        <Button variant="secondary" size="lg" onclick={handleTransfer} class="flex-col h-20">
          <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
          </svg>
          Transfer
        </Button>

        <Button variant="danger" size="lg" onclick={handleHangup} class="flex-col h-20">
          <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z"></path>
          </svg>
          Hang Up
        </Button>
      </div>

      <!-- Quick Actions -->
      <div class="flex gap-2"
           in:fly={{ y: 20, duration: 400, easing: quintOut, delay: 600 }}>
        <Button variant="secondary" size="sm" class="flex-1" onclick={handleMute}>
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" clip-rule="evenodd"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"></path>
          </svg>
          Mute
        </Button>
        <Button variant="secondary" size="sm" class="flex-1">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          Notes
        </Button>
        <Button variant="secondary" size="sm" class="flex-1">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          History
        </Button>
      </div>
    </div>
  {:else}
    <div class="text-center py-12" in:fade={{ duration: 300 }}>
      <div in:scale={{ duration: 600, easing: elasticOut }}>
        <svg class="w-20 h-20 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
        </svg>
      </div>
      <p class="text-gray-600 dark:text-gray-400" in:fly={{ y: 10, duration: 400, delay: 200 }}>No active call</p>
      <p class="text-sm text-gray-500 dark:text-gray-500 mt-2" in:fly={{ y: 10, duration: 400, delay: 300 }}>Waiting for incoming calls...</p>
    </div>
  {/if}
</Card>

<style>
  .tabular-nums {
    font-variant-numeric: tabular-nums;
  }
</style>
