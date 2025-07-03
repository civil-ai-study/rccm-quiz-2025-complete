// RCCM試験問題集2025 - Service Worker (オフライン対応)

const CACHE_NAME = 'rccm-quiz-2025-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/js/app.js',
    '/data/questions.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// インストール時
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Service Worker: キャッシュオープン');
                return cache.addAll(urlsToCache);
            })
    );
});

// フェッチ時 (オフライン対応)
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // キャッシュにある場合はキャッシュから返す
                if (response) {
                    return response;
                }
                
                // ネットワークから取得を試みる
                return fetch(event.request).then(function(response) {
                    // 有効なレスポンスかチェック
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    // レスポンスをキャッシュに保存
                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });
                    
                    return response;
                }).catch(function() {
                    // オフライン時のフォールバック
                    if (event.request.destination === 'document') {
                        return caches.match('/index.html');
                    }
                });
            })
    );
});

// アクティベート時 (古いキャッシュ削除)
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: 古いキャッシュを削除', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

console.log('Service Worker: 登録完了 - オフライン対応準備完了');