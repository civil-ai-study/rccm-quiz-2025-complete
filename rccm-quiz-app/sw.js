/**
 * RCCM問題集アプリ - Service Worker
 * PWAオフライン対応・キャッシュ管理
 */

const CACHE_NAME = 'rccm-quiz-v1.0.0';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/data/questions.csv',
  
  // 静的ファイル（CSS, JS, 画像）のパスを追加
  // プロジェクト構造に合わせて適宜変更してください
  '/static/css/style.css', // もしstyle.cssがある場合
  '/static/js/main.js',   // もしmain.jsがある場合
  
  // マニフェストファイルで参照されているアイコンファイル
  '/icon-72x72.png',
  '/icon-96x96.png',
  '/icon-128x128.png',
  '/icon-144x144.png',
  '/icon-152x152.png',
  '/icon-192x192.png',
  '/icon-384x384.png',
  '/icon-512x512.png',
  
  // CDNリソース (base.html で使用されているもの)
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  // Chart.js や PapaParse を使用する場合はそのCDNパスも追加（もしクライアントサイドで使用するなら）
  // 'https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js',
  // 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js',
];

// インストール時のキャッシュ
self.addEventListener('install', event => {
  console.log('[Service Worker] Install');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching app shell');
        // addAllは一つでも失敗すると全体が失敗するため、エラーが発生しやすいCDNリソースは除外する
        const localUrls = urlsToCache.filter(url => !url.startsWith('http'));
        return cache.addAll(localUrls).catch(err => {
            console.warn('[Service Worker] addAll failed for some local resources:', err);
            // addAllが一部失敗してもインストールは続行させる
            return Promise.resolve();
        });
      })
      .then(() => {
          console.log('[Service Worker] App shell cached (local resources)');
          // CDNリソースは個別にキャッシュするか、他のキャッシュ戦略で対応
          // return Promise.all(urlsToCache.filter(url => url.startsWith('http')).map(url => caches.open(CACHE_NAME).then(cache => cache.add(url).catch(err => console.warn(`[Service Worker] Failed to cache CDN: ${url}`, err)))));
      })
      .catch(err => {
        console.error('[Service Worker] Cache open or initial addAll error:', err);
        // 重大なエラーの場合、インストールをスキップする
        throw err;
      })
  );
  
  // 即座にアクティブ化
  self.skipWaiting();
});

// アクティベート時の古いキャッシュ削除
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activate');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // 即座にクライアントを制御
  self.clients.claim();
});

// フェッチイベントの処理
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // POSTリクエストやAPIリクエストはネットワーク優先（バックグラウンド同期で対応）
  if (request.method !== 'GET' || request.url.includes('/api/')) {
     event.respondWith(fetch(request).catch(err => {
         console.error(`[Service Worker] Network fetch failed for ${request.url}:`, err);
         // APIフェッチ失敗時などのエラーハンドリング（必要であればオフラインフォールバックなど）
         throw err; // エラーを再スロー
     }));
     return;
  }
  
  // GETリクエストのキャッシュ戦略: Cache First, then Network
  event.respondWith(
    caches.match(request).then(response => {
      // キャッシュにあればそれを返す
      if (response) {
        // console.log('[Service Worker] Cache hit:', request.url);
        return response;
      }
      
      // なければネットワークから取得し、キャッシュに入れる
      console.log('[Service Worker] Fetching from network:', request.url);
      
      return fetch(request).then(response => {
        // 有効なレスポンスかチェック (ステータス200)
        if (!response || response.status !== 200) {
          return response; // 無効なレスポンスはそのまま返す
        }
        
        // レスポンスをクローン（キャッシュ用）
        const responseToCache = response.clone();
        
        // 動的にキャッシュに追加
        caches.open(CACHE_NAME)
          .then(cache => { // Service Worker内では cache.put が安全
            cache.put(request, responseToCache);
          })
          .catch(err => {
              console.warn(`[Service Worker] Failed to cache ${request.url}:`, err);
          });
        
        return response; // ネットワークレスポンスを返す
      })
      .catch(networkError => {
         console.error(`[Service Worker] Network fetch failed for ${request.url}:`, networkError);
         // ネットワークエラー時のフォールバック
         // HTMLドキュメントの場合はオフラインページを返す
         if (request.destination === 'document') {
            return caches.match('/offline.html').catch(cacheErr => {
               console.error('[Service Worker] Offline page cache miss:', cacheErr);
               // オフラインページもキャッシュにない場合
               // ユーザーにエラーを伝えるなど
               // return new Response('<h1>Offline</h1><p>Please check your internet connection.</p>', { headers: { 'Content-Type': 'text/html' } });
               throw cacheErr; // エラーを再スロー
            });
         }
         // ドキュメント以外のリクエスト（CSS, JS, 画像など）でネットワークエラーの場合、
         // キャッシュにもない場合はエラーとなる
         throw networkError; 
      });
    })
  );
});

