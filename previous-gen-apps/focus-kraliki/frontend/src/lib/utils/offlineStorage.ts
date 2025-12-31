/**
 * Offline Storage Module using IndexedDB
 *
 * Provides offline-first data persistence for Focus by Kraliki PWA
 * Addresses CR-003 and H-010 from BACKLOG.md
 *
 * Features:
 * - IndexedDB wrapper for tasks, projects, knowledge items
 * - Offline queue for pending operations
 * - Background sync when connection restored
 * - Conflict resolution with server
 */

import { logger } from '$lib/utils/logger';

const DB_NAME = 'focus-kraliki-offline';
const DB_VERSION = 2;

// Store names
export const OFFLINE_STORES = {
  TASKS: 'tasks',
  PROJECTS: 'projects',
  KNOWLEDGE: 'knowledge',
  KNOWLEDGE_TYPES: 'knowledgeTypes',
  TIME_ENTRIES: 'timeEntries',
  QUEUE: 'syncQueue'
};

/**
 * Initialize IndexedDB database
 */
export async function initOfflineDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => {
      logger.error('Failed to open IndexedDB');
      reject(request.error);
    };

    request.onsuccess = () => {
      resolve(request.result);
    };

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;

      // Tasks store
      if (!db.objectStoreNames.contains(OFFLINE_STORES.TASKS)) {
        const taskStore = db.createObjectStore(OFFLINE_STORES.TASKS, { keyPath: 'id' });
        taskStore.createIndex('status', 'status', { unique: false });
        taskStore.createIndex('dueDate', 'dueDate', { unique: false });
        taskStore.createIndex('projectId', 'projectId', { unique: false });
        taskStore.createIndex('updatedAt', 'updatedAt', { unique: false });
      }

      // Projects store
      if (!db.objectStoreNames.contains(OFFLINE_STORES.PROJECTS)) {
        const projectStore = db.createObjectStore(OFFLINE_STORES.PROJECTS, { keyPath: 'id' });
        projectStore.createIndex('name', 'name', { unique: false });
        projectStore.createIndex('updatedAt', 'updatedAt', { unique: false });
      }

      // Knowledge items store
      if (!db.objectStoreNames.contains(OFFLINE_STORES.KNOWLEDGE)) {
        const knowledgeStore = db.createObjectStore(OFFLINE_STORES.KNOWLEDGE, { keyPath: 'id' });
        knowledgeStore.createIndex('typeId', 'typeId', { unique: false });
        knowledgeStore.createIndex('completed', 'completed', { unique: false });
        knowledgeStore.createIndex('updatedAt', 'updatedAt', { unique: false });
      }

      // Knowledge item types store
      if (!db.objectStoreNames.contains(OFFLINE_STORES.KNOWLEDGE_TYPES)) {
        const typesStore = db.createObjectStore(OFFLINE_STORES.KNOWLEDGE_TYPES, { keyPath: 'id' });
        typesStore.createIndex('name', 'name', { unique: false });
      }

      // Time entries store
      if (!db.objectStoreNames.contains(OFFLINE_STORES.TIME_ENTRIES)) {
        const timeStore = db.createObjectStore(OFFLINE_STORES.TIME_ENTRIES, { keyPath: 'id' });
        timeStore.createIndex('taskId', 'taskId', { unique: false });
        timeStore.createIndex('projectId', 'projectId', { unique: false });
        timeStore.createIndex('startTime', 'startTime', { unique: false });
      }

      // Sync queue store (for offline operations)
      if (!db.objectStoreNames.contains(OFFLINE_STORES.QUEUE)) {
        const queueStore = db.createObjectStore(OFFLINE_STORES.QUEUE, {
          keyPath: 'id',
          autoIncrement: true
        });
        queueStore.createIndex('timestamp', 'timestamp', { unique: false });
        queueStore.createIndex('type', 'type', { unique: false });
      }
    };
  });
}

/**
 * Generic function to save data to IndexedDB
 */
export async function saveOffline<T extends { id: string }>(
  storeName: string,
  data: T
): Promise<void> {
  const db = await initOfflineDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);

    // Add timestamp for sync tracking
    const dataWithTimestamp = {
      ...data,
      _offlineUpdatedAt: new Date().toISOString()
    };

    const request = store.put(dataWithTimestamp);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

/**
 * Get item from offline storage
 */
export async function getOffline<T>(
  storeName: string,
  id: string
): Promise<T | null> {
  const db = await initOfflineDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.get(id);

    request.onsuccess = () => {
      resolve(request.result || null);
    };
    request.onerror = () => reject(request.error);
  });
}

/**
 * Get all items from offline storage
 */
export async function getAllOffline<T>(storeName: string): Promise<T[]> {
  const db = await initOfflineDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();

    request.onsuccess = () => {
      resolve(request.result);
    };
    request.onerror = () => reject(request.error);
  });
}

/**
 * Delete item from offline storage
 */
