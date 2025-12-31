<script lang="ts">
  import { onMount } from 'svelte';

  interface Agent {
    name: string;
    status: 'online' | 'idle' | 'error';
    task?: string;
  }

  interface PageData {
    agents: Agent[];
  }

  let { data }: { data: PageData } = $props();

  // Webcam state
  let videoElement: HTMLVideoElement | undefined = $state(undefined);
  let canvasElement: HTMLCanvasElement | undefined = $state(undefined);
  let stream: MediaStream | null = $state(null);
  let isCameraActive = $state(false);
  let captures = $state<string[]>([]);
  let cameraError = $state<string | null>(null);
  let sendingCapture = $state(false);

  // Voice/AI conversation state
  let isRecording = $state(false);
  let recognition: any = null;
  let sttSupported = $state(false);
  let voiceMessage = $state('');
  let conversation = $state<Array<{ role: 'user' | 'ai'; message: string; timestamp: Date }>>([]);
  let sendingMessage = $state(false);

  function getStatusColor(status: string): string {
    switch (status) {
      case 'online': return '#33ff00';
      case 'idle': return '#6b7280';
      case 'error': return '#ff4444';
      default: return '#6b7280';
    }
  }

  function countByStatus(status: string): number {
    return data.agents.filter(a => a.status === status).length;
  }

  async function startCamera() {
    cameraError = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: 'user' },
        audio: false
      });

      if (videoElement) {
        videoElement.srcObject = stream;
        videoElement.play();
        isCameraActive = true;
      }
    } catch (e) {
      cameraError = e instanceof Error ? e.message : 'Failed to access camera';
      console.error('Camera error:', e);
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    if (videoElement) {
      videoElement.srcObject = null;
    }
    isCameraActive = false;
  }

  function captureFrame() {
    if (!videoElement || !canvasElement) return;

    const context = canvasElement.getContext('2d');
    if (!context) return;

    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0);

    const imageData = canvasElement.toDataURL('image/jpeg', 0.8);
    captures = [imageData, ...captures].slice(0, 10); // Keep last 10 captures
  }

  async function sendCaptureToComms(imageData: string) {
    sendingCapture = true;
    try {
      const timestamp = new Date().toLocaleString();
      const message = `📸 Visual capture from reception at ${timestamp}`;

      await fetch('/api/comms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: 'reception-camera',
          topic: 'visual',
          message: `${message}\n[Image data: ${imageData.substring(0, 100)}...]`
        })
      });

      // Show success feedback
      cameraError = null;
    } catch (e) {
      cameraError = 'Failed to send capture to comms';
    } finally {
      sendingCapture = false;
    }
  }

  function deleteCapture(index: number) {
    captures = captures.filter((_, i) => i !== index);
  }

  // Initialize Speech-to-Text
  function initSTT() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      sttSupported = false;
      return;
    }

    sttSupported = true;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      voiceMessage = finalTranscript + interimTranscript;
    };

    recognition.onerror = (event: any) => {
      console.error('STT error:', event.error);
      isRecording = false;
      if (event.error === 'not-allowed') {
        cameraError = 'Microphone access denied';
      }
    };

    recognition.onend = () => {
      if (isRecording) {
        recognition.start();
      }
    };
  }

  function toggleRecording() {
    if (!recognition) return;

    if (isRecording) {
      recognition.stop();
      isRecording = false;
    } else {
      recognition.start();
      isRecording = true;
    }
  }

  async function sendVoiceToAI() {
    if (!voiceMessage.trim() || sendingMessage) return;

    sendingMessage = true;
    const userMessage = voiceMessage.trim();

    // Add user message to conversation
    conversation = [...conversation, {
      role: 'user',
      message: userMessage,
      timestamp: new Date()
    }];

    // Clear input
    voiceMessage = '';

    try {
      // Send to comms API
      const response = await fetch('/api/comms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: 'see-multimodal',
          topic: 'voice',
          message: userMessage
        })
      });

      if (response.ok) {
        // Simulate AI response (for now, just echo confirmation)
        // In the future, this could be enhanced to query actual AI
        conversation = [...conversation, {
          role: 'ai',
          message: `Message received: "${userMessage}". Sent to agent swarm for processing.`,
          timestamp: new Date()
        }];
      }

      cameraError = null;
    } catch (e) {
      cameraError = 'Failed to send message to AI';
      console.error('AI send error:', e);
    } finally {
      sendingMessage = false;
    }
  }

  function clearConversation() {
    conversation = [];
  }

  onMount(() => {
    // Initialize Speech-to-Text
    initSTT();

    // Cleanup camera and recognition on unmount
    return () => {
      stopCamera();
      if (recognition) {
        recognition.stop();
      }
    };
  });
