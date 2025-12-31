/**
 * Service Worker for Focus by Kraliki PWA
 * Provides offline functionality and asset caching
 */

const CACHE_NAME = 'focus-kraliki-v1';
const STATIC_CACHE = 'focus-kraliki-static-v1';
const DYNAMIC_CACHE = 'focus-kraliki-dynamic-v1';

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

const LOG_LEVEL = (() => {
  const host = self.location.hostname;
  const isDev =
    host === 'localhost' ||
    host === '127.0.0.1' ||
    host.endsWith('.verduona.dev');
  return isDev ? 'DEBUG' : 'WARN';
})();

function shouldLog(level) {
  return LOG_LEVELS[level] >= LOG_LEVELS[LOG_LEVEL];
}

function log(level, message, extra) {
  if (!shouldLog(level)) return;
  const fn = level === 'ERROR' ? console.error : level === 'WARN' ? console.warn : console.log;
  if (typeof extra !== 'undefined') {
    fn(message, extra);
  } else {
    fn(message);
  }
}

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/dashboard',
  '/dashboard/tasks',
  '/dashboard/calendar',
  '/dashboard/time',
  '/dashboard/projects',
  '/dashboard/shadow',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  log('INFO', '[SW] Installing service worker...');

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        log('INFO', '[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  log('INFO', '[SW] Activating service worker...');

  event.waitUntil(
    caches.keys()
      .then((keys) => {
        return Promise.all(
          keys
            .filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
            .map(key => caches.delete(key))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip cross-origin requests
  if (!request.url.startsWith(self.location.origin)) {
    return;
  }

  // API requests - network first, then cache
  if (request.url.includes('/api/') || request.url.includes('localhost:8001')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Static assets - cache first, then network
  event.respondWith(cacheFirst(request));
});

/**
 * Cache-first strategy for static assets
 */
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    const cache = await caches.open(DYNAMIC_CACHE);
    cache.put(request, response.clone());
    return response;
  } catch (error) {
    log('ERROR', '[SW] Fetch failed:', error);
    return new Response('Offline - content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

/**
 * Network-first strategy for API requests
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    const cache = await caches.open(DYNAMIC_CACHE);
    cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }

    return new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Push notification event
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Focus by Kraliki';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icon-192.svg',
    badge: '/icon-72.svg',
    vibrate: [200, 100, 200],
    tag: data.tag || 'default',
    data: data.url || '/'
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});

// Background sync event
self.addEventListener('sync', (event) => {
  log('INFO', '[SW] Background sync:', event.tag);

  if (event.tag === 'sync-offline-data') {
    event.waitUntil(syncOfflineData());
  }
});

/**
 * Sync offline data with server
 * Called when connection is restored
 */
async function syncOfflineData() {
  log('INFO', '[SW] Syncing offline data with server...');

  try {
    // Open IndexedDB
    const db = await openDB();

    // Get all pending operations from queue
    const transaction = db.transaction(['syncQueue'], 'readonly');
    const store = transaction.objectStore('syncQueue');
    const operations = await new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });

    log('DEBUG', `[SW] Found ${operations.length} pending operations`);

    // Process each operation
    for (const op of operations) {
      try {
        const response = await fetch(op.endpoint, {
          method: op.method || 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${op.token || ''}`
          },
          body: JSON.stringify(op.data)
        });

        if (response.ok) {
          // Remove from queue on success
          const deleteTransaction = db.transaction(['syncQueue'], 'readwrite');
          const deleteStore = deleteTransaction.objectStore('syncQueue');
          deleteStore.delete(op.id);

          log('DEBUG', `[SW] Synced operation ${op.id}`);
        } else {
          log('ERROR', `[SW] Failed to sync operation ${op.id}:`, response.status);
        }
      } catch (error) {
        log('ERROR', `[SW] Error syncing operation ${op.id}:`, error);
      }
    }

    log('INFO', '[SW] Offline data sync completed');
  } catch (error) {
    log('ERROR', '[SW] Failed to sync offline data:', error);
  }
}

/**
 * Open IndexedDB connection
 */
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('focus-kraliki-offline', 2);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create stores if they don't exist
      if (!db.objectStoreNames.contains('tasks')) {
        const taskStore = db.createObjectStore('tasks', { keyPath: 'id' });
        taskStore.createIndex('status', 'status', { unique: false });
      }

      if (!db.objectStoreNames.contains('projects')) {
        db.createObjectStore('projects', { keyPath: 'id' });
      }

      if (!db.objectStoreNames.contains('knowledge')) {
        const knowledgeStore = db.createObjectStore('knowledge', { keyPath: 'id' });
        knowledgeStore.createIndex('typeId', 'typeId', { unique: false });
      }

      if (!db.objectStoreNames.contains('knowledgeTypes')) {
        const typesStore = db.createObjectStore('knowledgeTypes', { keyPath: 'id' });
        typesStore.createIndex('name', 'name', { unique: false });
      }

      if (!db.objectStoreNames.contains('timeEntries')) {
        db.createObjectStore('timeEntries', { keyPath: 'id' });
      }

      if (!db.objectStoreNames.contains('syncQueue')) {
        const queueStore = db.createObjectStore('syncQueue', {
          keyPath: 'id',
          autoIncrement: true
        });
        queueStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
}

// Message event for manual sync trigger
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SYNC_OFFLINE') {
    event.waitUntil(syncOfflineData());
  }
});
