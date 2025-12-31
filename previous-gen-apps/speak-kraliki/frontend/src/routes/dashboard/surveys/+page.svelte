<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { accessToken, isAuthenticated } from '$stores/auth';
  import { surveys, type Survey } from '$api/client';
  import { t } from '$lib/i18n';

  let surveyList = $state<Survey[]>([]);
  let loading = $state(true);
  let showCreateModal = $state(false);

  // New survey form
  let newSurvey = $state({
    name: '',
    description: '',
    frequency: 'monthly' as const,
    questions: [{ id: 1, question: '', follow_up_count: 2 }],
  });

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    await loadSurveys();
  });

  async function loadSurveys() {
    try {
      loading = true;
      surveyList = await surveys.list($accessToken!);
    } catch (e) {
      console.error('Failed to load surveys', e);
    } finally {
      loading = false;
    }
  }

  async function createSurvey() {
    try {
      await surveys.create(newSurvey, $accessToken!);
      showCreateModal = false;
      newSurvey = {
        name: '',
        description: '',
        frequency: 'monthly',
        questions: [{ id: 1, question: '', follow_up_count: 2 }],
      };
      await loadSurveys();
    } catch (e) {
      console.error('Failed to create survey', e);
    }
  }

  async function launchSurvey(id: string) {
    try {
      await surveys.launch(id, $accessToken!);
      await loadSurveys();
    } catch (e) {
      console.error('Failed to launch survey', e);
    }
  }

  async function pauseSurvey(id: string) {
    try {
      await surveys.pause(id, $accessToken!);
      await loadSurveys();
    } catch (e) {
      console.error('Failed to pause survey', e);
    }
  }

  function addQuestion() {
    const nextId = Math.max(...newSurvey.questions.map((q) => q.id)) + 1;
    newSurvey.questions = [...newSurvey.questions, { id: nextId, question: '', follow_up_count: 2 }];
  }

  function removeQuestion(id: number) {
    if (newSurvey.questions.length > 1) {
      newSurvey.questions = newSurvey.questions.filter((q) => q.id !== id);
    }
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      draft: $t('status.draft'),
      scheduled: $t('status.scheduled'),
      active: $t('status.active'),
      paused: $t('status.paused'),
      completed: $t('status.completed'),
    };
    return labels[status] || status;
  }

  function getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      draft: 'text-muted-foreground',
      scheduled: 'text-cyan-data',
      active: 'text-terminal-green',
      paused: 'text-yellow-400',
      completed: 'text-gray-500',
    };
    return colors[status] || '';
  }

  function getFrequencyLabel(freq: string): string {
    const labels: Record<string, string> = {
      once: $t('surveys.once'),
      weekly: $t('surveys.weekly'),
      monthly: $t('surveys.monthly'),
      quarterly: $t('surveys.quarterly'),
    };
    return labels[freq] || freq;
  }
</script>

