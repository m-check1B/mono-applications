import { l as logger } from "./logger.js";
const DB_NAME = "focus-kraliki-offline";
const DB_VERSION = 2;
const OFFLINE_STORES = {
  TASKS: "tasks",
  PROJECTS: "projects",
  KNOWLEDGE: "knowledge",
  KNOWLEDGE_TYPES: "knowledgeTypes",
  TIME_ENTRIES: "timeEntries",
  QUEUE: "syncQueue"
};
async function initOfflineDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => {
      logger.error("Failed to open IndexedDB");
      reject(request.error);
    };
    request.onsuccess = () => {
      resolve(request.result);
    };
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(OFFLINE_STORES.TASKS)) {
        const taskStore = db.createObjectStore(OFFLINE_STORES.TASKS, { keyPath: "id" });
        taskStore.createIndex("status", "status", { unique: false });
        taskStore.createIndex("dueDate", "dueDate", { unique: false });
        taskStore.createIndex("projectId", "projectId", { unique: false });
        taskStore.createIndex("updatedAt", "updatedAt", { unique: false });
      }
      if (!db.objectStoreNames.contains(OFFLINE_STORES.PROJECTS)) {
        const projectStore = db.createObjectStore(OFFLINE_STORES.PROJECTS, { keyPath: "id" });
        projectStore.createIndex("name", "name", { unique: false });
        projectStore.createIndex("updatedAt", "updatedAt", { unique: false });
      }
      if (!db.objectStoreNames.contains(OFFLINE_STORES.KNOWLEDGE)) {
        const knowledgeStore = db.createObjectStore(OFFLINE_STORES.KNOWLEDGE, { keyPath: "id" });
        knowledgeStore.createIndex("typeId", "typeId", { unique: false });
        knowledgeStore.createIndex("completed", "completed", { unique: false });
        knowledgeStore.createIndex("updatedAt", "updatedAt", { unique: false });
      }
      if (!db.objectStoreNames.contains(OFFLINE_STORES.KNOWLEDGE_TYPES)) {
        const typesStore = db.createObjectStore(OFFLINE_STORES.KNOWLEDGE_TYPES, { keyPath: "id" });
        typesStore.createIndex("name", "name", { unique: false });
      }
      if (!db.objectStoreNames.contains(OFFLINE_STORES.TIME_ENTRIES)) {
        const timeStore = db.createObjectStore(OFFLINE_STORES.TIME_ENTRIES, { keyPath: "id" });
        timeStore.createIndex("taskId", "taskId", { unique: false });
        timeStore.createIndex("projectId", "projectId", { unique: false });
        timeStore.createIndex("startTime", "startTime", { unique: false });
      }
      if (!db.objectStoreNames.contains(OFFLINE_STORES.QUEUE)) {
        const queueStore = db.createObjectStore(OFFLINE_STORES.QUEUE, {
          keyPath: "id",
          autoIncrement: true
        });
        queueStore.createIndex("timestamp", "timestamp", { unique: false });
        queueStore.createIndex("type", "type", { unique: false });
      }
    };
  });
}
async function saveOffline(storeName, data) {
  const db = await initOfflineDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);
    const dataWithTimestamp = {
      ...data,
      _offlineUpdatedAt: (/* @__PURE__ */ new Date()).toISOString()
    };
    const request = store.put(dataWithTimestamp);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}
async function getOffline(storeName, id) {
  const db = await initOfflineDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);
    const request = store.get(id);
    request.onsuccess = () => {
      resolve(request.result || null);
    };
    request.onerror = () => reject(request.error);
  });
}
async function getAllOffline(storeName) {
  const db = await initOfflineDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    request.onsuccess = () => {
      resolve(request.result);
    };
    request.onerror = () => reject(request.error);
  });
}
async function deleteOffline(storeName, id) {
  const db = await initOfflineDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}
async function queueOperation(operation) {
  const queueItem = {
    id: crypto.randomUUID?.() || `queue-${Date.now()}`,
    ...operation,
    timestamp: (/* @__PURE__ */ new Date()).toISOString(),
    retries: 0,
    status: "pending"
  };
  await saveOffline(OFFLINE_STORES.QUEUE, queueItem);
}
const offlineTasks = {
  async save(task) {
    await saveOffline(OFFLINE_STORES.TASKS, task);
  },
  async get(id) {
    return getOffline(OFFLINE_STORES.TASKS, id);
  },
  async getAll() {
    return getAllOffline(OFFLINE_STORES.TASKS);
  },
  async delete(id) {
    return deleteOffline(OFFLINE_STORES.TASKS, id);
  },
  async getByStatus(status) {
    const db = await initOfflineDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([OFFLINE_STORES.TASKS], "readonly");
      const store = transaction.objectStore(OFFLINE_STORES.TASKS);
      const index = store.index("status");
      const request = index.getAll(status);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
};
const offlineProjects = {
  async save(project) {
    await saveOffline(OFFLINE_STORES.PROJECTS, project);
  },
  async get(id) {
    return getOffline(OFFLINE_STORES.PROJECTS, id);
  },
  async getAll() {
    return getAllOffline(OFFLINE_STORES.PROJECTS);
  },
  async delete(id) {
    return deleteOffline(OFFLINE_STORES.PROJECTS, id);
  }
};
const offlineKnowledge = {
  async save(item) {
    await saveOffline(OFFLINE_STORES.KNOWLEDGE, item);
  },
  async get(id) {
    return getOffline(OFFLINE_STORES.KNOWLEDGE, id);
  },
  async getAll() {
    return getAllOffline(OFFLINE_STORES.KNOWLEDGE);
  },
  async delete(id) {
    return deleteOffline(OFFLINE_STORES.KNOWLEDGE, id);
  },
  async getByType(typeId) {
    const db = await initOfflineDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([OFFLINE_STORES.KNOWLEDGE], "readonly");
      const store = transaction.objectStore(OFFLINE_STORES.KNOWLEDGE);
      const index = store.index("typeId");
      const request = index.getAll(typeId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
};
const offlineTimeEntries = {
  async save(entry) {
    await saveOffline(OFFLINE_STORES.TIME_ENTRIES, entry);
  },
  async get(id) {
    return getOffline(OFFLINE_STORES.TIME_ENTRIES, id);
  },
  async getAll() {
    return getAllOffline(OFFLINE_STORES.TIME_ENTRIES);
  },
  async delete(id) {
    return deleteOffline(OFFLINE_STORES.TIME_ENTRIES, id);
  }
};
function isOnline() {
  if (typeof navigator === "undefined") {
    return true;
  }
  return navigator.onLine;
}
async function clearOfflineStore(storeName) {
  const db = await initOfflineDB();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);
    const request = store.clear();
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}
const offlineKnowledgeTypes = {
  async save(item) {
    await saveOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, item);
  },
  async get(id) {
    return getOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, id);
  },
  async getAll() {
    return getAllOffline(OFFLINE_STORES.KNOWLEDGE_TYPES);
  },
  async delete(id) {
    return deleteOffline(OFFLINE_STORES.KNOWLEDGE_TYPES, id);
  }
};
export {
  OFFLINE_STORES as O,
  offlineTimeEntries as a,
  offlineTasks as b,
  clearOfflineStore as c,
  offlineKnowledge as d,
  offlineKnowledgeTypes as e,
  isOnline as i,
  offlineProjects as o,
  queueOperation as q
};