export async function deleteOffline(
  storeName: string,
  id: string
): Promise<void> {
  const db = await initOfflineDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

/**
 * Queue operation for background sync
 */
export async function queueOperation(operation: {
  type: 'create' | 'update' | 'delete';
  entity: 'task' | 'project' | 'knowledge' | 'timeEntry';
  data: any;
  endpoint: string;
}): Promise<void> {
  const queueItem = {
    id: crypto.randomUUID?.() || `queue-${Date.now()}`,
    ...operation,
    timestamp: new Date().toISOString(),
    retries: 0,
    status: 'pending'
  };

  await saveOffline(OFFLINE_STORES.QUEUE, queueItem);
}

/**
 * Get pending sync operations
 */
export async function getPendingOperations(): Promise<any[]> {
  return getAllOffline(OFFLINE_STORES.QUEUE);
}

/**
 * Clear completed sync operation
 */
export async function clearSyncOperation(id: string): Promise<void> {
  return deleteOffline(OFFLINE_STORES.QUEUE, id);
}

/**
 * Offline-first task operations
 */
export const offlineTasks = {
  async save(task: any): Promise<void> {
    await saveOffline(OFFLINE_STORES.TASKS, task);
  },

  async get(id: string): Promise<any> {
    return getOffline(OFFLINE_STORES.TASKS, id);
  },

  async getAll(): Promise<any[]> {
    return getAllOffline(OFFLINE_STORES.TASKS);
  },

  async delete(id: string): Promise<void> {
    return deleteOffline(OFFLINE_STORES.TASKS, id);
  },

  async getByStatus(status: string): Promise<any[]> {
    const db = await initOfflineDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([OFFLINE_STORES.TASKS], 'readonly');
      const store = transaction.objectStore(OFFLINE_STORES.TASKS);
      const index = store.index('status');
      const request = index.getAll(status);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
};

/**
 * Offline-first project operations
 */
export const offlineProjects = {
  async save(project: any): Promise<void> {
    await saveOffline(OFFLINE_STORES.PROJECTS, project);
  },

  async get(id: string): Promise<any> {
    return getOffline(OFFLINE_STORES.PROJECTS, id);
  },

  async getAll(): Promise<any[]> {
    return getAllOffline(OFFLINE_STORES.PROJECTS);
  },

  async delete(id: string): Promise<void> {
    return deleteOffline(OFFLINE_STORES.PROJECTS, id);
  }
};

/**
 * Offline-first knowledge operations
 */
export const offlineKnowledge = {
  async save(item: any): Promise<void> {
    await saveOffline(OFFLINE_STORES.KNOWLEDGE, item);
  },

  async get(id: string): Promise<any> {
    return getOffline(OFFLINE_STORES.KNOWLEDGE, id);
  },

  async getAll(): Promise<any[]> {
    return getAllOffline(OFFLINE_STORES.KNOWLEDGE);
  },

  async delete(id: string): Promise<void> {
    return deleteOffline(OFFLINE_STORES.KNOWLEDGE, id);
  },

  async getByType(typeId: string): Promise<any[]> {
    const db = await initOfflineDB();

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([OFFLINE_STORES.KNOWLEDGE], 'readonly');
      const store = transaction.objectStore(OFFLINE_STORES.KNOWLEDGE);
      const index = store.index('typeId');
      const request = index.getAll(typeId);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
};

/**
 * Offline-first time entry operations
 */
export const offlineTimeEntries = {
  async save(entry: any): Promise<void> {
    await saveOffline(OFFLINE_STORES.TIME_ENTRIES, entry);
  },

  async get(id: string): Promise<any> {
    return getOffline(OFFLINE_STORES.TIME_ENTRIES, id);
  },

  async getAll(): Promise<any[]> {
    return getAllOffline(OFFLINE_STORES.TIME_ENTRIES);
  },

  async delete(id: string): Promise<void> {
    return deleteOffline(OFFLINE_STORES.TIME_ENTRIES, id);
  }
};

/**
 * Check if online
 */
export function isOnline(): boolean {
  if (typeof navigator === 'undefined') {
    return true;
  }
  return navigator.onLine;
}

/**
 * Sync offline data with server
 * Called when connection is restored
 */
export async function syncWithServer(apiClient: any): Promise<{
  success: number;
  failed: number;
  errors: any[];
}> {
  if (!isOnline()) {
    return { success: 0, failed: 0, errors: [] };
  }

  const pendingOps = await getPendingOperations();
  const results = { success: 0, failed: 0, errors: [] as any[] };

  for (const op of pendingOps) {
    try {
      // Execute operation via API
      switch (op.type) {
        case 'create':
          await apiClient.post(op.endpoint, op.data);
          break;
        case 'update':
          await apiClient.patch(op.endpoint, op.data);
          break;
        case 'delete':
          await apiClient.delete(op.endpoint);
          break;
      }

      // Clear from queue on success
      await clearSyncOperation(op.id);
      results.success++;
    } catch (error) {
      logger.error(`Failed to sync operation ${op.id}`, error);
      results.failed++;
      results.errors.push({ op, error });
    }
  }

  return results;
}

/**
 * Clear all offline data (for logout/reset)
 */
export async function clearAllOfflineData(): Promise<void> {
  const db = await initOfflineDB();

  const stores = [
    OFFLINE_STORES.TASKS,
    OFFLINE_STORES.PROJECTS,
    OFFLINE_STORES.KNOWLEDGE,
    OFFLINE_STORES.KNOWLEDGE_TYPES,
    OFFLINE_STORES.TIME_ENTRIES,
    OFFLINE_STORES.QUEUE
  ];

  for (const storeName of stores) {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    await new Promise((resolve) => {
      const request = store.clear();
      request.onsuccess = () => resolve(undefined);
    });
  }
}

export async function clearOfflineStore(storeName: string): Promise<void> {
  const db = await initOfflineDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.clear();

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

export const offlineKnowledgeTypes = {
  async save(item: any): Promise<void> {
    await saveOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, item);
  },

  async get(id: string): Promise<any> {
    return getOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, id);
  },

  async getAll(): Promise<any[]> {
    return getAllOffline(OFFLINE_STORES.KNOWLEDGE_TYPES);
  },

  async delete(id: string): Promise<void> {
    return deleteOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, id);
  }
};