</script>

<div class="page">
  <div class="page-header">
    <h2 class="glitch">Kraliki See // Multimodal Input</h2>
    <p class="subtitle">Visual + Voice AI Interface</p>
  </div>

  <div class="content">
    <!-- Visual Input (Camera) -->
    <div class="card camera-card">
      <h3>📹 VISUAL_INPUT // RECEPTION</h3>

      <div class="camera-container">
        {#if !isCameraActive}
          <div class="camera-placeholder">
            <span class="placeholder-icon">📹</span>
            <p class="placeholder-text">Camera inactive</p>
            <button class="brutal-btn" onclick={startCamera}>
              START CAMERA
            </button>
          </div>
        {:else}
          <div class="video-wrapper">
            <video bind:this={videoElement} class="video-preview" autoplay muted></video>
            <canvas bind:this={canvasElement} style="display: none;"></canvas>
            <div class="camera-controls">
              <button class="brutal-btn capture" onclick={captureFrame}>
                📸 CAPTURE
              </button>
              <button class="brutal-btn stop" onclick={stopCamera}>
                ⏹ STOP
              </button>
            </div>
          </div>
        {/if}

        {#if cameraError}
          <div class="camera-error">
            ⚠️ {cameraError}
          </div>
        {/if}
      </div>

      <!-- Captured Images -->
      {#if captures.length > 0}
        <div class="captures-section">
          <h4>RECENT CAPTURES ({captures.length})</h4>
          <div class="captures-grid">
            {#each captures as capture, index}
              <div class="capture-item">
                <img src={capture} alt="Capture {index + 1}" />
                <div class="capture-actions">
                  <button
                    class="action-btn send"
                    onclick={() => sendCaptureToComms(capture)}
                    disabled={sendingCapture}
                  >
                    📤
                  </button>
                  <button
                    class="action-btn delete"
                    onclick={() => deleteCapture(index)}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <!-- Status Summary -->
    <div class="status-summary">
      <div class="status-card online">
        <span class="status-dot" style="background: #33ff00;"></span>
        <span class="status-count">{countByStatus('online')}</span>
        <span class="status-label">ONLINE</span>
      </div>
      <div class="status-card idle">
        <span class="status-dot" style="background: #6b7280;"></span>
        <span class="status-count">{countByStatus('idle')}</span>
        <span class="status-label">IDLE</span>
      </div>
      <div class="status-card error">
        <span class="status-dot" style="background: #ff4444;"></span>
        <span class="status-count">{countByStatus('error')}</span>
        <span class="status-label">ERROR</span>
      </div>
    </div>

    <!-- Voice/AI Conversation -->
    <div class="card voice-card">
      <h3>🎤 VOICE_INPUT // AI_CONVERSATION</h3>

      {#if !sttSupported}
        <div class="stt-error">
          ⚠️ Speech recognition not supported in this browser. Try Chrome or Edge.
        </div>
      {:else}
        <div class="voice-controls">
          <div class="input-row">
            <textarea
              class="voice-input"
              bind:value={voiceMessage}
              placeholder="Speak or type your message to AI..."
              rows="3"
            ></textarea>
            <button
              class="mic-btn"
              class:recording={isRecording}
              onclick={toggleRecording}
              type="button"
              title={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {#if isRecording}
                <span class="mic-icon recording-pulse">⏹</span>
              {:else}
                <span class="mic-icon">🎤</span>
              {/if}
            </button>
          </div>

          <div class="action-row">
            <button
              class="brutal-btn send-btn"
              onclick={sendVoiceToAI}
              disabled={!voiceMessage.trim() || sendingMessage}
            >
              {sendingMessage ? 'SENDING...' : '📤 SEND TO AI'}
            </button>
            {#if conversation.length > 0}
              <button class="brutal-btn clear-btn" onclick={clearConversation}>
                🗑️ CLEAR
              </button>
            {/if}
          </div>
        </div>

        <!-- Conversation History -->
        {#if conversation.length > 0}
          <div class="conversation-section">
            <h4>CONVERSATION HISTORY ({conversation.length})</h4>
            <div class="conversation-list">
              {#each conversation as msg}
                <div class="conversation-item" class:user={msg.role === 'user'} class:ai={msg.role === 'ai'}>
                  <div class="msg-header">
                    <span class="msg-role">{msg.role === 'user' ? '👤 YOU' : '🤖 AI'}</span>
                    <span class="msg-time">{msg.timestamp.toLocaleTimeString()}</span>
                  </div>
                  <div class="msg-content">{msg.message}</div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </div>

    <!-- Agent Status Bar -->
    <div class="card agent-card">
      <h3>ACTIVE_PROCESSES</h3>
      <div class="agent-grid">
        {#each data.agents as agent}
          <div class="agent-badge" style="border-color: {getStatusColor(agent.status)}">
            <span class="agent-dot" style="background: {getStatusColor(agent.status)};"></span>
            <span class="agent-name">{agent.name}</span>
            {#if agent.task}
              <span class="agent-task">{agent.task}</span>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>

<style>
  .page {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .page-header {
    border-bottom: 2px solid var(--border);
    padding-bottom: 16px;
  }

  .subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-top: 8px;
  }

  .content {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .status-summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .status-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 24px;
    background: var(--surface);
    border: 2px solid var(--border);
    box-shadow: 4px 4px 0 0 var(--border);
    flex: 1;
    min-width: 140px;
  }

  .status-card.online {
    border-color: var(--terminal-green);
  }

  .status-card.error {
    border-color: var(--system-red);
  }

  .status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    box-shadow: 0 0 8px currentColor;
  }

  .status-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px;
    font-weight: 700;
    color: var(--text-main);
  }

  .status-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.1em;
  }

  /* Voice/Conversation Styles */
  .voice-card {
    border-color: var(--purple-agent, #a855f7);
  }

  .voice-card h3 {
    color: var(--purple-agent, #a855f7);
  }

  .stt-error {
    padding: 16px;
    background: rgba(255, 68, 68, 0.1);
    border: 2px solid var(--system-red, #ff4444);
    color: var(--system-red, #ff4444);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-align: center;
  }

  .voice-controls {
    margin-top: 16px;
  }

  .input-row {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
  }

  .voice-input {
    flex: 1;
    padding: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-main);
    resize: vertical;
    min-height: 80px;
  }

  .voice-input:focus {
    outline: none;
    border-color: var(--purple-agent, #a855f7);
  }

  .mic-btn {
    padding: 12px 20px;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-main);
    font-size: 24px;
    cursor: pointer;
    transition: all 0.1s;
    min-width: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 2px 2px 0 0 var(--border);
  }

  .mic-btn:hover {
    transform: translate(-1px, -1px);
    box-shadow: 3px 3px 0 0 var(--border);
  }

  .mic-btn.recording {
    background: var(--system-red);
    border-color: var(--system-red);
    color: var(--void);
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .action-row {
    display: flex;
    gap: 12px;
  }

  .send-btn {
    flex: 1;
    background: var(--terminal-green);
    color: var(--void);
    border-color: var(--terminal-green);
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .clear-btn {
    background: var(--system-red, #ff4444);
    color: var(--void);
    border-color: var(--system-red, #ff4444);
  }

  .conversation-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid var(--border);
  }

  .conversation-section h4 {
    font-size: 12px;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: var(--purple-agent, #a855f7);
    text-transform: uppercase;
  }

  .conversation-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;
  }

  .conversation-item {
    padding: 12px;
    border: 2px solid var(--border);
    background: rgba(255, 255, 255, 0.02);
  }

  .conversation-item.user {
    border-left: 4px solid var(--cyan-data, #00d4ff);
  }

  .conversation-item.ai {
    border-left: 4px solid var(--purple-agent, #a855f7);
    background: rgba(168, 85, 247, 0.05);
  }

  .msg-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .msg-role {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
  }

  .msg-time {
    font-size: 10px;
    color: var(--text-muted);
  }

  .msg-content {
    font-size: 13px;
    line-height: 1.5;
    color: var(--text-main);
  }

  .agent-card h3 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    letter-spacing: 0.1em;
  }

  .agent-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .agent-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: var(--surface);
    border: 2px solid;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    box-shadow: 2px 2px 0 0 var(--border);
  }

  .agent-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .agent-name {
    color: var(--text-main);
    font-weight: 600;
  }

  .agent-task {
    color: var(--cyan-data);
    font-size: 10px;
  }

  /* Camera Styles */
  .camera-card {
    border-color: var(--cyan-data, #00d4ff);
  }

  .camera-container {
    margin-top: 16px;
  }

  .camera-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    background: rgba(255, 255, 255, 0.02);
    border: 2px dashed var(--border);
  }

  .placeholder-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .placeholder-text {
    color: var(--text-muted);
    font-size: 14px;
    margin-bottom: 20px;
  }

  .video-wrapper {
    position: relative;
  }

  .video-preview {
    width: 100%;
    max-width: 800px;
    height: auto;
    border: 2px solid var(--terminal-green);
    background: #000;
    display: block;
  }

  .camera-controls {
    display: flex;
    gap: 12px;
    margin-top: 12px;
  }

  .brutal-btn.capture {
    background: var(--terminal-green);
    color: var(--void);
    border-color: var(--terminal-green);
  }

  .brutal-btn.stop {
    background: var(--system-red, #ff4444);
    color: var(--void);
    border-color: var(--system-red, #ff4444);
  }

  .camera-error {
    margin-top: 12px;
    padding: 12px;
    background: rgba(255, 68, 68, 0.1);
    border: 2px solid var(--system-red, #ff4444);
    color: var(--system-red, #ff4444);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }

  .captures-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid var(--border);
  }

  .captures-section h4 {
    font-size: 12px;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: var(--cyan-data, #00d4ff);
    text-transform: uppercase;
  }

  .captures-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }

  .capture-item {
    position: relative;
    border: 2px solid var(--border);
    background: rgba(255, 255, 255, 0.02);
    overflow: hidden;
    transition: all 0.1s;
  }

  .capture-item:hover {
    border-color: var(--terminal-green);
    transform: translate(-2px, -2px);
    box-shadow: 4px 4px 0 0 var(--terminal-green);
  }

  .capture-item img {
    width: 100%;
    height: auto;
    display: block;
  }

  .capture-actions {
    display: flex;
    gap: 8px;
    padding: 8px;
    background: rgba(0, 0, 0, 0.8);
  }

  .action-btn {
    flex: 1;
    padding: 8px;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-main);
    font-size: 16px;
    cursor: pointer;
    transition: all 0.1s;
  }

  .action-btn:hover:not(:disabled) {
    transform: translate(-1px, -1px);
    box-shadow: 2px 2px 0 0 var(--border);
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-btn.send:hover:not(:disabled) {
    border-color: var(--terminal-green);
    background: var(--terminal-green);
  }

  .action-btn.delete:hover {
    border-color: var(--system-red, #ff4444);
    background: var(--system-red, #ff4444);
  }
</style>