<svelte:head>
  <title>{$t('surveys.title')} - Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto p-6">
  <div class="flex items-center justify-between mb-8">
    <div>
      <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
        &lt; {$t('nav.dashboard')}
      </a>
      <h1 class="text-3xl">{$t('surveys.title').toUpperCase()}</h1>
    </div>
    <button onclick={() => (showCreateModal = true)} class="brutal-btn brutal-btn-primary">
      {$t('surveys.create').toUpperCase()}
    </button>
  </div>

  {#if loading}
    <div class="text-center py-12">
      <span class="animate-pulse">{$t('common.loading').toUpperCase()}</span>
    </div>
  {:else if surveyList.length === 0}
    <div class="brutal-card p-12 text-center">
      <p class="text-muted-foreground mb-4">{$t('surveys.noSurveys')}</p>
      <button onclick={() => (showCreateModal = true)} class="brutal-btn brutal-btn-primary">
        {$t('surveys.create').toUpperCase()}
      </button>
    </div>
  {:else}
    <div class="grid gap-4">
      {#each surveyList as survey}
        <div class="brutal-card p-6">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <h2 class="text-xl font-bold">{survey.name}</h2>
                <span class="text-xs px-2 py-1 border-2 border-foreground {getStatusColor(survey.status)}">
                  {getStatusLabel(survey.status).toUpperCase()}
                </span>
              </div>
              {#if survey.description}
                <p class="text-muted-foreground text-sm mb-3">{survey.description}</p>
              {/if}
              <div class="flex gap-6 text-sm text-muted-foreground">
                <span>{$t('surveys.frequency')}: {getFrequencyLabel(survey.frequency)}</span>
                <span>{$t('surveys.questions')}: {survey.questions?.length || 0}</span>
                {#if survey.conversation_count !== undefined}
                  <span>{$t('dashboard.responses')}: {survey.conversation_count}</span>
                {/if}
                {#if survey.completion_rate !== undefined}
                  <span>{$t('dashboard.participation')}: {Math.round(survey.completion_rate * 100)}%</span>
                {/if}
              </div>
            </div>
            <div class="flex gap-2">
              {#if survey.status === 'draft' || survey.status === 'paused'}
                <button onclick={() => launchSurvey(survey.id)} class="brutal-btn brutal-btn-primary text-sm">
                  {$t('surveys.launch').toUpperCase()}
                </button>
              {:else if survey.status === 'active'}
                <button onclick={() => pauseSurvey(survey.id)} class="brutal-btn text-sm">
                  {$t('surveys.pause').toUpperCase()}
                </button>
              {/if}
              <button onclick={() => goto(`/dashboard/surveys/${survey.id}`)} class="brutal-btn text-sm">
                {$t('surveys.stats').toUpperCase()}
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Create Survey Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="brutal-card max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl">{$t('surveys.create').toUpperCase()}</h2>
        <button onclick={() => (showCreateModal = false)} class="text-2xl hover:text-terminal-green">
          X
        </button>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); createSurvey(); }}>
        <div class="space-y-4">
          <div>
            <label for="survey-name" class="block text-sm mb-1">{$t('surveys.name').toUpperCase()}</label>
            <input id="survey-name" type="text" bind:value={newSurvey.name} class="brutal-input w-full" required />
          </div>

          <div>
            <label for="survey-description" class="block text-sm mb-1">{$t('surveys.description').toUpperCase()}</label>
            <textarea id="survey-description" bind:value={newSurvey.description} class="brutal-input w-full" rows="2"></textarea>
          </div>

          <div>
            <label for="survey-frequency" class="block text-sm mb-1">{$t('surveys.frequency').toUpperCase()}</label>
            <select id="survey-frequency" bind:value={newSurvey.frequency} class="brutal-input w-full">
              <option value="once">{$t('surveys.once')}</option>
              <option value="weekly">{$t('surveys.weekly')}</option>
              <option value="monthly">{$t('surveys.monthly')}</option>
              <option value="quarterly">{$t('surveys.quarterly')}</option>
            </select>
          </div>

          <fieldset>
            <legend class="block text-sm mb-2">{$t('surveys.questions').toUpperCase()}</legend>
            <div class="space-y-3">
              {#each newSurvey.questions as question, i}
                <div class="flex gap-2">
                  <input
                    type="text"
                    bind:value={question.question}
                    placeholder="Question {i + 1}"
                    class="brutal-input flex-1"
                    required
                    aria-label="Question {i + 1}"
                  />
                  {#if newSurvey.questions.length > 1}
                    <button
                      type="button"
                      onclick={() => removeQuestion(question.id)}
                      class="brutal-btn brutal-btn-danger px-3"
                    >
                      X
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
            <button type="button" onclick={addQuestion} class="brutal-btn text-sm mt-3">
              + {$t('surveys.addQuestion').toUpperCase()}
            </button>
          </fieldset>
        </div>

        <div class="flex gap-3 mt-6 pt-6 border-t-2 border-foreground/20">
          <button type="button" onclick={() => (showCreateModal = false)} class="brutal-btn flex-1">
            {$t('common.cancel').toUpperCase()}
          </button>
          <button type="submit" class="brutal-btn brutal-btn-primary flex-1">
            {$t('common.create').toUpperCase()}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
</style>
