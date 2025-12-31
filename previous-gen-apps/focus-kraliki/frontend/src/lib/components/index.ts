/**
 * Exportable Components for Platform
 */

// Re-usable UI Components
export { default as LoadingSpinner } from './LoadingSpinner.svelte';
export { default as AskAIButton } from './AskAIButton.svelte';
export { default as ThemeToggle } from './ThemeToggle.svelte';
export { default as ToastNotification } from './ToastNotification.svelte';
export { default as ToastStack } from './ToastStack.svelte';
export { default as MarkdownRenderer } from './MarkdownRenderer.svelte';
export { default as CommandPalette } from './CommandPalette.svelte';
export { default as ContextPanel } from './ContextPanel.svelte';
export { default as ErrorBoundary } from './ErrorBoundary.svelte';
export { default as PomodoroTimer } from './PomodoroTimer.svelte';
export { default as ModelPicker } from './ModelPicker.svelte';
export { default as TypePicker } from './TypePicker.svelte';
export { default as PanelRedirect } from './PanelRedirect.svelte';

// Export types (to be defined)
export type Task = {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  created_at: string;
  updated_at: string;
};

export type Project = {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
};

export type Shadow = {
  id: string;
  pattern: string;
  insight: string;
  confidence: number;
  created_at: string;
};

export type FlowMemory = {
  id: string;
  context: Record<string, any>;
  session_id: string;
  created_at: string;
};
