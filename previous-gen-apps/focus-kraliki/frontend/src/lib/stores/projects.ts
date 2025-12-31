/**
 * Projects Store
 * Svelte writable store for project management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import { logger } from '$lib/utils/logger';
import {
	OFFLINE_STORES,
	clearOfflineStore,
	isOnline,
	offlineProjects,
	queueOperation
} from '$lib/utils/offlineStorage';

export interface Project {
    id: string;
    name: string;
    description?: string;
    color?: string;
    icon?: string;
    userId: string;
    workspaceId?: string;
    taskCount?: number;
    status?: string;
    createdAt?: string;
    updatedAt?: string;
}

export interface ProjectTemplate {
    id: string;
    name: string;
    description: string;
    category: string;
    estimatedDuration: string;
    taskCount: number;
}

export interface ProjectsState {
    projects: Project[];
    templates: ProjectTemplate[];
    isLoading: boolean;
    error: string | null;
    currentProject: Project | null;
    currentProjectProgress: any | null;
}

const initialState: ProjectsState = {
    projects: [],
    templates: [],
    isLoading: false,
    error: null,
    currentProject: null,
    currentProjectProgress: null
};

function createProjectsStore() {
    const { subscribe, set, update } = writable<ProjectsState>(initialState);

    return {
        subscribe,

        async loadProjects() {
            update((state) => ({ ...state, isLoading: true, error: null }));

            try {
                if (!isOnline()) {
                    const projects = await offlineProjects.getAll();

                    update((state) => ({
                        ...state,
                        projects,
                        isLoading: false
                    }));

                    return { success: true, projects };
                }

                const response: any = await api.projects.list();
                const projects = response.projects || [];

                await clearOfflineStore(OFFLINE_STORES.PROJECTS);
                for (const project of projects) {
                    await offlineProjects.save(project);
                }

                update((state) => ({
                    ...state,
                    projects,
                    isLoading: false
                }));

                return { success: true, projects };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to load projects';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async createProject(projectData: { name: string; description?: string; color?: string; icon?: string }) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                if (!isOnline()) {
                    const now = new Date().toISOString();
                    const offlineProject: Project = {
                        id: crypto.randomUUID?.() || `offline-${Date.now()}`,
                        name: projectData.name,
                        description: projectData.description,
                        color: projectData.color,
                        icon: projectData.icon,
                        userId: 'offline',
                        createdAt: now,
                        updatedAt: now
                    };

                    await offlineProjects.save(offlineProject);
                    await queueOperation({
                        type: 'create',
                        entity: 'project',
                        data: projectData,
                        endpoint: '/projects'
                    });

                    update((state) => ({
                        ...state,
                        projects: [offlineProject, ...state.projects],
                        isLoading: false
                    }));

                    return { success: true, project: offlineProject };
                }

                const newProject: any = await api.projects.create(projectData);
                await offlineProjects.save(newProject);

                update((state) => ({
                    ...state,
                    projects: [newProject, ...state.projects],
                    isLoading: false
                }));

                return { success: true, project: newProject };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to create project';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async loadTemplates() {
            try {
                if (!isOnline()) {
                    return { success: false, error: 'Offline mode: templates unavailable.' };
                }

                const response: any = await api.projects.listTemplates();
                const templates = response.templates || [];

                update((state) => ({
                    ...state,
                    templates
                }));

                return { success: true, templates };
            } catch (error: any) {
                logger.error('Failed to load templates', error);
                return { success: false, error: error.detail };
            }
        },

        async createFromTemplate(templateId: string, customName?: string) {
            update((state) => ({ ...state, isLoading: true, error: null }));
            try {
                if (!isOnline()) {
                    return { success: false, error: 'Offline mode: cannot create from template.' };
                }

                const newProject: any = await api.projects.createFromTemplate(templateId, customName);
                await offlineProjects.save(newProject);

                update((state) => ({
                    ...state,
                    projects: [newProject, ...state.projects],
                    isLoading: false
                }));

                return { success: true, project: newProject };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to create project from template';
                update((state) => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async getProjectProgress(projectId: string) {
            try {
                if (!isOnline()) {
                    return { success: false, error: 'Offline mode: project progress unavailable.' };
                }

                const progress: any = await api.projects.getProgress(projectId);

                update((state) => ({
                    ...state,
                    currentProjectProgress: progress
                }));

                return { success: true, progress };
            } catch (error: any) {
                logger.error('Failed to load project progress', error);
                return { success: false, error: error.detail };
            }
        },

        async deleteProject(projectId: string) {
            try {
                if (!isOnline()) {
                    await offlineProjects.delete(projectId);
                    await queueOperation({
                        type: 'delete',
                        entity: 'project',
                        data: {},
                        endpoint: `/projects/${projectId}`
                    });

                    update((state) => ({
                        ...state,
                        projects: state.projects.filter((p) => p.id !== projectId)
                    }));

                    return { success: true };
                }

                await api.projects.delete(projectId);

                update((state) => ({
                    ...state,
                    projects: state.projects.filter((p) => p.id !== projectId)
                }));

                return { success: true };
            } catch (error: any) {
                const errorMessage = error.detail || 'Failed to delete project';
                return { success: false, error: errorMessage };
            }
        }
    };
}

export const projectsStore = createProjectsStore();
