/**
 * RCCM試験問題集アプリ - Service Worker (DISABLED)
 * PWA機能無効化済み - URL管理のみ使用
 */

// Service Worker disabled per user request
console.log('Service Worker disabled - URL management only');

// Immediately unregister to prevent PWA installation
self.addEventListener('install', function(event) {
  console.log('Service Worker installation blocked');
  // No caching, no installation
});

self.addEventListener('activate', function(event) {
  console.log('Service Worker activation blocked');
  // Clear any existing caches
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          return caches.delete(cacheName);
        })
      );
    })
  );
});

self.addEventListener('fetch', function(event) {
  // No caching, just pass through to network
  return;
});

// Disable PWA features completely
self.registration.unregister();