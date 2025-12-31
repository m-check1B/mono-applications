<script lang="ts">
  import { onMount } from 'svelte';
  import Button from './shared/Button.svelte';

  export let to: string = '';
  export let subject: string = '';
  export let body: string = '';
  export let onSent: (() => void) | undefined = undefined;

  interface EmailTemplate {
    id: string;
    name: string;
    subject: string;
    body: string;
  }

  const templates: EmailTemplate[] = [
    {
      id: 'blank',
      name: 'Blank Email',
      subject: '',
      body: ''
    },
    {
      id: 'follow_up',
      name: 'Call Follow-up',
      subject: 'Thank you for speaking with us today',
      body: `Dear Customer,

Thank you for taking the time to speak with us today. We appreciate your business and wanted to follow up on our conversation.

[Add specific details about the call here]

If you have any questions or need further assistance, please don't hesitate to reach out.

Best regards,
[Your Name]`
    },
    {
      id: 'meeting',
      name: 'Meeting Invite',
      subject: 'Meeting Invitation',
      body: `Dear Customer,

I would like to schedule a meeting with you to discuss [topic].

Proposed times:
- [Date/Time 1]
- [Date/Time 2]
- [Date/Time 3]

Please let me know which time works best for you, or suggest an alternative.

Looking forward to speaking with you.

Best regards,
[Your Name]`
    },
    {
      id: 'appointment',
      name: 'Appointment Confirmation',
      subject: 'Appointment Confirmation',
      body: `Dear Customer,

This is to confirm your appointment scheduled for:

Date: [Date]
Time: [Time]
Duration: [Duration]

If you need to reschedule, please contact us at least 24 hours in advance.

We look forward to meeting with you.

Best regards,
[Your Name]`
    }
  ];

  let selectedTemplate = 'blank';
  let sending = false;
  let error: string | null = null;
  let success = false;

  async function sendEmail() {
    if (!to || !subject || !body) {
      error = 'Please fill in all fields';
      return;
    }

    try {
      sending = true;
      error = null;
      success = false;

      const response = await fetch('http://localhost:3018/api/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to,
          subject,
          body,
          from: 'noreply@cc-lite.local'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send email');
      }

      success = true;

      // Reset form after successful send
      setTimeout(() => {
        to = '';
        subject = '';
        body = '';
        selectedTemplate = 'blank';
        success = false;

        if (onSent) {
          onSent();
        }
      }, 2000);

    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to send email';
      console.error('Error sending email:', err);
    } finally {
      sending = false;
    }
  }

  function loadTemplate(templateId: string) {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      subject = template.subject;
      body = template.body;
    }
  }

  $: {
    loadTemplate(selectedTemplate);
  }
</script>

<div class="email-composer">
  <div class="composer-header">
    <h3>Compose Email</h3>
    <div class="template-selector">
      <label for="template">Template:</label>
      <select id="template" bind:value={selectedTemplate}>
        {#each templates as template}
          <option value={template.id}>{template.name}</option>
        {/each}
      </select>
    </div>
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

  {#if success}
    <div class="alert alert-success">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      Email sent successfully!
    </div>
  {/if}

  <form class="composer-form" on:submit|preventDefault={sendEmail}>
    <div class="form-group">
      <label for="to">To:</label>
      <input
        id="to"
        type="email"
        bind:value={to}
        placeholder="recipient@example.com"
        required
      />
    </div>

    <div class="form-group">
      <label for="subject">Subject:</label>
      <input
        id="subject"
        type="text"
        bind:value={subject}
        placeholder="Email subject"
        required
      />
    </div>

    <div class="form-group">
      <label for="body">Message:</label>
      <textarea
        id="body"
        bind:value={body}
        rows={12}
        placeholder="Email body..."
        required
      ></textarea>
    </div>

    <div class="composer-actions">
      <Button type="submit" disabled={sending || !to || !subject || !body}>
        {sending ? 'Sending...' : 'Send Email'}
      </Button>
    </div>
  </form>
</div>

<style>
  .email-composer {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 1.5rem;
  }

  .composer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }

  .template-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .template-selector label {
    font-weight: 500;
    color: #64748b;
  }

  .template-selector select {
    padding: 0.5rem 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    cursor: pointer;
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

  .alert-success {
    background: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
  }

  .composer-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-weight: 500;
    color: #334155;
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    font-family: inherit;
    font-size: 1rem;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .form-group textarea {
    resize: vertical;
    min-height: 200px;
  }

  .composer-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.5rem;
  }
</style>
