<script lang="ts">
  import { page } from '$app/stores';
  import { voiceStore, conversationTranscript, isVoiceActive } from '$stores/voice';
  import { employee, actions } from '$api/client';
  import { onMount, onDestroy } from 'svelte';

  // Token is always defined in this route
  const token = $derived($page.params.token as string);

  let consentGiven = $state(false);
  let publicActions = $state<Array<{ id: string; topic: string; status: string; public_message?: string }>>([]);
  let error = $state<string | null>(null);
  let textInput = $state('');

  // Load public actions for Action Loop widget
  onMount(async () => {
    if (!token) return;
    try {
      publicActions = await actions.public(token);
    } catch (e) {
      // Actions may not be available
    }
  });

  onDestroy(() => {
    voiceStore.reset();
  });

  async function handleConsent() {
    if (!token) return;
    try {
      await employee.consent(token);
      consentGiven = true;
      voiceStore.connect(token);
    } catch (e) {
      error = 'Neplatny nebo vyprsely odkaz';
    }
  }

  function handleSendMessage() {
    if (textInput.trim()) {
      voiceStore.sendMessage(textInput.trim());
      textInput = '';
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  function handleSwitchToText() {
    voiceStore.switchToText('user_requested');
  }

  function handleEndConversation() {
    voiceStore.endConversation();
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      new: 'Novy',
      heard: 'Slysime vas',
      in_progress: 'Resime',
      resolved: 'Vyreseno',
    };
    return labels[status] || status;
  }

  function getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      new: 'text-cyan-data',
      heard: 'text-terminal-green',
      in_progress: 'text-yellow-400',
      resolved: 'text-gray-500',
    };
    return colors[status] || '';
  }
</script>

