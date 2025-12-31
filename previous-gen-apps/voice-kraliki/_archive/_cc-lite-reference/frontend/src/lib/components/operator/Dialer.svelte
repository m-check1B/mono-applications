<script lang="ts">
  import { onMount } from 'svelte';
  import { fly, scale } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Button from '../shared/Button.svelte';
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import { trpc } from '$lib/trpc/client';

  let { onCallStart, onCallEnd, onCallStatusChange } = $props<{
    onCallStart?: () => void;
    onCallEnd?: () => void;
    onCallStatusChange?: (status: any) => void;
  }>();

  let phoneNumber = $state('');
  let isInitializing = $state(true);
  let isReady = $state(false);
  let hasActiveCall = $state(false);
  let isMuted = $state(false);
  let volume = $state(75);
  let error = $state<string | null>(null);
  let callStatus = $state<any>(null);
  let incomingCall = $state<any>(null);
  let activeCallId = $state<string | null>(null);

  const dialerButtons = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
  ];

  let twilioDevice: any = null;

  onMount(() => {
    let destroyed = false;

    (async () => {
    try {
      isInitializing = true;

      // Fetch Twilio token for real Twilio integration
      try {
        const tokenResponse = await trpc.telephony.getToken.query();
        console.log('✅ Fetched Twilio token for identity:', tokenResponse.identity);

        // Dynamically import Twilio Device SDK
        const { Device } = await import('@twilio/voice-sdk');

        // Initialize Twilio Device with token
        twilioDevice = new Device(tokenResponse.token, ({
          codecPreferences: ['opus', 'pcmu'],
          fakeLocalDTMF: true,
          enableImprovedSignalingErrorPrecision: true
        }) as any);

        // Set up event listeners
        twilioDevice.on('registered', () => {
          console.log('✅ Twilio Device registered and ready');
          isReady = true;
        });

        twilioDevice.on('error', (twilioError: any) => {
          console.error('❌ Twilio Device error:', twilioError);
          error = twilioError.message || 'Twilio Device error';
        });

        twilioDevice.on('incoming', (call: any) => {
          console.log('📞 Incoming call from:', call.parameters.From);
          incomingCall = {
            call,
            from: call.parameters.From,
            to: call.parameters.To
          };
        });

        twilioDevice.on('tokenWillExpire', async () => {
          console.log('🔄 Token expiring, fetching new token...');
          try {
            const newTokenResponse = await trpc.telephony.getToken.query();
            twilioDevice.updateToken(newTokenResponse.token);
            console.log('✅ Token refreshed');
          } catch (refreshError) {
            console.error('Failed to refresh token:', refreshError);
          }
        });

        // Register the device
        await twilioDevice.register();

        console.log('✅ Twilio Device initialized successfully');
      } catch (tokenError: any) {
        console.warn('Twilio token unavailable, using fallback mode:', tokenError);
        // Fallback: Mark as ready without Twilio Device
        await new Promise(resolve => setTimeout(resolve, 500));
        isReady = true;
      }
    } catch (err: any) {
      error = 'Failed to initialize dialer';
      console.error('❌ Dialer initialization failed:', err);
    } finally {
      isInitializing = false;
    }

    })();

    // Cleanup on unmount
    return () => {
      destroyed = true;
      if (twilioDevice) {
        twilioDevice.unregister();
        twilioDevice.destroy();
      }
    };
  });

  const addDigit = (digit: string) => {
    phoneNumber += digit;
  };

  let activeConnection: any = null;

  const makeCall = async () => {
    if (!phoneNumber.trim()) return;

    try {
      console.log('📞 Making call to:', phoneNumber);

      const formattedNumber = phoneNumber.startsWith('+') ? phoneNumber : `+${phoneNumber}`;

      // If Twilio Device is available, use it for browser-based calling
      if (twilioDevice && twilioDevice.state === 'registered') {
        console.log('📞 Making call via Twilio Device SDK');

        const params = {
          To: formattedNumber
        };

        activeConnection = await twilioDevice.connect({ params });

        activeConnection.on('accept', () => {
          console.log('✅ Call accepted');
          hasActiveCall = true;
          callStatus = {
            callDirection: 'outbound',
            callTo: formattedNumber,
            isMuted: false,
            callId: activeConnection.parameters.CallSid
          };

          if (onCallStart) onCallStart();
          if (onCallStatusChange) onCallStatusChange(callStatus);
        });

        activeConnection.on('disconnect', () => {
          console.log('📴 Call disconnected');
          hasActiveCall = false;
          callStatus = null;
          activeConnection = null;
          if (onCallEnd) onCallEnd();
        });

        activeConnection.on('error', (err: any) => {
          console.error('Call error:', err);
          error = err.message || 'Call error';
        });

      } else {
        // Fallback to backend API call
        console.log('📞 Making call via backend API (Twilio Device unavailable)');

        const result = await trpc.telephony.createCall.mutate({
          to: formattedNumber,
          metadata: { source: 'dialer' }
        });

        activeCallId = result.callId;
        hasActiveCall = true;
        callStatus = {
          callDirection: 'outbound',
          callTo: formattedNumber,
          isMuted: false,
          callId: result.callId
        };

        if (onCallStart) onCallStart();
        if (onCallStatusChange) onCallStatusChange(callStatus);
      }

      phoneNumber = '';
    } catch (err: any) {
      error = 'Failed to make call';
      console.error('Call error:', err);
      alert(`Failed to make call: ${err.message || 'Unknown error'}`);
    }
  };

  const hangupCall = async () => {
    try {
      // If using Twilio Device SDK connection
      if (activeConnection) {
        activeConnection.disconnect();
        activeConnection = null;
      }
      // Otherwise use backend API
      else if (activeCallId) {
        await trpc.telephony.hangupCall.mutate({ callId: activeCallId });
      }

      hasActiveCall = false;
      callStatus = null;
      activeCallId = null;
      if (onCallEnd) onCallEnd();
    } catch (err) {
      console.error('Failed to hang up:', err);
      // Still clear local state even if API fails
      hasActiveCall = false;
      callStatus = null;
      activeCallId = null;
      activeConnection = null;
      if (onCallEnd) onCallEnd();
    }
  };

  const toggleMute = async () => {
    isMuted = !isMuted;
    if (callStatus) {
      callStatus.isMuted = isMuted;
    }

    // Mute via Twilio Device SDK if available
    if (activeConnection) {
      activeConnection.mute(isMuted);
      console.log(`🔇 Call ${isMuted ? 'muted' : 'unmuted'} via Twilio Device`);
    }
  };

  const sendDTMF = async (digit: string) => {
    if (hasActiveCall) {
      console.log('📲 Sending DTMF:', digit);
      // Send via Twilio Device SDK if available
      if (activeConnection) {
        activeConnection.sendDigits(digit);
      }
    }
  };

  const answerIncomingCall = async () => {
    if (incomingCall && incomingCall.call) {
      try {
        await incomingCall.call.accept();

        activeConnection = incomingCall.call;
        hasActiveCall = true;
        callStatus = {
          callDirection: 'inbound',
          callFrom: incomingCall.from,
          isMuted: false,
          callId: incomingCall.call.parameters.CallSid
        };

        // Set up disconnect handler
        activeConnection.on('disconnect', () => {
          console.log('📴 Call disconnected');
          hasActiveCall = false;
          callStatus = null;
          activeConnection = null;
          if (onCallEnd) onCallEnd();
        });

        incomingCall = null;

        if (onCallStart) onCallStart();
        if (onCallStatusChange) onCallStatusChange(callStatus);
      } catch (err: any) {
        console.error('Failed to answer call:', err);
        error = 'Failed to answer call';
      }
    }
  };

  const declineIncomingCall = () => {
    if (incomingCall && incomingCall.call) {
      incomingCall.call.reject();
      incomingCall = null;
    }
  };

  const formatPhoneNumber = (number: string): string => {
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    } else if (cleaned.length === 11 && cleaned.startsWith('1')) {
      return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
    }
    return number;
  };

  const getStatusVariant = () => {
    if (!isReady) return 'danger';
    if (hasActiveCall) return 'success';
    if (incomingCall) return 'warning';
    return 'gray';
  };

  const getStatusText = () => {
    if (isInitializing) return 'Initializing...';
    if (!isReady) return 'Offline';
    if (hasActiveCall) return 'In Call';
    if (incomingCall) return 'Incoming Call';
    return 'Ready';
  };

  const clearError = () => {
    error = null;
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Phone Dialer</h3>
      <Badge variant={getStatusVariant()}>
        {getStatusText()}
      </Badge>
    </div>
  {/snippet}

  <div class="space-y-4">
    {#if error}
      <div class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg" in:fly={{ y: -10, duration: 300 }}>
        <p class="text-red-800 dark:text-red-400 text-sm">{error}</p>
        <Button variant="secondary" size="sm" onclick={clearError} class="mt-1">
          Dismiss
        </Button>
      </div>
    {/if}

    {#if incomingCall}
      <div class="p-4 border-2 border-warning-500 bg-warning-50 dark:bg-warning-900/20 rounded-lg" in:scale={{ duration: 400 }}>
        <div class="text-center">
          <svg class="h-8 w-8 text-warning-500 mx-auto mb-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
          </svg>
          <p class="font-medium text-warning-800 dark:text-warning-400">Incoming Call</p>
          <p class="text-sm text-warning-700 dark:text-warning-500 mb-3">
            {formatPhoneNumber(incomingCall.from)}
          </p>
          <div class="flex gap-2 justify-center">
            <Button variant="success" size="sm" onclick={answerIncomingCall}>Answer</Button>
            <Button variant="danger" size="sm" onclick={declineIncomingCall}>Decline</Button>
          </div>
        </div>
      </div>
    {/if}

    {#if hasActiveCall && callStatus}
      <div class="p-3 border border-success-500 bg-success-50 dark:bg-success-900/20 rounded-lg" in:fly={{ y: -10, duration: 300 }}>
        <div class="text-center">
          <p class="text-sm font-medium text-success-800 dark:text-success-400">
            {callStatus.callDirection === 'inbound' ? 'Incoming from' : 'Calling'}:
            <span class="ml-1">
              {formatPhoneNumber(callStatus.callDirection === 'inbound' ? callStatus.callFrom : callStatus.callTo)}
            </span>
          </p>
          {#if callStatus.isMuted}
            <p class="text-xs text-success-600 dark:text-success-500 mt-1">🔇 Muted</p>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Phone Number Input -->
    <div>
      <label for="dialer-phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Phone Number
      </label>
      <input
        id="dialer-phone"
        type="tel"
        placeholder="+1 (555) 123-4567"
        bind:value={phoneNumber}
        disabled={hasActiveCall}
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white disabled:opacity-50"
      />
    </div>

    <!-- Dialer Pad -->
    <div class="grid grid-cols-3 gap-2">
      {#each dialerButtons.flat() as digit, i}
        <button
          class="aspect-square text-lg font-medium border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
          onclick={() => hasActiveCall ? sendDTMF(digit) : addDigit(digit)}
          disabled={isInitializing || !isReady}
          in:scale={{ duration: 300, delay: i * 30, easing: quintOut }}
        >
          {digit}
        </button>
      {/each}
    </div>

    <div class="h-px bg-gray-200 dark:bg-gray-700"></div>

    <!-- Call Controls -->
    <div class="flex gap-2">
      {#if !hasActiveCall}
        <Button
          variant="success"
          size="lg"
          onclick={makeCall}
          disabled={!isReady || !phoneNumber.trim() || isInitializing}
          class="flex-1"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
          </svg>
          Call
        </Button>
      {:else}
        <Button
          variant={isMuted ? 'warning' : 'secondary'}
          size="lg"
          onclick={toggleMute}
        >
          <svg class="w-5 h-5 mr-2" fill={isMuted ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
          </svg>
          {isMuted ? 'Unmute' : 'Mute'}
        </Button>
        <Button
          variant="danger"
          size="lg"
          onclick={hangupCall}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z"></path>
          </svg>
          Hang Up
        </Button>
      {/if}
    </div>

    <!-- Volume Control -->
    {#if hasActiveCall}
      <div class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg" in:fly={{ y: 10, duration: 300 }}>
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
          </svg>
          <label for="dialer-volume" class="sr-only">Call volume</label>
          <input
            id="dialer-volume"
            type="range"
            min="0"
            max="100"
            bind:value={volume}
            class="flex-1"
          />
          <span class="text-sm text-gray-500 w-12">{volume}%</span>
        </div>
      </div>
    {/if}

    <!-- Quick Actions -->
    {#if !hasActiveCall}
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Quick Dial:</p>
        <div class="flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            onclick={() => phoneNumber = '+1 (555) 123-4567'}
            disabled={hasActiveCall}
          >
            Demo
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onclick={() => phoneNumber = ''}
            disabled={hasActiveCall || !phoneNumber}
          >
            Clear
          </Button>
        </div>
      </div>
    {/if}
  </div>
</Card>
