/**
 * RCCM学習アプリ - モバイル機能強化 JavaScript
 * PWA、オフライン、音声、タッチ操作
 */

class MobileFeatures {
    constructor() {
        this.isOnline = navigator.onLine;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchStartTime = 0;
        this.speechSynthesis = window.speechSynthesis;
        this.currentSpeech = null;
        this.voiceSettings = {
            enabled: true,
            language: 'ja-JP',
            rate: 1.0,
            pitch: 1.0,
            volume: 0.8
        };
        
        this.init();
    }

    init() {
        this.setupPWA();
        this.setupOfflineHandler();
        this.setupTouchGestures();
        this.setupVoiceFeatures();
        this.setupKeyboardShortcuts();
        this.setupPerformanceMonitoring();
        this.setupAccessibilityFeatures();
        this.setupErrorBoundary();
        this.loadSettings();
        
        console.log('Mobile features initialized');
    }

    // PWA機能の設定
    setupPWA() {
        // Service Workerの登録
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                    
                    // 更新チェック
                    registration.addEventListener('updatefound', () => {
                        const newWorker = registration.installing;
                        newWorker.addEventListener('statechange', () => {
                            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                this.showUpdateNotification();
                            }
                        });
                    });
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        }

        // インストールプロンプトの処理
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton(deferredPrompt);
        });

        // インストール完了の処理
        window.addEventListener('appinstalled', () => {
            console.log('PWA installed');
            this.hideInstallButton();
            this.showToast('アプリがインストールされました！', 'success');
        });
    }

    // オフライン機能の設定
    setupOfflineHandler() {
        // オンライン/オフライン状態の監視
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleOnlineStateChange(true);
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.handleOnlineStateChange(false);
        });

        // IndexedDBでのオフラインデータ管理
        this.setupIndexedDB();
        
        // 定期的な同期
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            this.setupBackgroundSync();
        }
    }

    // タッチジェスチャーの設定
    setupTouchGestures() {
        if (!('ontouchstart' in window)) return;

        const quizContainer = document.querySelector('.quiz-container, .exam-container');
        if (!quizContainer) return;

        // タッチイベントの設定
        quizContainer.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        quizContainer.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        quizContainer.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });

        // 長押し防止（コンテキストメニュー）
        quizContainer.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    // 音声機能の設定
    setupVoiceFeatures() {
        if (!this.speechSynthesis) {
            console.warn('Speech Synthesis not supported');
            return;
        }

        // 音声読み上げボタンの追加
        this.addVoiceControls();
        
        // 音声認識の設定（対応ブラウザのみ）
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.setupSpeechRecognition();
        }
    }

    // キーボードショートカット
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + 数字でクイック選択
            if ((e.ctrlKey || e.metaKey) && /^[1-4]$/.test(e.key)) {
                e.preventDefault();
                this.selectAnswer(['A', 'B', 'C', 'D'][parseInt(e.key) - 1]);
            }
            
            // スペースキーで音声読み上げ
            if (e.code === 'Space' && !e.target.matches('input, textarea')) {
                e.preventDefault();
                this.toggleSpeech();
            }
            
            // 左右矢印で前後の問題
            if (e.code === 'ArrowLeft' && e.altKey) {
                e.preventDefault();
                this.navigateQuestion('prev');
            }
            if (e.code === 'ArrowRight' && e.altKey) {
                e.preventDefault();
                this.navigateQuestion('next');
            }
        });
    }

    // パフォーマンス監視
    setupPerformanceMonitoring() {
        // ページ読み込み時間の測定
        window.addEventListener('load', () => {
            if ('performance' in window) {
                const navigation = performance.getEntriesByType('navigation')[0];
                const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                console.log(`Page load time: ${loadTime}ms`);
            }
        });

        // メモリ使用量の監視（Chrome）
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('High memory usage detected');
                    this.showToast('メモリ使用量が高くなっています', 'warning');
                }
            }, 60000); // 1分ごと
        }
    }

    // タッチイベントハンドラー
    handleTouchStart(e) {
        if (e.touches.length !== 1) return;
        
        const touch = e.touches[0];
        this.touchStartX = touch.clientX;
        this.touchStartY = touch.clientY;
        this.touchStartTime = Date.now();
    }

    handleTouchMove(e) {
        // スクロール防止（必要に応じて）
        if (e.target.closest('.prevent-scroll')) {
            e.preventDefault();
        }
    }

    handleTouchEnd(e) {
        if (e.changedTouches.length !== 1) return;
        
        const touch = e.changedTouches[0];
        const endX = touch.clientX;
        const endY = touch.clientY;
        const endTime = Date.now();
        
        const deltaX = endX - this.touchStartX;
        const deltaY = endY - this.touchStartY;
        const deltaTime = endTime - this.touchStartTime;
        
        // スワイプジェスチャーの検出
        if (Math.abs(deltaX) > 50 && Math.abs(deltaY) < 100 && deltaTime < 500) {
            if (deltaX > 0) {
                this.handleSwipeRight();
            } else {
                this.handleSwipeLeft();
            }
        }
        
        // 長押しの検出
        if (deltaTime > 500 && Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
            this.handleLongPress(e);
        }
    }

    handleSwipeLeft() {
        // 次の問題へ
        this.navigateQuestion('next');
    }

    handleSwipeRight() {
        // 前の問題へ
        this.navigateQuestion('prev');
    }

    handleLongPress(e) {
        // 長押しメニューの表示
        const target = e.target.closest('.answer-option, .question-text');
        if (target) {
            this.showContextMenu(target, e.changedTouches[0]);
        }
    }

    // 音声読み上げ機能
    addVoiceControls() {
        const quizContainer = document.querySelector('.quiz-container, .exam-container');
        if (!quizContainer) return;

        // 音声コントロールボタンの追加
        const voiceControlsHTML = `
            <div class="voice-controls">
                <button id="speakBtn" class="btn btn-sm btn-outline-primary" title="音声読み上げ (Space)">
                    <i class="fas fa-volume-up"></i>
                </button>
                <button id="voiceSettingsBtn" class="btn btn-sm btn-outline-secondary" title="音声設定">
                    <i class="fas fa-cog"></i>
                </button>
            </div>
        `;
        
        quizContainer.insertAdjacentHTML('afterbegin', voiceControlsHTML);

        // イベントリスナーの設定
        document.getElementById('speakBtn')?.addEventListener('click', () => {
            this.toggleSpeech();
        });

        document.getElementById('voiceSettingsBtn')?.addEventListener('click', () => {
            this.showVoiceSettings();
        });
    }

    speakText(text, options = {}) {
        if (!this.voiceSettings.enabled || !this.speechSynthesis) return;

        // 現在の読み上げを停止
        this.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = options.language || this.voiceSettings.language;
        utterance.rate = options.rate || this.voiceSettings.rate;
        utterance.pitch = options.pitch || this.voiceSettings.pitch;
        utterance.volume = options.volume || this.voiceSettings.volume;

        utterance.onstart = () => {
            const speakBtn = document.getElementById('speakBtn');
            if (speakBtn) {
                speakBtn.innerHTML = '<i class="fas fa-stop"></i>';
                speakBtn.classList.add('speaking');
            }
        };

        utterance.onend = () => {
            const speakBtn = document.getElementById('speakBtn');
            if (speakBtn) {
                speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                speakBtn.classList.remove('speaking');
            }
            this.currentSpeech = null;
        };

        utterance.onerror = (e) => {
            console.error('Speech synthesis error:', e);
            this.showToast('音声読み上げでエラーが発生しました', 'error');
        };

        this.currentSpeech = utterance;
        this.speechSynthesis.speak(utterance);
    }

    toggleSpeech() {
        if (this.currentSpeech && this.speechSynthesis.speaking) {
            this.speechSynthesis.cancel();
        } else {
            const questionText = this.getQuestionTextForSpeech();
            if (questionText) {
                this.speakText(questionText);
            }
        }
    }

    getQuestionTextForSpeech() {
        const questionElement = document.querySelector('.question-text, .lead');
        if (!questionElement) return null;

        let speechText = `問題。${questionElement.textContent}。`;

        // 選択肢の追加
        const options = document.querySelectorAll('.answer-option .option-text, .form-check-label .option-text');
        options.forEach((option, index) => {
            const letter = ['A', 'B', 'C', 'D'][index];
            speechText += `選択肢${letter}。${option.textContent}。`;
        });

        return speechText;
    }

    // 音声認識の設定
    setupSpeechRecognition() {
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.lang = 'ja-JP';
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onresult = (event) => {
            const result = event.results[0][0].transcript.toLowerCase();
            this.handleVoiceCommand(result);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };

        // 音声入力ボタンの追加
        this.addVoiceInputButton();
    }

    handleVoiceCommand(command) {
        // 音声コマンドの処理
        if (command.includes('えー') || command.includes('a')) {
            this.selectAnswer('A');
        } else if (command.includes('びー') || command.includes('b')) {
            this.selectAnswer('B');
        } else if (command.includes('しー') || command.includes('c')) {
            this.selectAnswer('C');
        } else if (command.includes('でぃー') || command.includes('d')) {
            this.selectAnswer('D');
        } else if (command.includes('次') || command.includes('つぎ')) {
            this.navigateQuestion('next');
        } else if (command.includes('前') || command.includes('まえ')) {
            this.navigateQuestion('prev');
        } else if (command.includes('読み上げ') || command.includes('よみあげ')) {
            this.toggleSpeech();
        }
    }

    // IndexedDBの設定
    setupIndexedDB() {
        const request = indexedDB.open('RCCMQuizApp', 1);
        
        request.onerror = () => {
            console.error('IndexedDB opening failed');
        };
        
        request.onsuccess = (event) => {
            this.db = event.target.result;
            console.log('IndexedDB opened successfully');
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // オフラインデータ用のオブジェクトストア
            if (!db.objectStoreNames.contains('offlineData')) {
                const offlineStore = db.createObjectStore('offlineData', { keyPath: 'id' });
                offlineStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
            
            // キャッシュデータ用のオブジェクトストア
            if (!db.objectStoreNames.contains('cacheData')) {
                const cacheStore = db.createObjectStore('cacheData', { keyPath: 'key' });
            }
        };
    }

    // オフラインデータの保存
    saveOfflineData(data) {
        if (!this.db) return Promise.reject('IndexedDB not available');
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['offlineData'], 'readwrite');
            const store = transaction.objectStore('offlineData');
            
            const request = store.add({
                id: Date.now() + Math.random(),
                data: data,
                timestamp: new Date().toISOString()
            });
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // バックグラウンド同期の設定
    setupBackgroundSync() {
        navigator.serviceWorker.ready.then(registration => {
            return registration.sync.register('sync-study-data');
        }).catch(error => {
            console.error('Background sync registration failed:', error);
        });
    }

    // オンライン状態変更の処理
    handleOnlineStateChange(isOnline) {
        const statusIndicator = this.getOrCreateStatusIndicator();
        
        if (isOnline) {
            statusIndicator.className = 'online-status online';
            statusIndicator.innerHTML = '<i class="fas fa-wifi"></i> オンライン';
            this.showToast('オンラインに復帰しました', 'success');
            this.syncOfflineData();
        } else {
            statusIndicator.className = 'online-status offline';
            statusIndicator.innerHTML = '<i class="fas fa-wifi-slash"></i> オフライン';
            this.showToast('オフラインモードに切り替わりました', 'info');
        }
    }

    getOrCreateStatusIndicator() {
        let indicator = document.getElementById('onlineStatus');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'onlineStatus';
            indicator.className = 'online-status';
            document.body.appendChild(indicator);
        }
        return indicator;
    }

    // オフラインデータの同期
    syncOfflineData() {
        if (!this.db || !this.isOnline) return;
        
        const transaction = this.db.transaction(['offlineData'], 'readonly');
        const store = transaction.objectStore('offlineData');
        const request = store.getAll();
        
        request.onsuccess = () => {
            const offlineData = request.result;
            if (offlineData.length === 0) return;
            
            // サーバーに同期
            fetch('/api/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(offlineData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.clearOfflineData();
                    this.showToast('データを同期しました', 'success');
                }
            })
            .catch(error => {
                console.error('Sync failed:', error);
            });
        };
    }

    // ユーティリティ関数
    selectAnswer(answer) {
        const option = document.querySelector(`input[value="${answer}"]`);
        if (option) {
            option.checked = true;
            option.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    navigateQuestion(direction) {
        // 問題ナビゲーション（実装はページ固有）
        const event = new CustomEvent('questionNavigate', { detail: { direction } });
        document.dispatchEvent(event);
    }

    showToast(message, type = 'info') {
        // トースト通知の表示
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    showInstallButton(deferredPrompt) {
        const installBtn = document.createElement('button');
        installBtn.id = 'installBtn';
        installBtn.className = 'btn btn-primary install-btn';
        installBtn.innerHTML = '<i class="fas fa-download"></i> アプリをインストール';
        installBtn.onclick = () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(choiceResult => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
            });
        };
        
        document.body.appendChild(installBtn);
    }

    hideInstallButton() {
        const installBtn = document.getElementById('installBtn');
        if (installBtn) {
            installBtn.remove();
        }
    }

    showUpdateNotification() {
        if (confirm('新しいバージョンが利用可能です。今すぐ更新しますか？')) {
            window.location.reload();
        }
    }

    // 設定の保存・読み込み
    saveSettings() {
        localStorage.setItem('rccm_mobile_settings', JSON.stringify({
            voiceSettings: this.voiceSettings
        }));
    }

    loadSettings() {
        const saved = localStorage.getItem('rccm_mobile_settings');
        if (saved) {
            const settings = JSON.parse(saved);
            if (settings.voiceSettings) {
                this.voiceSettings = { ...this.voiceSettings, ...settings.voiceSettings };
            }
        }
    }

    // その他のユーティリティ
    clearOfflineData() {
        if (!this.db) return;
        
        const transaction = this.db.transaction(['offlineData'], 'readwrite');
        const store = transaction.objectStore('offlineData');
        store.clear();
    }

    addVoiceInputButton() {
        // 音声入力ボタンの実装（必要に応じて）
        const voiceInputBtn = document.createElement('button');
        voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceInputBtn.className = 'btn btn-sm btn-outline-success voice-input-btn';
        voiceInputBtn.onclick = () => {
            if (this.recognition) {
                this.recognition.start();
            }
        };
        
        const voiceControls = document.querySelector('.voice-controls');
        if (voiceControls) {
            voiceControls.appendChild(voiceInputBtn);
        }
    }

    showVoiceSettings() {
        // 音声設定モーダルの表示（簡易版）
        const modal = document.createElement('div');
        modal.className = 'voice-settings-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h5>音声設定</h5>
                <div class="form-group">
                    <label>読み上げ速度: <span id="rateValue">${this.voiceSettings.rate}</span></label>
                    <input type="range" id="rateSlider" min="0.5" max="2" step="0.1" value="${this.voiceSettings.rate}">
                </div>
                <div class="form-group">
                    <label>音量: <span id="volumeValue">${this.voiceSettings.volume}</span></label>
                    <input type="range" id="volumeSlider" min="0" max="1" step="0.1" value="${this.voiceSettings.volume}">
                </div>
                <button class="btn btn-primary" onclick="this.parentElement.parentElement.remove()">閉じる</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // スライダーイベント
        document.getElementById('rateSlider').oninput = (e) => {
            this.voiceSettings.rate = parseFloat(e.target.value);
            document.getElementById('rateValue').textContent = e.target.value;
            this.saveSettings();
        };
        
        document.getElementById('volumeSlider').oninput = (e) => {
            this.voiceSettings.volume = parseFloat(e.target.value);
            document.getElementById('volumeValue').textContent = e.target.value;
            this.saveSettings();
        };
    }

    showContextMenu(target, touch) {
        // コンテキストメニューの表示
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.left = touch.clientX + 'px';
        menu.style.top = touch.clientY + 'px';
        
        menu.innerHTML = `
            <div class="context-menu-item" onclick="mobileFeatures.speakText('${target.textContent}')">
                <i class="fas fa-volume-up"></i> 読み上げ
            </div>
            <div class="context-menu-item" onclick="mobileFeatures.closeContextMenu()">
                <i class="fas fa-times"></i> 閉じる
            </div>
        `;
        
        document.body.appendChild(menu);
        
        // 外側クリックで閉じる
        setTimeout(() => {
            document.addEventListener('click', () => this.closeContextMenu(), { once: true });
        }, 100);
    }

    closeContextMenu() {
        const menu = document.querySelector('.context-menu');
        if (menu) {
            menu.remove();
        }
    }

    // アクセシビリティ機能の設定
    setupAccessibilityFeatures() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
    }

    setupKeyboardNavigation() {
        // アプリ全体のキーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                switch (e.key) {
                    case 'h':
                    case 'H':
                        e.preventDefault();
                        window.location.href = '/';
                        break;
                    case 'd':
                    case 'D':
                        e.preventDefault();
                        if (window.toggleTheme) window.toggleTheme();
                        break;
                }
            }
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                window.location.href = '/help';
            }
        });
    }

    setupScreenReaderSupport() {
        // 動的コンテンツの読み上げ支援
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-announcements';
        document.body.appendChild(liveRegion);
    }

    // エラーバウンダリの設定（デバッグ用に一時無効化）
    setupErrorBoundary() {
        console.log('Error boundary setup - DISABLED FOR DEBUGGING');
        // グローバルエラーハンドラー - 一時的にコメントアウト
        /*
        window.addEventListener('error', (e) => {
            this.handleError({
                type: 'javascript',
                message: e.message,
                filename: e.filename,
                line: e.lineno,
                stack: e.error ? e.error.stack : 'スタックトレースなし'
            });
        });

        // Promise エラーハンドラー
        window.addEventListener('unhandledrejection', (e) => {
            this.handleError({
                type: 'promise',
                message: e.reason ? e.reason.toString() : 'Promise rejection'
            });
        });
        */
    }

    handleError(errorInfo) {
        console.error('Application Error:', errorInfo);
        const userMessage = this.getUserFriendlyErrorMessage(errorInfo);
        this.showToast(userMessage, 'error');
    }

    getUserFriendlyErrorMessage(errorInfo) {
        switch (errorInfo.type) {
            case 'network':
                return 'ネットワーク接続に問題があります。';
            case 'javascript':
                return 'ページを更新してもう一度お試しください。';
            default:
                return 'エラーが発生しました。';
        }
    }
}

