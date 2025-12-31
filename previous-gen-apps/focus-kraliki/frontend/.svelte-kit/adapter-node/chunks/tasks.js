import { w as writable } from "./index.js";
import { a as api } from "./client.js";
import { i as isOnline, b as offlineTasks, q as queueOperation, c as clearOfflineStore, O as OFFLINE_STORES } from "./offlineStorage.js";
const initialState = {
  tasks: [],
  isLoading: false,
  error: null,
  filters: {}
};
function createTasksStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    async loadTasks(filters) {
      update((state) => ({ ...state, isLoading: true, error: null, filters: filters || {} }));
      try {
        if (!isOnline()) {
          const offlineItems = await offlineTasks.getAll();
          const tasks2 = offlineItems.filter((task) => {
            if (filters?.status && task.status !== filters.status) return false;
            if (filters?.type && task.type !== filters.type) return false;
            if (filters?.priority && task.priority !== filters.priority) return false;
            if (filters?.search) {
              const q = filters.search.toLowerCase();
              return task.title.toLowerCase().includes(q) || (task.description || "").toLowerCase().includes(q);
            }
            return true;
          });
          update((state) => ({
            ...state,
            tasks: tasks2,
            isLoading: false
          }));
          return { success: true, tasks: tasks2 };
        }
        const response = await api.tasks.list(filters);
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
      } catch (error) {
        const errorMessage = error.detail || "Failed to load tasks";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async createTask(taskData) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          const offlineTask = {
            id: crypto.randomUUID?.() || `offline-${Date.now()}`,
            title: taskData.title || "Untitled task",
            description: taskData.description,
            status: taskData.status || "PENDING",
            priority: taskData.priority || "MEDIUM",
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
            type: "create",
            entity: "task",
            data: taskData,
            endpoint: "/tasks"
          });
          update((state) => ({
            ...state,
            tasks: [offlineTask, ...state.tasks]
          }));
          return { success: true, task: offlineTask };
        }
        const newTask = await api.tasks.create(taskData);
        await offlineTasks.save(newTask);
        update((state) => ({
          ...state,
          tasks: [newTask, ...state.tasks]
        }));
        return { success: true, task: newTask };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create task";
        return { success: false, error: errorMessage };
      }
    },
    async updateTask(taskId, updates) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          let updatedTask2 = null;
          update((state) => {
            const tasks = state.tasks.map((task) => {
              if (task.id !== taskId) return task;
              updatedTask2 = {
                ...task,
                ...updates,
                updated_at: now
              };
              return updatedTask2;
            });
            return {
              ...state,
              tasks
            };
          });
          if (updatedTask2) {
            await offlineTasks.save(updatedTask2);
          }
          await queueOperation({
            type: "update",
            entity: "task",
            data: updates,
            endpoint: `/tasks/${taskId}`
          });
          return { success: true, task: updatedTask2 };
        }
        const updatedTask = await api.tasks.update(taskId, updates);
        await offlineTasks.save(updatedTask);
        update((state) => ({
          ...state,
          tasks: state.tasks.map((t) => t.id === taskId ? updatedTask : t)
        }));
        return { success: true, task: updatedTask };
      } catch (error) {
        const errorMessage = error.detail || "Failed to update task";
        return { success: false, error: errorMessage };
      }
    },
    async toggleTask(taskId) {
      try {
        if (!isOnline()) {
          let updatedTask2 = null;
          update((state) => {
            const tasks = state.tasks.map((task) => {
              if (task.id !== taskId) return task;
              const nextStatus = task.status === "COMPLETED" ? "PENDING" : "COMPLETED";
              updatedTask2 = {
                ...task,
                status: nextStatus,
                completed_at: nextStatus === "COMPLETED" ? (/* @__PURE__ */ new Date()).toISOString() : void 0
              };
              return updatedTask2;
            });
            return {
              ...state,
              tasks
            };
          });
          if (updatedTask2) {
            await offlineTasks.save(updatedTask2);
          }
          await queueOperation({
            type: "create",
            entity: "task",
            data: {},
            endpoint: `/tasks/${taskId}/toggle`
          });
          return { success: true, task: updatedTask2 };
        }
        const updatedTask = await api.tasks.toggle(taskId);
        await offlineTasks.save(updatedTask);
        update((state) => ({
          ...state,
          tasks: state.tasks.map((t) => t.id === taskId ? updatedTask : t)
        }));
        return { success: true, task: updatedTask };
      } catch (error) {
        const errorMessage = error.detail || "Failed to toggle task";
        return { success: false, error: errorMessage };
      }
    },
    async deleteTask(taskId) {
      try {
        if (!isOnline()) {
          await offlineTasks.delete(taskId);
          await queueOperation({
            type: "delete",
            entity: "task",
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
      } catch (error) {
        const errorMessage = error.detail || "Failed to delete task";
        return { success: false, error: errorMessage };
      }
    },
    async searchTasks(query) {
      update((state) => ({ ...state, isLoading: true }));
      try {
        if (!isOnline()) {
          const offlineItems = await offlineTasks.getAll();
          const q = query.toLowerCase();
          const tasks2 = offlineItems.filter((task) => {
            return task.title.toLowerCase().includes(q) || (task.description || "").toLowerCase().includes(q);
          });
          update((state) => ({
            ...state,
            tasks: tasks2,
            isLoading: false,
            filters: { ...state.filters, search: query }
          }));
          return { success: true, tasks: tasks2 };
        }
        const response = await api.tasks.search(query);
        const tasks = response.tasks || [];
        update((state) => ({
          ...state,
          tasks,
          isLoading: false,
          filters: { ...state.filters, search: query }
        }));
        return { success: true, tasks };
      } catch (error) {
        const errorMessage = error.detail || "Search failed";
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
const tasksStore = createTasksStore();
export {
  tasksStore as t
};
