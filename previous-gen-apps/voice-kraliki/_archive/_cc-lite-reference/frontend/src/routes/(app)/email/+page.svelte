<script lang="ts">
  import { onMount } from 'svelte';
  import EmailComposer from '$lib/components/EmailComposer.svelte';
  import Badge from '$lib/components/shared/Badge.svelte';
  import Button from '$lib/components/shared/Button.svelte';

  interface Contact {
    id: string;
    name: string;
    email: string;
    phone?: string;
    company?: string;
  }

  interface SentEmail {
    id: string;
    to: string;
    subject: string;
    body: string;
    sent_at: string;
    status: 'sent' | 'failed' | 'pending';
  }

  let contacts: Contact[] = [];
  let sentEmails: SentEmail[] = [];
  let loading = true;
  let selectedContact: Contact | null = null;

  // Email composer state
  let composerTo = '';
  let composerSubject = '';
  let composerBody = '';

  async function loadContacts() {
    try {
      const response = await fetch('http://localhost:3018/api/contacts');
      if (response.ok) {
        contacts = await response.json();
      }
    } catch (err) {
      console.error('Failed to load contacts:', err);
    }
  }

  async function loadSentEmails() {
    try {
      const response = await fetch('http://localhost:3018/api/email/sent');
      if (response.ok) {
        const data = await response.json();
        sentEmails = data.items || [];
      }
    } catch (err) {
      console.error('Failed to load sent emails:', err);
    } finally {
      loading = false;
    }
  }

  function selectContact(contact: Contact) {
    selectedContact = contact;
    composerTo = contact.email;
  }

  function handleEmailSent() {
    // Reload sent emails
    loadSentEmails();
    selectedContact = null;
  }

  onMount(() => {
    loadContacts();
    loadSentEmails();
  });
</script>

<div class="email-page">
  <div class="page-header">
    <div>
      <h1>Email Communications</h1>
      <p class="subtitle">Send emails to customers and contacts</p>
    </div>
  </div>

  <div class="email-grid">
    <!-- Left Panel: Contacts -->
    <div class="contacts-panel">
      <div class="panel-header">
        <h2>Contacts</h2>
        <Badge>{contacts.length}</Badge>
      </div>

      {#if contacts.length === 0}
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <p>No contacts yet</p>
        </div>
      {:else}
        <div class="contact-list">
          {#each contacts as contact}
            <button
              class="contact-item"
              class:selected={selectedContact?.id === contact.id}
              on:click={() => selectContact(contact)}
            >
              <div class="contact-avatar">
                {contact.name.split(' ').map(n => n[0]).join('').toUpperCase()}
              </div>
              <div class="contact-info">
                <div class="contact-name">{contact.name}</div>
                <div class="contact-email">{contact.email}</div>
                {#if contact.company}
                  <div class="contact-company">{contact.company}</div>
                {/if}
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Middle Panel: Email Composer -->
    <div class="composer-panel">
      <EmailComposer
        bind:to={composerTo}
        bind:subject={composerSubject}
        bind:body={composerBody}
        onSent={handleEmailSent}
      />
    </div>

    <!-- Right Panel: Sent Emails -->
    <div class="sent-panel">
      <div class="panel-header">
        <h2>Sent Emails</h2>
        <Badge>{sentEmails.length}</Badge>
      </div>

      {#if loading}
        <div class="loading">Loading sent emails...</div>
      {:else if sentEmails.length === 0}
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
            <polyline points="22,6 12,13 2,6"/>
          </svg>
          <p>No sent emails yet</p>
        </div>
      {:else}
        <div class="sent-list">
          {#each sentEmails as email}
            <div class="sent-item">
              <div class="sent-header">
                <span class="sent-to">{email.to}</span>
                <Badge variant={email.status === 'sent' ? 'success' : email.status === 'failed' ? 'error' : 'warning'}>
                  {email.status}
                </Badge>
              </div>
              <div class="sent-subject">{email.subject}</div>
              <div class="sent-preview">{email.body.substring(0, 100)}...</div>
              <div class="sent-time">{new Date(email.sent_at).toLocaleString()}</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .email-page {
    padding: 2rem;
    max-width: 1600px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    color: #64748b;
    margin: 0;
  }

  .email-grid {
    display: grid;
    grid-template-columns: 300px 1fr 350px;
    gap: 1.5rem;
    min-height: calc(100vh - 200px);
  }

  .contacts-panel,
  .composer-panel,
  .sent-panel {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    overflow: hidden;
  }

  .contacts-panel,
  .sent-panel {
    display: flex;
    flex-direction: column;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    color: #64748b;
    text-align: center;
  }

  .empty-state svg {
    opacity: 0.3;
    margin-bottom: 1rem;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    color: #64748b;
  }

  .contact-list,
  .sent-list {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
  }

  .contact-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    background: white;
    margin-bottom: 0.75rem;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
  }

  .contact-item:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }

  .contact-item.selected {
    background: #eff6ff;
    border-color: #3b82f6;
  }

  .contact-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #3b82f6;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
  }

  .contact-info {
    flex: 1;
    min-width: 0;
  }

  .contact-name {
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .contact-email {
    font-size: 0.875rem;
    color: #64748b;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .contact-company {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 0.25rem;
  }

  .sent-item {
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    margin-bottom: 0.75rem;
    background: white;
  }

  .sent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .sent-to {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.875rem;
  }

  .sent-subject {
    font-weight: 600;
    color: #334155;
    margin-bottom: 0.5rem;
  }

  .sent-preview {
    font-size: 0.875rem;
    color: #64748b;
    line-height: 1.5;
    margin-bottom: 0.5rem;
  }

  .sent-time {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  @media (max-width: 1200px) {
    .email-grid {
      grid-template-columns: 1fr;
    }

    .contacts-panel,
    .sent-panel {
      max-height: 400px;
    }
  }
</style>
