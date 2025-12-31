<script lang="ts">
  import { page } from '$app/stores';
  import { employee } from '$api/client';
  import { onMount } from 'svelte';

  // Token is always defined in this route
  const token = $derived($page.params.token as string);

  interface TranscriptTurn {
    role: 'ai' | 'user';
    content: string;
    timestamp?: string;
    redacted?: boolean;
  }

  let transcript = $state<TranscriptTurn[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let selectedForRedaction = $state<Set<number>>(new Set());
  let saving = $state(false);

  onMount(async () => {
    if (!token) return;
    try {
      const data = await employee.transcript(token);
      transcript = (data.transcript || []) as TranscriptTurn[];
    } catch (e) {
      error = 'Prepis neni k dispozici';
    } finally {
      loading = false;
    }
  });

  function toggleRedaction(index: number) {
    const newSet = new Set(selectedForRedaction);
    if (newSet.has(index)) {
      newSet.delete(index);
    } else {
      newSet.add(index);
    }
    selectedForRedaction = newSet;
  }

  async function handleSaveRedactions() {
    if (selectedForRedaction.size === 0 || !token) return;

    saving = true;
    try {
      await employee.redact(token, Array.from(selectedForRedaction));
      // Update local transcript
      transcript = transcript.map((turn, idx) => {
        if (selectedForRedaction.has(idx)) {
          return { ...turn, redacted: true, content: '[ODEBRANO ZAMESTNANCEM]' };
        }
        return turn;
      });
      selectedForRedaction = new Set();
    } catch (e) {
      error = 'Nepodarilo se ulozit zmeny';
    } finally {
      saving = false;
    }
  }

  async function handleDeleteAll() {
    if (!token) return;
    if (!confirm('Opravdu chces smazat vsechna svá data? Tato akce je nevratna.')) {
      return;
    }

    try {
      await employee.deleteData(token);
      transcript = [];
      error = 'Tvoje data byla smazana';
    } catch (e) {
      error = 'Nepodarilo se smazat data';
    }
  }
</script>

<svelte:head>
  <title>Prepis rozhovoru - Speak by Kraliki</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center p-4 bg-void">
  <div class="brutal-card max-w-2xl w-full p-6">
    <h1 class="text-xl mb-6">PREPIS TVEHO ROZHOVORU</h1>

    {#if loading}
      <div class="text-center py-8">
        <span class="animate-pulse">Nacitam...</span>
      </div>

    {:else if error}
      <div class="text-center py-8">
        <p class="text-muted-foreground">{error}</p>
      </div>

    {:else}
      <p class="text-sm text-muted-foreground mb-6">
        Muzes oznacit casti, ktere chces odstranit z analyzy. Tvuj nadrizeny tyto casti nikdy neuvidi.
      </p>

      <div class="max-h-[400px] overflow-y-auto mb-6 border-2 border-foreground p-4">
        {#each transcript as turn, index}
          <div class="mb-4 p-3 border-2 {turn.redacted ? 'border-foreground/30 bg-foreground/5' : selectedForRedaction.has(index) ? 'border-system-red' : 'border-foreground/50'}">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs text-muted-foreground">
                {turn.role === 'ai' ? 'AI' : 'TY'}
              </span>

              {#if turn.role === 'user' && !turn.redacted}
                <button
                  onclick={() => toggleRedaction(index)}
                  class="text-xs {selectedForRedaction.has(index) ? 'text-system-red' : 'text-muted-foreground hover:text-foreground'}"
                >
                  {selectedForRedaction.has(index) ? '[ZRUSIT]' : '[ODSTRANIT TUTO CAST]'}
                </button>
              {/if}
            </div>

            <p class="{turn.redacted ? 'text-muted-foreground italic' : ''}">
              {turn.content}
            </p>
          </div>
        {/each}
      </div>

      <div class="flex flex-col sm:flex-row gap-4">
        {#if selectedForRedaction.size > 0}
          <button
            onclick={handleSaveRedactions}
            class="brutal-btn brutal-btn-primary flex-1"
            disabled={saving}
          >
            {saving ? 'UKLADAM...' : `POTVRDIT A ODESLAT (${selectedForRedaction.size} ODEBRANO)`}
          </button>
        {:else}
          <a href={`/v/${token}`} class="brutal-btn brutal-btn-primary flex-1 text-center">
            POTVRDIT A ODESLAT
          </a>
        {/if}

        <button
          onclick={handleDeleteAll}
          class="brutal-btn brutal-btn-danger"
        >
          SMAZAT VSE
        </button>
      </div>

      <p class="text-xs text-muted-foreground mt-4 text-center">
        Po potvrzeni budou tvoje odpovedi anonymne analyzovany.
      </p>
    {/if}
  </div>
</div>

<style>
</style>
