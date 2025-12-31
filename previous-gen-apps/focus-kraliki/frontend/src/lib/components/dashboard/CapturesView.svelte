<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api/client";
  import { toast } from "$lib/stores/toast";
  import {
    Paperclip,
    Link,
    FileText,
    Image,
    Trash2,
    Sparkles,
    Clock,
    Tag,
    Lightbulb,
    CheckSquare,
  } from "lucide-svelte";
  import { logger } from "$lib/utils/logger";

  interface CaptureProcessed {
    summary: string;
    key_points: string[];
    entities: string[];
    suggested_tags: string[];
    action_items: string[];
  }

  interface Capture {
    id: string;
    source_type: string;
    title: string;
    content: string;
    original_content: string;
    processed: CaptureProcessed;
    createdAt: string;
  }

  let captures: Capture[] = $state([]);
  let loading = $state(true);
  let error: string | null = $state(null);

  // Source type icons
  const sourceIcons: Record<string, typeof Image> = {
    image: Image,
    url: Link,
    text: FileText,
    file: Paperclip,
  };

  async function loadCaptures() {
    loading = true;
    error = null;
    try {
      const response = await api.get<{ captures: Capture[]; total: number }>(
        "/captures?limit=50"
      );
      captures = response.captures || [];
    } catch (e: any) {
      error = e?.detail || "Failed to load captures";
      logger.error("[Captures] Load error", e);
    } finally {
      loading = false;
    }
  }

  async function deleteCapture(id: string) {
    try {
      await api.delete(`/captures/${id}`);
      captures = captures.filter((c) => c.id !== id);
      toast.success("Capture deleted");
    } catch (e: any) {
      toast.error(e?.detail || "Failed to delete");
    }
  }

  function formatTime(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }

  onMount(() => {
    loadCaptures();
  });
</script>

<div class="p-4 space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-2">
      <Paperclip class="w-5 h-5" />
      <span class="text-sm font-bold uppercase tracking-widest"
        >Recent Captures</span
      >
    </div>
    <button
      class="text-xs uppercase font-bold text-muted-foreground hover:text-foreground"
      onclick={loadCaptures}
    >
      Refresh
    </button>
  </div>

  <!-- Loading -->
  {#if loading}
    <div class="text-center py-8">
      <div class="animate-pulse text-muted-foreground">Loading captures...</div>
    </div>
  {:else if error}
    <div class="brutal-card bg-destructive/10 border-destructive p-4">
      <p class="text-sm text-destructive">{error}</p>
    </div>
  {:else if captures.length === 0}
    <div class="text-center py-12 space-y-4">
      <div
        class="w-16 h-16 mx-auto brutal-card bg-muted flex items-center justify-center"
      >
        <Paperclip class="w-8 h-8 text-muted-foreground" />
      </div>
      <p class="text-sm text-muted-foreground">No captures yet</p>
      <p class="text-xs text-muted-foreground max-w-xs mx-auto">
        Drop images, paste URLs, or type ideas. AI will process and organize
        everything.
      </p>
    </div>
  {:else}
    <!-- Captures List -->
    <div class="space-y-3">
      {#each captures as capture (capture.id)}
        {@const IconComponent = sourceIcons[capture.source_type] || FileText}
        <div class="brutal-card bg-card p-4 space-y-3">
          <!-- Header -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2">
              <div
                class="w-8 h-8 brutal-card bg-accent flex items-center justify-center flex-shrink-0"
              >
                <IconComponent class="w-4 h-4" />
              </div>
              <div class="min-w-0">
                <h3 class="font-bold text-sm truncate">{capture.title}</h3>
                <div
                  class="flex items-center gap-2 text-[10px] text-muted-foreground"
                >
                  <Clock class="w-3 h-3" />
                  <span>{formatTime(capture.createdAt)}</span>
                  <span class="uppercase">{capture.source_type}</span>
                </div>
              </div>
            </div>
            <button
              class="p-1 hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
              onclick={() => deleteCapture(capture.id)}
              title="Delete capture"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <!-- AI Summary -->
          {#if capture.processed?.summary}
            <div class="flex items-start gap-2">
              <Sparkles class="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
              <p class="text-sm text-muted-foreground">
                {capture.processed.summary}
              </p>
            </div>
          {/if}

          <!-- Key Points -->
          {#if capture.processed?.key_points?.length > 0}
            <div class="space-y-1">
              <p
                class="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center gap-1"
              >
                <Lightbulb class="w-3 h-3" /> Key Points
              </p>
              <ul class="text-xs space-y-1 pl-4">
                {#each capture.processed.key_points.slice(0, 3) as point}
                  <li class="text-muted-foreground">{point}</li>
                {/each}
              </ul>
            </div>
          {/if}

          <!-- Action Items -->
          {#if capture.processed?.action_items?.length > 0}
            <div class="space-y-1">
              <p
                class="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center gap-1"
              >
                <CheckSquare class="w-3 h-3" /> Action Items
              </p>
              <ul class="text-xs space-y-1">
                {#each capture.processed.action_items.slice(0, 3) as item}
                  <li
                    class="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer"
                  >
                    <span
                      class="w-3 h-3 border border-current flex-shrink-0"
                    ></span>
                    {item}
                  </li>
                {/each}
              </ul>
            </div>
          {/if}

          <!-- Tags -->
          {#if capture.processed?.suggested_tags?.length > 0}
            <div class="flex items-center gap-1 flex-wrap">
              <Tag class="w-3 h-3 text-muted-foreground" />
              {#each capture.processed.suggested_tags.slice(0, 5) as tag}
                <span
                  class="text-[10px] px-2 py-0.5 bg-accent/20 text-accent-foreground uppercase font-bold"
                >
                  {tag}
                </span>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
