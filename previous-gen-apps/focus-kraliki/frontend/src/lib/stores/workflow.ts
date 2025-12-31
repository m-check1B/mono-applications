/**
 * Workflow Store
 * Svelte writable store for workflow template management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';

export interface WorkflowStep {
    step: number;
    action: string;
    estimatedMinutes: number;
    dependencies: number[];
    type: 'manual' | 'automated';
}

export interface WorkflowTemplate {
    id: string;
    userId?: string;
    name: string;
    description: string;
    category: string;
    icon?: string;
    steps: WorkflowStep[];
    totalEstimatedMinutes: number;
    tags: string[];
    isPublic: boolean;
    isSystem: boolean;
    usageCount: number;
    createdAt: string;
}

export interface WorkflowState {
    templates: WorkflowTemplate[];
    categories: string[];
    isLoading: boolean;
    error: string | null;
}

const initialState: WorkflowState = {
    templates: [],
    categories: [],
    isLoading: false,
    error: null
};

function createWorkflowStore() {
    const { subscribe, set, update } = writable<WorkflowState>(initialState);

    return {
        subscribe,

        async loadTemplates(params?: { category?: string }) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                const response: any = await api.workflow.listTemplates(params);
                const templates = response.templates || [];

                update((state) => ({
                    ...state,
                    templates,
                    isLoading: false
                }));

                return { success: true, templates };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load templates';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async loadCategories() {
            try {
                const response: any = await api.workflow.getCategories();
                const categories = response.categories || [];

                update((state) => ({
                    ...state,
                    categories
                }));

                return { success: true, categories };
            } catch (error: any) {
                logger.error('Failed to load categories', error);
                return { success: false, error: error.detail };
            }
        },

        async createTemplate(templateData: any) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                const newTemplate: any = await api.workflow.createTemplate(templateData);

                update((state) => ({
                    ...state,
                    templates: [newTemplate, ...state.templates],
                    isLoading: false
                }));

                return { success: true, template: newTemplate };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to create template';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async generateTemplate(description: string, category?: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                const newTemplate: any = await api.workflow.generate({ description, category });

                update((state) => ({
                    ...state,
                    templates: [newTemplate, ...state.templates],
                    isLoading: false
                }));

                return { success: true, template: newTemplate };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to generate template';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async executeWorkflow(templateId: string, options: { startDate?: string; priority?: number; customTitle?: string }) {
            try {
                const response = await api.workflow.execute({
                    templateId,
                    startDate: options.startDate,
                    priority: options.priority,
                    customTitle: options.customTitle
                }) as any;
                return { success: true, ...response };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to execute workflow' };
            }
        },

        async deleteTemplate(templateId: string) {
            try {
                await api.workflow.deleteTemplate(templateId);
                update((state) => ({
                    ...state,
                    templates: state.templates.filter(t => t.id !== templateId)
                }));
                return { success: true };
            } catch (error: any) {
                return { success: false, error: error.detail || 'Failed to delete template' };
            }
        }
    };
}

export const workflowStore = createWorkflowStore();
