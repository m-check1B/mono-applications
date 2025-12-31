<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api/client';
  import { logger } from '$lib/utils/logger';
  import { Mic, UploadCloud, Radio } from 'lucide-svelte';

  type Provider = 'gemini-native' | 'openai-realtime';
  interface VoiceProvidersResponse {
    providers: Record<string, boolean>;
  }
  interface VoiceSessionInitResponse {
    sessionId: string;
  }

  let voiceProvider: Provider = 'gemini-native';
let conversationHistory: Array<{ role: string; content: string; timestamp: Date }> = [];
let transcript = '';
let response = '';
let detectedIntent: string | null = null;
let voiceStatus: { providers: Record<string, boolean> } | null = null;
let sessionId: string | null = null;
  let isInitializing = false;
  let uploadError: string | null = null;
let recordingError: string | null = null;
let supportsRecording = false;
let isRecording = false;
let isProcessing = false;
let mediaRecorder: MediaRecorder | null = null;
  let recordingStream: MediaStream | null = null;
let audioChunks: Blob[] = [];
let shouldProcessRecording = true;
  const voiceProviderSelectId = 'voice-provider-select';

  onMount(async () => {
    supportsRecording =
      typeof navigator !== 'undefined' &&
      typeof navigator.mediaDevices?.getUserMedia === 'function' &&
      typeof MediaRecorder !== 'undefined';
    loadConversation();
    await initializeVoiceSession();
  });

  onDestroy(() => {
    stopRecording(true);
    cleanupRecording();
  });

  function loadConversation() {
    const saved = localStorage.getItem('voice_conversation');
    if (saved) {
      try {
        conversationHistory = JSON.parse(saved).map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp)
        }));
      } catch (e) {
        logger.error('Failed to parse history', e);
      }
    }
  }

  async function initializeVoiceSession() {
    if (isInitializing) return;
    isInitializing = true;
    uploadError = null;
    try {
      const providersResponse = (await api.assistant.getProviders()) as VoiceProvidersResponse;
      voiceStatus = providersResponse;
      sessionId = 'ready'; // Voice service is stateless, no session init needed
    } catch (error: any) {
      uploadError = error.message || 'Failed to check voice providers.';
      logger.error('Failed to initialize voice session', error);
    } finally {
      isInitializing = false;
    }
  }

  async function handleFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;
    try {
      await processVoiceFile(file);
    } finally {
      target.value = '';
    }
  }

  async function processVoiceFile(file: File) {
    await processAudioBlob(file, file.type || 'audio/webm');
  }

  async function processAudioBlob(audio: Blob, mimetype: string) {
    if (!sessionId) {
      await initializeVoiceSession();
      if (!sessionId) return;
    }
    uploadError = null;
    recordingError = null;
    isProcessing = true;
    try {
      // Step 1: Transcribe audio
      const transcribeResult: any = await api.assistant.transcribeAudio(
        audio,
        'en',
        voiceProvider === 'gemini-native' ? 'gemini' : voiceProvider === 'openai-realtime' ? 'deepgram' : undefined
      );

      transcript = transcribeResult.transcript || 'No transcript available';

      // Step 2: Process with AI to get intent and response
      const processResult: any = await api.assistant.processVoice({
        transcript: transcript,
        recordingId: transcribeResult.id
      });

      response = processResult.response || 'Understood.';
      detectedIntent = processResult.intent || null;

      conversationHistory = [
        ...conversationHistory,
        { role: 'user', content: transcript, timestamp: new Date() },
        { role: 'assistant', content: response, timestamp: new Date() }
      ];
      localStorage.setItem('voice_conversation', JSON.stringify(conversationHistory));
    } catch (error: any) {
      uploadError = error.message || 'Failed to process audio';
      logger.error('Failed to process audio', error);
    } finally {
      isProcessing = false;
    }
  }

  function cleanupRecording() {
    recordingStream?.getTracks().forEach((track) => track.stop());
    recordingStream = null;
    mediaRecorder = null;
    audioChunks = [];
  }

  function getRecorderOptions(): MediaRecorderOptions | undefined {
    if (typeof MediaRecorder === 'undefined' || typeof MediaRecorder.isTypeSupported !== 'function') {
      return undefined;
    }
    const preferredTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus'];
    for (const type of preferredTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        return { mimeType: type };
      }
    }
    return undefined;
  }

  async function startRecording() {
    if (isRecording) return;
    recordingError = null;

    if (!supportsRecording) {
      recordingError = 'Live recording is not supported in this browser.';
      return;
    }

    try {
      if (!sessionId) {
        await initializeVoiceSession();
        if (!sessionId) return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recordingStream = stream;
      const options = getRecorderOptions();
      mediaRecorder = new MediaRecorder(stream, options);
      audioChunks = [];
      shouldProcessRecording = true;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onerror = (event) => {
        recordingError = event.error?.message || 'Recording failed.';
        stopRecording(true);
      };

      mediaRecorder.onstop = async () => {
        const chunks = [...audioChunks];
        const mimeType = mediaRecorder?.mimeType || options?.mimeType || 'audio/webm';
        cleanupRecording();
        const shouldProcess = shouldProcessRecording && chunks.length > 0;
        shouldProcessRecording = true;
        const blob = new Blob(chunks, { type: mimeType });
        if (shouldProcess) {
          await processAudioBlob(blob, mimeType);
        }
        isRecording = false;
      };

      mediaRecorder.start();
      isRecording = true;
    } catch (error: any) {
      recordingError = error?.message || 'Unable to access microphone.';
      cleanupRecording();
    }
  }

  function stopRecording(skipProcessing = false) {
    if (!mediaRecorder) {
      cleanupRecording();
      isRecording = false;
      return;
    }

    if (skipProcessing) {
      shouldProcessRecording = false;
    }

    if (mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    } else {
      cleanupRecording();
    }
    isRecording = false;
  }

  function clearConversation() {
    if (confirm('Clear conversation history?')) {
      conversationHistory = [];
      transcript = '';
      response = '';
      localStorage.removeItem('voice_conversation');
    }
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold flex items-center gap-2">
        <Radio class="w-8 h-8 text-primary" />
        Voice Interface
      </h1>
      <p class="text-muted-foreground mt-1">Upload or record audio to let the assistant respond.</p>
    </div>
    <button
      onclick={clearConversation}
      class="px-4 py-2 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors"
    >
      Clear History
    </button>
  </div>

  {#if transcript}
    <div class="border-2 border-black dark:border-white bg-secondary/20 p-4 space-y-2">
      <div class="text-xs font-bold uppercase text-muted-foreground">Transcript</div>
      <p class="font-mono text-sm">{transcript}</p>
      {#if detectedIntent}
        <span class="text-[10px] font-black uppercase px-2 py-1 border border-black dark:border-white bg-white dark:bg-black">
          Intent: {detectedIntent}
        </span>
      {/if}
    </div>
  {/if}

  <div class="bg-card border border-border rounded-lg p-6 space-y-4">
    <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <label class="text-sm font-medium" for={voiceProviderSelectId}>Voice Provider</label>
        <select
          id={voiceProviderSelectId}
          bind:value={voiceProvider}
          onchange={initializeVoiceSession}
          class="mt-1 px-3 py-2 bg-background border border-input rounded-md"
        >
          <option value="gemini-native">Gemini Native</option>
          <option value="openai-realtime">OpenAI Realtime</option>
        </select>
        {#if voiceStatus}
          <p class="text-xs text-muted-foreground mt-1">
            Available: {Object.keys(voiceStatus.providers || {}).join(', ') || 'none'}
          </p>
        {/if}
      </div>
      <div class="flex flex-col sm:flex-row gap-4 items-start w-full md:w-auto">
        <div class="flex flex-col items-start flex-1">
          <input type="file" class="hidden" id="voice-file" accept="audio/*" onchange={handleFileChange} />
          <button
            class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            onclick={() => document.getElementById('voice-file')?.click()}
            disabled={isProcessing}
          >
            <UploadCloud class="w-4 h-4" />
            Upload Audio
          </button>
          <p class="text-xs text-muted-foreground mt-1">Supported formats: webm, wav, mp3</p>
        </div>
        <div class="flex flex-col items-start flex-1">
          <button
            class={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              isRecording
                ? 'bg-destructive text-destructive-foreground hover:bg-destructive/80'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
            onclick={() => (isRecording ? stopRecording() : startRecording())}
            disabled={!supportsRecording || (isProcessing && !isRecording)}
          >
            <Mic class="w-4 h-4" />
            {isRecording ? 'Stop Recording' : 'Record Live Audio'}
          </button>
          <p class="text-xs text-muted-foreground mt-1">
            {supportsRecording
              ? isRecording
                ? 'Recording in progress...'
                : 'Capture audio directly from your microphone.'
              : 'Your browser does not support live recording.'}
          </p>
          {#if recordingError}
            <p class="text-xs text-destructive mt-1">{recordingError}</p>
          {/if}
        </div>
      </div>
    </div>
    {#if uploadError}
      <p class="text-sm text-destructive">{uploadError}</p>
    {/if}
  </div>

  <div class="bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20 rounded-lg p-8 space-y-4">
    <div class="flex flex-col items-center space-y-4">
      <div class="w-24 h-24 rounded-full bg-primary flex items-center justify-center">
        <Mic class="w-12 h-12 text-primary-foreground" />
      </div>
      <p class="text-lg font-semibold">Choose a provider and upload audio to receive an AI response.</p>
    </div>
    {#if isRecording}
      <div class="w-full max-w-2xl p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-900 dark:text-yellow-100">
        Recording... click stop to send audio to the assistant.
      </div>
    {:else if isProcessing}
      <div class="w-full max-w-2xl p-4 bg-card border border-border rounded-lg">
        Processing audio, please wait...
      </div>
    {/if}
    {#if transcript}
      <div class="w-full max-w-2xl p-4 bg-card border border-border rounded-lg">
        <p class="text-sm text-muted-foreground mb-1">You said:</p>
        <p class="font-medium">{transcript}</p>
      </div>
    {/if}
    {#if response}
      <div class="w-full max-w-2xl p-4 bg-primary/5 border border-primary/20 rounded-lg">
        <p class="text-sm text-muted-foreground mb-1">Assistant reply:</p>
        <p>{response}</p>
      </div>
    {/if}
  </div>

  {#if conversationHistory.length > 0}
    <div class="bg-card border border-border rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">Conversation History</h2>
      <div class="space-y-3 max-h-96 overflow-y-auto">
        {#each conversationHistory as message (message.timestamp.getTime())}
          <div class="p-3 rounded-lg {message.role === 'user' ? 'bg-primary/10 ml-8' : 'bg-accent/50 mr-8'}">
            <div class="text-xs text-muted-foreground mb-1">
              {message.role === 'user' ? 'You' : 'Assistant'} •
              {new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }).format(message.timestamp)}
            </div>
            <p>{message.content}</p>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
