<script lang="ts">
  /**
   * SMSComposer Component (Shared from ui-core)
   *
   * NOTE: This component will be extracted to @ocelot/ui-core package
   * when tools-core integration is complete. For now, we keep a copy here.
   *
   * Props:
   * - to: Phone number recipient
   * - message: Message body
   * - maxLength: Max message length (default 1600)
   * - onSend: Callback function for sending SMS
   */
  export let to: string = '';
  export let message: string = '';
  export let maxLength: number = 1600;
  export let onSend: (to: string, message: string) => Promise<void>;
  export let placeholder: string = 'Type your message...';

  let sending = false;

  $: charactersLeft = maxLength - message.length;
  $: segmentCount = Math.ceil(message.length / 160) || 1;
  $: isValid = to.trim() !== '' && message.trim() !== '';

  async function handleSend() {
    if (!isValid) {
      alert('Please enter both phone number and message');
      return;
    }

    sending = true;
    try {
      await onSend(to, message);
      // Clear form after successful send
      to = '';
      message = '';
    } catch (error) {
      console.error('Failed to send SMS:', error);
      alert('Failed to send SMS. Please try again.');
    } finally {
      sending = false;
    }
  }

  function formatPhoneNumber(value: string): string {
    // Remove all non-numeric characters except +
    const cleaned = value.replace(/[^\d+]/g, '');
    return cleaned;
  }

  function handlePhoneInput(event: Event) {
    const target = event.target as HTMLInputElement;
    to = formatPhoneNumber(target.value);
  }
</script>

<div class="sms-composer rounded-lg border bg-white p-6 shadow-sm">
  <!-- Phone Number Input -->
  <div class="mb-4">
    <label class="mb-2 block text-sm font-medium text-gray-700">
      Recipient <span class="text-red-500">*</span>
    </label>
    <input
      type="tel"
      bind:value={to}
      on:input={handlePhoneInput}
      placeholder="+1234567890"
      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      required
    />
    <p class="mt-1 text-xs text-gray-500">Include country code (e.g., +1)</p>
  </div>

  <!-- Message Input -->
  <div class="mb-4">
    <label class="mb-2 block text-sm font-medium text-gray-700">
      Message <span class="text-red-500">*</span>
    </label>
    <textarea
      bind:value={message}
      {placeholder}
      maxlength={maxLength}
      rows={6}
      class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      required
    ></textarea>
  </div>

  <!-- Character Counter -->
  <div class="mb-4 flex items-center justify-between text-sm">
    <div class="flex items-center gap-3">
      <span class="text-gray-500">
        {charactersLeft} character{charactersLeft !== 1 ? 's' : ''} left
      </span>
      <span class="text-gray-500">
        {segmentCount} SMS segment{segmentCount !== 1 ? 's' : ''}
      </span>
    </div>
    <div class="text-xs text-gray-400">
      {message.length} / {maxLength}
    </div>
  </div>

  <!-- Info Alert -->
  {#if segmentCount > 1}
    <div class="mb-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm">
      <p class="font-medium text-amber-900">⚠️ Multiple SMS Segments</p>
      <p class="mt-1 text-xs text-amber-800">
        This message will be sent as {segmentCount} SMS messages.
      </p>
    </div>
  {/if}

  <!-- Send Button -->
  <div class="flex justify-end">
    <button
      type="button"
      on:click={handleSend}
      disabled={sending || !isValid}
      class="rounded-md bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
    >
      {sending ? 'Sending...' : `Send SMS${segmentCount > 1 ? ` (${segmentCount} segments)` : ''}`}
    </button>
  </div>
</div>

<style>
  .sms-composer {
    /* Component-specific styles */
  }
</style>