// CSS スタイルの動的追加
const mobileCSS = `
.voice-controls {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 1000;
    display: flex;
    gap: 5px;
}

.online-status {
    position: fixed;
    top: 50px;
    right: 10px;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    z-index: 1000;
}

.online-status.online {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.online-status.offline {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.install-btn {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
}

.toast-notification {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px 20px;
    border-radius: 5px;
    color: white;
    z-index: 1001;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.toast-notification.show {
    opacity: 1;
}

.toast-info { background: #17a2b8; }
.toast-success { background: #28a745; }
.toast-warning { background: #ffc107; color: #212529; }
.toast-error { background: #dc3545; }

.context-menu {
    position: fixed;
    background: white;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    z-index: 1002;
}

.context-menu-item {
    padding: 10px 15px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
}

.context-menu-item:last-child {
    border-bottom: none;
}

.context-menu-item:hover {
    background: #f8f9fa;
}

.voice-settings-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1003;
}

.voice-settings-modal .modal-content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    max-width: 400px;
    width: 90%;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
}

.form-group input[type="range"] {
    width: 100%;
}

@media (max-width: 768px) {
    .voice-controls {
        top: 5px;
        right: 5px;
    }
    
    .online-status {
        top: 45px;
        right: 5px;
        font-size: 11px;
    }
}
`;

// CSSスタイルを追加
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileCSS;
document.head.appendChild(styleSheet);

// グローバルインスタンス
let mobileFeatures;

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', () => {
    mobileFeatures = new MobileFeatures();
});

// エクスポート（モジュール環境用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileFeatures;
}