<!--
✨ ASK AI BUTTON: AI Affordances in Forms (Gap #11)
Add "Ask AI" buttons to form fields for intelligent suggestions
-->
<script lang="ts">
  import { Sparkles, Loader2 } from "lucide-svelte";
  import { api } from "$lib/api/client";
  import { toast } from "$lib/stores/toast";
  import { logger } from "$lib/utils/logger";

  interface Props {
    context?: string; // What field this button is for (e.g., "title", "description")
    currentValue?: string; // Current value in the field
    promptHint?: string; // Additional context for AI
    size?: "sm" | "md";
    variant?: "primary" | "ghost";
    disabled?: boolean;
    onsuggestion?: (suggestion: string) => void;
  }

  let {
    context = "",
    currentValue = "",
    promptHint = "",
    size = "md",
    variant = "ghost",
    disabled = false,
    onsuggestion,
  }: Props = $props();

  let isLoading = $state(false);

  async function askAI() {
    if (isLoading || disabled) return;

    isLoading = true;

    try {
      // Build prompt based on context
      let prompt = "";

      if (context === "title") {
        prompt = promptHint
          ? `Suggest a clear, actionable title for: ${promptHint}`
          : "Suggest a clear, actionable title for a task";
      } else if (context === "description") {
        prompt = currentValue
          ? `Improve and expand this description: ${currentValue}`
          : promptHint
            ? `Write a brief description for: ${promptHint}`
            : "Suggest a helpful task description";
      } else if (context === "priority") {
        prompt = promptHint
          ? `Based on this task: "${promptHint}", what priority (LOW, MEDIUM, HIGH) would you suggest? Return just the priority level.`
          : "Suggest a priority level for this task";
      } else if (context === "dueDate") {
        prompt = promptHint
          ? `Based on this task: "${promptHint}", suggest a reasonable due date. Return in format YYYY-MM-DD.`
          : "Suggest a due date for this task";
      } else {
        prompt = promptHint || `Provide a suggestion for ${context}`;
      }

      const response = (await api.ai.chat({
        message: prompt,
        conversation_history: [],
      })) as { response?: string };

      const suggestion = response.response || "";

      if (suggestion) {
        onsuggestion?.(suggestion);
        toast.success("AI suggestion ready", 2000);
      } else {
        toast.warning("No suggestion available", 3000);
      }
    } catch (error: any) {
      logger.error('[AskAI] Error', error);
      toast.error("Failed to get AI suggestion", 3000);
    } finally {
      isLoading = false;
    }
  }
</script>

<button
  type="button"
  onclick={askAI}
  disabled={isLoading || disabled}
  class="btn {size === 'sm' ? 'btn-sm' : ''} {variant === 'primary'
    ? 'btn-primary'
    : 'btn-ghost'} flex items-center gap-2"
  class:loading={isLoading}
  title="Ask AI for suggestion"
>
  {#if isLoading}
    <Loader2 class="w-4 h-4 animate-spin" />
  {:else}
    <Sparkles class="w-4 h-4" />
  {/if}
  <span class="hidden sm:inline">Ask AI</span>
</button>

<style>
  .loading {
    opacity: 0.7;
    cursor: not-allowed;
  }
</style>
