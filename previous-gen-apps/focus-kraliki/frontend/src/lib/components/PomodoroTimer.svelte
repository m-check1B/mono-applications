<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  interface Props {
    duration?: number; // in seconds
    breakDuration?: number; // in seconds
    onComplete?: () => void;
  }

  let {
    duration = $bindable(25 * 60), // 25 minutes in seconds
    breakDuration = 5 * 60, // 5 minutes
    onComplete
  }: Props = $props();

  // State
  let timeLeft = $state(duration);
  let isRunning = $state(false);
  let isBreak = $state(false);
  let interval = $state<ReturnType<typeof setInterval> | undefined>(undefined);
  let sessions = $state(0);

  // Computed
  let progress = $derived(((duration - timeLeft) / duration) * 100);
  let minutes = $derived(Math.floor(timeLeft / 60));
  let seconds = $derived(timeLeft % 60);
  let displayTime = $derived(`${minutes}:${seconds.toString().padStart(2, '0')}`);

  function start() {
    isRunning = true;
    interval = setInterval(() => {
      timeLeft--;

      if (timeLeft <= 0) {
        complete();
      }
    }, 1000);
  }

  function pause() {
    isRunning = false;
    if (interval) {
      clearInterval(interval);
      interval = undefined;
    }
  }

  function reset() {
    pause();
    timeLeft = isBreak ? breakDuration : duration;
    isBreak = false;
  }

  function complete() {
    pause();

    // Toggle between work and break
    if (!isBreak) {
      sessions++;
    }
    isBreak = !isBreak;
    timeLeft = isBreak ? breakDuration : duration;

    // Play alert
    playAlert();

    // Show notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Pomodoro Timer', {
        body: isBreak ? 'Time for a break!' : 'Focus time!',
        icon: '/favicon.ico'
      });
    }

    // Call callback
    if (onComplete) {
      onComplete();
    }
  }

  function playAlert() {
    // Create audio context for beep
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    gainNode.gain.value = 0.3;

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.2);
  }

  function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  onMount(() => {
    requestNotificationPermission();
  });

  onDestroy(() => {
    if (interval) {
      clearInterval(interval);
      interval = undefined;
    }
  });
</script>

<div class="pomodoro-timer brutal-card bg-card p-8 relative overflow-hidden">
  <!-- Scanline effect for that terminal feel -->
  <div class="absolute inset-0 pointer-events-none opacity-[0.03] bg-grid-pattern"></div>
  <div class="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-white/5 to-transparent h-1 bg-[length:100%_4px] animate-scan-line"></div>

  <!-- Header -->
  <div class="relative z-10 text-center mb-8 border-b-2 border-border pb-6">
    <h2 class="text-3xl font-black uppercase tracking-tighter mb-2">
      {isBreak ? '☕ System Break' : '🎯 Focus Protocol'}
    </h2>
    <div class="flex items-center justify-center gap-4">
      <p class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-secondary px-2 py-0.5">
        Sessions: {sessions.toString().padStart(2, '0')}
      </p>
      <p class="text-[10px] font-bold uppercase tracking-widest {isRunning ? 'text-terminal-green animate-pulse' : 'text-system-red'}">
        Status: {isRunning ? 'ACTIVE' : 'IDLE'}
      </p>
    </div>
  </div>

  <!-- Timer Display -->
  <div class="relative z-10 flex flex-col items-center justify-center mb-8">
    <div class="text-8xl font-mono font-black tracking-widest mb-6 tabular-nums">
      {displayTime}
    </div>

    <!-- Brutalist Progress Bar -->
    <div class="w-full h-8 border-2 border-border bg-secondary relative overflow-hidden">
      <div
        class="h-full bg-terminal-green transition-all duration-1000 ease-linear"
        style="width: {progress}%"
      ></div>
      <!-- Grid overlay for the bar -->
      <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.1)_1px,transparent_1px)] bg-[size:20px_100%]"></div>
    </div>
    <div class="w-full flex justify-between mt-1">
      <span class="text-[9px] font-bold uppercase text-muted-foreground">0%</span>
      <span class="text-[9px] font-bold uppercase text-muted-foreground">Progress: {Math.round(progress)}%</span>
      <span class="text-[9px] font-bold uppercase text-muted-foreground">100%</span>
    </div>
  </div>

  <!-- Controls -->
  <div class="relative z-10 flex flex-col sm:flex-row justify-center gap-4">
    {#if !isRunning}
      <button
        onclick={start}
        class="btn btn-primary px-10 py-4 text-xl"
      >
        ▶ Initiate
      </button>
    {:else}
      <button
        onclick={pause}
        class="btn bg-accent text-accent-foreground px-10 py-4 text-xl"
      >
        ⏸ Suspend
      </button>
    {/if}

    <button
      onclick={reset}
      class="btn btn-secondary px-10 py-4 text-xl"
    >
      ↻ Reset
    </button>
  </div>

  <!-- Settings (Quick Access) -->
  <div class="relative z-10 mt-8 pt-6 border-t-2 border-border">
    <p class="text-[10px] font-bold uppercase tracking-widest text-center mb-4 text-muted-foreground">Preset Intervals</p>
    <div class="flex justify-center flex-wrap gap-3">
      <button
        onclick={() => { duration = 25 * 60; reset(); }}
        class="btn btn-sm {duration === 25 * 60 ? 'bg-terminal-green text-black' : 'bg-card'}"
      >
        25M
      </button>
      <button
        onclick={() => { duration = 50 * 60; reset(); }}
        class="btn btn-sm {duration === 50 * 60 ? 'bg-terminal-green text-black' : 'bg-card'}"
      >
        50M
      </button>
      <button
        onclick={() => { duration = 90 * 60; reset(); }}
        class="btn btn-sm {duration === 90 * 60 ? 'bg-terminal-green text-black' : 'bg-card'}"
      >
        90M
      </button>
    </div>
  </div>
</div>
