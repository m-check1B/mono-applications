<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import SMSComposer from '$lib/components/SMSComposer.svelte';

  interface SMSMessage {
    id: string;
    from_number: string;
    to_number: string;
    body: string;
    direction: 'inbound' | 'outbound';
    status: string;
    created_at: string;
  }

  interface SMSConversation {
    contact_number: string;
    contact_name: string;
    last_message: string;
    unread_count: number;
    last_message_at: string;
  }

  let messages = writable<SMSMessage[]>([]);
  let conversations = writable<SMSConversation[]>([]);
  let loading = true;
  let error: string | null = null;
  let selectedConversation: string | null = null;

  // SMS composer state
  let composerOpen = false;
  let composerRecipient = '';
  let composerMessage = '';

  async function loadInbox() {
    try {
      loading = true;
      error = null;

      const response = await fetch('http://localhost:3018/api/sms/inbox');

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      messages.set(data.items || []);

      // Load conversations
      const convResponse = await fetch('http://localhost:3018/api/sms/conversations');
      if (convResponse.ok) {
        const convData = await convResponse.json();
        conversations.set(convData || []);
      }

    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load inbox';
      console.error('Error loading SMS inbox:', err);
    } finally {
      loading = false;
    }
  }

  async function handleSendSMS(to: string, body: string) {
    const response = await fetch('http://localhost:3018/api/sms/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        to_number: to,
        body: body
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to send SMS');
    }

    const newMessage = await response.json();
    messages.update(msgs => [newMessage, ...msgs]);

    // Close composer and reload
    composerOpen = false;
    await loadInbox();
  }

  function openComposer(number?: string) {
    composerOpen = true;
    if (number) {
      composerRecipient = number;
    } else {
      composerRecipient = '';
    }
    composerMessage = '';
  }

  function closeComposer() {
    composerOpen = false;
    composerRecipient = '';
    composerMessage = '';
  }

  onMount(() => {
    loadInbox();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadInbox, 30000);
    return () => clearInterval(interval);
  });
</script>

<div class="sms-inbox-container">
  <div class="header">
    <h1>SMS Inbox</h1>
    <button class="btn-primary" on:click={() => openComposer()}>
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      New Message
    </button>
  </div>

  {#if error}
    <div class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {error}
    </div>
  {/if}

  <div class="content-grid">
    <!-- Conversations List -->
    <div class="conversations-panel">
      <h2>Conversations</h2>

      {#if loading}
        <div class="loading">Loading conversations...</div>
      {:else if $conversations.length === 0}
        <div class="empty-state">
          <p>No conversations yet</p>
          <button class="btn-secondary" on:click={() => openComposer()}>
            Start a conversation
          </button>
        </div>
      {:else}
        <div class="conversation-list">
          {#each $conversations as conv}
            <button
              class="conversation-item"
              class:active={selectedConversation === conv.contact_number}
              on:click={() => {
                selectedConversation = conv.contact_number;
                openComposer(conv.contact_number);
              }}
            >
              <div class="conv-header">
                <span class="conv-name">{conv.contact_name || conv.contact_number}</span>
                {#if conv.unread_count > 0}
                  <span class="unread-badge">{conv.unread_count}</span>
                {/if}
              </div>
              <p class="conv-preview">{conv.last_message}</p>
              <span class="conv-time">{new Date(conv.last_message_at).toLocaleTimeString()}</span>
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Messages Panel -->
    <div class="messages-panel">
      <h2>Messages</h2>

      {#if loading}
        <div class="loading">Loading messages...</div>
      {:else if $messages.length === 0}
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <p>No messages yet</p>
        </div>
      {:else}
        <div class="message-list">
          {#each $messages as msg}
            <div class="message-item" class:inbound={msg.direction === 'inbound'} class:outbound={msg.direction === 'outbound'}>
              <div class="message-header">
                <span class="message-from">
                  {msg.direction === 'inbound' ? `From ${msg.from_number}` : `To ${msg.to_number}`}
                </span>
                <span class="message-time">{new Date(msg.created_at).toLocaleString()}</span>
              </div>
              <div class="message-body">{msg.body}</div>
              <div class="message-status">{msg.status}</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- SMS Composer Modal (using SMSComposer component from ui-core) -->
  {#if composerOpen}
    <div class="modal-overlay" on:click={closeComposer}>
      <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
          <h2>New SMS Message</h2>
          <button class="btn-close" on:click={closeComposer}>×</button>
        </div>

        <SMSComposer
          to={composerRecipient}
          message={composerMessage}
          maxLength={1600}
          onSend={handleSendSMS}
          placeholder="Type your SMS message..."
        />
      </div>
    </div>
  {/if}
</div>

<style>
  .sms-inbox-container {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #2563eb;
  }

  .btn-secondary {
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-weight: 500;
  }

  .alert {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .alert-error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;
    height: calc(100vh - 200px);
  }

  .conversations-panel,
  .messages-panel {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 1.5rem;
    overflow-y: auto;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1e293b;
  }

  .loading,
  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #64748b;
  }

  .empty-state svg {
    margin: 0 auto 1rem;
    opacity: 0.3;
  }

  .conversation-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .conversation-item {
    width: 100%;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    background: white;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
  }

  .conversation-item:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }

  .conversation-item.active {
    background: #eff6ff;
    border-color: #3b82f6;
  }

  .conv-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .conv-name {
    font-weight: 600;
    color: #1e293b;
  }

  .unread-badge {
    background: #3b82f6;
    color: white;
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 1rem;
    font-weight: 600;
  }

  .conv-preview {
    color: #64748b;
    font-size: 0.875rem;
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .conv-time {
    color: #94a3b8;
    font-size: 0.75rem;
  }

  .message-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .message-item {
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
  }

  .message-item.inbound {
    background: #f8fafc;
    border-left: 3px solid #10b981;
  }

  .message-item.outbound {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .message-from {
    font-weight: 600;
    color: #1e293b;
  }

  .message-time {
    color: #64748b;
  }

  .message-body {
    color: #334155;
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }

  .message-status {
    font-size: 0.75rem;
    color: #94a3b8;
    text-transform: capitalize;
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 0.75rem;
    padding: 2rem;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .btn-close {
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: #64748b;
    line-height: 1;
  }
</style>
