<script lang="ts">
  import { onMount } from 'svelte';
  import Button from '../shared/Button.svelte';
  import { trpc } from '$lib/trpc/client';

  let { recording, onError } = $props<{
    recording: any;
    onError?: (error: Error) => void;
  }>();

  let audioElement: HTMLAudioElement;
  let isPlaying = $state(false);
  let currentTime = $state(0);
  let duration = $state(0);
  let playbackRate = $state(1.0);
  let isLoading = $state(true);
  let recordingUrl = $state<string | null>(null);

  // Fetch real recording URL from backend
  const fetchRecordingUrl = async () => {
    try {
      isLoading = true;

      // Check if recording has recordingId for fetching
      const recordingId = recording.recordingId || recording.id;

      if (!recordingId) {
        console.warn('No recording ID available');
        // Fallback to provided URL if any
        recordingUrl = recording.storageUrl || recording.recordingUrl;
        isLoading = false;
        return;
      }

      // Fetch real URL from backend
      const result = await trpc.telephony.getRecording.query({ recordingId });
      recordingUrl = result.url;

      console.log('✅ Fetched recording URL:', recordingUrl);
    } catch (err: any) {
      console.error('Failed to fetch recording URL:', err);

      // Fallback to provided URL or mock
      recordingUrl = recording.storageUrl || recording.recordingUrl || `/api/recordings/${recording.id}/audio`;

      if (onError) onError(new Error('Failed to load recording URL'));
    } finally {
      isLoading = false;
    }
  };

  onMount(async () => {
    // Fetch recording URL first
    await fetchRecordingUrl();

    if (audioElement) {
      audioElement.addEventListener('loadedmetadata', () => {
        duration = audioElement.duration;
      });

      audioElement.addEventListener('timeupdate', () => {
        currentTime = audioElement.currentTime;
      });

      audioElement.addEventListener('ended', () => {
        isPlaying = false;
      });

      audioElement.addEventListener('error', (e) => {
        console.error('Audio playback error:', e);
        if (onError) onError(new Error('Failed to play recording'));
      });
    }
  });

  const togglePlayPause = () => {
    if (!audioElement) return;

    if (isPlaying) {
      audioElement.pause();
    } else {
      audioElement.play();
    }
    isPlaying = !isPlaying;
  };

  const seek = (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (audioElement) {
      audioElement.currentTime = parseFloat(input.value);
    }
  };

  const changeSpeed = (rate: number) => {
    playbackRate = rate;
    if (audioElement) {
      audioElement.playbackRate = rate;
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const skip = (seconds: number) => {
    if (audioElement) {
      audioElement.currentTime = Math.max(0, Math.min(duration, audioElement.currentTime + seconds));
    }
  };
</script>

<div class="space-y-4">
  <!-- Audio Element -->
  <audio
    bind:this={audioElement}
    src={recordingUrl || ''}
    preload="metadata"
  ></audio>

  {#if isLoading}
    <div class="text-center py-4">
      <div class="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
      <p class="text-sm text-gray-500 mt-2">Loading recording...</p>
    </div>
  {:else}
    <!-- Player Controls -->
    <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
      <!-- Progress Bar -->
      <div class="mb-4">
        <input
          type="range"
          min="0"
          max={duration}
          value={currentTime}
          oninput={seek}
          class="w-full"
        />
        <div class="flex justify-between text-xs text-gray-500 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      <!-- Control Buttons -->
      <div class="flex items-center justify-center gap-2">
        <Button
          size="sm"
          variant="secondary"
          onclick={() => skip(-10)}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z"></path>
          </svg>
          -10s
        </Button>

        <Button
          size="lg"
          variant="primary"
          onclick={togglePlayPause}
        >
          {#if isPlaying}
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          {:else}
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-6.586-3.88A1 1 0 007 8.183v7.634a1 1 0 001.5.866l6.586-3.88a1 1 0 00 0-1.732z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          {/if}
        </Button>

        <Button
          size="sm"
          variant="secondary"
          onclick={() => skip(10)}
        >
          +10s
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z"></path>
          </svg>
        </Button>
      </div>

      <!-- Playback Speed -->
      <div class="flex items-center justify-center gap-2 mt-4">
        <span class="text-xs text-gray-500">Speed:</span>
        {#each [0.5, 0.75, 1.0, 1.25, 1.5, 2.0] as rate}
          <button
            class={`px-2 py-1 text-xs rounded ${playbackRate === rate ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
            onclick={() => changeSpeed(rate)}
          >
            {rate}x
          </button>
        {/each}
      </div>
    </div>

    <!-- Recording Info -->
    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>
        <span class="text-gray-500">Duration:</span>
        <span class="ml-2 font-medium">{formatTime(recording.duration || 0)}</span>
      </div>
      <div>
        <span class="text-gray-500">Size:</span>
        <span class="ml-2 font-medium">
          {recording.fileSize ? `${(recording.fileSize / (1024 * 1024)).toFixed(1)} MB` : '--'}
        </span>
      </div>
    </div>
  {/if}
</div>
