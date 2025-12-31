/**
 * Focus by Kraliki Frontend Module Export
 */

export const MODULE_CONFIG = {
  name: 'focus-kraliki',
  displayName: 'Planning',
  icon: 'checklist',
  color: '#8b5cf6',
  routes: [
    { path: '/tasks', name: 'Tasks' },
    { path: '/projects', name: 'Projects' },
    { path: '/shadow', name: 'Shadow AI' },
    { path: '/flow-memory', name: 'Flow Memory' }
  ]
};

export const metadata = {
  version: '2.1.0',
  author: 'Ocelot Platform',
  description: 'Task management and planning with AI',
  capabilities: [
    'task_management',
    'project_tracking',
    'shadow_ai_analysis',
    'flow_memory',
    'ai_insights',
    'cross_session_context'
  ]
};