// バックグラウンド同期 (app.pyで実装されている /api/sync エンドポイントと連携)
// クライアントサイドJSで SyncManager.register('sync-study-data') を呼び出す必要があります。
self.addEventListener('sync', event => {
  console.log('[Service Worker] Sync event triggered with tag:', event.tag);
  
  if (event.tag === 'sync-study-data') {
    // この部分はクライアントサイドのスクリプト（IndexedDBなど）と連携して
    // オフライン中に記録された学習データを取得し、サーバーに送信する処理を実装する必要があります。
    // 現状では、これは単なるプレースホルダーです。
    event.waitUntil((async function() {
      try {
        const pendingData = await getPendingDataFromIndexedDB(); // IndexedDBからの取得はクライアント側JSで実装
        if (!pendingData || pendingData.length === 0) {
          console.log('[Service Worker] No pending data to sync.');
          return;
        }
        const response = await fetch('/api/sync', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(pendingData)
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // 成功したらIndexedDBのデータをクリア
        // await clearPendingDataInIndexedDB(); // クライアント側JSで実装
        console.log('[Service Worker] Data synced successfully');
      } catch (error) {
        console.error('[Service Worker] Background sync failed:', error);
        throw error; // 再試行のためにエラーをスロー
      }
    })());
    // 未実装のため、再試行させないように ResolvedPromise を返すか、実装済みであれば上記コードを有効化
    // event.waitUntil(Promise.resolve());
  }
});

// プッシュ通知 (app.pyで実装されていない機能 - バックエンドでのPush API実装と連携が必要)
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received');
  
  const options = {
    body: event.data ? event.data.text() : '新しいお知らせがあります', // 通知本文
    icon: '/icon-192x192.png', // 適切なアイコンパスに変更
    badge: '/icon-72x72.png', // 適切なアイコンパスに変更
    vibrate: [100, 50, 100], // バイブレーションパターン
    data: { // 通知に含めるカスタムデータ
      dateOfArrival: Date.now(),
      // notificationId: ...
    },
    actions: [ // 通知に表示するアクションボタン
      { action: 'open_app', title: 'アプリを開く' },
      { action: 'close', title: '閉じる' }
    ]
  };
  
  // プッシュ通知を表示する
  event.waitUntil(
    self.registration.showNotification('RCCM問題集アプリ', options).catch(err => {
        console.error('[Service Worker] Failed to show notification:', err);
    })
  );
});

