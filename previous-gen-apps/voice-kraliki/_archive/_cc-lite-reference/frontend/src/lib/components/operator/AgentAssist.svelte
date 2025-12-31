<script lang="ts">
  import { fly, scale, fade } from 'svelte/transition';
  import { quintOut, elasticOut } from 'svelte/easing';
  import Card from '../shared/Card.svelte';
  import Badge from '../shared/Badge.svelte';
  import Button from '../shared/Button.svelte';

  type Suggestion = {
    id: string;
    type: 'response' | 'action' | 'knowledge';
    title: string;
    content: string;
    confidence: number;
  };

  type KnowledgeArticle = {
    id: string;
    title: string;
    summary: string;
    relevance: number;
  };

  let {
    suggestions = [],
    articles = []
  }: {
    suggestions?: Suggestion[];
    articles?: KnowledgeArticle[];
  } = $props();

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'gray';
  };

  const handleUseSuggestion = (suggestion: Suggestion) => {
    console.log('Using suggestion', suggestion.id);
    // TODO: Insert suggestion into response field
  };

  const handleViewArticle = (article: KnowledgeArticle) => {
    console.log('View article', article.id);
    // TODO: Open article in modal/sidebar
  };
</script>

<Card>
  {#snippet header()}
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-primary-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h2>
      </div>
      <div class="flex items-center gap-2">
        {#if suggestions.length > 0}
          <Badge variant="success" class="animate-pulse">🤖 AI ACTIVE</Badge>
        {:else}
          <Badge variant="gray">AI READY</Badge>
        {/if}
      </div>
    </div>
  {/snippet}

  <div class="space-y-4">
    <!-- AI Suggestions -->
    {#if suggestions.length > 0}
      <div in:fade={{ duration: 300 }}>
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Suggested Responses</h3>
        <div class="space-y-2">
          {#each suggestions as suggestion, i (suggestion.id)}
            <div
              class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600 hover:border-primary-500 transition-all duration-300"
              in:fly={{ x: 20, duration: 400, delay: i * 100, easing: quintOut }}>
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">{suggestion.title}</span>
                  <Badge variant={getConfidenceColor(suggestion.confidence)} class="text-xs">
                    {Math.round(suggestion.confidence * 100)}%
                  </Badge>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onclick={() => handleUseSuggestion(suggestion)}
                >
                  Use
                </Button>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">{suggestion.content}</p>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Knowledge Base Articles -->
    {#if articles.length > 0}
      <div in:fade={{ duration: 300, delay: 200 }}>
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Related Articles</h3>
        <div class="space-y-2">
          {#each articles as article, i (article.id)}
            <button
              class="w-full text-left bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 hover:border-primary-500 transition-all duration-300"
              in:fly={{ x: 20, duration: 400, delay: 200 + i * 100, easing: quintOut }}
              onclick={() => handleViewArticle(article)}
            >
              <div class="flex items-start justify-between mb-1">
                <span class="text-sm font-medium text-gray-900 dark:text-white">{article.title}</span>
                <Badge variant="primary" class="text-xs ml-2">
                  {Math.round(article.relevance * 100)}%
                </Badge>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-400">{article.summary}</p>
            </button>
          {/each}
        </div>
      </div>
    {/if}

    {#if suggestions.length === 0 && articles.length === 0}
      <div class="text-center py-8" in:fade={{ duration: 300 }}>
        <div in:scale={{ duration: 600, easing: elasticOut }}>
          <svg class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400" in:fly={{ y: 10, duration: 400, delay: 200 }}>AI suggestions will appear here</p>
        <p class="text-xs text-gray-500 dark:text-gray-500 mt-1" in:fly={{ y: 10, duration: 400, delay: 300 }}>Based on the conversation context</p>
      </div>
    {/if}
  </div>
</Card>
