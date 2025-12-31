// Voice by Kraliki PWA Service Worker
const CACHE_VERSION = 'cc-lite-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/offline.html'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...', CACHE_VERSION);
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[Service Worker] Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...', CACHE_VERSION);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return cacheName.startsWith('cc-lite-') &&
                   cacheName !== STATIC_CACHE &&
                   cacheName !== DYNAMIC_CACHE;
          })
          .map((cacheName) => {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip WebSocket and API requests
  if (request.url.includes('/ws') ||
      request.url.includes('/api/') ||
      request.url.includes('chrome-extension')) {
    return;
  }

  event.respondWith(
    // Network first strategy
    fetch(request)
      .then((response) => {
        // Cache successful responses
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Fallback to cache
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }

          // Fallback to offline page for navigation requests
          if (request.mode === 'navigate') {
            return caches.match('/offline.html');
          }

          return new Response('Network error', {
            status: 408,
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});

// Push notification event
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Voice by Kraliki Notification';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icons/icon-192.png',
    badge: '/icons/badge.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: data.actions || []
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Focus existing window if available
      for (const client of clientList) {
        if (client.url === event.notification.data.url && 'focus' in client) {
          return client.focus();
        }
      }
      // Open new window
      if (clients.openWindow) {
        return clients.openWindow(event.notification.data.url || '/');
      }
    })
  );
});

// Background sync event (for offline operations)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-calls') {
    event.waitUntil(syncCalls());
  }
});

async function syncCalls() {
  // Sync queued calls when back online
  console.log('[Service Worker] Syncing offline calls...');
  // Implementation would sync with backend
}