// 通知クリック処理
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click received with action:', event.action);
  
  event.notification.close(); // 通知を閉じる
  
  // クライアントを開くか、特定のURLに移動
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(clientList => {
      for (let i = 0; i < clientList.length; i++) {
        let client = clientList[i];
        // すでに開いているクライアントがあればそれにフォーカス
        // URLは適切に調整してください
        if (client.url.startsWith(self.location.origin) && client.url.includes('/?start=quiz') && 'focus' in client) { // 例: 学習開始ショートカットに対応
             return client.focus();
        }
        if (client.url.startsWith(self.location.origin) && client.url.includes('/?view=statistics') && 'focus' in client) { // 例: 統計確認ショートカットに対応
             return client.focus();
        }
        if (client.url.startsWith(self.location.origin) && 'focus' in client) { // 一般的なアプリのURL
             return client.focus();
        }
      }
      // 開いているクライアントがない場合、新しいタブで開く
      if (clients.openWindow) {
        // クリックされたアクションに応じて開くURLを決定
        let urlToOpen = '/';
        if (event.action === 'open_app') { // 例: アプリを開くアクション
           urlToOpen = '/'; // または '/?start=quiz' など
        }
        // 他のアクションに対するURLも追加
        
        return clients.openWindow(urlToOpen);
      }
    }).catch(err => {
        console.error('[Service Worker] Failed to open window on notification click:', err);
    })
  );
});

// 定期的なバックグラウンド更新 (Periodic Background Sync API - まだ広くサポートされていません)
// クライアントサイドJSで PeriodicSyncManager.register() を呼び出す必要があります。
self.addEventListener('periodicsync', event => {
  console.log('[Service Worker] Periodic Sync event triggered with tag:', event.tag);
  
  if (event.tag === 'update-questions') {
    // 例: 問題データファイルを定期的に更新
    event.waitUntil(updateQuestions().catch(err => {
        console.error('[Service Worker] Periodic sync update failed:', err);
        throw err; // 再試行のためにエラーをスロー
    }));
  }
  // 他の定期同期タグに対する処理を追加
});

// 問題データの更新 (Service Workerから直接fetchしてキャッシュを更新)
async function updateQuestions() {
   console.log('[Service Worker] Attempting to update questions data...');
   try {
       const response = await fetch('/data/questions.csv'); // サーバーからの問題データ取得エンドポイント
       if (!response.ok) {
           throw new Error(`HTTP error! status: ${response.status}`);
       }
       const cache = await caches.open(CACHE_NAME);
       await cache.put('/data/questions.csv', response); // キャッシュを更新
       console.log('[Service Worker] Questions data updated successfully');
   } catch (error) {
       console.error('[Service Worker] Failed to update questions data:', error);
       // 失敗した場合の処理（例: ユーザーに通知）
       throw error; // 再試行のためにエラーをスロー
   }
}

// メッセージ処理 (クライアントサイドJSからのメッセージ受信)
self.addEventListener('message', event => {
  console.log('[Service Worker] Message received:', event.data);
  
  // クライアントからのメッセージに応じて処理を実行
  if (event.data && event.data.type === 'SKIP_WAITING') {
    // 新しいService Workerをすぐにアクティブ化
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    // 指定されたキャッシュ、またはデフォルトキャッシュをクリア
    const cacheKey = event.data.cacheName || CACHE_NAME;
    event.waitUntil(
      caches.delete(cacheKey).then(() => {
        console.log(`[Service Worker] Cache '${cacheKey}' cleared`);
        // クライアントに完了を通知する場合
        // event.source.postMessage({ type: 'CACHE_CLEARED', cacheName: cacheKey });
      }).catch(err => {
         console.error(`[Service Worker] Failed to clear cache '${cacheKey}'`, err);
         // クライアントに失敗を通知する場合
         // event.source.postMessage({ type: 'CACHE_CLEAR_FAILED', cacheName: cacheKey, error: err });
      })
    );
  }
  
  // Other custom messaging can be added here (e.g., instructions to save offline data, etc.)
});

// 例外発生時のロギング強化
self.addEventListener('error', event => {
    console.error('[Service Worker] Uncaught error:', event.message, event.filename, event.lineno);
});

self.addEventListener('unhandledrejection', event => {
    console.error('[Service Worker] Unhandled Promise Rejection:', event.reason);
});

// fetch() 中にエラーが発生した場合、これはネットワークエラーを示す可能性があります。
// オフライン状態のより堅牢な検出と処理はクライアントサイドJSで行うのが推奨されます。
// Service Worker内では fetch イベントのエラーハンドリングが主なオフライン検出方法です。