<script lang="ts">
  import { onMount } from 'svelte';
  import { Send, Paperclip, Mic, X } from 'lucide-svelte';

  interface Props {
    onSendMessage: (message: string, metadata?: Record<string, any>) => void | Promise<void>;
    disabled?: boolean;
    placeholder?: string;
  }

  interface AttachmentPayload {
    name: string;
    size: number;
    type: string;
    text?: string;
  }

  interface AttachmentState {
    file: File;
    payload: AttachmentPayload;
  }

  const MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024;
  const MAX_TEXT_PREVIEW_CHARS = 4000;
  const TEXT_FILE_RE = /\.(txt|md|csv|json|log)$/i;

  let { onSendMessage, disabled = false, placeholder = "Type your message..." }: Props = $props();

  let message = $state('');
  let isRecording = $state(false);
  let attachments = $state<AttachmentState[]>([]);
  let attachmentErrors = $state<string[]>([]);
  let textareaElement: HTMLTextAreaElement;
  let fileInputElement: HTMLInputElement;

  onMount(() => {
    // Auto-resize textarea
    if (textareaElement) {
      textareaElement.style.height = 'auto';
      textareaElement.style.height = textareaElement.scrollHeight + 'px';
    }
  });

  function handleInput() {
    if (textareaElement) {
      textareaElement.style.height = 'auto';
      textareaElement.style.height = Math.min(textareaElement.scrollHeight, 120) + 'px';
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  async function handleSend() {
    const trimmedMessage = message.trim();
    if ((trimmedMessage === '' && attachments.length === 0) || disabled) {
      return;
    }

    const payloads = attachments.map((attachment) => attachment.payload);
    const metadata = payloads.length > 0 ? { attachments: payloads } : undefined;
    const attachmentNames = payloads.map((payload) => payload.name).join(', ');
    const content = trimmedMessage || `Attached file${payloads.length === 1 ? '' : 's'}: ${attachmentNames}`;

    await onSendMessage(content, metadata);
    message = '';
    attachments = [];
    attachmentErrors = [];

    // Reset textarea height
    if (textareaElement) {
      textareaElement.style.height = 'auto';
    }
  }

  function handleFileSelect() {
    if (disabled) {
      return;
    }
    fileInputElement?.click();
  }

  async function handleFileChange(event: Event) {
    if (disabled) {
      return;
    }

    const target = event.currentTarget as HTMLInputElement;
    const files = Array.from(target.files ?? []);
    const nextAttachments: AttachmentState[] = [];
    const nextErrors: string[] = [];

    for (const file of files) {
      if (file.size > MAX_FILE_SIZE_BYTES) {
        nextErrors.push(`${file.name} is larger than 2 MB.`);
        continue;
      }

      let text: string | undefined;
      if (file.type.startsWith('text/') || TEXT_FILE_RE.test(file.name)) {
        try {
          const rawText = await file.text();
          text = rawText.length > MAX_TEXT_PREVIEW_CHARS
            ? `${rawText.slice(0, MAX_TEXT_PREVIEW_CHARS)}...`
            : rawText;
        } catch (error) {
          console.error('Failed to read file', error);
        }
      }

      nextAttachments.push({
        file,
        payload: {
          name: file.name,
          size: file.size,
          type: file.type || 'application/octet-stream',
          text
        }
      });
    }

    attachments = [...attachments, ...nextAttachments];
    attachmentErrors = nextErrors;
    target.value = '';
  }

  function removeAttachment(index: number) {
    attachments = attachments.filter((_, idx) => idx !== index);
  }

  function formatFileSize(size: number) {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }

  function toggleRecording() {
    if (isRecording) {
      // Stop recording
      isRecording = false;
      console.log('Recording stopped');
    } else {
      // Start recording
      isRecording = true;
      console.log('Recording started');
    }
  }
</script>

<div class="flex items-end gap-3">
  <!-- Attachment Button -->
  <button
    onclick={handleFileSelect}
    class="flex size-10 items-center justify-center rounded-lg text-text-secondary hover:bg-secondary-hover disabled:opacity-50"
    disabled={disabled}
    title="Attach file"
  >
    <Paperclip class="size-5" />
  </button>

  <input
    bind:this={fileInputElement}
    type="file"
    class="hidden"
    onchange={handleFileChange}
    multiple
    disabled={disabled}
  />

  <!-- Message Input -->
  <div class="flex-1">
    <textarea
      bind:this={textareaElement}
      bind:value={message}
      oninput={handleInput}
      onkeydown={handleKeydown}
      placeholder={placeholder}
      disabled={disabled}
      class="w-full resize-none border-2 border-divider bg-background px-4 py-3 text-sm placeholder-text-muted focus:outline-none disabled:opacity-50 shadow-card"
      rows="1"
      style="max-height: 120px; min-height: 44px;"
    ></textarea>

    {#if attachmentErrors.length > 0}
      <p class="mt-2 text-xs text-red-500">{attachmentErrors.join(' ')}</p>
    {/if}

    {#if attachments.length > 0}
      <div class="mt-2 flex flex-wrap gap-2">
        {#each attachments as attachment, index}
          <div
            class="flex items-center gap-2 rounded-lg border border-divider bg-card px-2 py-1 text-xs text-text-secondary"
          >
            <span class="max-w-[180px] truncate">{attachment.payload.name}</span>
            <span class="text-text-muted">{formatFileSize(attachment.payload.size)}</span>
            <button
              class="text-text-muted hover:text-text-primary"
              onclick={() => removeAttachment(index)}
              title="Remove attachment"
              type="button"
            >
              <X class="size-3" />
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Voice Record Button -->
  <button
    onclick={toggleRecording}
    class="inline-flex size-10 items-center justify-center border-2 border-divider bg-card text-text-secondary shadow-card disabled:opacity-50"
    disabled={disabled}
    title={isRecording ? 'Stop recording' : 'Start recording'}
  >
    <Mic class="size-5 {isRecording ? 'text-red-500' : ''}" />
  </button>

  <!-- Send Button -->
  <button
    onclick={handleSend}
    class="inline-flex size-10 items-center justify-center border-2 border-divider bg-primary text-primary-foreground shadow-card disabled:opacity-50"
    disabled={disabled || (!message.trim() && attachments.length === 0)}
    title="Send message"
  >
    <Send class="size-5" />
  </button>
</div>

<style>
	/* Custom scrollbar for textarea */
	textarea::-webkit-scrollbar {
		width: 4px;
	}

	textarea::-webkit-scrollbar-track {
		background: transparent;
	}

	textarea::-webkit-scrollbar-thumb {
		background-color: var(--color-border-subtle);
		border-radius: 2px;
	}

	textarea::-webkit-scrollbar-thumb:hover {
		background-color: var(--color-border-default);
	}
</style>
