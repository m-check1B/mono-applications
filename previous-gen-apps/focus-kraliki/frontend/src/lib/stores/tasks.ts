/**
 * Task Store
 * Svelte writable store for task management
 */

import { writable } from 'svelte/store';
import { api } from '$lib/api/client';
import {
	OFFLINE_STORES,
	clearOfflineStore,
	isOnline,
	offlineTasks,
	queueOperation
} from '$lib/utils/offlineStorage';

export interface Task {
	id: string;
	title: string;
	description?: string;
	status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
	priority: 'LOW' | 'MEDIUM' | 'HIGH';
	type?: string;
	due_date?: string;
	completed_at?: string;
	created_at: string;
	updated_at: string;
	workspaceId?: string;
	assignedUserId?: string;
}

export interface TasksState {
	tasks: Task[];
	isLoading: boolean;
	error: string | null;
	filters: {
		status?: string;
		type?: string;
		priority?: string;
		search?: string;
	};
}

const initialState: TasksState = {
	tasks: [],
	isLoading: false,
	error: null,
	filters: {}
};

function createTasksStore() {
	const { subscribe, set, update } = writable<TasksState>(initialState);

	return {
		subscribe,

		async loadTasks(filters?: any) {
			update((state) => ({ ...state, isLoading: true, error: null, filters: filters || {} }));

			try {
				if (!isOnline()) {
					const offlineItems = await offlineTasks.getAll();
					const tasks = offlineItems.filter((task: Task) => {
						if (filters?.status && task.status !== filters.status) return false;
						if (filters?.type && task.type !== filters.type) return false;
						if (filters?.priority && task.priority !== filters.priority) return false;
						if (filters?.search) {
							const q = filters.search.toLowerCase();
							return (
								task.title.toLowerCase().includes(q) ||
								(task.description || '').toLowerCase().includes(q)
							);
						}
						return true;
					});

					update((state) => ({
						...state,
						tasks,
						isLoading: false
					}));

					return { success: true, tasks };
				}

				const response: any = await api.tasks.list(filters);
				const tasks = response.tasks || [];

				await clearOfflineStore(OFFLINE_STORES.TASKS);
				for (const task of tasks) {
					await offlineTasks.save(task);
				}

				update((state) => ({
					...state,
					tasks,
					isLoading: false
				}));

				return { success: true, tasks };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to load tasks';
				update((state) => ({
					...state,
					isLoading: false,
					error: errorMessage
				}));
				return { success: false, error: errorMessage };
			}
		},

		async createTask(taskData: Partial<Task>) {
			try {
				if (!isOnline()) {
					const now = new Date().toISOString();
					const offlineTask: Task = {
						id: crypto.randomUUID?.() || `offline-${Date.now()}`,
						title: taskData.title || 'Untitled task',
						description: taskData.description,
						status: taskData.status || 'PENDING',
						priority: taskData.priority || 'MEDIUM',
						type: taskData.type,
						due_date: taskData.due_date,
						completed_at: taskData.completed_at,
						created_at: now,
						updated_at: now,
						workspaceId: taskData.workspaceId,
						assignedUserId: taskData.assignedUserId
					};

					await offlineTasks.save(offlineTask);
					await queueOperation({
						type: 'create',
						entity: 'task',
						data: taskData,
						endpoint: '/tasks'
					});

					update((state) => ({
						...state,
						tasks: [offlineTask, ...state.tasks]
					}));

					return { success: true, task: offlineTask };
				}

				const newTask: any = await api.tasks.create(taskData);
				await offlineTasks.save(newTask);

				update((state) => ({
					...state,
					tasks: [newTask, ...state.tasks]
				}));

				return { success: true, task: newTask };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to create task';
				return { success: false, error: errorMessage };
			}
		},

		async updateTask(taskId: string, updates: Partial<Task>) {
			try {
				if (!isOnline()) {
					const now = new Date().toISOString();
					let updatedTask: Task | null = null;

					update((state) => {
						const tasks = state.tasks.map((task) => {
							if (task.id !== taskId) return task;
							updatedTask = {
								...task,
								...updates,
								updated_at: now
							};
							return updatedTask;
						});

						return {
							...state,
							tasks
						};
					});

					if (updatedTask) {
						await offlineTasks.save(updatedTask);
					}

					await queueOperation({
						type: 'update',
						entity: 'task',
						data: updates,
						endpoint: `/tasks/${taskId}`
					});

					return { success: true, task: updatedTask };
				}

				const updatedTask: any = await api.tasks.update(taskId, updates);
				await offlineTasks.save(updatedTask);

				update((state) => ({
					...state,
					tasks: state.tasks.map((t) => (t.id === taskId ? updatedTask : t))
				}));

				return { success: true, task: updatedTask };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to update task';
				return { success: false, error: errorMessage };
			}
		},

		async toggleTask(taskId: string) {
			try {
				if (!isOnline()) {
					let updatedTask: Task | null = null;

					update((state) => {
						const tasks = state.tasks.map((task) => {
							if (task.id !== taskId) return task;
							const nextStatus = task.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
							updatedTask = {
								...task,
								status: nextStatus,
								completed_at: nextStatus === 'COMPLETED' ? new Date().toISOString() : undefined
							};
							return updatedTask;
						});

						return {
							...state,
							tasks
						};
					});

					if (updatedTask) {
						await offlineTasks.save(updatedTask);
					}

					await queueOperation({
						type: 'create',
						entity: 'task',
						data: {},
						endpoint: `/tasks/${taskId}/toggle`
					});

					return { success: true, task: updatedTask };
				}

				const updatedTask: any = await api.tasks.toggle(taskId);
				await offlineTasks.save(updatedTask);

				update((state) => ({
					...state,
					tasks: state.tasks.map((t) => (t.id === taskId ? updatedTask : t))
				}));

				return { success: true, task: updatedTask };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to toggle task';
				return { success: false, error: errorMessage };
			}
		},

		async deleteTask(taskId: string) {
			try {
				if (!isOnline()) {
					await offlineTasks.delete(taskId);
					await queueOperation({
						type: 'delete',
						entity: 'task',
						data: {},
						endpoint: `/tasks/${taskId}`
					});

					update((state) => ({
						...state,
						tasks: state.tasks.filter((t) => t.id !== taskId)
					}));

					return { success: true };
				}

				await api.tasks.delete(taskId);

				update((state) => ({
					...state,
					tasks: state.tasks.filter((t) => t.id !== taskId)
				}));

				return { success: true };
			} catch (error: any) {
				const errorMessage = error.detail || 'Failed to delete task';
				return { success: false, error: errorMessage };
			}
		},

		async searchTasks(query: string) {
			update((state) => ({ ...state, isLoading: true }));

			try {
				if (!isOnline()) {
					const offlineItems = await offlineTasks.getAll();
					const q = query.toLowerCase();
					const tasks = offlineItems.filter((task: Task) => {
						return (
							task.title.toLowerCase().includes(q) ||
							(task.description || '').toLowerCase().includes(q)
						);
					});

					update((state) => ({
						...state,
						tasks,
						isLoading: false,
						filters: { ...state.filters, search: query }
					}));

					return { success: true, tasks };
				}

				const response: any = await api.tasks.search(query);
				const tasks = response.tasks || [];

				update((state) => ({
					...state,
					tasks,
					isLoading: false,
					filters: { ...state.filters, search: query }
				}));

				return { success: true, tasks };
			} catch (error: any) {
				const errorMessage = error.detail || 'Search failed';
				update((state) => ({
					...state,
					isLoading: false,
					error: errorMessage
				}));
				return { success: false, error: errorMessage };
			}
		},

		clearError() {
			update((state) => ({ ...state, error: null }));
		},

		clearFilters() {
			update((state) => ({ ...state, filters: {} }));
		}
	};
}

export const tasksStore = createTasksStore();