<svelte:head>
  <title>Speak by Kraliki - Check-in</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center p-4 bg-void relative overflow-hidden">
  {#if error}
    <!-- Error State -->
    <div class="brutal-card max-w-lg w-full p-8 text-center relative z-20">
      <div class="text-system-red text-4xl mb-4 font-display">!</div>
      <h1 class="text-xl mb-4 font-display">CHYBA</h1>
      <p class="text-muted-foreground font-mono">{error}</p>
    </div>

  {:else if !consentGiven}
    <!-- Trust Layer - Consent Screen -->
    <div class="brutal-card max-w-lg w-full p-8 relative z-20">
      <div class="text-center mb-6">
        <div class="text-terminal-green text-3xl mb-2 font-display">///</div>
        <h1 class="text-2xl font-display">SPEAK BY KRALIKI</h1>
      </div>

      <p class="mb-6 text-center font-mono">
        Ahoj! Toto je tvůj měsíční prostor pro zpětnou vazbu.
      </p>

      <div class="border-2 border-terminal-green p-4 mb-6 bg-void brutal-shadow-sm">
        <div class="flex items-center gap-2 mb-2 font-mono text-sm">
          <span class="text-terminal-green">[OK]</span>
          <span>Rozhovor je 100% ANONYMNÍ</span>
        </div>
        <div class="flex items-center gap-2 mb-2 font-mono text-sm">
          <span class="text-terminal-green">[OK]</span>
          <span>Tvůj nadřízený NEUVIDÍ co jsi řekl/a</span>
        </div>
        <div class="flex items-center gap-2 mb-2 font-mono text-sm">
          <span class="text-terminal-green">[OK]</span>
          <span>Vedení vidí pouze agregované trendy</span>
        </div>
        <div class="flex items-center gap-2 mb-2 font-mono text-sm">
          <span class="text-terminal-green">[OK]</span>
          <span>Po rozhovoru si můžeš přečíst a upravit přepis</span>
        </div>
        <div class="flex items-center gap-2 font-mono text-sm">
          <span class="text-terminal-green">[OK]</span>
          <span>Můžeš kdykoliv požádat o smazání svých dat</span>
        </div>
      </div>

      <p class="text-sm text-muted-foreground mb-6 text-center font-mono">
        Rozhovor trvá cca 5 minut.
      </p>

      <button onclick={handleConsent} class="brutal-btn brutal-btn-primary w-full mb-4">
        ROZUMÍM, POJĎME NA TO
      </button>

      <div class="text-center">
        <button type="button" class="text-sm text-muted-foreground hover:text-foreground bg-transparent border-none cursor-pointer font-mono uppercase">
          Nechci odpovídat: Přeskočit tento měsíc
        </button>
      </div>

      <!-- Action Loop Widget -->
      {#if publicActions.length > 0}
        <div class="mt-8 pt-6 border-t-2 border-foreground">
          <h3 class="text-sm font-bold mb-4 uppercase font-display">Co děláme s vaší zpětnou vazbou</h3>
          <div class="space-y-3">
            {#each publicActions.slice(0, 3) as action}
              <div class="p-3 border-2 border-foreground bg-card brutal-shadow-sm text-sm">
                <div class="flex items-center gap-2 mb-1">
                  <span class="{getStatusColor(action.status)} font-bold font-mono">
                    [{getStatusLabel(action.status)}]
                  </span>
                </div>
                <span class="font-mono">{action.public_message || action.topic}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

  {:else if $voiceStore.status === 'completed'}
    <!-- Completed Screen -->
    <div class="brutal-card max-w-lg w-full p-8 text-center relative z-20">
      <div class="text-terminal-green text-4xl mb-4 font-display">OK</div>
      <h1 class="text-xl mb-4 font-display">DĚKUJEME!</h1>
      <p class="text-muted-foreground mb-6 font-mono">
        Tvoje zpětná vazba byla zaznamenána. Vážíme si tvého času.
      </p>

      <a href={`/v/${token}/transcript`} class="brutal-btn">
        ZOBRAZIT PŘEPIS
      </a>
    </div>

  {:else}
    <!-- Active Conversation -->
    <div class="brutal-card max-w-2xl w-full p-6 relative z-20">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="relative">
            <div class="voice-indicator"></div>
            {#if $voiceStore.isRecording}
              <div class="voice-ring"></div>
            {/if}
          </div>
          <span class="text-xs text-muted-foreground font-mono uppercase tracking-widest">
            {$voiceStore.mode === 'voice' ? 'Hlasový režim' : 'Textový režim'}
          </span>
        </div>

        <div class="flex gap-2">
          {#if $voiceStore.mode === 'voice'}
            <button onclick={handleSwitchToText} class="brutal-btn text-[10px] py-1 px-2">
              PŘEJÍT NA TEXT
            </button>
          {/if}
          <button onclick={handleEndConversation} class="brutal-btn brutal-btn-danger text-[10px] py-1 px-2">
            UKONČIT
          </button>
        </div>
      </div>

      <!-- Transcript -->
      <div class="h-[400px] overflow-y-auto mb-6 p-4 bg-void border-2 border-foreground brutal-shadow-sm">
        {#each $conversationTranscript as turn}
          <div class="mb-6 {turn.role === 'ai' ? '' : 'text-right'}">
            <div class="text-[10px] text-muted-foreground mb-1 font-mono uppercase tracking-tighter">
              {turn.role === 'ai' ? 'SPEAK BY KRALIKI' : 'TY'}
            </div>
            <div class="inline-block max-w-[85%] p-3 font-mono text-sm {turn.role === 'ai' ? 'bg-card border-2 border-foreground brutal-shadow-sm' : 'bg-terminal-green text-black border-2 border-black'}">
              {turn.content}
            </div>
          </div>
        {/each}

        {#if $voiceStore.isProcessing}
          <div class="mb-4">
            <div class="text-[10px] text-muted-foreground mb-1 font-mono uppercase">SPEAK BY KRALIKI</div>
            <div class="inline-block p-3 bg-card border-2 border-foreground font-mono text-sm italic">
              <span class="animate-pulse">Přemýšlím...</span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Input Area -->
      {#if $voiceStore.mode === 'text'}
        <div class="flex gap-2">
          <input
            type="text"
            bind:value={textInput}
            onkeypress={handleKeyPress}
            placeholder="Napiš svou odpověď..."
            class="brutal-input flex-1 text-sm"
            disabled={$voiceStore.isProcessing}
          />
          <button
            onclick={handleSendMessage}
            class="brutal-btn brutal-btn-primary"
            disabled={$voiceStore.isProcessing || !textInput.trim()}
          >
            ODESLAT
          </button>
        </div>
      {:else}
        <div class="text-center text-sm text-muted-foreground font-mono border-2 border-dashed border-foreground/30 py-6">
          <p class="animate-pulse">MLUV DO MIKROFONU...</p>
          <p class="text-[10px] mt-2 opacity-50 uppercase">Nebo přepni na textový režim výše</p>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
</style>
