<!--
CONTEXT PANEL: AI-First Architecture (Gap #10)

This component is the EXCLUSIVE container for all CRUD views.
Traditional routes redirect here - forms are "escape hatches", not primary interfaces.

AI creates -> Panels manage -> No standalone CRUD pages
-->
<script lang="ts">
  import { contextPanelStore } from "$lib/stores/contextPanel";
  import { onMount, tick } from "svelte";
  import { X } from "lucide-svelte";

  // PANEL-EXCLUSIVE CRUD VIEWS (Gap #10)
  // These views are ONLY accessible through this panel - no standalone routes
  import TasksView from "./dashboard/TasksView.svelte";
  import ProjectsView from "./dashboard/ProjectsView.svelte";
  import KnowledgeView from "./dashboard/KnowledgeView.svelte";
  import CalendarView from "./dashboard/CalendarView.svelte";
  import AnalyticsView from "./dashboard/AnalyticsView.svelte";
  import SettingsView from "./dashboard/SettingsView.svelte";
  import WorkflowTemplatesView from "./dashboard/WorkflowTemplatesView.svelte";
  import ShadowView from "./dashboard/ShadowView.svelte";
  import TimeTrackingView from "./dashboard/TimeTrackingView.svelte";
  import PomodoroView from "./dashboard/PomodoroView.svelte";
  import InfraView from "./dashboard/InfraView.svelte";
  import N8nHooksView from "./dashboard/N8nHooksView.svelte";
  import VoiceView from "./dashboard/VoiceView.svelte";
  import CapturesView from "./dashboard/CapturesView.svelte";

  let panelState = $derived($contextPanelStore);
  let isOpen = $derived(panelState.isOpen);
  let panelType = $derived(panelState.type);

  // Gap #14: Scroll memory
  let scrollContainer: HTMLDivElement | undefined = $state();
  let previousPanelType: string | null = $state(null);

  const panelTitles: Record<string, string> = {
    tasks: "Tasks",
    projects: "Projects",
    knowledge: "Knowledge Base",
    calendar: "Calendar",
    analytics: "Analytics",
    settings: "Settings",
    workflow: "Workflows",
    shadow: "Shadow Work",
    time: "Time Tracking",
    pomodoro: "Focus Protocol",
    infra: "Infrastructure",
    n8n: "Workflows",
    voice: "Voice by Kraliki Remote",
    captures: "Captures",
  };

  // Gap #14: Save scroll position before panel closes or changes
  function saveScrollPosition() {
    if (scrollContainer && panelType) {
      const scrollTop = scrollContainer.scrollTop;
      contextPanelStore.saveScrollPosition(panelType, scrollTop);
    }
  }

  // Gap #14: Restore scroll position after panel content loads
  async function restoreScrollPosition() {
    if (scrollContainer && panelType) {
      // Wait for DOM to update
      await tick();
      const savedPosition = panelState.scrollPositions?.[panelType] || 0;
      // Use requestAnimationFrame to ensure smooth restoration
      requestAnimationFrame(() => {
        if (scrollContainer) {
          scrollContainer.scrollTop = savedPosition;
        }
      });
    }
  }

  // Gap #14: Track scroll position changes (throttled)
  let scrollTimeout: number | null = $state(null);
  function handleScroll() {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    scrollTimeout = window.setTimeout(() => {
      saveScrollPosition();
      scrollTimeout = null;
    }, 100); // Throttle to save every 100ms
  }

  // Gap #14: Watch for panel type changes
  $effect(() => {
    if (panelType !== previousPanelType) {
      // Save scroll position of previous panel before switching
      if (previousPanelType && scrollContainer) {
        saveScrollPosition();
      }
      previousPanelType = panelType;

      // Restore scroll position of new panel after switching
      if (isOpen && panelType) {
        restoreScrollPosition();
      }
    }
  });

  // Gap #14: Restore scroll when panel opens
  $effect(() => {
    if (isOpen && panelType && scrollContainer) {
      restoreScrollPosition();
    }
  });

  function handleClose() {
    saveScrollPosition(); // Gap #14: Save before close
    contextPanelStore.close();
  }

  function handleEscape(event: KeyboardEvent) {
    if (event.key === "Escape" && isOpen) {
      handleClose();
    }
  }

  onMount(() => {
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  });
</script>

<!-- Backdrop -->
{#if isOpen}
  <div
    class="fixed inset-0 bg-black/40 z-40 transition-opacity duration-300"
    onclick={handleClose}
    onkeydown={(e) => e.key === "Enter" && handleClose()}
    role="button"
    tabindex="-1"
    aria-label="Close panel"
  ></div>
{/if}

<!-- Panel -->
<div
  class="fixed top-0 right-0 h-full w-full md:w-[600px] lg:w-[800px] bg-background z-50 border-l-2 border-black dark:border-white shadow-[-8px_0_0_0_rgba(0,0,0,1)] dark:shadow-[-8px_0_0_0_rgba(255,255,255,1)] transform transition-transform duration-300 flex flex-col"
  class:translate-x-full={!isOpen}
  class:translate-x-0={isOpen}
>
  <!-- Panel Header (Gap #10: Visual "escape hatch" indicator) -->
  <div
    class="flex-shrink-0 flex items-center justify-between p-4 border-b-2 border-black dark:border-white bg-card"
  >
    <div class="flex items-center gap-3">
      <h2 class="text-xl font-display uppercase tracking-tighter">
        {panelType ? panelTitles[panelType] : ""}
      </h2>
      <!-- "Escape Hatch" indicator (Gap #10: AI-first hierarchy) -->
      <span
        class="text-[9px] uppercase font-bold tracking-widest text-muted-foreground opacity-60 hidden md:inline"
      >
        Manual Mode
      </span>
    </div>
    <button
      type="button"
      class="btn btn-sm btn-ghost p-2"
      onclick={handleClose}
      title="Close panel (ESC)"
    >
      <X class="w-5 h-5" />
    </button>
  </div>

  <!-- Panel Content (Gap #14: Scroll memory via bind:this and onscroll) -->
  <div
    bind:this={scrollContainer}
    onscroll={handleScroll}
    class="flex-1 overflow-y-auto"
  >
    {#if panelType === "tasks"}
      <TasksView />
    {:else if panelType === "projects"}
      <ProjectsView />
    {:else if panelType === "knowledge"}
      <KnowledgeView />
    {:else if panelType === "calendar"}
      <CalendarView />
    {:else if panelType === "analytics"}
      <AnalyticsView />
    {:else if panelType === "settings"}
      <SettingsView />
    {:else if panelType === "workflow"}
      <WorkflowTemplatesView />
    {:else if panelType === "shadow"}
      <ShadowView />
    {:else if panelType === "time"}
      <TimeTrackingView />
    {:else if panelType === "pomodoro"}
      <PomodoroView />
    {:else if panelType === "infra"}
      <InfraView />
    {:else if panelType === "n8n"}
      <N8nHooksView />
    {:else if panelType === "voice"}
      <VoiceView />
    {:else if panelType === "captures"}
      <CapturesView />
    {/if}
  </div>
</div>
